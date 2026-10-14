#!/usr/bin/env python3
"""ACC-N1 exposure-log prerequisite withdrawal: focused zero-solve tests.

What this suite proves
----------------------
* The accepted canonical pointer R1 still verifies and still blocks the three
  scientific purposes: nothing here activates the amendment.
* Pointer candidate R2 verifies as a candidate, and its payload differs from R1
  only in the ACC-N1 scientific-exposure routing.  Every identity binding,
  including the accepted Full81 G1 result set, is carried unchanged.
* Only a valid owner amendment withdraws ACC-N1's blocking flags.  An invalid,
  missing, altered or overreaching amendment lifts nothing and fails closed.
* The amendment keeps ACC-N1 OPEN, claims no exposure log, and carries U-01
  (OPEN / HOLD, frozen before every A2 event), the Full81-to-U-01 calibration
  prohibition and the A2 HARD BLOCK unchanged.
* Canonical mode serves the three purposes only after an audited, accepted,
  published activation that also accepts and publishes the amendment record.

Two layers, as in ``test_current_mainline_pointer_v1``
------------------------------------------------------
``Live*`` classes read the real repository.  They encode a LIVE PREMISE: R1 is
the canonical pointer and R2 is an unaccepted candidate.  Retire them with that
premise when R2 is activated; do not edit them until they pass.

``Fixture*`` classes are hermetic.  They reuse the synthetic repository of the
v1 suite and add a synthetic amendment record built from the fixture pointer.

ZERO SOLVE.  Nothing here imports a solver, a model or a production module.  No
test parses, prints or compares a case-level result value.
"""

from __future__ import annotations

import copy
import json
import subprocess
import sys
import unittest
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from typing import Any, Callable

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src import current_mainline_pointer_v1 as cmp  # noqa: E402
from tests import test_current_mainline_pointer_v1 as v1  # noqa: E402

CANDIDATE_R1 = v1.CANDIDATE
CANDIDATE_R2 = "configs/candidates/current_mainline_pointer_candidate_r2.json"
CANONICAL = cmp.CANONICAL_POINTER_RELATIVE_PATH
RECORD = (
    "results/provenance/acc_n1_exposure_log_prerequisite_withdrawal_candidate_r1/"
    "governance_amendment_record.json"
)
AMENDMENT_ID = "ACC_N1_EXPOSURE_LOG_PREREQUISITE_WITHDRAWAL_R1"
LIFTED = [cmp.PURPOSE_SCIENTIFIC_INSPECTION, cmp.PURPOSE_RESULTS_ANALYSIS, cmp.PURPOSE_SUPERVISOR_DISCUSSION]
LIFTED_ITEMS = [
    "DOWNSTREAM_LAYER_A_RESULTS_ANALYSIS_OR_SCIENTIFIC_INSPECTION",
    "SUPERVISOR_DISCUSSION_OF_FULL81_RESULTS_WITHOUT_AN_EXPOSURE_EVENT",
]
#: Payload locations R2 may change relative to R1.  Everything else is equal.
R2_CHANGED_TOP_LEVEL = {
    "pointer_revision",
    "documentation",
    "scientific_exposure_restrictions",
    "open_findings_and_limitations",
    "non_authorization_boundaries",
    "validation_contract",
}


def load(relative: str, root: Path = ROOT) -> dict:
    return json.loads(root.joinpath(*relative.split("/")).read_bytes().decode("utf-8"))


def payload(pointer: dict) -> dict:
    return {key: value for key, value in pointer.items() if key not in cmp.ENVELOPE_KEYS}


def acc_n1(pointer: dict) -> dict:
    return next(f for f in pointer["open_findings_and_limitations"]["findings"] if f["id"] == "ACC-N1")


def _r2_sweep_probe(path: tuple) -> tuple[tuple, bool]:
    """Mutate one leaf of the live R2 candidate; report whether the verifier noticed."""

    pointer = load(CANDIDATE_R2)
    node = pointer
    for key in path[:-1]:
        node = node[key]
    node[path[-1]] = v1._mutated_leaf(node[path[-1]])
    result = v1.verify_object(ROOT, pointer, relative=CANDIDATE_R2)
    return path, result["verdict"] == cmp.VERDICT_FAIL_CLOSED


# ---------------------------------------------------------------------------
# Synthetic amendment for the hermetic fixture
# ---------------------------------------------------------------------------


def amendment_record(pointer: dict) -> dict:
    """The fields the verifier checks, derived from a fixture pointer."""

    restrictions = pointer["scientific_exposure_restrictions"]
    acceptance = pointer["formal_results_acceptance"]["acceptance_closure"]
    u01 = pointer["open_findings_and_limitations"]["unresolved_register"]["U-01"]
    return {
        "artifact_type": cmp.AMENDMENT_ARTIFACT_TYPE,
        "schema_version": cmp.AMENDMENT_SCHEMA_VERSION,
        "amendment_id": AMENDMENT_ID,
        "lifecycle_state": "CANDIDATE",
        "self_accepted": False,
        "target_finding": {
            "id": "ACC-N1",
            "results_acceptance_closure": {"path": acceptance["path"], "sha256": acceptance["sha256"]},
        },
        "amended_clause": {
            "path": restrictions["governing_clause"]["path"],
            "sha256": restrictions["governing_clause"]["sha256"],
        },
        "effect": {
            "lifted_blocking_flags": list(cmp.CLOSURE_BLOCKING_FLAG_PURPOSES),
            "lifted_purposes": list(LIFTED),
            "lifted_non_authorization_items": list(LIFTED_ITEMS),
            "superseded_carry_forward_conditions": [
                c for c in restrictions["carry_forward_conditions"] if c.startswith("ACC-N1:")
            ],
            "scope": {
                "result_set_run_path": pointer["accepted_result_set"]["run_path"],
                "case_set": pointer["accepted_result_set"]["case_set"],
            },
        },
        "finding_status_after_amendment": {"closed": False, "remediated": False, "blocking": False},
        "exposure_log": {
            "established": False,
            "created_by_this_amendment": False,
            "retrospective_or_reconstructed_record_created": False,
        },
        "preserved_restrictions": {
            "u_01_status": u01["status"],
            "u_01_must_be_frozen_before": list(u01["must_be_frozen_before"]),
            "a2_variable_floor_status": pointer["non_authorization_boundaries"]["a2_variable_floor_status"],
            "full81_to_u01_calibration_prohibited": True,
            "u01_may_be_described_as_pre_full81_blinded": False,
            "main_full81_results_treated_as_exposed": True,
        },
        "is_exposure_log_or_exposure_event": False,
    }


def to_r2(pointer: dict, record_bytes: bytes, record: dict) -> dict:
    """The R1-shaped fixture pointer, revised the way the real R2 is."""

    revised = copy.deepcopy(pointer)
    revised["pointer_revision"] = "R2"
    revised["pointer_identity"].update(
        pointer_id="CURRENT_MAINLINE_POINTER_CANDIDATE_R2", this_file_path=CANDIDATE_R2
    )
    restrictions = revised["scientific_exposure_restrictions"]
    restrictions["blocked_purposes"] = []
    restrictions["permitted_purposes"] = [cmp.PURPOSE_TECHNICAL_IDENTITY_VERIFICATION, *LIFTED]
    restrictions["governance_amendments"] = [
        {
            "amendment_id": AMENDMENT_ID,
            "artifact_type": cmp.AMENDMENT_ARTIFACT_TYPE,
            "target_finding": "ACC-N1",
            "record_path": RECORD,
            "record_sha256": v1._sha(record_bytes),
            "record_bytes": len(record_bytes),
            "lifted_purposes": list(record["effect"]["lifted_purposes"]),
            "lifted_non_authorization_items": list(record["effect"]["lifted_non_authorization_items"]),
            "superseded_carry_forward_conditions": list(
                record["effect"]["superseded_carry_forward_conditions"]
            ),
        }
    ]
    acc_n1(revised)["blocks_purposes"] = []
    boundaries = revised["non_authorization_boundaries"]
    boundaries["not_authorized_by_this_pointer"] = [
        item for item in boundaries["not_authorized_by_this_pointer"] if item not in LIFTED_ITEMS
    ]
    return revised


def write_r2(fixture: v1.Fixture, record: dict | None = None) -> dict:
    """Write an amendment record and an R2 candidate binding it; return the candidate."""

    record = amendment_record(fixture.pointer) if record is None else record
    data = v1._json_bytes(record)
    fixture.write(RECORD, data)
    candidate = to_r2(fixture.pointer, data, record)
    fixture.write_pointer(CANDIDATE_R2, candidate)
    return candidate


def activate_r2(
    fixture: v1.Fixture,
    *,
    accept_amendment: bool = True,
    commit_record: bool = True,
) -> dict:
    """Publish R2 the proposed way: candidate (+ record), audit, acceptance, canonical."""

    candidate_bytes = fixture.path(CANDIDATE_R2).read_bytes()
    candidate = json.loads(candidate_bytes.decode("utf-8"))
    digest = cmp.pointer_payload_digest(candidate)
    commit_candidate = fixture.commit(
        "pointer candidate R2 and amendment", [CANDIDATE_R2, *([RECORD] if commit_record else [])]
    )
    accepted_candidate = {"path": CANDIDATE_R2, "sha256": v1._sha(candidate_bytes)}
    fixture.write(
        v1.ACTIVATION_AUDIT,
        v1._json_bytes(
            {
                "artifact_type": cmp.ACTIVATION_AUDIT_ARTIFACT_TYPE,
                "verdict": "PASS",
                "self_audit": False,
                "audited_candidate": accepted_candidate,
                "audited_payload_digest": digest,
            }
        ),
    )
    commit_audit = fixture.commit("pointer R2 independent audit", [v1.ACTIVATION_AUDIT])
    entry = candidate["scientific_exposure_restrictions"]["governance_amendments"][0]
    closure: dict = {
        "artifact_type": cmp.ACTIVATION_CLOSURE_ARTIFACT_TYPE,
        "acceptance_status": "CLOSED_ACCEPTED",
        "canonical_pointer_path": CANONICAL,
        "accepted_candidate": accepted_candidate,
        "accepted_payload_digest": digest,
        "independent_audit_record": fixture.identity(v1.ACTIVATION_AUDIT, commit_audit),
    }
    if accept_amendment:
        closure["accepted_governance_amendments"] = [
            {"amendment_id": entry["amendment_id"], "path": entry["record_path"], "sha256": entry["record_sha256"]}
        ]
    fixture.write(v1.ACTIVATION_CLOSURE, v1._json_bytes(closure))
    fixture.write(
        v1.ACTIVATION_MANIFEST,
        v1._json_bytes(
            {
                "artifact_type": cmp.ACTIVATION_MANIFEST_ARTIFACT_TYPE,
                "acceptance_closure": {
                    "path": v1.ACTIVATION_CLOSURE,
                    "sha256": v1._sha(fixture.path(v1.ACTIVATION_CLOSURE).read_bytes()),
                },
            }
        ),
    )
    commit_acceptance = fixture.commit(
        "pointer R2 acceptance", [v1.ACTIVATION_CLOSURE, v1.ACTIVATION_MANIFEST]
    )
    canonical = copy.deepcopy(candidate)
    canonical["pointer_identity"] = {
        "pointer_id": "CURRENT_MAINLINE_POINTER_R2",
        "lifecycle": "ACCEPTED / CANONICAL / CURRENT AUTHORITY",
        "lifecycle_state": cmp.LIFECYCLE_CANONICAL,
        "is_candidate": False,
        "is_accepted": True,
        "is_canonical": True,
        "is_current_authority": True,
        "self_accepted": False,
        "this_file_path": CANONICAL,
        "proposed_canonical_path": CANONICAL,
    }
    canonical["activation_basis"] = {
        "status": cmp.ACTIVATION_ACCEPTED_PUBLISHED,
        "audited_candidate": fixture.identity(CANDIDATE_R2, commit_candidate),
        "independent_audit_record": fixture.identity(v1.ACTIVATION_AUDIT, commit_audit),
        "acceptance_closure": fixture.identity(v1.ACTIVATION_CLOSURE, commit_acceptance),
        "acceptance_manifest": fixture.identity(v1.ACTIVATION_MANIFEST, commit_acceptance),
    }
    fixture.write_pointer(CANONICAL, canonical)
    fixture.commit("canonical pointer R2", [CANONICAL])
    fixture.publish()
    return canonical


class AmendmentCase(v1.VerifierCase):
    def assertLiftsNothing(self, result: dict, *codes: str) -> None:
        """An invalid amendment fails closed and the ACC-N1 restriction is enforced."""

        self.assertFailsClosed(result, "SCIENTIFIC_EXPOSURE_RESTRICTION_WEAKENED", *codes)
        for report in result.get("governance_amendments", []):
            self.assertFalse(report["valid"])


# ---------------------------------------------------------------------------
# Static
# ---------------------------------------------------------------------------


class AmendmentInterfaceTests(unittest.TestCase):
    def test_only_exposure_derived_boundaries_are_liftable(self) -> None:
        self.assertEqual(cmp.AMENDMENT_LIFTABLE_NON_AUTHORIZATIONS, frozenset(LIFTED_ITEMS))
        self.assertFalse(cmp.AMENDMENT_LIFTABLE_NON_AUTHORIZATIONS & set(cmp.POINTER_OWN_NON_AUTHORIZATIONS))
        for item in cmp.AMENDMENT_LIFTABLE_NON_AUTHORIZATIONS:
            for never in ("A2", "U_01", "SOLVER", "EXECUTION", "RERUN", "AGGREGATION", "EXPOSURE_LOG_CREATION"):
                self.assertNotIn(never, item)

    def test_no_new_check_and_no_new_purpose(self) -> None:
        """The extension adds neither a check id nor a consumption purpose."""

        self.assertEqual(len(cmp.CHECK_IDS), 13)
        self.assertEqual(
            set(cmp.KNOWN_PURPOSES),
            {cmp.PURPOSE_TECHNICAL_IDENTITY_VERIFICATION, *LIFTED},
        )
        self.assertEqual(cmp.INTERFACE_VERSION, "iris-thesis-current-mainline-pointer-verifier-v1")


# ---------------------------------------------------------------------------
# Live: the real repository
# ---------------------------------------------------------------------------


class LiveAmendmentTests(AmendmentCase):
    """LIVE PREMISE: R1 is canonical and R2 is an unaccepted candidate."""

    @classmethod
    def setUpClass(cls) -> None:
        for relative in (CANDIDATE_R2, RECORD, CANONICAL):
            if not (ROOT / relative).is_file():
                raise unittest.SkipTest(f"{relative} is absent")
        cls.r1 = load(CANONICAL)
        cls.r2 = load(CANDIDATE_R2)
        cls.record = load(RECORD)
        cls.result = cmp.verify_candidate_pointer(ROOT, CANDIDATE_R2)

    def mutated(self, change: Callable[[dict], Any]) -> dict:
        pointer = copy.deepcopy(self.r2)
        change(pointer)
        return v1.verify_object(ROOT, pointer, relative=CANDIDATE_R2)

    def test_canonical_r1_is_unchanged_and_still_blocks(self) -> None:
        result = cmp.verify_canonical_pointer(ROOT)
        self.assertEqual(result["failures"], [])
        self.assertEqual(result["verdict"], cmp.VERDICT_CANONICAL_VERIFIED)
        self.assertEqual(result["scientific_exposure"]["blocked_purposes"], LIFTED)
        self.assertNotIn("governance_amendments", result["scientific_exposure"])
        self.assertNotIn("governance_amendments", result)
        self.assertEqual(self.r1["pointer_revision"], "R1")
        self.assertEqual(
            cmp.pointer_payload_digest(self.r1), cmp.pointer_payload_digest(load(CANDIDATE_R1))
        )
        for purpose in LIFTED:
            with self.subTest(purpose=purpose), self.assertRaises(cmp.CurrentMainlinePointerError) as caught:
                cmp.require_current_mainline(ROOT, purpose=purpose, results_policy=cmp.RESULTS_POLICY_NONE)
            self.assertEqual(caught.exception.code, "PURPOSE_BLOCKED_BY_SCIENTIFIC_EXPOSURE_RESTRICTION")

    def test_r2_candidate_is_internally_consistent_and_nothing_more(self) -> None:
        self.assertCandidateConsistent(self.result)
        exposure = self.result["scientific_exposure"]
        self.assertEqual(exposure["blocked_purposes"], [])
        self.assertEqual(exposure["permitted_purposes"], [cmp.PURPOSE_TECHNICAL_IDENTITY_VERIFICATION, *LIFTED])
        self.assertEqual(exposure["governance_amendments"], [AMENDMENT_ID])
        self.assertIs(exposure["exposure_log_established"], False)
        self.assertEqual(
            [(r["amendment_id"], r["record_path"], r["valid"]) for r in self.result["governance_amendments"]],
            [(AMENDMENT_ID, RECORD, True)],
        )
        identity = self.r2["pointer_identity"]
        self.assertEqual(
            (identity["lifecycle_state"], identity["is_candidate"], identity["is_accepted"],
             identity["is_canonical"], identity["is_current_authority"], identity["self_accepted"]),
            (cmp.LIFECYCLE_CANDIDATE, True, False, False, False, False),
        )
        self.assertEqual(self.r2["activation_basis"]["status"], cmp.ACTIVATION_NOT_ACTIVATED)

    def test_r2_payload_differs_from_r1_only_in_acc_n1_routing(self) -> None:
        old, new = payload(self.r1), payload(self.r2)
        self.assertEqual(set(old), set(new))
        for key in sorted(set(old) - R2_CHANGED_TOP_LEVEL):
            with self.subTest(section=key):
                self.assertEqual(new[key], old[key])
        self.assertEqual(new["pointer_revision"], "R2")
        self.assertEqual(
            {k: v for k, v in new["documentation"].items() if k != "revision_note"}, old["documentation"]
        )
        old_r, new_r = old["scientific_exposure_restrictions"], new["scientific_exposure_restrictions"]
        for key in ("governing_finding", "governing_clause", "carry_forward_conditions", "verifier_output_note"):
            self.assertEqual(new_r[key], old_r[key], key)
        self.assertEqual(
            {k: v for k, v in new_r["exposure_log"].items() if k != "note"},
            {k: v for k, v in old_r["exposure_log"].items() if k != "note"},
        )
        self.assertEqual(old_r["blocked_purposes"], LIFTED)
        self.assertEqual(new_r["blocked_purposes"], [])
        old_f, new_f = old["open_findings_and_limitations"], new["open_findings_and_limitations"]
        self.assertEqual(
            {k: v for k, v in new_f.items() if k != "findings"},
            {k: v for k, v in old_f.items() if k != "findings"},
        )
        self.assertEqual([f["id"] for f in new_f["findings"]], [f["id"] for f in old_f["findings"]])
        for before, after in zip(old_f["findings"], new_f["findings"]):
            if before["id"] != "ACC-N1":
                self.assertEqual(after, before)
        before, after = acc_n1(old), acc_n1(new)
        self.assertEqual(
            {k: v for k, v in after.items() if k not in ("blocks_purposes", "blocking_note")},
            {k: v for k, v in before.items() if k != "blocks_purposes"},
        )
        self.assertEqual((before["blocks_purposes"], after["blocks_purposes"]), (LIFTED, []))
        self.assertEqual((after["severity"], after["disposition"], after["closed"]), ("MAJOR", "OPEN", False))
        old_b, new_b = old["non_authorization_boundaries"], new["non_authorization_boundaries"]
        self.assertEqual(
            new_b["not_authorized_by_this_pointer"],
            [item for item in old_b["not_authorized_by_this_pointer"] if item not in LIFTED_ITEMS],
        )
        self.assertEqual(
            {k: v for k, v in new_b.items() if k not in ("not_authorized_by_this_pointer", "lifted_by_governance_amendment_note")},
            {k: v for k, v in old_b.items() if k != "not_authorized_by_this_pointer"},
        )
        self.assertEqual(
            {k: v for k, v in new["validation_contract"].items() if k != "documentation"},
            {k: v for k, v in old["validation_contract"].items() if k != "documentation"},
        )

    def test_accepted_full81_identity_is_unchanged_and_strictly_verified(self) -> None:
        """Hashes the 651 result files as opaque bytes; reads no result value."""

        for section in ("accepted_result_set", "formal_results_acceptance", "production_generation",
                        "methodology_authority", "evidence_authority", "implementation",
                        "canonical_annual_input", "economic_parameter_interfaces", "git_provenance"):
            self.assertEqual(self.r2[section], self.r1[section], section)
        if not (ROOT / self.r2["accepted_result_set"]["run_path"]).is_dir():
            self.skipTest("the local result files are absent")
        strict = cmp.verify_candidate_pointer(ROOT, CANDIDATE_R2, results_policy=cmp.RESULTS_POLICY_STRICT)
        self.assertCandidateConsistent(strict)
        self.assertEqual(strict["results_integrity"], cmp.RESULTS_STRICT_PASS)
        self.assertEqual(strict["zero_execution_counters"]["optimize_calls"], 0)

    def test_amendment_record_preserves_what_must_be_preserved(self) -> None:
        record = self.record
        self.assertEqual((record["lifecycle_state"], record["self_accepted"]), ("CANDIDATE", False))
        self.assertIs(record["is_exposure_log_or_exposure_event"], False)
        self.assertEqual(record["finding_status_after_amendment"]["closed"], False)
        self.assertEqual(record["finding_status_after_amendment"]["remediated"], False)
        self.assertEqual(set(record["exposure_log"].values()) - {record["exposure_log"]["statement"]}, {False})
        preserved = record["preserved_restrictions"]
        register = self.r1["open_findings_and_limitations"]["unresolved_register"]["U-01"]
        self.assertEqual(preserved["u_01_status"], "OPEN_HOLD")
        self.assertEqual(preserved["u_01_must_be_frozen_before"], register["must_be_frozen_before"])
        self.assertEqual(
            preserved["u_01_must_be_frozen_before"],
            ["A2_EXECUTION", "A2_RESULT_EXPOSURE", "A2_INTERPRETATION", "A2_CONDITIONAL_EXTENSION_AUTHORIZATION"],
        )
        self.assertTrue(preserved["a2_variable_floor_status"].startswith("HARD_BLOCKED"))
        self.assertIs(preserved["full81_to_u01_calibration_prohibited"], True)
        self.assertIs(preserved["u01_may_be_described_as_pre_full81_blinded"], False)
        self.assertIs(preserved["main_full81_results_treated_as_exposed"], True)
        conditions = self.r1["scientific_exposure_restrictions"]["carry_forward_conditions"]
        superseded = record["effect"]["superseded_carry_forward_conditions"]
        self.assertEqual(superseded, [conditions[0]])
        self.assertTrue(all(c.startswith("ACC-N1:") for c in superseded))
        self.assertTrue(any("U-01" in c and "A2" in c for c in conditions[1:]))
        self.assertEqual(record["amended_clause"]["sections_amended"], ["13"])
        self.assertEqual(record["amended_clause"]["sections_retained_unchanged"], ["8", "11", "12"])
        for item in ("A2_EXECUTION_EXPOSURE_OR_INTERPRETATION", "U_01_RESOLUTION_OR_CALIBRATION",
                     "ANY_SOLVER_CALL_MODEL_CONSTRUCTION_OR_PRODUCTION_RUN", "EXPOSURE_LOG_CREATION",
                     "SELF_ACCEPTANCE"):
            self.assertIn(item, record["not_authorized_by_this_record"])

    def test_negative_controls_on_the_live_candidate(self) -> None:
        entry = ("scientific_exposure_restrictions", "governance_amendments", 0)

        def at(keys: tuple, value: Any) -> Callable[[dict], Any]:
            return lambda p: v1._set(p, keys, value)

        u01_condition = self.r2["scientific_exposure_restrictions"]["carry_forward_conditions"][1]
        cases = {
            "amendment dropped": (
                lambda p: p["scientific_exposure_restrictions"].pop("governance_amendments"),
                ("SCIENTIFIC_EXPOSURE_RESTRICTION_WEAKENED", "NON_AUTHORIZATION_BOUNDARY_DROPPED"),
            ),
            "record hash altered": (at((*entry, "record_sha256"), "c" * 64), ("AMENDMENT_RECORD_IDENTITY_MISMATCH",)),
            "record size altered": (at((*entry, "record_bytes"), 1), ("AMENDMENT_RECORD_IDENTITY_MISMATCH",)),
            "record swapped": (
                at((*entry, "record_path"), self.r2["formal_results_acceptance"]["acceptance_closure"]["path"]),
                ("AMENDMENT_RECORD_IDENTITY_MISMATCH",),
            ),
            "technical purpose lifted": (
                at((*entry, "lifted_purposes"), [*LIFTED, cmp.PURPOSE_TECHNICAL_IDENTITY_VERIFICATION]),
                ("AMENDMENT_INVALID",),
            ),
            "A2 boundary lifted": (
                at((*entry, "lifted_non_authorization_items"), [*LIFTED_ITEMS, "A2_LAYER_B_DG_OR_SENSITIVITY"]),
                ("AMENDMENT_INVALID",),
            ),
            "U-01 condition superseded": (
                at((*entry, "superseded_carry_forward_conditions"),
                   [self.r2["scientific_exposure_restrictions"]["carry_forward_conditions"][0], u01_condition]),
                ("AMENDMENT_INVALID",),
            ),
            "another finding targeted": (at((*entry, "target_finding"), "G1-N2"), ("AMENDMENT_INVALID",)),
            "artifact type": (at((*entry, "artifact_type"), "OWNER_NOTE"), ("AMENDMENT_INVALID",)),
            "amendment bound twice": (
                lambda p: p["scientific_exposure_restrictions"]["governance_amendments"].append(
                    copy.deepcopy(p["scientific_exposure_restrictions"]["governance_amendments"][0])),
                ("AMENDMENT_INVALID",),
            ),
        }
        for name, (change, codes) in cases.items():
            with self.subTest(name):
                self.assertLiftsNothing(self.mutated(change), *codes)

        def edit_acc_n1(**fields: Any) -> Callable[[dict], Any]:
            return lambda p: acc_n1(p).update(fields)

        self.assertFailsClosed(self.mutated(edit_acc_n1(closed=True)), "FINDING_CLOSED_WITHOUT_EVIDENCE", "AMENDMENT_INVALID")
        self.assertFailsClosed(
            self.mutated(edit_acc_n1(disposition="CLOSED")), "FINDING_SEVERITY_OR_DISPOSITION_ALTERED"
        )
        self.assertFailsClosed(
            self.mutated(lambda p: p["scientific_exposure_restrictions"]["exposure_log"].update(
                established=True, path="results/provenance/exposure_log.json")),
            "EXPOSURE_LOG_CLAIMED_WHILE_FINDING_OPEN",
        )
        self.assertFailsClosed(
            self.mutated(at(("open_findings_and_limitations", "unresolved_register", "U-01", "status"), "RESOLVED")),
            "CROSS_BINDING_MISMATCH", "AMENDMENT_INVALID",
        )
        self.assertFailsClosed(
            self.mutated(lambda p: p["open_findings_and_limitations"]["unresolved_register"]["U-01"][
                "must_be_frozen_before"].remove("A2_EXECUTION")),
            "CROSS_BINDING_MISMATCH", "AMENDMENT_INVALID",
        )
        self.assertFailsClosed(
            self.mutated(at(("non_authorization_boundaries", "a2_variable_floor_status"), "AUTHORIZED")),
            "CROSS_BINDING_MISMATCH", "AMENDMENT_INVALID",
        )
        self.assertFailsClosed(
            self.mutated(lambda p: p["non_authorization_boundaries"]["not_authorized_by_this_pointer"].remove(
                "A2_LAYER_B_DG_OR_SENSITIVITY")),
            "NON_AUTHORIZATION_BOUNDARY_DROPPED",
        )
        self.assertFailsClosed(
            self.mutated(lambda p: p["non_authorization_boundaries"]["not_authorized_by_this_pointer"].remove(
                "U_01_RESOLUTION_OR_CALIBRATION")),
            "NON_AUTHORIZATION_BOUNDARY_DROPPED",
        )
        self.assertFailsClosed(
            self.mutated(lambda p: p["non_authorization_boundaries"]["not_authorized_by_this_pointer"].append(
                LIFTED_ITEMS[0])),
            "NON_AUTHORIZATION_BOUNDARY_UNKNOWN",
        )

        def unapplied(p: dict) -> None:
            p["scientific_exposure_restrictions"]["blocked_purposes"] = list(LIFTED)
            p["scientific_exposure_restrictions"]["permitted_purposes"] = [cmp.PURPOSE_TECHNICAL_IDENTITY_VERIFICATION]

        self.assertFailsClosed(self.mutated(unapplied), "AMENDMENT_NOT_APPLIED")
        self.assertFailsClosed(
            self.mutated(edit_acc_n1(blocks_purposes=list(LIFTED))),
            "AMENDMENT_NOT_APPLIED", "OPEN_FINDING_RESTRICTION_NOT_ENFORCED",
        )
        self.assertFailsClosed(
            self.mutated(lambda p: p["scientific_exposure_restrictions"]["permitted_purposes"].append("A2")),
            "UNKNOWN_PURPOSE",
        )
        self.assertFailsClosed(
            self.mutated(lambda p: p["scientific_exposure_restrictions"]["carry_forward_conditions"].pop(0)),
            "CROSS_BINDING_MISMATCH",
        )
        for malformed in ([], {}, [{"amendment_id": AMENDMENT_ID}]):
            with self.subTest(malformed=malformed):
                self.assertFailsClosed(
                    self.mutated(at(("scientific_exposure_restrictions", "governance_amendments"), malformed)),
                    "SCHEMA_VIOLATION",
                )

    def test_every_revised_leaf_is_verified_or_explicitly_descriptive(self) -> None:
        """One mutation per non-descriptive leaf of every section R2 revises."""

        sections = ("scientific_exposure_restrictions", "open_findings_and_limitations", "non_authorization_boundaries")
        targets = [
            path
            for path, _value in v1._leaves(payload(self.r2))
            if path[0] in sections and not any(cmp.is_descriptive_key(key) for key in path)
        ]
        with ProcessPoolExecutor(max_workers=6) as pool:
            outcomes = dict(pool.map(_r2_sweep_probe, targets, chunksize=8))
        self.assertEqual(sorted((p for p, noticed in outcomes.items() if not noticed), key=str), [])
        self.assertGreater(len(targets), 150)

    def test_no_solver_or_production_module_is_loaded(self) -> None:
        script = (
            "import sys; sys.path.insert(0, sys.argv[1]);"
            "from src import current_mainline_pointer_v1 as cmp;"
            "r = cmp.verify_candidate_pointer(sys.argv[1], sys.argv[2]);"
            "bad = sorted(m for m in sys.modules if m.split('.')[0] in sys.argv[3].split(',') "
            "or m.startswith(('src.production', 'src.annual_design')));"
            "print(r['verdict'], ','.join(bad))"
        )
        done = subprocess.run(
            [sys.executable, "-B", "-c", script, str(ROOT), CANDIDATE_R2, ",".join(v1.FORBIDDEN_RUNTIME_MODULES)],
            capture_output=True, check=True, cwd=ROOT,
        )
        self.assertEqual(done.stdout.decode().split(), [cmp.VERDICT_CANDIDATE_CONSISTENT])


# ---------------------------------------------------------------------------
# Hermetic fixture layer
# ---------------------------------------------------------------------------


class FixtureAmendmentTests(AmendmentCase, v1.FixtureCase):
    def test_a_valid_amendment_makes_a_consistent_candidate(self) -> None:
        fixture = self.fresh()
        write_r2(fixture)
        result = cmp.verify_candidate_pointer(fixture.root, CANDIDATE_R2)
        self.assertCandidateConsistent(result)
        self.assertEqual(result["scientific_exposure"]["blocked_purposes"], [])
        self.assertEqual([r["valid"] for r in result["governance_amendments"]], [True])
        # The R1-shaped candidate beside it still verifies and still blocks.
        r1 = self.candidate(fixture)
        self.assertCandidateConsistent(r1)
        self.assertEqual(r1["scientific_exposure"]["blocked_purposes"], LIFTED)

    def test_content_attacks_lift_nothing(self) -> None:
        """Every checked field of the record is load-bearing, even with a correct hash binding."""

        attacks = {
            ("finding_status_after_amendment", "closed"): True,
            ("finding_status_after_amendment", "remediated"): True,
            ("exposure_log", "established"): True,
            ("exposure_log", "created_by_this_amendment"): True,
            ("exposure_log", "retrospective_or_reconstructed_record_created"): True,
            ("self_accepted",): True,
            ("is_exposure_log_or_exposure_event",): True,
            ("preserved_restrictions", "u_01_status"): "RESOLVED",
            ("preserved_restrictions", "u_01_must_be_frozen_before"): ["A2_INTERPRETATION"],
            ("preserved_restrictions", "a2_variable_floor_status"): "AUTHORIZED",
            ("preserved_restrictions", "full81_to_u01_calibration_prohibited"): False,
            ("preserved_restrictions", "u01_may_be_described_as_pre_full81_blinded"): True,
            ("preserved_restrictions", "main_full81_results_treated_as_exposed"): False,
            ("effect", "lifted_blocking_flags"): ["blocking_for_an_unknown_flag"],
            ("effect", "scope", "result_set_run_path"): "results/layer_a/final_81/runs/other",
            ("effect", "scope", "case_set"): "core3",
            ("target_finding", "id"): "G1-N2",
            ("target_finding", "results_acceptance_closure", "sha256"): "d" * 64,
            ("amended_clause", "sha256"): "e" * 64,
            ("artifact_type",): "OWNER_NOTE",
            ("schema_version",): "v0",
            ("amendment_id",): "SOMETHING_ELSE",
        }
        for keys, value in attacks.items():
            with self.subTest(field=".".join(keys)):
                fixture = self.fresh()
                record = amendment_record(fixture.pointer)
                v1._set(record, keys, value)
                write_r2(fixture, record)
                self.assertLiftsNothing(cmp.verify_candidate_pointer(fixture.root, CANDIDATE_R2), "AMENDMENT_INVALID")

    def test_a_record_that_lifts_more_than_its_flags_lifts_nothing(self) -> None:
        fixture = self.fresh()
        record = amendment_record(fixture.pointer)
        record["effect"]["lifted_blocking_flags"] = ["blocking_for_first_scientific_inspection_of_full81_results"]
        write_r2(fixture, record)
        self.assertLiftsNothing(cmp.verify_candidate_pointer(fixture.root, CANDIDATE_R2), "AMENDMENT_INVALID")

    def test_an_activated_amendment_serves_the_three_purposes(self) -> None:
        fixture = self.fresh()
        write_r2(fixture)
        canonical = activate_r2(fixture)
        result = cmp.verify_canonical_pointer(fixture.root, results_policy=cmp.RESULTS_POLICY_STRICT)
        self.assertEqual(result["failures"], [])
        self.assertEqual(result["verdict"], cmp.VERDICT_CANONICAL_VERIFIED)
        self.assertTrue(result["results_consumption_permitted"])
        self.assertEqual(result["checks"][cmp.CHECK_ACTIVATION], cmp.STATUS_PASS)
        for purpose in (cmp.PURPOSE_TECHNICAL_IDENTITY_VERIFICATION, *LIFTED):
            with self.subTest(purpose=purpose):
                route = cmp.require_current_mainline(fixture.root, purpose=purpose)
                self.assertEqual(route["accepted_result_run_path"], canonical["accepted_result_set"]["run_path"])
                self.assertFalse(route["grants_execution_authority"])
        for purpose in ("FULL81_EXECUTION", "A2", "LAYER_B", "U_01_CALIBRATION", ""):
            with self.subTest(purpose=purpose), self.assertRaises(cmp.CurrentMainlinePointerError) as caught:
                cmp.require_current_mainline(fixture.root, purpose=purpose)
            self.assertEqual(caught.exception.code, "PURPOSE_NOT_PERMITTED")

    def test_an_unaccepted_amendment_is_refused_in_canonical_mode(self) -> None:
        fixture = self.fresh()
        write_r2(fixture)
        activate_r2(fixture, accept_amendment=False)
        result = cmp.verify_canonical_pointer(fixture.root, results_policy=cmp.RESULTS_POLICY_NONE)
        self.assertFailsClosed(result, "ACTIVATION_AMENDMENT_NOT_ACCEPTED")
        with self.assertRaises(cmp.CurrentMainlinePointerError):
            cmp.require_current_mainline(fixture.root, purpose=cmp.PURPOSE_RESULTS_ANALYSIS)

    def test_an_unpublished_amendment_is_refused_in_canonical_mode(self) -> None:
        with self.subTest("never committed"):
            fixture = self.fresh()
            write_r2(fixture)
            activate_r2(fixture, commit_record=False)
            self.assertFailsClosed(
                cmp.verify_canonical_pointer(fixture.root, results_policy=cmp.RESULTS_POLICY_NONE),
                "ACTIVATION_AMENDMENT_NOT_PUBLISHED",
            )
        with self.subTest("committed but not pushed"):
            fixture = self.fresh()
            published = fixture.git("rev-parse", "HEAD")
            write_r2(fixture)
            activate_r2(fixture)
            fixture.git("update-ref", "refs/remotes/origin/thesis-v7", published)
            self.assertFailsClosed(
                cmp.verify_canonical_pointer(fixture.root, results_policy=cmp.RESULTS_POLICY_NONE),
                "ACTIVATION_AMENDMENT_NOT_PUBLISHED",
            )
        with self.subTest("changed after acceptance"):
            fixture = self.fresh()
            write_r2(fixture)
            activate_r2(fixture)
            record = amendment_record(fixture.pointer)
            record["later_edit"] = "rewritten after acceptance"
            fixture.write(RECORD, v1._json_bytes(record))
            fixture.commit("rewrite the amendment", [RECORD])
            fixture.publish()
            result = cmp.verify_canonical_pointer(fixture.root, results_policy=cmp.RESULTS_POLICY_NONE)
            self.assertLiftsNothing(
                result, "AMENDMENT_RECORD_IDENTITY_MISMATCH", "ACTIVATION_AMENDMENT_NOT_PUBLISHED"
            )


if __name__ == "__main__":
    unittest.main(verbosity=2)
