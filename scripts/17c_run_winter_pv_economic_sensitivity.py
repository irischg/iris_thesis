#!/usr/bin/env python3
"""Run the controlled two-solve Winter-PV economic sensitivity for v7.2.

This script is intentionally limited to the accepted alternative-input EOB and
the single Layer-A a0.80_b08 case.  It never solves the canonical input and it
never constructs or solves the 81-case Layer-A matrix.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import subprocess
import sys
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

import numpy as np
import pandas as pd


SCRIPT_VERSION = "v7.2-winter-pv-economic-sensitivity-corrected-authority-2026-09-18-r2"
EXPECTED_BRANCH = "thesis-v7"
EXPECTED_COMMIT = "b03721275c73b05d45517bdf84c1e0bd03833376"
EXPECTED_CORE_VERSION = "v7.2-annual-design-core-transition-candidate1-exact-d-preflight-2026-09-16-r10"
EXPECTED_TRACKED_MODIFIED = {
    "scripts/06a_build_taipower_tou_calendar.py",
    "scripts/13c_regress_taipower_core_bill_components.py",
    "scripts/16a_preflight_layer_a_representative_binary_cases.py",
    "scripts/17b_build_winter_pv_sensitivity_annual_input.py",
    "scripts/17c_run_winter_pv_economic_sensitivity.py",
    "scripts/19a_preflight_final_layer_a_81_cases.py",
    "src/annual_design_model_v7_2.py",
    "tests/test_transition_candidate1_static_v7_2.py",
}
CORRECTED_EOB_RUN_ID = "20260917T082758521112Z_a4b6383308"
CURRENT_LAYER_RUN_ID = "20260918T085202453195Z_755e01dfb2"
CURRENT_17B_RUN_ID = "20260918T143929009039Z_8f11437d44"
MIP_GAP = 1e-6
TIME_LIMIT_SEC = None
ALPHA = 0.80
BETA_H = 8
CASE_ID = "a0.80_b08"
TOL = 1e-6

ACTIVE_HASHES = {
    "framework": ("docs/research_framework_v7_2_2026-08-24.md", "bfe724a35dd019b9f29456a7a7b569e132aa63b399c21c82d2c69a9fd934c8d5"),
    "registry": ("docs/thesis_literature_evidence_registry_v7_2_2026-08-24.md", "8b72bd3f56226f0be6900f52779b1702daaa8bbf85f674040b336f9aae6e021e"),
    "winter_pv_protocol": ("docs/winter_pv_longblock_sensitivity_protocol_v7_2_2026-09-07.md", "630c9c20a388fde31d424d8b1e43d99cd05c5d2c9cf51b17e2d36f90fb50f525"),
    "annual_core": ("src/annual_design_model_v7_2.py", "9d828321814b09141497056d1bb17da8b2839c5eb151fce8530059fb7e193da8"),
    "rainflow_core": ("src/rainflow_validation_v7_2.py", "4ae83643dca4e7266ad0e4ebe54c0302a1cf38918935c8789e493798ea6c09d2"),
    "script_16a": ("scripts/16a_preflight_layer_a_representative_binary_cases.py", "3f62fa290e1c8e1699c34d4b1bc78b9af0e716387b251afb4ada2b3198d7524f"),
    "script_17a": ("scripts/17a_validate_winter_pv_longblock_holdouts.py", "c8bb665fb607b129df2187435c5454e49dbf6faff3ca25013a3eda7d26670c91"),
    "script_17b": ("scripts/17b_build_winter_pv_sensitivity_annual_input.py", "96e7c0fdd77bb3a6293becea401cc83dd0f24659ee26676e18aef69991d33160"),
    "canonical_annual": ("data/processed/annual_input_v7_1.parquet", "9142b8b6f81b3f423c4ab43ac049765b3e934aae57d33c761208f3452598518e"),
    "alternative_annual": ("data/processed/alternatives/annual_input_v7_2_winter_pv_sensitivity_corrected_authority_project_venv_2026-09-18.parquet", "1c1dbc265b092415e649bba23232f645f7ba5c74e0f074f2914c1ed7ac9d7cd9"),
    "alternative_manifest": ("data/processed/alternatives/annual_input_v7_2_winter_pv_sensitivity_corrected_authority_project_venv_2026-09-18_manifest.json", "e6808ca6270afd808e930a4baa8032852d88bf92c232bb53e68f434fdfba1381"),
    "economic_interface": ("data/reference/production_economic_interface_v7_2.json", "9277d310a124e1ae9d91fe1bf5fc1d70210372ca2f3d9e3b1c110cd210c319a9"),
    "normalized_tariff": ("data/reference/taipower_tariff_optimization_ntd2023_v7_2.csv", "5c1582d8ecebba3fc46a4afe61a5ecb66c8a059ef81b4edeba69f67cc9974395"),
    "settlement_interface": ("data/reference/taipower_transition_period_settlement_interface_v7_2.json", "f101af4754f89a2126333796e3cea63210140c94cccc1ad925fa9128361c5b88"),
    "settlement_matrix": ("data/reference/taipower_seasonal_settlement_matrix_v7_2.csv", "ed7f8dbf9d3e41564e3fc289c395df17aa390466b1abc1ea03a5c9e421324b79"),
    "technical_provenance": ("results/parameter_audit/pnnl_table4_2_cyclelife_g_provenance_by_bracket.csv", "1172963521fbc4b646394cb2df6947ade9f961211bf608c5928ef4de215644f6"),
    "observed_bill": ("data/reference/taipower_bills_final_clean.csv", "e18d05a1cec3917b0f69f9a769e549ab50228f060ac7bf6bd06361a4b247f34d"),
    "17a_run_manifest": ("results/data_audit/winter_pv_holdouts/20260909T042957292822Z_7de1c7a4f4/run_manifest.json", "374a52ebc2db0ad0b4c26a05b51a6ed50273dd1dc803164e99da4560ac14d14b"),
    "17a_completion": ("results/data_audit/winter_pv_holdouts/20260909T042957292822Z_7de1c7a4f4/completion_manifest.json", "678a11d8acd0dec10020f39c011917a998d75c0055fd568fe14d75a7226f34f6"),
    "17a_decision": ("results/data_audit/winter_pv_holdouts/20260909T042957292822Z_7de1c7a4f4/final_validation_decision.json", "454a60574d30731fc621ed57d1355911586df4c97aa6b2184ab405015708c594"),
    "17b_run_manifest": ("results/data_audit/winter_pv_17b/20260918T143929009039Z_8f11437d44/run_manifest.json", "37250bf2367517e8b519c4b6b8fe04309e938e0838fecccce10915071e5f8024"),
    "17b_diff_audit": ("results/data_audit/winter_pv_17b/20260918T143929009039Z_8f11437d44/annual_input_v7_2_winter_pv_sensitivity_corrected_authority_project_venv_2026-09-18_column_diff_audit.csv", "a20998fddec6188a1d0ffd7c0132a4b65bd70907cc6e3f3c97f7661283ad829d"),
    "17b_completion": ("results/data_audit/winter_pv_17b/20260918T143929009039Z_8f11437d44/completion_manifest.json", "b11133993ff2bb791bc7f131e66e8fd9b6b4df9c38fcbc24ff53f888679698e4"),
    "corrected_eob_acceptance": ("docs/checkpoints/corrected_eob_accepted_authority_v7_2_2026-09-17.md", "e71401ec3562b0803e52e3d054f8d7a69a1528fd197a03c6a7d42df629ab32a2"),
    "r3_delta": ("results/provenance/post_eob_delta_freeze_v7_2_20260917_r3/post_eob_old_new_delta_r3_2026-09-17.json", "e217b7f64100260ae2a5d8de5231f0a1b608844afc818271236f99ead5c5ce96"),
    "r3_manifest": ("results/provenance/post_eob_delta_freeze_v7_2_20260917_r3/post_eob_delta_package_r3_hash_manifest_2026-09-17.json", "6cf23560f2daa1e9fc45d0eaf46d3af6d97303829d8fd20ef5e94068bb89495e"),
    "r3_checkpoint": ("docs/checkpoints/post_eob_delta_freeze_r3_authority_v7_2_2026-09-17.md", "32f4c437f6279c7a53aad2e0d9f0a0d1692a1e11fdc7c8b700f31aec818730e0"),
    "16a_checkpoint": ("docs/checkpoints/16a_current_authority_comparator_update_v7_2_2026-09-17.md", "f0610c7b20afe063d9f4e844e9a10421af083e380572ceb192b45b3e99889db3"),
    "current_eob_manifest": ("results/eob_production_corrected/runs/20260917T082758521112Z_a4b6383308/run_manifest.json", "9acb3f52948c63e65c29baf3f8a84653d127febf96369f1945cbb358389eb99a"),
    "current_eob_result": ("results/eob_production_corrected/runs/20260917T082758521112Z_a4b6383308/corrected_eob_result.json", "d7c37a0013ad6ea5a8dc3231a67bf427ec0c502aef96fedc47aacfe7c8897022"),
    "current_eob_dispatch": ("results/eob_production_corrected/runs/20260917T082758521112Z_a4b6383308/corrected_eob_dispatch.csv", "b4dca52eba714a2d28cb7b3b6928facdeda39949b1b5cdcab4e25acdc52fa147"),
    "current_eob_billing": ("results/eob_production_corrected/runs/20260917T082758521112Z_a4b6383308/corrected_eob_billing_exact.csv", "5bb71bfb0b817ec5efa3923174daf2ceceb78bf84a60dadd039a67c7cda5de1c"),
    "current_layer_manifest": ("results/layer_a/preflight/runs/20260918T085202453195Z_755e01dfb2/run_manifest_v7_2.json", "1a331faaf2d079bfd0d70d46d400e29eeeb8ee1edc67a566b096926ed1202118"),
    "current_layer_completion": ("results/layer_a/preflight/runs/20260918T085202453195Z_755e01dfb2/run_completion_v7_2.json", "06a794588623d1658cec1bb2196279915a5a77ad251e4ebc6899ef3d9c829aac"),
    "current_layer_case_manifest": ("results/layer_a/preflight/runs/20260918T085202453195Z_755e01dfb2/representative_cases/a0.80_b08/case_manifest_v7_2.json", "2be9e0716827e83e380bf17c1c9210f760818e0a4ccaa86b53a46bd16979c23f"),
    "current_layer_result": ("results/layer_a/preflight/runs/20260918T085202453195Z_755e01dfb2/representative_cases/a0.80_b08/a0.80_b08_result_v7_2.json", "8a9bc67fc541ea682f9360e6063ededdb5bc0e2c6340c43c10c1fde86ab155f6"),
    "current_layer_dispatch": ("results/layer_a/preflight/runs/20260918T085202453195Z_755e01dfb2/representative_cases/a0.80_b08/a0.80_b08_dispatch_v7_2.csv", "1b5f1fbc3c68bd3d52d426bc4e3c58c35b8a90830b42113f62c5a4ca92fde926"),
    "current_layer_billing": ("results/layer_a/preflight/runs/20260918T085202453195Z_755e01dfb2/representative_cases/a0.80_b08/a0.80_b08_billing_exact_v7_2.csv", "ba9762031435c1e06464878356e81d4e289ac20562cac9e713f3756fbb156f83"),
    "current_layer_rainflow": ("results/layer_a/preflight/runs/20260918T085202453195Z_755e01dfb2/representative_cases/a0.80_b08/a0.80_b08_rainflow_summary_v7_2.csv", "a433f9c28dac71f2c28f4c46e1c514c23afb7bd24b22ad7a82829fbab30b4a44"),
}

HISTORICAL_PROVENANCE_HASHES = {
    "historical_eob_result": ("results/eob_production/eob_production_result_v7_2.json", "ad606a503b3f68ceba048e4b94bc0e19e6ddde00f88c145d051f772557e0bd56"),
    "historical_eob_freeze": ("results/eob_production/eob_production_freeze_audit_v7_2.json", "18bf93414dcc677bdd4ab68b99aae3c0af9412ea52c950eaf8f186b075822907"),
    "historical_eob_rainflow": ("results/degradation_validation/eob_rainflow_validation_audit_v7_2.json", "8660da9fcee9507d9e03b656981cc325dc2533283657d4c4dbf1f5585fcd9f71"),
    "historical_eob_dispatch": ("results/eob_production/eob_production_dispatch_v7_2.csv", "91a13101ca7f3ef82903359fed1f3de6093d0015b8b6a892463a22e9142f4d85"),
    "historical_eob_billing": ("results/eob_production/eob_production_billing_exact_v7_2.csv", "9567163c72ce50ea9144a04e035a9613a3c5653488cc8f62ad4fe632eac3b710"),
    "historical_layer_manifest": ("results/layer_a/preflight/runs/20260906T050046737317Z_5f2cd1942c/run_manifest_v7_2.json", "6872f8de736b60fda2be86ecfe30aac6c1fb05460eeddd5f468a4b8c6bb23f26"),
    "historical_layer_completion": ("results/layer_a/preflight/runs/20260906T050046737317Z_5f2cd1942c/run_completion_v7_2.json", "7a1e9c0d839201e175d336dad9b37c8d5bd71a00f84bf1f394758ac9e18397bc"),
    "historical_layer_result": ("results/layer_a/preflight/runs/20260906T050046737317Z_5f2cd1942c/representative_cases/a0.80_b08/a0.80_b08_result_v7_2.json", "0dd931e5075e94e0ef6e7d215af46b30e673ba48455e3395d4dfbea4be902074"),
    "historical_layer_dispatch": ("results/layer_a/preflight/runs/20260906T050046737317Z_5f2cd1942c/representative_cases/a0.80_b08/a0.80_b08_dispatch_v7_2.csv", "5586caaafc7cdc7261e14f556e7fcf4edb26168be3dd04aaf1cd05bb580d0fb9"),
    "historical_layer_billing": ("results/layer_a/preflight/runs/20260906T050046737317Z_5f2cd1942c/representative_cases/a0.80_b08/a0.80_b08_billing_exact_v7_2.csv", "f79fb12c841c9890560af8c1919ed16252f5efe9aeebeed87e6c177df77006f2"),
    "historical_layer_rainflow": ("results/layer_a/preflight/runs/20260906T050046737317Z_5f2cd1942c/representative_cases/a0.80_b08/a0.80_b08_rainflow_summary_v7_2.csv", "d2e6712adb38eeb8c03768f9c6b4944a643663c75686749f964a72f59772803d"),
}


def root_path() -> Path:
    return Path(__file__).resolve().parents[1]


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def utc_text(value: datetime | None = None) -> str:
    return (value or utc_now()).isoformat().replace("+00:00", "Z")


def json_safe(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(k): json_safe(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [json_safe(v) for v in value]
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, (pd.Timestamp, datetime)):
        return value.isoformat()
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        return float(value) if np.isfinite(value) else None
    if isinstance(value, (np.bool_,)):
        return bool(value)
    if isinstance(value, float):
        return value if math.isfinite(value) else None
    return value


def write_json(path: Path, payload: dict[str, Any], *, exclusive: bool = True) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x" if exclusive else "w", encoding="utf-8") as handle:
        json.dump(json_safe(payload), handle, indent=2)
        handle.write("\n")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def run_git(root: Path, *args: str) -> str:
    result = subprocess.run(["git", *args], cwd=root, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} failed: {result.stderr.strip()}")
    return result.stdout.strip()


def load_module(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load module {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def check_hashes(
    root: Path,
    records: dict[str, tuple[str, str]] = ACTIVE_HASHES,
) -> dict[str, Any]:
    checks: dict[str, Any] = {}
    for label, (relative, expected) in records.items():
        path = root / relative
        actual = sha256_file(path) if path.is_file() else None
        checks[label] = {
            "path": relative,
            "expected_sha256": expected,
            "actual_sha256": actual,
            "status": "PASS" if actual == expected else "FAIL",
        }
    failed = [key for key, record in checks.items() if record["status"] != "PASS"]
    if failed:
        raise RuntimeError(f"Frozen artifact hash failure: {failed}")
    return checks


def check_repository(root: Path) -> dict[str, Any]:
    branch = run_git(root, "branch", "--show-current")
    head = run_git(root, "rev-parse", "HEAD")
    origin = run_git(root, "rev-parse", "origin/thesis-v7")
    tracked_modified = set(run_git(root, "diff", "--name-only").splitlines())
    staged_modified = run_git(root, "diff", "--cached", "--name-only").splitlines()
    repo = {
        "branch": branch,
        "head": head,
        "local_origin_thesis_v7": origin,
        "tracked_modified": sorted(tracked_modified),
        "expected_tracked_modified": sorted(EXPECTED_TRACKED_MODIFIED),
        "staged_modified": staged_modified,
        "network_lookup_performed": False,
    }
    expected = (
        branch == EXPECTED_BRANCH
        and head == origin == EXPECTED_COMMIT
        and tracked_modified == EXPECTED_TRACKED_MODIFIED
        and not staged_modified
    )
    repo["status"] = "PASS" if expected else "FAIL"
    if not expected:
        raise RuntimeError(f"Repository identity/cleanliness failure: {repo}")
    return repo


def run_read_only_validator(root: Path, script: str) -> dict[str, Any]:
    completed = subprocess.run(
        [sys.executable, str(root / script)], cwd=root, capture_output=True, text=True, check=False
    )
    record = {
        "path": script,
        "returncode": completed.returncode,
        "status": "PASS" if completed.returncode == 0 else "FAIL",
        "stdout": completed.stdout[-12000:],
        "stderr": completed.stderr[-4000:],
    }
    if completed.returncode != 0:
        raise RuntimeError(f"Read-only validator failed: {script}")
    return record


def verify_accepted_chain(root: Path) -> dict[str, Any]:
    alt_manifest = read_json(root / ACTIVE_HASHES["alternative_manifest"][0])
    decision = read_json(root / ACTIVE_HASHES["17a_decision"][0])
    completion_17b = read_json(root / ACTIVE_HASHES["17b_completion"][0])
    acceptance = (root / ACTIVE_HASHES["corrected_eob_acceptance"][0]).read_text(encoding="utf-8")
    decision_text = decision.get("WINTER_PV_RECONSTRUCTION_VALIDATION")
    checks = {
        "corrected_eob_acceptance": "CORRECTED_EOB_ACCEPTED_PRODUCTION_AUTHORITY" in acceptance,
        "corrected_eob_run_identity": CORRECTED_EOB_RUN_ID in acceptance,
        "17a_decision": decision_text == "PASS_FOR_SENSITIVITY",
        "17b_run_identity": completion_17b.get("run_id") == CURRENT_17B_RUN_ID,
        "17b_status": completion_17b.get("status") == "17B_BUILD_PASS",
        "alternative_role": alt_manifest.get("additive_provenance", {}).get("artifact_role") == "winter_pv_sensitivity_only",
        "alternative_uses_corrected_canonical": alt_manifest.get("canonical_annual_input", {}).get("sha256_before_build") == ACTIVE_HASHES["canonical_annual"][1],
        "17b_all_gates_pass": completion_17b.get("all_build_gates_pass") is True and all(bool(value) for value in completion_17b.get("build_gates", {}).values()),
    }
    if not all(checks.values()):
        raise RuntimeError(f"Accepted 17a/17b chain failure: {checks}")
    return {
        "checks": {key: "PASS" if value else "FAIL" for key, value in checks.items()},
        "authority_route": "CORRECTED_EOB_ACCEPTANCE -> CURRENT_16A -> AUDITED_A0.80_B08 -> CORRECTED_17B_INPUT",
    }


def load_current_comparators(root: Path) -> dict[str, Any]:
    eob_manifest = read_json(root / ACTIVE_HASHES["current_eob_manifest"][0])
    eob_result = read_json(root / ACTIVE_HASHES["current_eob_result"][0])
    layer_manifest = read_json(root / ACTIVE_HASHES["current_layer_manifest"][0])
    layer_completion = read_json(root / ACTIVE_HASHES["current_layer_completion"][0])
    case_manifest = read_json(root / ACTIVE_HASHES["current_layer_case_manifest"][0])
    layer_record = read_json(root / ACTIVE_HASHES["current_layer_result"][0])
    layer_result = layer_record.get("result", {})
    rainflow = layer_record.get("rainflow_validation", {})
    checks = {
        "eob_run_id": eob_manifest.get("run_id") == CORRECTED_EOB_RUN_ID,
        "eob_core": eob_manifest.get("CORE_VERSION") == EXPECTED_CORE_VERSION
        and eob_manifest.get("core_sha256") == ACTIVE_HASHES["annual_core"][1],
        "eob_canonical": eob_manifest.get("canonical_input_sha256") == ACTIVE_HASHES["canonical_annual"][1],
        "eob_optimal_binary": eob_result.get("status") == "OPTIMAL"
        and eob_result.get("mode") == "binary"
        and float(eob_result.get("mip_gap", math.inf)) <= MIP_GAP,
        "layer_run_id": layer_manifest.get("run_id") == CURRENT_LAYER_RUN_ID,
        "layer_selected_case": layer_manifest.get("selected_cases")
        == [{"case_id": CASE_ID, "alpha": ALPHA, "beta_h": BETA_H}],
        "layer_current_eob_authority": layer_manifest.get("eob_comparator_authority", {}).get("run_id") == CORRECTED_EOB_RUN_ID
        and layer_manifest.get("eob_comparator_authority", {}).get("historical_fallback_allowed") is False,
        "layer_completion": layer_completion.get("run_id") == CURRENT_LAYER_RUN_ID
        and layer_completion.get("status") == "REPRESENTATIVE_PASS"
        and layer_completion.get("all_gates_pass") is True,
        "case_identity": case_manifest.get("run_id") == CURRENT_LAYER_RUN_ID
        and case_manifest.get("case_id") == CASE_ID
        and case_manifest.get("mode") == "binary",
        "case_optimal_binary": layer_result.get("status") == "OPTIMAL"
        and layer_result.get("mode") == "binary"
        and float(layer_result.get("mip_gap", math.inf)) <= MIP_GAP,
        "case_18_gates": len(layer_record.get("gates", {})) == 18
        and all(value == "PASS" for value in layer_record.get("gates", {}).values()),
        "case_rainflow": rainflow.get("summary", {}).get("verdict") == "RAINFLOW_VALIDATION_PASS"
        and all(value == "PASS" for value in rainflow.get("gates", {}).values()),
    }
    if not all(checks.values()):
        raise RuntimeError(f"Current comparator authority failure: {checks}")
    return {
        "checks": {key: "PASS" if value else "FAIL" for key, value in checks.items()},
        "eob_result": eob_result,
        "layer_record": layer_record,
        "layer_result": layer_result,
    }


def fairness_audit(canonical: pd.DataFrame, alternative: pd.DataFrame) -> dict[str, Any]:
    provenance_columns = {
        "artifact_role", "winter_pv_sensitivity_applied",
        "winter_pv_sensitivity_method", "winter_pv_sensitivity_protocol_sha256",
    }
    if len(canonical) != len(alternative) or not set(canonical.columns).issubset(alternative.columns):
        raise RuntimeError("Canonical/alternative row count or inherited schema mismatch.")
    if set(alternative.columns) - set(canonical.columns) != provenance_columns:
        raise RuntimeError("Alternative has an unexpected additive provenance schema.")
    if canonical.dtypes.astype(str).to_dict() != alternative[canonical.columns].dtypes.astype(str).to_dict():
        raise RuntimeError("Canonical/alternative dtype mismatch.")
    timestamp_equal = canonical["timestamp"].astype(str).equals(alternative["timestamp"].astype(str))
    permitted = {
        "pv_available_kw", "pv_available_kwh", "residual_load_kw",
        "grid_demand_before_bess_kw", "pv_surplus_before_bess_kw",
    }
    changes: dict[str, int] = {}
    forbidden: list[str] = []
    for column in canonical.columns:
        left, right = canonical[column], alternative[column]
        if pd.api.types.is_numeric_dtype(left):
            count = int(np.count_nonzero(~np.isclose(left.to_numpy(float), right.to_numpy(float), atol=1e-10, rtol=0.0, equal_nan=True)))
        else:
            equal = left.eq(right) | (left.isna() & right.isna())
            count = int((~equal.fillna(False)).sum())
        changes[column] = count
        if count and column not in permitted:
            forbidden.append(column)
    delta_pv = float(alternative["pv_available_kwh"].sum() - canonical["pv_available_kwh"].sum())
    target = alternative["winter_pv_sensitivity_applied"].astype(bool)
    provenance_ok = (
        alternative["artifact_role"].eq("winter_pv_sensitivity_only").all()
        and int(target.sum()) == 1463
        and alternative["winter_pv_sensitivity_method"].eq("cwa_hourly_ghi_ratio_median_all_eligible_v7_2").all()
        and alternative["winter_pv_sensitivity_protocol_sha256"].eq(ACTIVE_HASHES["winter_pv_protocol"][1]).all()
    )
    report = {
        "status": "PASS" if timestamp_equal and not forbidden and provenance_ok and abs(delta_pv - 39484.422494085295) <= 1e-6 else "FAIL",
        "row_count": len(canonical),
        "timestamp_vector_exact": timestamp_equal,
        "target_window_rows": int(target.sum()),
        "column_change_counts": changes,
        "forbidden_changed_columns": forbidden,
        "additive_provenance_columns": sorted(provenance_columns),
        "additive_provenance_valid": provenance_ok,
        "alternative_minus_canonical_pv_energy_kwh": delta_pv,
        "expected_pv_energy_delta_kwh": 39484.422494085295,
    }
    if report["status"] != "PASS":
        raise RuntimeError(f"Alternative-input fairness audit failed: {report}")
    return report


def single_case_requirement(annual: pd.DataFrame, eta_d: float, soc_min: float, soc_max: float) -> dict[str, Any]:
    timestamps = pd.to_datetime(annual["timestamp"], errors="raise").reset_index(drop=True)
    load = annual["baseline_load_kw"].to_numpy(float)
    pv = annual["pv_available_kw"].to_numpy(float)
    deficit = np.maximum(ALPHA * load - pv, 0.0)
    windows = np.convolve(deficit, np.ones(BETA_H), mode="valid")
    binding = int(np.argmax(windows))
    reserve = float(windows[binding] / eta_d)
    return {
        "case_id": CASE_ID,
        "alpha": ALPHA,
        "beta_h": BETA_H,
        "P_out_kw_ac": float(deficit.max()),
        "R_kwh_battery": reserve,
        "analytical_E_N_min_kwh": reserve / (soc_max - soc_min),
        "binding_start_index": binding,
        "binding_historical_start": timestamps.iloc[binding],
        "binding_historical_end_exclusive": timestamps.iloc[binding] + pd.Timedelta(hours=BETA_H),
        "valid_start_count": len(windows),
        "expected_valid_start_count": len(annual) - BETA_H + 1,
        "no_circular_wrap": True,
        "derivation_scope": "SINGLE_ACCEPTED_CASE_ONLY; EXACT_SCRIPT_16A_FORMULA; NO_81_POINT_SURFACE",
    }


def strip_result(result: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in result.items() if key not in {"dispatch", "billing_exact", "transition_settlement_detail"}}


def rainflow_json(validation: dict[str, Any]) -> dict[str, Any]:
    return {
        "summary": validation["summary"],
        "gates": validation["gates"],
        "algorithm_self_test": validation["algorithm_self_test"],
    }


def base_solve_gates(result: dict[str, Any], billing: dict[str, Any], rainflow: dict[str, Any]) -> dict[str, str]:
    phys = result.get("physical_diagnostics", {})
    transition = result.get("transition_settlement", {})
    rainflow_pass = (
        rainflow["summary"].get("verdict") == "RAINFLOW_VALIDATION_PASS"
        and all(value == "PASS" for value in rainflow["gates"].values())
    )
    return {
        "solver_optimal": "PASS" if result.get("status") == "OPTIMAL" else "FAIL",
        "binary_formulation": "PASS" if result.get("mode") == "binary" else "FAIL",
        "mip_gap": "PASS" if result.get("mip_gap") is not None and float(result["mip_gap"]) <= MIP_GAP else "FAIL",
        "ac_balance": "PASS" if abs(float(phys.get("max_ac_balance_residual_kw", math.inf))) <= 1e-5 else "FAIL",
        "segment_dynamics": "PASS" if abs(float(phys.get("max_segment_dynamics_residual_kwh", math.inf))) <= 1e-5 else "FAIL",
        "segment_cyclic": "PASS" if abs(float(phys.get("max_segment_cyclic_residual_kwh", math.inf))) <= 1e-5 else "FAIL",
        "technical_soc": "PASS" if float(phys.get("soc_min_realized", -math.inf)) >= 0.1 - TOL and float(phys.get("soc_max_realized", math.inf)) <= 0.9 + TOL else "FAIL",
        "simultaneous_charge_discharge": "PASS" if int(phys.get("simultaneous_hours_above_tol", -1)) == 0 else "FAIL",
        "cost_reconciliation": "PASS" if abs(float(result.get("cost_reconciliation_residual_ntd", math.inf))) <= 1e-3 else "FAIL",
        "transition_ambiguity": "PASS" if transition.get("nonbinding_certificate") == "PASS_NO_RATE_AMBIGUOUS_INCREMENTAL_OVERAGE" else "FAIL",
        "billing_period_ids": billing["period_ids"],
        "billing_detail_columns": billing["detail_columns"],
        "billing_detail_key_validity": billing["valid_detail_keys"],
        "billing_detail_key_duplicates": billing["duplicate_detail_keys"],
        "billing_tariff_calendar_structure": billing["tariff_calendar_structure"],
        "billing_row_count": "PASS" if billing["actual_row_count"] == billing["expected_row_count"] else "FAIL",
        "rainflow_validation": "PASS" if rainflow_pass else "FAIL",
    }


def write_solution_outputs(run_dir: Path, prefix: str, result: dict[str, Any], audit: dict[str, Any], rainflow: dict[str, Any]) -> list[Path]:
    paths = [
        run_dir / f"{prefix}_result.json",
        run_dir / f"{prefix}_post_solve_audit.json",
        run_dir / f"{prefix}_rainflow_audit.json",
        run_dir / f"{prefix}_dispatch.parquet",
        run_dir / f"{prefix}_billing_exact.csv",
        run_dir / f"{prefix}_transition_settlement_detail.csv",
        run_dir / f"{prefix}_rainflow_cycles.csv",
        run_dir / f"{prefix}_rainflow_turning_points.csv",
        run_dir / f"{prefix}_rainflow_depth_bins.csv",
        run_dir / f"{prefix}_rainflow_pwl_segments.csv",
        run_dir / f"{prefix}_rainflow_g_curve.csv",
    ]
    write_json(paths[0], strip_result(result))
    write_json(paths[1], audit)
    write_json(paths[2], rainflow_json(rainflow))
    result["dispatch"].to_parquet(paths[3], index=False)
    result["billing_exact"].to_csv(paths[4], index=False, encoding="utf-8-sig")
    result["transition_settlement_detail"].to_csv(paths[5], index=False, encoding="utf-8-sig")
    for frame, path in zip(
        [rainflow["cycles"], rainflow["turning_points"], rainflow["depth_bins"], rainflow["pwl_segments"], rainflow["g_curve"]],
        paths[6:],
    ):
        frame.to_csv(path, index=False, encoding="utf-8-sig")
    return paths


def pv_metrics(dispatch: pd.DataFrame) -> dict[str, float]:
    available = float(dispatch["pv_available_kw"].sum())
    curtailed = float(dispatch["pv_curtailment_kw"].sum())
    return {"pv_available_kwh": available, "pv_used_kwh": available - curtailed, "pv_curtailment_kwh": curtailed}


def demand_metrics(dispatch: pd.DataFrame, billing: pd.DataFrame) -> dict[str, float]:
    return {
        "max_grid_import_kw": float(dispatch["p_grid_kw"].max()),
        "max_exact_billing_demand_kw": float(billing["exact_billing_demand_kw"].max()),
        "max_overall_exact_billing_demand_kw": float(billing["overall_exact_billing_demand_kw"].max()),
    }


def scenario_metrics(result: dict[str, Any], dispatch: pd.DataFrame, billing: pd.DataFrame, package: dict[str, Any]) -> dict[str, float]:
    sizing = result["sizing"]
    costs = result["cost_components_ntd2023_per_year"]
    annual = result["annual_energy"]
    e_n, p_b = float(sizing["E_N_kwh"]), float(sizing["P_B_kw_ac"])
    metrics = {
        "objective_ntd2023_per_year": float(result["objective_ntd2023_per_year"]),
        "E_N_kwh": e_n,
        "P_B_kw_ac": p_b,
        "CC_regular_kw": float(sizing["CC_regular_kw"]),
        "annualized_capex": float(costs["annualized_capex"]),
        "annualized_capex_energy": float(package["annualized_capex_C_E_ntd2023_per_kwh_year"]) * e_n,
        "annualized_capex_power": float(package["annualized_capex_C_P_ntd2023_per_kw_year"]) * p_b,
        "fom": float(costs["fom"]),
        "fom_energy": float(package["fom_E_ntd2023_per_kwh_year"]) * e_n,
        "fom_power": float(package["fom_P_ntd2023_per_kw_year"]) * p_b,
        "energy": float(costs["energy"]),
        "basic": float(costs["basic"]),
        "overcontract_pure_season": float(costs["overcontract_pure_season"]),
        "overcontract_transition_resolved": float(costs["overcontract_transition_resolved"]),
        "degradation": float(costs["degradation"]),
        "grid_import_kwh": float(annual["grid_import_kwh"]),
        "charge_ac_kwh": float(annual["charge_ac_kwh"]),
        "discharge_ac_kwh": float(annual["discharge_ac_kwh"]),
        "battery_side_discharge_kwh": float(annual["battery_side_discharge_kwh"]),
    }
    metrics.update(pv_metrics(dispatch))
    metrics.update(demand_metrics(dispatch, billing))
    return metrics


def comparison_rows(label: str, main: dict[str, float], alternative: dict[str, float]) -> list[dict[str, Any]]:
    rows = []
    for metric in main:
        delta = alternative[metric] - main[metric]
        pct = 100.0 * delta / main[metric] if main[metric] != 0 else None
        rows.append({"scenario": label, "metric": metric, "mainline": main[metric], "winter_pv": alternative[metric], "delta": delta, "percent_change": pct})
    return rows


def telemetry_writer(path: Path, solve_id: str) -> Callable[[dict[str, Any]], None]:
    def emit(record: dict[str, Any]) -> None:
        payload = {"timestamp_utc": utc_text(), "solve_id": solve_id, **record}
        with path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(json_safe(payload), sort_keys=True) + "\n")
            handle.flush()
    return emit


def artifact_registry(run_dir: Path) -> dict[str, Any]:
    records: dict[str, Any] = {}
    for path in sorted(run_dir.iterdir()):
        if path.is_file() and path.name not in {"completion_manifest.json", "failure_manifest.json"}:
            records[path.name] = {"path": str(path.relative_to(root_path())).replace("\\", "/"), "sha256": sha256_file(path), "bytes": path.stat().st_size}
    return records


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--authority-validation",
        action="store_true",
        help="Validate corrected authority and input fairness without constructing a model or writing outputs.",
    )
    return parser.parse_args()


def validate_authority(root: Path) -> tuple[dict[str, Any], pd.DataFrame, dict[str, Any]]:
    hashes = check_hashes(root)
    repository = check_repository(root)
    chain = verify_accepted_chain(root)
    canonical = pd.read_parquet(root / ACTIVE_HASHES["canonical_annual"][0])
    canonical_load_route = "HASH_PINNED_CANONICAL_PARQUET"
    alternative = pd.read_parquet(root / ACTIVE_HASHES["alternative_annual"][0])
    fairness = fairness_audit(canonical, alternative)
    comparators = load_current_comparators(root)
    report = {
        "status": "PASS",
        "mode": "READ_ONLY_NO_SOLVE_NO_WRITE",
        "script_version": SCRIPT_VERSION,
        "active_hashes": hashes,
        "repository": repository,
        "accepted_chain": chain,
        "canonical_load_route": canonical_load_route,
        "input_fairness": fairness,
        "current_comparators": comparators["checks"],
        "historical_provenance_active": False,
        "model_construction_attempts": 0,
        "optimization_attempts": 0,
        "solve_eob_calls": 0,
        "output_directories_created": 0,
    }
    return report, alternative, comparators


def main() -> int:
    args = parse_args()
    root = root_path()
    sys.path.insert(0, str(root))
    started = utc_now()
    run_id = f"{started.strftime('%Y%m%dT%H%M%S%fZ')}_{uuid.uuid4().hex[:10]}"
    run_dir: Path | None = None
    solve_count = 0
    try:
        authority, alternative, comparators = validate_authority(root)
        if args.authority_validation:
            print(json.dumps(json_safe(authority), indent=2))
            return 0

        from src.annual_design_model_v7_2 import (
            CORE_VERSION, ETA_D, SOC_MAX, SOC_MIN,
            LayerAResilienceRequirements, SolveSettings,
            load_annual_design_inputs, solve_eob,
        )
        if CORE_VERSION != EXPECTED_CORE_VERSION:
            raise RuntimeError(f"Core version mismatch: {CORE_VERSION}")

        fairness = authority["input_fairness"]
        requirement = single_case_requirement(alternative, float(ETA_D), float(SOC_MIN), float(SOC_MAX))
        if requirement["valid_start_count"] != requirement["expected_valid_start_count"]:
            raise RuntimeError("Single-case all-start enumeration failed.")

        main_eob = comparators["eob_result"]
        main_layer_record = comparators["layer_record"]
        main_layer = comparators["layer_result"]

        inputs = load_annual_design_inputs(
            root,
            annual_parquet=root / ACTIVE_HASHES["alternative_annual"][0],
            annual_csv=root / "data/processed/alternatives/DO_NOT_FALL_BACK.csv",
        )
        if Path(inputs.source_paths["annual_input"]).resolve() != (root / ACTIVE_HASHES["alternative_annual"][0]).resolve():
            raise RuntimeError("Loader did not bind to the accepted alternative annual input.")
        package = inputs.mainline_package
        package_checks = {
            "mainline_role": package.get("role") == "mainline",
            "ten_mw_package": float(package.get("power_scale_bracket_mw", -1)) == 10.0,
            "currency": package.get("currency") == "NTD",
            "currency_base_year": int(package.get("currency_base_year", -1)) == 2023,
        }
        if not all(package_checks.values()):
            raise RuntimeError(f"Economic-package gate failed: {package_checks}")

        run_dir = root / "results/sensitivity/winter_pv_17c" / run_id
        run_dir.mkdir(parents=True, exist_ok=False)
        script_hash = sha256_file(Path(__file__).resolve())
        preflight = {
            "script_version": SCRIPT_VERSION,
            "script_sha256": script_hash,
            "generated_utc": utc_text(),
            "status": "PASS",
            "solve_boundary": {"authorized_solves": ["alternative_EOB", CASE_ID], "exact_solve_count": 2, "canonical_re_solve": False, "matrix_81_point": False},
            "repository": authority["repository"],
            "active_hashes": authority["active_hashes"],
            "accepted_chain": authority["accepted_chain"],
            "input_fairness": fairness,
            "single_case_analytical_requirement": requirement,
            "economic_package_checks": {key: "PASS" if value else "FAIL" for key, value in package_checks.items()},
            "solver_settings": {"mode": "binary", "MIPGap": MIP_GAP, "TimeLimit": TIME_LIMIT_SEC, "NumericFocus": 1},
            "mainline_eob_comparator_qualification": "CURRENT_CORRECTED_EOB_ACCEPTED_PRODUCTION_AUTHORITY",
            "mainline_layer_comparator_qualification": "CURRENT_AUDITED_EXACT_A0.80_B08_REPRESENTATIVE_CASE",
            "historical_provenance_active": False,
        }
        write_json(run_dir / "pre_solve_gate.json", preflight)
        write_json(run_dir / "run_manifest.json", {
            "run_id": run_id, "script_version": SCRIPT_VERSION, "script_sha256": script_hash,
            "started_utc": utc_text(started), "output_directory": str(run_dir.relative_to(root)).replace("\\", "/"),
            "input_role": "winter_pv_sensitivity_only", "authorized_solve_count": 2,
            "authorized_cases": ["alternative_EOB", CASE_ID], "mainline_solve_count": 0,
            "claim_boundary": "PAIRED_SENSITIVITY_ONLY; NO_HISTORICAL_TRUTH_OR_UNIVERSAL_MATERIALITY_CLAIM",
        })

        helper = load_module(root / ACTIVE_HASHES["script_16a"][0], "script16a_17c_helpers")
        eob_settings = SolveSettings(
            mode="binary", mip_gap=MIP_GAP, time_limit_sec=TIME_LIMIT_SEC, output_flag=1,
            numeric_focus=1, log_file=str(run_dir / "alternative_eob_gurobi.log"),
            telemetry_callback=telemetry_writer(run_dir / "alternative_eob_telemetry.jsonl", "alternative_EOB"),
        )
        eob_started = time.perf_counter()
        alternative_eob = solve_eob(inputs, eob_settings, None)
        solve_count += 1
        eob_rainflow = helper.validate_representative_rainflow(root, inputs, alternative_eob)
        eob_billing = helper.billing_structure_audit(alternative_eob["billing_exact"], inputs.annual)
        eob_gates = base_solve_gates(alternative_eob, eob_billing, eob_rainflow)
        if not all(value == "PASS" for value in eob_gates.values()):
            raise RuntimeError(f"Alternative EOB post-solve gate failure: {eob_gates}")
        eob_audit = {"status": "PASS", "elapsed_wall_seconds": time.perf_counter() - eob_started, "gates": eob_gates, "billing_audit": eob_billing}
        write_solution_outputs(run_dir, "alternative_eob", alternative_eob, eob_audit, eob_rainflow)

        layer_requirement = LayerAResilienceRequirements(
            alpha=ALPHA, beta_h=BETA_H,
            reserve_kwh_battery=float(requirement["R_kwh_battery"]),
            power_requirement_kw_ac=float(requirement["P_out_kw_ac"]),
        )
        layer_settings = SolveSettings(
            mode="binary", mip_gap=MIP_GAP, time_limit_sec=TIME_LIMIT_SEC, output_flag=1,
            numeric_focus=1, log_file=str(run_dir / "alternative_layer_a0.80_b08_gurobi.log"),
            telemetry_callback=telemetry_writer(run_dir / "alternative_layer_a0.80_b08_telemetry.jsonl", CASE_ID),
        )
        layer_started = time.perf_counter()
        alternative_layer = solve_eob(inputs, layer_settings, layer_requirement)
        solve_count += 1
        layer_rainflow = helper.validate_representative_rainflow(root, inputs, alternative_layer)
        layer_billing = helper.billing_structure_audit(alternative_layer["billing_exact"], inputs.annual)
        layer_gates = helper.representative_gate(
            alternative_layer, requirement, alternative_eob,
            soc_min=float(SOC_MIN), soc_max=float(SOC_MAX),
            rainflow_validation=layer_rainflow, billing_audit=layer_billing,
        )
        layer_gates.update({
            "all_start_enumeration": "PASS" if requirement["valid_start_count"] == 8753 and requirement["no_circular_wrap"] else "FAIL",
            "exact_case_identity": "PASS" if alternative_layer.get("layer_a_resilience", {}).get("alpha") == ALPHA and alternative_layer.get("layer_a_resilience", {}).get("beta_h") == BETA_H else "FAIL",
        })
        if not all(value == "PASS" for value in layer_gates.values()):
            raise RuntimeError(f"Alternative Layer-A post-solve gate failure: {layer_gates}")
        layer_audit = {"status": "PASS", "elapsed_wall_seconds": time.perf_counter() - layer_started, "gates": layer_gates, "billing_audit": layer_billing, "analytical_requirement": requirement}
        write_solution_outputs(run_dir, "alternative_layer_a0.80_b08", alternative_layer, layer_audit, layer_rainflow)

        main_eob_dispatch = pd.read_csv(root / ACTIVE_HASHES["current_eob_dispatch"][0])
        main_eob_billing = pd.read_csv(root / ACTIVE_HASHES["current_eob_billing"][0])
        main_layer_dispatch = pd.read_csv(root / ACTIVE_HASHES["current_layer_dispatch"][0])
        main_layer_billing = pd.read_csv(root / ACTIVE_HASHES["current_layer_billing"][0])
        main_eob_metrics = scenario_metrics(main_eob, main_eob_dispatch, main_eob_billing, package)
        alt_eob_metrics = scenario_metrics(alternative_eob, alternative_eob["dispatch"], alternative_eob["billing_exact"], package)
        main_layer_metrics = scenario_metrics(main_layer, main_layer_dispatch, main_layer_billing, package)
        alt_layer_metrics = scenario_metrics(alternative_layer, alternative_layer["dispatch"], alternative_layer["billing_exact"], package)
        rows = comparison_rows("EOB", main_eob_metrics, alt_eob_metrics) + comparison_rows(CASE_ID, main_layer_metrics, alt_layer_metrics)
        comparison_csv = run_dir / "paired_sensitivity_comparison.csv"
        pd.DataFrame(rows).to_csv(comparison_csv, index=False, encoding="utf-8-sig")

        main_premium = main_layer_metrics["objective_ntd2023_per_year"] - main_eob_metrics["objective_ntd2023_per_year"]
        alt_premium = alt_layer_metrics["objective_ntd2023_per_year"] - alt_eob_metrics["objective_ntd2023_per_year"]
        comparison = {
            "status": "PASS",
            "monetary_basis": "constant NTD-2023 per year",
            "mainline_comparators": {"EOB": main_eob_metrics, CASE_ID: main_layer_metrics},
            "winter_pv_sensitivity": {"EOB": alt_eob_metrics, CASE_ID: alt_layer_metrics},
            "resilience_premium": {
                "mainline_ntd2023_per_year": main_premium,
                "winter_pv_ntd2023_per_year": alt_premium,
                "delta_ntd2023_per_year": alt_premium - main_premium,
                "mainline_pct_of_eob": 100.0 * main_premium / main_eob_metrics["objective_ntd2023_per_year"],
                "winter_pv_pct_of_eob": 100.0 * alt_premium / alt_eob_metrics["objective_ntd2023_per_year"],
            },
            "reconciliation": {
                "EOB_component_delta_minus_objective_delta_ntd": sum(alt_eob_metrics[key] - main_eob_metrics[key] for key in ["annualized_capex", "fom", "energy", "basic", "overcontract_pure_season", "overcontract_transition_resolved", "degradation"]) - (alt_eob_metrics["objective_ntd2023_per_year"] - main_eob_metrics["objective_ntd2023_per_year"]),
                "LayerA_component_delta_minus_objective_delta_ntd": sum(alt_layer_metrics[key] - main_layer_metrics[key] for key in ["annualized_capex", "fom", "energy", "basic", "overcontract_pure_season", "overcontract_transition_resolved", "degradation"]) - (alt_layer_metrics["objective_ntd2023_per_year"] - main_layer_metrics["objective_ntd2023_per_year"]),
            },
            "interpretation_boundary": "Observed deltas apply only to this accepted Winter-PV sensitivity input and these two paired cases; they do not establish historical truth or a universal materiality threshold.",
        }
        if max(abs(value) for value in comparison["reconciliation"].values()) > 1e-3:
            raise RuntimeError(f"Paired cost decomposition does not reconcile: {comparison['reconciliation']}")
        write_json(run_dir / "paired_sensitivity_comparison.json", comparison)

        if solve_count != 2:
            raise RuntimeError(f"Solve count is {solve_count}, expected exactly 2.")
        outputs = artifact_registry(run_dir)
        completion = {
            "run_id": run_id,
            "script_version": SCRIPT_VERSION,
            "script_sha256": script_hash,
            "completed_utc": utc_text(),
            "status": "PASS",
            "final_verdict": "17C WINTER-PV ECONOMIC SENSITIVITY PASS — P1 CLOSED",
            "solve_count": solve_count,
            "solve_boundary": {"alternative_eob": 1, CASE_ID: 1, "mainline": 0, "other_layer_cases": 0, "matrix_81_point": 0},
            "all_post_solve_gates_pass": True,
            "alternative_eob_gates": eob_gates,
            "alternative_layer_gates": layer_gates,
            "artifact_registry": outputs,
            "claim_boundary": comparison["interpretation_boundary"],
            "git_actions": {"staged": False, "committed": False, "tagged": False, "pushed": False},
        }
        write_json(run_dir / "completion_manifest.json", completion)
        print(json.dumps({"verdict": completion["final_verdict"], "run_id": run_id, "run_dir": str(run_dir), "solve_count": solve_count}, indent=2))
        return 0
    except Exception as exc:
        if run_dir is not None and run_dir.exists():
            failure = run_dir / "failure_manifest.json"
            if not failure.exists():
                write_json(failure, {
                    "run_id": run_id, "script_version": SCRIPT_VERSION, "failed_utc": utc_text(),
                    "status": "FAIL", "final_verdict": "17C WINTER-PV ECONOMIC SENSITIVITY FAIL — P1 REMAINS OPEN",
                    "solve_count_at_failure": solve_count, "exception_type": type(exc).__name__, "exception_message": str(exc),
                    "completion_manifest_written": False,
                })
        raise


if __name__ == "__main__":
    raise SystemExit(main())
