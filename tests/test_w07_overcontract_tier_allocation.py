"""W-07 deterministic, non-solver regression suite (Gate B).

Frozen W-07 semantics (official basis: 詳細電價表 §七(一)2.(5) non-duplication and
§七(二) 10% / 2x / 3x):

    r[p]    = max(0, D[p] - C[p])
    q[p]    = max(0, r[p] - max_{j<p} r[j])
    h[p]    = 0.10 * C[p]                      (continuous; never rounded)
    q_2x[p] = min(q[p], h[p])
    q_3x[p] = q[p] - q_2x[p]
    charge  = rate[p] * (2*q_2x[p] + 3*q_3x[p])

No Gurobi model is constructed anywhere in this module.  ``gurobipy.Model`` is
replaced by a raising sentinel before the production core is imported, so an
accidental model construction fails loudly instead of consuming a licence.
The solver-facing formulation (Surface 1) is validated by static source
inspection only.
"""

from __future__ import annotations

import ast
import importlib.util
import re
import sys
import types
import unittest
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]

# --- hard zero-model guarantee --------------------------------------------
try:  # pragma: no cover - depends on the local project environment
    import gurobipy
except ImportError:  # pragma: no cover - exercised only without Gurobi
    gurobipy = types.ModuleType("gurobipy")
    gurobipy.GRB = types.SimpleNamespace(BINARY="B", OPTIMAL=2)
    sys.modules["gurobipy"] = gurobipy


def _forbidden_model(*_args, **_kwargs):  # pragma: no cover - must never run
    raise AssertionError(
        "W-07 Gate B regression attempted to construct a Gurobi model."
    )


gurobipy.Model = _forbidden_model

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.annual_design_model_v7_2 import (  # noqa: E402
    PURE_APPLICABLE_PERIODS,
    TOU_ORDER,
    overcontract_tier_split,
)

CORE_PATH = ROOT / "src" / "annual_design_model_v7_2.py"
S13C_PATH = ROOT / "scripts" / "13c_regress_taipower_core_bill_components.py"

_SPEC = importlib.util.spec_from_file_location("s13c_w07", S13C_PATH)
S13C = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(S13C)

TARIFF_REGISTRY = ROOT / "data" / "reference" / "taipower_tariff_registry_v7_1.csv"

# Official school high-voltage three-period (fixed-peak) basic-charge rates.
# Primary source: 高壓及特高壓電力電價 — 幼兒園、大學（專）及社福團體適用,
# (二)三段式時間電價 (verified against the 113-10-16 公告 and 詳細電價表).
RATES = {
    "summer": {"peak": 223.6, "half": 166.9, "sat_half": 44.7, "off": 44.7},
    "non_summer": {"peak": None, "half": 166.9, "sat_half": 33.3, "off": 33.3},
}


def frozen_sequence(periods, raw_by_period, thresholds, rates):
    """Mirror of production Surfaces 2/3, which both call overcontract_tier_split."""
    prior_max = 0.0
    rows = []
    total = 0.0
    for period in periods:
        raw = float(raw_by_period[period])
        cap = 0.10 * float(thresholds[period])
        q, q2x, q3x = overcontract_tier_split(raw, prior_max, cap)
        rate = float(rates[period])
        charge = rate * (2.0 * q2x + 3.0 * q3x)
        total += charge
        rows.append(
            {
                "period": period, "raw": raw, "h": cap, "q": q,
                "q_2x": q2x, "q_3x": q3x, "rate": rate, "charge": charge,
            }
        )
        prior_max = max(prior_max, raw)
    return total, rows


def historical_defective_split(raw, prior_max, cap):
    """Pre-Gate-B behaviour: a single cumulative 2x pool shared across the month."""
    lower = min(prior_max, raw)
    incremental = max(0.0, raw - prior_max)
    tier1 = max(0.0, min(raw, cap) - min(lower, cap))
    tier2 = max(0.0, incremental - tier1)
    return incremental, tier1, tier2


def historical_sequence(periods, raw_by_period, thresholds, rates):
    prior_max = 0.0
    total = 0.0
    rows = []
    for period in periods:
        raw = float(raw_by_period[period])
        cap = 0.10 * float(thresholds[period])
        q, q2x, q3x = historical_defective_split(raw, prior_max, cap)
        total += float(rates[period]) * (2.0 * q2x + 3.0 * q3x)
        rows.append({"period": period, "q": q, "q_2x": q2x, "q_3x": q3x})
        prior_max = max(prior_max, raw)
    return total, rows


def s13c_overcontract(cc_kw, demands, season):
    """Drive Surface 4 end-to-end against the real tariff registry (read-only)."""
    indexed = S13C.registry_index(S13C.load_registry(TARIFF_REGISTRY))
    row = pd.Series(
        {
            "usage_period_id": "TEST",
            S13C.BILL_COLUMNS["regular_cc_kw"]: cc_kw,
            **{S13C.DEMAND_COLUMNS[p]: demands.get(p, 0.0) for p in TOU_ORDER},
        }
    )
    return S13C.overcontract_components(row, indexed, season)


def ntust_thresholds(cc_kw):
    """NTUST mainline: supplementary contract capacities are fixed to zero."""
    return {p: float(cc_kw) for p in TOU_ORDER}


class W07PublishedExamples(unittest.TestCase):
    """W07-1 / W07-2 — PUBLISHED-EXAMPLE REPRODUCTION ONLY.

    These carry supplementary contract capacities, which Script 13c's
    NTUST-specialised threshold builder deliberately fixes to zero, so they are
    reproduced against the frozen semantics with explicit per-period thresholds.
    """

    def test_w07_1_official_july(self):
        periods = ["peak", "half", "sat_half", "off"]
        thresholds = {"peak": 200.0, "half": 220.0, "sat_half": 230.0, "off": 235.0}
        demands = {"peak": 201.0, "half": 223.0, "sat_half": 236.0, "off": 245.0}
        raw = {p: max(0.0, demands[p] - thresholds[p]) for p in periods}
        self.assertEqual([raw[p] for p in periods], [1.0, 3.0, 6.0, 10.0])

        total, rows = frozen_sequence(periods, raw, thresholds, RATES["summer"])
        self.assertEqual([r["q"] for r in rows], [1.0, 2.0, 3.0, 4.0])
        for r in rows:  # every increment sits below its own 10% allowance
            self.assertAlmostEqual(r["q_3x"], 0.0, places=12)
        self.assertAlmostEqual(total, 1740.6, places=6)

    def test_w07_2_official_january(self):
        # The published final block is 24 @2x + 3 @3x.  It is reproduced as the
        # published continuous 0.10 * C with C = 240 -- NOT by rounding 23.5.
        periods = ["half", "sat_half", "off"]
        thresholds = {p: 240.0 for p in periods}
        raw = {"half": 3.0, "sat_half": 6.0, "off": 33.0}

        total, rows = frozen_sequence(periods, raw, thresholds, RATES["non_summer"])
        self.assertEqual([r["q"] for r in rows], [3.0, 3.0, 27.0])
        final = rows[-1]
        self.assertAlmostEqual(final["h"], 24.0, places=12)
        self.assertAlmostEqual(final["q_2x"], 24.0, places=12)
        self.assertAlmostEqual(final["q_3x"], 3.0, places=12)
        self.assertAlmostEqual(total, 3099.3, places=6)


class W07StructuralOracles(unittest.TestCase):
    def test_w07_3_structural_oracle_discriminates(self):
        """HARD: rounding-independent discriminator (10% of 240 = 24 exactly)."""
        periods = ["half", "sat_half", "off"]
        cc = 240.0
        thresholds = {p: cc for p in periods}
        raw = {"half": 3.0, "sat_half": 6.0, "off": 33.0}

        corrected, rows = frozen_sequence(
            periods, raw, thresholds, RATES["non_summer"]
        )
        final = rows[-1]
        self.assertAlmostEqual(final["h"], 24.0, places=12)
        self.assertAlmostEqual(final["q"], 27.0, places=12)
        self.assertAlmostEqual(final["q_2x"], 24.0, places=12)
        self.assertAlmostEqual(final["q_3x"], 3.0, places=12)
        self.assertAlmostEqual(corrected, 3099.3, places=6)

        old_total, old_rows = historical_sequence(
            periods, raw, thresholds, RATES["non_summer"]
        )
        self.assertAlmostEqual(old_rows[-1]["q_2x"], 18.0, places=12)
        self.assertAlmostEqual(old_rows[-1]["q_3x"], 9.0, places=12)
        self.assertAlmostEqual(old_total, 3299.1, places=6)
        self.assertGreater(abs(old_total - corrected), 1.0)

        s13c_total, detail = s13c_overcontract(
            cc,
            {"peak": 0.0, "half": 243.0, "sat_half": 246.0, "off": 273.0},
            "non_summer",
        )
        off_row = [d for d in detail if d["tou_period"] == "off"][0]
        self.assertAlmostEqual(off_row["tier1_kw"], 24.0, places=12)
        self.assertAlmostEqual(off_row["tier2_kw"], 3.0, places=12)
        self.assertAlmostEqual(s13c_total, corrected, places=6)

    def test_w07_10_fractional_threshold_guard(self):
        """HARD: 10% of 235 must stay 23.5 -- never 24, never 23."""
        cc = 235.0
        periods = ["half", "sat_half", "off"]
        thresholds = {p: cc for p in periods}
        raw = {"half": 3.0, "sat_half": 6.0, "off": 33.0}

        _, rows = frozen_sequence(periods, raw, thresholds, RATES["non_summer"])
        final = rows[-1]
        self.assertAlmostEqual(final["h"], 23.5, places=12)
        self.assertAlmostEqual(final["q"], 27.0, places=12)
        self.assertAlmostEqual(final["q_2x"], 23.5, places=12)
        self.assertAlmostEqual(final["q_3x"], 3.5, places=12)
        for rejected in (24.0, 23.0):
            self.assertNotAlmostEqual(final["q_2x"], rejected, places=6)
        for rejected in (3.0, 4.0):
            self.assertNotAlmostEqual(final["q_3x"], rejected, places=6)

        s13c_total, detail = s13c_overcontract(
            cc,
            {"peak": 0.0, "half": 238.0, "sat_half": 241.0, "off": 268.0},
            "non_summer",
        )
        off_row = [d for d in detail if d["tou_period"] == "off"][0]
        self.assertAlmostEqual(off_row["tier1_cap_kw"], 23.5, places=12)
        self.assertAlmostEqual(off_row["tier1_kw"], 23.5, places=12)
        self.assertAlmostEqual(off_row["tier2_kw"], 3.5, places=12)
        self.assertAlmostEqual(
            s13c_total,
            166.9 * 2 * 3 + 33.3 * 2 * 3 + 33.3 * (2 * 23.5 + 3 * 3.5),
            places=6,
        )


class W07NtustCases(unittest.TestCase):
    def test_w07_4_september_continuity_anchor(self):
        cc = 5000.0
        demands = {"peak": 4896.0, "half": 5016.0, "sat_half": 3352.0, "off": 3776.0}
        periods = list(TOU_ORDER)
        thresholds = ntust_thresholds(cc)
        raw = {p: max(0.0, demands[p] - thresholds[p]) for p in periods}
        self.assertEqual([raw[p] for p in periods], [0.0, 16.0, 0.0, 0.0])

        total, rows = frozen_sequence(periods, raw, thresholds, RATES["summer"])
        half = [r for r in rows if r["period"] == "half"][0]
        self.assertAlmostEqual(half["q"], 16.0, places=12)
        self.assertAlmostEqual(half["q_2x"], 16.0, places=12)
        self.assertAlmostEqual(half["q_3x"], 0.0, places=12)
        self.assertAlmostEqual(half["rate"], 166.9, places=12)
        self.assertAlmostEqual(total, 16.0 * 166.9 * 2.0, places=9)
        self.assertAlmostEqual(total, 5340.8, places=6)

        s13c_total, _ = s13c_overcontract(cc, demands, "summer")
        self.assertAlmostEqual(s13c_total, total, places=6)

        # Continuity anchor, not a discriminator: the historical formula agreed.
        old_total, _ = historical_sequence(periods, raw, thresholds, RATES["summer"])
        self.assertAlmostEqual(old_total, total, places=6)

    def test_w07_5_no_exceedance(self):
        cc = 5000.0
        demands = {"peak": 4000.0, "half": 4200.0, "sat_half": 3000.0, "off": 3500.0}
        periods = list(TOU_ORDER)
        thresholds = ntust_thresholds(cc)
        raw = {p: max(0.0, demands[p] - thresholds[p]) for p in periods}

        total, rows = frozen_sequence(periods, raw, thresholds, RATES["summer"])
        for r in rows:
            self.assertEqual((r["q"], r["q_2x"], r["q_3x"]), (0.0, 0.0, 0.0))
        self.assertAlmostEqual(total, 0.0, places=12)
        s13c_total, _ = s13c_overcontract(cc, demands, "summer")
        self.assertAlmostEqual(s13c_total, 0.0, places=12)

    def test_w07_6_tier1_only(self):
        cc = 5000.0  # h = 500
        demands = {"peak": 5100.0, "half": 0.0, "sat_half": 0.0, "off": 0.0}
        periods = list(TOU_ORDER)
        thresholds = ntust_thresholds(cc)
        raw = {p: max(0.0, demands[p] - thresholds[p]) for p in periods}

        _, rows = frozen_sequence(periods, raw, thresholds, RATES["summer"])
        peak = rows[0]
        self.assertTrue(0.0 < peak["q"] < peak["h"])
        self.assertAlmostEqual(peak["q_2x"], 100.0, places=12)
        self.assertAlmostEqual(peak["q_3x"], 0.0, places=12)

        s13c_total, detail = s13c_overcontract(cc, demands, "summer")
        d = [x for x in detail if x["tou_period"] == "peak"][0]
        self.assertAlmostEqual(d["tier1_kw"], 100.0, places=12)
        self.assertAlmostEqual(d["tier2_kw"], 0.0, places=12)
        self.assertAlmostEqual(s13c_total, 100.0 * 223.6 * 2.0, places=6)

    def test_w07_7_tier_crossing(self):
        cc = 5000.0  # h = 500
        demands = {"peak": 5700.0, "half": 0.0, "sat_half": 0.0, "off": 0.0}
        periods = list(TOU_ORDER)
        thresholds = ntust_thresholds(cc)
        raw = {p: max(0.0, demands[p] - thresholds[p]) for p in periods}

        _, rows = frozen_sequence(periods, raw, thresholds, RATES["summer"])
        peak = rows[0]
        self.assertAlmostEqual(peak["q"], 700.0, places=12)
        self.assertAlmostEqual(peak["h"], 500.0, places=12)
        self.assertAlmostEqual(peak["q_2x"], 500.0, places=12)
        self.assertAlmostEqual(peak["q_3x"], 200.0, places=12)

        s13c_total, detail = s13c_overcontract(cc, demands, "summer")
        d = [x for x in detail if x["tou_period"] == "peak"][0]
        self.assertAlmostEqual(d["tier1_kw"], 500.0, places=12)
        self.assertAlmostEqual(d["tier2_kw"], 200.0, places=12)
        self.assertAlmostEqual(
            s13c_total, 223.6 * (2.0 * 500.0 + 3.0 * 200.0), places=6
        )

    def test_w07_8_zero_later_increment(self):
        cc = 5000.0
        demands = {"peak": 5800.0, "half": 5300.0, "sat_half": 5100.0, "off": 4000.0}
        periods = list(TOU_ORDER)
        thresholds = ntust_thresholds(cc)
        raw = {p: max(0.0, demands[p] - thresholds[p]) for p in periods}
        self.assertEqual([raw[p] for p in periods], [800.0, 300.0, 100.0, 0.0])

        total, rows = frozen_sequence(periods, raw, thresholds, RATES["summer"])
        for r in rows[1:]:
            self.assertAlmostEqual(r["q"], 0.0, places=12)
            self.assertAlmostEqual(r["q_2x"], 0.0, places=12)
            self.assertAlmostEqual(r["q_3x"], 0.0, places=12)
            self.assertAlmostEqual(r["charge"], 0.0, places=12)
        self.assertAlmostEqual(
            total, 223.6 * (2.0 * 500.0 + 3.0 * 300.0), places=6
        )
        s13c_total, _ = s13c_overcontract(cc, demands, "summer")
        self.assertAlmostEqual(s13c_total, total, places=6)

    def test_w07_9_non_summer_peak_is_not_applicable(self):
        self.assertNotIn("peak", PURE_APPLICABLE_PERIODS["non_summer"])
        self.assertIn("peak", PURE_APPLICABLE_PERIODS["summer"])
        self.assertNotIn("peak", S13C.applicable_overcontract_periods("non_summer"))
        self.assertIn("peak", S13C.applicable_overcontract_periods("summer"))

        # A non-summer peak demand far above CC contributes nothing and is not
        # silently priced as an applicable zero-rate period.
        cc = 5000.0
        demands = {"peak": 9000.0, "half": 5100.0, "sat_half": 0.0, "off": 0.0}
        s13c_total, detail = s13c_overcontract(cc, demands, "non_summer")
        self.assertTrue(all(d["tou_period"] != "peak" for d in detail))
        self.assertAlmostEqual(s13c_total, 100.0 * 166.9 * 2.0, places=6)


class W07HelperProperties(unittest.TestCase):
    def test_pure_helper_properties(self):
        # q is never negative
        self.assertEqual(overcontract_tier_split(5.0, 9.0, 100.0), (0.0, 0.0, 0.0))
        # prior exceedance reduces q but never the allowance h
        self.assertEqual(overcontract_tier_split(33.0, 6.0, 24.0), (27.0, 24.0, 3.0))
        # a standalone increment of the same size allocates identically
        self.assertEqual(overcontract_tier_split(27.0, 0.0, 24.0), (27.0, 24.0, 3.0))
        # a negative allowance is clamped, never producing negative tier-1
        self.assertEqual(overcontract_tier_split(10.0, 0.0, -5.0), (10.0, 0.0, 10.0))

    def test_allowance_is_continuous_in_cc(self):
        for cc in (4399.137305991739, 4363.187561632778, 235.0, 240.7, 5000.5):
            h = 0.10 * cc
            q, q2x, q3x = overcontract_tier_split(1e9, 0.0, h)
            self.assertAlmostEqual(q2x, h, places=9)
            self.assertAlmostEqual(q3x, q - h, places=3)
            self.assertEqual(q2x, h)  # exact, not rounded

    def test_idle_reference_semantics_at_zero_cc(self):
        # CC = 0 -> h = 0 -> everything in the 3x tier.
        q, q2x, q3x = overcontract_tier_split(120.0, 0.0, 0.0)
        self.assertEqual((q, q2x, q3x), (120.0, 0.0, 120.0))


class W07StaticSurfaceInspection(unittest.TestCase):
    """Surface 1 is solver-facing; validate it statically -- never build a model."""

    @classmethod
    def setUpClass(cls):
        cls.core_src = CORE_PATH.read_text(encoding="utf-8")
        cls.s13c_src = S13C_PATH.read_text(encoding="utf-8")

    def test_solver_surface_uses_per_increment_allowance(self):
        # q_tier1 <= this period's own increment, and <= 0.10*CC.
        self.assertIn("q_tier1 <= delta_z", self.core_src)
        self.assertIn("q_tier1 <= tier_threshold", self.core_src)
        self.assertIn("tier1_threshold_link", self.core_src)
        self.assertIn("delta_s = q_tier1", self.core_src)

    def test_solver_surface_dropped_cumulative_pool(self):
        for removed in (
            "s_tier",
            "s_prev",
            "tier1_monotone",
            "tier1_increment_le_total",
            "tier1_le_cum",
        ):
            self.assertNotIn(removed, self.core_src, f"stale pool construct: {removed}")

    def test_objective_weighting_is_2x_and_3x(self):
        self.assertIn("tier1_mult * delta_s + tier2_mult * (delta_z - delta_s)",
                      self.core_src)
        self.assertIn("W = 3.0 * delta_z - delta_s", self.core_src)

    def test_numeric_surfaces_delegate_to_single_helper(self):
        calls = re.findall(r"overcontract_tier_split\(", self.core_src)
        # one definition + Surface 2 + Surface 3
        self.assertGreaterEqual(len(calls), 3)
        self.assertNotIn("min(raw, cap) - min(lower, cap)", self.core_src)
        self.assertNotIn("tier1_interval_start", self.s13c_src)

    def test_no_tariff_relevant_rounding_introduced(self):
        banned = re.compile(
            r"\b(?:math\.ceil|math\.floor|np\.round|numpy\.round|round|trunc|"
            r"astype\(\s*int)\b"
        )
        for label, source in (("core", self.core_src), ("13c", self.s13c_src)):
            tree = ast.parse(source)
            for node in ast.walk(tree):
                if not isinstance(node, ast.Call):
                    continue
                seg = ast.get_source_segment(source, node) or ""
                if not banned.search(seg):
                    continue
                lowered = seg.lower()
                if any(
                    token in lowered
                    for token in ("cc", "tier", "cap", "threshold", "overage", "demand")
                ):
                    self.fail(f"tariff-relevant rounding in {label}: {seg[:120]}")

    def test_no_model_was_constructed(self):
        self.assertIs(gurobipy.Model, _forbidden_model)


if __name__ == "__main__":
    unittest.main()
