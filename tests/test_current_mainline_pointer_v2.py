#!/usr/bin/env python3
"""Pointer schema v2 / candidate R3: focused zero-solve tests.

What this suite proves
----------------------
* Candidate R3 verifies under schema v2 as internally consistent, and that is
  neither an acceptance nor an activation.
* It binds Framework v8 (= Framework v8 Candidate R2 bytes), the Gate 3
  acceptance record and Registry v8 = Registry v7.4 base + Registry v8 Delta R1,
  all anchored at the v8 package publication commit (Registry v7.4 at the
  commit that added it), never at the historical Full81 execution commit.
* Every v8 implementation, production, input, Pilot and result stage carries its
  exact NOT_YET_* sentinel.  No G1 identity and no placeholder hash can stand in.
* v7.4 history is bound by content through pointer R2 and verified by v1; the
  ACC-N1, U-01 and A2 dispositions stay as R2 records them.
* Canonical mode refuses an unactivated, unpublished or unaudited v8 activation.
* EOL conversion of a tracked file is reported as such and fails closed.
* v1 is byte-identical and its canonical and candidate routes are unaffected.
* Verification runs only read-only Git subcommands and builds no model.

LIVE PREMISE (``Live*`` and ``V1Regression*`` classes): the canonical pointer
is R2 (schema v1, v7.4 current) and R3 is an unaccepted candidate.  Retire these
classes with an audited replacement if R3 is ever activated; do not edit them
until then.  The other classes mutate in-memory copies of R3 or use a hermetic
temporary repository.

ZERO SOLVE.  Nothing here imports a solver, a model or a production module, and
no test parses or prints a case-level result value.
"""

from __future__ import annotations

import ast
import copy
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Any, Callable
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src import current_mainline_pointer_v1 as cmp1  # noqa: E402
from src import current_mainline_pointer_v2 as cmp2  # noqa: E402

MODULE_PATH = ROOT / "src" / "current_mainline_pointer_v2.py"
V1_MODULE_PATH = ROOT / "src" / "current_mainline_pointer_v1.py"
CANDIDATE_R3 = "configs/candidates/current_mainline_pointer_candidate_r3.json"
CANDIDATE_R2 = "configs/candidates/current_mainline_pointer_candidate_r2.json"
CANONICAL = cmp2.CANONICAL_POINTER_RELATIVE_PATH

#: Owner-stated accepted identities (Gate 3 record section 1), checked here
#: against what R3 binds.  Tests may carry literals; the verifier may not.
FW8R2_SHA256 = "cf299f2edbb771d36a1ce791e837c513d24428791eab982e6fcdf2608a171f93"
REGD_SHA256 = "99fe6eb5d2c47784d978012368f254b0094abdd8613cb1547a0def29f310e93c"
REG74_SHA256 = "5cc5d091af3be1943531a5a44d648fad58738730581dbf0331cdc2fe86029433"
GATE3_SHA256 = "b67eb1f05f8cd6dfd08040cf12599a324483cb4616c23bb1dc8763d436880cc9"
V8_PUBLICATION_COMMIT = "420f182ed221f3d4e2629f5e44da95c395d9f6b3"
HISTORICAL_EXECUTION_COMMIT = "c8f555094d6ab711ce6426302419fff958ed19fa"
#: v1 as accepted with pointer R2 (R2 acceptance closure, D5 r2_accepted_identity).
V1_ACCEPTED_SHA256 = "03485b36188d83163cdf9fd49cc14770aec8ca37769a402cbca4643df18ad930"

STDLIB_ALLOWLIST = {
    "__future__", "argparse", "json", "re", "sys", "pathlib", "typing",
    "src", "current_mainline_pointer_v1",
}


def load(relative: str, root: Path = ROOT) -> dict:
    return json.loads(root.joinpath(*relative.split("/")).read_bytes().decode("utf-8"))


def _set(node: Any, path: tuple, value: Any) -> None:
    for key in path[:-1]:
        node = node[key]
    node[path[-1]] = value


def verify(pointer: Any, mode: str = cmp2.MODE_CANDIDATE, path: str = CANDIDATE_R3) -> dict:
    return cmp2._verify(ROOT, pointer, mode=mode, pointer_relative_path=path)


class VerifierCase(unittest.TestCase):
    base: dict

    @classmethod
    def setUpClass(cls) -> None:
        cls.base = load(CANDIDATE_R3)

    def mutated(self, change: Callable[[dict], None], **kwargs: Any) -> dict:
        pointer = copy.deepcopy(self.base)
        change(pointer)
        return verify(pointer, **kwargs)

    def assertFailsClosed(self, result: dict, *codes: str) -> None:
        self.assertEqual(result["verdict"], cmp2.VERDICT_FAIL_CLOSED, result["failure_codes"])
        self.assertFalse(result["is_current_authority"])
        self.assertFalse(result["results_consumption_permitted"])
        self.assertFalse(result["grants_execution_authority"])
        for code in codes:
            self.assertIn(code, result["failure_codes"])

    def assertCandidateConsistent(self, result: dict) -> None:
        self.assertEqual(result["failures"], [])
        self.assertEqual(result["verdict"], cmp2.VERDICT_CANDIDATE_CONSISTENT)
        for flag in (
            "is_current_authority", "authority_conferred_by_this_verification", "candidate_promoted",
            "candidate_accepted", "activation_performed_by_this_verification",
            "results_consumption_permitted", "grants_execution_authority",
        ):
            self.assertFalse(result[flag], flag)


# ---------------------------------------------------------------------------
# Static: the v2 verifier is read-only by construction; v1 is untouched
# ---------------------------------------------------------------------------


class StaticV2Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.source = MODULE_PATH.read_text(encoding="utf-8")
        cls.tree = ast.parse(cls.source)
        cls.names = {node.id for node in ast.walk(cls.tree) if isinstance(node, ast.Name)}
        cls.attributes = {
            node.attr for node in ast.walk(cls.tree) if isinstance(node, ast.Attribute)
        }

    def test_imports_are_standard_library_plus_v1(self) -> None:
        imported = set()
        for node in ast.walk(self.tree):
            if isinstance(node, ast.Import):
                imported |= {alias.name.split(".")[0] for alias in node.names}
            elif isinstance(node, ast.ImportFrom):
                self.assertEqual(node.level, 0, "relative import")
                imported.add((node.module or "").split(".")[0])
        self.assertLessEqual(imported, STDLIB_ALLOWLIST, imported - STDLIB_ALLOWLIST)

    def test_no_solver_model_subprocess_or_dynamic_code(self) -> None:
        for forbidden in (
            "gurobipy", "gp", "Model", "optimize", "optimizeAsync", "addVar", "addConstr",
            "subprocess", "import_module", "__import__", "exec", "eval",
        ):
            self.assertNotIn(forbidden, self.names | self.attributes)

    def test_no_file_is_ever_written(self) -> None:
        for writer in (
            "write_text", "write_bytes", "mkdir", "makedirs", "unlink", "rmdir", "rename",
            "touch", "symlink_to", "hardlink_to", "chmod", "remove", "rmtree", "copy", "copyfile",
        ):
            self.assertNotIn(writer, self.attributes)
        for node in ast.walk(self.tree):
            if isinstance(node, ast.Call):
                self.assertFalse(isinstance(node.func, ast.Name) and node.func.id == "open")
                if isinstance(node.func, ast.Attribute) and node.func.attr == "write":
                    self.assertEqual(ast.unparse(node.func), "sys.stdout.write")

    def test_the_module_carries_no_identity_literal(self) -> None:
        self.assertEqual(re.findall(r"\b[0-9a-f]{40}\b", self.source), [])
        self.assertEqual(re.findall(r"\b[0-9a-f]{64}\b", self.source), [])

    def test_no_public_entry_point_can_promote_or_activate(self) -> None:
        public = {n for n in vars(cmp2) if not n.startswith("_") and callable(getattr(cmp2, n))}
        for name in public:
            self.assertIsNone(
                re.search(r"promote|activate|accept|publish|write|create|install", name, re.I), name
            )

    def test_check_ids_are_closed_and_v1_aliases_resolve(self) -> None:
        self.assertEqual(len(set(cmp2.CHECK_IDS)), len(cmp2.CHECK_IDS))
        self.assertLessEqual(set(cmp2._V1_CHECK_ALIASES.values()), set(cmp2.CHECK_IDS))
        self.assertEqual(set(cmp2.V8_UNBUILT_STAGES), {
            "scientific_implementation", "production_generation", "production_runner",
            "input_compatibility", "pilot", "numerical_results", "result_acceptance",
        })
        for status, identity in cmp2.V8_UNBUILT_STAGES.values():
            self.assertIn(status, (cmp2.NOT_YET_AUTHORIZED, cmp2.NOT_YET_EXECUTED))
            self.assertIn(identity, (cmp2.NOT_YET_AUTHORIZED, cmp2.NOT_YET_EXECUTED))

    def test_v1_module_is_byte_identical_to_its_accepted_identity(self) -> None:
        data = V1_MODULE_PATH.read_bytes()
        self.assertEqual(hashlib.sha256(data).hexdigest(), V1_ACCEPTED_SHA256)
        git = cmp1._Git(ROOT)
        blob = git.tree("HEAD")[cmp1.VERIFIER_MODULE_RELATIVE_PATH]
        self.assertEqual(git.blob_digests([blob])[blob], (V1_ACCEPTED_SHA256, len(data)))


# ---------------------------------------------------------------------------
# Live: the real candidate R3 (LIVE PREMISE: R2 canonical, R3 a candidate)
# ---------------------------------------------------------------------------


class LiveR3Tests(VerifierCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.result = cmp2.verify_candidate_pointer(ROOT, CANDIDATE_R3)

    def test_candidate_r3_is_consistent_and_not_authority(self) -> None:
        self.assertCandidateConsistent(self.result)
        expected = {check: cmp2.STATUS_PASS for check in cmp2.CHECK_IDS}
        expected[cmp2.CHECK_V8_RESULTS] = cmp2.STATUS_NOT_APPLICABLE
        expected[cmp2.CHECK_ACTIVATION] = cmp2.STATUS_NOT_APPLICABLE
        self.assertEqual(self.result["checks"], expected)
        self.assertEqual(
            self.result["routed_current_authority"],
            {"methodology_authority": None, "evidence_authority_components": []},
        )
        self.assertEqual(self.result["v8_result_validation"], cmp2.V8_RESULT_VALIDATION_NOT_APPLICABLE)

    def test_framework_and_composite_registry_identities(self) -> None:
        methodology, evidence = self.base["methodology_authority"], self.base["evidence_authority"]
        self.assertEqual(methodology["formal_name"], "Framework v8")
        self.assertEqual(methodology["document"]["sha256"], FW8R2_SHA256)
        self.assertEqual(methodology["gate3_acceptance_record"]["sha256"], GATE3_SHA256)
        self.assertEqual(evidence["formal_name"], "Registry v8")
        self.assertNotIn("document", evidence)
        self.assertEqual(evidence["base_component"]["document"]["sha256"], REG74_SHA256)
        self.assertEqual(evidence["delta_component"]["document"]["sha256"], REGD_SHA256)
        self.assertFalse(evidence["base_component"]["modified_by_v8"])
        for identity in (
            methodology["document"], methodology["gate3_acceptance_record"],
            evidence["delta_component"]["document"],
        ):
            self.assertEqual(identity["git_anchor_commit"], V8_PUBLICATION_COMMIT)
            self.assertEqual(identity["git_anchor_role"], cmp1.ANCHOR_ADDED)
        self.assertNotIn(HISTORICAL_EXECUTION_COMMIT, json.dumps(methodology))

    def test_every_v8_stage_is_not_yet(self) -> None:
        stages = self.base["v8_unbuilt_stages"]
        for name, (status, identity) in cmp2.V8_UNBUILT_STAGES.items():
            self.assertEqual((stages[name]["status"], stages[name]["identity"]), (status, identity))
        self.assertFalse(stages["historical_identity_reuse_permitted"])

    def test_historical_route_ran_through_v1_and_passed(self) -> None:
        route = self.result["historical_v7_4_route"]
        self.assertEqual(route["verifier_module"], cmp1.VERIFIER_MODULE_RELATIVE_PATH)
        self.assertEqual(route["pointer_path"], CANDIDATE_R2)
        self.assertEqual(route["verdict"], cmp1.VERDICT_CANDIDATE_CONSISTENT)
        self.assertEqual(route["failure_codes"], [])

    def test_candidate_pass_is_not_acceptance_or_activation(self) -> None:
        identity = self.base["pointer_identity"]
        self.assertEqual(identity["lifecycle_state"], cmp1.LIFECYCLE_CANDIDATE)
        self.assertEqual(
            (identity["is_candidate"], identity["is_accepted"], identity["is_canonical"],
             identity["is_current_authority"], identity["self_accepted"]),
            (True, False, False, False, False),
        )
        activation = self.base["activation_basis"]
        self.assertEqual(activation["status"], cmp1.ACTIVATION_NOT_ACTIVATED)
        self.assertTrue(all(activation[role] is None for role in cmp1.ACTIVATION_ROLES))
        self.assertFalse(self.base["activation_contract"]["candidate_consistency_is_acceptance"])
        self.assertFalse(self.base["activation_contract"]["automatic_progression"])
        result = verify(copy.deepcopy(self.base), mode=cmp2.MODE_CANONICAL, path=CANONICAL)
        self.assertFailsClosed(
            result, "CANONICAL_POINTER_IS_CANDIDATE_ONLY", "ACTIVATION_BASIS_ABSENT",
            "POINTER_PATH_FIELD_MISMATCH",
        )

    def test_live_canonical_is_schema_v1_and_v2_does_not_verify_it(self) -> None:
        result = cmp2.verify_canonical_pointer(ROOT)
        self.assertFailsClosed(result, "SCHEMA_VERSION_NOT_V2")
        self.assertEqual(load(CANONICAL)["schema_version"], cmp1.POINTER_SCHEMA_VERSION)


# ---------------------------------------------------------------------------
# Negative controls on in-memory copies of R3
# ---------------------------------------------------------------------------

_M = ("methodology_authority",)
_E = ("evidence_authority",)
_H = ("historical_v7_4_authority",)
_S = ("v8_unbuilt_stages",)


class Gate3AndIdentityTests(VerifierCase):
    def test_missing_gate3_acceptance_record(self) -> None:
        result = self.mutated(lambda p: p["methodology_authority"].pop("gate3_acceptance_record"))
        self.assertFailsClosed(result, "SCHEMA_VIOLATION")

    def test_gate3_record_swapped_for_another_accepted_record(self) -> None:
        def change(p: dict) -> None:
            rec = copy.deepcopy(p["methodology_authority"]["gate2_governing_sources"][0]["document"])
            p["methodology_authority"]["gate3_acceptance_record"] = rec
            p["roles"]["accepted_current"][3]["path"] = rec["path"]

        self.assertFailsClosed(self.mutated(change), "GATE3_RECORD_DOES_NOT_BIND")

    def test_gate3_record_hash_tampered(self) -> None:
        result = self.mutated(lambda p: _set(p, (*_M, "gate3_acceptance_record", "sha256"), "0" * 64))
        self.assertFailsClosed(result, "RAW_BYTES_DIFFER_IN_CONTENT", "GIT_BLOB_BYTES_MISMATCH")

    def test_gate3_verdict_not_pass_and_custody_fabricated(self) -> None:
        stop = "FRAMEWORK V8 R2 + REGISTRY V8 DELTA — CONTINUATION AUDIT STOP"
        result = self.mutated(lambda p: _set(p, (*_M, "gate3_independent_audit", "verdict_as_recorded"), stop))
        self.assertFailsClosed(result, "GATE3_AUDIT_NOT_PASS")
        result = self.mutated(
            lambda p: _set(p, (*_M, "gate3_independent_audit", "report_custody"), "FILE_BOUND")
        )
        self.assertFailsClosed(result, "GATE3_AUDIT_CUSTODY_MISSTATED")
        result = self.mutated(lambda p: _set(
            p, (*_M, "gate3_independent_audit", "report_file"), copy.deepcopy(p["methodology_authority"]["document"])
        ))
        self.assertFailsClosed(result, "SCHEMA_VIOLATION")

    def test_gate3_acceptance_cannot_claim_activation(self) -> None:
        result = self.mutated(lambda p: _set(
            p, (*_M, "gate3_researcher_acceptance", "activation_authorized_by_gate3_record"), True
        ))
        self.assertFailsClosed(result, "GATE3_RECORD_CLAIMS_ACTIVATION")

    def test_framework_hash_tampered(self) -> None:
        result = self.mutated(lambda p: _set(p, (*_M, "document", "sha256"), "1" * 64))
        self.assertFailsClosed(
            result, "RAW_BYTES_DIFFER_IN_CONTENT", "GIT_BLOB_BYTES_MISMATCH", "GATE3_RECORD_DOES_NOT_BIND"
        )

    def test_registry_component_hashes_tampered(self) -> None:
        result = self.mutated(lambda p: _set(p, (*_E, "delta_component", "document", "sha256"), "2" * 64))
        self.assertFailsClosed(result, "GIT_BLOB_BYTES_MISMATCH", "GATE3_RECORD_DOES_NOT_BIND")
        result = self.mutated(lambda p: _set(p, (*_E, "base_component", "document", "sha256"), "3" * 64))
        self.assertFailsClosed(
            result, "GIT_BLOB_BYTES_MISMATCH", "REGISTRY_BASE_NOT_REGISTRY_V7_4", "GATE3_RECORD_DOES_NOT_BIND"
        )

    def test_delta_alone_is_not_registry_v8(self) -> None:
        def change(p: dict) -> None:
            p["evidence_authority"]["document"] = copy.deepcopy(
                p["evidence_authority"]["delta_component"]["document"]
            )
            p["evidence_authority"]["delta_alone_is_registry_v8"] = True

        self.assertFailsClosed(self.mutated(change), "EVIDENCE_AUTHORITY_NOT_COMPOSITE")
        result = self.mutated(lambda p: p["evidence_authority"].pop("base_component"))
        self.assertFailsClosed(result, "SCHEMA_VIOLATION")

    def test_v8_methodology_anchored_at_historical_execution_commit(self) -> None:
        def change(p: dict) -> None:
            document = p["methodology_authority"]["document"]
            document["git_anchor_commit"] = HISTORICAL_EXECUTION_COMMIT
            document["git_anchor_role"] = cmp1.ANCHOR_CONTENT

        self.assertFailsClosed(
            self.mutated(change),
            "V8_ANCHORED_TO_HISTORICAL_EXECUTION_COMMIT",
            "V8_IDENTITY_NOT_ANCHORED_AT_V8_PUBLICATION",
            "GIT_BLOB_MISMATCH_AT_ANCHOR_COMMIT",
        )


class PromotionAndStageTests(VerifierCase):
    def test_historical_g1_runner_promoted_to_v8_current(self) -> None:
        runner = "scripts/21d_preflight_v7_3_final81_successor.py"
        result = self.mutated(
            lambda p: p["roles"]["accepted_current"].append({"role": "PRODUCTION_RUNNER", "path": runner})
        )
        self.assertFailsClosed(
            result, "ACCEPTED_CURRENT_ROLES_MISMATCH", "HISTORICAL_ROLE_PROMOTED_TO_V8_CURRENT",
            "NON_CURRENT_PATH_CLAIMED_CURRENT",
        )

    def test_framework_v7_4_routed_as_framework_v8(self) -> None:
        framework_v7_4 = load(CANDIDATE_R2)["methodology_authority"]["document"]

        def change(p: dict) -> None:
            p["methodology_authority"]["document"] = copy.deepcopy(framework_v7_4)
            p["roles"]["accepted_current"][0]["path"] = framework_v7_4["path"]

        self.assertFailsClosed(
            self.mutated(change),
            "HISTORICAL_ROLE_PROMOTED_TO_V8_CURRENT",
            "V8_ANCHORED_TO_HISTORICAL_EXECUTION_COMMIT",
            "GATE3_RECORD_DOES_NOT_BIND",
        )

    def test_historical_roles_must_be_carried_and_labelled(self) -> None:
        run = "results/layer_a/final_81_v7_3/runs/20261008T183934456307Z_a6826f4828"

        def drop(p: dict) -> None:
            p["roles"]["historical_only"] = [e for e in p["roles"]["historical_only"] if e["path"] != run]

        self.assertFailsClosed(self.mutated(drop), "HISTORICAL_ROLE_NOT_CARRIED")

        def relabel(p: dict) -> None:
            entry = next(e for e in p["roles"]["historical_only"] if e["path"] == run)
            entry["role"] = "ACCEPTED_CURRENT_FULL81_LAYER_A_RESULT_SET"

        self.assertFailsClosed(self.mutated(relabel), "HISTORICAL_ROLE_LABEL_INVALID")

    def test_g1_or_placeholder_identity_in_a_v8_stage(self) -> None:
        core_sha = load(CANDIDATE_R2)["implementation"]["scientific_model_core"]["sha256"]
        for stage, value in (
            ("scientific_implementation", core_sha),
            ("production_runner", "scripts/21d_preflight_v7_3_final81_successor.py"),
            ("input_compatibility", "0" * 64),
            ("pilot", HISTORICAL_EXECUTION_COMMIT),
        ):
            with self.subTest(stage=stage):
                result = self.mutated(lambda p: _set(p, (*_S, stage, "identity"), value))
                self.assertFailsClosed(result, "V8_STAGE_IDENTITY_FABRICATED")
        result = self.mutated(lambda p: _set(
            p, (*_S, "production_generation", "accepted_lifecycle_record"),
            copy.deepcopy(p["methodology_authority"]["document"]),
        ))
        self.assertFailsClosed(result, "V8_STAGE_CARRIES_UNDECLARED_FIELD")
        result = self.mutated(lambda p: _set(p, (*_S, "historical_identity_reuse_permitted"), True))
        self.assertFailsClosed(result, "V8_HISTORICAL_IDENTITY_REUSE_PERMITTED")

    def test_missing_or_invalid_not_yet_statuses(self) -> None:
        result = self.mutated(lambda p: p["v8_unbuilt_stages"].pop("pilot"))
        self.assertFailsClosed(result, "V8_STAGE_STATUS_MISSING")
        result = self.mutated(lambda p: _set(p, (*_S, "input_compatibility", "status"), "ACCEPTED"))
        self.assertFailsClosed(result, "V8_STAGE_STATUS_INVALID")
        result = self.mutated(lambda p: _set(p, (*_S, "scientific_implementation", "status"), "NOT_YET_EXECUTED"))
        self.assertFailsClosed(result, "V8_STAGE_STATUS_INVALID")
        result = self.mutated(lambda p: _set(p, (*_S, "dg_extension"), {"status": "NOT_YET_AUTHORIZED",
                                                                       "identity": "NOT_YET_AUTHORIZED"}))
        self.assertFailsClosed(result, "V8_STAGE_UNKNOWN")

    def test_not_applicable_is_not_an_escape_from_result_validation(self) -> None:
        result = self.mutated(lambda p: _set(p, (*_S, "numerical_results", "status"), "NOT_APPLICABLE"))
        self.assertFailsClosed(
            result, "V8_STAGE_STATUS_INVALID", "V8_RESULT_CLAIM_WITHOUT_RESULT_VALIDATOR"
        )
        self.assertEqual(result["checks"][cmp2.CHECK_V8_RESULTS], cmp2.STATUS_FAIL)
        self.assertEqual(result["v8_result_validation"], cmp2.V8_RESULT_VALIDATION_FAIL)
        result = self.mutated(lambda p: _set(p, (*_S, "result_acceptance", "identity"), "4" * 64))
        self.assertEqual(result["checks"][cmp2.CHECK_V8_RESULTS], cmp2.STATUS_FAIL)
        self.assertFailsClosed(result, "V8_RESULT_CLAIM_WITHOUT_RESULT_VALIDATOR")


class HistoricalPreservationTests(VerifierCase):
    def test_dispositions_cannot_be_closed_or_reinterpreted(self) -> None:
        cases = (
            ((*_H, "carried_dispositions", "ACC-N1", "closed"), True, "HISTORICAL_DISPOSITION_ALTERED"),
            ((*_H, "carried_dispositions", "ACC-N1", "disposition"), "CLOSED", "HISTORICAL_DISPOSITION_ALTERED"),
            ((*_H, "carried_dispositions", "U-01", "status"), "CLOSED", "HISTORICAL_DISPOSITION_ALTERED"),
            (
                (*_H, "carried_dispositions", "A2", "a2_variable_floor_status"), "LIFTED",
                "HISTORICAL_DISPOSITION_ALTERED",
            ),
            (
                (*_H, "carried_dispositions", "reinterpreted_as_v8_constraint"), True,
                "HISTORICAL_FINDING_REINTERPRETED_AS_V8",
            ),
            (
                (*_H, "carried_dispositions", "closed_or_remediated_by_this_pointer"), ["ACC-N1"],
                "HISTORICAL_FINDING_CLOSED_BY_POINTER",
            ),
            ((*_H, "carried_dispositions", "scope"), "V8_SCOPE", "HISTORICAL_SCOPE_ALTERED"),
        )
        for location, value, code in cases:
            with self.subTest(location=location):
                self.assertFailsClosed(self.mutated(lambda p: _set(p, location, value)), code)

    def test_carried_identities_are_compared_with_pointer_r2(self) -> None:
        result = self.mutated(
            lambda p: _set(p, (*_H, "carried_identities", "full81_run_id"), "20990101T000000000000Z_0000000000")
        )
        self.assertFailsClosed(result, "HISTORICAL_IDENTITY_ALTERED")
        result = self.mutated(lambda p: _set(p, (*_H, "carried_identities", "v8_runner_sha256"), "x"))
        self.assertFailsClosed(result, "HISTORICAL_IDENTITY_UNDECLARED")

    def test_predecessor_binding_is_by_content(self) -> None:
        result = self.mutated(lambda p: _set(p, (*_H, "predecessor_pointer", "payload_digest"), "5" * 64))
        self.assertFailsClosed(result, "PREDECESSOR_PAYLOAD_MISMATCH")
        result = self.mutated(
            lambda p: _set(p, (*_H, "predecessor_pointer", "canonical_object", "git_blob_id"), "6" * 40)
        )
        self.assertFailsClosed(result, "HISTORICAL_OBJECT_BLOB_MISMATCH")
        # Same bytes, but at a commit that did not write them.
        result = self.mutated(
            lambda p: _set(p, (*_H, "predecessor_pointer", "canonical_object", "git_commit"), V8_PUBLICATION_COMMIT)
        )
        self.assertFailsClosed(
            result, "HISTORICAL_OBJECT_NOT_WRITTEN_BY_COMMIT", "PREDECESSOR_ACTIVATION_COMMIT_MISMATCH"
        )
        result = self.mutated(lambda p: _set(p, (*_H, "pointer_r1", "payload_digest"), "7" * 64))
        self.assertFailsClosed(result, "POINTER_R1_PAYLOAD_MISMATCH")

    def test_historical_route_must_be_v1_candidate_on_r2(self) -> None:
        result = self.mutated(lambda p: _set(
            p, (*_H, "historical_verification_route", "pointer_path"),
            "configs/candidates/current_mainline_pointer_candidate_r1.json",
        ))
        self.assertFailsClosed(result, "HISTORICAL_ROUTE_MISDECLARED")


class LifecycleBoundaryAndGitTests(VerifierCase):
    def test_candidate_cannot_claim_acceptance_or_activation(self) -> None:
        result = self.mutated(lambda p: _set(p, ("pointer_identity", "is_accepted"), True))
        self.assertFailsClosed(result, "CANDIDATE_CLAIMS_AUTHORITY")
        result = self.mutated(lambda p: _set(p, ("activation_basis", "status"), cmp1.ACTIVATION_ACCEPTED_PUBLISHED))
        self.assertFailsClosed(result, "CANDIDATE_CLAIMS_ACTIVATION")
        result = self.mutated(lambda p: _set(p, ("pointer_identity", "self_accepted"), True))
        self.assertFailsClosed(result, "POINTER_SELF_ACCEPTED")
        result = verify(copy.deepcopy(self.base), path="configs/elsewhere/r3.json")
        self.assertFailsClosed(result, "CANDIDATE_NOT_UNDER_CANDIDATE_DIRECTORY")

    def test_non_authorization_and_activation_contract(self) -> None:
        def drop(p: dict) -> None:
            p["non_authorization_boundaries"]["not_authorized_by_this_pointer"].remove("SOLVER_CALL")

        self.assertFailsClosed(self.mutated(drop), "NON_AUTHORIZATION_BOUNDARY_DROPPED")
        result = self.mutated(
            lambda p: _set(p, ("non_authorization_boundaries", "pointer_grants_execution_authority"), True)
        )
        self.assertFailsClosed(result, "POINTER_CLAIMS_EXECUTION_AUTHORITY")
        result = self.mutated(lambda p: _set(p, ("non_authorization_boundaries", "authorizes"), ["V8_PILOT"]))
        self.assertFailsClosed(result, "POINTER_CLAIMS_AUTHORIZATION")
        for key, value in (
            ("automatic_progression", True),
            ("independent_audit_required_before_acceptance", False),
            ("candidate_consistency_is_acceptance", True),
        ):
            with self.subTest(key=key):
                result = self.mutated(lambda p: _set(p, ("activation_contract", key), value))
                self.assertFailsClosed(result, "ACTIVATION_CONTRACT_INVALID")
        result = self.mutated(
            lambda p: _set(p, ("validation_contract", "verifier_module"), cmp1.VERIFIER_MODULE_RELATIVE_PATH)
        )
        self.assertFailsClosed(result, "VALIDATION_CONTRACT_MISMATCH")

    def test_schema_refuses_v1_payloads_and_untracked_identities(self) -> None:
        result = self.mutated(lambda p: _set(p, ("schema_version",), cmp1.POINTER_SCHEMA_VERSION))
        self.assertFailsClosed(result, "SCHEMA_VERSION_NOT_V2")
        generation = load(CANDIDATE_R2)["production_generation"]
        result = self.mutated(lambda p: _set(p, ("production_generation",), generation))
        self.assertFailsClosed(result, "SCHEMA_VIOLATION")

        def untrack(p: dict) -> None:
            p["methodology_authority"]["document"].update(
                git_tracked=False, git_blob_id=None, git_anchor_commit=None, git_anchor_role=None
            )

        self.assertFailsClosed(self.mutated(untrack), "SCHEMA_VIOLATION")

    def test_git_provenance(self) -> None:
        result = self.mutated(lambda p: p["git_provenance"]["ancestry_chain_oldest_to_newest"].reverse())
        self.assertFailsClosed(result, "GIT_ANCESTRY_ORDER_VIOLATED")
        result = self.mutated(lambda p: _set(p, ("git_provenance", "live_head_must_equal_a_recorded_commit"), True))
        self.assertFailsClosed(result, "LIVE_HEAD_EQUALITY_REQUIREMENT_FORBIDDEN")
        result = self.mutated(lambda p: _set(p, ("git_provenance", "v8_package_publication_commit"), "8" * 40))
        self.assertFailsClosed(result, "GIT_COMMIT_ABSENT", "GIT_COMMIT_NOT_IN_ANCESTRY_CHAIN")


# ---------------------------------------------------------------------------
# Canonical mode: unpublished or unaudited v8 activation is refused
# ---------------------------------------------------------------------------


def _as_activated(pointer: dict, activation: dict) -> None:
    pointer["pointer_identity"].update(
        lifecycle="ACCEPTED / CANONICAL / CURRENT AUTHORITY",
        lifecycle_state=cmp1.LIFECYCLE_CANONICAL,
        is_candidate=False,
        is_accepted=True,
        is_canonical=True,
        is_current_authority=True,
        this_file_path=CANONICAL,
    )
    pointer["activation_basis"] = {"status": cmp1.ACTIVATION_ACCEPTED_PUBLISHED, **activation}


class CanonicalModeTests(VerifierCase):
    def canonical(self, activation: dict) -> dict:
        pointer = copy.deepcopy(self.base)
        _as_activated(pointer, activation)
        return verify(pointer, mode=cmp2.MODE_CANONICAL, path=CANONICAL)

    def test_unpublished_activation_records_are_refused(self) -> None:
        def fake(role: str) -> dict:
            return {
                "path": f"results/provenance/nonexistent_test_only_{role}/record.json",
                "sha256": "9" * 64,
                "bytes": 1,
                "git_tracked": True,
                "git_blob_id": "a" * 40,
                "git_anchor_commit": V8_PUBLICATION_COMMIT,
                "git_anchor_role": cmp1.ANCHOR_ADDED,
            }

        activation = {role: fake(role) for role in cmp1.ACTIVATION_ROLES}
        activation["audited_candidate"]["path"] = "configs/candidates/nonexistent_test_only_r3.json"
        result = self.canonical(activation)
        # v1's activation check stops at the first unreadable record, so the
        # published-file comparison is not reached; the verdict is still closed.
        self.assertFailsClosed(
            result, "FILE_ABSENT", "RECORD_UNREADABLE", "ACTIVATION_DOES_NOT_ACCEPT_V8_METHODOLOGY"
        )
        self.assertFalse(result["is_current_authority"])
        self.assertIsNone(result["routed_current_authority"]["methodology_authority"])

    def test_activation_reusing_the_r2_audit_and_acceptance_is_refused(self) -> None:
        predecessor = self.base["historical_v7_4_authority"]["predecessor_pointer"]
        activation = {role: copy.deepcopy(predecessor[role]) for role in cmp1.ACTIVATION_ROLES}
        result = self.canonical(activation)
        self.assertFailsClosed(
            result,
            "ACTIVATION_PAYLOAD_NOT_THE_AUDITED_CANDIDATE",
            "ACTIVATION_AUDIT_INVALID",
            "ACTIVATION_ACCEPTANCE_INVALID",
            "ACTIVATION_ROLE_ALIASED",
            "ACTIVATION_DOES_NOT_ACCEPT_V8_METHODOLOGY",
            "CANONICAL_OBJECT_NOT_THE_PUBLISHED_FILE",
        )

    def test_v1_cannot_verify_a_v2_pointer_as_canonical(self) -> None:
        pointer = copy.deepcopy(self.base)
        _as_activated(pointer, {role: None for role in cmp1.ACTIVATION_ROLES})
        result = cmp1._verify(
            ROOT, pointer, mode=cmp1.MODE_CANONICAL, pointer_relative_path=CANONICAL,
            results_policy=cmp1.RESULTS_POLICY_NONE,
        )
        self.assertEqual(result["verdict"], cmp1.VERDICT_FAIL_CLOSED)
        self.assertIn("SCHEMA_VIOLATION", result["failure_codes"])


# ---------------------------------------------------------------------------
# v1 regression (LIVE PREMISE) and the competing-pointer scan
# ---------------------------------------------------------------------------


class V1RegressionTests(VerifierCase):
    def test_v1_canonical_still_verifies_with_r3_present(self) -> None:
        result = cmp1.verify_canonical_pointer(ROOT, results_policy=cmp1.RESULTS_POLICY_NONE)
        self.assertEqual(result["verdict"], cmp1.VERDICT_CANONICAL_VERIFIED, result["failure_codes"])
        self.assertEqual(result["checks"][cmp1.CHECK_ROLES], cmp1.STATUS_PASS)
        self.assertNotIn("CONFLICTING_CURRENT_MAINLINE_CLAIM", result["failure_codes"])

    def test_v1_candidate_r2_still_consistent(self) -> None:
        result = cmp1.verify_candidate_pointer(ROOT, CANDIDATE_R2, results_policy=cmp1.RESULTS_POLICY_NONE)
        self.assertEqual(result["verdict"], cmp1.VERDICT_CANDIDATE_CONSISTENT, result["failure_codes"])

    def test_r3_is_seen_by_the_v1_scan_and_claims_nothing(self) -> None:
        self.assertEqual(self.base["artifact_type"], cmp1.POINTER_ARTIFACT_TYPE)
        identity = self.base["pointer_identity"]
        self.assertIs(identity["is_current_authority"], False)
        self.assertIs(identity["is_canonical"], False)
        self.assertEqual(identity["lifecycle_state"], cmp1.LIFECYCLE_CANDIDATE)


class ScanAfterActivationTests(VerifierCase):
    """A hermetic ``configs/`` tree shaped like the repository after a future
    activation: a schema-v2 pointer at the canonical path, R2 and R3 as
    candidates.  Only the competing-pointer scans are exercised here."""

    def setUp(self) -> None:
        self.home = Path(tempfile.mkdtemp(prefix="cmp2_")).resolve()
        activated = copy.deepcopy(self.base)
        _as_activated(activated, {role: None for role in cmp1.ACTIVATION_ROLES})
        self.write(CANONICAL, activated)
        self.write(CANDIDATE_R2, load(CANDIDATE_R2))
        self.write(CANDIDATE_R3, self.base)

    def tearDown(self) -> None:
        shutil.rmtree(self.home, ignore_errors=True)

    def write(self, relative: str, payload: dict) -> None:
        target = self.home.joinpath(*relative.split("/"))
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes((json.dumps(payload, indent=2, ensure_ascii=False) + "\n").encode("utf-8"))

    def scans(self) -> tuple[dict, dict]:
        old = cmp1._Verification(self.home, cmp1.MODE_CANDIDATE, cmp1.RESULTS_POLICY_NONE, CANDIDATE_R2)
        old.pointer = load(CANDIDATE_R2)
        cmp1._check_roles(old, False)
        new = cmp2._Verification(self.home, cmp2.MODE_CANDIDATE, CANDIDATE_R3)
        new.pointer = self.base
        new.start(cmp2.CHECK_ROLES)
        cmp2._check_conflicting_pointers(new)
        return old.result(), new.result()

    def test_historical_v1_route_scan_is_clean_after_activation(self) -> None:
        for result in self.scans():
            self.assertNotIn("CONFLICTING_CURRENT_MAINLINE_CLAIM", result["failure_codes"])
            self.assertTrue(result["canonical_pointer_present"])

    def test_a_rival_claiming_candidate_is_caught_by_both_scans(self) -> None:
        rival = copy.deepcopy(self.base)
        rival["pointer_identity"]["is_current_authority"] = True
        self.write("configs/candidates/rival.json", rival)
        for result in self.scans():
            self.assertIn("CONFLICTING_CURRENT_MAINLINE_CLAIM", result["failure_codes"])


# ---------------------------------------------------------------------------
# EOL: raw bytes, Git blob bytes and anchor/HEAD blob ids stay separate axes
# ---------------------------------------------------------------------------


class EolAxisTests(unittest.TestCase):
    LF = b"line one\nline two\n"

    def setUp(self) -> None:
        self.home = Path(tempfile.mkdtemp(prefix="cmp2_eol_")).resolve()
        self.root = self.home / "repo"
        self.root.mkdir()
        empty = self.home / "empty_gitconfig"
        empty.write_bytes(b"")
        self.env = dict(
            os.environ,
            GIT_CONFIG_NOSYSTEM="1",
            GIT_CONFIG_GLOBAL=str(empty),
            GIT_OPTIONAL_LOCKS="0",
            GIT_TERMINAL_PROMPT="0",
            GIT_AUTHOR_NAME="fixture",
            GIT_AUTHOR_EMAIL="fixture@example.invalid",
            GIT_COMMITTER_NAME="fixture",
            GIT_COMMITTER_EMAIL="fixture@example.invalid",
        )
        self.git("init", "-q", "-b", "thesis-v7", ".")
        self.git("config", "core.autocrlf", "false")
        self.doc = self.root / "docs" / "doc.md"
        self.doc.parent.mkdir()
        self.doc.write_bytes(self.LF)
        self.git("add", "--", "docs/doc.md")
        self.git("commit", "-q", "-m", "fixture")
        self.anchor = self.git("rev-parse", "HEAD")

    def tearDown(self) -> None:
        shutil.rmtree(self.home, ignore_errors=True)

    def git(self, *args: str) -> str:
        done = subprocess.run(["git", *args], cwd=self.root, env=self.env, capture_output=True, check=False)
        if done.returncode != 0:
            raise AssertionError(f"git {args} failed: {done.stderr!r}")
        return done.stdout.decode("utf-8").strip()

    def check(self, sha256: str | None = None) -> dict:
        identity = {
            "path": "docs/doc.md",
            "sha256": sha256 or hashlib.sha256(self.LF).hexdigest(),
            "bytes": len(self.LF),
            "git_tracked": True,
            "git_blob_id": self.git("rev-parse", f"{self.anchor}:docs/doc.md"),
            "git_anchor_commit": self.anchor,
            "git_anchor_role": cmp1.ANCHOR_ADDED,
        }
        v = cmp2._Verification(self.root, cmp2.MODE_CANDIDATE, CANDIDATE_R3)
        v.pointer = {"methodology_authority": {"document": identity}}
        cmp1._check_files(v, True)
        return v.result()

    def test_lf_working_tree_matches_both_axes(self) -> None:
        result = self.check()
        self.assertEqual(result["failures"], [])
        self.assertEqual(result["checks"][cmp2.CHECK_FILES], cmp2.STATUS_PASS)

    def test_crlf_conversion_is_reported_and_fails_closed(self) -> None:
        self.doc.write_bytes(self.LF.replace(b"\n", b"\r\n"))
        result = self.check()
        self.assertEqual(result["verdict"], cmp2.VERDICT_FAIL_CLOSED)
        self.assertEqual(result["failure_codes"], ["RAW_BYTES_DIFFER_BY_EOL_CONVERSION_ONLY"])
        self.assertEqual(result["checks"][cmp2.CHECK_FILES], cmp2.STATUS_FAIL)

    def test_content_change_is_not_called_eol(self) -> None:
        self.doc.write_bytes(b"line one\nline 2\n")
        result = self.check()
        self.assertEqual(result["failure_codes"], ["RAW_BYTES_DIFFER_IN_CONTENT"])

    def test_recording_the_crlf_hash_fails_on_the_blob_axis(self) -> None:
        crlf = self.LF.replace(b"\n", b"\r\n")
        self.doc.write_bytes(crlf)
        result = self.check(hashlib.sha256(crlf).hexdigest())
        self.assertEqual(result["verdict"], cmp2.VERDICT_FAIL_CLOSED)
        self.assertIn("GIT_BLOB_BYTES_MISMATCH", result["failure_codes"])


# ---------------------------------------------------------------------------
# Zero execution: read-only Git only, no model, repository unchanged
# ---------------------------------------------------------------------------


def _snapshot() -> dict:
    head = (ROOT / ".git" / "HEAD").read_bytes()
    return {
        "index": hashlib.sha256((ROOT / ".git" / "index").read_bytes()).hexdigest(),
        "HEAD": head,
        "head_commit": cmp1._Git(ROOT).rev("HEAD"),
        "candidate_r3": hashlib.sha256((ROOT / CANDIDATE_R3).read_bytes()).hexdigest(),
        "canonical": hashlib.sha256((ROOT / CANONICAL).read_bytes()).hexdigest(),
        "v1": hashlib.sha256(V1_MODULE_PATH.read_bytes()).hexdigest(),
    }


class ZeroExecutionTests(unittest.TestCase):
    def test_verification_runs_only_read_only_git_and_builds_no_model(self) -> None:
        calls: list[list[str]] = []
        real_run = subprocess.run

        def recording_run(command: Any, *args: Any, **kwargs: Any) -> Any:
            calls.append(list(command))
            return real_run(command, *args, **kwargs)

        loaded_before = set(sys.modules)
        before = _snapshot()
        with mock.patch.object(subprocess, "run", recording_run):
            result = cmp2.verify_candidate_pointer(ROOT, CANDIDATE_R3)
        self.assertEqual(result["verdict"], cmp2.VERDICT_CANDIDATE_CONSISTENT, result["failure_codes"])
        self.assertTrue(calls)
        for command in calls:
            self.assertEqual(command[:3], ["git", "-c", "core.quotepath=false"], command)
            self.assertIn(command[3], cmp1._GIT_READ_ONLY_SUBCOMMANDS, command)
        new_modules = set(sys.modules) - loaded_before
        for module in new_modules:
            self.assertNotRegex(module, r"gurobi|pyomo|pulp|annual_design_model|production_|scripts")
        self.assertNotIn("gurobipy", sys.modules)
        self.assertEqual(_snapshot(), before)
        self.assertEqual(result["zero_execution_counters"], {
            "solver_library_imports": 0, "model_constructions": 0, "optimize_calls": 0,
            "files_written": 0, "git_write_subcommands": 0,
        })


if __name__ == "__main__":
    unittest.main()
