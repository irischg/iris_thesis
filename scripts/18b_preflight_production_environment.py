#!/usr/bin/env python3
"""Non-solving environment preflight for future v7.2 annual production runners."""

from __future__ import annotations

import hashlib
import importlib.metadata
import json
from pathlib import Path
import platform
import subprocess
import sys
from typing import Any


PREFLIGHT_VERSION = "v7.2-production-environment-preflight-2026-09-09-r1"
EXPECTED_REQUIREMENTS_LOCK_SHA256 = "12622a7d651f5fd2b13bff2a14ca1df9c124054ea79dabf05f4886b5c90103dd"
LOCKED_PACKAGES = ("pandas", "numpy", "pyarrow", "gurobipy")


def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def git_value(root: Path, *args: str) -> str | None:
    completed = subprocess.run(["git", *args], cwd=root, capture_output=True, text=True, check=False)
    return completed.stdout.strip() if completed.returncode == 0 else None


def locked_versions(lock_path: Path) -> dict[str, str]:
    locked: dict[str, str] = {}
    for raw_line in lock_path.read_text(encoding="utf-8-sig").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "==" not in line:
            continue
        name, version = line.split("==", 1)
        locked[name.lower()] = version
    return locked


def main() -> int:
    root = project_root()
    lock_path = root / "requirements-lock.txt"
    required_checks: list[dict[str, Any]] = []
    recorded: dict[str, Any] = {}
    warnings: list[str] = []

    executable = Path(sys.executable).resolve()
    expected_venv = (root / ".venv").resolve()
    try:
        executable.relative_to(expected_venv)
        in_project_venv = True
    except ValueError:
        in_project_venv = False
    required_checks.append({"check": "python_executable_in_project_venv", "classification": "REQUIRED MATCH", "expected_root": str(expected_venv), "actual": str(executable), "status": "PASS" if in_project_venv else "FAIL"})

    if not lock_path.is_file():
        required_checks.append({"check": "requirements_lock_exists", "classification": "REQUIRED MATCH", "status": "FAIL"})
        locks: dict[str, str] = {}
    else:
        required_checks.append({"check": "requirements_lock_exists", "classification": "REQUIRED MATCH", "status": "PASS"})
        lock_hash = sha256_file(lock_path)
        required_checks.append({"check": "requirements_lock_sha256", "classification": "REQUIRED MATCH", "expected": EXPECTED_REQUIREMENTS_LOCK_SHA256, "actual": lock_hash, "status": "PASS" if lock_hash == EXPECTED_REQUIREMENTS_LOCK_SHA256 else "FAIL"})
        locks = locked_versions(lock_path)
        recorded["requirements_lock"] = {"path": str(lock_path), "sha256": lock_hash}

    package_versions: dict[str, Any] = {}
    for package in LOCKED_PACKAGES:
        expected = locks.get(package)
        try:
            actual = importlib.metadata.version(package)
            status = "PASS" if expected is not None and actual == expected else "FAIL"
        except importlib.metadata.PackageNotFoundError:
            actual = None
            status = "FAIL"
        package_versions[package] = {"classification": "REQUIRED MATCH", "expected": expected, "actual": actual, "status": status}
        required_checks.append({"check": f"locked_package_{package}", **package_versions[package]})

    gurobi_license_status = "FAIL"
    gurobi_runtime_version: str | None = None
    gurobi_error: str | None = None
    try:
        import gurobipy as gp
        gurobi_runtime_version = ".".join(str(part) for part in gp.gurobi.version())
        environment = gp.Env(empty=True)
        environment.setParam("OutputFlag", 0)
        environment.start()
        environment.dispose()
        gurobi_license_status = "PASS" if gurobi_runtime_version == locks.get("gurobipy") else "FAIL"
    except Exception as exc:
        gurobi_error = f"{type(exc).__name__}: {exc}"
    required_checks.append({"check": "gurobi_runtime_and_license_nonoptimizing", "classification": "REQUIRED MATCH", "runtime_version": gurobi_runtime_version, "status": gurobi_license_status, "error": gurobi_error})

    status_porcelain = git_value(root, "status", "--porcelain=v1")
    if status_porcelain:
        warnings.append("Working tree is not clean; future runner must record and explicitly accept this state.")
    recorded.update({
        "classification": "RECORDED FOR PROVENANCE",
        "repository_root": str(root.resolve()),
        "python_executable": str(executable),
        "python_version": platform.python_version(),
        "packages": package_versions,
        "gurobi_runtime_version": gurobi_runtime_version,
        "active_branch": git_value(root, "branch", "--show-current"),
        "head": git_value(root, "rev-parse", "HEAD"),
        "working_tree_status": status_porcelain.splitlines() if status_porcelain else [],
    })
    overall = "PASS" if all(item.get("status") == "PASS" for item in required_checks) else "FAIL"
    print(json.dumps({
        "preflight_version": PREFLIGHT_VERSION,
        "mode": "NON_SOLVING_ENVIRONMENT_PREFLIGHT",
        "status": overall,
        "required_match": required_checks,
        "recorded_for_provenance": recorded,
        "warning_only": {"classification": "WARNING ONLY", "messages": warnings},
    }, indent=2, sort_keys=True))
    return 0 if overall == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
