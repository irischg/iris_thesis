#!/usr/bin/env python3
"""Current-mainline pointer verifier (interface v1): focused zero-solve tests.

What this suite proves
----------------------
* The verifier is read-only by construction: standard library only, no solver
  import, no file write, read-only Git subcommands only, no identity literal.
* A candidate that verifies is reported as internally consistent and nothing
  more: it is never promoted, never accepted and never confers authority.
* Canonical mode looks only at the canonical path and fails closed when the
  pointer there is absent, candidate-only, unpublished, mismatched or stale.
* Every bound identity is load-bearing: a wrong Framework, Registry, annual
  input, production generation, run id, results-acceptance reference, Git
  commit or Git blob fails closed.
* A historical-only or stale result namespace cannot become current, and no
  path can leave the repository.
* Results consumption needs strict verification of the local result
  registrations; a metadata check is never reported as full integrity.
* Later commits that preserve every accepted identity do not invalidate the
  historical source commits.
* The scientific-exposure restrictions stay explicit and cannot be dropped.

Two layers
----------
``Live*`` classes read the real repository and the real candidate pointer, and
apply negative controls to an in-memory copy of that pointer.  They encode a
LIVE PREMISE: the repository state bound by Candidate R1 is the live state.
When a later accepted pointer revision supersedes R1 they are to be retired
with it, not edited until they pass.

``Fixture*`` classes are hermetic.  They build a throwaway Git repository under
the system temp directory out of synthetic bytes, shaped by the real candidate
pointer used only as a schema template.  It shares nothing with the real
repository: no alternates, no real result byte, no real commit.

ZERO SOLVE.  Nothing here imports a solver, a model or a production module, and
no production script is invoked.  No test parses, prints or compares a
case-level result value; real result files are only hashed as opaque bytes.
"""

from __future__ import annotations

import ast
import copy
import hashlib
import json
import os
import re
import shutil
import stat
import subprocess
import sys
import tempfile
import unittest
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from typing import Any, Callable, Iterator


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src import current_mainline_pointer_v1 as cmp  # noqa: E402

MODULE_PATH = ROOT / "src" / "current_mainline_pointer_v1.py"
CANDIDATE = "configs/candidates/current_mainline_pointer_candidate_r1.json"
CANONICAL = cmp.CANONICAL_POINTER_RELATIVE_PATH
ACTIVATION_AUDIT = (
    "results/provenance/current_mainline_pointer_independent_audit_r1/independent_audit_record.json"
)
ACTIVATION_CLOSURE = (
    "results/provenance/current_mainline_pointer_acceptance_r1/acceptance_closure.json"
)
ACTIVATION_MANIFEST = (
    "results/provenance/current_mainline_pointer_acceptance_r1/acceptance_manifest.json"
)
CASE_FILE_NAMES = (
    "billing_exact.csv",
    "case_definition.json",
    "dispatch.csv",
    "mandatory_audits.json",
    "result.json",
    "solver_settings.json",
    "transition_settlement_detail.csv",
)
STDLIB_ALLOWLIST = {
    "__future__",
    "argparse",
    "hashlib",
    "json",
    "os",
    "pathlib",
    "re",
    "subprocess",
    "sys",
    "typing",
}
FORBIDDEN_RUNTIME_MODULES = ("gurobipy", "numpy", "pandas", "scipy", "pyomo", "pyarrow")


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _json_bytes(payload: Any) -> bytes:
    return (json.dumps(payload, indent=2, ensure_ascii=False) + "\n").encode("utf-8")


def _set(node: Any, keys: tuple, value: Any) -> None:
    """Assign ``value`` at ``keys`` inside ``node``, creating dicts and lists."""

    for index, key in enumerate(keys[:-1]):
        following = keys[index + 1]
        if isinstance(key, int):
            while len(node) <= key:
                node.append(None)
            if node[key] is None:
                node[key] = [] if isinstance(following, int) else {}
            node = node[key]
        else:
            node = node.setdefault(key, [] if isinstance(following, int) else {})
    last = keys[-1]
    if isinstance(last, int):
        while len(node) <= last:
            node.append(None)
    node[last] = value


def record_from_bindings(pointer: dict, record: str) -> dict:
    """The smallest record that satisfies every cross-binding row for ``record``."""

    payload: dict = {}
    for name, keys, expected in cmp.CROSS_BINDINGS:
        if name != record:
            continue
        if isinstance(expected, cmp._Literal):
            value = expected.value
        else:
            value = cmp._lookup(pointer, expected)
        assert value is not cmp._MISSING, (record, keys, expected)
        _set(payload, keys, copy.deepcopy(value))
    return payload


def load_live_candidate() -> dict:
    return json.loads((ROOT / CANDIDATE).read_bytes().decode("utf-8"))


def _leaves(node: Any, path: tuple = ()) -> Iterator[tuple[tuple, Any]]:
    if isinstance(node, dict):
        for key, value in node.items():
            yield from _leaves(value, (*path, key))
    elif isinstance(node, list):
        for index, value in enumerate(node):
            yield from _leaves(value, (*path, index))
    else:
        yield path, node


def _mutated_leaf(value: Any) -> Any:
    if value is None:
        return "x"
    if isinstance(value, bool):
        return not value
    if isinstance(value, int):
        return value + 1
    if isinstance(value, float):
        return value + 0.01
    if re.fullmatch(r"[0-9a-f]{40}|[0-9a-f]{64}", value):
        return value[:-1] + ("0" if value[-1] != "0" else "1")
    return value + "x"


def _sweep_probe(path: tuple) -> tuple[tuple, bool]:
    """Mutate one leaf of the live candidate; report whether the verifier noticed."""

    pointer = load_live_candidate()
    node = pointer
    for key in path[:-1]:
        node = node[key]
    node[path[-1]] = _mutated_leaf(node[path[-1]])
    result = cmp._verify(
        ROOT,
        pointer,
        mode=cmp.MODE_CANDIDATE,
        pointer_relative_path=CANDIDATE,
        results_policy=cmp.RESULTS_POLICY_METADATA,
    )
    return path, result["verdict"] == cmp.VERDICT_FAIL_CLOSED


def _dispose(path: Path) -> None:
    def retry(function: Callable[..., Any], target: str, _error: BaseException) -> None:
        os.chmod(target, stat.S_IWRITE)
        function(target)

    shutil.rmtree(path, onexc=retry)


class Fixture:
    """A hermetic repository that a pointer shaped like the real one verifies in."""

    def __init__(self, source: "Fixture | None" = None) -> None:
        self.home = Path(tempfile.mkdtemp(prefix="cmp1_")).resolve()
        self.root = self.home / "repo"
        self.empty_config = self.home / "empty_gitconfig"
        self.empty_config.write_bytes(b"")
        self.commits: dict[str, str] = {}
        if source is None:
            self.pointer = load_live_candidate()
            self._build()
        else:
            shutil.copytree(source.root, self.root)
            self.pointer = copy.deepcopy(source.pointer)
            self.commits = dict(source.commits)

    def clone(self) -> "Fixture":
        return Fixture(self)

    def dispose(self) -> None:
        _dispose(self.home)

    # -- Git, isolated from every user and system setting --------------------

    def git(self, *args: str) -> str:
        environment = dict(
            os.environ,
            GIT_CONFIG_NOSYSTEM="1",
            GIT_CONFIG_GLOBAL=str(self.empty_config),
            GIT_OPTIONAL_LOCKS="0",
            GIT_TERMINAL_PROMPT="0",
            GIT_AUTHOR_NAME="fixture",
            GIT_AUTHOR_EMAIL="fixture@example.invalid",
            GIT_COMMITTER_NAME="fixture",
            GIT_COMMITTER_EMAIL="fixture@example.invalid",
        )
        done = subprocess.run(
            ["git", *args], cwd=self.root, env=environment, capture_output=True, check=False
        )
        if done.returncode != 0:
            raise AssertionError(f"git {args} failed: {done.stderr.decode('utf-8', 'replace')}")
        return done.stdout.decode("utf-8", "replace").strip()

    def commit(self, message: str, paths: list[str]) -> str:
        self.git("add", "-f", "--", *paths)
        self.git("commit", "-q", "-m", message)
        return self.git("rev-parse", "HEAD")

    def publish(self) -> None:
        self.git("update-ref", "refs/remotes/origin/thesis-v7", "HEAD")

    # -- files and identities -------------------------------------------------

    def path(self, relative: str) -> Path:
        return self.root.joinpath(*relative.split("/"))

    def write(self, relative: str, data: bytes) -> None:
        target = self.path(relative)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)

    def identity(self, relative: str, anchor: str | None = None, added: bool = True) -> dict:
        data = self.path(relative).read_bytes()
        entry: dict = {"path": relative, "sha256": _sha(data), "bytes": len(data)}
        if anchor is None:
            entry.update(
                git_tracked=False, git_blob_id=None, git_anchor_commit=None, git_anchor_role=None
            )
        else:
            entry.update(
                git_tracked=True,
                git_blob_id=self.git("rev-parse", f"{anchor}:{relative}"),
                git_anchor_commit=anchor,
                git_anchor_role=cmp.ANCHOR_ADDED if added else cmp.ANCHOR_CONTENT,
            )
        return entry

    def node(self, location: tuple) -> dict:
        node = cmp._lookup(self.pointer, location)
        assert isinstance(node, dict), location
        return node

    def bind(self, location: tuple, anchor: str | None = None, added: bool = True) -> None:
        node = self.node(location)
        node.update(self.identity(node["path"], anchor, added))

    def synthetic(self, location: tuple) -> str:
        relative = self.node(location)["path"]
        self.write(relative, f"synthetic fixture bytes for {relative}\n".encode("utf-8"))
        self.bind(location)
        return relative

    def record(self, location: tuple, name: str, extra: dict | None = None) -> str:
        payload = record_from_bindings(self.pointer, name)
        for key, value in (extra or {}).items():
            _set(payload, key if isinstance(key, tuple) else (key,), value)
        relative = self.node(location)["path"]
        self.write(relative, _json_bytes(payload))
        self.bind(location)
        return relative

    def write_pointer(self, relative: str = CANDIDATE, pointer: dict | None = None) -> None:
        self.write(relative, _json_bytes(self.pointer if pointer is None else pointer))

    # -- construction ----------------------------------------------------------

    def _build(self) -> None:
        self.root.mkdir()
        self.git("init", "-q", "-b", "thesis-v7", ".")
        self.git("config", "core.autocrlf", "false")
        self.write(".gitignore", b"results/\ndata/\n")
        pointer = self.pointer
        generation, axes = cmp._GENERATION, cmp._AXES
        economic = ("economic_parameter_interfaces",)
        inputs = [
            (*economic, "execution_input_authority", index)
            for index in range(len(pointer["economic_parameter_interfaces"]["execution_input_authority"]))
        ]
        accepted_at_a = [
            ("methodology_authority", "acceptance_closure"),
            ("methodology_authority", "acceptance_manifest"),
            ("evidence_authority", "independent_audit"),
            ("evidence_authority", "acceptance_closure"),
            ("evidence_authority", "acceptance_manifest"),
        ]
        base = [
            ("methodology_authority", "document"),
            ("evidence_authority", "document"),
            cmp._INPUT,
            cmp._CORE,
            cmp._STACK,
            cmp._RUNNER,
            (*economic, "parameter_registry"),
            *inputs,
            ("scientific_exposure_restrictions", "governing_clause"),
        ]
        paths_a = [".gitignore"] + [self.synthetic(location) for location in base]

        # Identity axes over a small member set; the path map lives in the manifest.
        validation_member = "tests/test_fixture_validation_member.py"
        self.write(validation_member, b"# synthetic validation member\n")
        paths_a.append(validation_member)
        members = {
            "runtime": [self.node(cmp._CORE)["path"], self.node(cmp._STACK)["path"], self.node(cmp._RUNNER)["path"]],
            "validation": [validation_member],
            "governance_authority": [
                self.node(cmp._FRAMEWORK)["path"],
                self.node(cmp._REGISTRY)["path"],
                self.node(cmp._INPUT)["path"],
            ],
        }
        maps = {
            axis: {relative: _sha(self.path(relative).read_bytes()) for relative in listed}
            for axis, listed in members.items()
        }
        for axis, mapping in maps.items():
            pointer["production_generation"]["identity_axes"][axis].update(
                digest=cmp.canonical_identity_digest(mapping), path_count=len(mapping)
            )
        chain_a = [
            *accepted_at_a,
            (*generation, "candidate_checkpoint"),
            (*generation, "candidate_change_ledger"),
            (*cmp._ROLES, "independent_audit_pass"),
        ]
        paths_a += [self.synthetic(location) for location in chain_a]
        manifest_location = (*axes, "path_list_source")
        paths_a.append(
            self.record(
                manifest_location,
                "g1_candidate_manifest",
                {
                    (pointer["production_generation"]["identity_axes"][axis]["manifest_key"], "paths"): mapping
                    for axis, mapping in maps.items()
                },
            )
        )
        commit_a = self.commit("G1 candidate and independent audit", paths_a)
        for location in (*chain_a, manifest_location):
            self.bind(location, commit_a)
        self.node((*cmp._ROLES, "implementation_candidate")).update(self.node(manifest_location))

        acceptance = [(*cmp._ROLES, "acceptance_closure"), (*cmp._ROLES, "acceptance_manifest")]
        commit_b = self.commit("G1 acceptance", [self.synthetic(location) for location in acceptance])
        for location in acceptance:
            self.bind(location, commit_b)

        re_freeze = (*cmp._ROLES, "production_authority_re_freeze")
        paths_c = [self.synthetic(re_freeze), self.record(cmp._LIFECYCLE, "g1_accepted_lifecycle")]
        commit_c = self.commit("G1 re-freeze and accepted lifecycle", paths_c)
        self.bind(re_freeze, commit_c)
        self.bind(cmp._LIFECYCLE, commit_c)

        commit_d = self.commit("scope authorization", [self.record(cmp._SCOPE, "scope_authorization")])
        self.bind(cmp._SCOPE, commit_d)
        commit_p = self.commit("no-solve preflight evidence", [self.synthetic(cmp._PREFLIGHT)])
        self.bind(cmp._PREFLIGHT, commit_p)
        execution_inputs = {self.node(location)["path"]: self.node(location)["sha256"] for location in inputs}
        commit_e = self.commit(
            "execution authorization",
            [
                self.record(
                    cmp._EXECUTION,
                    "execution_authorization",
                    {"execution_input_authority": execution_inputs},
                )
            ],
        )
        self.bind(cmp._EXECUTION, commit_e)
        for location in base:
            self.bind(location, commit_e, added=False)
        provenance = pointer["git_provenance"]
        provenance["historical_execution_commit"] = commit_e
        pointer["methodology_authority"]["acceptance_commit"] = commit_a
        pointer["evidence_authority"]["acceptance_commit"] = commit_a

        self._build_run()

        audit = cmp._AUDIT
        audit_plain = [(*audit, "independent_audit_report"), (*audit, "audit_evidence_record"), (*audit, "checkpoint")]
        paths_u = [self.synthetic(location) for location in audit_plain]
        paths_u.append(self.record((*audit, "publication_manifest"), "audit_publication_manifest"))
        commit_u = self.commit("audit evidence publication", paths_u)
        for location in (*audit_plain, (*audit, "publication_manifest")):
            self.bind(location, commit_u)
        pointer["independent_audit_evidence_publication"]["publication_commit"] = commit_u
        provenance["audit_evidence_publication_commit"] = commit_u

        acceptance_section = cmp._ACCEPTANCE
        checkpoint = (*acceptance_section, "checkpoint")
        paths_r = [self.synthetic(checkpoint)]
        section = pointer["open_findings_and_limitations"]
        findings = section["findings"]
        accepted_lists: dict = {row[0]: [] for row in cmp.ACCEPTED_FINDING_LISTS}
        for finding in findings:
            listed, severity_key, disposition_key = next(
                row for row in cmp.ACCEPTED_FINDING_LISTS if row[0] == finding["accepted_list"]
            )
            entry = {
                "id": finding["id"],
                "closed": False,
                severity_key: finding["severity"],
                disposition_key: finding["disposition"],
            }
            for flag, purposes in cmp.CLOSURE_BLOCKING_FLAG_PURPOSES.items():
                entry[flag] = set(purposes) <= set(finding["blocks_purposes"]) or None
            accepted_lists[listed].append(entry)
        boundaries = [
            item
            for item in pointer["non_authorization_boundaries"]["not_authorized_by_this_pointer"]
            if item not in cmp.POINTER_OWN_NON_AUTHORIZATIONS
        ]
        paths_r.append(
            self.record(
                (*acceptance_section, "acceptance_closure"),
                "results_acceptance_closure",
                {
                    **accepted_lists,
                    "not_authorized_by_this_record": ["CURRENT_MAINLINE_POINTER", *boundaries],
                    "disclosed_limitations_carried": copy.deepcopy(
                        section["limitations_carried_from_results_acceptance"]
                    ),
                },
            )
        )
        fields = ("path", "sha256", "bytes", "git_blob_id")
        phase_a_files = [
            {field: self.node((*audit, name))[field] for field in fields}
            for name in ("independent_audit_report", "audit_evidence_record", "publication_manifest", "checkpoint")
        ]
        paths_r.append(
            self.record(
                (*acceptance_section, "acceptance_manifest"),
                "results_acceptance_manifest",
                {
                    "findings_open_after_acceptance": [finding["id"] for finding in findings],
                    ("accepted_evidence_references", "phase_a_files"): phase_a_files,
                },
            )
        )
        commit_r = self.commit("results acceptance", paths_r)
        for name in ("checkpoint", "acceptance_closure", "acceptance_manifest"):
            self.bind((*acceptance_section, name), commit_r)
        pointer["formal_results_acceptance"]["publication_commit"] = commit_r
        provenance["results_acceptance_publication_commit"] = commit_r
        provenance["ancestry_chain_oldest_to_newest"] = [
            commit_a, commit_b, commit_c, commit_d, commit_p, commit_e, commit_u, commit_r,
        ]
        provenance["direct_parent_links"] = [[commit_e, commit_u], [commit_u, commit_r]]
        self.commits = {"execution": commit_e, "audit": commit_u, "acceptance": commit_r}
        self.publish()
        self.write_pointer()

    def _build_run(self) -> None:
        """A synthetic run: opaque placeholder bytes, no result value anywhere."""

        pointer = self.pointer
        results = pointer["accepted_result_set"]
        run = results["run_path"]
        case_ids = cmp.expected_case_ids(
            results["case_universe"]["alpha_universe"], results["case_universe"]["beta_universe_h"]
        )
        registry: dict[str, dict] = {}

        def put(relative: str, data: bytes) -> None:
            self.write(f"{run}/{relative}", data)
            registry[relative] = {"bytes": len(data), "sha256": _sha(data)}

        case_entries = 0
        for case_id in case_ids:
            case_registry = {}
            for name in CASE_FILE_NAMES:
                data = f"placeholder {case_id} {name}\n".encode("utf-8")
                put(f"cases/{case_id}/{name}", data)
                case_registry[name] = {"bytes": len(data), "sha256": _sha(data)}
            case_entries += len(case_registry)
            put(
                f"cases/{case_id}/completion_manifest.json",
                _json_bytes(
                    {
                        "artifact_registry": case_registry,
                        "case_id": case_id,
                        "mandatory_audits": [],
                        "optimization_calls": 1,
                        "status": results["status_layers"]["execution_time_case_status"],
                    }
                ),
            )
        put("case_schedule.json", _json_bytes({"cases": case_ids}))
        put("authority.json", _json_bytes(record_from_bindings(pointer, "run_authority")))
        manifest = record_from_bindings(pointer, "run_completion_manifest")
        manifest.update(artifact_registry=registry, case_ids=case_ids)
        self.write(f"{run}/completion_manifest.json", _json_bytes(manifest))
        for name in ("completion_manifest", "authority", "case_schedule"):
            self.bind((*cmp._ROOT, name))
        sizes = {
            file.relative_to(self.path(run)).as_posix(): file.stat().st_size
            for file in self.path(run).rglob("*")
            if file.is_file()
        }
        hashes = {relative: _sha(self.path(f"{run}/{relative}").read_bytes()) for relative in sizes}
        results["registrations"].update(
            files_under_run_root=len(sizes),
            total_bytes=sum(sizes.values()),
            root_registered_artifacts=len(registry),
            case_registered_artifacts=case_entries,
        )
        results["run_file_aggregate"]["sha256"] = _sha(
            "".join(f"{p}\t{hashes[p]}\t{sizes[p]}\n" for p in sorted(sizes)).encode("utf-8")
        )

    # -- activation (canonical mode) -------------------------------------------

    def activate(self, *, tamper_payload: bool = False, alias_roles: bool = False) -> dict:
        """Publish an audited, accepted canonical pointer the proposed way."""

        candidate_bytes = self.path(CANDIDATE).read_bytes()
        candidate = json.loads(candidate_bytes.decode("utf-8"))
        digest = cmp.pointer_payload_digest(candidate)
        commit_candidate = self.commit("pointer candidate", [CANDIDATE])
        accepted_candidate = {"path": CANDIDATE, "sha256": _sha(candidate_bytes)}
        self.write(
            ACTIVATION_AUDIT,
            _json_bytes(
                {
                    "artifact_type": cmp.ACTIVATION_AUDIT_ARTIFACT_TYPE,
                    "verdict": "PASS",
                    "self_audit": False,
                    "audited_candidate": accepted_candidate,
                    "audited_payload_digest": digest,
                }
            ),
        )
        commit_audit = self.commit("pointer independent audit", [ACTIVATION_AUDIT])
        self.write(
            ACTIVATION_CLOSURE,
            _json_bytes(
                {
                    "artifact_type": cmp.ACTIVATION_CLOSURE_ARTIFACT_TYPE,
                    "acceptance_status": "CLOSED_ACCEPTED",
                    "canonical_pointer_path": CANONICAL,
                    "accepted_candidate": accepted_candidate,
                    "accepted_payload_digest": digest,
                    "independent_audit_record": self.identity(ACTIVATION_AUDIT, commit_audit),
                }
            ),
        )
        self.write(
            ACTIVATION_MANIFEST,
            _json_bytes(
                {
                    "artifact_type": cmp.ACTIVATION_MANIFEST_ARTIFACT_TYPE,
                    "acceptance_closure": {
                        "path": ACTIVATION_CLOSURE,
                        "sha256": _sha(self.path(ACTIVATION_CLOSURE).read_bytes()),
                    },
                }
            ),
        )
        commit_acceptance = self.commit("pointer acceptance", [ACTIVATION_CLOSURE, ACTIVATION_MANIFEST])
        canonical = copy.deepcopy(candidate)
        canonical["pointer_identity"] = {
            "pointer_id": "CURRENT_MAINLINE_POINTER_R1",
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
            "audited_candidate": self.identity(CANDIDATE, commit_candidate),
            "independent_audit_record": self.identity(ACTIVATION_AUDIT, commit_audit),
            "acceptance_closure": self.identity(ACTIVATION_CLOSURE, commit_acceptance),
            "acceptance_manifest": self.identity(ACTIVATION_MANIFEST, commit_acceptance),
        }
        if tamper_payload:
            canonical["documentation"]["purpose"] += " Altered after the audit."
        if alias_roles:
            canonical["activation_basis"]["acceptance_closure"] = dict(
                canonical["activation_basis"]["independent_audit_record"]
            )
        self.write_pointer(CANONICAL, canonical)
        self.commit("canonical pointer", [CANONICAL])
        self.publish()
        return canonical


def verify_object(
    root: Path,
    pointer: Any,
    *,
    policy: str = cmp.RESULTS_POLICY_NONE,
    mode: str = cmp.MODE_CANDIDATE,
    relative: str = CANDIDATE,
) -> dict:
    return cmp._verify(
        root, pointer, mode=mode, pointer_relative_path=relative, results_policy=policy
    )


class VerifierCase(unittest.TestCase):
    def assertFailsClosed(self, result: dict, *codes: str) -> None:
        self.assertEqual(result["verdict"], cmp.VERDICT_FAIL_CLOSED, result["failure_codes"])
        self.assertFalse(result["is_current_authority"])
        self.assertFalse(result["results_consumption_permitted"])
        for code in codes:
            self.assertIn(code, result["failure_codes"])

    def assertCandidateConsistent(self, result: dict) -> None:
        self.assertEqual(result["failures"], [])
        self.assertEqual(result["verdict"], cmp.VERDICT_CANDIDATE_CONSISTENT)
        self.assertFalse(result["is_current_authority"])
        self.assertFalse(result["results_consumption_permitted"])
        self.assertFalse(result["candidate_promoted"])
        self.assertFalse(result["authority_conferred_by_this_verification"])
        self.assertFalse(result["grants_execution_authority"])


# ---------------------------------------------------------------------------
# Static: the verifier is read-only by construction
# ---------------------------------------------------------------------------


class StaticVerifierTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.source = MODULE_PATH.read_text(encoding="utf-8")
        cls.tree = ast.parse(cls.source)

    def test_imports_are_standard_library_only(self) -> None:
        imported = set()
        for node in ast.walk(self.tree):
            if isinstance(node, ast.Import):
                imported |= {alias.name.split(".")[0] for alias in node.names}
            elif isinstance(node, ast.ImportFrom):
                self.assertEqual(node.level, 0, "relative import")
                imported.add((node.module or "").split(".")[0])
        self.assertLessEqual(imported, STDLIB_ALLOWLIST, imported - STDLIB_ALLOWLIST)

    def test_no_solver_model_or_optimize_reference(self) -> None:
        names = {node.id for node in ast.walk(self.tree) if isinstance(node, ast.Name)}
        attributes = {node.attr for node in ast.walk(self.tree) if isinstance(node, ast.Attribute)}
        for forbidden in ("gurobipy", "gp", "Model", "optimize", "optimizeAsync", "addVar", "addConstr"):
            self.assertNotIn(forbidden, names | attributes)
        self.assertNotIn("import_module", names | attributes)
        self.assertNotIn("__import__", names)
        self.assertNotIn("exec", names)
        self.assertNotIn("eval", names)

    def test_no_file_is_ever_written(self) -> None:
        attributes = {node.attr for node in ast.walk(self.tree) if isinstance(node, ast.Attribute)}
        for writer in (
            "write_text", "write_bytes", "mkdir", "makedirs", "unlink", "rmdir", "rename",
            "touch", "symlink_to", "hardlink_to", "chmod", "remove", "rmtree", "copy", "copyfile",
        ):
            self.assertNotIn(writer, attributes)
        for node in ast.walk(self.tree):
            if not isinstance(node, ast.Call):
                continue
            self.assertFalse(isinstance(node.func, ast.Name) and node.func.id == "open", "builtin open")
            if isinstance(node.func, ast.Attribute) and node.func.attr == "open":
                self.assertEqual([ast.literal_eval(a) for a in node.args], ["rb"])
            if isinstance(node.func, ast.Attribute) and node.func.attr == "write":
                self.assertEqual(ast.unparse(node.func), "sys.stdout.write")

    def test_only_read_only_git_subcommands_can_run(self) -> None:
        used = set()
        for node in ast.walk(self.tree):
            if (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Attribute)
                and node.func.attr == "run"
                and ast.unparse(node.func) != "subprocess.run"
            ):
                self.assertIsInstance(node.args[0], ast.Constant)
                used.add(node.args[0].value)
        self.assertTrue(used)
        self.assertLessEqual(used, cmp._GIT_READ_ONLY_SUBCOMMANDS)
        writers = {"add", "commit", "push", "tag", "reset", "clean", "stash", "checkout", "update-ref",
                   "status", "diff", "fetch", "pull", "merge", "rebase", "gc", "config", "restore"}
        self.assertFalse(writers & cmp._GIT_READ_ONLY_SUBCOMMANDS)
        for subcommand in sorted(writers):
            with self.assertRaises(RuntimeError):
                cmp._Git(ROOT).run(subcommand)
        subprocess_calls = [
            node for node in ast.walk(self.tree)
            if isinstance(node, ast.Call) and ast.unparse(node.func).startswith("subprocess.")
        ]
        self.assertEqual({ast.unparse(node.func) for node in subprocess_calls}, {"subprocess.run"})
        for node in subprocess_calls:
            self.assertEqual(ast.unparse(node.args[0]), "command")

    def test_the_module_carries_no_identity_literal(self) -> None:
        """Every hash and commit lives in the pointer, never in the code."""

        self.assertEqual(re.findall(r"\b[0-9a-f]{40}\b", self.source), [])
        self.assertEqual(re.findall(r"\b[0-9a-f]{64}\b", self.source), [])

    def test_no_public_entry_point_can_promote_or_activate(self) -> None:
        public = {name for name in vars(cmp) if not name.startswith("_") and callable(getattr(cmp, name))}
        for name in public:
            self.assertIsNone(
                re.search(r"promote|activate|accept|publish|write|create|install", name, re.I), name
            )

    def test_required_checks_and_schema_are_closed(self) -> None:
        self.assertEqual(len(set(cmp.CHECK_IDS)), len(cmp.CHECK_IDS))
        self.assertEqual(set(cmp.ENVELOPE_KEYS) & set(cmp.POINTER_SCHEMA), set(cmp.ENVELOPE_KEYS))
        records = {row[0] for row in cmp.CROSS_BINDINGS}
        self.assertEqual(records, set(cmp.TRACKED_RECORDS) | set(cmp.LOCAL_RECORDS))


class PathContainmentTests(unittest.TestCase):
    def test_escaping_and_ambiguous_paths_are_refused(self) -> None:
        refused = {
            "../outside.md": "PATH_TRAVERSAL_SEGMENT",
            "docs/../../outside.md": "PATH_TRAVERSAL_SEGMENT",
            "docs/./x.md": "PATH_TRAVERSAL_SEGMENT",
            "docs//x.md": "PATH_TRAVERSAL_SEGMENT",
            "docs/x.md/": "PATH_TRAVERSAL_SEGMENT",
            "/etc/passwd": "PATH_ABSOLUTE",
            "~/x": "PATH_ABSOLUTE",
            "C:/Windows/win.ini": "PATH_ABSOLUTE",
            "c:relative": "PATH_ABSOLUTE",
            "docs\\x.md": "PATH_NOT_POSIX",
            "\\\\server\\share\\x": "PATH_NOT_POSIX",
            " docs/x.md": "PATH_NOT_POSIX",
            "docs/x.md:stream": "PATH_UNSAFE_SEGMENT",
            "docs/x.": "PATH_UNSAFE_SEGMENT",
            "docs/x ": "PATH_NOT_POSIX",
            "": "PATH_NOT_A_NONEMPTY_STRING",
        }
        for relative, code in refused.items():
            with self.subTest(path=relative):
                with self.assertRaises(cmp.PointerPathError) as caught:
                    cmp.resolve_repository_path(ROOT, relative)
                self.assertEqual(caught.exception.code, code)
        for not_a_string in (None, 7, ["docs"], Path("docs")):
            with self.assertRaises(cmp.PointerPathError):
                cmp.resolve_repository_path(ROOT, not_a_string)

    def test_a_contained_path_resolves_inside_the_repository(self) -> None:
        resolved = cmp.resolve_repository_path(ROOT, "src/current_mainline_pointer_v1.py")
        self.assertTrue(resolved.is_file())
        self.assertEqual(resolved.relative_to(ROOT.resolve()).as_posix(), "src/current_mainline_pointer_v1.py")
        absent = cmp.resolve_repository_path(ROOT, CANONICAL)
        self.assertEqual(absent.relative_to(ROOT.resolve()).as_posix(), CANONICAL)

    def test_case_ids_follow_the_declared_rule(self) -> None:
        self.assertEqual(
            cmp.expected_case_ids([0.6, 1.0], [4, 12]),
            ["a0.60_b04", "a0.60_b12", "a1.00_b04", "a1.00_b12"],
        )
        for alpha, beta in (([True], [4]), (["0.6"], [4]), ([0.6], [4.0]), ([0.6], [True])):
            with self.assertRaises(ValueError):
                cmp.expected_case_ids(alpha, beta)


# ---------------------------------------------------------------------------
# Live: the real candidate against the real repository
# ---------------------------------------------------------------------------


class LiveCandidateTests(VerifierCase):
    """LIVE PREMISE: the state bound by Candidate R1 is the live repository state."""

    @classmethod
    def setUpClass(cls) -> None:
        if not (ROOT / CANDIDATE).is_file():
            raise unittest.SkipTest(f"{CANDIDATE} is absent; the live layer has nothing to verify")
        cls.pointer = load_live_candidate()
        cls.result = cmp.verify_candidate_pointer(ROOT, CANDIDATE)

    def mutated(self, change: Callable[[dict], Any], **options: Any) -> dict:
        pointer = copy.deepcopy(self.pointer)
        change(pointer)
        return verify_object(ROOT, pointer, **options)

    def test_candidate_is_internally_consistent_and_nothing_more(self) -> None:
        self.assertCandidateConsistent(self.result)
        self.assertEqual(self.result["mode"], cmp.MODE_CANDIDATE)
        self.assertEqual(self.result["checks"][cmp.CHECK_ACTIVATION], cmp.STATUS_NOT_APPLICABLE)
        self.assertEqual(self.result["checks"][cmp.CHECK_RESULTS], cmp.STATUS_NOT_RUN)
        self.assertEqual(self.result["results_integrity"], cmp.RESULTS_NOT_CHECKED)
        for check in cmp.CHECK_IDS[:11]:
            self.assertEqual(self.result["checks"][check], cmp.STATUS_PASS, check)
        self.assertEqual(self.result["pointer_sha256"], _sha((ROOT / CANDIDATE).read_bytes()))

    def test_candidate_declares_its_own_lifecycle(self) -> None:
        identity = self.pointer["pointer_identity"]
        self.assertEqual(identity["lifecycle"], "CANDIDATE / NOT ACCEPTED / NOT CURRENT AUTHORITY")
        self.assertEqual(
            [identity[k] for k in ("is_candidate", "is_accepted", "is_canonical", "is_current_authority", "self_accepted")],
            [True, False, False, False, False],
        )
        self.assertEqual(identity["proposed_canonical_path"], CANONICAL)
        self.assertEqual(self.pointer["activation_basis"]["status"], cmp.ACTIVATION_NOT_ACTIVATED)
        self.assertNotIn("sha256", identity)

    def test_serialization_is_lf_utf8_and_portable(self) -> None:
        data = (ROOT / CANDIDATE).read_bytes()
        self.assertNotIn(b"\r", data)
        self.assertTrue(data.endswith(b"}\n"))
        self.assertEqual(data, _json_bytes(json.loads(data.decode("utf-8"))))
        text = data.decode("utf-8")
        self.assertIsNone(re.search(r"[A-Za-z]:[\\/]", text), "absolute Windows path in the pointer")
        self.assertNotIn("Users", text)

    def test_candidate_cannot_be_promoted_by_claiming_authority(self) -> None:
        def claim(field: str, value: Any) -> Callable[[dict], Any]:
            return lambda p: p["pointer_identity"].__setitem__(field, value)

        self.assertFailsClosed(self.mutated(claim("is_current_authority", True)), "CANDIDATE_CLAIMS_AUTHORITY")
        self.assertFailsClosed(self.mutated(claim("is_accepted", True)), "CANDIDATE_CLAIMS_AUTHORITY")
        self.assertFailsClosed(self.mutated(claim("is_canonical", True)), "CANDIDATE_CLAIMS_AUTHORITY")
        self.assertFailsClosed(self.mutated(claim("self_accepted", True)), "POINTER_SELF_ACCEPTED")
        self.assertFailsClosed(
            self.mutated(claim("lifecycle_state", cmp.LIFECYCLE_CANONICAL)), "CANDIDATE_LIFECYCLE_STATE"
        )
        self.assertFailsClosed(
            self.mutated(lambda p: p["activation_basis"].__setitem__("status", cmp.ACTIVATION_ACCEPTED_PUBLISHED)),
            "CANDIDATE_CLAIMS_ACTIVATION",
        )
        self.assertFailsClosed(
            self.mutated(lambda p: None, relative="configs/current_mainline_pointer_candidate_r1.json"),
            "CANDIDATE_NOT_UNDER_CANDIDATE_DIRECTORY",
        )
        # The same bytes presented as canonical are refused as candidate-only.
        self.assertFailsClosed(
            self.mutated(lambda p: None, mode=cmp.MODE_CANONICAL, relative=CANONICAL),
            "CANONICAL_POINTER_IS_CANDIDATE_ONLY",
            "ACTIVATION_BASIS_ABSENT",
        )

    def test_wrong_framework_or_registry_identity_fails(self) -> None:
        for section in ("methodology_authority", "evidence_authority"):
            with self.subTest(section=section):
                def flip(p: dict, section: str = section) -> None:
                    document = p[section]["document"]
                    document["sha256"] = document["sha256"][:-1] + ("0" if document["sha256"][-1] != "0" else "1")

                result = self.mutated(flip)
                self.assertFailsClosed(
                    result, "RAW_BYTES_DIFFER_IN_CONTENT", "GIT_BLOB_BYTES_MISMATCH", "CROSS_BINDING_MISMATCH"
                )
                self.assertNotIn("RAW_BYTES_DIFFER_BY_EOL_CONVERSION_ONLY", result["failure_codes"])

                def repoint(p: dict, section: str = section) -> None:
                    document = p[section]["document"]
                    predecessor = next(
                        e["path"] for e in p["roles"]["historical_only"]
                        if e["role"].startswith("HISTORICAL_ACCEPTED") and ("framework" in e["path"]) == (section == "methodology_authority")
                    )
                    document["path"] = predecessor

                self.assertFailsClosed(self.mutated(repoint), "NON_CURRENT_PATH_CLAIMED_CURRENT", "CROSS_BINDING_MISMATCH")

    def test_wrong_annual_input_identity_fails(self) -> None:
        def flip(p: dict) -> None:
            p["canonical_annual_input"]["sha256"] = "0" * 64

        self.assertFailsClosed(self.mutated(flip), "RAW_BYTES_DIFFER_IN_CONTENT", "GIT_BLOB_BYTES_MISMATCH", "CROSS_BINDING_MISMATCH")
        self.assertFailsClosed(
            self.mutated(lambda p: p["canonical_annual_input"].__setitem__("bytes", 1)), "RAW_BYTES_DIFFER_IN_CONTENT"
        )

    def test_wrong_generation_or_run_id_fails(self) -> None:
        self.assertFailsClosed(
            self.mutated(lambda p: p["production_generation"].__setitem__("generation_id", "CURRENT_FULL81_PRODUCTION_GENERATION_G2")),
            "CROSS_BINDING_MISMATCH",
        )
        run_id = self.pointer["accepted_result_set"]["run_id"]
        other = run_id[:-1] + ("0" if run_id[-1] != "0" else "1")
        self.assertFailsClosed(
            self.mutated(lambda p: p["accepted_result_set"].__setitem__("run_id", other)),
            "RUN_PATH_NOT_BOUND_TO_RUN_ID",
            "CROSS_BINDING_MISMATCH",
        )

        def repoint(p: dict) -> None:
            results = p["accepted_result_set"]
            results["run_id"] = other
            results["run_path"] = results["run_path"].replace(run_id, other)
            for artifact in results["root_artifacts"].values():
                artifact["path"] = artifact["path"].replace(run_id, other)
            for entry in p["roles"]["accepted_current"]:
                entry["path"] = entry["path"].replace(run_id, other)

        self.assertFailsClosed(self.mutated(repoint), "CROSS_BINDING_MISMATCH")
        self.assertFailsClosed(
            self.mutated(lambda p: p["production_generation"]["identity_axes"]["runtime"].__setitem__("digest", "f" * 64)),
            "IDENTITY_AXIS_RECORDED_DIGEST",
            "IDENTITY_AXIS_LIVE_DRIFT",
            "IDENTITY_AXIS_GIT_BLOB_DIGEST",
            "CROSS_BINDING_MISMATCH",
        )

    def test_missing_or_inconsistent_results_acceptance_reference_fails(self) -> None:
        self.assertFailsClosed(self.mutated(lambda p: p.pop("formal_results_acceptance")), "SCHEMA_VIOLATION")
        self.assertFailsClosed(
            self.mutated(lambda p: p["formal_results_acceptance"].pop("acceptance_closure")), "SCHEMA_VIOLATION"
        )
        self.assertFailsClosed(
            self.mutated(lambda p: p["formal_results_acceptance"].__setitem__("acceptance_status", "PENDING")),
            "CROSS_BINDING_MISMATCH",
        )
        self.assertFailsClosed(
            self.mutated(lambda p: p["formal_results_acceptance"]["acceptance_closure"].__setitem__("sha256", "a" * 64)),
            "GIT_BLOB_BYTES_MISMATCH",
            "CROSS_BINDING_MISMATCH",
        )

        def swap(p: dict) -> None:
            # The audit-evidence manifest presented as the results-acceptance manifest.
            p["formal_results_acceptance"]["acceptance_manifest"] = dict(
                p["independent_audit_evidence_publication"]["publication_manifest"]
            )

        self.assertFailsClosed(self.mutated(swap), "CROSS_BINDING_MISMATCH", "POINTER_INTERNAL_INCONSISTENCY")
        self.assertFailsClosed(
            self.mutated(
                lambda p: p["accepted_result_set"]["root_artifacts"]["completion_manifest"].__setitem__("sha256", "b" * 64)
            ),
            "CROSS_BINDING_MISMATCH",
        )

    def test_the_two_status_layers_cannot_be_conflated(self) -> None:
        layers = self.pointer["accepted_result_set"]["status_layers"]
        self.assertEqual(layers["execution_time_completion_manifest_status"], "COMPLETE_PASS_PENDING_INDEPENDENT_ACCEPTANCE")
        self.assertEqual(layers["current_governance_status"], "CLOSED / ACCEPTED / PUBLISHED")
        self.assertEqual(self.pointer["formal_results_acceptance"]["governance_status"], "CLOSED / ACCEPTED / PUBLISHED")
        self.assertFailsClosed(
            self.mutated(lambda p: p["accepted_result_set"]["status_layers"].__setitem__(
                "execution_time_completion_manifest_status", "CLOSED_ACCEPTED")),
            "CROSS_BINDING_MISMATCH",
        )
        self.assertFailsClosed(
            self.mutated(lambda p: p["independent_audit_evidence_publication"].__setitem__(
                "result_acceptance_status_recorded_at_publication", "CLOSED_ACCEPTED")),
            "CROSS_BINDING_MISMATCH",
        )

    def test_historical_or_stale_result_namespace_cannot_become_current(self) -> None:
        roles = self.pointer["roles"]
        run_id = self.pointer["accepted_result_set"]["run_id"]
        not_current = roles["historical_only"] + roles["accepted_other_scope_not_bound_by_this_pointer"]
        self.assertTrue(not_current)
        for entry in not_current:
            if not entry["path"].startswith("results/") or "/runs/" not in entry["path"]:
                continue
            with self.subTest(path=entry["path"]):
                namespace, _, other = entry["path"].partition("/runs/")

                def repoint(p: dict, namespace: str = namespace, other: str = other) -> None:
                    results = p["accepted_result_set"]
                    old = results["run_path"]
                    results.update(result_namespace=namespace, run_id=other, run_path=f"{namespace}/runs/{other}")
                    for artifact in results["root_artifacts"].values():
                        artifact["path"] = artifact["path"].replace(old, results["run_path"])
                    for current in p["roles"]["accepted_current"]:
                        if current["path"] == old:
                            current["path"] = results["run_path"]

                self.assertFailsClosed(
                    self.mutated(repoint), "NON_CURRENT_PATH_CLAIMED_CURRENT", "CROSS_BINDING_MISMATCH"
                )
        self.assertFailsClosed(
            self.mutated(lambda p: p["accepted_result_set"].__setitem__("run_id", ".pending_layer_a_" + run_id)),
            "RUN_ID_MALFORMED",
        )
        self.assertFailsClosed(
            self.mutated(lambda p: p["roles"]["historical_only"].append(
                {"role": "X", "path": p["accepted_result_set"]["run_path"]})),
            "NON_CURRENT_PATH_CLAIMED_CURRENT",
        )
        self.assertFailsClosed(
            self.mutated(lambda p: p["roles"]["accepted_current"].append(
                {"role": "X", "path": p["roles"]["historical_only"][0]["path"]})),
            "ACCEPTED_CURRENT_ROLES_MISMATCH",
        )
        self.assertFailsClosed(
            self.mutated(lambda p: p["roles"].__setitem__(
                "accepted_current",
                [e for e in p["roles"]["accepted_current"] if e["path"] != p["accepted_result_set"]["run_path"]])),
            "ACCEPTED_CURRENT_ROLES_MISMATCH",
        )
        self.assertFailsClosed(
            self.mutated(lambda p: p["roles"]["accepted_current"][0].__setitem__("role", "HISTORICAL_ONLY")),
            "ACCEPTED_CURRENT_ROLES_MISMATCH",
        )
        self.assertFailsClosed(
            self.mutated(lambda p: p["roles"]["accepted_current"].reverse()), "ACCEPTED_CURRENT_ROLES_MISMATCH"
        )

    def test_paths_escaping_the_repository_are_rejected(self) -> None:
        document = self.pointer["methodology_authority"]["document"]["path"]
        escapes = {
            "../outside.md": "PATH_TRAVERSAL_SEGMENT",
            "docs/../../outside.md": "PATH_TRAVERSAL_SEGMENT",
            "/etc/passwd": "PATH_ABSOLUTE",
            "C:/Windows/win.ini": "PATH_ABSOLUTE",
            document.replace("/", "\\"): "PATH_NOT_POSIX",
        }
        for relative, code in escapes.items():
            with self.subTest(path=relative):
                self.assertFailsClosed(
                    self.mutated(lambda p, relative=relative: p["methodology_authority"]["document"].__setitem__("path", relative)),
                    code,
                )
        self.assertFailsClosed(
            self.mutated(lambda p: p["accepted_result_set"].__setitem__("result_namespace", "../results")),
            "PATH_TRAVERSAL_SEGMENT",
        )
        self.assertFailsClosed(
            self.mutated(lambda p: p["roles"]["historical_only"][0].__setitem__("path", "C:/elsewhere")),
            "PATH_ABSOLUTE",
        )
        # A case alias of a real path is not the same path.
        aliased = self.mutated(
            lambda p: p["methodology_authority"]["document"].__setitem__("path", document.replace("docs/", "Docs/", 1))
        )
        self.assertEqual(aliased["verdict"], cmp.VERDICT_FAIL_CLOSED)

    def test_git_provenance_is_bound_without_pinning_the_live_head(self) -> None:
        provenance = self.pointer["git_provenance"]
        self.assertIs(provenance["live_head_must_equal_a_recorded_commit"], False)
        self.assertTrue(self.result["git"]["live_head_equality_is_not_required"])
        self.assertFailsClosed(
            self.mutated(lambda p: p["git_provenance"].__setitem__("live_head_must_equal_a_recorded_commit", True)),
            "LIVE_HEAD_EQUALITY_REQUIREMENT_FORBIDDEN",
        )
        self.assertFailsClosed(
            self.mutated(lambda p: p["git_provenance"].__setitem__("historical_execution_commit", "0" * 40)),
            "GIT_COMMIT_ABSENT",
            "POINTER_INTERNAL_INCONSISTENCY",
            "CROSS_BINDING_MISMATCH",
        )
        self.assertFailsClosed(
            self.mutated(lambda p: p["git_provenance"].__setitem__(
                "historical_execution_commit", p["git_provenance"]["results_acceptance_publication_commit"])),
            "POINTER_INTERNAL_INCONSISTENCY",
            "CROSS_BINDING_MISMATCH",
        )
        self.assertFailsClosed(
            self.mutated(lambda p: p["git_provenance"]["ancestry_chain_oldest_to_newest"].reverse()),
            "GIT_ANCESTRY_ORDER_VIOLATED",
        )
        self.assertFailsClosed(
            self.mutated(lambda p: p["git_provenance"]["direct_parent_links"][0].reverse()),
            "GIT_PARENT_LINK_VIOLATED",
        )
        self.assertFailsClosed(
            self.mutated(lambda p: p["git_provenance"].__setitem__("upstream_ref", "refs/remotes/origin/absent-branch")),
            "UPSTREAM_REF_ABSENT",
        )
        self.assertFailsClosed(
            self.mutated(lambda p: p["git_provenance"].__setitem__("upstream_ref", "HEAD")), "UPSTREAM_REF_ABSENT"
        )
        self.assertFailsClosed(
            self.mutated(lambda p: p["methodology_authority"]["document"].__setitem__("git_blob_id", "1" * 40)),
            "GIT_BLOB_MISMATCH_AT_ANCHOR_COMMIT",
            "GIT_BLOB_CHANGED_IN_LIVE_HEAD",
        )

        def older_anchor(p: dict) -> None:
            # Claiming the results-acceptance closure was published by the audit commit.
            closure = p["formal_results_acceptance"]["acceptance_closure"]
            closure["git_anchor_commit"] = p["git_provenance"]["audit_evidence_publication_commit"]

        self.assertFailsClosed(
            self.mutated(older_anchor), "GIT_BLOB_MISMATCH_AT_ANCHOR_COMMIT", "POINTER_INTERNAL_INCONSISTENCY"
        )

    def test_scientific_exposure_restrictions_remain_explicit(self) -> None:
        restrictions = self.pointer["scientific_exposure_restrictions"]
        findings = {f["id"]: f for f in self.pointer["open_findings_and_limitations"]["findings"]}
        self.assertEqual(restrictions["governing_finding"], "ACC-N1")
        self.assertEqual((findings["ACC-N1"]["severity"], findings["ACC-N1"]["disposition"]), ("MAJOR", "OPEN"))
        self.assertEqual(
            set(restrictions["blocked_purposes"]),
            {cmp.PURPOSE_SCIENTIFIC_INSPECTION, cmp.PURPOSE_RESULTS_ANALYSIS, cmp.PURPOSE_SUPERVISOR_DISCUSSION},
        )
        self.assertEqual(restrictions["permitted_purposes"], [cmp.PURPOSE_TECHNICAL_IDENTITY_VERIFICATION])
        log = restrictions["exposure_log"]
        self.assertEqual(
            (log["established"], log["path"], log["entries_created_by_this_pointer"], log["this_pointer_is_an_exposure_log"]),
            (False, None, 0, False),
        )
        self.assertEqual(self.result["scientific_exposure"]["blocked_purposes"], restrictions["blocked_purposes"])
        expected_open = {
            "ACC-N1", "AUD-N1", "AUD-N2", "AUD-N3", "AUD-N4", "G1-N1", "G1-N2", "G1-N3",
            "R7_BINDING_AND_PRESERVATION_GIT_DURABILITY", "SAR-N1", "SAR-N2", "SAR-N3", "SAR-N4",
        }
        self.assertLessEqual(expected_open, set(findings))
        self.assertTrue(all(f["closed"] is False and f["resolution_evidence"] is None for f in findings.values()))
        register = self.pointer["open_findings_and_limitations"]["unresolved_register"]["U-01"]
        self.assertEqual((register["status"], register["blocks_main_full81"]), ("OPEN_HOLD", False))
        self.assertEqual(len(register["must_be_frozen_before"]), 4)
        self.assertEqual(self.pointer["open_findings_and_limitations"]["closed_or_remediated_by_this_pointer"], [])

        def drop(finding_id: str) -> Callable[[dict], Any]:
            def change(p: dict) -> None:
                section = p["open_findings_and_limitations"]
                section["findings"] = [f for f in section["findings"] if f["id"] != finding_id]
            return change

        def edit(finding_id: str, **fields: Any) -> Callable[[dict], Any]:
            def change(p: dict) -> None:
                next(f for f in p["open_findings_and_limitations"]["findings"] if f["id"] == finding_id).update(fields)
            return change

        for finding_id in sorted(expected_open):
            with self.subTest(dropped=finding_id):
                self.assertFailsClosed(self.mutated(drop(finding_id)), "OPEN_FINDING_DROPPED")
        for finding_id in ("ACC-N1", "G1-N2", "R7_BINDING_AND_PRESERVATION_GIT_DURABILITY"):
            with self.subTest(closed=finding_id):
                self.assertFailsClosed(
                    self.mutated(edit(finding_id, closed=True)), "FINDING_CLOSED_WITHOUT_EVIDENCE"
                )
        self.assertFailsClosed(self.mutated(drop("ACC-N1")), "GOVERNING_FINDING_ABSENT")
        for purpose in sorted(restrictions["blocked_purposes"]):
            with self.subTest(unblocked=purpose):
                self.assertFailsClosed(
                    self.mutated(lambda p, purpose=purpose: p["scientific_exposure_restrictions"]["blocked_purposes"].remove(purpose)),
                    "OPEN_FINDING_RESTRICTION_NOT_ENFORCED",
                    "SCIENTIFIC_EXPOSURE_RESTRICTION_WEAKENED",
                )

        def silently_unblock(p: dict) -> None:
            p["scientific_exposure_restrictions"]["blocked_purposes"] = []
            next(f for f in p["open_findings_and_limitations"]["findings"] if f["id"] == "ACC-N1")["blocks_purposes"] = []

        self.assertFailsClosed(self.mutated(silently_unblock), "SCIENTIFIC_EXPOSURE_RESTRICTION_WEAKENED")
        self.assertFailsClosed(
            self.mutated(lambda p: p["scientific_exposure_restrictions"]["permitted_purposes"].append(cmp.PURPOSE_RESULTS_ANALYSIS)),
            "PURPOSE_BOTH_BLOCKED_AND_PERMITTED",
        )
        self.assertFailsClosed(
            self.mutated(lambda p: p["scientific_exposure_restrictions"]["exposure_log"].update(
                established=True, path="results/provenance/exposure_log.json")),
            "EXPOSURE_LOG_CLAIMED_WHILE_FINDING_OPEN",
        )
        self.assertFailsClosed(
            self.mutated(lambda p: p["scientific_exposure_restrictions"]["exposure_log"].__setitem__(
                "this_pointer_is_an_exposure_log", True)),
            "POINTER_ACTS_AS_EXPOSURE_LOG",
        )
        self.assertFailsClosed(
            self.mutated(lambda p: p["open_findings_and_limitations"]["closed_or_remediated_by_this_pointer"].append("ACC-N1")),
            "FINDING_CLOSED_BY_POINTER",
        )
        self.assertFailsClosed(
            self.mutated(lambda p: p["open_findings_and_limitations"]["unresolved_register"]["U-01"].__setitem__("status", "RESOLVED")),
            "CROSS_BINDING_MISMATCH",
        )
        for field, value in (("severity", "MINOR"), ("disposition", "CLOSED"), ("accepted_list", "findings_carried_not_closed")):
            with self.subTest(regraded=field):
                self.assertFailsClosed(
                    self.mutated(edit("ACC-N1", **{field: value})), "FINDING_SEVERITY_OR_DISPOSITION_ALTERED"
                )
        self.assertFailsClosed(
            self.mutated(edit("G1-N2", severity="MINOR")), "FINDING_SEVERITY_OR_DISPOSITION_ALTERED"
        )
        self.assertFailsClosed(
            self.mutated(lambda p: p["open_findings_and_limitations"]["findings"].append(
                dict(p["open_findings_and_limitations"]["findings"][0], id="INVENTED-1"))),
            "FINDING_WITHOUT_ACCEPTED_SOURCE",
        )
        self.assertFailsClosed(
            self.mutated(lambda p: p["open_findings_and_limitations"]["limitations_carried_from_results_acceptance"].pop()),
            "DISCLOSED_LIMITATION_DROPPED_OR_ALTERED",
        )
        self.assertFailsClosed(
            self.mutated(lambda p: p["open_findings_and_limitations"]["fixture_control_limitation"].__setitem__("passed", 54)),
            "CROSS_BINDING_MISMATCH",
        )
        self.assertFailsClosed(
            self.mutated(lambda p: p["scientific_exposure_restrictions"]["carry_forward_conditions"].pop(0)),
            "CROSS_BINDING_MISMATCH",
        )
        self.assertFailsClosed(
            self.mutated(lambda p: p["scientific_exposure_restrictions"]["permitted_purposes"].append("FULL81_EXECUTION")),
            "UNKNOWN_PURPOSE",
        )
        self.assertFailsClosed(self.mutated(lambda p: p.pop("scientific_exposure_restrictions")), "SCHEMA_VIOLATION")
        self.assertFailsClosed(self.mutated(lambda p: p.pop("open_findings_and_limitations")), "SCHEMA_VIOLATION")

    def test_the_pointer_grants_no_execution_authority(self) -> None:
        boundaries = self.pointer["non_authorization_boundaries"]
        self.assertEqual((boundaries["pointer_grants_execution_authority"], boundaries["authorizes"]), (False, []))
        self.assertIs(self.pointer["full81_authorizations"]["pointer_grants_execution_authority"], False)
        declared = set(boundaries["not_authorized_by_this_pointer"])
        for required in (
            "NEW_FULL81_EXECUTION_OR_RERUN", "ANY_SOLVER_CALL_MODEL_CONSTRUCTION_OR_PRODUCTION_RUN",
            "A2_LAYER_B_DG_OR_SENSITIVITY", "LAYER_B", "DG_EXTENSION", "EXPOSURE_LOG_CREATION",
            "DOWNSTREAM_LAYER_A_RESULTS_ANALYSIS_OR_SCIENTIFIC_INSPECTION", "PIPELINE_MANAGEMENT_NOTEBOOK",
            "PRESERVATION_OR_PUBLICATION_OF_THE_651_RESULT_FILES", "DEPENDENCY_GRAPH", "SELECTIVE_RERUN_PLANNER",
            "CONTROLLED_EXECUTOR",
        ):
            self.assertIn(required, declared)
        self.assertIn("A2", self.pointer["full81_authorizations"]["execution_authorization"]["excluded_scopes"])
        self.assertFailsClosed(
            self.mutated(lambda p: p["non_authorization_boundaries"]["authorizes"].append("MAIN_FULL81_EXECUTION")),
            "POINTER_CLAIMS_EXECUTION_AUTHORITY",
        )
        self.assertFailsClosed(
            self.mutated(lambda p: p["non_authorization_boundaries"].__setitem__("pointer_grants_execution_authority", True)),
            "POINTER_CLAIMS_EXECUTION_AUTHORITY",
        )
        self.assertFailsClosed(
            self.mutated(lambda p: p["full81_authorizations"].__setitem__("pointer_grants_execution_authority", True)),
            "POINTER_CLAIMS_EXECUTION_AUTHORITY",
        )
        self.assertFailsClosed(
            self.mutated(lambda p: p["non_authorization_boundaries"]["not_authorized_by_this_pointer"].remove(
                "A2_LAYER_B_DG_OR_SENSITIVITY")),
            "NON_AUTHORIZATION_BOUNDARY_DROPPED",
        )
        self.assertFailsClosed(
            self.mutated(lambda p: p["non_authorization_boundaries"]["not_authorized_by_this_pointer"].remove("LAYER_B")),
            "NON_AUTHORIZATION_BOUNDARY_DROPPED",
        )
        self.assertFailsClosed(
            self.mutated(lambda p: p["non_authorization_boundaries"]["not_authorized_by_this_pointer"].append("NOTHING_REALLY")),
            "NON_AUTHORIZATION_BOUNDARY_UNKNOWN",
        )
        self.assertFailsClosed(
            self.mutated(lambda p: p["full81_authorizations"]["execution_authorization"][
                "authorized_historically_by_this_record"].append("A2")),
            "CROSS_BINDING_MISMATCH",
        )
        self.assertFailsClosed(
            self.mutated(lambda p: p["full81_authorizations"]["execution_authorization"]["excluded_scopes"].remove("A2")),
            "CROSS_BINDING_MISMATCH",
        )
        self.assertFailsClosed(
            self.mutated(lambda p: p["non_authorization_boundaries"].__setitem__("a2_variable_floor_status", "AUTHORIZED")),
            "CROSS_BINDING_MISMATCH",
        )
        self.assertFailsClosed(
            self.mutated(lambda p: p["validation_contract"]["required_checks"].remove(cmp.CHECK_FINDINGS)),
            "VALIDATION_CONTRACT_MISMATCH",
        )

    def test_schema_is_enforced(self) -> None:
        self.assertFailsClosed(self.mutated(lambda p: p.__setitem__("current_authority_override", True)), "SCHEMA_VIOLATION")
        self.assertFailsClosed(self.mutated(lambda p: p.__setitem__("schema_version", "v0")), "POINTER_INTERNAL_INCONSISTENCY")
        self.assertFailsClosed(self.mutated(lambda p: p["accepted_result_set"].__setitem__("case_count", "81")), "SCHEMA_VIOLATION")
        self.assertFailsClosed(self.mutated(lambda p: p["accepted_result_set"].__setitem__("case_count", True)), "SCHEMA_VIOLATION")
        self.assertFailsClosed(self.mutated(lambda p: p["accepted_result_set"].__setitem__("case_count", 80)), "CASE_UNIVERSE_INVALID")
        self.assertFailsClosed(
            self.mutated(lambda p: p["accepted_result_set"]["case_universe"]["beta_universe_h"].append(24)),
            "CASE_UNIVERSE_INVALID",
            "CROSS_BINDING_MISMATCH",
        )
        self.assertFailsClosed(self.mutated(lambda p: p["canonical_annual_input"].pop("git_blob_id")), "SCHEMA_VIOLATION")
        self.assertEqual(verify_object(ROOT, [])["failure_codes"], ["SCHEMA_NOT_AN_OBJECT"])

    def test_result_durability_statement_is_checked_against_git(self) -> None:
        durability = self.pointer["accepted_result_set"]["git_durability"]
        self.assertEqual((durability["result_files_git_tracked"], durability["status"]), (0, "LOCALLY_RETAINED_NOT_GIT_DURABLE"))
        self.assertEqual(self.pointer["accepted_result_set"]["registrations"]["files_under_run_root"], 651)
        self.assertFailsClosed(
            self.mutated(lambda p: p["accepted_result_set"]["git_durability"].__setitem__("result_files_git_tracked", 651)),
            "RESULT_DURABILITY_STATEMENT_STALE",
        )

    def test_local_results_are_verified_only_under_a_named_policy(self) -> None:
        """Hashes result files as opaque bytes; reads no result value."""

        run_root = ROOT / self.pointer["accepted_result_set"]["run_path"]
        metadata = cmp.verify_candidate_pointer(ROOT, CANDIDATE, results_policy=cmp.RESULTS_POLICY_METADATA)
        strict = cmp.verify_candidate_pointer(ROOT, CANDIDATE, results_policy=cmp.RESULTS_POLICY_STRICT)
        if not run_root.is_dir():
            # The result files are local-only: without them nothing may pass.
            for result in (metadata, strict):
                self.assertFailsClosed(result, "LOCAL_RESULTS_ABSENT")
                self.assertEqual(result["results_integrity"], cmp.RESULTS_FAIL)
            return
        self.assertCandidateConsistent(metadata)
        self.assertEqual(metadata["results_integrity"], cmp.RESULTS_METADATA_ONLY)
        self.assertNotIn("STRICT", metadata["results_integrity"])
        self.assertCandidateConsistent(strict)
        self.assertEqual(strict["results_integrity"], cmp.RESULTS_STRICT_PASS)
        self.assertEqual(strict["checks"][cmp.CHECK_RESULTS], cmp.STATUS_PASS)
        wrong = self.mutated(
            lambda p: p["accepted_result_set"]["run_file_aggregate"].__setitem__("sha256", "c" * 64),
            policy=cmp.RESULTS_POLICY_STRICT,
        )
        self.assertFailsClosed(wrong, "RUN_FILE_AGGREGATE_MISMATCH", "CROSS_BINDING_MISMATCH")
        self.assertEqual(wrong["results_integrity"], cmp.RESULTS_FAIL)

    def test_identities_inside_lists_are_hash_checked(self) -> None:
        inputs = self.pointer["economic_parameter_interfaces"]["execution_input_authority"]
        self.assertEqual(len(inputs), 4)
        tracked = {
            value["path"]
            for _location, _key, value, _parent in cmp._walk(self.pointer)
            if cmp._is_file_identity(value) and value["git_tracked"]
        }
        self.assertLessEqual({entry["path"] for entry in inputs}, tracked)
        self.assertEqual(self.result["file_identities"]["tracked"], len(tracked))
        section = "economic_parameter_interfaces"
        self.assertFailsClosed(
            self.mutated(lambda p: p[section]["execution_input_authority"][0].__setitem__("bytes", 1)),
            "RAW_BYTES_DIFFER_IN_CONTENT",
        )
        self.assertFailsClosed(
            self.mutated(lambda p: p[section]["execution_input_authority"][3].__setitem__("git_blob_id", "2" * 40)),
            "GIT_BLOB_MISMATCH_AT_ANCHOR_COMMIT",
        )

    def test_every_payload_value_is_verified_or_explicitly_descriptive(self) -> None:
        """One mutation per payload leaf: nothing in the pointer is decorative by accident."""

        if not (ROOT / self.pointer["accepted_result_set"]["run_path"]).is_dir():
            self.skipTest("the local result files are absent; the sweep runs under the metadata policy")
        paths = [path for path, _value in _leaves(self.pointer) if path[0] not in cmp.ENVELOPE_KEYS]
        targets = [path for path in paths if not any(cmp.is_descriptive_key(key) for key in path)]
        with ProcessPoolExecutor(max_workers=6) as pool:
            outcomes = dict(pool.map(_sweep_probe, targets, chunksize=8))
        unnoticed = sorted((path for path, noticed in outcomes.items() if not noticed), key=str)
        advisory = ("accepted_other_scope_not_bound_by_this_pointer", "historical_only")

        def explained(path: tuple) -> bool:
            return (
                path == ("pointer_revision",)  # the pointer's own name
                # bound by the per-case manifests, i.e. under the strict policy only
                or path == (*cmp._LAYERS, "execution_time_case_status")
                # advisory lists, enforced only as "must not overlap a bound path"
                or (path[0] == "roles" and path[1] in advisory)
            )

        self.assertEqual([path for path in unnoticed if not explained(path)], [])
        self.assertGreater(len(targets) - len(unnoticed), 550)
        self.assertLess(len(paths) - len(targets), 100, "descriptive text is growing")

    def test_verifier_output_carries_no_result_magnitude(self) -> None:
        strict = cmp.verify_candidate_pointer(ROOT, CANDIDATE, results_policy=cmp.RESULTS_POLICY_STRICT)
        text = json.dumps(strict)
        for term in ("objective", "mip_gap", "MIPGap", "e_n_kwh", "p_b_kw", "runtime_s", "capex"):
            self.assertNotIn(term, text)
        self.assertEqual(
            strict["zero_execution_counters"],
            {"solver_library_imports": 0, "model_constructions": 0, "optimize_calls": 0,
             "files_written": 0, "git_write_subcommands": 0},
        )


# ---------------------------------------------------------------------------
# Hermetic fixture layer
# ---------------------------------------------------------------------------


class FixtureCase(VerifierCase):
    base: Fixture

    @classmethod
    def setUpClass(cls) -> None:
        if not (ROOT / CANDIDATE).is_file():
            raise unittest.SkipTest(f"{CANDIDATE} is absent; it is the schema template of the fixture")
        cls.base = Fixture()

    @classmethod
    def tearDownClass(cls) -> None:
        cls.base.dispose()

    def fresh(self) -> Fixture:
        fixture = self.base.clone()
        self.addCleanup(fixture.dispose)
        return fixture

    def candidate(self, fixture: Fixture, policy: str = cmp.RESULTS_POLICY_NONE) -> dict:
        return cmp.verify_candidate_pointer(fixture.root, CANDIDATE, results_policy=policy)


class FixtureCandidateTests(FixtureCase):
    def test_fixture_is_hermetic(self) -> None:
        self.assertNotIn(str(ROOT.resolve()).lower(), str(self.base.root).lower())
        self.assertFalse((self.base.root / ".git" / "objects" / "info" / "alternates").exists())
        self.assertNotEqual(
            self.base.pointer["git_provenance"]["historical_execution_commit"],
            load_live_candidate()["git_provenance"]["historical_execution_commit"],
        )

    def test_fixture_candidate_verifies_under_every_policy(self) -> None:
        self.assertCandidateConsistent(self.candidate(self.base))
        metadata = self.candidate(self.base, cmp.RESULTS_POLICY_METADATA)
        self.assertCandidateConsistent(metadata)
        self.assertEqual(metadata["results_integrity"], cmp.RESULTS_METADATA_ONLY)
        strict = self.candidate(self.base, cmp.RESULTS_POLICY_STRICT)
        self.assertCandidateConsistent(strict)
        self.assertEqual(strict["results_integrity"], cmp.RESULTS_STRICT_PASS)

    def test_verification_is_read_only(self) -> None:
        fixture = self.fresh()

        def snapshot() -> dict[str, str]:
            return {
                path.relative_to(fixture.root).as_posix(): _sha(path.read_bytes())
                for path in sorted(fixture.root.rglob("*"))
                if path.is_file()
            }

        before = snapshot()
        self.assertCandidateConsistent(self.candidate(fixture, cmp.RESULTS_POLICY_STRICT))
        self.assertFailsClosed(cmp.verify_canonical_pointer(fixture.root, results_policy=cmp.RESULTS_POLICY_STRICT))
        self.assertEqual(snapshot(), before)
        self.assertFalse(fixture.path(CANONICAL).exists())

    def test_a_passing_candidate_is_never_promoted(self) -> None:
        fixture = self.fresh()
        self.assertCandidateConsistent(self.candidate(fixture, cmp.RESULTS_POLICY_STRICT))
        canonical = cmp.verify_canonical_pointer(fixture.root, results_policy=cmp.RESULTS_POLICY_STRICT)
        self.assertFailsClosed(canonical)
        self.assertEqual(canonical["failure_codes"], ["CANONICAL_POINTER_ABSENT"])
        self.assertFalse(fixture.path(CANONICAL).exists())
        with self.assertRaises(cmp.CurrentMainlinePointerError) as caught:
            cmp.require_current_mainline(fixture.root, purpose=cmp.PURPOSE_TECHNICAL_IDENTITY_VERIFICATION)
        self.assertEqual(caught.exception.code, "CANONICAL_POINTER_NOT_VERIFIED")
        self.assertEqual(caught.exception.result["failure_codes"], ["CANONICAL_POINTER_ABSENT"])

    def test_missing_local_results_prevent_any_results_pass(self) -> None:
        fixture = self.fresh()
        _dispose(fixture.path(fixture.pointer["accepted_result_set"]["run_path"]))
        for policy in (cmp.RESULTS_POLICY_METADATA, cmp.RESULTS_POLICY_STRICT):
            result = self.candidate(fixture, policy)
            self.assertFailsClosed(result, "LOCAL_RESULTS_ABSENT")
            self.assertEqual(result["results_integrity"], cmp.RESULTS_FAIL)
            self.assertEqual(result["checks"][cmp.CHECK_RESULTS], cmp.STATUS_FAIL)
        unchecked = self.candidate(fixture)
        self.assertCandidateConsistent(unchecked)
        self.assertEqual(unchecked["results_integrity"], cmp.RESULTS_NOT_CHECKED)
        self.assertEqual(unchecked["checks"][cmp.CHECK_RESULTS], cmp.STATUS_NOT_RUN)
        self.assertTrue(any("NOT checked" in note for note in unchecked["notes"]))

    def test_metadata_check_is_not_full_integrity(self) -> None:
        """A same-size content change passes metadata and fails strict."""

        fixture = self.fresh()
        run = fixture.pointer["accepted_result_set"]["run_path"]
        target = fixture.path(f"{run}/cases/a0.80_b08/result.json")
        data = bytearray(target.read_bytes())
        data[0] ^= 0x01
        target.write_bytes(bytes(data))
        metadata = self.candidate(fixture, cmp.RESULTS_POLICY_METADATA)
        self.assertCandidateConsistent(metadata)
        self.assertEqual(metadata["results_integrity"], cmp.RESULTS_METADATA_ONLY)
        self.assertTrue(any("not full integrity" in note for note in metadata["notes"]))
        strict = self.candidate(fixture, cmp.RESULTS_POLICY_STRICT)
        self.assertFailsClosed(
            strict, "REGISTERED_RESULT_HASH_MISMATCH", "CASE_REGISTRATION_MISMATCH", "RUN_FILE_AGGREGATE_MISMATCH"
        )
        self.assertEqual(strict["results_integrity"], cmp.RESULTS_FAIL)

    def test_missing_extra_or_altered_result_files_fail(self) -> None:
        run = self.base.pointer["accepted_result_set"]["run_path"]
        with self.subTest("one registered file is missing"):
            fixture = self.fresh()
            fixture.path(f"{run}/cases/a0.60_b04/dispatch.csv").unlink()
            for policy in (cmp.RESULTS_POLICY_METADATA, cmp.RESULTS_POLICY_STRICT):
                self.assertFailsClosed(
                    self.candidate(fixture, policy), "REGISTERED_RESULT_FILE_ABSENT", "RESULT_FILE_COUNT_MISMATCH"
                )
        with self.subTest("one whole case is missing"):
            fixture = self.fresh()
            _dispose(fixture.path(f"{run}/cases/a1.00_b12"))
            self.assertFailsClosed(self.candidate(fixture, cmp.RESULTS_POLICY_METADATA), "CASE_UNIVERSE_MISMATCH")
        with self.subTest("an unregistered file is present"):
            fixture = self.fresh()
            fixture.write(f"{run}/cases/a0.60_b04/extra.csv", b"x\n")
            self.assertFailsClosed(
                self.candidate(fixture, cmp.RESULTS_POLICY_METADATA), "UNREGISTERED_RESULT_FILE_PRESENT"
            )
        with self.subTest("a registered file changed size"):
            fixture = self.fresh()
            fixture.write(f"{run}/cases/a0.60_b04/dispatch.csv", b"different length\n")
            self.assertFailsClosed(
                self.candidate(fixture, cmp.RESULTS_POLICY_METADATA), "REGISTERED_RESULT_SIZE_MISMATCH"
            )
        with self.subTest("the root completion manifest was rewritten"):
            fixture = self.fresh()
            manifest = fixture.path(f"{run}/completion_manifest.json")
            payload = json.loads(manifest.read_bytes())
            payload["status"] = "CLOSED_ACCEPTED"
            manifest.write_bytes(_json_bytes(payload))
            self.assertFailsClosed(
                self.candidate(fixture, cmp.RESULTS_POLICY_METADATA),
                "ROOT_ARTIFACT_IDENTITY_MISMATCH",
                "CROSS_BINDING_MISMATCH",
            )
        with self.subTest("a result file became Git-tracked"):
            fixture = self.fresh()
            fixture.commit("track one result", [f"{run}/case_schedule.json"])
            self.assertFailsClosed(self.candidate(fixture), "RESULT_DURABILITY_STATEMENT_STALE")

    def test_a_link_cannot_stand_in_for_results(self) -> None:
        fixture = self.fresh()
        run = fixture.pointer["accepted_result_set"]["run_path"]
        outside = fixture.home / "outside_run"
        shutil.copytree(fixture.path(run), outside)
        _dispose(fixture.path(run))
        link = fixture.path(run)
        try:
            if os.name == "nt":
                import _winapi

                _winapi.CreateJunction(str(outside), str(link))
            else:
                os.symlink(outside, link, target_is_directory=True)
        except OSError as error:
            self.skipTest(f"this environment cannot create a directory link: {error}")
        try:
            for policy in cmp.RESULTS_POLICIES:
                result = self.candidate(fixture, policy)
                self.assertFailsClosed(result, "PATH_ESCAPES_REPOSITORY")
        finally:
            os.rmdir(link) if os.name == "nt" else os.unlink(link)

    def test_later_commits_preserving_identities_keep_the_pointer_valid(self) -> None:
        fixture = self.fresh()
        fixture.write("docs/later_unrelated_note.md", b"later additive work\n")
        later = fixture.commit("later additive commit", ["docs/later_unrelated_note.md"])
        result = self.candidate(fixture, cmp.RESULTS_POLICY_STRICT)
        self.assertCandidateConsistent(result)
        git = result["git"]
        self.assertEqual(git["live_head"], later)
        self.assertNotIn(later, fixture.pointer["git_provenance"]["ancestry_chain_oldest_to_newest"])
        self.assertFalse(git["live_head_equals_results_acceptance_publication_commit"])
        self.assertFalse(git["live_head_equals_upstream"])
        self.assertTrue(git["live_head_equality_is_not_required"])
        fixture.publish()
        self.assertCandidateConsistent(self.candidate(fixture))

    def test_a_later_commit_that_changes_a_bound_file_makes_the_pointer_stale(self) -> None:
        fixture = self.fresh()
        framework = fixture.pointer["methodology_authority"]["document"]["path"]
        fixture.write(framework, b"a later, different framework\n")
        fixture.commit("change the framework", [framework])
        fixture.publish()
        self.assertFailsClosed(
            self.candidate(fixture),
            "GIT_BLOB_CHANGED_IN_LIVE_HEAD",
            "RAW_BYTES_DIFFER_IN_CONTENT",
            "IDENTITY_AXIS_LIVE_DRIFT",
        )

    def test_raw_bytes_and_git_blobs_are_distinct_axes(self) -> None:
        relative = self.base.pointer["evidence_authority"]["document"]["path"]
        with self.subTest("an EOL-converted working tree is named as such"):
            fixture = self.fresh()
            target = fixture.path(relative)
            target.write_bytes(target.read_bytes().replace(b"\n", b"\r\n"))
            result = self.candidate(fixture)
            self.assertFailsClosed(result, "RAW_BYTES_DIFFER_BY_EOL_CONVERSION_ONLY")
            self.assertNotIn("RAW_BYTES_DIFFER_IN_CONTENT", result["failure_codes"])
            self.assertNotIn("GIT_BLOB_BYTES_MISMATCH", result["failure_codes"])
            self.assertNotIn("GIT_BLOB_CHANGED_IN_LIVE_HEAD", result["failure_codes"])
        with self.subTest("an edited working tree is a content difference"):
            fixture = self.fresh()
            fixture.write(relative, b"edited in the working tree only\n")
            result = self.candidate(fixture)
            self.assertFailsClosed(result, "RAW_BYTES_DIFFER_IN_CONTENT")
            self.assertNotIn("RAW_BYTES_DIFFER_BY_EOL_CONVERSION_ONLY", result["failure_codes"])
            self.assertNotIn("GIT_BLOB_CHANGED_IN_LIVE_HEAD", result["failure_codes"])
        with self.subTest("a bound file missing from the working tree"):
            fixture = self.fresh()
            fixture.path(relative).unlink()
            self.assertFailsClosed(self.candidate(fixture), "FILE_ABSENT")

    def test_publication_commits_must_be_the_commits_that_added_the_records(self) -> None:
        root, commits = self.base.root, self.base.commits

        def changed(change: Callable[[dict], Any]) -> dict:
            pointer = copy.deepcopy(self.base.pointer)
            change(pointer)
            return verify_object(root, pointer)

        # A later commit also contains the record, but it did not publish it.
        self.assertFailsClosed(
            changed(lambda p: p["production_generation"]["accepted_lifecycle_record"].__setitem__(
                "git_anchor_commit", commits["acceptance"])),
            "GIT_PATH_NOT_ADDED_BY_ANCHOR_COMMIT",
            "CROSS_BINDING_MISMATCH",
        )
        self.assertFailsClosed(
            changed(lambda p: p["canonical_annual_input"].__setitem__("git_anchor_role", cmp.ANCHOR_ADDED)),
            "GIT_PATH_NOT_ADDED_BY_ANCHOR_COMMIT",
        )
        self.assertFailsClosed(
            changed(lambda p: p["formal_results_acceptance"]["acceptance_closure"].__setitem__(
                "git_anchor_role", cmp.ANCHOR_CONTENT)),
            "POINTER_INTERNAL_INCONSISTENCY",
        )
        self.assertFailsClosed(
            changed(lambda p: p["evidence_authority"].__setitem__("acceptance_commit", commits["execution"])),
            "POINTER_INTERNAL_INCONSISTENCY",
        )
        self.assertFailsClosed(
            changed(lambda p: p["canonical_annual_input"].__setitem__("git_anchor_role", "ANYWHERE")),
            "SCHEMA_VIOLATION",
        )

    def test_case_status_layer_is_bound_by_strict_verification(self) -> None:
        pointer = copy.deepcopy(self.base.pointer)
        pointer["accepted_result_set"]["status_layers"]["execution_time_case_status"] = "CLOSED_ACCEPTED"
        strict = verify_object(self.base.root, pointer, policy=cmp.RESULTS_POLICY_STRICT)
        self.assertFailsClosed(strict, "CASE_REGISTRATION_MISMATCH")
        metadata = verify_object(self.base.root, pointer, policy=cmp.RESULTS_POLICY_METADATA)
        self.assertEqual(metadata["verdict"], cmp.VERDICT_CANDIDATE_CONSISTENT)
        self.assertEqual(metadata["results_integrity"], cmp.RESULTS_METADATA_ONLY)

    def test_unpublished_history_is_not_accepted_as_published(self) -> None:
        fixture = self.fresh()
        fixture.git("update-ref", "refs/remotes/origin/thesis-v7", fixture.commits["execution"])
        self.assertFailsClosed(self.candidate(fixture), "GIT_COMMIT_NOT_PUBLISHED_UPSTREAM")
        fixture.git("update-ref", "-d", "refs/remotes/origin/thesis-v7")
        self.assertFailsClosed(self.candidate(fixture), "UPSTREAM_REF_ABSENT")

    def test_conflicting_current_mainline_claims_are_detected(self) -> None:
        with self.subTest("a second candidate that stays a candidate is not a conflict"):
            fixture = self.fresh()
            fixture.write_pointer("configs/candidates/current_mainline_pointer_candidate_r2.json")
            self.assertCandidateConsistent(self.candidate(fixture))
        with self.subTest("a candidate file that claims authority"):
            fixture = self.fresh()
            rival = copy.deepcopy(fixture.pointer)
            rival["pointer_identity"]["is_current_authority"] = True
            fixture.write_pointer("configs/candidates/current_mainline_pointer_candidate_r2.json", rival)
            self.assertFailsClosed(self.candidate(fixture), "CONFLICTING_CURRENT_MAINLINE_CLAIM")
        with self.subTest("a pointer outside the sanctioned locations"):
            fixture = self.fresh()
            fixture.write_pointer("configs/current_mainline_pointer_v2.json")
            self.assertFailsClosed(self.candidate(fixture), "CONFLICTING_CURRENT_MAINLINE_CLAIM")

    def test_unreadable_pointers_fail_closed(self) -> None:
        fixture = self.fresh()
        fixture.write(CANDIDATE, b"{ not json")
        self.assertEqual(self.candidate(fixture)["failure_codes"], ["POINTER_NOT_VALID_JSON"])
        absent = cmp.verify_candidate_pointer(fixture.root, "configs/candidates/absent.json")
        self.assertEqual(absent["failure_codes"], ["POINTER_ABSENT"])
        escaped = cmp.verify_candidate_pointer(fixture.root, "../outside.json")
        self.assertEqual(escaped["failure_codes"], ["PATH_TRAVERSAL_SEGMENT"])
        for result in (absent, escaped):
            self.assertEqual(result["verdict"], cmp.VERDICT_FAIL_CLOSED)

    def test_no_solver_or_production_module_is_ever_loaded(self) -> None:
        script = (
            "import json, sys\n"
            f"sys.path.insert(0, {str(ROOT)!r})\n"
            "from src import current_mainline_pointer_v1 as m\n"
            f"r = m.verify_candidate_pointer({str(self.base.root)!r}, {CANDIDATE!r}, "
            "results_policy=m.RESULTS_POLICY_STRICT)\n"
            f"forbidden = {FORBIDDEN_RUNTIME_MODULES!r}\n"
            "loaded = sorted(n for n in sys.modules if n.split('.')[0] in forbidden)\n"
            "project = sorted(n for n in sys.modules if n.startswith('src.') and n != 'src.current_mainline_pointer_v1')\n"
            "print(json.dumps({'verdict': r['verdict'], 'integrity': r['results_integrity'], "
            "'loaded': loaded, 'project': project}))\n"
        )
        done = subprocess.run(
            [sys.executable, "-B", "-I", "-c", script], capture_output=True, check=False, cwd=self.base.home
        )
        self.assertEqual(done.returncode, 0, done.stderr.decode("utf-8", "replace"))
        report = json.loads(done.stdout.decode("utf-8"))
        self.assertEqual(report["verdict"], cmp.VERDICT_CANDIDATE_CONSISTENT)
        self.assertEqual(report["integrity"], cmp.RESULTS_STRICT_PASS)
        self.assertEqual(report["loaded"], [])
        self.assertEqual(report["project"], [])

    def test_command_line_reports_machine_readable_results(self) -> None:
        def run(*arguments: str) -> tuple[int, dict]:
            done = subprocess.run(
                [sys.executable, "-B", "-I", str(MODULE_PATH), *arguments, "--repo-root", str(self.base.root)],
                capture_output=True, check=False, cwd=self.base.home,
            )
            return done.returncode, json.loads(done.stdout.decode("utf-8"))

        code, result = run("candidate", "--pointer", CANDIDATE, "--results-policy", cmp.RESULTS_POLICY_STRICT)
        self.assertEqual((code, result["verdict"]), (0, cmp.VERDICT_CANDIDATE_CONSISTENT))
        self.assertFalse(result["is_current_authority"])
        code, result = run("canonical")
        self.assertEqual((code, result["verdict"]), (2, cmp.VERDICT_FAIL_CLOSED))
        self.assertEqual(result["failure_codes"], ["CANONICAL_POINTER_ABSENT"])


class FixtureCanonicalTests(FixtureCase):
    """The PROPOSED activation contract, exercised on synthetic artifacts only."""

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.activated = cls.base.clone()
        cls.canonical_pointer = cls.activated.activate()

    @classmethod
    def tearDownClass(cls) -> None:
        cls.activated.dispose()
        super().tearDownClass()

    def canonical(self, fixture: Fixture, policy: str = cmp.RESULTS_POLICY_STRICT) -> dict:
        return cmp.verify_canonical_pointer(fixture.root, results_policy=policy)

    def fresh_activated(self) -> Fixture:
        fixture = self.activated.clone()
        self.addCleanup(fixture.dispose)
        return fixture

    def test_an_accepted_published_canonical_pointer_verifies(self) -> None:
        result = self.canonical(self.activated)
        self.assertEqual(result["failures"], [])
        self.assertEqual(result["verdict"], cmp.VERDICT_CANONICAL_VERIFIED)
        self.assertTrue(result["is_current_authority"])
        self.assertEqual(result["results_integrity"], cmp.RESULTS_STRICT_PASS)
        self.assertTrue(result["results_consumption_permitted"])
        self.assertFalse(result["grants_execution_authority"])
        self.assertFalse(result["authority_conferred_by_this_verification"])
        self.assertEqual(result["checks"][cmp.CHECK_ACTIVATION], cmp.STATUS_PASS)
        self.assertEqual(
            result["pointer_payload_digest"],
            cmp.pointer_payload_digest(json.loads(self.activated.path(CANDIDATE).read_bytes())),
        )
        # The audited candidate still verifies as a candidate, and only as one.
        self.assertCandidateConsistent(self.candidate(self.activated))

    def test_results_consumption_needs_strict_verification(self) -> None:
        for policy in (cmp.RESULTS_POLICY_NONE, cmp.RESULTS_POLICY_METADATA):
            result = self.canonical(self.activated, policy)
            self.assertEqual(result["verdict"], cmp.VERDICT_CANONICAL_VERIFIED)
            self.assertFalse(result["results_consumption_permitted"])
            route = cmp.require_current_mainline(
                self.activated.root, purpose=cmp.PURPOSE_TECHNICAL_IDENTITY_VERIFICATION, results_policy=policy
            )
            self.assertIsNone(route["accepted_result_run_path"])
            self.assertFalse(route["results_consumption_permitted"])

    def test_the_route_is_served_only_for_a_permitted_purpose(self) -> None:
        route = cmp.require_current_mainline(
            self.activated.root, purpose=cmp.PURPOSE_TECHNICAL_IDENTITY_VERIFICATION
        )
        pointer = self.canonical_pointer
        self.assertEqual(route["accepted_result_run_path"], pointer["accepted_result_set"]["run_path"])
        self.assertEqual(route["methodology_authority"], pointer["methodology_authority"]["document"]["path"])
        self.assertEqual(route["production_generation"], pointer["production_generation"]["generation_id"])
        self.assertFalse(route["grants_execution_authority"])
        for purpose in (
            cmp.PURPOSE_SCIENTIFIC_INSPECTION, cmp.PURPOSE_RESULTS_ANALYSIS, cmp.PURPOSE_SUPERVISOR_DISCUSSION,
        ):
            with self.subTest(purpose=purpose), self.assertRaises(cmp.CurrentMainlinePointerError) as caught:
                cmp.require_current_mainline(self.activated.root, purpose=purpose)
            self.assertEqual(caught.exception.code, "PURPOSE_BLOCKED_BY_SCIENTIFIC_EXPOSURE_RESTRICTION")
        for purpose in ("FULL81_EXECUTION", "A2", "LAYER_B", "", "technical_identity_verification"):
            with self.subTest(purpose=purpose), self.assertRaises(cmp.CurrentMainlinePointerError) as caught:
                cmp.require_current_mainline(self.activated.root, purpose=purpose)
            self.assertEqual(caught.exception.code, "PURPOSE_NOT_PERMITTED")

    def test_missing_canonical_pointer_fails_closed_without_a_fallback(self) -> None:
        result = self.canonical(self.base)
        self.assertFailsClosed(result)
        self.assertEqual(result["failure_codes"], ["CANONICAL_POINTER_ABSENT"])
        self.assertEqual(result["pointer_path"], CANONICAL)
        self.assertTrue(self.base.path(CANDIDATE).is_file(), "a valid candidate exists and is not consulted")
        self.assertNotIn("git", result)

    def test_candidate_bytes_at_the_canonical_path_are_refused(self) -> None:
        fixture = self.fresh()
        candidate = json.loads(fixture.path(CANDIDATE).read_bytes())
        fixture.write_pointer(CANONICAL, candidate)
        self.assertFailsClosed(
            self.canonical(fixture), "CANONICAL_POINTER_IS_CANDIDATE_ONLY", "ACTIVATION_BASIS_ABSENT"
        )
        relabelled = copy.deepcopy(candidate)
        relabelled["pointer_identity"].update(
            lifecycle_state=cmp.LIFECYCLE_CANONICAL, is_candidate=False, is_accepted=True,
            is_canonical=True, is_current_authority=True, this_file_path=CANONICAL,
        )
        fixture.write_pointer(CANONICAL, relabelled)
        result = self.canonical(fixture)
        self.assertFailsClosed(result, "ACTIVATION_BASIS_ABSENT")
        fixture.commit("self-declared canonical pointer", [CANONICAL])
        fixture.publish()
        self.assertFailsClosed(self.canonical(fixture), "ACTIVATION_BASIS_ABSENT")

    def test_an_unpublished_canonical_pointer_is_refused(self) -> None:
        with self.subTest("edited in the working tree after publication"):
            fixture = self.fresh_activated()
            edited = copy.deepcopy(self.canonical_pointer)
            edited["pointer_identity"]["pointer_id"] = "EDITED_LOCALLY"
            fixture.write_pointer(CANONICAL, edited)
            self.assertFailsClosed(self.canonical(fixture), "CANONICAL_POINTER_NOT_PUBLISHED")
        with self.subTest("committed locally but not published upstream"):
            fixture = self.base.clone()
            self.addCleanup(fixture.dispose)
            published = fixture.git("rev-parse", "HEAD")
            fixture.activate()
            fixture.git("update-ref", "refs/remotes/origin/thesis-v7", published)
            self.assertFailsClosed(
                self.canonical(fixture), "GIT_COMMIT_NOT_PUBLISHED_UPSTREAM", "CANONICAL_POINTER_NOT_PUBLISHED"
            )
        with self.subTest("an in-memory variant of the published file"):
            variant = copy.deepcopy(self.canonical_pointer)
            variant["pointer_identity"]["pointer_id"] = "IN_MEMORY_VARIANT"
            result = verify_object(
                self.activated.root, variant, mode=cmp.MODE_CANONICAL, relative=CANONICAL,
                policy=cmp.RESULTS_POLICY_STRICT,
            )
            self.assertFailsClosed(result, "CANONICAL_OBJECT_NOT_THE_PUBLISHED_FILE")

    def test_a_canonical_payload_must_be_the_audited_candidate(self) -> None:
        fixture = self.base.clone()
        self.addCleanup(fixture.dispose)
        fixture.activate(tamper_payload=True)
        self.assertFailsClosed(
            self.canonical(fixture),
            "ACTIVATION_PAYLOAD_NOT_THE_AUDITED_CANDIDATE",
            "ACTIVATION_AUDIT_INVALID",
            "ACTIVATION_ACCEPTANCE_INVALID",
        )

    def test_activation_roles_cannot_be_aliased_or_substituted(self) -> None:
        fixture = self.base.clone()
        self.addCleanup(fixture.dispose)
        fixture.activate(alias_roles=True)
        self.assertFailsClosed(self.canonical(fixture), "ACTIVATION_ROLE_ALIASED", "ACTIVATION_ACCEPTANCE_INVALID")

        def substituted(role: str, location: tuple) -> dict:
            # An accepted, published record of ANOTHER lifecycle offered for a pointer role.
            clone = self.fresh_activated()
            pointer = copy.deepcopy(self.canonical_pointer)
            pointer["activation_basis"][role] = {
                key: cmp._lookup(pointer, location)[key]
                for key in (
                    "path", "sha256", "bytes", "git_tracked", "git_blob_id", "git_anchor_commit",
                    "git_anchor_role",
                )
            }
            clone.write_pointer(CANONICAL, pointer)
            clone.commit("substituted activation role", [CANONICAL])
            clone.publish()
            return self.canonical(clone)

        self.assertFailsClosed(
            substituted("acceptance_closure", (*cmp._ACCEPTANCE, "acceptance_closure")), "ACTIVATION_ACCEPTANCE_INVALID"
        )
        self.assertFailsClosed(
            substituted("independent_audit_record", (*cmp._ROLES, "independent_audit_pass")), "RECORD_UNREADABLE"
        )
        self.assertFailsClosed(
            substituted("independent_audit_record", (*cmp._AUDIT, "publication_manifest")), "ACTIVATION_AUDIT_INVALID"
        )

    def test_a_stale_canonical_pointer_is_refused(self) -> None:
        fixture = self.fresh_activated()
        core = fixture.pointer["implementation"]["scientific_model_core"]["path"]
        fixture.write(core, b"# a later model core\n")
        fixture.commit("change the model core", [core])
        fixture.publish()
        result = self.canonical(fixture)
        self.assertFailsClosed(result, "GIT_BLOB_CHANGED_IN_LIVE_HEAD", "IDENTITY_AXIS_LIVE_DRIFT")
        with self.assertRaises(cmp.CurrentMainlinePointerError):
            cmp.require_current_mainline(fixture.root, purpose=cmp.PURPOSE_TECHNICAL_IDENTITY_VERIFICATION)

    def test_canonical_pointer_survives_later_additive_commits(self) -> None:
        fixture = self.fresh_activated()
        fixture.write("docs/later_unrelated_note.md", b"later additive work\n")
        fixture.commit("later additive commit", ["docs/later_unrelated_note.md"])
        result = self.canonical(fixture)
        self.assertEqual(result["failures"], [])
        self.assertEqual(result["verdict"], cmp.VERDICT_CANONICAL_VERIFIED)

    def test_canonical_results_consumption_fails_closed_without_local_results(self) -> None:
        fixture = self.fresh_activated()
        _dispose(fixture.path(fixture.pointer["accepted_result_set"]["run_path"]))
        result = self.canonical(fixture)
        self.assertFailsClosed(result, "LOCAL_RESULTS_ABSENT")
        with self.assertRaises(cmp.CurrentMainlinePointerError):
            cmp.require_current_mainline(fixture.root, purpose=cmp.PURPOSE_TECHNICAL_IDENTITY_VERIFICATION)
        identity_only = self.canonical(fixture, cmp.RESULTS_POLICY_NONE)
        self.assertEqual(identity_only["verdict"], cmp.VERDICT_CANONICAL_VERIFIED)
        self.assertFalse(identity_only["results_consumption_permitted"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
