#!/usr/bin/env python3
"""Read-only v7.2 production-lineage validator. This module never solves or writes."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
from typing import Any, Iterator


VALIDATOR_VERSION = "v7.2-production-checkpoint-validator-2026-09-09-r1"
DEFAULT_MANIFEST = "docs/checkpoints/production_checkpoint_manifest_v7_2_2026-09-09.json"
TRACKED_CLASSIFICATIONS = {"tracked_source", "current_model"}
IGNORED_CLASSIFICATIONS = {
    "local_ignored_artifact",
    "historical_frozen_artifact",
    "accepted_validation_evidence",
}


class ValidationError(RuntimeError):
    """A hard immutable-lineage mismatch."""


def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8-sig") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValidationError(f"Expected JSON object: {path}")
    return payload


def resolve_controlled(root: Path, relative: str) -> Path:
    path = (root / relative).resolve()
    try:
        path.relative_to(root.resolve())
    except ValueError as exc:
        raise ValidationError(f"Manifest path escapes repository root: {relative}") from exc
    return path


def artifact_entries(node: Any, trail: tuple[str, ...] = ()) -> Iterator[tuple[tuple[str, ...], dict[str, Any]]]:
    if isinstance(node, dict):
        if isinstance(node.get("path"), str) and isinstance(node.get("sha256"), str):
            yield trail, node
        for key, value in node.items():
            yield from artifact_entries(value, (*trail, str(key)))
    elif isinstance(node, list):
        for index, value in enumerate(node):
            yield from artifact_entries(value, (*trail, str(index)))


def git_check(root: Path, args: list[str]) -> bool:
    completed = subprocess.run(
        ["git", *args], cwd=root, capture_output=True, text=True, check=False
    )
    return completed.returncode == 0


def source_assignment(path: Path, name: str) -> str:
    text = path.read_text(encoding="utf-8-sig")
    match = re.search(rf'^\s*{re.escape(name)}\s*=\s*["\']([^"\']+)["\']', text, re.MULTILINE)
    if not match:
        raise ValidationError(f"Missing {name} assignment in {path}")
    return match.group(1)


def require_equal(actual: Any, expected: Any, label: str) -> None:
    if actual != expected:
        raise ValidationError(f"{label}: expected={expected!r}, actual={actual!r}")


def validate_all_artifact_hashes(root: Path, manifest: dict[str, Any]) -> list[dict[str, Any]]:
    checks: list[dict[str, Any]] = []
    for trail, entry in artifact_entries(manifest):
        label = ".".join(trail)
        path = resolve_controlled(root, entry["path"])
        if not path.is_file():
            raise ValidationError(f"{label}: required file missing: {entry['path']}")
        actual = sha256_file(path)
        require_equal(actual, entry["sha256"].lower(), f"{label} SHA-256")
        classification = entry.get("classification")
        relative = path.relative_to(root).as_posix()
        if classification in TRACKED_CLASSIFICATIONS:
            if not git_check(root, ["ls-files", "--error-unmatch", "--", relative]):
                raise ValidationError(f"{label}: expected Git-tracked source: {relative}")
        elif classification in IGNORED_CLASSIFICATIONS:
            if not git_check(root, ["check-ignore", "-q", "--", relative]):
                raise ValidationError(f"{label}: expected ignored/local artifact: {relative}")
        checks.append({"role": label, "path": relative, "sha256": actual, "status": "PASS"})
    return checks


def validate_versions(root: Path, manifest: dict[str, Any]) -> None:
    entries = (
        manifest["model"]["annual_core"],
        manifest["model"]["representative_wrapper_16a"],
        manifest["frozen_eob_comparator"]["originating_script_15b"],
        manifest["winter_pv_validation"]["script_17a"],
    )
    for entry in entries:
        path = resolve_controlled(root, entry["path"])
        actual = source_assignment(path, entry["version_field"])
        require_equal(actual, entry["version"], f"{entry['path']} version")


def validate_eob(root: Path, manifest: dict[str, Any]) -> dict[str, Any]:
    checkpoint = manifest["frozen_eob_comparator"]
    result = load_json(resolve_controlled(root, checkpoint["result"]["path"]))
    audit = load_json(resolve_controlled(root, checkpoint["freeze_audit"]["path"]))
    rainflow = load_json(resolve_controlled(root, checkpoint["rainflow_validation"]["path"]))
    expected = checkpoint["expectations"]

    require_equal(result.get("status"), expected["result_status"], "EOB result status")
    require_equal(result.get("mode"), expected["result_mode"], "EOB result mode")
    require_equal(result.get("has_solution"), expected["result_has_solution"], "EOB has_solution")
    require_equal(audit.get("freeze_status"), expected["freeze_status"], "EOB freeze status")
    require_equal(
        result.get("transition_settlement", {}).get("nonbinding_certificate"),
        expected["transition_certificate"],
        "EOB transition certificate",
    )
    gates = audit.get("production_gates")
    if not isinstance(gates, dict) or not gates:
        raise ValidationError("EOB freeze audit has no production_gates")
    bad_gates = {key: value for key, value in gates.items() if value != expected["all_production_gates"]}
    if bad_gates:
        raise ValidationError(f"EOB freeze audit contains non-PASS gates: {bad_gates}")
    require_equal(
        rainflow.get("final_verdict"),
        checkpoint["rainflow_validation"]["expected_final_verdict"],
        "EOB rainflow verdict",
    )

    require_equal(
        audit.get("script_version"), checkpoint["originating_script_15b"]["version"], "historical Script-15b version"
    )
    historical_core = checkpoint["historical_source_core_recorded_by_eob"]
    require_equal(audit.get("core_version"), historical_core["version"], "historical EOB core version")
    recorded = audit.get("source_hashes", {})
    require_equal(recorded.get("script_15b", {}).get("sha256"), checkpoint["originating_script_15b"]["sha256"], "historical Script-15b hash")
    require_equal(recorded.get("shared_core", {}).get("sha256"), historical_core["sha256"], "historical EOB core hash")
    require_equal(recorded.get("annual_input", {}).get("sha256"), checkpoint["canonical_annual_input_sha256"], "historical EOB annual-input hash")
    require_equal(recorded.get("economic_interface_14a", {}).get("sha256"), checkpoint["economic_interface_sha256"], "historical EOB economic-interface hash")
    require_equal(recorded.get("settlement_interface_14b", {}).get("sha256"), checkpoint["settlement_interface_sha256"], "historical EOB settlement-interface hash")
    require_equal(recorded.get("settlement_matrix_14b", {}).get("sha256"), checkpoint["settlement_matrix_sha256"], "historical EOB settlement-matrix hash")

    current_core = manifest["model"]["annual_core"]
    return {
        "status": "PASS",
        "classification": checkpoint["classification"],
        "historical_core_version": historical_core["version"],
        "historical_core_sha256": historical_core["sha256"],
        "current_core_version": current_core["version"],
        "current_core_sha256": current_core["sha256"],
        "historical_is_not_relabeled_as_current": True,
    }


def validate_representative(root: Path, manifest: dict[str, Any]) -> dict[str, Any]:
    checkpoint = manifest["current_representative_validation"]
    run_manifest = load_json(resolve_controlled(root, checkpoint["run_manifest"]["path"]))
    completion = load_json(resolve_controlled(root, checkpoint["completion_manifest"]["path"]))
    require_equal(run_manifest.get("run_id"), checkpoint["run_id"], "representative run ID")
    require_equal(completion.get("run_id"), checkpoint["run_id"], "representative completion run ID")
    require_equal(completion.get("status"), checkpoint["expected_status"], "representative completion status")
    require_equal(completion.get("all_gates_pass"), checkpoint["expected_all_gates_pass"], "representative all_gates_pass")
    require_equal(run_manifest.get("script_version"), checkpoint["wrapper_version"], "representative wrapper version")
    require_equal(run_manifest.get("core_version"), checkpoint["core_version"], "representative core version")
    require_equal(run_manifest.get("source_hashes_at_start", {}).get("script_16a"), checkpoint["wrapper_sha256"], "representative wrapper hash")
    require_equal(run_manifest.get("source_hashes_at_start", {}).get("annual_core"), checkpoint["core_sha256"], "representative core hash")
    case_ids = [item.get("case_id") for item in completion.get("selected_cases", [])]
    require_equal(case_ids, checkpoint["expected_case_ids"], "representative case IDs")
    return {"status": "PASS", "run_id": checkpoint["run_id"], "case_ids": case_ids}


def validate_winter(root: Path, manifest: dict[str, Any]) -> dict[str, Any]:
    checkpoint = manifest["winter_pv_validation"]
    run_manifest = load_json(resolve_controlled(root, checkpoint["run_manifest"]["path"]))
    completion = load_json(resolve_controlled(root, checkpoint["completion_manifest"]["path"]))
    require_equal(run_manifest.get("run_id"), checkpoint["run_id"], "Winter-PV run ID")
    require_equal(completion.get("run_id"), checkpoint["run_id"], "Winter-PV completion run ID")
    require_equal(completion.get("source_commit"), checkpoint["source_commit"], "Winter-PV source commit")
    require_equal(completion.get("status"), checkpoint["expected_completion_status"], "Winter-PV completion status")
    require_equal(completion.get("decision"), checkpoint["expected_decision"], "Winter-PV decision")
    require_equal(completion.get("holdout_status"), checkpoint["expected_holdout_status"], "Winter-PV holdout status")
    hashes = completion.get("source_hashes_at_start", {})
    require_equal(hashes.get("protocol"), checkpoint["frozen_protocol"]["sha256"], "Winter-PV protocol hash")
    require_equal(hashes.get("script_17a"), checkpoint["script_17a"]["sha256"], "Winter-PV Script-17a hash")
    return {"status": "PASS", "run_id": checkpoint["run_id"], "decision": completion["decision"]}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", default=DEFAULT_MANIFEST)
    parser.add_argument("--section", choices=("all", "eob"), default="all")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = project_root()
    try:
        manifest_path = resolve_controlled(root, args.manifest)
        manifest = load_json(manifest_path)
        require_equal(manifest.get("status"), "FROZEN_PRODUCTION_LINEAGE", "checkpoint status")
        artifact_checks = validate_all_artifact_hashes(root, manifest)
        validate_versions(root, manifest)
        eob = validate_eob(root, manifest)
        payload: dict[str, Any] = {
            "validator_version": VALIDATOR_VERSION,
            "mode": "READ_ONLY_NO_SOLVE",
            "manifest": manifest_path.relative_to(root).as_posix(),
            "manifest_version": manifest.get("manifest_version"),
            "artifact_hash_checks": len(artifact_checks),
            "eob_comparator": eob,
        }
        if args.section == "all":
            payload["representative_validation"] = validate_representative(root, manifest)
            payload["winter_pv_validation"] = validate_winter(root, manifest)
        payload["status"] = "PASS"
        print(json.dumps(payload, indent=2, sort_keys=True))
        return 0
    except Exception as exc:
        print(json.dumps({"validator_version": VALIDATOR_VERSION, "mode": "READ_ONLY_NO_SOLVE", "status": "FAIL", "error": str(exc)}, indent=2, sort_keys=True), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
