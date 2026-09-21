"""No-solve tests for the additive 1 MW BESS cost-scale sensitivity runner."""

from __future__ import annotations

import ast
import contextlib
import copy
from dataclasses import dataclass
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "17d_run_bess_cost_scale_sensitivity.py"
CORE = ROOT / "src" / "annual_design_model_v7_2.py"
INTERFACE = ROOT / "data" / "reference" / "production_economic_interface_v7_2.json"


def load_script():
    spec = importlib.util.spec_from_file_location("script17d_cost_scale_test", SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot import {SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


runner = load_script()


@dataclass(frozen=True)
class FakeAnnualInputs:
    mainline_package: dict
    physical_marker: object


class BessCostScaleSensitivityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        interface = json.loads(INTERFACE.read_text(encoding="utf-8-sig"))
        cls.sensitivity = interface["package_selector"]["cost_scale_sensitivity"]
        cls.mainline = interface["package_selector"]["mainline"]
        cls.authority = runner.validate_authority(ROOT)

    # A. Package selection.
    def test_a_authoritative_1mw_package_is_selected_explicitly(self) -> None:
        audit = runner.validate_sensitivity_package(self.sensitivity, self.mainline)
        self.assertEqual(audit["status"], "PASS")
        self.assertEqual(audit["package_id"], runner.EXPECTED_SENSITIVITY_PACKAGE_ID)
        self.assertEqual(
            audit["package_object_sha256"], runner.EXPECTED_SENSITIVITY_PACKAGE_SHA256
        )

    def test_a_10mw_package_is_rejected_as_sensitivity_target(self) -> None:
        with self.assertRaises(runner.SensitivityAuthorityError):
            runner.validate_sensitivity_package(
                self.mainline,
                self.mainline,
                expected_hash=runner.EXPECTED_MAINLINE_PACKAGE_SHA256,
            )

    def test_a_wrong_hash_role_and_bracket_are_rejected(self) -> None:
        wrong_hash = copy.deepcopy(self.sensitivity)
        wrong_hash["capex_C_E_ntd2023_per_kwh"] += 1.0
        with self.assertRaisesRegex(runner.SensitivityAuthorityError, "hash mismatch"):
            runner.validate_sensitivity_package(wrong_hash, self.mainline)

        for field, value in (("role", "mainline"), ("power_scale_bracket_mw", 10.0)):
            with self.subTest(field=field):
                package = copy.deepcopy(self.sensitivity)
                package[field] = value
                object_hash = runner.canonical_object_sha256(package)
                with self.assertRaises(runner.SensitivityAuthorityError):
                    runner.validate_sensitivity_package(
                        package, self.mainline, expected_hash=object_hash
                    )

    # B. Full-package atomicity.
    def test_b_each_required_cost_or_degradation_field_rejects_mixing(self) -> None:
        required_atomic_fields = (
            "capex_C_E_ntd2023_per_kwh",
            "capex_C_P_ntd2023_per_kw",
            "fom_E_ntd2023_per_kwh_year",
            "fom_P_ntd2023_per_kw_year",
            "crep_ntd2023_per_kwh",
            "lambda_1_ntd2023_per_battery_side_discharged_kwh",
            "lambda_2_ntd2023_per_battery_side_discharged_kwh",
            "lambda_3_ntd2023_per_battery_side_discharged_kwh",
        )
        for field in required_atomic_fields:
            with self.subTest(field=field):
                mixed = copy.deepcopy(self.sensitivity)
                mixed[field] = self.mainline[field]
                with self.assertRaises(runner.SensitivityAuthorityError):
                    runner.validate_sensitivity_package(
                        mixed,
                        self.mainline,
                        expected_hash=runner.canonical_object_sha256(mixed),
                    )

    def test_b_copy_adapter_is_atomic_and_does_not_mutate_canonical_inputs(self) -> None:
        marker = object()
        canonical = FakeAnnualInputs(copy.deepcopy(self.mainline), marker)
        original_hash = runner.canonical_object_sha256(canonical.mainline_package)
        adapted, selected = runner.adapt_inputs_to_1mw(canonical, self.sensitivity)
        self.assertIsNot(adapted, canonical)
        self.assertIs(adapted.mainline_package, selected)
        self.assertIs(adapted.physical_marker, marker)
        self.assertEqual(
            runner.canonical_object_sha256(adapted.mainline_package),
            runner.EXPECTED_SENSITIVITY_PACKAGE_SHA256,
        )
        self.assertEqual(
            runner.canonical_object_sha256(canonical.mainline_package), original_hash
        )

    # C. Lambda lineage.
    def test_c_lambda_lineage_is_derived_from_selected_1mw_crep(self) -> None:
        c_rep = float(self.sensitivity["crep_ntd2023_per_kwh"])
        expected = (
            (c_rep / 32000.0) / 0.30,
            (c_rep / 8000.0 - c_rep / 32000.0) / 0.30,
            (c_rep / 4800.0 - c_rep / 8000.0) / 0.20,
        )
        actual = tuple(
            float(
                self.sensitivity[
                    f"lambda_{index}_ntd2023_per_battery_side_discharged_kwh"
                ]
            )
            for index in range(1, 4)
        )
        for actual_value, expected_value in zip(actual, expected, strict=True):
            self.assertAlmostEqual(actual_value, expected_value, places=12)

        contaminated = copy.deepcopy(self.sensitivity)
        contaminated["lambda_2_ntd2023_per_battery_side_discharged_kwh"] += 0.01
        with self.assertRaises(runner.SensitivityAuthorityError):
            runner.validate_sensitivity_package(
                contaminated,
                self.mainline,
                expected_hash=runner.canonical_object_sha256(contaminated),
            )

    # D. No legacy contamination.
    def test_d_known_legacy_coefficients_are_rejected_explicitly(self) -> None:
        legacy_field_values = (
            ("annualized_capex_C_E_ntd2023_per_kwh_year", 813.75),
            ("annualized_capex_C_P_ntd2023_per_kw_year", 694.4),
            ("crep_ntd2023_per_kwh", 5107.57),
            ("lambda_1_ntd2023_per_battery_side_discharged_kwh", 0.532),
            ("lambda_2_ntd2023_per_battery_side_discharged_kwh", 1.596),
            ("lambda_3_ntd2023_per_battery_side_discharged_kwh", 2.128),
        )
        for field, legacy_value in legacy_field_values:
            with self.subTest(field=field):
                contaminated = copy.deepcopy(self.sensitivity)
                contaminated[field] = legacy_value
                with self.assertRaisesRegex(
                    runner.SensitivityAuthorityError, "Legacy contamination"
                ):
                    runner.validate_sensitivity_package(
                        contaminated,
                        self.mainline,
                        expected_hash=runner.canonical_object_sha256(contaminated),
                    )

    # E. Fair-comparison freeze.
    def test_e_fair_comparison_and_authority_pins_are_frozen(self) -> None:
        authority = self.authority
        self.assertEqual(authority["canonical_input"]["sha256"], "9142b8b6f81b3f423c4ab43ac049765b3e934aae57d33c761208f3452598518e")
        self.assertEqual(authority["canonical_input"]["winter_pv_treatment"], "MAINLINE_CONSERVATIVE_ZERO")
        self.assertFalse(authority["canonical_input"]["alternative_input_used"])
        self.assertEqual(authority["fair_comparison"]["soc_window"], [0.10, 0.90])
        self.assertEqual(authority["fair_comparison"]["reserve_floor"], "CONSTANT_WORST_CASE_CASE_SPECIFIC_REQUIREMENT")
        self.assertEqual(authority["fair_comparison"]["efficiency"], {"eta_c": 0.90, "eta_d": 0.90})
        for label in (
            "economic_interface",
            "optimization_tariff",
            "settlement_interface",
            "settlement_matrix",
        ):
            self.assertTrue(authority["authority_hashes"][label]["match"])

    # F. Exact case allow-list.
    def test_f_exact_six_case_allowlist_and_rejections(self) -> None:
        expected = (
            "EOB",
            "a0.60_b04",
            "a0.60_b12",
            "a0.80_b08",
            "a1.00_b04",
            "a1.00_b12",
        )
        self.assertEqual(runner.ALLOWED_CASE_IDS, expected)
        for case_id in expected:
            self.assertEqual(runner.require_authorized_case(case_id).case_id, case_id)
        for case_id in ("a0.80_b04", "a1.00_b08", "a0.60_b24", "final81"):
            with self.subTest(case_id=case_id):
                with self.assertRaises(runner.SensitivityAuthorityError):
                    runner.require_authorized_case(case_id)

    # G. Accepted comparator pins.
    def test_g_comparator_result_hashes_are_exact_and_reuse_only(self) -> None:
        expected = {
            "EOB": "d7c37a0013ad6ea5a8dc3231a67bf427ec0c502aef96fedc47aacfe7c8897022",
            "a0.60_b04": "2e5710835b9a882a4978fda39990f493020418b34cd0d386d6f1399301fa23c5",
            "a0.60_b12": "6372608d847b8498c7b819bddd8e59a707cf4fbecb311496d27787e52205df3d",
            "a0.80_b08": "8a9bc67fc541ea682f9360e6063ededdb5bc0e2c6340c43c10c1fde86ab155f6",
            "a1.00_b04": "9fa5506db13681df0dd86b91bf3f9729b47f7a874fe57909b422dea7a6dfa628",
            "a1.00_b12": "6ea1dce9c951d11f3129c8654057c33df97030e54241f367123cfb6776590321",
        }
        records = self.authority["comparators"]
        self.assertEqual(set(records), set(expected))
        for case_id, expected_hash in expected.items():
            self.assertEqual(records[case_id]["result_sha256"], expected_hash)
            self.assertTrue(records[case_id]["reuse_only"])
            self.assertEqual(records[case_id]["future_mainline_solve_count"], 0)

    # H. Default invocation is no-solve and read-only.
    def test_h_default_cli_is_read_only_and_reports_zero_solve(self) -> None:
        output_root = ROOT / runner.OUTPUT_ROOT_RELATIVE
        before = sorted(path.relative_to(output_root).as_posix() for path in output_root.rglob("*")) if output_root.exists() else []
        completed = subprocess.run(
            [sys.executable, "-B", str(SCRIPT)],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["status"], "PASS")
        self.assertEqual(payload["mode"], "READ_ONLY_NO_SOLVE_NO_WRITE")
        self.assertEqual(payload["execution_counters"]["optimization_calls"], 0)
        self.assertEqual(payload["execution_counters"]["model_constructions"], 0)
        after = sorted(path.relative_to(output_root).as_posix() for path in output_root.rglob("*")) if output_root.exists() else []
        self.assertEqual(after, before)

    # I. Execution requires both explicit mode and a passing pre-solve gate.
    def test_i_executor_is_unreachable_without_explicit_flag_or_passing_gate(self) -> None:
        executor_calls: list[str] = []

        def passing_validator(_: Path) -> dict:
            return {"status": "PASS"}

        def fake_executor(_: Path, __: dict) -> Path:
            executor_calls.append("called")
            return Path("completion_manifest.json")

        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(
                runner.run([], root=ROOT, validator=passing_validator, executor=fake_executor),
                0,
            )
        self.assertEqual(executor_calls, [])

        def failing_validator(_: Path) -> dict:
            raise runner.SensitivityAuthorityError("test pre-solve rejection")

        with self.assertRaisesRegex(runner.SensitivityAuthorityError, "pre-solve rejection"):
            runner.run(
                ["--execute-production"],
                root=ROOT,
                validator=failing_validator,
                executor=fake_executor,
            )
        self.assertEqual(executor_calls, [])

        with self.assertRaisesRegex(runner.SensitivityAuthorityError, "without a passing"):
            runner.run(
                ["--execute-production"],
                root=ROOT,
                validator=lambda _: {"status": "FAIL"},
                executor=fake_executor,
            )
        self.assertEqual(executor_calls, [])

        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(
                runner.run(
                    ["--execute-production"],
                    root=ROOT,
                    validator=passing_validator,
                    executor=fake_executor,
                ),
                0,
            )
        self.assertEqual(executor_calls, ["called"])

    def test_i_real_execution_path_revalidates_before_output_or_solver_import(self) -> None:
        tree = ast.parse(SCRIPT.read_text(encoding="utf-8"))
        function = next(
            node
            for node in tree.body
            if isinstance(node, ast.FunctionDef) and node.name == "execute_production"
        )
        statements = function.body
        validate_index = next(
            index
            for index, statement in enumerate(statements)
            if "validate_authority" in (ast.get_source_segment(SCRIPT.read_text(encoding="utf-8"), statement) or "")
        )
        allocation_index = next(
            index
            for index, statement in enumerate(statements)
            if "allocate_run_directory" in (ast.get_source_segment(SCRIPT.read_text(encoding="utf-8"), statement) or "")
        )
        self.assertLess(validate_index, allocation_index)
        self.assertEqual(runner.SOLVER_CONTRACT["expected_total_optimize_calls"], 6)
        self.assertEqual(runner.SOLVER_CONTRACT["mainline_comparator_solves"], 0)
        self.assertFalse(runner.SOLVER_CONTRACT["retry"])
        self.assertFalse(runner.SOLVER_CONTRACT["tuning"])

    # J. Core immutability.
    def test_j_corrected_core_hash_is_unchanged(self) -> None:
        self.assertEqual(runner.sha256_file(CORE), runner.EXPECTED_CORE_SHA256)
        self.assertEqual(
            runner.EXPECTED_CORE_SHA256,
            "9d828321814b09141497056d1bb17da8b2839c5eb151fce8530059fb7e193da8",
        )

    def test_manifest_and_artifact_contract_is_complete_without_writing(self) -> None:
        manifest = runner.run_manifest_payload(ROOT, "test_run_id", self.authority)
        selected = manifest["selected_package"]
        for field in runner.REQUIRED_PACKAGE_FIELDS:
            self.assertIn(field, selected)
        self.assertEqual(manifest["run_id"], "test_run_id")
        self.assertEqual(manifest["solve_count_contract"]["new_1mw"], 6)
        self.assertEqual(manifest["solve_count_contract"]["new_10mw"], 0)
        self.assertEqual(
            self.authority["output_contract"]["terminal_state"],
            "exactly one of completion_manifest.json or failure_manifest.json",
        )
        self.assertEqual(
            self.authority["output_contract"]["artifact_registry_fields"],
            ["path", "sha256", "bytes", "role"],
        )

    def test_validation_functions_have_no_model_or_write_calls(self) -> None:
        source = SCRIPT.read_text(encoding="utf-8")
        tree = ast.parse(source)
        functions = {
            node.name: node for node in tree.body if isinstance(node, ast.FunctionDef)
        }
        validation_names = {
            "repository_authority",
            "verify_file_pins",
            "validate_sensitivity_package",
            "verify_source_package_rows",
            "load_and_verify_package_authority",
            "verify_canonical_input",
            "verify_comparators",
            "validate_authority",
        }
        forbidden = {
            "solve_eob",
            "build_eob_model",
            "optimize",
            "optimizeAsync",
            "optimizeBatch",
            "mkdir",
            "write_json",
            "to_csv",
            "to_parquet",
        }
        for name in validation_names:
            called = {
                node.func.attr if isinstance(node.func, ast.Attribute) else node.func.id
                for node in ast.walk(functions[name])
                if isinstance(node, ast.Call)
                and isinstance(node.func, (ast.Attribute, ast.Name))
            }
            self.assertTrue(called.isdisjoint(forbidden), (name, called & forbidden))


if __name__ == "__main__":
    unittest.main()
