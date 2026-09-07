"""Focused production-backed Class-C monetary-settlement integration tests.

These are deliberately tiny four-hour fixtures, not annual research cases.
They invoke the unchanged production ``build_eob_model`` / ``solve_eob``
path, including its native MAX resultants, source selector, bounded product,
objective allocation, and post-solve provenance checks.  The test wrapper adds
only fixture locks for dispatch, BESS size, and regular contract capacity; it
does not recreate any production transition equations.
"""

from __future__ import annotations

import json
import unittest
from dataclasses import dataclass
from dataclasses import replace
from pathlib import Path
from unittest.mock import patch

import numpy as np
import pandas as pd

try:  # pragma: no cover - availability depends on the invoking environment
    import gurobipy  # noqa: F401
except ImportError:  # pragma: no cover - the project .venv supplies Gurobi
    core = None
else:
    from src import annual_design_model_v7_2 as core


@dataclass(frozen=True)
class _ClassCFixture:
    case_id: str
    early_load_kw: tuple[float, float]
    later_load_kw: tuple[float, float]
    expected_source: str
    expected_policy_status: str


@unittest.skipIf(core is None, "gurobipy is required for the focused integration test")
class ProductionClassCIntegrationTests(unittest.TestCase):
    """Exercise the live October Class-C/off production branch end to end."""

    MONTH = "2025-10"
    TOU_PERIOD = "off"
    EARLY_SEASON = "summer"
    LATER_SEASON = "non_summer"
    FIXED_CC_KW = 100.0

    FIXTURES = (
        _ClassCFixture(
            case_id="C1_early_season_wins",
            early_load_kw=(1200.0, 1180.0),
            later_load_kw=(900.0, 880.0),
            expected_source="summer",
            expected_policy_status="EARLIER_SEASON_CLEARLY_LARGER",
        ),
        _ClassCFixture(
            case_id="C2_later_season_wins",
            early_load_kw=(900.0, 880.0),
            later_load_kw=(1200.0, 1180.0),
            expected_source="non_summer",
            expected_policy_status="LATER_SEASON_CLEARLY_LARGER",
        ),
        _ClassCFixture(
            case_id="C3_genuine_numerical_tie",
            early_load_kw=(1200.0, 1180.0),
            later_load_kw=(1200.0, 1180.0),
            expected_source="summer",
            expected_policy_status="NUMERICAL_TIE_EARLIEST_MAX_TIMESTAMP",
        ),
    )

    @classmethod
    def setUpClass(cls) -> None:
        cls.root = Path(__file__).resolve().parents[1]
        cls.live_inputs = core.load_annual_design_inputs(
            cls.root,
            annual_parquet=cls.root / "data" / "processed" / "__not_used__.parquet",
            annual_csv=cls.root / "data" / "processed" / "annual_input_v7_1.csv",
        )

    def _fixture_inputs(self, fixture: _ClassCFixture):
        timestamps = pd.to_datetime(
            (
                "2025-10-01 12:00:00",
                "2025-10-01 13:00:00",
                "2025-10-16 12:00:00",
                "2025-10-16 13:00:00",
            )
        )
        synthetic_load = tuple(fixture.early_load_kw + fixture.later_load_kw)
        annual = pd.DataFrame(
            {
                "timestamp": timestamps,
                "baseline_load_kw": synthetic_load,
                "pv_available_kw": (0.0, 0.0, 0.0, 0.0),
                "season": (
                    self.EARLY_SEASON,
                    self.EARLY_SEASON,
                    self.LATER_SEASON,
                    self.LATER_SEASON,
                ),
                "tou_period": (self.TOU_PERIOD,) * 4,
                "billing_usage_period_id": (self.MONTH,) * 4,
            }
        )
        matrix_mask = (
            self.live_inputs.settlement_matrix["billing_usage_period_id"]
            .astype(str)
            .eq(self.MONTH)
            & self.live_inputs.settlement_matrix["tou_period"].astype(str).eq(
                self.TOU_PERIOD
            )
            & self.live_inputs.settlement_matrix["season"].astype(str).isin(
                (self.EARLY_SEASON, self.LATER_SEASON)
            )
        )
        settlement_matrix = self.live_inputs.settlement_matrix.loc[matrix_mask].copy()
        self.assertEqual(len(settlement_matrix), 2)
        settlement_matrix.loc[:, "hour_count"] = 2
        settlement_matrix.loc[:, "active_in_hourly_case"] = True
        settlement_matrix.loc[:, "billing_period_role"] = "transition"

        return replace(
            self.live_inputs,
            annual=annual,
            energy_rate_ntd2023_per_kwh=np.zeros(len(annual), dtype=float),
            settlement_matrix=settlement_matrix.reset_index(drop=True),
        )

    def _run_fixture(self, fixture: _ClassCFixture) -> dict[str, object]:
        inputs = self._fixture_inputs(fixture)
        settings = core.SolveSettings(
            mode="binary",
            mip_gap=1e-6,
            time_limit_sec=900.0,
            output_flag=0,
            numeric_focus=1,
        )
        original_builder = core.build_eob_model
        captured: dict[str, object] = {}

        def fixture_locked_builder(received_inputs, received_settings, layer_a_requirements=None):
            self.assertIs(received_inputs, inputs)
            model, handles = original_builder(
                received_inputs, received_settings, layer_a_requirements
            )
            model.addConstr(handles["E_N"] == 0.0, name="fixture_lock_E_N_zero")
            model.addConstr(handles["P_B"] == 0.0, name="fixture_lock_P_B_zero")
            model.addConstr(
                handles["CC"] == self.FIXED_CC_KW,
                name="fixture_lock_CC",
            )
            loads = inputs.annual["baseline_load_kw"].to_numpy(dtype=float)
            for t, value in enumerate(loads):
                model.addConstr(
                    handles["p_grid"][t] == float(value),
                    name=f"fixture_lock_grid_t{t}",
                )
            captured["model"] = model
            captured["handles"] = handles
            return model, handles

        try:
            # ``solve_eob`` performs the production post-solve audit as well as
            # optimizing the builder's unmodified Class-C formulation.
            with patch.object(core, "build_eob_model", fixture_locked_builder):
                result = core.solve_eob(inputs, settings)

            self.assertEqual(result["status"], "OPTIMAL")
            detail = result["transition_settlement_detail"]
            self.assertEqual(len(detail), 1)
            row = detail.iloc[0]
            self.assertEqual(
                row["settlement_class"],
                "CLASS_C_TWO_SEASON_DIFFERENT_SETTLEMENT_RATE",
            )

            handles = captured["handles"]
            period_aux = handles["billing_aux"][self.MONTH]["periods"][
                self.TOU_PERIOD
            ]
            source_binary = int(round(float(period_aux["transition_source_later"].X)))
            delta_z = float(period_aux["z"].X)
            delta_s = float(period_aux["s"].X)
            quantity_w = float(3.0 * delta_z - delta_s)
            product_q = float(period_aux["transition_product_later"].X)

            seasonal_exact = json.loads(row["seasonal_maxima_kw"])
            seasonal_native = json.loads(row["solver_seasonal_maxima_kw"])
            candidate_rates = json.loads(row["candidate_rates_ntd2023_per_kw_month"])
            early_exact = float(seasonal_exact[self.EARLY_SEASON])
            later_exact = float(seasonal_exact[self.LATER_SEASON])
            selected_source = str(row["selected_max_source_season"])
            selected_rate = float(row["resolved_rate_ntd2023_per_kw_month"])
            expected_rate = float(candidate_rates[fixture.expected_source])
            expected_charge = float(expected_rate * quantity_w)
            solver_charge = float(
                result["cost_components_ntd2023_per_year"][
                    "overcontract_transition_resolved"
                ]
            )
            direct_product = float(source_binary * quantity_w)
            source_policy_status = str(row["cross_season_tie_status"])
            boundary_affects_settlement = bool(row["boundary_affects_settlement"])

            self.assertEqual(
                tuple(period_aux["transition_spec"]["chronological_seasons"]),
                (self.EARLY_SEASON, self.LATER_SEASON),
            )
            self.assertEqual(source_policy_status, fixture.expected_policy_status)
            self.assertEqual(selected_source, fixture.expected_source)
            self.assertEqual(source_binary, int(fixture.expected_source == self.LATER_SEASON))
            self.assertAlmostEqual(
                float(row["later_minus_earlier_max_kw"]),
                later_exact - early_exact,
                delta=core.BALANCE_TOL,
            )
            self.assertAlmostEqual(
                float(seasonal_native[self.EARLY_SEASON]),
                early_exact,
                delta=core.BALANCE_TOL,
            )
            self.assertAlmostEqual(
                float(seasonal_native[self.LATER_SEASON]),
                later_exact,
                delta=core.BALANCE_TOL,
            )
            self.assertAlmostEqual(
                quantity_w,
                float(row["equivalent_overcontract_quantity_W_kw"]),
                delta=core.BALANCE_TOL,
            )
            self.assertAlmostEqual(
                product_q,
                direct_product,
                delta=core.BALANCE_TOL,
            )
            self.assertAlmostEqual(
                solver_charge,
                expected_charge,
                delta=core.COST_RECONCILIATION_TOL_NTD,
            )
            self.assertAlmostEqual(
                float(row["resolved_exact_charge_ntd2023"]),
                expected_charge,
                delta=core.COST_RECONCILIATION_TOL_NTD,
            )
            self.assertGreater(delta_z, 0.0)
            self.assertGreater(delta_s, 0.0)
            self.assertGreater(delta_z - delta_s, 0.0)
            self.assertGreater(quantity_w, 0.0)
            self.assertTrue(bool(row["mcCormick_product_pass"]))
            self.assertTrue(bool(row["source_selection_consistency_pass"]))
            self.assertTrue(bool(row["max_timestamp_consistency_pass"]))
            self.assertTrue(bool(row["resolved_rate_consistency_pass"]))
            self.assertTrue(bool(row["native_seasonal_max_pass"]))
            self.assertFalse(boundary_affects_settlement)
            self.assertEqual(
                result["transition_settlement"]["nonbinding_certificate"],
                "PASS_NO_RATE_AMBIGUOUS_INCREMENTAL_OVERAGE",
            )

            if fixture.case_id == "C3_genuine_numerical_tie":
                self.assertLess(
                    float(candidate_rates[self.LATER_SEASON]),
                    float(candidate_rates[self.EARLY_SEASON]),
                )
                self.assertEqual(selected_source, self.EARLY_SEASON)
                self.assertEqual(
                    str(row["max_timestamp"]), "2025-10-01 12:00:00"
                )
                self.assertEqual(str(row["max_timestamp_season"]), self.EARLY_SEASON)
                self.assertGreater(
                    solver_charge,
                    float(candidate_rates[self.LATER_SEASON]) * quantity_w
                    + core.COST_RECONCILIATION_TOL_NTD,
                )

            return {
                "case": fixture.case_id,
                "early_exact_kw": early_exact,
                "later_exact_kw": later_exact,
                "difference_later_minus_earlier_kw": float(
                    row["later_minus_earlier_max_kw"]
                ),
                "tie_band_kw": float(row["transition_tie_band_kw"]),
                "selection_guard_kw": float(row["transition_selection_guard_kw"]),
                "source_expected": fixture.expected_source,
                "source_selected": selected_source,
                "source_policy_status": source_policy_status,
                "source_binary_y": source_binary,
                "selected_rate_ntd2023_per_kw_month": selected_rate,
                "expected_rate_ntd2023_per_kw_month": expected_rate,
                "delta_z_kw": delta_z,
                "delta_s_kw": delta_s,
                "tier1_kw": delta_s,
                "tier2_kw": float(delta_z - delta_s),
                "W_kw": quantity_w,
                "q_kw": product_q,
                "direct_yW_kw": direct_product,
                "q_minus_yW_kw": float(product_q - direct_product),
                "expected_charge_ntd2023": expected_charge,
                "solver_charge_ntd2023": solver_charge,
                "charge_residual_ntd2023": float(solver_charge - expected_charge),
                "boundary_affects_settlement": boundary_affects_settlement,
                "max_timestamp": str(row["max_timestamp"]),
                "max_timestamp_season": str(row["max_timestamp_season"]),
            }
        finally:
            model = captured.get("model")
            if model is not None:
                model.dispose()

    def test_positive_class_c_monetary_settlement_uses_production_path(self) -> None:
        for fixture in self.FIXTURES:
            with self.subTest(case=fixture.case_id):
                observed = self._run_fixture(fixture)
                # Emit the required test evidence without creating a production
                # result artifact. unittest leaves stdout visible under -v.
                print("CLASS_C_INTEGRATION_RESULT=" + json.dumps(observed, sort_keys=True))


if __name__ == "__main__":
    unittest.main(verbosity=2)
