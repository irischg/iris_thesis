"""No-solve positive and fail-closed tests for the Step 2E-1 v7.3 route."""

from __future__ import annotations

import ast
import importlib.util
import json
import subprocess
import sys
import unittest
from dataclasses import replace
from pathlib import Path
from unittest.mock import patch

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src import production_input_authority_v7_3 as authority  # noqa: E402


SCRIPT = ROOT / "scripts/21a_preflight_v7_3_production_routing.py"


def load_script():
    spec = importlib.util.spec_from_file_location("step2e1_preflight_tests", SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError("Could not load Step 2E-1 preflight.")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class ProductionInputAuthorityV73Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.accepted = authority.load_accepted_v7_3_annual_input(ROOT)

    def test_positive_accepted_r3_identity(self) -> None:
        self.assertEqual(
            self.accepted.identity.path,
            authority.ACCEPTED_ANNUAL_RELATIVE_PATH.as_posix(),
        )
        self.assertEqual(
            self.accepted.identity.sha256, authority.ACCEPTED_ANNUAL_SHA256
        )
        self.assertEqual(
            self.accepted.identity.artifact_role, authority.ACCEPTED_ARTIFACT_ROLE
        )
        self.assertEqual(self.accepted.identity.row_count, 8760)
        self.assertEqual(
            set(self.accepted.authority_hashes),
            {"methodology", "evidence", "lifecycle"},
        )

    def test_historical_v7_1_and_old_canonical_sha_are_rejected(self) -> None:
        with self.assertRaisesRegex(
            authority.ProductionInputAuthorityError, "Historical annual_input_v7_1"
        ):
            authority.load_accepted_v7_3_annual_input(
                ROOT,
                parquet_path=ROOT / "data/processed/annual_input_v7_1.parquet",
            )
        with self.assertRaisesRegex(
            authority.ProductionInputAuthorityError, "not the accepted v7.3 identity"
        ):
            authority.load_accepted_v7_3_annual_input(
                ROOT,
                claimed_sha256=authority.HISTORICAL_ANNUAL_SHA256,
            )

    def test_winter_sensitivity_artifact_is_rejected(self) -> None:
        with self.assertRaisesRegex(
            authority.ProductionInputAuthorityError,
            "winter_pv_sensitivity_only",
        ):
            authority.load_accepted_v7_3_annual_input(
                ROOT,
                parquet_path=ROOT / authority.WINTER_SENSITIVITY_RELATIVE_PATH,
            )

    def test_artifact_role_missing_wrong_or_sensitivity_fails_closed(self) -> None:
        missing = self.accepted.dataframe.drop(columns=["artifact_role"])
        with self.assertRaisesRegex(
            authority.ProductionInputAuthorityError, "missing required columns"
        ):
            authority.validate_accepted_annual_dataframe(missing)

        for role in ("wrong_role", authority.WINTER_SENSITIVITY_ROLE):
            changed = self.accepted.dataframe.copy(deep=True)
            changed["artifact_role"] = role
            with self.subTest(role=role):
                with self.assertRaisesRegex(
                    authority.ProductionInputAuthorityError,
                    "artifact_role must be reconstructed_pv_mainline",
                ):
                    authority.validate_accepted_annual_dataframe(changed)

    def test_wrong_parquet_sha_fails_closed(self) -> None:
        native_sha256 = authority.sha256_file
        accepted_path = authority.accepted_annual_path(ROOT)

        def substituted(path: Path) -> str:
            if path.resolve() == accepted_path:
                return "0" * 64
            return native_sha256(path)

        with patch.object(authority, "sha256_file", side_effect=substituted):
            with self.assertRaisesRegex(
                authority.ProductionInputAuthorityError, "parquet SHA256 mismatch"
            ):
                authority.load_accepted_v7_3_annual_input(ROOT)

    def test_row_count_and_timeline_fail_closed(self) -> None:
        short = self.accepted.dataframe.iloc[:-1].copy()
        with self.assertRaisesRegex(
            authority.ProductionInputAuthorityError, "rows=8759"
        ):
            authority.validate_accepted_annual_dataframe(short)

        shifted = self.accepted.dataframe.copy(deep=True)
        shifted.loc[100, "timestamp"] = shifted.loc[99, "timestamp"]
        with self.assertRaisesRegex(
            authority.ProductionInputAuthorityError, "exact ordered formal"
        ):
            authority.validate_accepted_annual_dataframe(shifted)

    def test_integration_status_must_be_passed_only(self) -> None:
        changed = self.accepted.dataframe.copy(deep=True)
        changed.loc[0, "integration_status"] = "failed"
        with self.assertRaisesRegex(
            authority.ProductionInputAuthorityError,
            "integration_status must be passed",
        ):
            authority.validate_accepted_annual_dataframe(changed)

    def test_load_and_pv_must_be_finite_and_nonnegative(self) -> None:
        cases = (
            ("baseline_load_kw", np.inf),
            ("baseline_load_kw", -1.0),
            ("pv_available_kw", np.nan),
            ("pv_available_kw", -1.0),
        )
        for column, value in cases:
            changed = self.accepted.dataframe.copy(deep=True)
            changed.loc[0, column] = value
            with self.subTest(column=column, value=value):
                with self.assertRaisesRegex(
                    authority.ProductionInputAuthorityError,
                    "finite and non-negative",
                ):
                    authority.validate_accepted_annual_dataframe(changed)

    def test_parquet_read_failure_never_uses_csv_fallback(self) -> None:
        with patch.object(
            authority.pd,
            "read_parquet",
            side_effect=ImportError("test parquet engine failure"),
        ), patch.object(authority.pd, "read_csv") as read_csv:
            with self.assertRaisesRegex(
                authority.ProductionInputAuthorityError, "CSV fallback is forbidden"
            ):
                authority.load_accepted_v7_3_annual_input(ROOT)
            read_csv.assert_not_called()


class RoutingPreflightV73Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.script = load_script()
        cls.accepted = authority.load_accepted_v7_3_annual_input(ROOT)
        cls.payload = cls.script.run_preflight(ROOT)

    def test_positive_full_preflight_is_zero_solve(self) -> None:
        self.assertEqual(self.payload["status"], "PASS")
        self.assertEqual(
            self.payload["verdict"], "STEP 2E-1 ROUTING PREFLIGHT PASS"
        )
        counters = self.payload["execution_counters"]
        self.assertEqual(counters["model_constructions"], 0)
        self.assertEqual(counters["optimization_calls"], 0)
        self.assertEqual(counters["economic_evaluations"], 0)
        self.assertEqual(counters["forbidden_attempts"], [])

    def test_core_loader_used_exact_parquet_and_impossible_csv(self) -> None:
        audit = self.payload["unchanged_core_loader_integration"]
        self.assertEqual(audit["status"], "PASS")
        self.assertFalse(audit["csv_argument_exists"])
        self.assertFalse(audit["csv_fallback_occurred"])
        self.assertFalse(audit["legacy_default_used"])
        self.assertEqual(
            audit["core_dataframe_fingerprint"]["fingerprint_sha256"],
            self.accepted.identity.fingerprint_sha256,
        )

    def test_complete_81_case_surface_and_monotonicity(self) -> None:
        audit = self.payload["analytical_surface_audit"]
        self.assertEqual(audit["status"], "PASS")
        self.assertEqual(audit["case_count"], 81)
        self.assertEqual(len(audit["cases"]), 81)
        self.assertEqual(audit["power_monotonicity"], "PASS")
        self.assertEqual(audit["reserve_monotonicity_over_beta"], "PASS")
        self.assertEqual(audit["reserve_monotonicity_over_alpha"], "PASS")

    def test_valid_start_counts_and_non_circular_semantics(self) -> None:
        audit = self.payload["valid_start_identity_audit"]
        self.assertEqual(audit["status"], "PASS")
        self.assertFalse(audit["pv_values_used_in_start_set"])
        counts = {row["beta_h"]: row["valid_start_count"] for row in audit["rows"]}
        self.assertEqual(counts, {beta: 8760 - beta + 1 for beta in range(4, 13)})
        self.assertTrue(all(row["no_circular_wrap"] for row in audit["rows"]))

    def test_analytical_replay_uses_same_artifact_and_no_surplus_recharge(self) -> None:
        replay = self.payload["analytical_replay_audit"]
        self.assertEqual(replay["status"], "PASS")
        self.assertEqual(replay["case_count"], 81)
        self.assertFalse(replay["surplus_pv_recharge"])
        self.assertEqual(
            replay["annual_identity"], self.accepted.identity.as_dict()
        )

    def test_eob_and_layer_a_identity_difference_fails_closed(self) -> None:
        routing = self.script.build_routing_map(self.accepted.identity)
        routing["prospective_layer_a_annual_economics"] = dict(
            routing["prospective_layer_a_annual_economics"]
        )
        routing["prospective_layer_a_annual_economics"]["sha256"] = "f" * 64
        with self.assertRaisesRegex(
            self.script.RoutingPreflightError, "Same-artifact routing failure"
        ):
            self.script.validate_routing_map(routing, self.accepted.identity)

    def test_analytical_replay_different_artifact_fails_closed(self) -> None:
        different = replace(self.accepted.identity, sha256="f" * 64)
        with self.assertRaisesRegex(
            authority.ProductionInputAuthorityError,
            "received a different annual artifact identity",
        ):
            authority.require_same_annual_identity(
                self.accepted.identity,
                different,
                consumer="layer_a_analytical_replay",
            )

    def test_every_solver_entry_point_is_runtime_blocked(self) -> None:
        import gurobipy as gp

        with self.script.ZeroSolveGuard() as guard:
            guarded = ("__init__", "optimize", "optimizeAsync", "optimizeBatch", "tune")
            for name in guarded:
                with self.subTest(name=name):
                    with self.assertRaisesRegex(
                        self.script.RoutingPreflightError, "ZERO-SOLVE guard blocked"
                    ):
                        getattr(gp.Model, name)(object())
        self.assertEqual(guard.model_constructions, 1)
        self.assertEqual(guard.optimization_calls, 4)

    def test_source_has_no_model_build_solve_or_optimization_call_site(self) -> None:
        tree = ast.parse(SCRIPT.read_text(encoding="utf-8"))
        forbidden = {
            "solve_eob",
            "build_eob_model",
            "optimize",
            "optimizeAsync",
            "optimizeBatch",
            "tune",
        }
        calls = [
            node
            for node in ast.walk(tree)
            if isinstance(node, ast.Call)
            and (
                (isinstance(node.func, ast.Name) and node.func.id in forbidden)
                or (isinstance(node.func, ast.Attribute) and node.func.attr in forbidden)
            )
        ]
        self.assertEqual(calls, [])

    def test_cli_returns_machine_readable_pass_without_output_files(self) -> None:
        before = subprocess.run(
            ["git", "status", "--porcelain=v1", "--untracked-files=all"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        ).stdout
        completed = subprocess.run(
            [sys.executable, "-B", str(SCRIPT), "--compact"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        payload = json.loads(completed.stdout)
        after = subprocess.run(
            ["git", "status", "--porcelain=v1", "--untracked-files=all"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        ).stdout
        self.assertEqual(payload["status"], "PASS")
        self.assertEqual(payload["execution_counters"]["optimization_calls"], 0)
        self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main()
