from __future__ import annotations

import ast
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "17c_run_winter_pv_economic_sensitivity.py"


def load_script():
    spec = importlib.util.spec_from_file_location("script17c_authority_test", SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class CorrectedAuthorityAlignmentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = load_script()

    def test_active_and_historical_dependency_sets_are_disjoint(self) -> None:
        active_paths = {record[0] for record in self.module.ACTIVE_HASHES.values()}
        historical_paths = {
            record[0] for record in self.module.HISTORICAL_PROVENANCE_HASHES.values()
        }
        self.assertTrue(active_paths.isdisjoint(historical_paths))
        self.assertIn(
            "results/eob_production_corrected/runs/20260917T082758521112Z_a4b6383308/corrected_eob_result.json",
            active_paths,
        )
        self.assertIn(
            "results/eob_production/eob_production_result_v7_2.json",
            historical_paths,
        )

    def test_authority_validator_source_has_no_solve_or_write_calls(self) -> None:
        tree = ast.parse(SCRIPT.read_text(encoding="utf-8"))
        validator = next(
            node
            for node in tree.body
            if isinstance(node, ast.FunctionDef) and node.name == "validate_authority"
        )
        called = {
            node.func.attr if isinstance(node.func, ast.Attribute) else node.func.id
            for node in ast.walk(validator)
            if isinstance(node, ast.Call)
            and isinstance(node.func, (ast.Attribute, ast.Name))
        }
        self.assertTrue(
            called.isdisjoint(
                {"solve_eob", "optimize", "optimizeAsync", "optimizeBatch", "mkdir", "write_json"}
            )
        )

    def test_authority_validation_cli_is_read_only_and_passes(self) -> None:
        output_root = ROOT / "results" / "sensitivity" / "winter_pv_17c"
        before = sorted(path.name for path in output_root.iterdir()) if output_root.exists() else []
        completed = subprocess.run(
            [sys.executable, "-B", str(SCRIPT), "--authority-validation"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["status"], "PASS")
        self.assertEqual(payload["mode"], "READ_ONLY_NO_SOLVE_NO_WRITE")
        self.assertFalse(payload["historical_provenance_active"])
        self.assertEqual(payload["model_construction_attempts"], 0)
        self.assertEqual(payload["optimization_attempts"], 0)
        self.assertEqual(payload["solve_eob_calls"], 0)
        after = sorted(path.name for path in output_root.iterdir()) if output_root.exists() else []
        self.assertEqual(after, before)


if __name__ == "__main__":
    unittest.main()
