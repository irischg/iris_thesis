"""No-solve tests for Script 16a's explicit current EOB comparator authority."""

from __future__ import annotations

import ast
import hashlib
import importlib.util
import json
import subprocess
import sys
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "16a_preflight_layer_a_representative_binary_cases.py"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_script():
    spec = importlib.util.spec_from_file_location("script16a_current_authority_test", SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError("Could not load Script 16a.")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class CurrentEobAuthorityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.script = load_script()

    def test_current_comparator_resolves_exact_accepted_run(self) -> None:
        result, authority, paths = self.script.current_corrected_eob(ROOT)
        self.assertEqual(
            self.script.SCRIPT_VERSION,
            "v7.2-layer-a-analytical-representative-binary-preflight-current-eob-authority-2026-09-17-r11",
        )
        self.assertEqual(authority["authority_role"], "CURRENT_CORRECTED_EOB_COMPARATOR")
        self.assertEqual(authority["run_id"], "20260917T082758521112Z_a4b6383308")
        self.assertEqual(
            authority["result_sha256"],
            "d7c37a0013ad6ea5a8dc3231a67bf427ec0c502aef96fedc47aacfe7c8897022",
        )
        self.assertEqual(
            authority["run_manifest_sha256"],
            "9acb3f52948c63e65c29baf3f8a84653d127febf96369f1945cbb358389eb99a",
        )
        self.assertEqual(
            authority["core_version"],
            "v7.2-annual-design-core-transition-candidate1-exact-d-preflight-2026-09-16-r10",
        )
        self.assertEqual(
            authority["core_sha256"],
            "9d828321814b09141497056d1bb17da8b2839c5eb151fce8530059fb7e193da8",
        )
        self.assertEqual(result["objective_ntd2023_per_year"], 66708197.09463947)
        self.assertEqual(sha256(paths["current_eob_result"]), authority["result_sha256"])
        self.assertFalse(authority["historical_fallback_allowed"])

    def test_acceptance_checkpoint_and_r3_evidence_are_hash_valid(self) -> None:
        _result, authority, paths = self.script.current_corrected_eob(ROOT)
        self.assertEqual(
            sha256(paths["current_eob_acceptance_checkpoint"]),
            authority["acceptance_checkpoint_sha256"],
        )
        self.assertEqual(sha256(paths["accepted_r3_delta"]), authority["r3_delta_sha256"])
        self.assertEqual(
            sha256(paths["accepted_r3_package_manifest"]),
            authority["r3_package_manifest_sha256"],
        )
        self.assertEqual(
            sha256(paths["accepted_r3_checkpoint"]), authority["r3_checkpoint_sha256"]
        )

    def test_missing_corrected_result_never_falls_back_to_historical(self) -> None:
        missing = Path("results/eob_production_corrected/runs/DOES_NOT_EXIST/result.json")
        with patch.object(self.script, "CURRENT_CORRECTED_EOB_RESULT", missing):
            with self.assertRaises(FileNotFoundError):
                self.script.current_corrected_eob(ROOT)

    def test_historical_comparator_remains_explicit_and_distinct(self) -> None:
        historical, audit, historical_paths = self.script.historical_eob(ROOT)
        legacy, legacy_audit, legacy_paths = self.script.canonical_eob(ROOT)
        corrected, authority, corrected_paths = self.script.current_corrected_eob(ROOT)
        self.assertEqual(audit["freeze_status"], "PRODUCTION_EOB_FREEZE_PASS")
        self.assertEqual(historical, legacy)
        self.assertEqual(legacy_audit, audit)
        self.assertEqual(legacy_paths, historical_paths)
        self.assertIn("historical_eob_result", historical_paths)
        self.assertIn("current_eob_result", corrected_paths)
        self.assertNotEqual(
            historical["objective_ntd2023_per_year"], corrected["objective_ntd2023_per_year"]
        )
        self.assertEqual(authority["authority_role"], "CURRENT_CORRECTED_EOB_COMPARATOR")

    def test_historical_files_and_expected_reference_are_unchanged(self) -> None:
        expected = {
            "results/eob_production/eob_production_result_v7_2.json":
                "ad606a503b3f68ceba048e4b94bc0e19e6ddde00f88c145d051f772557e0bd56",
            "results/eob_production/eob_production_freeze_audit_v7_2.json":
                "18bf93414dcc677bdd4ab68b99aae3c0af9412ea52c950eaf8f186b075822907",
            "scripts/15b_freeze_production_eob_baseline.py":
                "9a5f61d19bc279920f51f67294ef96ddcd7623ffe240482ff66b88e029eafc60",
            "scripts/15c_validate_production_eob_rainflow.py":
                "14fd9f3363979dd6af6f50723a75477e1525b9330265a0a820d11eec1774f408",
        }
        for relative, digest in expected.items():
            self.assertEqual(sha256(ROOT / relative), digest, relative)
        source15c = (ROOT / "scripts/15c_validate_production_eob_rainflow.py").read_text(
            encoding="utf-8"
        )
        self.assertIn("EXPECTED_EOB_REFERENCE", source15c)
        self.assertIn("66738326.341512", source15c)

    def test_authority_validation_path_is_real_and_model_free(self) -> None:
        source = SCRIPT.read_text(encoding="utf-8")
        tree = ast.parse(source)
        functions = {
            node.name: node for node in tree.body if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        }
        loader_calls = {
            node.func.id
            for node in ast.walk(functions["current_corrected_eob"])
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
        }
        self.assertTrue(
            loader_calls.isdisjoint({"solve_eob", "build_eob_model", "Model", "optimize"})
        )
        self.assertLess(
            source.index('if args.mode == "authority-validation"'),
            source.index("from src.annual_design_model_v7_2 import CORE_VERSION"),
        )

        output = ROOT / "results" / "provenance" / "__16a_authority_validation_must_not_create__"
        self.assertFalse(output.exists())
        completed = subprocess.run(
            [
                sys.executable,
                "-B",
                str(SCRIPT),
                "--mode",
                "authority-validation",
                "--output-dir",
                str(output),
            ],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["status"], "PASS")
        self.assertEqual(payload["validation_mode"], "NO_SOLVE_CURRENT_EOB_AUTHORITY")
        self.assertEqual(
            payload["authority"]["run_id"], "20260917T082758521112Z_a4b6383308"
        )
        self.assertEqual(
            payload["execution_counters"],
            {
                "optimization_calls": 0,
                "model_creations": 0,
                "solve_eob_calls": 0,
                "layer_a_runs": 0,
                "sensitivity_runs": 0,
                "case81_runs": 0,
            },
        )
        self.assertFalse(output.exists())

    def test_corrected_rainflow_is_not_a_comparator_dependency(self) -> None:
        _result, authority, paths = self.script.current_corrected_eob(ROOT)
        self.assertFalse(authority["corrected_rainflow_required"])
        self.assertFalse(any("rainflow" in key for key in paths))


if __name__ == "__main__":
    unittest.main()
