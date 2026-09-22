"""Static and build-only tests for the candidate SOC2080 sensitivity implementation.

``SocWindowContractTests`` stays pure/static: it does not import Gurobi or build
a model.  ``SocWindowBuildOnlyTests`` constructs the real production-structure
model through the isolated adapter and asserts structure from the Gurobi model
itself.  Neither class calls ``solve_eob``, ``optimize()`` or any other solver
entry point, and neither writes production artifacts.
"""

from __future__ import annotations

import ast
import contextlib
import importlib
import importlib.util
import io
import math
import sys
import unittest
import uuid
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src import soc_window_sensitivity_adapter_v7_2 as adapter


def load_runner():
    path = ROOT / "scripts/17e_run_soc_window_sensitivity.py"
    name = f"_test_soc2080_runner_{uuid.uuid4().hex}"
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return name, module


RUNNER_MODULE_NAME, runner = load_runner()


class SocWindowContractTests(unittest.TestCase):
    def test_soc2080_contract(self) -> None:
        spec = adapter.SOC2080_SPEC
        self.assertEqual(spec.soc_min, 0.20)
        self.assertEqual(spec.soc_max, 0.80)
        self.assertEqual(spec.usable_fraction, 0.60)
        self.assertEqual(spec.lineage_id, "SENS-SOC2080-R10")
        self.assertEqual(spec.parent_lineage_id, "MAINLINE-CORRECTED-R10")

    def test_invalid_windows_are_rejected(self) -> None:
        invalid = (
            (-0.1, 0.8, 0.9),
            (0.8, 0.2, -0.6),
            (0.2, 1.1, 0.9),
            (0.2, 0.8, 0.8),
            (0.2, 0.8, float("nan")),
        )
        for soc_min, soc_max, usable in invalid:
            with self.subTest(values=(soc_min, soc_max, usable)):
                with self.assertRaises(ValueError):
                    adapter.SocWindowSpec(soc_min, soc_max, usable)

    def test_active_widths_clip_technical_domain(self) -> None:
        widths = adapter.derive_active_segment_widths(
            adapter.TECHNICAL_BREAKPOINTS,
            adapter.SOC2080_SPEC.usable_fraction,
        )
        self.assertEqual(adapter.TECHNICAL_BREAKPOINTS, (0.0, 0.30, 0.60, 0.80))
        self.assertEqual(adapter.TECHNICAL_SEGMENT_WIDTHS, (0.30, 0.30, 0.20))
        self.assertEqual(widths, (0.30, 0.30, 0.0))
        self.assertTrue(math.isclose(sum(widths), 0.60, abs_tol=1e-12))
        self.assertEqual(widths[2], 0.0)

    def test_analytical_bound_uses_point60(self) -> None:
        for reserve in (0.0, 60.0, 1234.5):
            with self.subTest(reserve=reserve):
                self.assertEqual(
                    adapter.required_nameplate_energy_kwh(reserve), reserve / 0.60
                )


class RunnerContractTests(unittest.TestCase):
    def test_case_allowlist_and_solve_counts(self) -> None:
        self.assertEqual(
            runner.SCRIPT_VERSION,
            "v7.2-soc2080-sensitivity-runner-candidate-2026-09-22-r2",
        )
        self.assertEqual(
            runner.ALLOWED_CASE_IDS,
            (
                "EOB",
                "a0.60_b04",
                "a0.60_b12",
                "a0.80_b08",
                "a1.00_b04",
                "a1.00_b12",
            ),
        )
        self.assertEqual(runner.EXPECTED_FUTURE_SENSITIVITY_OPTIMIZE_CALLS, 6)
        self.assertEqual(runner.EXPECTED_FUTURE_COMPARATOR_OPTIMIZE_CALLS, 0)

    def test_one_factor_isolation(self) -> None:
        contract = runner.ONE_FACTOR_CONTRACT
        self.assertEqual(contract["only_changed_factor"], "SOC_WINDOW_10_90_TO_20_80")
        self.assertEqual(contract["package_id"], runner.EXPECTED_MAINLINE_PACKAGE_ID)
        self.assertEqual(contract["power_scale_bracket_mw"], 10.0)
        self.assertEqual(contract["winter_pv_treatment"], "MAINLINE_CONSERVATIVE_ZERO")
        self.assertEqual(
            contract["reserve_policy"], "CONSTANT_WORST_CASE_CASE_SPECIFIC_REQUIREMENT"
        )
        self.assertEqual((contract["eta_c"], contract["eta_d"]), (0.90, 0.90))
        self.assertFalse(contract["outage_pv_surplus_recharge"])
        self.assertEqual(runner.MIP_GAP, 1e-6)

    def test_output_namespace_isolated(self) -> None:
        namespace = runner.OUTPUT_ROOT_RELATIVE.as_posix()
        self.assertEqual(namespace, "results/sensitivity/soc_20_80/runs")
        for forbidden in (
            "eob_production",
            "layer_a",
            "winter_pv_17c",
            "bess_cost_scale_1mw",
            "final_81",
        ):
            self.assertNotIn(forbidden, namespace)

    def test_comparator_pins_are_recovered_from_hash_pinned_17d(self) -> None:
        pins = runner.recover_authoritative_comparator_pins(ROOT)
        self.assertEqual(tuple(pin.case_id for pin in pins), runner.ALLOWED_CASE_IDS)
        self.assertEqual(
            tuple(pin.run_id for pin in pins),
            (
                "20260917T082758521112Z_a4b6383308",
                "20260918T054012682911Z_54b3624894",
                "20260918T063627414306Z_c114929d2c",
                "20260918T085202453195Z_755e01dfb2",
                "20260918T105101058616Z_a75a268198",
                "20260918T123936526903Z_82e3bc3214",
            ),
        )
        records = runner.verify_comparators(ROOT)
        self.assertEqual(tuple(records), runner.ALLOWED_CASE_IDS)
        self.assertTrue(all(record["reuse_only"] for record in records.values()))
        self.assertTrue(
            all(
                record["future_comparator_optimize_calls"] == 0
                for record in records.values()
            )
        )

    def test_default_run_never_calls_executor(self) -> None:
        calls = {"executor": 0}

        def validator(_root: Path):
            return {"status": "STATIC_ONLY", "actual_optimize_calls": 0}

        def executor(_root: Path, _authority):
            calls["executor"] += 1
            raise AssertionError("default path entered production executor")

        with contextlib.redirect_stdout(io.StringIO()):
            return_code = runner.run(
                [], root=ROOT, validator=validator, executor=executor
            )
        self.assertEqual(return_code, 0)
        self.assertEqual(calls["executor"], 0)


class RainflowAuthorityStateTests(unittest.TestCase):
    @staticmethod
    def _rainflow(verdict: str, cost_state: str, hard_state: str = "PASS"):
        return {
            "summary": {
                "verdict": verdict,
                "maximum_rainflow_DOD_fraction_nameplate": 0.60,
            },
            "gates": {
                "soc_energy_identity": hard_state,
                "pwl_vs_rainflow_cost_numerical_equivalence": cost_state,
            },
        }

    @staticmethod
    def _result():
        return {
            "status": "OPTIMAL",
            "mode": "binary",
            "mip_gap": 0.0,
            "dispatch": pd.DataFrame(
                {
                    "e_seg_3_kwh": [0.0, 0.0],
                    "p_charge_seg_3_kw_ac": [0.0, 0.0],
                    "p_discharge_seg_3_kw_ac": [0.0, 0.0],
                    "soc_fraction": [0.20, 0.80],
                }
            ),
            "physical_diagnostics": {
                "soc_min_realized": 0.20,
                "soc_max_realized": 0.80,
                "max_ac_balance_residual_kw": 0.0,
                "max_segment_dynamics_residual_kwh": 0.0,
                "max_segment_cyclic_residual_kwh": 0.0,
                "simultaneous_hours_above_tol": 0,
            },
            "cost_reconciliation_residual_ntd": 0.0,
            "transition_settlement": {
                "nonbinding_certificate": "PASS_NO_RATE_AMBIGUOUS_INCREMENTAL_OVERAGE"
            },
        }

    @staticmethod
    def _billing():
        return {
            "period_ids": "PASS",
            "detail_columns": "PASS",
            "valid_detail_keys": "PASS",
            "duplicate_detail_keys": "PASS",
            "tariff_calendar_structure": "PASS",
        }

    def test_base_gate_preserves_pass_review_fail_and_fails_closed(self) -> None:
        cases = (
            ("RAINFLOW_VALIDATION_PASS", "PASS", "PASS", "PASS"),
            (
                "RAINFLOW_VALIDATION_REVIEW_REQUIRED_PWL_COST_DIFFERENCE",
                "REVIEW",
                "PASS",
                "REVIEW",
            ),
            ("RAINFLOW_VALIDATION_FAIL", "PASS", "FAIL", "FAIL"),
            ("RAINFLOW_VALIDATION_PASS", "REVIEW", "PASS", "FAIL"),
        )
        for verdict, cost_state, hard_state, expected in cases:
            with self.subTest(
                verdict=verdict, cost_state=cost_state, hard_state=hard_state
            ):
                gates = runner.base_post_solve_gates(
                    self._result(),
                    self._billing(),
                    self._rainflow(verdict, cost_state, hard_state),
                )
                self.assertEqual(gates["rainflow_validation"], expected)

    def test_review_and_fail_are_serialized_before_termination(self) -> None:
        for state, expected_status in (
            ("REVIEW", "CANDIDATE_REVIEW_REQUIRED"),
            ("FAIL", "CANDIDATE_GATE_FAILED"),
        ):
            events = []

            def serializer(status, post_solve_state):
                events.append(("serialized", status, post_solve_state))

            with self.subTest(state=state):
                with self.assertRaises(runner.SocSensitivityAuthorityError):
                    runner.serialize_case_diagnostics_before_enforcement(
                        "synthetic_case",
                        {"rainflow_validation": state},
                        serializer,
                    )
                self.assertEqual(
                    events,
                    [("serialized", expected_status, state)],
                )

    def test_pass_serialization_retains_candidate_completion_semantics(self) -> None:
        events = []

        def serializer(status, post_solve_state):
            events.append(("serialized", status, post_solve_state))

        status = runner.serialize_case_diagnostics_before_enforcement(
            "synthetic_case",
            {"rainflow_validation": "PASS", "all_other_gates": "PASS"},
            serializer,
        )
        self.assertEqual(status, "CANDIDATE_PENDING_INDEPENDENT_POST_RUN_AUDIT")
        self.assertEqual(
            events,
            [
                (
                    "serialized",
                    "CANDIDATE_PENDING_INDEPENDENT_POST_RUN_AUDIT",
                    "PASS",
                )
            ],
        )

    def test_corrected_representative_helper_hash_is_pinned(self) -> None:
        self.assertEqual(
            runner.sha256_file(
                ROOT / "scripts/16a_preflight_layer_a_representative_binary_cases.py"
            ),
            runner.EXPECTED_HELPER_SHA256,
        )


class SourceIsolationTests(unittest.TestCase):
    def test_importing_adapter_does_not_mutate_canonical_module(self) -> None:
        canonical_name = adapter.CANONICAL_MODULE_NAME
        canonical = sys.modules.get(canonical_name)
        before = None
        if canonical is not None:
            before = {
                name: getattr(canonical, name)
                for name in (
                    "SOC_MIN",
                    "SOC_MAX",
                    "BREAKPOINTS",
                    "SEGMENT_WIDTHS",
                    "build_eob_model",
                    "solve_eob",
                )
            }
        importlib.reload(adapter)
        self.assertIs(sys.modules.get(canonical_name), canonical)
        if canonical is not None and before is not None:
            for name, value in before.items():
                current = getattr(canonical, name)
                if callable(value):
                    self.assertIs(current, value)
                else:
                    self.assertEqual(current, value)

    def test_new_sources_have_no_direct_optimize_call(self) -> None:
        for relative in (
            "src/soc_window_sensitivity_adapter_v7_2.py",
            "scripts/17e_run_soc_window_sensitivity.py",
        ):
            tree = ast.parse((ROOT / relative).read_text(encoding="utf-8"))
            direct = [
                node
                for node in ast.walk(tree)
                if isinstance(node, ast.Call)
                and isinstance(node.func, ast.Attribute)
                and node.func.attr == "optimize"
            ]
            self.assertEqual(direct, [], relative)

    def test_adapter_does_not_import_canonical_core(self) -> None:
        tree = ast.parse(
            (ROOT / "src/soc_window_sensitivity_adapter_v7_2.py").read_text(
                encoding="utf-8"
            )
        )
        imported = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported.extend(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported.append(node.module)
        self.assertNotIn("src.annual_design_model_v7_2", imported)

    def test_explicit_third_segment_exclusion_constraints_exist(self) -> None:
        source = (
            ROOT / "src/soc_window_sensitivity_adapter_v7_2.py"
        ).read_text(encoding="utf-8")
        for marker in (
            "soc2080_inactive_state_",
            "soc2080_inactive_charge_",
            "soc2080_inactive_discharge_",
            "soc2080_aggregate_shifted_cap_",
        ):
            self.assertIn(marker, source)

    def test_accepted_r10_hash_pin(self) -> None:
        self.assertEqual(
            runner.sha256_file(ROOT / "src/annual_design_model_v7_2.py"),
            adapter.EXPECTED_R10_CORE_SHA256,
        )


class SocWindowLoaderIntegrityTests(unittest.TestCase):
    """DEFECT-1/DEFECT-2 regression: the real loader and its integrity gate."""

    def test_float_sequence_helper_accepts_derived_width(self) -> None:
        # Accepted R10 derives 0.80 - 0.60 = 0.20000000000000007.
        self.assertTrue(
            adapter._float_sequence_matches(
                (0.30, 0.30, 0.20000000000000007), (0.30, 0.30, 0.20)
            )
        )
        canonical = importlib.import_module(adapter.CANONICAL_MODULE_NAME)
        self.assertTrue(
            adapter._float_sequence_matches(
                tuple(canonical.SEGMENT_WIDTHS), adapter.TECHNICAL_SEGMENT_WIDTHS
            )
        )

    def test_float_sequence_helper_rejects_material_drift(self) -> None:
        for actual in (
            (0.30, 0.30, 0.19),
            (0.30, 0.30, 0.20 + 1e-11),
            (0.30, 0.30),
            (0.30, 0.30, 0.20, 0.10),
            (True, 0.30, 0.20),
            ("0.30", 0.30, 0.20),
            (float("nan"), 0.30, 0.20),
        ):
            with self.subTest(actual=actual):
                self.assertFalse(
                    adapter._float_sequence_matches(actual, (0.30, 0.30, 0.20))
                )

    def test_real_loader_succeeds_against_accepted_r10(self) -> None:
        isolated = adapter.load_isolated_r10_soc_core(ROOT)
        module = isolated.module
        self.assertEqual(module.CORE_VERSION, adapter.EXPECTED_R10_CORE_VERSION)
        self.assertEqual(module.SOC_MIN, 0.20)
        self.assertEqual(module.SOC_MAX, 0.80)
        self.assertEqual(int(module.N_SEGMENTS), 3)
        self.assertTrue(
            adapter._float_sequence_matches(
                tuple(module.BREAKPOINTS), (0.0, 0.30, 0.60, 0.80)
            )
        )
        self.assertTrue(
            adapter._float_sequence_matches(
                tuple(module.SEGMENT_WIDTHS), (0.30, 0.30, 0.0)
            )
        )
        self.assertEqual(isolated.inactive_segment_indices, (2,))
        canonical = importlib.import_module(adapter.CANONICAL_MODULE_NAME)
        self.assertEqual(canonical.SOC_MIN, 0.10)
        self.assertEqual(canonical.SOC_MAX, 0.90)
        self.assertTrue(
            adapter._float_sequence_matches(
                tuple(canonical.SEGMENT_WIDTHS), (0.30, 0.30, 0.20)
            )
        )

    def test_loader_integrity_gate_still_rejects_material_width_drift(self) -> None:
        # Accepted R10 bytes are never modified; the reference literal is
        # temporarily moved so the loader's own gate is what gets exercised.
        original = adapter.TECHNICAL_SEGMENT_WIDTHS
        adapter.TECHNICAL_SEGMENT_WIDTHS = (0.30, 0.30, 0.19)
        try:
            with self.assertRaises(adapter.SocWindowAdapterError):
                adapter.load_isolated_r10_soc_core(ROOT)
        finally:
            adapter.TECHNICAL_SEGMENT_WIDTHS = original
        self.assertEqual(adapter.TECHNICAL_SEGMENT_WIDTHS, (0.30, 0.30, 0.20))
        self.assertEqual(
            runner.sha256_file(ROOT / "src/annual_design_model_v7_2.py"),
            adapter.EXPECTED_R10_CORE_SHA256,
        )

    def test_repeated_isolated_loads_never_touch_canonical_module(self) -> None:
        canonical = importlib.import_module(adapter.CANONICAL_MODULE_NAME)
        watched = ("SOC_MIN", "SOC_MAX", "BREAKPOINTS", "SEGMENT_WIDTHS", "N_SEGMENTS")
        before = {name: getattr(canonical, name) for name in watched}
        before_builder = canonical.build_eob_model
        first = adapter.load_isolated_r10_soc_core(ROOT)
        second = adapter.load_isolated_r10_soc_core(ROOT)
        self.assertIsNot(first.module, second.module)
        self.assertIsNot(first.module, canonical)
        self.assertIsNot(second.module, canonical)
        self.assertIs(sys.modules.get(adapter.CANONICAL_MODULE_NAME), canonical)
        self.assertIs(canonical.build_eob_model, before_builder)
        for name, value in before.items():
            self.assertEqual(getattr(canonical, name), value)
        self.assertEqual(canonical.SOC_MIN, 0.10)
        self.assertEqual(canonical.SOC_MAX, 0.90)


class SocWindowBuildOnlyTests(unittest.TestCase):
    """Construct the real production-structure model. No ``optimize()`` call."""

    BUILT: dict = {}

    @classmethod
    def setUpClass(cls) -> None:
        import gurobipy as gp

        cls._blocked = []
        for name in (
            "optimize",
            "optimizeAsync",
            "optimizeBatch",
            "tune",
            "feasRelax",
            "feasRelaxS",
            "computeIIS",
        ):
            if hasattr(gp.Model, name):
                cls._blocked.append((name, getattr(gp.Model, name)))

        def forbidden(*_args, **_kwargs):
            raise AssertionError("Build-only test attempted a solver call.")

        for name, _original in cls._blocked:
            setattr(gp.Model, name, forbidden)

        cls.isolated = adapter.load_isolated_r10_soc_core(ROOT)
        core = cls.isolated.module
        cls.inputs = core.load_annual_design_inputs(
            ROOT,
            annual_parquet=ROOT / "data/processed/annual_input_v7_1.parquet",
            annual_csv=ROOT / "data/processed/annual_input_v7_1.csv",
            economic_interface_path=ROOT
            / "data/reference/production_economic_interface_v7_2.json",
            normalized_tariff_path=ROOT
            / "data/reference/taipower_tariff_optimization_ntd2023_v7_2.csv",
            settlement_interface_path=ROOT
            / "data/reference/taipower_transition_period_settlement_interface_v7_2.json",
            settlement_matrix_path=ROOT
            / "data/reference/taipower_seasonal_settlement_matrix_v7_2.csv",
        )
        helper_name = f"_test_soc2080_helper_{uuid.uuid4().hex}"
        helper_spec = importlib.util.spec_from_file_location(
            helper_name,
            ROOT / "scripts/16a_preflight_layer_a_representative_binary_cases.py",
        )
        helper = importlib.util.module_from_spec(helper_spec)
        sys.modules[helper_name] = helper
        helper_spec.loader.exec_module(helper)
        cls._helper_name = helper_name
        surface, _starts, audit = helper.analytical_surface(
            cls.inputs.annual,
            eta_d=0.90,
            soc_min=adapter.SOC2080_SPEC.soc_min,
            soc_max=adapter.SOC2080_SPEC.soc_max,
        )
        assert audit.get("status") == "PASS"
        cls.surface = surface
        cls.requirement = surface.loc[surface["case_id"].eq("a0.80_b08")].iloc[0].to_dict()

        for case_id in ("EOB", "a0.80_b08"):
            layer = None
            if case_id != "EOB":
                layer = core.LayerAResilienceRequirements(
                    alpha=float(cls.requirement["alpha"]),
                    beta_h=int(cls.requirement["beta_h"]),
                    reserve_kwh_battery=float(cls.requirement["R_kwh_battery"]),
                    power_requirement_kw_ac=float(cls.requirement["P_out_kw_ac"]),
                )
            settings = core.SolveSettings(
                mode="binary",
                mip_gap=1e-6,
                time_limit_sec=None,
                output_flag=0,
                numeric_focus=1,
                log_file=None,
                telemetry_callback=None,
            )
            model, handles = core.build_eob_model(cls.inputs, settings, layer)
            model.update()
            cls.BUILT[case_id] = (model, handles)

    @classmethod
    def tearDownClass(cls) -> None:
        import gurobipy as gp

        for model, _handles in cls.BUILT.values():
            model.dispose()
        cls.BUILT.clear()
        for name, original in getattr(cls, "_blocked", []):
            setattr(gp.Model, name, original)
        sys.modules.pop(getattr(cls, "_helper_name", ""), None)

    def _names(self, model) -> list[str]:
        return [constraint.ConstrName for constraint in model.getConstrs()]

    def test_built_models_use_the_soc2080_window(self) -> None:
        core = self.isolated.module
        self.assertEqual(core.SOC_MIN, 0.20)
        self.assertEqual(core.SOC_MAX, 0.80)
        for case_id, (_model, handles) in self.BUILT.items():
            with self.subTest(case=case_id):
                window = handles["soc_window_spec"]
                self.assertEqual(window["soc_min"], 0.20)
                self.assertEqual(window["soc_max"], 0.80)
                self.assertEqual(window["usable_fraction"], 0.60)
                self.assertTrue(
                    adapter._float_sequence_matches(
                        tuple(handles["active_segment_widths"]), (0.30, 0.30, 0.0)
                    )
                )

    def test_third_segment_state_is_structurally_zero(self) -> None:
        states = len(self.inputs.annual) + 1
        for case_id, (model, handles) in self.BUILT.items():
            with self.subTest(case=case_id):
                upper = max(handles["e_seg"][t, 2].UB for t in range(states))
                self.assertEqual(upper, 0.0)
                rows = sum(
                    1
                    for name in self._names(model)
                    if name.startswith("soc2080_inactive_state_")
                )
                self.assertEqual(rows, states)

    def test_third_segment_flows_are_structurally_zero(self) -> None:
        intervals = len(self.inputs.annual)
        for case_id, (model, _handles) in self.BUILT.items():
            with self.subTest(case=case_id):
                names = self._names(model)
                charge = sum(
                    1 for name in names if name.startswith("soc2080_inactive_charge_")
                )
                discharge = sum(
                    1 for name in names if name.startswith("soc2080_inactive_discharge_")
                )
                self.assertEqual(charge, intervals)
                self.assertEqual(discharge, intervals)

    def test_aggregate_shifted_state_cap_is_point60_of_nameplate(self) -> None:
        states = len(self.inputs.annual) + 1
        for case_id, (model, handles) in self.BUILT.items():
            with self.subTest(case=case_id):
                rows = sum(
                    1
                    for name in self._names(model)
                    if name.startswith("soc2080_aggregate_shifted_cap_")
                )
                self.assertEqual(rows, states)
                constraint = model.getConstrByName("soc2080_aggregate_shifted_cap_t0")
                self.assertIsNotNone(constraint)
                expression = model.getRow(constraint)
                coefficient = None
                for index in range(expression.size()):
                    if expression.getVar(index).VarName == handles["E_N"].VarName:
                        coefficient = expression.getCoeff(index)
                self.assertIsNotNone(coefficient)
                self.assertAlmostEqual(coefficient, -0.60, places=12)

    def test_layer_a_reserve_floor_present_only_for_layer_a_case(self) -> None:
        states = len(self.inputs.annual) + 1
        eob_rows = sum(
            1
            for name in self._names(self.BUILT["EOB"][0])
            if name.startswith("layer_a_reserve_floor_t")
        )
        self.assertEqual(eob_rows, 0)
        layer_rows = sum(
            1
            for name in self._names(self.BUILT["a0.80_b08"][0])
            if name.startswith("layer_a_reserve_floor_t")
        )
        self.assertEqual(layer_rows, states)

    def test_reserve_adequacy_uses_r_over_point60(self) -> None:
        reserve = float(self.requirement["R_kwh_battery"])
        self.assertAlmostEqual(reserve, 33706.0, places=6)
        expected = reserve / 0.60
        self.assertAlmostEqual(expected, 56176.666666666664, places=6)
        self.assertAlmostEqual(
            adapter.required_nameplate_energy_kwh(reserve), expected, places=9
        )
        self.assertAlmostEqual(
            float(self.requirement["analytical_E_N_min_kwh"]), expected, places=6
        )
        self.assertNotAlmostEqual(expected, reserve / 0.80, places=3)

    def test_objective_present_and_no_solver_call_occurred(self) -> None:
        import gurobipy as gp

        for case_id, (model, _handles) in self.BUILT.items():
            with self.subTest(case=case_id):
                self.assertGreater(model.getObjective().size(), 0)
                self.assertGreater(model.NumVars, 0)
                self.assertGreater(model.NumConstrs, 0)
        with self.assertRaises(AssertionError):
            gp.Model.optimize(self.BUILT["EOB"][0])


def tearDownModule() -> None:
    sys.modules.pop(RUNNER_MODULE_NAME, None)


if __name__ == "__main__":
    unittest.main()
