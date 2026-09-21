"""No-solve tests for the Gate-6A corrected-EOB production driver."""

from __future__ import annotations

import contextlib
import datetime as dt
import hashlib
import importlib.util
import io
import json
import shutil
import subprocess
import sys
import types
import unittest
import uuid
from pathlib import Path
from typing import Any


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
DRIVER_PATH = REPOSITORY_ROOT / "scripts" / "15d_run_corrected_eob_v7_2.py"
TEST_TEMP_ROOT = REPOSITORY_ROOT / "_t6a"


def load_driver() -> Any:
    spec = importlib.util.spec_from_file_location("corrected_eob_driver_15d", DRIVER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot import driver from {DRIVER_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


driver = load_driver()


class FakeTable:
    def __init__(self, label: str) -> None:
        self.label = label

    def to_csv(self, path: Path, **_: Any) -> None:
        Path(path).write_text(f"label\n{self.label}\n", encoding="utf-8")

    def to_parquet(self, path: Path, **_: Any) -> None:
        Path(path).write_bytes(f"TEST_ONLY_PARQUET:{self.label}".encode("utf-8"))


class FakeSettings:
    last_kwargs: dict[str, Any] | None = None

    def __init__(self, **kwargs: Any) -> None:
        type(self).last_kwargs = dict(kwargs)
        for key, value in kwargs.items():
            setattr(self, key, value)


class CorrectedEobDriverTests(unittest.TestCase):
    def setUp(self) -> None:
        TEST_TEMP_ROOT.mkdir(parents=True, exist_ok=True)
        self.root = TEST_TEMP_ROOT / f"c_{uuid.uuid4().hex[:8]}"
        self.root.mkdir(exist_ok=False)
        self.hashes: dict[Path, str] = {}
        self.solve_calls: list[dict[str, Any]] = []
        self._build_authority_fixture()

    def tearDown(self) -> None:
        shutil.rmtree(self.root)
        try:
            TEST_TEMP_ROOT.rmdir()
        except OSError:
            pass

    def _write(self, relative: str | Path, content: str | bytes = b"fixture") -> Path:
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(content, bytes):
            path.write_bytes(content)
        else:
            path.write_text(content, encoding="utf-8")
        return path

    def _build_authority_fixture(self) -> None:
        execution_source = REPOSITORY_ROOT / driver.EXECUTION_CONTRACT_RELATIVE_PATH
        acceptance_source = REPOSITORY_ROOT / driver.ACCEPTANCE_CONTRACT_RELATIVE_PATH
        execution_path = self._write(
            driver.EXECUTION_CONTRACT_RELATIVE_PATH,
            execution_source.read_bytes(),
        )
        acceptance_path = self._write(
            driver.ACCEPTANCE_CONTRACT_RELATIVE_PATH,
            acceptance_source.read_bytes(),
        )
        self.hashes[execution_path.resolve()] = driver.EXECUTION_CONTRACT_SHA256
        self.hashes[acceptance_path.resolve()] = driver.ACCEPTANCE_CONTRACT_SHA256

        core_source = f'CORE_VERSION = "{driver.EXPECTED_CORE_VERSION}"\n'
        core_path = self._write(driver.CORE_RELATIVE_PATH, core_source)
        self.hashes[core_path.resolve()] = driver.EXPECTED_CORE_SHA256

        for pin in driver.DEPENDENCY_PINS:
            if pin.label == "economic_interface_14a":
                content: str | bytes = json.dumps(
                    {"billing_demand_proxy": {"kappa": driver.EXPECTED_KAPPA}}
                )
            else:
                content = f"fixture:{pin.label}\n"
            path = self._write(pin.path, content)
            self.hashes[path.resolve()] = pin.sha256

        self._write(driver.DRIVER_RELATIVE_PATH, DRIVER_PATH.read_bytes())

    def _hash_reader(self, path: Path) -> str:
        resolved = path.resolve()
        if resolved not in self.hashes:
            return hashlib.sha256(path.read_bytes()).hexdigest()
        return self.hashes[resolved]

    @staticmethod
    def _git_probe(_: Path) -> dict[str, Any]:
        return {
            "branch": driver.EXPECTED_BRANCH,
            "HEAD": "a" * 40,
            "working_tree_status": "TEST_ONLY_FIXTURE",
        }

    def _validate(self) -> dict[str, Any]:
        return driver.validate_authority(
            self.root,
            hash_reader=self._hash_reader,
            row_counter=lambda _: driver.EXPECTED_ANNUAL_ROWS,
            git_probe=self._git_probe,
        )

    @staticmethod
    def _fake_result() -> dict[str, Any]:
        return {
            "core_version": driver.EXPECTED_CORE_VERSION,
            "mode": "binary",
            "status": "OPTIMAL",
            "status_code": 2,
            "has_solution": True,
            "runtime_sec_gurobi": 1.25,
            "runtime_sec_wall": 1.30,
            "node_count": 4.0,
            "iteration_count": 12.0,
            "solution_count": 1,
            "mip_gap": 0.0,
            "objective_ntd2023_per_year": 123.0,
            "sizing": {
                "E_N_kwh": 10.0,
                "P_B_kw_ac": 2.0,
                "CC_regular_kw": 3.0,
            },
            "cost_components_ntd2023_per_year": {
                "energy": 10.0,
                "basic": 20.0,
                "overcontract_pure_season": 1.0,
                "overcontract_transition_resolved": 2.0,
                "degradation": 3.0,
                "annualized_capex": 80.0,
                "fom": 7.0,
            },
            "cost_reconciliation_residual_ntd": 0.0,
            "physical_diagnostics": {"max_ac_balance_residual_kw": 0.0},
            "transition_settlement": {"postsolve_invariants_pass": True},
            "dispatch": FakeTable("dispatch"),
            "billing_exact": FakeTable("billing"),
            "transition_settlement_detail": FakeTable("transition"),
        }

    def _execute_with_fakes(self) -> tuple[Path, dict[str, Any]]:
        authority = self._validate()
        pins = {pin.label: pin for pin in driver.DEPENDENCY_PINS}

        def load_inputs(_: Path, **__: Any) -> Any:
            return types.SimpleNamespace(
                kappa=driver.EXPECTED_KAPPA,
                source_paths={
                    "annual_input": str(self.root / pins["canonical_annual_input"].path),
                    "economic_interface_14a": str(self.root / pins["economic_interface_14a"].path),
                    "normalized_tariff_14a": str(self.root / pins["normalized_tariff_14a"].path),
                    "settlement_interface_14b": str(self.root / pins["settlement_interface_14b"].path),
                    "settlement_matrix_14b": str(self.root / pins["settlement_matrix_14b"].path),
                },
            )

        def fake_solve(inputs: Any, settings: Any, **kwargs: Any) -> dict[str, Any]:
            self.solve_calls.append(
                {"inputs": inputs, "settings": settings, "kwargs": kwargs}
            )
            settings.telemetry_callback(
                {
                    "event": "gurobi_optimize_finished",
                    "model_optimize": {
                        "status": "OPTIMAL",
                        "status_code": 2,
                        "solution_count": 1,
                        "node_count": 4.0,
                        "iteration_count": 12.0,
                        "best_bound": 123.0,
                        "mip_gap": 0.0,
                        "incumbent_objective": 123.0,
                    },
                }
            )
            return self._fake_result()

        runtime = driver.RuntimeBindings(
            core_version=driver.EXPECTED_CORE_VERSION,
            solve_settings_type=FakeSettings,
            load_inputs=load_inputs,
            solve_eob=fake_solve,
            solver_name="Gurobi-TEST-ONLY",
            solver_version="TEST-ONLY",
        )
        manifest_path = driver.execute_production(
            self.root,
            authority,
            runtime_loader=lambda: runtime,
            now_utc=dt.datetime(2026, 9, 17, 0, 0, 0, 123456, tzinfo=dt.timezone.utc),
        )
        return manifest_path, json.loads(manifest_path.read_text(encoding="utf-8"))

    @staticmethod
    def _runtime_import_subprocess() -> tuple[subprocess.CompletedProcess[str], dict[str, Any]]:
        completed = subprocess.run(
            [
                sys.executable,
                "-X",
                "utf8",
                "-B",
                str(DRIVER_PATH.relative_to(REPOSITORY_ROOT)),
                "--runtime-import-check",
            ],
            cwd=REPOSITORY_ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=120,
            check=False,
        )
        payload = json.loads(completed.stdout) if completed.returncode == 0 else {}
        return completed, payload

    def test_t01_valid_authority_validation_has_no_model_or_optimize_call(self) -> None:
        authority = self._validate()
        self.assertEqual(authority["validation_status"], "PASS")
        self.assertEqual(authority["validation_mode"], "NO_MODEL_IMPORT_NO_SOLVE")
        self.assertEqual(self.solve_calls, [])

    def test_t02_wrong_core_version_refused_before_solve(self) -> None:
        self._write(driver.CORE_RELATIVE_PATH, 'CORE_VERSION = "r9-is-not-authorized"\n')
        with self.assertRaisesRegex(driver.ProvenanceError, "CORE_VERSION mismatch"):
            self._validate()
        self.assertEqual(self.solve_calls, [])

    def test_t03_wrong_core_sha_refused_before_solve(self) -> None:
        core = (self.root / driver.CORE_RELATIVE_PATH).resolve()
        self.hashes[core] = "0" * 64
        with self.assertRaisesRegex(driver.ProvenanceError, "Core SHA-256 mismatch"):
            self._validate()
        self.assertEqual(self.solve_calls, [])

    def test_t04_wrong_canonical_input_sha_refused_before_solve(self) -> None:
        pin = next(p for p in driver.DEPENDENCY_PINS if p.label == "canonical_annual_input")
        self.hashes[(self.root / pin.path).resolve()] = "1" * 64
        with self.assertRaisesRegex(driver.ProvenanceError, "canonical_annual_input"):
            self._validate()
        self.assertEqual(self.solve_calls, [])

    def test_t05_wrong_settlement_interface_sha_refused_before_solve(self) -> None:
        pin = next(p for p in driver.DEPENDENCY_PINS if p.label == "settlement_interface_14b")
        self.hashes[(self.root / pin.path).resolve()] = "2" * 64
        with self.assertRaisesRegex(driver.ProvenanceError, "settlement_interface_14b"):
            self._validate()
        self.assertEqual(self.solve_calls, [])

    def test_t06_historical_output_path_is_rejected(self) -> None:
        historical = self.root / driver.HISTORICAL_OUTPUT_RELATIVE_PATH
        with self.assertRaisesRegex(driver.ProvenanceError, "Historical output namespace"):
            driver.validate_output_root(self.root, historical)

    def test_t07_existing_nonempty_run_directory_is_not_overwritten(self) -> None:
        output_root = self.root / driver.CORRECTED_OUTPUT_ROOT_RELATIVE_PATH
        run_id = "20260917T000000123456Z_0123456789"
        existing = output_root / run_id
        existing.mkdir(parents=True)
        (existing / "evidence.txt").write_text("preserve", encoding="utf-8")
        with self.assertRaisesRegex(driver.ProvenanceError, "Refusing to overwrite non-empty"):
            driver.allocate_run_directory(output_root, run_id)
        self.assertEqual((existing / "evidence.txt").read_text(encoding="utf-8"), "preserve")

    def test_t08_future_call_is_exactly_once_and_unconstrained(self) -> None:
        self._execute_with_fakes()
        self.assertEqual(len(self.solve_calls), 1)
        self.assertEqual(self.solve_calls[0]["kwargs"], {"layer_a_requirements": None})

    def test_t09_future_call_uses_frozen_solver_settings_without_node_limit(self) -> None:
        self._execute_with_fakes()
        self.assertIsNotNone(FakeSettings.last_kwargs)
        settings = FakeSettings.last_kwargs or {}
        self.assertEqual(settings["mode"], "binary")
        self.assertEqual(settings["mip_gap"], 1e-6)
        self.assertIsNone(settings["time_limit_sec"])
        self.assertEqual(settings["output_flag"], 1)
        self.assertEqual(settings["numeric_focus"], 1)
        self.assertNotIn("node_limit", settings)
        for forbidden in ("cuts", "heuristics", "mip_focus", "method", "presolve"):
            self.assertNotIn(forbidden, settings)
        self.assertFalse(driver.PRODUCTION_SOLVER_POLICY["NodeLimit"]["driver_sets_parameter"])

    def test_t10_fake_manifest_has_pending_audit_authority(self) -> None:
        _, manifest = self._execute_with_fakes()
        self.assertEqual(manifest["result_authority"], driver.CANDIDATE_AUTHORITY)
        self.assertEqual(
            manifest["acceptance_status"],
            "NOT_AUDITED_DRIVER_DOES_NOT_ACCEPT_ITS_OWN_RESULT",
        )

    def test_t11_validation_does_not_mutate_historical_15b_or_15c(self) -> None:
        protected = [
            REPOSITORY_ROOT / "scripts/15b_freeze_production_eob_baseline.py",
            REPOSITORY_ROOT / "scripts/15c_validate_production_eob_rainflow.py",
        ]
        before = {path: hashlib.sha256(path.read_bytes()).hexdigest() for path in protected}
        self._validate()
        after = {path: hashlib.sha256(path.read_bytes()).hexdigest() for path in protected}
        self.assertEqual(after, before)

    def test_t12_validate_only_never_calls_executor(self) -> None:
        calls = {"validated": 0, "executed": 0}

        def validator(_: Path) -> dict[str, Any]:
            calls["validated"] += 1
            return self._validate()

        def forbidden_executor(_: Path, __: Any) -> Path:
            calls["executed"] += 1
            raise AssertionError("validate-only called the production executor")

        with contextlib.redirect_stdout(io.StringIO()):
            code = driver.run(
                root=self.root,
                validate_only=True,
                validator=validator,
                executor=forbidden_executor,
            )
        self.assertEqual(code, 0)
        self.assertEqual(calls, {"validated": 1, "executed": 0})

    def test_t13_actual_subprocess_runtime_import(self) -> None:
        completed, payload = self._runtime_import_subprocess()
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual(payload["runtime_import_status"], "PASS")
        self.assertEqual(payload["core"]["module"], "src.annual_design_model_v7_2")
        self.assertEqual(payload["core"]["CORE_VERSION"], driver.EXPECTED_CORE_VERSION)
        self.assertTrue(all(payload["runtime_bindings"].values()))
        self.assertEqual(
            payload["execution_guard"],
            {
                "model_construction_attempts": 0,
                "optimization_attempts": 0,
                "solve_eob_calls": 0,
            },
        )

    def test_t14_runtime_import_check_performs_zero_solve_calls(self) -> None:
        calls = {"solve": 0, "execute": 0}

        def forbidden_solve(*_: Any, **__: Any) -> dict[str, Any]:
            calls["solve"] += 1
            raise AssertionError("runtime-import-check called solve_eob")

        runtime = driver.RuntimeBindings(
            core_version=driver.EXPECTED_CORE_VERSION,
            solve_settings_type=FakeSettings,
            load_inputs=lambda *_args, **_kwargs: object(),
            solve_eob=forbidden_solve,
            solver_name="Gurobi-TEST-ONLY",
            solver_version="TEST-ONLY",
        )

        def forbidden_executor(_: Path, __: Any) -> Path:
            calls["execute"] += 1
            raise AssertionError("runtime-import-check called the production executor")

        stream = io.StringIO()
        with contextlib.redirect_stdout(stream):
            code = driver.run(
                root=self.root,
                validate_only=False,
                runtime_import_check=True,
                validator=lambda _: self._validate(),
                executor=forbidden_executor,
                runtime_loader=lambda: runtime,
            )
        payload = json.loads(stream.getvalue())
        self.assertEqual(code, 0)
        self.assertEqual(calls, {"solve": 0, "execute": 0})
        self.assertEqual(payload["execution_guard"]["solve_eob_calls"], 0)
        self.assertEqual(payload["execution_guard"]["model_construction_attempts"], 0)
        self.assertEqual(payload["execution_guard"]["optimization_attempts"], 0)

    def test_t15_runtime_import_check_allocates_no_production_run_directory(self) -> None:
        output_root = REPOSITORY_ROOT / driver.CORRECTED_OUTPUT_ROOT_RELATIVE_PATH
        before = sorted(path.name for path in output_root.iterdir())
        completed, payload = self._runtime_import_subprocess()
        after = sorted(path.name for path in output_root.iterdir())
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual(after, before)
        self.assertTrue(payload["production_output_registry"]["unchanged"])
        self.assertEqual(payload["production_output_registry"]["run_directories_allocated"], 0)

    def test_t16_runtime_import_repair_preserves_hard_pins(self) -> None:
        self.assertEqual(
            driver.EXPECTED_CORE_VERSION,
            "v7.2-annual-design-core-transition-candidate1-exact-d-preflight-2026-09-16-r10",
        )
        self.assertEqual(
            driver.EXPECTED_CORE_SHA256,
            "9d828321814b09141497056d1bb17da8b2839c5eb151fce8530059fb7e193da8",
        )
        self.assertEqual(
            hashlib.sha256((REPOSITORY_ROOT / driver.CORE_RELATIVE_PATH).read_bytes()).hexdigest(),
            driver.EXPECTED_CORE_SHA256,
        )
        self.assertEqual(driver.EXECUTION_CONTRACT_SHA256, "94c251a93356870c978acb97c25ee64680b1f40eee0680ef121483d9aa51e601")
        self.assertEqual(driver.ACCEPTANCE_CONTRACT_SHA256, "dca4c62dfde4db3747582d152a6ca05fe3cfcd0d7a19f51fa115a8d870bc776e")
        self.assertEqual(driver.PRODUCTION_SOLVER_POLICY["layer_a_requirements"], None)
        self.assertFalse(driver.PRODUCTION_SOLVER_POLICY["automatic_retry_with_changed_parameters"])

    def test_t17_failed_gate7_run_directory_is_never_reused(self) -> None:
        failed_id = "20260917T074854498781Z_967301557c"
        output_root = REPOSITORY_ROOT / driver.CORRECTED_OUTPUT_ROOT_RELATIVE_PATH
        failed = output_root / failed_id
        self.assertTrue(failed.is_dir())
        self.assertEqual(list(failed.iterdir()), [])
        with self.assertRaisesRegex(driver.ProvenanceError, "Refusing to overwrite existing"):
            driver.validate_run_directory(output_root, failed_id)
        self.assertTrue(failed.is_dir())
        self.assertEqual(list(failed.iterdir()), [])


if __name__ == "__main__":
    unittest.main()
