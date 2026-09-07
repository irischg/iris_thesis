"""Static Candidate-1 transition-settlement tests; no MILP is built or solved."""

from __future__ import annotations

import sys
import types
import unittest
from pathlib import Path
import math
import re
import ast


# The production core intentionally requires gurobipy at runtime.  These tests
# exercise only pure calendar/rate/tie/product helpers, so provide a minimal
# import shim when this checkout's Python interpreter lacks the optional solver
# package.  No fake Model is provided and no model construction is possible.
try:  # pragma: no cover - depends on the local project environment
    import gurobipy  # noqa: F401
except ImportError:  # pragma: no cover - exercised only without Gurobi
    shim = types.ModuleType("gurobipy")
    shim.GRB = types.SimpleNamespace()
    sys.modules["gurobipy"] = shim

from src.annual_design_model_v7_2 import (  # noqa: E402
    classify_transition_component,
    LayerAResilienceRequirements,
    _finite_design_bounds,
    _mainline_cost_coefficients,
    _regular_basic_rate,
    load_annual_design_inputs,
    transition_class_c_cost_from_product,
    transition_boundary_settlement_accounting,
    transition_component_classification,
    transition_formulation_metadata,
    transition_tie_band_static_audit,
    transition_tie_band_kw,
    transition_tie_selection_guard_kw,
)


class TransitionCandidate1StaticTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.root = Path(__file__).resolve().parents[1]
        # Force the audited CSV to keep this source-level test independent of
        # optional parquet-engine behavior in the local Python environment.
        cls.inputs = load_annual_design_inputs(
            cls.root,
            annual_parquet=cls.root / "data" / "processed" / "__not_used__.parquet",
            annual_csv=cls.root / "data" / "processed" / "annual_input_v7_1.csv",
        )

    def test_component_classes_are_rate_and_calendar_driven(self) -> None:
        self.assertEqual(
            classify_transition_component(["summer"], {"summer": 1.0}),
            "CLASS_A_SINGLE_SEASON",
        )
        self.assertEqual(
            classify_transition_component(
                ["summer", "non_summer"],
                {"summer": 1.0, "non_summer": 1.0},
            ),
            "CLASS_B_TWO_SEASON_EQUAL_SETTLEMENT_RATE",
        )
        self.assertEqual(
            classify_transition_component(
                ["summer", "non_summer"],
                {"summer": 1.0, "non_summer": 1.0000000001},
            ),
            "CLASS_C_TWO_SEASON_DIFFERENT_SETTLEMENT_RATE",
        )

    def test_live_component_metadata_has_no_empty_seasonal_max_slice(self) -> None:
        rows = transition_component_classification(self.inputs)
        self.assertEqual(len(rows), 8)
        counts = {
            label: sum(row["settlement_class"] == label for row in rows)
            for label in (
                "CLASS_A_SINGLE_SEASON",
                "CLASS_B_TWO_SEASON_EQUAL_SETTLEMENT_RATE",
                "CLASS_C_TWO_SEASON_DIFFERENT_SETTLEMENT_RATE",
            )
        }
        self.assertEqual(counts, {
            "CLASS_A_SINGLE_SEASON": 2,
            "CLASS_B_TWO_SEASON_EQUAL_SETTLEMENT_RATE": 2,
            "CLASS_C_TWO_SEASON_DIFFERENT_SETTLEMENT_RATE": 4,
        })
        # The reduced-native-MAX formulation retains exact seasonal MAX only
        # for Class C, where seasonal source identity selects a different
        # settlement rate. A/B use a live-calendar-derived billing epigraph.
        expected_max_constraints = sum(
            len(row["active_seasons"])
            for row in rows
            if row["settlement_class"]
            == "CLASS_C_TWO_SEASON_DIFFERENT_SETTLEMENT_RATE"
        )
        self.assertEqual(expected_max_constraints, 8)
        formulation = transition_formulation_metadata(self.inputs)
        self.assertEqual(formulation["exact_max_general_constraints_total"], 8)
        self.assertEqual(formulation["exact_global_max_constraints"], 0)
        self.assertEqual(formulation["native_max_hourly_operands"], 858)
        self.assertEqual(
            formulation["native_max_hourly_operands_by_class"],
            {
                "CLASS_A_SINGLE_SEASON": 0,
                "CLASS_B_TWO_SEASON_EQUAL_SETTLEMENT_RATE": 0,
                "CLASS_C_TWO_SEASON_DIFFERENT_SETTLEMENT_RATE": 858,
            },
        )
        self.assertEqual(
            formulation["billing_epigraph_rows_by_class"],
            {
                "CLASS_A_SINGLE_SEASON": 120,
                "CLASS_B_TWO_SEASON_EQUAL_SETTLEMENT_RATE": 510,
                "CLASS_C_TWO_SEASON_DIFFERENT_SETTLEMENT_RATE": 0,
            },
        )
        self.assertEqual(formulation["billing_epigraph_rows_total"], 630)
        self.assertEqual(formulation["class_c_demand_link_rows"], 8)
        self.assertEqual(
            formulation["economically_necessary_class_c_source_binaries"], 4
        )
        self.assertEqual(formulation["transition_indicator_constraints"], 0)
        for row in rows:
            self.assertGreater(row["period_hour_count"], 0)
            self.assertTrue(all(count > 0 for count in row["season_hour_counts"].values()))
            self.assertEqual(
                sum(row["season_hour_counts"].values()), row["period_hour_count"]
            )
            if row["settlement_class"] == "CLASS_A_SINGLE_SEASON":
                self.assertEqual(len(row["active_seasons"]), 1)
            else:
                self.assertEqual(len(row["active_seasons"]), 2)
                self.assertEqual(len(row["chronological_seasons"]), 2)

    def test_reduced_max_builder_is_class_specific_and_ex_post_safe(self) -> None:
        core_text = (self.root / "src" / "annual_design_model_v7_2.py").read_text(
            encoding="utf-8"
        )
        build_start = core_text.index("# Over-contract settlement.")
        build_end = core_text.index("return model, handles", build_start)
        transition_build = core_text[build_start:build_end]

        # Native MAX creation remains exclusively inside the Class-C branch.
        class_c_native_block = transition_build.split(
            'if settlement_class == "CLASS_C_TWO_SEASON_DIFFERENT_SETTLEMENT_RATE":',
            1,
        )[1].split('elif settlement_class in {', 1)[0]
        self.assertIn("model.addGenConstrMax(", class_c_native_block)
        self.assertIn("transition_demand_ge_seasonal_max_", class_c_native_block)
        self.assertIn("transition_demand_epi_", transition_build)
        self.assertNotIn("transition_global_max_grid", transition_build)
        self.assertNotIn("transition_exact_max_{month}_{period}_global", transition_build)
        self.assertNotIn("addGenConstrIndicator(", transition_build)
        self.assertNotIn("math.nextafter", core_text)

        # The sole transition source selector is declared in the Class-C
        # branch. Class B bills directly at its common rate and must not grow a
        # source-cost binary merely to retain diagnostics.
        source_selector_index = transition_build.index(
            "transition_source_later = model.addVar("
        )
        class_b_cost_index = transition_build.rfind(
            'elif settlement_class == "CLASS_B_TWO_SEASON_EQUAL_SETTLEMENT_RATE":',
            0,
            source_selector_index,
        )
        class_c_cost_index = transition_build.rfind(
            'elif settlement_class == "CLASS_C_TWO_SEASON_DIFFERENT_SETTLEMENT_RATE":',
            0,
            source_selector_index,
        )
        self.assertGreater(class_c_cost_index, class_b_cost_index)
        self.assertEqual(
            transition_build.count("transition_source_later = model.addVar("), 1
        )

        # A/B diagnostics must use dispatch-derived maxima rather than absent
        # native seasonal variables; Class C retains native-resultant checks.
        self.assertIn("NOT_APPLICABLE_CLASS_A_OR_B_EPIGRAPH", core_text)
        self.assertIn("billing_demand_epigraph_pass", core_text)
        self.assertIn("if has_native_seasonal_max:", core_text)

    def test_bounded_binary_product_cost_algebra(self) -> None:
        rate_early = 32.0
        rate_later = 43.0
        quantity = 17.5
        self.assertAlmostEqual(
            transition_class_c_cost_from_product(
                rate_early, rate_later, quantity, 0, 0.0
            ),
            rate_early * quantity,
        )
        self.assertAlmostEqual(
            transition_class_c_cost_from_product(
                rate_early, rate_later, quantity, 1, quantity
            ),
            rate_later * quantity,
        )

    def test_tie_policy_covers_closed_band_and_explicit_guard(self) -> None:
        audit = transition_tie_band_static_audit()
        self.assertEqual(audit["status"], "PASS")
        rows = {row["case"]: row for row in audit["cases"]}
        self.assertEqual(
            rows["difference_eq_tie_band"]["classification"],
            "NUMERICAL_TIE_EARLIEST_MAX_TIMESTAMP",
        )
        self.assertEqual(
            rows["difference_inside_selection_guard"]["classification"],
            "NUMERICAL_BOUNDARY_UNRESOLVED",
        )
        self.assertEqual(
            rows["difference_eq_later_selection_threshold"]["classification"],
            "LATER_SEASON_CLEARLY_LARGER",
        )

    def test_unresolved_boundary_certificate_accounting_is_class_specific(self) -> None:
        status = "NUMERICAL_BOUNDARY_UNRESOLVED"
        class_b = transition_boundary_settlement_accounting(
            "CLASS_B_TWO_SEASON_EQUAL_SETTLEMENT_RATE", status, 12.5
        )
        self.assertFalse(class_b["boundary_affects_settlement"])
        self.assertEqual(class_b["certificate_failure_count_increment"], 0)
        self.assertEqual(class_b["ambiguous_incremental_overage_kw"], 0.0)

        class_c = transition_boundary_settlement_accounting(
            "CLASS_C_TWO_SEASON_DIFFERENT_SETTLEMENT_RATE", status, 12.5
        )
        self.assertTrue(class_c["boundary_affects_settlement"])
        self.assertEqual(class_c["certificate_failure_count_increment"], 1)
        self.assertEqual(class_c["ambiguous_incremental_overage_kw"], 12.5)

        class_a = transition_boundary_settlement_accounting(
            "CLASS_A_SINGLE_SEASON", "SINGLE_SEASON", 12.5
        )
        self.assertFalse(class_a["boundary_affects_settlement"])
        self.assertEqual(class_a["certificate_failure_count_increment"], 0)

        core_text = (self.root / "src" / "annual_design_model_v7_2.py").read_text(
            encoding="utf-8"
        )
        self.assertIn(
            "boundary_accounting = transition_boundary_settlement_accounting(",
            core_text,
        )

    def test_class_b_common_rate_billing_is_source_invariant(self) -> None:
        common_rate = 160.67170620437955
        delta_z = 12.5
        delta_s = 1.25
        quantity = 3.0 * delta_z - delta_s
        early_source_cost = transition_class_c_cost_from_product(
            common_rate, common_rate, quantity, 0, 0.0
        )
        later_source_cost = transition_class_c_cost_from_product(
            common_rate, common_rate, quantity, 1, quantity
        )
        self.assertAlmostEqual(early_source_cost, common_rate * quantity)
        self.assertAlmostEqual(later_source_cost, common_rate * quantity)
        self.assertAlmostEqual(early_source_cost, later_source_cost)

        core_text = (self.root / "src" / "annual_design_model_v7_2.py").read_text(
            encoding="utf-8"
        )
        class_b_block = core_text.split(
            'elif settlement_class == "CLASS_B_TWO_SEASON_EQUAL_SETTLEMENT_RATE":', 1
        )[1].split(
            'elif settlement_class == "CLASS_C_TWO_SEASON_DIFFERENT_SETTLEMENT_RATE":', 1
        )[0]
        self.assertIn("month_cost += rate * W", class_b_block)

    def test_idle_reference_derives_finite_case_specific_design_bounds(self) -> None:
        requirement = LayerAResilienceRequirements(
            alpha=0.60,
            beta_h=4,
            reserve_kwh_battery=12807.111111111111,
            power_requirement_kw_ac=2914.2,
        )
        band = transition_tie_band_kw(1e-6, 6000.0)
        bounds = _finite_design_bounds(
            self.inputs,
            _mainline_cost_coefficients(self.inputs.mainline_package),
            requirement,
            band,
            transition_tie_selection_guard_kw(1e-6),
        )
        for key in ("E_N_ub_kwh", "P_B_ub_kw_ac", "CC_ub_kw"):
            self.assertTrue(math.isfinite(bounds[key]))
            self.assertGreater(bounds[key], 0.0)
        self.assertGreaterEqual(bounds["E_N_ub_kwh"], bounds["reference_E_N_kwh"])
        self.assertGreaterEqual(bounds["P_B_ub_kw_ac"], bounds["reference_P_B_kw_ac"])

    def test_current_guard_moves_only_16a_not_frozen_15b_15c(self) -> None:
        core_text = (self.root / "src" / "annual_design_model_v7_2.py").read_text(
            encoding="utf-8"
        )
        script_16a = (
            self.root / "scripts" / "16a_preflight_layer_a_representative_binary_cases.py"
        ).read_text(encoding="utf-8")
        script_15b = (
            self.root / "scripts" / "15b_freeze_production_eob_baseline.py"
        ).read_text(encoding="utf-8")
        script_15c = (
            self.root / "scripts" / "15c_validate_production_eob_rainflow.py"
        ).read_text(encoding="utf-8")
        core_version = re.search(
            r'^CORE_VERSION = "([^"]+)"', core_text, re.MULTILINE
        ).group(1)
        expected_16a = re.search(
            r'^EXPECTED_CORE_VERSION = "([^"]+)"', script_16a, re.MULTILINE
        ).group(1)
        self.assertEqual(core_version, expected_16a)
        self.assertIn(
            "v7.2-annual-design-core-transition-rate-audit-2026-08-29-r1",
            script_15b,
        )
        self.assertIn("validate_source_hash_against_freeze", script_15c)
        self.assertIn("shared_core", script_15c)
        build_only_source = script_16a.split("def build_only_case_audit", 1)[1].split(
            "\ndef main", 1
        )[0]
        self.assertIn("build_eob_model", build_only_source)
        calls = [
            node.func.attr
            for node in ast.walk(ast.parse("def build_only_case_audit" + build_only_source))
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
        ]
        self.assertNotIn("optimize", calls)
        self.assertNotIn("presolve", calls)

    def test_locked_regular_and_overcontract_tariff_rules_remain(self) -> None:
        may_transition_rate = _regular_basic_rate(self.inputs, "2025-05", None)
        may_average = 0.5 * (
            _regular_basic_rate(self.inputs, "2025-05", "summer")
            + _regular_basic_rate(self.inputs, "2025-05", "non_summer")
        )
        self.assertAlmostEqual(may_transition_rate, may_average)
        rule = self.inputs.settlement_interface["overcontract_rule"]
        self.assertEqual(float(rule["tier1_threshold_fraction"]), 0.10)
        self.assertEqual(float(rule["tier1_multiplier"]), 2.0)
        self.assertEqual(float(rule["tier2_multiplier"]), 3.0)


if __name__ == "__main__":
    unittest.main()
