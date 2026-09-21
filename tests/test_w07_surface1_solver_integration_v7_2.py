"""W-07 Surface-1 solver integration tests (Pre-EOB Solver Integration Gate).

Closes the validation gap carried forward from Gate B: the corrected
solver-facing MILP formulation had only static/algebraic validation.  These
tests BUILD AND OPTIMIZE small synthetic MILPs through the unchanged
production ``build_eob_model`` / ``solve_eob`` path and read the solved
``q_tier1`` variable back out of ``billing_aux``.

Scope guard: the fixtures replace the annual frame with a handful of
synthetic hours and lock E_N = 0, P_B = 0, CC and p_grid.  No production
annual optimization is performed, and no EOB artifact is written.

Model budget: 2 model builds / 2 optimize() calls in this module.
"""

from __future__ import annotations

import json
import unittest
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

ORDER = ("half", "sat_half", "off")
TOL = 1e-6  # strict solver tolerance, not an economic tolerance


@unittest.skipIf(core is None, "gurobipy is required for the solver integration gate")
class W07Surface1SolverIntegration(unittest.TestCase):
    """Exercise the corrected per-increment 2x allowance inside a real MILP."""

    MODELS_BUILT = 0
    SOLVES = 0

    @classmethod
    def setUpClass(cls) -> None:
        cls.root = Path(__file__).resolve().parents[1]
        cls.live = core.load_annual_design_inputs(
            cls.root,
            annual_parquet=cls.root / "data" / "processed" / "__not_used__.parquet",
            annual_csv=cls.root / "data" / "processed" / "annual_input_v7_1.csv",
        )
        cls.evidence: list[dict] = []

    # ------------------------------------------------------------------
    # fixture construction
    # ------------------------------------------------------------------
    def _fixture_inputs(self, months, order=ORDER, season="non_summer"):
        """months: {usage_period_id: {tou_period: target billing demand D}}."""
        rows = []
        base = pd.Timestamp("2025-02-03 10:00:00")
        step = 0
        for month, demands in months.items():
            for period in order:
                rows.append(
                    {
                        "timestamp": base + pd.Timedelta(hours=step),
                        "baseline_load_kw": float(demands[period]) / self.live.kappa,
                        "pv_available_kw": 0.0,
                        "season": season,
                        "tou_period": period,
                        "billing_usage_period_id": month,
                    }
                )
                step += 1
        annual = pd.DataFrame(rows)

        mask = (
            self.live.settlement_matrix["billing_usage_period_id"]
            .astype(str)
            .isin(tuple(months))
            & self.live.settlement_matrix["season"].astype(str).eq(season)
            & self.live.settlement_matrix["tou_period"].astype(str).isin(order)
        )
        matrix = self.live.settlement_matrix.loc[mask].copy()
        self.assertEqual(len(matrix), len(order) * len(months))
        matrix.loc[:, "hour_count"] = 1
        matrix.loc[:, "active_in_hourly_case"] = True
        matrix.loc[:, "billing_period_role"] = (
            "pure_summer" if season == "summer" else "pure_non_summer"
        )

        return replace(
            self.live,
            annual=annual,
            energy_rate_ntd2023_per_kwh=np.zeros(len(annual), dtype=float),
            settlement_matrix=matrix.reset_index(drop=True),
        )

    def _solve(self, months, cc_kw, order=ORDER, season="non_summer"):
        inputs = self._fixture_inputs(months, order=order, season=season)
        settings = core.SolveSettings(
            mode="binary", mip_gap=1e-9, time_limit_sec=300.0,
            output_flag=0, numeric_focus=3,
        )
        original = core.build_eob_model
        captured: dict[str, object] = {}

        def locked_builder(received_inputs, received_settings, layer_a_requirements=None):
            model, handles = original(received_inputs, received_settings, layer_a_requirements)
            model.addConstr(handles["E_N"] == 0.0, name="fx_E_N")
            model.addConstr(handles["P_B"] == 0.0, name="fx_P_B")
            model.addConstr(handles["CC"] == float(cc_kw), name="fx_CC")
            loads = received_inputs.annual["baseline_load_kw"].to_numpy(dtype=float)
            for t, value in enumerate(loads):
                model.addConstr(handles["p_grid"][t] == float(value), name=f"fx_grid_{t}")
            type(self).MODELS_BUILT += 1
            captured["model"] = model
            captured["handles"] = handles
            return model, handles

        try:
            with patch.object(core, "build_eob_model", locked_builder):
                result = core.solve_eob(inputs, settings)
            type(self).SOLVES += 1
            self.assertEqual(result["status"], "OPTIMAL")
            model = captured["model"]
            handles = captured["handles"]
            observed = {}
            for month in months:
                aux = handles["billing_aux"][month]["periods"]
                prev_z = 0.0
                per = {}
                for period in order:
                    a = aux[period]
                    z = float(a["z"].X)
                    per[period] = {
                        "D": float(a["D"].X),
                        "raw": float(a["raw"].X),
                        "z": z,
                        "delta_z": z - prev_z,
                        "q_tier1": float(a["s"].X),
                        "rate": float(a["rate"]),
                    }
                    prev_z = z
                observed[month] = per
            observed["_meta"] = {
                "num_vars": model.NumVars,
                "num_constrs": model.NumConstrs,
                "runtime_sec": round(model.Runtime, 4),
                "status": result["status"],
                "cost_overcontract_pure_season": float(
                    result["cost_components_ntd2023_per_year"]["overcontract_pure_season"]
                ),
                "cc_kw": float(handles["CC"].X),
                "tier1_frac_times_cc": 0.10 * float(handles["CC"].X),
            }
            return observed
        finally:
            m = captured.get("model")
            if m is not None:
                m.dispose()

    # ------------------------------------------------------------------
    # assertions shared by S1 / S2 / S3
    # ------------------------------------------------------------------
    def _check_month(self, label, per, cc_kw, expected):
        """expected: {period: (q, q_2x, q_3x)}; also cross-checks the helper."""
        h = 0.10 * cc_kw
        prior_max = 0.0
        total = 0.0
        for period in ORDER:
            o = per[period]
            exp_q, exp_2x, exp_3x = expected[period]
            # frozen pure/exact helper on the same inputs
            hq, h2x, h3x = core.overcontract_tier_split(o["raw"], prior_max, h)
            self.assertAlmostEqual(o["delta_z"], exp_q, delta=TOL,
                                   msg=f"{label}/{period} q")
            self.assertAlmostEqual(o["q_tier1"], exp_2x, delta=TOL,
                                   msg=f"{label}/{period} q_2x")
            self.assertAlmostEqual(o["delta_z"] - o["q_tier1"], exp_3x, delta=TOL,
                                   msg=f"{label}/{period} q_3x")
            # solver == frozen helper
            self.assertAlmostEqual(o["delta_z"], hq, delta=TOL)
            self.assertAlmostEqual(o["q_tier1"], h2x, delta=TOL)
            # q_2x == min(q, h) numerically
            self.assertAlmostEqual(o["q_tier1"], min(o["delta_z"], h), delta=TOL)
            # W identity
            w = 2.0 * o["q_tier1"] + 3.0 * (o["delta_z"] - o["q_tier1"])
            self.assertAlmostEqual(w, 3.0 * o["delta_z"] - o["q_tier1"], delta=TOL)
            total += o["rate"] * w
            prior_max = max(prior_max, o["raw"])
            self.evidence.append({
                "case": label, "period": period, "cc_kw": cc_kw, "h_kw": h,
                "D_kw": o["D"], "raw_kw": o["raw"], "q_kw": o["delta_z"],
                "solver_q_2x_kw": o["q_tier1"],
                "solver_q_3x_kw": o["delta_z"] - o["q_tier1"],
                "helper_q_2x_kw": h2x, "helper_q_3x_kw": h3x,
                "W_kw": w, "rate_ntd2023_per_kw_month": o["rate"],
                "binding": ("h-binding" if o["delta_z"] > h + TOL
                            else "q-binding" if o["delta_z"] > TOL else "inactive"),
            })
        return total

    # ------------------------------------------------------------------
    # S1 (+ S3 in the same model) and S2
    # ------------------------------------------------------------------
    def test_s1_and_s3_cc240(self):
        """S1: CC=240, h=24, q=3/3/27 -> 24/3.  S3: zero later increments."""
        months = {
            "2025-02": {"half": 243.0, "sat_half": 246.0, "off": 273.0},   # r = 3/6/33
            "2025-03": {"half": 270.0, "sat_half": 250.0, "off": 245.0},   # r = 30/10/5
        }
        obs = self._solve(months, 240.0)
        meta = obs.pop("_meta")
        self.assertAlmostEqual(meta["tier1_frac_times_cc"], 24.0, delta=TOL)

        s1 = self._check_month("S1", obs["2025-02"], 240.0, {
            "half": (3.0, 3.0, 0.0),
            "sat_half": (3.0, 3.0, 0.0),
            "off": (27.0, 24.0, 3.0),       # HARD: not 18/9
        })
        # explicit rejection of the historical defective allocation
        off = obs["2025-02"]["off"]
        self.assertNotAlmostEqual(off["q_tier1"], 18.0, delta=1e-3)
        self.assertNotAlmostEqual(off["delta_z"] - off["q_tier1"], 9.0, delta=1e-3)
        self.assertAlmostEqual(
            2.0 * off["q_tier1"] + 3.0 * (off["delta_z"] - off["q_tier1"]),
            57.0, delta=TOL)

        s3 = self._check_month("S3", obs["2025-03"], 240.0, {
            "half": (30.0, 24.0, 6.0),
            "sat_half": (0.0, 0.0, 0.0),    # zero later increment
            "off": (0.0, 0.0, 0.0),
        })
        self.assertAlmostEqual(
            meta["cost_overcontract_pure_season"], s1 + s3, delta=1e-6)
        self.evidence.append({"case": "S1+S3", "meta": meta,
                              "solver_overcontract_ntd2023": meta["cost_overcontract_pure_season"],
                              "exact_overcontract_ntd2023": s1 + s3,
                              "residual_ntd2023": meta["cost_overcontract_pure_season"] - (s1 + s3)})

    def test_s2_cc235_fractional(self):
        """S2: CC=235, h=23.5 exactly -> 23.5/3.5; reject 24/3 and 23/4."""
        months = {"2025-02": {"half": 238.0, "sat_half": 241.0, "off": 268.0}}
        obs = self._solve(months, 235.0)
        meta = obs.pop("_meta")
        self.assertAlmostEqual(meta["tier1_frac_times_cc"], 23.5, delta=TOL)

        total = self._check_month("S2", obs["2025-02"], 235.0, {
            "half": (3.0, 3.0, 0.0),
            "sat_half": (3.0, 3.0, 0.0),
            "off": (27.0, 23.5, 3.5),       # HARD: continuous, not rounded
        })
        off = obs["2025-02"]["off"]
        q3x = off["delta_z"] - off["q_tier1"]
        for rejected in (24.0, 23.0):
            self.assertNotAlmostEqual(off["q_tier1"], rejected, delta=1e-3)
        for rejected in (3.0, 4.0):
            self.assertNotAlmostEqual(q3x, rejected, delta=1e-3)
        self.assertAlmostEqual(
            2.0 * off["q_tier1"] + 3.0 * q3x, 57.5, delta=TOL)
        self.assertAlmostEqual(
            meta["cost_overcontract_pure_season"], total, delta=1e-6)
        self.evidence.append({"case": "S2", "meta": meta,
                              "solver_overcontract_ntd2023": meta["cost_overcontract_pure_season"],
                              "exact_overcontract_ntd2023": total,
                              "residual_ntd2023": meta["cost_overcontract_pure_season"] - total})

    def test_r5_structural_z_patterns(self):
        """R4+R5: exact running max across raw patterns, in a rate ordering
        where no interior z has a zero objective coefficient, so the separate
        D-epigraph exploit cannot mask the z/raw repair.

        summer peak/half/sat_half rates are 223.6 > 166.9 > 44.7, so every
        interior z coefficient 3*(rate_k - rate_{k+1}) is strictly positive.
        """
        order = ("peak", "half", "sat_half")
        cc = 240.0
        patterns = {
            "2025-06": (5.0, 10.0, 20.0),    # strictly increasing
            "2025-07": (30.0, 10.0, 5.0),    # strictly decreasing  (== R4 / S3)
            "2025-08": (10.0, 10.0, 10.0),   # equal consecutive
            "2025-09": (20.0, 5.0, 30.0),    # new max after a non-new-max
        }
        expected_z = {
            "2025-06": (5.0, 10.0, 20.0),
            "2025-07": (30.0, 30.0, 30.0),
            "2025-08": (10.0, 10.0, 10.0),
            "2025-09": (20.0, 20.0, 30.0),
        }
        months = {m: {p: cc + r for p, r in zip(order, raws)}
                  for m, raws in patterns.items()}
        obs = self._solve(months, cc, order=order, season="summer")
        meta = obs.pop("_meta")

        # (a) STRUCTURAL relations introduced by the repair: these must hold for
        #     every feasible solution, independently of whether the chain input
        #     D is pinned.
        for month in patterns:
            prev = 0.0
            for period in order:
                o = obs[month][period]
                with self.subTest(structural=f"{month}/{period}"):
                    self.assertAlmostEqual(
                        o["raw"], max(0.0, o["D"] - cc), delta=TOL,
                        msg=f"{month}/{period} raw != max(0, D-CC)")
                    self.assertAlmostEqual(
                        o["z"], max(prev, o["raw"]), delta=TOL,
                        msg=f"{month}/{period} z != max(z_prev, raw)")
                prev = o["z"]

        # (b) VALUE oracle: the solved quantities must equal the intended ones.
        for month, raws in patterns.items():
            per = obs[month]
            prev = 0.0
            for i, period in enumerate(order):
                o = per[period]
                true_running_max = max(raws[: i + 1])
                with self.subTest(value=f"{month}/{period}"):
                    self.assertAlmostEqual(o["raw"], raws[i], delta=TOL,
                                           msg=f"{month}/{period} raw not exact")
                    self.assertAlmostEqual(o["z"], expected_z[month][i], delta=TOL,
                                           msg=f"{month}/{period} z not exact")
                    self.assertAlmostEqual(o["z"], true_running_max, delta=TOL)
                    q_frozen = max(0.0, true_running_max - prev)
                    self.assertAlmostEqual(o["delta_z"], q_frozen, delta=TOL,
                                           msg=f"{month}/{period} delta_z != frozen q")
                prev = o["z"]
            # R4: zero later increments produce no allocation and no charge
            if month == "2025-07":
                for period in order[1:]:
                    o = per[period]
                    self.assertAlmostEqual(o["delta_z"], 0.0, delta=TOL)
                    self.assertAlmostEqual(o["q_tier1"], 0.0, delta=TOL)
                    self.assertAlmostEqual(o["delta_z"] - o["q_tier1"], 0.0, delta=TOL)

        # solver over-contract must equal the frozen pure/exact reconstruction
        exact = 0.0
        for month in patterns:
            prior = 0.0
            for period in order:
                o = obs[month][period]
                q, q2, q3 = core.overcontract_tier_split(o["raw"], prior, 0.10 * cc)
                exact += o["rate"] * (2.0 * q2 + 3.0 * q3)
                prior = max(prior, o["raw"])
        self.assertAlmostEqual(meta["cost_overcontract_pure_season"], exact, delta=1e-6)
        self.evidence.append({
            "case": "R5", "meta": meta,
            "solver_overcontract_ntd2023": meta["cost_overcontract_pure_season"],
            "exact_overcontract_ntd2023": exact,
            "residual_ntd2023": meta["cost_overcontract_pure_season"] - exact,
            "z_by_month": {m: [obs[m][p]["z"] for p in order] for m in patterns},
            "delta_z_by_month": {m: [obs[m][p]["delta_z"] for p in order] for m in patterns},
        })

    def test_e5_multi_period_class_c_transition(self):
        """E5: bounded synthetic MULTI-PERIOD Class-C transition fixture.

        2025-10 sat_half and off are both Class-C, and within each season their
        basic rates are equal (summer 43.031907, non-summer 32.057327), which is
        exactly the adjacent-equal-rate condition that made the running-max
        inflation profitable.  A later period (off) establishes a new maximum.
        """
        month = "2025-10"
        periods = ("sat_half", "off")
        # CC is sized inside this fixture's derived finite bound
        # (CC_ub ~= 68.68 here), so h = 0.10 * CC = 6.0 exactly.
        cc = 60.0
        kap = self.live.kappa
        # (timestamp, tou_period, season, target billing demand D)
        spec = [
            ("2025-10-04 12:00:00", "sat_half", "summer", 64.0),
            ("2025-10-04 13:00:00", "sat_half", "summer", 60.0),
            ("2025-10-11 12:00:00", "off", "summer", 70.0),
            ("2025-10-11 13:00:00", "off", "summer", 66.0),
            ("2025-10-18 12:00:00", "sat_half", "non_summer", 58.0),
            ("2025-10-18 13:00:00", "sat_half", "non_summer", 56.0),
            ("2025-10-25 12:00:00", "off", "non_summer", 100.0),
            ("2025-10-25 13:00:00", "off", "non_summer", 95.0),
        ]
        annual = pd.DataFrame(
            {
                "timestamp": pd.to_datetime([s[0] for s in spec]),
                "baseline_load_kw": [s[3] / kap for s in spec],
                "pv_available_kw": [0.0] * len(spec),
                "season": [s[2] for s in spec],
                "tou_period": [s[1] for s in spec],
                "billing_usage_period_id": [month] * len(spec),
            }
        )
        mask = (
            self.live.settlement_matrix["billing_usage_period_id"].astype(str).eq(month)
            & self.live.settlement_matrix["tou_period"].astype(str).isin(periods)
        )
        matrix = self.live.settlement_matrix.loc[mask].copy()
        self.assertEqual(len(matrix), 4)
        matrix.loc[:, "hour_count"] = 2
        matrix.loc[:, "active_in_hourly_case"] = True
        matrix.loc[:, "billing_period_role"] = "transition"
        inputs = replace(
            self.live,
            annual=annual,
            energy_rate_ntd2023_per_kwh=np.zeros(len(annual), dtype=float),
            settlement_matrix=matrix.reset_index(drop=True),
        )

        settings = core.SolveSettings(
            mode="binary", mip_gap=1e-9, time_limit_sec=300.0,
            output_flag=0, numeric_focus=3,
        )
        original = core.build_eob_model
        captured: dict[str, object] = {}

        def locked_builder(ri, rs, lar=None):
            model, handles = original(ri, rs, lar)
            model.addConstr(handles["E_N"] == 0.0)
            model.addConstr(handles["P_B"] == 0.0)
            model.addConstr(handles["CC"] == cc)
            for t, v in enumerate(ri.annual["baseline_load_kw"].to_numpy(dtype=float)):
                model.addConstr(handles["p_grid"][t] == float(v))
            type(self).MODELS_BUILT += 1
            captured["model"] = model
            captured["handles"] = handles
            return model, handles

        try:
            with patch.object(core, "build_eob_model", locked_builder):
                result = core.solve_eob(inputs, settings)
            type(self).SOLVES += 1
            self.assertEqual(result["status"], "OPTIMAL")
            aux = captured["handles"]["billing_aux"][month]["periods"]

            expected_D = {"sat_half": 64.0, "off": 100.0}
            expected_raw = {"sat_half": 4.0, "off": 40.0}
            expected_z = {"sat_half": 4.0, "off": 40.0}
            expected_q = {"sat_half": 4.0, "off": 36.0}
            expected_2x = {"sat_half": 4.0, "off": 6.0}    # h = 6 binds on off
            expected_3x = {"sat_half": 0.0, "off": 30.0}
            expected_source = {"sat_half": "summer", "off": "non_summer"}

            prev_z = 0.0
            exact_w = {}
            for period in periods:
                a = aux[period]
                D = float(a["D"].X)
                raw = float(a["raw"].X)
                z = float(a["z"].X)
                dz = z - prev_z
                q1 = float(a["s"].X)
                with self.subTest(period=period):
                    self.assertAlmostEqual(D, expected_D[period], delta=TOL,
                                           msg=f"{period} D not exact")
                    self.assertAlmostEqual(raw, expected_raw[period], delta=TOL)
                    self.assertAlmostEqual(z, expected_z[period], delta=TOL)
                    self.assertAlmostEqual(z, max(prev_z, raw), delta=TOL)
                    self.assertAlmostEqual(dz, expected_q[period], delta=TOL)
                    self.assertAlmostEqual(q1, expected_2x[period], delta=TOL)
                    self.assertAlmostEqual(dz - q1, expected_3x[period], delta=TOL)
                    self.assertAlmostEqual(q1, min(dz, 0.10 * cc), delta=TOL)
                    # frozen pure/exact helper agreement
                    hq, h2x, h3x = core.overcontract_tier_split(
                        raw, prev_z, 0.10 * cc)
                    self.assertAlmostEqual(dz, hq, delta=TOL)
                    self.assertAlmostEqual(q1, h2x, delta=TOL)
                exact_w[period] = 2.0 * q1 + 3.0 * (dz - q1)
                prev_z = z

            # transition source/rate selection must still be correct
            detail = result["transition_settlement_detail"]
            detail = detail[detail["tou_period"].astype(str).isin(periods)]
            self.assertEqual(len(detail), 2)
            expected_cost = 0.0
            for _, row in detail.iterrows():
                period = str(row["tou_period"])
                with self.subTest(source=period):
                    self.assertEqual(str(row["max_timestamp_season"]),
                                     expected_source[period])
                rate = float(row["resolved_rate_ntd2023_per_kw_month"])
                expected_cost += rate * exact_w[period]

            solver_cost = float(
                result["cost_components_ntd2023_per_year"][
                    "overcontract_transition_resolved"]
            )
            self.assertAlmostEqual(solver_cost, expected_cost, delta=1e-6)
            self.evidence.append({
                "case": "E5_multi_period_class_c", "month": month,
                "periods": list(periods),
                "D": {p: float(aux[p]["D"].X) for p in periods},
                "raw": {p: float(aux[p]["raw"].X) for p in periods},
                "z": {p: float(aux[p]["z"].X) for p in periods},
                "q_2x": {p: float(aux[p]["s"].X) for p in periods},
                "W": exact_w,
                "solver_transition_cost_ntd2023": solver_cost,
                "exact_transition_cost_ntd2023": expected_cost,
                "residual_ntd2023": solver_cost - expected_cost,
            })
        finally:
            m = captured.get("model")
            if m is not None:
                m.dispose()

    @classmethod
    def tearDownClass(cls) -> None:
        print("W07_SURFACE1_MODELS_BUILT=" + str(cls.MODELS_BUILT))
        print("W07_SURFACE1_SOLVES=" + str(cls.SOLVES))
        for row in cls.evidence:
            print("W07_SURFACE1_EVIDENCE=" + json.dumps(row, sort_keys=True, default=float))


if __name__ == "__main__":
    unittest.main(verbosity=2)
