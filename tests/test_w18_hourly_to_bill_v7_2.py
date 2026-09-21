"""Gate A non-solver regression and failure-injection tests; no output writes."""

import ast
import importlib.util
from pathlib import Path
import unittest

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "w18", ROOT / "scripts/06b_validate_hourly_to_bill_v7_2.py"
)
w18 = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(w18)


class W18Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.annual = pd.read_csv(w18.ANNUAL)
        cls.calendar = pd.read_csv(w18.CALENDAR)
        # Test fixture only: works both before and after the real correction.
        cls.calendar.loc[cls.calendar.date.eq("2025-02-01"), "tou_day_type"] = "offpeak_day"
        mask = cls.annual.timestamp.str.startswith("2025-02-01 ")
        cls.annual.loc[mask, "tou_day_type"] = "offpeak_day"
        cls.annual.loc[mask, "tou_period"] = "off"
        cls.billing = pd.read_csv(w18.BILLING)
        cls.bills = pd.read_csv(w18.BILLS)
        cls.tariff = pd.read_csv(w18.TARIFF)

    def test_pinned_colored_evidence(self):
        self.assertEqual(len(w18.evidence_identities()), 2)

    def test_full_calendar_and_additional_discrepancy_rejected(self):
        result = w18.calendar_audit(self.calendar)
        self.assertEqual(result.scope.eq("HARD").sum(), 304)
        self.assertEqual(result.special_non_sunday.sum(), 13)
        wrong = self.calendar.copy()
        wrong.loc[wrong.date.eq("2025-04-04"), "tou_day_type"] = "weekday"
        with self.assertRaisesRegex(ValueError, "Calendar discrepancy"):
            w18.calendar_audit(wrong)

    def test_historical_calendar_rejected(self):
        wrong = self.calendar.copy()
        wrong.loc[wrong.date.eq("2025-02-01"), "tou_day_type"] = "saturday"
        with self.assertRaisesRegex(ValueError, "Calendar discrepancy"):
            w18.calendar_audit(wrong)

    def test_structure(self):
        self.assertEqual(w18.structural_audit(self.annual, self.calendar, self.tariff)["status"], "PASS")

    def test_missing_duplicate_and_unordered_hours_rejected(self):
        for broken in (self.annual.iloc[1:], pd.concat([self.annual.iloc[:1], self.annual.iloc[:-1]]), self.annual.iloc[::-1]):
            with self.subTest(rows=len(broken)):
                with self.assertRaisesRegex(ValueError, "chronology"):
                    w18.structural_audit(broken, self.calendar, self.tariff)

    def test_wrong_tou_rejected(self):
        wrong = self.annual.copy()
        wrong.loc[0, "tou_period"] = "peak"
        with self.assertRaisesRegex(ValueError, "time-band"):
            w18.structural_audit(wrong, self.calendar, self.tariff)

    def test_summer_boundary_rejected(self):
        wrong = self.annual.copy()
        wrong.loc[wrong.timestamp.str.startswith("2025-05-15 "), "is_summer"] = True
        with self.assertRaisesRegex(ValueError, "Summer boundary"):
            w18.structural_audit(wrong, self.calendar, self.tariff)

    def test_non_summer_zero_rate_rejected(self):
        wrong = self.tariff.copy()
        mask = wrong.parameter_id.eq("energy_non_summer_peak")
        wrong.loc[mask, "applicable"] = True
        wrong.loc[mask, "value_numeric"] = 0.0
        with self.assertRaisesRegex(ValueError, "N/A"):
            w18.structural_audit(self.annual, self.calendar, wrong)

    def test_observed_boundary_and_alias_rejection(self):
        observed, proof = w18.observed_meter(self.annual)
        pd.testing.assert_series_equal(observed, self.annual.observed_load_kw-self.annual.observed_pv_kw)
        self.assertGreater(proof["observed_vs_planning_load_different_rows"], 0)
        wrong = self.annual.copy()
        wrong["observed_load_kw"] = wrong.baseline_load_kw
        with self.assertRaisesRegex(ValueError, "aliased"):
            w18.observed_meter(wrong)

    def test_project_empirical_tolerance_boundaries(self):
        self.assertTrue(w18.residual(100200, 100000, total=True)["criterion_pass"])
        self.assertFalse(w18.residual(100201, 100000, total=True)["criterion_pass"])
        self.assertTrue(w18.residual(101000, 100000)["criterion_pass"])
        self.assertFalse(w18.residual(101001, 100000)["criterion_pass"])
        self.assertTrue(w18.residual(1008000, 1000000)["criterion_pass"])
        self.assertFalse(w18.residual(1008001, 1000000)["criterion_pass"])
        self.assertTrue(w18.residual(48000, 40000)["criterion_pass"])
        self.assertFalse(w18.residual(48001, 40000)["criterion_pass"])
        self.assertFalse(w18.residual(51000, 50000)["criterion_pass"])
        self.assertTrue(w18.residual(8000, 0)["criterion_pass"])

    def test_current_data_counterfactual_scale_discrimination(self):
        new = w18.reconcile(self.annual, self.billing, self.bills)
        self.assertTrue(w18.hard_pass(new))
        old = self.annual.copy()
        feb1 = old.timestamp.str.startswith("2025-02-01 ")
        old.loc[feb1, "tou_day_type"] = "saturday"
        old.loc[feb1, "tou_period"] = [w18.expected_period(h, False, "saturday") for h in old.loc[feb1, "hour"]]
        historical = w18.reconcile(old, self.billing, self.bills)
        self.assertFalse(w18.hard_pass(historical))
        failures = historical.loc[historical.scope.eq("HARD") & ~historical.criterion_pass]
        self.assertEqual(set(zip(failures.usage_period_id, failures.tou_period)), {("2025-02", "sat_half"), ("2025-02", "off")})
        self.assertTrue(new.loc[new.scope.eq("INFORMATIONAL") & new.applicable, "status"].eq("INFORMATIONAL").all())

    def test_bill_title_is_not_grouping_key(self):
        expected = w18.reconcile(self.annual, self.billing, self.bills)
        altered = self.billing.copy()
        altered["bill_title_month"] = "deliberately_wrong_title"
        actual = w18.reconcile(self.annual, altered, self.bills)
        pd.testing.assert_frame_equal(expected.drop(columns="bill_title_month"), actual.drop(columns="bill_title_month"))

    def test_billing_boundary_and_overlap_rejected(self):
        altered = self.billing.copy()
        altered.loc[altered.usage_period_id.eq("2025-02"), "usage_period_start"] = "2025-01-31"
        with self.assertRaisesRegex(ValueError, "identity mismatch"):
            w18.reconcile(self.annual, altered, self.bills)

    def test_import_surface_has_no_solver_or_pipeline_import(self):
        tree = ast.parse(Path(w18.__file__).read_text(encoding="utf-8"))
        roots = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                roots.update(a.name.split(".")[0] for a in node.names)
            elif isinstance(node, ast.ImportFrom):
                roots.add(node.module.split(".")[0])
        self.assertTrue(roots <= {"__future__", "argparse", "datetime", "hashlib", "io", "json", "pathlib", "shutil", "subprocess", "sys", "numpy", "pandas"})


if __name__ == "__main__":
    unittest.main()
