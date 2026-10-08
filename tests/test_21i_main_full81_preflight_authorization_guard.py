#!/usr/bin/env python3
"""N-04: the Main Full81 NO-SOLVE preflight entrypoint must fail closed.

Finding N-04 (MAJOR) was that
``scripts/21d_preflight_v7_3_final81_successor.py`` *resolved and reported* the
Main Full81 scope authorization but never *required* it.  A safe negative
control showed ``verify_v7_4_authority_bundle(..., authorization=None)``
returning ``PASS`` while reporting Full81 as ``NOT_AUTHORIZED``, so the
zero-solve runner was fail-open with respect to its own prerequisite.

These tests are deliberately **integration** tests of the entrypoint, not unit
tests of the guard.  Testing ``require_full81_scope_authorization`` in isolation
is exactly the coverage hole N-04 names: that guard already behaved correctly;
what was missing was any mechanical path from ``21d.main()`` through it.  Every
test here therefore drives the real ``main()`` and asserts on the real emitted
payload.

ZERO SOLVE.  No production model is constructed, no ``optimize()`` is reachable,
no production result is written, and no Full81 case is executed.  Three
independent controls enforce that:

1. :func:`setUpModule` replaces every real Gurobi entry point for the whole
   module, so a regression that reintroduces a live production path raises
   instead of solving;
2. ``run_layer_a_production`` — the only model-constructing callee of the runner
   — is replaced by a tripwire on every no-solve test, so the execute path
   cannot be entered silently;
3. ``run_successor_stack`` is replaced by a counting double, so the real
   preflight plan is never built against the live repository.
"""

from __future__ import annotations

import ast
import contextlib
import importlib.util
import io
import json
import sys
import unittest
from pathlib import Path
from typing import Any, Mapping
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.main_full81_authorization_v7_4 import (  # noqa: E402
    _AUTHORIZED_INVARIANTS,
    AUTHORIZED_FOR_NO_SOLVE_PREFLIGHT,
    EXPECTED_RUNNER_RELATIVE_PATH,
    NOT_GRANTED,
    PRESENT_INVALID,
    absent_authorization,
    require_full81_execution_authorization,
    Full81AuthorizationError,
)
from src.production_authority_bundle_v7_4 import (  # noqa: E402
    Full81AuthorizationNotGranted,
    require_a2_hard_block,
    verify_v7_4_authority_bundle,
)
from src.production_authority_lifecycle_u06 import (  # noqa: E402
    implementation_identity_digest,
    resolve_u06_lifecycle,
)


RUNNER_RELATIVE_PATH = "scripts/21d_preflight_v7_3_final81_successor.py"
RUNNER_PATH = ROOT / RUNNER_RELATIVE_PATH

#: N-05.  The sibling no-solve entrypoints that share ``run_successor_stack``.
#: The Layer-A one is the subject of N-05; the EOB one is included so that
#: "21d is the SOLE Full81 entrypoint" is proved against every sibling rather
#: than asserted about the one that happened to be found.
LAYER_A_RELATIVE_PATH = "scripts/21c_preflight_v7_3_layer_a_successor.py"
LAYER_A_PATH = ROOT / LAYER_A_RELATIVE_PATH
EOB_RELATIVE_PATH = "scripts/21b_preflight_v7_3_eob_successor.py"
EOB_PATH = ROOT / EOB_RELATIVE_PATH

#: The status the Layer-A entrypoint must refuse the Main Full81 scope with.
FULL81_ENTRYPOINT_REFUSAL_STATUS = "FULL81_REQUIRES_21D_ENTRYPOINT"

#: The canonical guard the entrypoint must pass through.  Named once, here, so a
#: rename that silently drops the guard fails these tests rather than passing
#: them against a differently named local reimplementation.
CANONICAL_GUARD_NAME = "require_full81_scope_authorization"

_TRIPWIRE_PATCHES: list[Any] = []


class NativeSolverTripwire(RuntimeError):
    """Raised if any test in this module reaches a real native solver entry."""


class ProductionExecutionTripwire(RuntimeError):
    """Raised if a no-solve test reaches the model-constructing execute path."""


def setUpModule() -> None:
    """Make real native solver entry structurally impossible for this module."""

    def _forbidden(name):
        def _raise(*args, **kwargs):
            raise NativeSolverTripwire(
                f"Test suite reached real native solver entry point: {name}"
            )

        return _raise

    try:
        import gurobipy as gp
    except Exception:  # pragma: no cover - gurobipy absent is already safe
        return

    for target, attribute in (
        (gp.Model, "__init__"),
        (gp.Model, "optimize"),
        (gp.Model, "optimizeAsync"),
        (gp.Model, "optimizeBatch"),
        (gp.Model, "tune"),
    ):
        if not hasattr(target, attribute):
            continue
        patcher = patch.object(
            target, attribute, _forbidden(f"gurobipy.Model.{attribute}")
        )
        patcher.start()
        _TRIPWIRE_PATCHES.append(patcher)


def tearDownModule() -> None:
    while _TRIPWIRE_PATCHES:
        _TRIPWIRE_PATCHES.pop().stop()


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


class _FakeStack(dict):
    """Stand-in for the real preflight plan.

    Any key the runner reads resolves to an inert placeholder, so this double
    stays correct when the emitted payload gains provenance keys.  The point of
    these tests is the authorization gate, not the payload shape, and a complete
    stand-in is what lets T1 reach the PASS path without the live repository.
    """

    def __missing__(self, key: str) -> str:
        return f"<fake:{key}>"


def granted_authorization() -> dict[str, Any]:
    """A resolved authorization that lawfully grants the no-solve preflight.

    Built from the live invariant table and the live implementation digest
    rather than from copied literals, so a lawful successor rename of the
    lineage / candidate identity cannot turn this fixture into a false PASS or a
    false failure.
    """

    authorization = dict(_AUTHORIZED_INVARIANTS)
    authorization["implementation_identity_digest"] = implementation_identity_digest(
        ROOT
    )
    return authorization


def frozen_lifecycle() -> dict[str, Any]:
    """A lifecycle mapping that reports production authority as FROZEN."""

    return {
        "accepted_lifecycle_overlay": "PRESENT_VALID",
        "production_authority_freeze_status": "FROZEN",
        "implementation_identity_digest": implementation_identity_digest(ROOT),
    }


class RunnerHarness:
    """Drives the real ``21d.main()`` with every production callee isolated."""

    def __init__(
        self,
        *,
        authorization: Mapping[str, Any] | None,
        lifecycle: Mapping[str, Any] | None = None,
        stack_is_tripwire: bool = False,
    ) -> None:
        self.authorization = authorization
        self.lifecycle = lifecycle if lifecycle is not None else frozen_lifecycle()
        self.stack_is_tripwire = stack_is_tripwire
        self.stack_calls = 0
        self.case_selection_calls = 0
        self.layer_a_calls = 0
        self.module = self._load_runner()
        self._patchers: list[Any] = []

    @staticmethod
    def _load_runner():
        """Import the runner by path; its filename is not a valid identifier."""

        spec = importlib.util.spec_from_file_location(
            "iris_thesis_21d_runner_under_test", RUNNER_PATH
        )
        module = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(module)
        return module

    # -- doubles ----------------------------------------------------------
    def _fake_resolve_lifecycle(self, *args, **kwargs):
        return self.lifecycle

    def _fake_resolve_authorization(self, *args, **kwargs):
        return self.authorization

    def _fake_run_successor_stack(self, *args, **kwargs):
        self.stack_calls += 1
        if self.stack_is_tripwire:
            raise AssertionError(
                "The preflight plan was built although Main Full81 was NOT "
                "AUTHORIZED. The authorization guard must precede planning."
            )
        return _FakeStack()

    def _fake_select_production_cases(self, *args, **kwargs):
        self.case_selection_calls += 1
        return ["a1.00_b12"]

    def _fake_run_layer_a_production(self, *args, **kwargs):
        self.layer_a_calls += 1
        raise ProductionExecutionTripwire(
            "A no-solve test reached run_layer_a_production, the only "
            "model-constructing callee of the runner."
        )

    def __enter__(self) -> "RunnerHarness":
        doubles = {
            "resolve_u06_lifecycle": self._fake_resolve_lifecycle,
            "resolve_full81_authorization": self._fake_resolve_authorization,
            "run_successor_stack": self._fake_run_successor_stack,
            "select_production_cases": self._fake_select_production_cases,
            "run_layer_a_production": self._fake_run_layer_a_production,
        }
        for name, double in doubles.items():
            if not hasattr(self.module, name):
                raise AssertionError(
                    f"The runner does not expose {name!r}. The N-04 guard must "
                    "be wired into the runner's own module namespace so it can "
                    "be proved; see test_t7_guard_is_wired_into_the_entrypoint."
                )
            patcher = patch.object(self.module, name, double)
            patcher.start()
            self._patchers.append(patcher)
        return self

    def __exit__(self, *exc_info) -> None:
        while self._patchers:
            self._patchers.pop().stop()

    # -- invocation -------------------------------------------------------
    def run(self, argv: list[str] | None = None) -> tuple[int, dict[str, Any]]:
        """Call the real ``main()`` and return ``(exit_code, payload)``."""

        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            code = self.module.main(list(argv or []) + ["--compact"])
        return code, json.loads(buffer.getvalue())


class LayerAHarness:
    """Drives the real ``21c.main()`` with every production callee isolated.

    N-05 counterpart of :class:`RunnerHarness`.  The Layer-A entrypoint resolves
    no lifecycle and no authorization -- that absence is the whole point of the
    N-05 remediation -- so this harness doubles only the three callees that
    could build a plan or a model.
    """

    def __init__(self, *, stack_is_tripwire: bool = False) -> None:
        self.stack_is_tripwire = stack_is_tripwire
        self.stack_calls = 0
        self.case_selection_calls = 0
        self.layer_a_calls = 0
        self.module = self._load()
        self._patchers: list[Any] = []

    @staticmethod
    def _load():
        spec = importlib.util.spec_from_file_location(
            "iris_thesis_21c_layer_a_under_test", LAYER_A_PATH
        )
        module = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(module)
        return module

    def _fake_run_successor_stack(self, *args, **kwargs):
        self.stack_calls += 1
        if self.stack_is_tripwire:
            raise AssertionError(
                "The Layer-A preflight plan was built for a scope this "
                "entrypoint may not route. The scope refusal must precede "
                "planning."
            )
        return _FakeStack()

    def _fake_select_production_cases(self, *args, **kwargs):
        self.case_selection_calls += 1
        return ["a1.00_b12"]

    def _fake_run_layer_a_production(self, *args, **kwargs):
        self.layer_a_calls += 1
        raise ProductionExecutionTripwire(
            "A no-solve test reached run_layer_a_production, the only "
            "model-constructing callee of the Layer-A entrypoint."
        )

    def __enter__(self) -> "LayerAHarness":
        doubles = {
            "run_successor_stack": self._fake_run_successor_stack,
            "select_production_cases": self._fake_select_production_cases,
            "run_layer_a_production": self._fake_run_layer_a_production,
        }
        for name, double in doubles.items():
            if not hasattr(self.module, name):
                raise AssertionError(
                    f"The Layer-A entrypoint does not expose {name!r}."
                )
            patcher = patch.object(self.module, name, double)
            patcher.start()
            self._patchers.append(patcher)
        return self

    def __exit__(self, *exc_info) -> None:
        while self._patchers:
            self._patchers.pop().stop()

    def run(self, argv: list[str] | None = None) -> tuple[int, dict[str, Any]]:
        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            code = self.module.main(list(argv or []) + ["--compact"])
        return code, json.loads(buffer.getvalue())


class _GuardIntegrationTestCase(unittest.TestCase):
    """Shared assertions every no-solve outcome must satisfy."""

    def assertFailedClosed(
        self, code: int, payload: Mapping[str, Any], harness: RunnerHarness
    ) -> None:
        """The entrypoint refused, before planning and before any solve."""

        self.assertNotEqual(code, 0, f"Entrypoint returned success: {payload}")
        self.assertNotEqual(payload.get("status"), "PASS")
        self.assertNotIn("PASS", str(payload.get("verdict", "")))
        self.assertNotIn("selected_case_plan", payload)
        self.assertFalse(payload.get("production_execution_attempted", False))
        # The guard must precede the preflight plan, not follow it.
        self.assertEqual(
            harness.stack_calls,
            0,
            "The preflight plan was built although Full81 was NOT AUTHORIZED.",
        )
        self.assertEqual(harness.case_selection_calls, 0)
        self.assertEqual(harness.layer_a_calls, 0)


# ---------------------------------------------------------------------------
# T1 - a lawful authorization permits exactly the no-solve preflight
# ---------------------------------------------------------------------------


class T1ValidAuthorizationTests(_GuardIntegrationTestCase):
    def test_t1_valid_authorization_reaches_the_no_solve_preflight(self) -> None:
        with RunnerHarness(authorization=granted_authorization()) as harness:
            code, payload = harness.run()

        self.assertEqual(code, 0, payload)
        self.assertEqual(payload["status"], "PASS")
        self.assertIn("ZERO-SOLVE PREFLIGHT PASS", payload["verdict"])
        # Progression to the preflight planning path, and no further.
        self.assertEqual(harness.stack_calls, 1)
        self.assertEqual(harness.case_selection_calls, 1)
        # No model, no optimize, no execution: the execute path was never taken.
        self.assertEqual(harness.layer_a_calls, 0)

    def test_t1_default_scope_is_full81_and_is_guarded(self) -> None:
        """The guarded scope is the one the runner actually plans."""

        with RunnerHarness(authorization=granted_authorization()) as harness:
            code, payload = harness.run()

        self.assertEqual(code, 0, payload)
        self.assertEqual(payload["case_set"], "full81")


class SharedRouteSafetyTests(unittest.TestCase):
    """The guard must close Full81 without blocking non-Full81 routes.

    ``require_full81_scope_authorization`` is scope-aware: a scope that is not
    ``full81`` is not its business and returns immediately.  That is what keeps
    this remediation confined to the Main Full81 entrypoint instead of silently
    revoking the EOB and Layer-A preflights, which share ``run_successor_stack``
    but never select the Full81 scope.
    """

    def test_non_full81_case_sets_are_unaffected(self) -> None:
        for case_set in ("low", "central", "high", "core-three", "historical-five"):
            with self.subTest(case_set=case_set):
                with RunnerHarness(authorization=absent_authorization()) as harness:
                    code, payload = harness.run(["--case-set", case_set])

                self.assertEqual(code, 0, payload)
                self.assertEqual(payload["status"], "PASS")
                self.assertEqual(payload["case_set"], case_set)
                self.assertEqual(harness.stack_calls, 1)
                self.assertEqual(harness.layer_a_calls, 0)

    def test_full81_case_set_is_guarded_explicitly(self) -> None:
        """The same runner, same state, differing only in scope."""

        with RunnerHarness(authorization=absent_authorization()) as harness:
            code, _ = harness.run(["--case-set", "full81"])
        self.assertNotEqual(code, 0)
        self.assertEqual(harness.stack_calls, 0)

    def test_shared_entrypoints_do_not_import_the_full81_guard(self) -> None:
        """EOB and Layer-A entrypoints are untouched by this remediation."""

        for relative in (
            "scripts/21b_preflight_v7_3_eob_successor.py",
            "scripts/21c_preflight_v7_3_layer_a_successor.py",
        ):
            with self.subTest(entrypoint=relative):
                source = (ROOT / relative).read_text(encoding="utf-8")
                self.assertNotIn(CANONICAL_GUARD_NAME, source)


# ---------------------------------------------------------------------------
# T2 - absent authorization fails closed
# ---------------------------------------------------------------------------


class T2AuthorizationAbsentTests(_GuardIntegrationTestCase):
    def test_t2_absent_authorization_fails_closed(self) -> None:
        with RunnerHarness(authorization=absent_authorization()) as harness:
            code, payload = harness.run()

        self.assertFailedClosed(code, payload, harness)
        self.assertIn("NOT AUTHORIZED", payload.get("error", ""))

    def test_t2_none_authorization_fails_closed(self) -> None:
        """``None`` is the most restrictive state and must never be authority."""

        with RunnerHarness(authorization=None) as harness:
            code, payload = harness.run()

        self.assertFailedClosed(code, payload, harness)

    def test_t2_pass_is_unreachable_when_planning_is_a_tripwire(self) -> None:
        """Nothing downstream of the guard can manufacture a PASS."""

        with RunnerHarness(
            authorization=absent_authorization(), stack_is_tripwire=True
        ) as harness:
            code, payload = harness.run()

        self.assertFailedClosed(code, payload, harness)


# ---------------------------------------------------------------------------
# T3 - a present-but-invalid authorization fails closed
# ---------------------------------------------------------------------------


class T3AuthorizationInvalidTests(_GuardIntegrationTestCase):
    def _assert_rejected(self, authorization: Mapping[str, Any]) -> None:
        with RunnerHarness(authorization=authorization) as harness:
            code, payload = harness.run()
        self.assertFailedClosed(code, payload, harness)

    def test_t3_overlay_present_invalid_fails_closed(self) -> None:
        authorization = granted_authorization()
        authorization["authorization_overlay"] = PRESENT_INVALID
        self._assert_rejected(authorization)

    def test_t3_status_not_granted_fails_closed(self) -> None:
        authorization = granted_authorization()
        authorization["full81_authorization_status"] = NOT_GRANTED
        self._assert_rejected(authorization)

    def test_t3_implementation_identity_drift_fails_closed(self) -> None:
        """An authorization never carries forward to changed production bytes."""

        authorization = granted_authorization()
        authorization["implementation_identity_digest"] = "0" * 64
        self._assert_rejected(authorization)

    def test_t3_unpublished_authorization_fails_closed(self) -> None:
        for field in ("record_present", "record_committed", "record_published"):
            with self.subTest(field=field):
                authorization = granted_authorization()
                authorization[field] = False
                self._assert_rejected(authorization)

    def test_t3_self_authorized_fails_closed(self) -> None:
        authorization = granted_authorization()
        authorization["self_authorized"] = True
        self._assert_rejected(authorization)

    def test_t3_wrong_lineage_or_candidate_fails_closed(self) -> None:
        for field in ("lineage_id", "candidate_id"):
            with self.subTest(field=field):
                authorization = granted_authorization()
                authorization[field] = "SOME_OTHER_LINEAGE"
                self._assert_rejected(authorization)

    def test_t3_wrong_scope_fails_closed(self) -> None:
        authorization = granted_authorization()
        authorization["authorization_scope"] = "A2"
        self._assert_rejected(authorization)

    def test_t3_broadened_authorization_fails_closed(self) -> None:
        """An artifact claiming more than the no-solve preflight is refused."""

        for field in ("authorizes_optimize_calls", "authorizes_full81_execution"):
            with self.subTest(field=field):
                authorization = granted_authorization()
                authorization[field] = True
                self._assert_rejected(authorization)


# ---------------------------------------------------------------------------
# T4 - a frozen production authority is not authorization
# ---------------------------------------------------------------------------


class T4FrozenAuthorityIsNotEnoughTests(_GuardIntegrationTestCase):
    def test_t4_frozen_lifecycle_without_authorization_fails_closed(self) -> None:
        lifecycle = frozen_lifecycle()
        self.assertEqual(lifecycle["production_authority_freeze_status"], "FROZEN")

        with RunnerHarness(
            authorization=absent_authorization(), lifecycle=lifecycle
        ) as harness:
            code, payload = harness.run()

        self.assertFailedClosed(code, payload, harness)

    def test_t4_authorization_claiming_frozen_is_not_self_sufficient(self) -> None:
        """``production_authority_freeze_status`` alone authorizes nothing."""

        authorization = {"production_authority_freeze_status": "FROZEN"}
        with RunnerHarness(authorization=authorization) as harness:
            code, payload = harness.run()

        self.assertFailedClosed(code, payload, harness)


# ---------------------------------------------------------------------------
# T5 - bundle PASS is not authorization.  This is the N-04 control.
# ---------------------------------------------------------------------------


class T5BundlePassIsNotEnoughTests(_GuardIntegrationTestCase):
    """The exact fail-open path the independent audit reported as N-04."""

    def test_t5_bundle_returns_pass_without_any_authorization(self) -> None:
        """Reproduce the negative control: PASS while reporting NOT_AUTHORIZED."""

        lifecycle = resolve_u06_lifecycle(ROOT)
        bundle = verify_v7_4_authority_bundle(ROOT, lifecycle, None)

        self.assertEqual(bundle["status"], "PASS")
        report = bundle["full81_authorization"]
        self.assertEqual(report["main_full81_authorization"], "NOT_AUTHORIZED")
        self.assertEqual(
            report["main_full81_authorization_resolved"][
                "main_full81_authorization"
            ],
            NOT_GRANTED,
        )

    def test_t5_bundle_pass_does_not_let_the_entrypoint_pass(self) -> None:
        """N-04: a PASSing bundle must not produce a PASSing preflight.

        G1: phase-aware, from the source contract (current_generation_phase
        over G1_GOVERNANCE_STAGES).  The control needs a state with a frozen
        lifecycle and NO lawful scope authorization.  A disposable G1
        repository promoted through Phase C is that state in every phase, so
        N-04 is proved there unconditionally.  The real repository is that
        state only until its G1 scope authorization is published; from then on
        its no-solve preflight PASS is lawful, but only for a VALID scope
        authorization, and it never reaches the execution callee.
        """

        from src.main_full81_authorization_v7_4 import resolve_full81_authorization
        from src.production_authority_lifecycle_u06 import (
            current_generation_phase,
            is_frozen,
        )
        from tests.test_21l_full81_production_generation_g1 import G1Fixture

        fixture = G1Fixture(stage="promote")
        try:
            frozen = fixture.resolve_lifecycle()
            self.assertTrue(is_frozen(frozen))
            self.assertEqual(
                verify_v7_4_authority_bundle(fixture.root, frozen, None)["status"], "PASS"
            )
            with RunnerHarness(authorization=None, lifecycle=frozen) as harness:
                with patch.object(harness.module, "ROOT", fixture.root):
                    code, payload = harness.run()
            self.assertFailedClosed(code, payload, harness)
        finally:
            fixture.dispose()

        lifecycle = resolve_u06_lifecycle(ROOT)
        self.assertEqual(
            verify_v7_4_authority_bundle(ROOT, lifecycle, None)["status"], "PASS"
        )
        phase = current_generation_phase(ROOT)
        self.assertEqual(phase["out_of_order_present"], [], phase["phase"])

        with RunnerHarness(authorization=None, lifecycle=lifecycle) as harness:
            code, payload = harness.run()

        if not phase["presence"]["main_full81_scope_authorization"]:
            self.assertFailedClosed(code, payload, harness)
            return
        scope = resolve_full81_authorization(ROOT, lifecycle)
        self.assertEqual(scope["authorization_overlay"], "PRESENT_VALID", scope.get("rejected_status"))
        self.assertEqual(scope["full81_authorization_status"], AUTHORIZED_FOR_NO_SOLVE_PREFLIGHT)
        self.assertEqual(code, 0, payload)
        self.assertEqual(payload["status"], "PASS")
        self.assertTrue(payload["main_full81_no_solve_preflight_authorized"])
        self.assertFalse(payload.get("production_execution_attempted", False))
        self.assertEqual(harness.layer_a_calls, 0)


# ---------------------------------------------------------------------------
# T6 - scope authorization is still not execution authorization
# ---------------------------------------------------------------------------


class T6ExecutionRemainsSeparateTests(unittest.TestCase):
    def test_t6_valid_scope_authorization_grants_no_execution(self) -> None:
        authorization = granted_authorization()

        self.assertIs(authorization["authorizes_optimize_calls"], False)
        self.assertIs(authorization["authorizes_full81_execution"], False)
        self.assertIs(
            authorization["requires_no_solve_preflight_before_execution"], True
        )
        self.assertEqual(
            authorization["full81_authorization_status"],
            AUTHORIZED_FOR_NO_SOLVE_PREFLIGHT,
        )

    def test_t6_execution_authorization_still_refuses(self) -> None:
        """Even a lawful scope authorization cannot reach execution."""

        with self.assertRaises(Full81AuthorizationError) as caught:
            require_full81_execution_authorization(granted_authorization())
        self.assertEqual(caught.exception.status, "FULL81_EXECUTION_NOT_AUTHORIZED")

    def test_t6_a2_remains_hard_blocked(self) -> None:
        for scope in ("a2", "A2", "a2-variable-floor"):
            with self.subTest(scope=scope):
                with self.assertRaises(Exception):
                    require_a2_hard_block(scope)

    def test_t6_confirm_native_solve_without_execute_is_refused(self) -> None:
        """The retained double interlock is untouched by the N-04 guard."""

        with RunnerHarness(authorization=granted_authorization()) as harness:
            code, payload = harness.run(["--confirm-native-solve"])

        self.assertNotEqual(code, 0)
        self.assertEqual(payload["status"], "EXECUTION_DISABLED")
        self.assertEqual(harness.layer_a_calls, 0)
        self.assertEqual(harness.stack_calls, 0)


# ---------------------------------------------------------------------------
# T7 - the guard is actually wired into the entrypoint
# ---------------------------------------------------------------------------


class T7GuardWiringTests(unittest.TestCase):
    """The coverage hole N-04 named: prove the wiring, not just the guard."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.source = RUNNER_PATH.read_text(encoding="utf-8")
        cls.tree = ast.parse(cls.source)

    def _main_function(self) -> ast.FunctionDef:
        for node in self.tree.body:
            if isinstance(node, ast.FunctionDef) and node.name == "main":
                return node
        self.fail("The runner does not define main().")

    @staticmethod
    def _called_names(node: ast.AST) -> list[tuple[int, str]]:
        found: list[tuple[int, str]] = []
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                func = child.func
                name = (
                    func.id
                    if isinstance(func, ast.Name)
                    else func.attr if isinstance(func, ast.Attribute) else None
                )
                if name:
                    found.append((child.lineno, name))
        return found

    def test_t7_entrypoint_calls_the_canonical_guard(self) -> None:
        names = {name for _, name in self._called_names(self._main_function())}
        self.assertIn(
            CANONICAL_GUARD_NAME,
            names,
            "21d.main() does not call the canonical Full81 authorization guard.",
        )

    def test_t7_guard_precedes_the_preflight_plan(self) -> None:
        """Ordering: require authorization BEFORE building the plan."""

        calls = self._called_names(self._main_function())
        guard_lines = [line for line, name in calls if name == CANONICAL_GUARD_NAME]
        stack_lines = [line for line, name in calls if name == "run_successor_stack"]
        self.assertTrue(guard_lines, "No canonical guard call found in main().")
        self.assertTrue(stack_lines, "No run_successor_stack call found in main().")
        self.assertLess(
            min(guard_lines),
            min(stack_lines),
            "The authorization guard must run before the preflight plan is built.",
        )

    def test_t7_guard_is_imported_not_reimplemented(self) -> None:
        """Reuse the canonical guard; never duplicate authorization semantics."""

        imported_from: list[str] = []
        for node in self.tree.body:
            if isinstance(node, ast.ImportFrom) and any(
                alias.name == CANONICAL_GUARD_NAME for alias in node.names
            ):
                imported_from.append(node.module or "")
        self.assertTrue(
            imported_from,
            f"{CANONICAL_GUARD_NAME} must be imported, not locally defined.",
        )
        for module in imported_from:
            self.assertIn("production_authority_bundle_v7_4", module)

        defined = {
            node.name
            for node in ast.walk(self.tree)
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        }
        self.assertNotIn(
            CANONICAL_GUARD_NAME,
            defined,
            "The runner must not define its own authorization guard.",
        )

    def test_t7_runner_declares_a_runner_version(self) -> None:
        """The identity an authorization must name is declared by the runner."""

        self.assertTrue(
            isinstance(getattr(RunnerHarness._load_runner(), "RUNNER_VERSION", None), str)
        )

    def test_t7_guard_cannot_be_bypassed_by_the_pass_path(self) -> None:
        """Runtime companion to the source assertions above.

        Every no-solve outcome is either a lawful PASS with an authorization, or
        a refusal.  There is no third path: with the plan builder replaced by a
        tripwire, an unauthorized run can only refuse.
        """

        with RunnerHarness(
            authorization=absent_authorization(), stack_is_tripwire=True
        ) as harness:
            code, payload = harness.run()
        self.assertNotEqual(code, 0)
        self.assertNotEqual(payload.get("status"), "PASS")
        self.assertEqual(harness.stack_calls, 0)

        with RunnerHarness(authorization=granted_authorization()) as harness:
            code, payload = harness.run()
        self.assertEqual(code, 0)
        self.assertEqual(payload["status"], "PASS")

    def test_t7_no_authorization_constant_shortcut(self) -> None:
        """The runner must not carry a hard-coded authorization verdict."""

        for forbidden in (
            f'"{AUTHORIZED_FOR_NO_SOLVE_PREFLIGHT}"',
            f"'{AUTHORIZED_FOR_NO_SOLVE_PREFLIGHT}'",
        ):
            self.assertNotIn(
                forbidden,
                self.source,
                "The runner may not declare an authorization verdict itself.",
            )


# ---------------------------------------------------------------------------
# N-05 - the Layer-A entrypoint is not an alternate Main Full81 gate
# ---------------------------------------------------------------------------


class _LayerAScopeTestCase(unittest.TestCase):
    """Shared assertions for a Layer-A scope refusal."""

    def assertScopeRefused(
        self,
        code: int,
        payload: Mapping[str, Any],
        harness: "LayerAHarness",
        *,
        expected_status: str,
    ) -> None:
        """Refused, with no plan, no model, and no optimization."""

        self.assertEqual(code, 2, f"Layer-A entrypoint did not refuse: {payload}")
        self.assertEqual(payload.get("status"), expected_status)
        self.assertNotIn("PASS", str(payload.get("verdict", "")))
        self.assertNotIn("selected_case_plan", payload)
        self.assertNotIn("selected_case_count", payload)
        self.assertFalse(payload.get("production_execution_attempted", False))
        counters = payload["execution_counters"]
        self.assertEqual(counters["model_constructions"], 0)
        self.assertEqual(counters["optimization_calls"], 0)
        self.assertEqual(counters["economic_evaluations"], 0)
        # N5-T4 / N5-T5 / N5-T6: the refusal preceded planning, case
        # selection, and the only model-constructing callee.
        self.assertEqual(harness.stack_calls, 0)
        self.assertEqual(harness.case_selection_calls, 0)
        self.assertEqual(harness.layer_a_calls, 0)


class N5T1ExplicitFull81IsRefusedTests(_LayerAScopeTestCase):
    """N5-T1: ``21c --case-set full81`` fails closed."""

    def test_n5_t1_explicit_full81_fails_closed(self) -> None:
        with LayerAHarness() as harness:
            code, payload = harness.run(["--case-set", "full81"])

        self.assertScopeRefused(
            code,
            payload,
            harness,
            expected_status=FULL81_ENTRYPOINT_REFUSAL_STATUS,
        )
        # The refusal must say where the one lawful route is.
        self.assertIn(RUNNER_RELATIVE_PATH, payload["error"])
        self.assertIn("no model was constructed", payload["error"])
        self.assertIn("no optimization ran", payload["error"])

    def test_n5_t1_full81_is_refused_on_the_execute_path_too(self) -> None:
        """Routing is prior to arming, so the refusal is flag-independent."""

        for argv in (
            ["--case-set", "full81", "--execute-production"],
            ["--case-set", "full81", "--confirm-native-solve"],
            [
                "--case-set",
                "full81",
                "--execute-production",
                "--confirm-native-solve",
            ],
        ):
            with self.subTest(argv=argv):
                with LayerAHarness() as harness:
                    code, payload = harness.run(argv)

                self.assertScopeRefused(
                    code,
                    payload,
                    harness,
                    expected_status=FULL81_ENTRYPOINT_REFUSAL_STATUS,
                )


class N5T2ImplicitRouteCannotReachFull81Tests(_LayerAScopeTestCase):
    """N5-T2: the no-argument route must not resolve to a Full81 PASS."""

    def test_n5_t2_no_argument_route_fails_closed(self) -> None:
        with LayerAHarness() as harness:
            code, payload = harness.run([])

        self.assertScopeRefused(
            code, payload, harness, expected_status="CASE_SCOPE_REQUIRED"
        )

    def test_n5_t2_no_argument_route_never_names_full81(self) -> None:
        """Not merely "not PASS": the default must not *be* Full81 at all."""

        with LayerAHarness() as harness:
            _, payload = harness.run([])

        self.assertNotEqual(payload.get("case_set"), "full81")
        self.assertNotIn("case_set", payload)

    def test_n5_t2_the_source_carries_no_full81_default(self) -> None:
        source = LAYER_A_PATH.read_text(encoding="utf-8")
        for forbidden in (
            'args.case_set or "full81"',
            "args.case_set or 'full81'",
        ):
            self.assertNotIn(
                forbidden,
                source,
                "The Layer-A entrypoint may not default its scope to Full81.",
            )


class N5T3LegitimateLayerARoutesSurviveTests(unittest.TestCase):
    """N5-T3: the analytical case sets this entrypoint exists for still work."""

    def test_n5_t3_every_permitted_case_set_passes_zero_solve(self) -> None:
        permitted = LayerAHarness().module.LAYER_A_PERMITTED_CASE_SETS
        self.assertTrue(permitted, "No Layer-A case set remained usable.")

        for case_set in permitted:
            with self.subTest(case_set=case_set):
                with LayerAHarness() as harness:
                    code, payload = harness.run(["--case-set", case_set])

                self.assertEqual(code, 0, payload)
                self.assertEqual(payload["status"], "PASS")
                self.assertIn("ZERO-SOLVE PREFLIGHT PASS", payload["verdict"])
                self.assertEqual(payload["case_set"], case_set)
                # Planning happened; no model and no execution did.
                self.assertEqual(harness.stack_calls, 1)
                self.assertEqual(harness.case_selection_calls, 1)
                self.assertEqual(harness.layer_a_calls, 0)
                # No authorization of any kind was required to get here.
                self.assertFalse(payload["main_full81_scope_routable_here"])

    def test_n5_t3_permitted_set_is_the_closed_vocabulary_minus_full81(
        self,
    ) -> None:
        """Derived, not enumerated: a renamed case set cannot be dropped."""

        module = LayerAHarness().module
        self.assertEqual(
            set(module.LAYER_A_PERMITTED_CASE_SETS),
            set(module.PRODUCTION_CASE_SETS) - {"full81"},
        )
        self.assertNotIn("full81", module.LAYER_A_PERMITTED_CASE_SETS)

    def test_n5_t3_a_layer_a_pass_is_not_a_full81_preflight_pass(self) -> None:
        """The PASS payload says, mechanically, which act it is not."""

        with LayerAHarness() as harness:
            code, payload = harness.run(["--case-set", "core-three"])

        self.assertEqual(code, 0, payload)
        self.assertFalse(payload["main_full81_scope_routable_here"])
        self.assertEqual(
            payload["main_full81_no_solve_preflight_entrypoint"],
            RUNNER_RELATIVE_PATH,
        )
        self.assertNotIn("main_full81_no_solve_preflight_authorized", payload)


class N5T4ToT6RefusalPrecedesEverythingTests(_LayerAScopeTestCase):
    """N5-T4/T5/T6: refusal precedes plan, model, and optimize."""

    def test_n5_t4_refusal_precedes_plan_selection(self) -> None:
        """With planning itself a tripwire, Full81 must still be refused."""

        for argv in (["--case-set", "full81"], []):
            with self.subTest(argv=argv):
                with LayerAHarness(stack_is_tripwire=True) as harness:
                    code, payload = harness.run(argv)

                self.assertEqual(code, 2, payload)
                self.assertEqual(harness.stack_calls, 0)
                self.assertEqual(harness.case_selection_calls, 0)

    def test_n5_t5_refusal_precedes_model_construction(self) -> None:
        """``run_layer_a_production`` is the only model-constructing callee."""

        with LayerAHarness() as harness:
            code, payload = harness.run(
                ["--case-set", "full81", "--execute-production"]
            )

        self.assertEqual(code, 2, payload)
        self.assertEqual(
            harness.layer_a_calls,
            0,
            "Full81 reached the model-constructing callee of 21c.",
        )

    def test_n5_t6_refusal_precedes_any_optimize(self) -> None:
        """No native backend is constructed on any refused Full81 route."""

        import src.production_successor_stack_v7_3 as stack_module

        for argv in (
            ["--case-set", "full81"],
            ["--case-set", "full81", "--execute-production"],
            ["--case-set", "full81", "--execute-production",
             "--confirm-native-solve"],
            [],
        ):
            with self.subTest(argv=argv):
                with patch.object(
                    stack_module, "NativeProductionBackend"
                ) as native_backend:
                    with LayerAHarness() as harness:
                        code, payload = harness.run(argv)

                self.assertEqual(code, 2, payload)
                native_backend.assert_not_called()
                counters = payload["execution_counters"]
                self.assertEqual(counters["model_constructions"], 0)
                self.assertEqual(counters["optimization_calls"], 0)
                self.assertEqual(counters["economic_evaluations"], 0)
                self.assertEqual(harness.layer_a_calls, 0)


class N5T7Full81EntrypointIsExclusiveTests(unittest.TestCase):
    """N5-T7: among 21b / 21c / 21d, only 21d can progress a Full81 preflight."""

    def test_n5_t7_eob_entrypoint_has_no_case_scope_at_all(self) -> None:
        """21b cannot select any case set, so it cannot select Full81."""

        spec = importlib.util.spec_from_file_location(
            "iris_thesis_21b_eob_under_test", EOB_PATH
        )
        module = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(module)

        self.assertFalse(hasattr(module.parse_args([]), "case_set"))
        source = EOB_PATH.read_text(encoding="utf-8")
        self.assertNotIn("select_production_cases", source)
        self.assertNotIn("full81", source)

    def test_n5_t7_layer_a_cannot_progress_full81(self) -> None:
        with LayerAHarness() as harness:
            code, payload = harness.run(["--case-set", "full81"])

        self.assertEqual(code, 2)
        self.assertEqual(payload["status"], FULL81_ENTRYPOINT_REFUSAL_STATUS)
        self.assertEqual(harness.stack_calls, 0)

    def test_n5_t7_only_the_guarded_runner_can_progress_full81(self) -> None:
        """Same scope, same state; the difference is the entrypoint."""

        with LayerAHarness() as layer_a:
            layer_a_code, layer_a_payload = layer_a.run(["--case-set", "full81"])

        with RunnerHarness(authorization=granted_authorization()) as runner:
            runner_code, runner_payload = runner.run(["--case-set", "full81"])

        self.assertEqual(layer_a_code, 2)
        self.assertNotEqual(layer_a_payload["status"], "PASS")
        self.assertEqual(layer_a.stack_calls, 0)

        self.assertEqual(runner_code, 0, runner_payload)
        self.assertEqual(runner_payload["status"], "PASS")
        self.assertEqual(runner_payload["case_set"], "full81")
        self.assertEqual(runner.stack_calls, 1)
        self.assertEqual(runner.layer_a_calls, 0)

    def test_n5_t7_the_exclusive_entrypoint_is_the_authorized_runner(
        self,
    ) -> None:
        """21c names the runner the authorization mechanism already designates.

        Asserted rather than imported, so that the Layer-A refusal creates no
        dependency on the authorization layer while a lawful rename of the
        runner still cannot leave a stale path in the refusal message.
        """

        module = LayerAHarness().module
        self.assertEqual(
            module.FULL81_EXCLUSIVE_ENTRYPOINT, EXPECTED_RUNNER_RELATIVE_PATH
        )
        self.assertEqual(
            module.FULL81_EXCLUSIVE_ENTRYPOINT, RUNNER_RELATIVE_PATH
        )


class N5T8GuardedRunnerStillRequiresAuthorizationTests(
    _GuardIntegrationTestCase
):
    """N5-T8: the N-05 remediation did not loosen the N-04 guard."""

    def test_n5_t8_full81_without_authorization_still_fails_closed(self) -> None:
        for authorization in (absent_authorization(), None):
            with self.subTest(authorization=authorization):
                with RunnerHarness(authorization=authorization) as harness:
                    code, payload = harness.run(["--case-set", "full81"])

                self.assertFailedClosed(code, payload, harness)

    def test_n5_t8_the_canonical_guard_is_still_wired_into_the_runner(
        self,
    ) -> None:
        source = RUNNER_PATH.read_text(encoding="utf-8")
        self.assertIn(CANONICAL_GUARD_NAME, source)


class N5T9AuthorizationCannotCreateASecondGateTests(_LayerAScopeTestCase):
    """N5-T9: a lawful authorization does not make 21c a Full81 gate.

    This is the control that separates exclusivity from "a second guard".  Had
    N-05 been remediated by copying the authorization guard into 21c, a lawful
    authorization would have opened a second valid Full81 no-solve PASS route
    and this test would fail.
    """

    def test_n5_t9_granted_authorization_does_not_legalise_layer_a_full81(
        self,
    ) -> None:
        import src.main_full81_authorization_v7_4 as auth_module
        import src.production_authority_lifecycle_u06 as lifecycle_module

        granted = granted_authorization()
        with patch.object(
            auth_module, "resolve_full81_authorization", lambda *a, **k: granted
        ), patch.object(
            lifecycle_module,
            "resolve_u06_lifecycle",
            lambda *a, **k: frozen_lifecycle(),
        ):
            with LayerAHarness() as harness:
                code, payload = harness.run(["--case-set", "full81"])

        self.assertScopeRefused(
            code,
            payload,
            harness,
            expected_status=FULL81_ENTRYPOINT_REFUSAL_STATUS,
        )

    def test_n5_t9_layer_a_resolves_no_authorization_at_all(self) -> None:
        """Structural: 21c cannot consult an authorization it never imports."""

        source = LAYER_A_PATH.read_text(encoding="utf-8")
        tree = ast.parse(source)
        imported: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    imported.add(alias.name)
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    imported.add(alias.name)

        for forbidden in (
            CANONICAL_GUARD_NAME,
            "resolve_full81_authorization",
            "require_full81_preflight_authorization",
            "require_full81_execution_authorization",
            "resolve_u06_lifecycle",
        ):
            with self.subTest(symbol=forbidden):
                self.assertNotIn(forbidden, imported)
                self.assertNotIn(forbidden, source)

    def test_n5_t9_layer_a_declares_no_authorization_verdict(self) -> None:
        source = LAYER_A_PATH.read_text(encoding="utf-8")
        for forbidden in (
            f'"{AUTHORIZED_FOR_NO_SOLVE_PREFLIGHT}"',
            f"'{AUTHORIZED_FOR_NO_SOLVE_PREFLIGHT}'",
        ):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":  # pragma: no cover
    unittest.main(verbosity=2)
