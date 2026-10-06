#!/usr/bin/env python3
"""R3-AUD-01 / R3-AUD-02 / R3-AUD-03 regression suite.

Candidate R3 received ``FAIL / NO-GO`` on five blocking findings. Three of them
are structural properties of the candidate package and of the production
authority bundle, and none of them had a test that could have caught it:

``R3-AUD-01`` (MAJOR)
    The candidate package used a MUTUAL raw-hash binding: the manifest bound
    the checkpoint's SHA-256 and the checkpoint also recorded a SHA-256 for the
    manifest. That contract is unsatisfiable by construction, and in practice
    the checkpoint carried a stale value no live byte reproduced.

``R3-AUD-02`` (MAJOR)
    ``.gitattributes`` coverage and the real raw-byte consumer set were
    maintained independently, so twelve historical accepted-lifecycle artifacts
    had no deterministic checkout rule. Under ``core.autocrlf=true`` all twelve
    became CRLF on a fresh checkout and Git still reported the tree clean.

``R3-AUD-03`` (CRITICAL)
    ``all_pins()`` declared a ``repository_eol_policy`` pin that
    ``verify_v7_4_authority_bundle()`` never verified, while
    ``verified_pin_count`` was reported from ``len(all_pins())``. Deleting
    ``.gitattributes`` outright still returned ``PASS``.

The tests below are deliberately *property* tests of the production objects,
not assertions about today's numbers. They fail closed when a future raw-byte
consumer is added without an EOL rule, when a pin group is declared but not
traversed, or when a package re-acquires a circular binding — which is what
makes them a drift guard rather than a snapshot.

Candidate R6 adds the controls for Candidate R5's two blocking findings:

``R5-AUD-01`` (CRITICAL)
    The checkpoint identity guard checked VALUE MEMBERSHIP only, so a lawful
    implementation digest printed under a "Manifest SHA-256" label passed.
    The controls below drive the real production validator against canonical
    identity claims whose ROLE is verified, value-for-pointer.

``R5-AUD-02`` (MAJOR)
    The disposable-write helper did not keep its target inside the disposable
    root.

Candidate R7 adds the controls for Candidate R6's two blocking findings, as
DEFECT CLASSES rather than examples:

``R6-AUD-01`` (CRITICAL)
    GATE mode accepted predecessor identities structurally, so lawful digests
    permuted between roles - claims rebound - passed. ``SemanticRoleOwnership
    Tests`` drives the real validator with a consistent-permutation attacker
    over every identity role, in a clean-checkout copy.

``R6-AUD-02`` (MAJOR)
    The name-based AST guard missed unsafe writers and teardown could delete
    through a junction. Every mutation in this module now goes through the
    runtime primitive :class:`_DisposableRoot`, attacked mutator by operand by
    ``DisposableWriteContainmentTests``; the AST lint is defence-in-depth.

Candidate R8 realigns the ``R6-AUD-01`` controls to Candidate R7's blocking
finding:

``R7-AUD-01`` (CRITICAL)
    R7's GATE took historical expected values from a table in candidate source,
    so a recomputing author could rewrite it with the rest of the package. Under
    contract V4 every historical value comes from the EXTERNAL historical
    authority (Git-frozen pre-R8 trust root -> accepted R7 binding ->
    authenticated R7 package). GATE fixtures therefore carry that evidence and a
    read-only shared Git object store (:class:`_DisposableExternalAuthorityRoot`);
    a clean checkout WITHOUT it now fails closed instead of passing; and every
    historical permutation is refused as an external-authority mismatch. The
    fully recomputing adversary - which also rewrites the bundle table and the
    implementation identity - is attacked separately in
    ``tests/test_21k_external_historical_authority_attacks.py``.

ZERO SOLVE. Every check is read-only: no production model is constructed, no
``optimize()`` is reachable, no case is run, nothing is staged or committed,
and no production validator is mocked. The negative controls that need a
mutated repository build a DISPOSABLE COPY under ``tempfile`` and never touch
the source repository; every mutation is runtime-contained first.
"""

from __future__ import annotations

import ast
import copy
import hashlib
import json
import re
import os
import stat
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path, PureWindowsPath

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src import production_authority_bundle_v7_4 as bundle  # noqa: E402
from src import production_authority_lifecycle_u06 as lc  # noqa: E402


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


SHA256_RE = re.compile(r"\b[0-9a-f]{64}\b")


def _enclosing_function(tree: ast.AST, target: ast.AST) -> str:
    """Name of the innermost function containing ``target``, or ``"<module>"``."""

    best = "<module>"
    best_span = None
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        start = node.lineno
        end = getattr(node, "end_lineno", start)
        if start <= getattr(target, "lineno", -1) <= end:
            span = end - start
            if best_span is None or span < best_span:
                best, best_span = node.name, span
    return best


# ---------------------------------------------------------------------------
# R5-AUD-02 / R6-AUD-02: every filesystem mutation is RUNTIME-CONTAINED
# ---------------------------------------------------------------------------
#
# Candidate R5 failed partly on ``R5-AUD-02``: the disposable-write helper
# could be aimed outside its root.  Candidate R6 then failed on ``R6-AUD-02``
# (MAJOR): its safety rested on an AST guard that recognised writers by NAME
# (so aliases, ``io.open``, ``Path.open``, ``getattr`` and friends were
# invisible to it), it allowed any write inside a function merely NAMED as a
# guarded writer, and its teardown trusted a root that was only checked to be
# "some directory under tempdir" - so a teardown could be turned against a
# target outside the fixture through a junction.
#
# Candidate R7 moves the boundary to RUNTIME.  :class:`_DisposableRoot` is the
# ONE containment primitive and the only code in this module that mutates the
# filesystem.  It is bound at creation to the identity (device, inode) of the
# directory ``tempfile.mkdtemp`` created, and EVERY mutating method - write,
# copy-in, unlink, rename, replace, subtree removal, link creation and teardown
# - validates its OWN operand immediately before the mutation:
#
# * the root must still be that same directory, not a link / junction /
#   reparse point, strictly under tempdir, and disjoint from the repository;
# * a relative operand is refused lexically if it is absolute, rooted,
#   drive-qualified, UNC, empty, has ``.`` / ``..`` / empty / trailing-dot or
#   trailing-space components, a reserved device name, NUL, ``:`` or any other
#   character Windows does not allow in a name;
# * no existing component of the operand (or of the root) may be a symbolic
#   link, junction or any other reparse point (``lstat``, never ``stat``);
# * the resolved target must be strictly inside the resolved root.
#
# Teardown never calls ``shutil.rmtree``: it walks the tree with ``lstat``,
# removes a link / junction / reparse point as the LINK itself (never
# descending into it), and re-validates every entry's operand before removing
# it.  No helper accepts a pre-validated path from a caller.
#
# The AST lint further below is defence-in-depth only: it keeps mutation APIs
# out of the rest of this module so that every mutation stays inside the
# primitive, but it does not - and does not claim to - prove containment.


class _DisposableEscape(RuntimeError):
    """A disposable-fixture operand that is not safely inside its own root."""


#: ``FILE_ATTRIBUTE_REPARSE_POINT`` / ``FILE_ATTRIBUTE_DIRECTORY`` (winnt.h).
_FILE_ATTRIBUTE_REPARSE_POINT = 0x400
_FILE_ATTRIBUTE_DIRECTORY = 0x10
_WINDOWS_INVALID_NAME_CHARS = frozenset('<>:"|?*')
_WINDOWS_RESERVED_NAMES = frozenset(
    {"CON", "PRN", "AUX", "NUL", "CONIN$", "CONOUT$"}
    | {f"COM{i}" for i in range(10)}
    | {f"LPT{i}" for i in range(10)}
)


def _is_link_or_reparse(st: os.stat_result) -> bool:
    """THE link decision: symlink, junction, or any other reparse point.

    Takes an ``lstat`` result, so it is a pure function of metadata and can be
    tested deterministically even where a link cannot be created.  On Windows
    every symbolic link and junction carries the reparse-point attribute.
    """

    return (
        stat.S_ISLNK(st.st_mode)
        or bool(getattr(st, "st_file_attributes", 0) & _FILE_ATTRIBUTE_REPARSE_POINT)
        or bool(getattr(st, "st_reparse_tag", 0))
    )


def _is_directory_entry(st: os.stat_result) -> bool:
    return stat.S_ISDIR(st.st_mode) or bool(
        getattr(st, "st_file_attributes", 0) & _FILE_ATTRIBUTE_DIRECTORY
    )


def _lexical_parts(relative: object) -> tuple[str, ...]:
    """The components of a relative operand, or :class:`_DisposableEscape`.

    Purely lexical: decides from the string alone, before any filesystem call.
    """

    # Exactly ``str``: a subclass could override the methods used below.
    if type(relative) is not str or not relative.strip():
        raise _DisposableEscape(f"unusable disposable operand {relative!r}")
    if any(ord(ch) < 32 for ch in relative):
        raise _DisposableEscape(f"control character in disposable operand {relative!r}")
    posix = relative.replace("\\", "/")
    windows = PureWindowsPath(relative)
    if posix.startswith("/") or windows.drive or windows.root or windows.anchor:
        raise _DisposableEscape(f"absolute, rooted, drive or UNC operand {relative!r}")
    parts = tuple(posix.split("/"))
    for part in parts:
        if part in ("", ".", ".."):
            raise _DisposableEscape(f"non-canonical or traversing operand {relative!r}")
        if part != part.rstrip(" ."):
            # Windows silently strips trailing dots and spaces, so ".. " and
            # "a." would alias ".." and "a".
            raise _DisposableEscape(f"trailing dot or space in operand {relative!r}")
        if _WINDOWS_INVALID_NAME_CHARS & set(part):
            raise _DisposableEscape(f"drive, stream or invalid name in operand {relative!r}")
        if part.split(".")[0].upper() in _WINDOWS_RESERVED_NAMES:
            raise _DisposableEscape(f"reserved device name in operand {relative!r}")
    return parts


class _DisposableRoot:
    """THE containment primitive: one identity-bound disposable directory.

    The only code in this module that mutates the filesystem.  Every public
    mutating method takes a RELATIVE operand and validates it itself, right
    before the mutation; none trusts a caller to have validated anything.
    """

    _PREFIX = "iris_r7_disposable_"
    #: Dunder members that ARE containment logic; every non-dunder member is.
    #: ``__enter__`` alone may be overridden: it is how a fixture is POPULATED,
    #: and population itself goes through the public mutators.
    _PROTECTED_DUNDERS = frozenset({"__init__", "__exit__", "__setattr__", "__init_subclass__"})

    def __init_subclass__(cls, **kwargs: object) -> None:
        super().__init_subclass__(**kwargs)
        overridden = {
            name
            for name in vars(cls)
            if name in vars(_DisposableRoot)
            and (not name.startswith("__") or name in _DisposableRoot._PROTECTED_DUNDERS)
        }
        if overridden:
            raise _DisposableEscape(
                f"{cls.__name__} may not override containment members {sorted(overridden)}"
            )

    def __setattr__(self, name: str, value: object) -> None:
        # The root identity is bound once, at creation; rebinding the PATH is
        # possible but is then refused by every operation (identity mismatch).
        if name == "_identity" and "_identity" in self.__dict__:
            raise _DisposableEscape("the disposable root identity is write-once")
        object.__setattr__(self, name, value)

    def __init__(self) -> None:
        created = Path(tempfile.mkdtemp(prefix=self._PREFIX))
        resolved = created.resolve(strict=True)
        st = os.lstat(resolved)
        self._path = resolved
        self._identity = (st.st_dev, st.st_ino)
        self._require_root()

    # -- the containment decision ---------------------------------------------

    @property
    def dir(self) -> Path:
        """The bound root.  Read-only: rebinding it is refused at runtime."""

        return self._path

    def _require_root(self) -> Path:
        """The root is still the directory this object created, and safe."""

        root = self._path
        temp = Path(tempfile.gettempdir()).resolve()
        repository = ROOT.resolve()
        try:
            st = os.lstat(root)
        except OSError as exc:
            raise _DisposableEscape(f"disposable root {root} is gone: {exc}") from exc
        if _is_link_or_reparse(st) or not _is_directory_entry(st):
            raise _DisposableEscape(f"disposable root {root} is a link or not a directory")
        if (st.st_dev, st.st_ino) != self._identity:
            raise _DisposableEscape(f"{root} is not the directory this fixture created")
        if root.resolve(strict=True) != root:
            raise _DisposableEscape(f"disposable root {root} resolves elsewhere")
        if root == temp or not root.is_relative_to(temp):
            raise _DisposableEscape(f"{root} is not a disposable directory under {temp}")
        if root.is_relative_to(repository) or repository.is_relative_to(root):
            raise _DisposableEscape(f"{root} overlaps the source repository {repository}")
        return root

    def _operand(self, relative: str, *, leaf_is_link: bool = False) -> Path:
        """Validate ONE operand immediately before it is mutated.

        ``leaf_is_link`` is used only to remove a link itself: every component
        but the last must still be a plain directory, and the last must be a
        link, which is then removed without being followed.
        """

        root = self._require_root()
        parts = _lexical_parts(relative)
        probe = root
        for position, part in enumerate(parts):
            probe = probe / part
            try:
                st = os.lstat(probe)
            except FileNotFoundError:
                break  # nothing below a missing component exists to traverse
            last = position == len(parts) - 1
            if _is_link_or_reparse(st) and not (leaf_is_link and last):
                raise _DisposableEscape(f"{relative!r} passes through a link at {probe}")
        target = root.joinpath(*parts)
        if leaf_is_link:
            if not target.parent.resolve(strict=True).is_relative_to(root):
                raise _DisposableEscape(f"{relative!r} has a parent outside {root}")
        elif not target.resolve(strict=False).is_relative_to(root) or target == root:
            raise _DisposableEscape(f"{relative!r} resolves outside {root}")
        return target

    def _ensure_parents(self, parts: tuple[str, ...]) -> None:
        for depth in range(1, len(parts)):
            relative = "/".join(parts[:depth])
            target = self._operand(relative)
            if not target.exists():
                target.mkdir()

    # -- mutating methods: each validates its own operand ---------------------

    def contained_write(self, relative: str, data: bytes) -> str:
        """Write ``data`` strictly inside the root; returns its SHA-256."""

        self._ensure_parents(_lexical_parts(relative))
        target = self._operand(relative)
        if os.path.lexists(target):
            st = os.lstat(target)
            # A hard link is not a reparse point, but writing through one
            # would change the bytes of every other name of that file.
            if not stat.S_ISREG(st.st_mode) or st.st_nlink != 1:
                raise _DisposableEscape(
                    f"{relative!r} is not a singly-linked regular file"
                )
        target.write_bytes(data)
        return hashlib.sha256(data).hexdigest()

    def contained_copy_in(self, source: Path, relative: str) -> str:
        """Copy repository bytes IN (the source is only read)."""

        return self.contained_write(relative, Path(source).read_bytes())

    def contained_unlink(self, relative: str) -> None:
        target = self._operand(relative)
        if not target.is_file():
            raise _DisposableEscape(f"{relative!r} is not a regular file")
        os.unlink(target)

    def contained_rename(self, source: str, destination: str) -> None:
        src = self._operand(source)
        dst = self._operand(destination)
        if dst.exists():
            raise _DisposableEscape(f"rename destination {destination!r} exists")
        os.rename(src, dst)

    def contained_replace(self, source: str, destination: str) -> None:
        src = self._operand(source)
        dst = self._operand(destination)
        os.replace(src, dst)

    def contained_remove_tree(self, relative: str) -> None:
        """Remove a subtree strictly inside the root, links as links only."""

        target = self._operand(relative)
        self._remove_entry(target)

    def contained_link(
        self,
        relative: str,
        outside: "_DisposableRoot",
        *,
        kind: str,
        outside_file: str | None = None,
    ) -> Path:
        """Create a link INSIDE the root (escape-attack fixture only).

        The link target must itself be another disposable root (or, for a
        ``hardlink``, a file inside one), so even a containment failure could
        never reach the repository.  ``kind`` is ``symlink`` / ``junction``
        (directory links) or ``hardlink``; ``unittest.SkipTest`` is raised when
        this platform or account cannot create that kind of link.
        """

        if not isinstance(outside, _DisposableRoot):
            raise _DisposableEscape("a link may only target another disposable root")
        target_dir = outside._require_root()
        link = self._operand(relative)
        if os.path.lexists(link):
            raise _DisposableEscape(f"{relative!r} already exists")
        if kind == "hardlink":
            source = outside._operand(str(outside_file))
            if not source.is_file():
                raise _DisposableEscape("a hard link may only name a regular file")
            os.link(source, link)
        elif kind == "symlink":
            try:
                os.symlink(target_dir, link, target_is_directory=True)
            except (OSError, NotImplementedError) as exc:
                raise unittest.SkipTest(f"symbolic links unavailable here: {exc}")
        elif kind == "junction":
            try:
                import _winapi
            except ImportError as exc:
                raise unittest.SkipTest(f"junctions unavailable here: {exc}")
            _winapi.CreateJunction(str(target_dir), str(link))
        else:
            raise _DisposableEscape(f"unknown link kind {kind!r}")
        return link

    def teardown(self) -> None:
        """Delete the root's contents and the root, never following a link."""

        root = self._require_root()
        for entry in sorted(os.scandir(root), key=lambda e: e.name):
            self._remove_entry(Path(entry.path))
        self._require_root()
        os.rmdir(root)

    def _remove_entry(self, path: Path) -> None:
        root = self._require_root()
        relative = path.relative_to(root).as_posix()
        st = os.lstat(path)
        if _is_link_or_reparse(st):
            link = self._operand(relative, leaf_is_link=True)
            if _is_directory_entry(st):
                os.rmdir(link)  # removes a junction / directory link itself
            else:
                os.unlink(link)
            return
        target = self._operand(relative)
        if _is_directory_entry(st):
            for entry in sorted(os.scandir(target), key=lambda e: e.name):
                self._remove_entry(Path(entry.path))
            self._operand(relative)
            os.rmdir(target)
        else:
            os.unlink(target)

    # -- context management ---------------------------------------------------

    def __enter__(self) -> "_DisposableRoot":
        self._require_root()
        return self

    def __exit__(self, *exc: object) -> None:
        self.teardown()


class _DisposableDir(_DisposableRoot):
    """An empty disposable root, for the containment primitive's own controls."""


# ---------------------------------------------------------------------------
# R3-AUD-01: acyclic candidate package binding
# ---------------------------------------------------------------------------


class AcyclicPackageBindingTests(unittest.TestCase):
    """The candidate package binding must be one-directional and exact."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.generation = lc.CURRENT_GENERATION
        cls.checkpoint_rel = cls.generation.candidate_checkpoint_path
        cls.manifest_rel = cls.generation.candidate_manifest_path
        cls.checkpoint_path = ROOT / cls.checkpoint_rel
        cls.manifest_path = ROOT / cls.manifest_rel
        cls.manifest = json.loads(cls.manifest_path.read_text(encoding="utf-8"))
        cls.checkpoint_text = cls.checkpoint_path.read_text(encoding="utf-8")

    def test_both_candidate_artifacts_exist(self) -> None:
        self.assertTrue(self.checkpoint_path.is_file(), self.checkpoint_rel)
        self.assertTrue(self.manifest_path.is_file(), self.manifest_rel)

    def test_manifest_binds_the_checkpoint_path_and_sha_exactly(self) -> None:
        entry = self.manifest["candidate_checkpoint"]
        self.assertEqual(entry["path"], self.checkpoint_rel)
        self.assertEqual(entry["sha256"], sha(self.checkpoint_path))
        self.assertEqual(self.manifest["candidate_checkpoint_path"], self.checkpoint_rel)

    def test_checkpoint_identifies_the_correct_manifest_path(self) -> None:
        self.assertIn(self.manifest_rel, self.checkpoint_text)
        self.assertEqual(self.manifest["candidate_manifest_path"], self.manifest_rel)

    def test_no_checkpoint_field_claims_the_manifest_raw_sha(self) -> None:
        """The core R3-AUD-01 control, now CLOSED-WORLD.

        R4-AUD-01 / N-R5D-02. This used to search the checkpoint only for the
        manifest's FINAL digest. R3-AUD-01 itself was a STALE manifest digest,
        which that search could never find. A checkpoint is finalized before
        the manifest that hashes it, so ANY manifest digest in it is
        necessarily stale - and it is caught because every raw identity in
        the checkpoint must be one the manifest itself accounts for.
        """

        identities, hidden = lc.collect_identity_pointers(self.manifest)
        self.assertEqual(hidden, [])
        owned = {lc.rfc6901_pointer(p): v for p, v in identities}
        accounted = set(owned.values())
        # R5-AUD-01 / contract V2: membership is not enough. Every raw identity
        # in the checkpoint is a canonical claim, and the manifest holds that
        # EXACT digest at that EXACT pointer - so its role is verified.
        parsed = lc.parse_checkpoint_identity_claims(self.checkpoint_text)
        self.assertEqual(parsed["outside_identities"], [])
        self.assertEqual(parsed["malformed"], [])
        self.assertIsNone(parsed["unterminated_block_line"])
        self.assertTrue(parsed["claims"], "the checkpoint states no identity at all")
        claimed_pointers = [pointer for _, pointer, _ in parsed["claims"]]
        self.assertEqual(len(claimed_pointers), len(set(claimed_pointers)))
        for line, pointer, digest in parsed["claims"]:
            with self.subTest(line=line, pointer=pointer):
                self.assertNotEqual(pointer, lc.CHECKPOINT_SELF_IDENTITY_POINTER)
                self.assertIn(pointer, owned)
                self.assertEqual(owned[pointer], digest)
        tokens = lc.checkpoint_identity_tokens(self.checkpoint_text)
        self.assertEqual(
            sorted(tokens), sorted(digest for _, _, digest in parsed["claims"])
        )
        # The manifest cannot account for its own digest, so neither can the
        # checkpoint; this is a consequence of the closed world, not a search.
        self.assertNotIn(sha(self.manifest_path), accounted)
        # And the checkpoint must not even name a manifest-SHA field.
        for forbidden in (
            "manifest_sha256",
            "manifest sha256",
            "manifest raw sha",
            "manifest_raw_sha256",
        ):
            self.assertNotIn(forbidden.lower(), self.checkpoint_text.lower())

    def test_the_predecessor_stale_sha_is_not_reused_as_a_binding(self) -> None:
        """The exact R3 stale value may appear only as recorded provenance.

        HISTORICAL EVIDENCE, retained. The R3-AUD-01 defect is recorded in the
        immutable Candidate R4 manifest; Candidate R5 records R4-AUD-01
        instead, and the R3 value may appear nowhere in R5 as an identity.
        """

        stale = (
            "11e76c887f9984b74a3b90ad1d47f409db13dfb5b37f1e1ea0adab3ce43070a7"
        )
        # It is not the live manifest digest, and not any live binding.
        self.assertNotEqual(stale, sha(self.manifest_path))
        self.assertNotEqual(stale, sha(self.checkpoint_path))
        self.assertNotEqual(self.manifest["candidate_checkpoint"]["sha256"], stale)
        identities, _ = lc.collect_identity_pointers(self.manifest)
        self.assertNotIn(stale, {value for _, value in identities})
        self.assertNotIn(stale, self.checkpoint_text)
        # Where it is recorded, it is recorded AS the predecessor defect, in
        # the immutable R4 bytes.
        r4 = json.loads(
            (ROOT / lc.FULL81_PREFLIGHT_AUTH_GUARD_R1_CANDIDATE_R4_MANIFEST_PATH)
            .read_text(encoding="utf-8")
        )
        defect = r4["package_binding"]["predecessor_defect"]
        self.assertEqual(defect["finding"], "R3-AUD-01")
        self.assertEqual(defect["r3_checkpoint_recorded_manifest_sha256"], stale)
        self.assertTrue(defect["stale"])

    def test_manifest_does_not_self_hash(self) -> None:
        """Semantic C8: no identity anywhere is tied to the manifest's own path.

        R4-AUD-01. The old control searched only for the FINAL digest, so the
        stale digest R4 stored against its own path passed it. Ownership is
        now established by semantic traversal, and the manifest's own durable
        entry may state nothing but its external binding.
        """

        own = self.manifest_rel
        identities, hidden = lc.collect_identity_pointers(self.manifest)
        self.assertEqual(hidden, [])
        for pointer, _ in identities:
            with self.subTest(pointer=pointer):
                self.assertNotIn(own, pointer)
                parent = self.manifest
                for segment in pointer[:-1]:
                    parent = parent[segment]
                if isinstance(parent, dict):
                    self.assertNotEqual(parent.get("path"), own)
        entry = self.manifest["durable_publication_declaration"]["entries"][own]
        self.assertEqual(
            set(entry), {"identity_source", "external_binding_fields"}
        )
        self.assertEqual(entry["identity_source"], "EXTERNAL_LIFECYCLE_ROLE_BINDING")
        report = lc.validate_candidate_manifest_identity_contract(
            ROOT, own, mode=lc.CANDIDATE_MANIFEST_MODE_CANDIDATE_PACKAGE
        )
        self.assertFalse(report["computed_binding_facts"]["manifest_records_own_sha256"])
        # Supplementary only: the final digest is absent too.
        self.assertNotIn(sha(self.manifest_path), self.manifest_path.read_text(encoding="utf-8"))

    def test_binding_contract_is_declared_acyclic(self) -> None:
        """Declared scheme plus COMPUTED facts; no hand-set self-label.

        R4-AUD-01. R4 declared seven binding booleans by hand and one of them
        (``placeholder_or_stale_sha_used=false``) was false. Those labels are
        now forbidden keys; the validator computes the facts instead.
        """

        binding = self.manifest["package_binding"]
        self.assertEqual(binding["scheme"], "ACYCLIC_MANIFEST_TO_CHECKPOINT_ONLY")
        self.assertEqual(binding["direction"], "manifest -> checkpoint")
        self.assertEqual(
            binding["manifest_self_identity"], "EXTERNAL_LIFECYCLE_ROLE_BINDING"
        )
        for label in (
            "manifest_binds_checkpoint_path",
            "manifest_binds_checkpoint_raw_sha256",
            "checkpoint_names_manifest_path",
            "checkpoint_records_manifest_raw_sha256",
            "manifest_records_own_sha256",
            "mutual_raw_hash_cycle_present",
            "placeholder_or_stale_sha_used",
        ):
            with self.subTest(self_label=label):
                self.assertNotIn(label, binding)
                self.assertIn(label, lc.CANDIDATE_MANIFEST_FORBIDDEN_KEYS)
        facts = lc.validate_candidate_manifest_identity_contract(
            ROOT, self.manifest_rel, mode=lc.CANDIDATE_MANIFEST_MODE_CANDIDATE_PACKAGE
        )["computed_binding_facts"]
        self.assertTrue(facts["manifest_binds_checkpoint_path"])
        self.assertTrue(facts["manifest_binds_checkpoint_raw_sha256"])
        self.assertFalse(facts["manifest_records_own_sha256"])
        self.assertFalse(facts["checkpoint_records_unaccounted_raw_sha256"])
        self.assertFalse(facts["mutual_raw_hash_cycle_present"])
        self.assertFalse(facts["placeholder_or_stale_sha_used"])

    def test_checkpoint_states_why_the_manifest_sha_is_omitted(self) -> None:
        """The omission must be explicit, not silent."""

        lowered = self.checkpoint_text.lower()
        self.assertIn("acyclic", lowered)
        self.assertIn("circular", lowered)
        self.assertIn("deliberately does not record", lowered)

    def test_changing_checkpoint_bytes_invalidates_the_manifest_binding(self) -> None:
        """The binding is not decorative: perturb the checkpoint and it fails."""

        declared = self.manifest["candidate_checkpoint"]["sha256"]
        perturbed = hashlib.sha256(
            self.checkpoint_path.read_bytes() + b"\n"
        ).hexdigest()
        self.assertNotEqual(perturbed, declared)
        # And the live bytes do satisfy it, so the control is not vacuous.
        self.assertEqual(sha(self.checkpoint_path), declared)

    def test_there_is_no_circular_hash_dependency(self) -> None:
        """Formally: the raw-hash graph is acyclic, from SEMANTIC edges.

        R4-AUD-01. The old control derived edges by searching for each
        artifact's FINAL digest, so a stale back-edge - the R3-AUD-01 and
        R4-AUD-01 defect class - produced no edge and passed. Edges are now the
        identity pointers the production validator VERIFIED against live
        bytes, and every identity in either artifact must be verified or
        explicitly structural, so a stale back-edge fails the contract
        instead of disappearing.
        """

        report = lc.validate_candidate_manifest_identity_contract(
            ROOT, self.manifest_rel, mode=lc.CANDIDATE_MANIFEST_MODE_CANDIDATE_PACKAGE
        )
        self.assertEqual(report["unaccounted_identity_count"], 0)
        ledger_rel = lc.CURRENT_GENERATION.candidate_change_ledger_path
        identities, _ = lc.collect_identity_pointers(self.manifest)
        node_of = {
            self.checkpoint_rel: "checkpoint",
            self.manifest_rel: "manifest",
            ledger_rel: "ledger",
        }
        node_sha = {name: sha(ROOT / rel) for rel, name in node_of.items()}
        edges: set[tuple[str, str]] = set()
        # Manifest edges: verified identity pointers naming a candidate artifact.
        for pointer, value in identities:
            parent = self.manifest
            for segment in pointer[:-1]:
                parent = parent[segment]
            target = parent.get("path") if isinstance(parent, dict) else None
            if target in node_of:
                self.assertEqual(sha(ROOT / target), value)
                edges.add(("manifest", node_of[target]))
        # Checkpoint edges: its role-verified claims (contract V2).
        claimed = {d for _, _, d in lc.parse_checkpoint_identity_claims(
            self.checkpoint_text
        )["claims"]}
        self.assertLessEqual(
            set(lc.checkpoint_identity_tokens(self.checkpoint_text)), claimed
        )
        # Ledger edges: every identity it states, closed-world.
        ledger = json.loads((ROOT / ledger_rel).read_bytes())
        ledger_values = {v for _, v in lc.collect_identity_pointers(ledger)[0]}
        for source, values in (("checkpoint", claimed), ("ledger", ledger_values)):
            for name, digest in node_sha.items():
                if digest in values:
                    edges.add((source, name))

        self.assertIn(("manifest", "checkpoint"), edges, "binding is missing")
        self.assertIn(("manifest", "ledger"), edges, "ledger binding is missing")
        self.assertNotIn(("checkpoint", "manifest"), edges, "cycle reintroduced")
        self.assertNotIn(("ledger", "manifest"), edges, "cycle reintroduced")
        self.assertNotIn(("ledger", "checkpoint"), edges, "back-edge from the ledger")
        for name in node_sha:
            self.assertNotIn((name, name), edges, f"{name} self-hashes")
        # Finalization order ledger < checkpoint < manifest: every edge points
        # from a later artifact to an earlier one.
        rank = {"ledger": 0, "checkpoint": 1, "manifest": 2}
        for source, target in edges:
            with self.subTest(edge=(source, target)):
                self.assertGreater(rank[source], rank[target])


# ---------------------------------------------------------------------------
# R3-AUD-02: complete EOL authority coverage, derived from primary source
# ---------------------------------------------------------------------------


class RawByteConsumerUniverseTests(unittest.TestCase):
    """The universe must be DERIVED, and must contain what it must contain."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.universe = lc.authority_raw_byte_consumer_universe(ROOT)

    def test_universe_is_non_trivial_and_fully_attributed(self) -> None:
        self.assertGreater(len(self.universe), 50)
        for path, reasons in self.universe.items():
            with self.subTest(path=path):
                self.assertTrue(reasons, f"{path} has no derivation reason")
                self.assertNotIn("<", path, "unresolvable import sentinel present")

    def test_universe_contains_every_bundle_pin_target(self) -> None:
        for pin in bundle.all_pins():
            with self.subTest(pin=pin.label):
                self.assertIn(pin.relative_path, self.universe)

    def test_universe_contains_every_implementation_and_validation_path(self) -> None:
        for path in lc.ACCEPTED_IMPLEMENTATION_PATHS:
            self.assertIn(path, self.universe)
        for path in lc.VALIDATION_IDENTITY_PATHS:
            self.assertIn(path, self.universe)

    def test_universe_contains_every_generation_lifecycle_path(self) -> None:
        for generation in lc.AUTHORITY_GENERATIONS:
            with self.subTest(generation=generation.generation_id):
                self.assertIn(generation.candidate_checkpoint_path, self.universe)
                self.assertIn(generation.candidate_manifest_path, self.universe)
                self.assertIn(
                    generation.accepted_lifecycle_record_path, self.universe
                )
                for path in generation.candidate_artifact_paths:
                    self.assertIn(path, self.universe)

    def test_universe_contains_the_twelve_audit_named_accepted_artifacts(self) -> None:
        """R3-AUD-02's twelve, as a SUBSET check, not as the definition.

        These are listed here only to prove the derivation reaches them. The
        production universe is not defined from this list — if it were, this
        suite would be re-encoding the very defect it exists to catch.
        """

        audit_named = (
            "docs/checkpoints/"
            "u_06_v7_4_production_authority_alignment_candidate_r3_2026-10-02.md",
            "results/provenance/"
            "u_06_v7_4_production_authority_alignment_candidate_r3_2026-10-02/"
            "alignment_manifest.json",
            "results/provenance/"
            "u_06_v7_4_production_authority_independent_audit_r3/"
            "independent_audit_pass_record.json",
            "results/provenance/"
            "u_06_v7_4_production_authority_acceptance_r3/acceptance_closure.json",
            "results/provenance/"
            "u_06_v7_4_production_authority_acceptance_r3/acceptance_manifest.json",
            "results/provenance/"
            "u_06_v7_4_production_authority_re_freeze_r3/"
            "production_authority_re_freeze_record.json",
            "docs/checkpoints/"
            "main_full81_authorization_mechanism_candidate_r2_2026-10-02.md",
            "results/provenance/"
            "main_full81_authorization_mechanism_candidate_r2_2026-10-02/"
            "authorization_mechanism_manifest.json",
            "results/provenance/"
            "main_full81_authorization_mechanism_independent_audit_r2/"
            "independent_audit_pass_record.json",
            "results/provenance/"
            "main_full81_authorization_mechanism_acceptance_r2/"
            "acceptance_closure.json",
            "results/provenance/"
            "main_full81_authorization_mechanism_acceptance_r2/"
            "acceptance_manifest.json",
            "results/provenance/"
            "main_full81_authorization_mechanism_re_freeze_r2/"
            "production_authority_re_freeze_record.json",
        )
        self.assertEqual(len(audit_named), 12)
        for path in audit_named:
            with self.subTest(path=path):
                self.assertIn(path, self.universe)
        # And the derivation finds strictly MORE than the twelve.
        self.assertGreater(len(self.universe), len(audit_named))

    def test_universe_reaches_role_records_through_on_disk_records(self) -> None:
        """The derivation step Candidate R3 had no equivalent of."""

        role_sourced = [
            path
            for path, reasons in self.universe.items()
            if any(r.startswith("ACCEPTED_LIFECYCLE_ROLE[") for r in reasons)
        ]
        self.assertGreaterEqual(len(role_sourced), 10, role_sourced)

    def test_universe_contains_every_preservation_package_file(self) -> None:
        for candidate, package in lc.CANDIDATE_PRESERVATION_PACKAGES.items():
            for key in ("archive", "index", "stop_record"):
                rel = f"{package['directory']}/{package[key]}"
                with self.subTest(candidate=candidate, file=key):
                    self.assertIn(rel, self.universe)
                    self.assertTrue((ROOT / rel).is_file(), rel)

    def test_universe_is_not_a_hand_written_list_in_this_module(self) -> None:
        """The production universe must not be defined by a test fixture."""

        overlay = (ROOT / "src/production_authority_lifecycle_u06.py").read_text(
            encoding="utf-8"
        )
        self.assertIn("def authority_raw_byte_consumer_universe", overlay)
        # The overlay must not contain a literal twelve-path block masquerading
        # as the derivation: the accepted-lifecycle role chain is reached by
        # reading on-disk records, so these paths are absent from the source.
        for path in (
            "results/provenance/"
            "u_06_v7_4_production_authority_independent_audit_r3/"
            "independent_audit_pass_record.json",
            "results/provenance/"
            "main_full81_authorization_mechanism_acceptance_r2/"
            "acceptance_closure.json",
        ):
            with self.subTest(path=path):
                self.assertNotIn(path, overlay)


class EolPolicyCoverageTests(unittest.TestCase):
    """Coverage must be complete, correctly typed, and fail closed."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.report = lc.eol_policy_coverage(ROOT)

    def test_coverage_is_satisfied(self) -> None:
        self.assertTrue(self.report["satisfied"], self.report["blocking_reason"])

    def test_uncovered_count_is_zero(self) -> None:
        self.assertEqual(self.report["uncovered_count"], 0, self.report["uncovered"])
        self.assertEqual(self.report["uncovered"], [])

    def test_every_universe_path_has_a_deterministic_checkout_rule(self) -> None:
        self.assertEqual(
            self.report["universe_path_count"], len(self.report["entries"])
        )
        for path, entry in self.report["entries"].items():
            with self.subTest(path=path):
                self.assertIsNotNone(entry["rule_pattern"], f"{path} has no rule")
                self.assertTrue(entry["deterministic"], entry)

    def test_canonical_non_lf_paths_keep_byte_preserving_treatment(self) -> None:
        """A CRLF or binary authority artifact must never get `text eol=lf`."""

        for path, entry in self.report["entries"].items():
            if entry["eol_class"] in ("CRLF", "MIXED", "BINARY"):
                with self.subTest(path=path, eol=entry["eol_class"]):
                    attributes = set(entry["rule_attributes"])
                    self.assertTrue(
                        attributes & {"-text", "binary"},
                        f"{path} is {entry['eol_class']} but is not byte-preserving",
                    )
                    self.assertNotIn("eol=lf", attributes)

    def test_the_known_canonical_crlf_artifacts_are_still_crlf(self) -> None:
        """Their canonical form is the pinned one; a silent flip is a failure."""

        for path in lc.CANONICAL_NON_LF_AUTHORITY_PATHS:
            with self.subTest(path=path):
                self.assertEqual(lc.canonical_eol_class(ROOT, path), "CRLF")
                self.assertTrue(
                    set(self.report["entries"][path]["rule_attributes"])
                    & {"-text", "binary"}
                )

    def test_parameter_registry_identity_is_the_crlf_form(self) -> None:
        registry = "data/reference/parameter_registry_v7_2.csv"
        pin = next(p for p in bundle.all_pins() if p.relative_path == registry)
        self.assertEqual(sha(ROOT / registry), pin.sha256)
        self.assertEqual(lc.canonical_eol_class(ROOT, registry), "CRLF")

    def test_no_broad_rule_reaches_the_unfiltered_historical_blobs(self) -> None:
        self.assertEqual(self.report["overreaching_rules"], [])
        for prefix in lc.DELIBERATELY_UNFILTERED_HISTORICAL_PREFIXES:
            directory = ROOT / prefix
            if not directory.is_dir():
                continue
            rules = lc._parse_eol_policy(
                (ROOT / lc.EOL_POLICY_RELATIVE_PATH).read_text(encoding="utf-8")
            )
            for candidate in sorted(directory.rglob("*")):
                if not candidate.is_file():
                    continue
                rel = candidate.relative_to(ROOT).as_posix()
                with self.subTest(path=rel):
                    self.assertIsNone(
                        lc.effective_eol_rule(rules, rel),
                        f"{rel} must remain entirely unfiltered",
                    )

    def test_policy_declares_no_extension_wide_or_repository_wide_rule(self) -> None:
        rules = lc._parse_eol_policy(
            (ROOT / lc.EOL_POLICY_RELATIVE_PATH).read_text(encoding="utf-8")
        )
        for pattern, _ in rules:
            with self.subTest(pattern=pattern):
                self.assertNotIn("*", pattern)
                self.assertNotIn("?", pattern)
                self.assertNotIn("[", pattern)
                self.assertNotEqual(pattern, "/")

    def test_every_rule_is_used_by_the_universe(self) -> None:
        """A rule matching nothing is drift: either over-broad or orphaned."""

        self.assertEqual(self.report["unused_rules"], [])

    def test_the_policy_file_itself_is_covered_and_pinned(self) -> None:
        entry = self.report["entries"][lc.EOL_POLICY_RELATIVE_PATH]
        self.assertTrue(entry["deterministic"])
        self.assertEqual(entry["eol_class"], "LF")
        pin = next(
            p for p in bundle.all_pins() if p.relative_path == lc.EOL_POLICY_RELATIVE_PATH
        )
        self.assertEqual(pin.label, "repository_eol_policy")
        self.assertEqual(sha(ROOT / lc.EOL_POLICY_RELATIVE_PATH), pin.sha256)

    def test_coverage_fails_closed_when_a_consumer_has_no_rule(self) -> None:
        """The guard is not vacuous: remove a rule and coverage must fail.

        Performed on a DISPOSABLE COPY of the policy text handed to the same
        production parser. The source repository's .gitattributes is never
        written to.
        """

        policy = (ROOT / lc.EOL_POLICY_RELATIVE_PATH).read_text(encoding="utf-8")
        victim = (
            "results/provenance/"
            "u_06_v7_4_production_authority_re_freeze_r3/"
            "production_authority_re_freeze_record.json"
        )
        self.assertIn(victim, policy)
        reduced = "\n".join(
            line for line in policy.splitlines() if not line.startswith(victim)
        )
        rules = lc._parse_eol_policy(reduced)
        self.assertIsNone(lc.effective_eol_rule(rules, victim))
        # ...while the unreduced policy does cover it.
        self.assertIsNotNone(
            lc.effective_eol_rule(lc._parse_eol_policy(policy), victim)
        )

    def test_coverage_fails_closed_when_the_policy_is_absent(self) -> None:
        with _DisposableDir() as fixture:
            report = lc.eol_policy_coverage(fixture.dir)
            self.assertFalse(report["satisfied"])
            self.assertFalse(report["policy_present"])
            self.assertIn("REPOSITORY_EOL_POLICY_MISSING", report["blocking_reason"])


# ---------------------------------------------------------------------------
# R3-AUD-03: declared/verified pin parity and fail-closed .gitattributes
# ---------------------------------------------------------------------------


class _DisposableRepo(_DisposableRoot):
    """A disposable copy of the authority surface, outside the source repo.

    Only the files the production verifier reads are copied, so the fixture is
    small; everything the bundle pins plus the policy file is present, which is
    what makes a PASS here meaningful. The fixture is derived from the live pin
    table rather than listed by hand, so it cannot fall behind a new pin.
    Every copy goes through the containment primitive.
    """

    def __enter__(self) -> "_DisposableRepo":
        for pin in bundle.all_pins():
            self.contained_copy_in(ROOT / pin.relative_path, pin.relative_path)
        return self


class BundlePinParityTests(unittest.TestCase):
    """Every declared pin is verified exactly once, and the count is honest."""

    def test_declared_inventory_is_well_formed(self) -> None:
        inventory = bundle.declared_pin_inventory()
        self.assertTrue(inventory["integrity_ok"])
        self.assertEqual(inventory["duplicate_labels"], [])
        self.assertEqual(inventory["duplicate_paths"], [])
        self.assertEqual(
            inventory["declared_label_count"], inventory["declared_unique_label_count"]
        )

    def test_all_pins_is_derived_from_the_declared_groups(self) -> None:
        """One declaration, not two lists that can drift apart."""

        from_groups = [pin.label for group in bundle.PIN_GROUPS.values() for pin in group]
        self.assertEqual([pin.label for pin in bundle.all_pins()], from_groups)

    def test_every_declared_group_is_traversed_by_the_verifier(self) -> None:
        """The exact R3-AUD-03 defect: a declared group left unverified."""

        with _DisposableRepo() as fixture:
            report = bundle.verify_v7_4_authority_bundle(fixture.dir)
        parity = report["pin_parity"]
        self.assertEqual(
            sorted(parity["verified_groups"]), sorted(parity["declared_groups"])
        )
        self.assertIn("repository_governance_authority", parity["verified_groups"])

    def test_declared_and_verified_pin_sets_are_exactly_equal(self) -> None:
        with _DisposableRepo() as fixture:
            report = bundle.verify_v7_4_authority_bundle(fixture.dir)
        parity = report["pin_parity"]
        self.assertEqual(parity["declared_but_unverified"], [])
        self.assertEqual(parity["verified_but_undeclared"], [])
        self.assertEqual(parity["verified_more_than_once"], [])
        self.assertTrue(parity["exact_set_equality"])

    def test_verified_pin_count_is_honest(self) -> None:
        """It counts pins actually hashed, never ``len(all_pins())``."""

        with _DisposableRepo() as fixture:
            report = bundle.verify_v7_4_authority_bundle(fixture.dir)
        verified_labels: set[str] = set()
        for group_name in bundle.PIN_GROUPS:
            key = {
                "methodology_evidence_authority": "methodology_evidence_authority",
                "task_3_authority": "task_3_authority",
                "governance_sequencing_successor": "governance_sequencing_successor",
                "implementation_authority": "implementation_authority",
                "alignment_surface": "alignment_surface",
                "repository_governance_authority": "repository_governance_authority",
                "inherited_v7_3_historical_authority": (
                    "inherited_v7_3_historical_authority"
                ),
            }[group_name]
            verified_labels.update(report[key])
        self.assertEqual(report["verified_pin_count"], len(verified_labels))
        self.assertEqual(report["verified_pin_count"], report["declared_pin_count"])
        self.assertEqual(
            report["pin_parity"]["count_source"],
            "ACTUALLY_VERIFIED_UNIQUE_PINS_NOT_LEN_ALL_PINS",
        )

    def test_the_repository_governance_group_is_emitted(self) -> None:
        with _DisposableRepo() as fixture:
            report = bundle.verify_v7_4_authority_bundle(fixture.dir)
        group = report["repository_governance_authority"]
        self.assertIn("repository_eol_policy", group)
        self.assertEqual(
            group["repository_eol_policy"]["path"], lc.EOL_POLICY_RELATIVE_PATH
        )

    # -- negative controls ------------------------------------------------

    def test_missing_gitattributes_fails_the_production_verifier_closed(self) -> None:
        """Negative control A. This returned PASS under Candidate R3."""

        with _DisposableRepo() as fixture:
            fixture.contained_unlink(lc.EOL_POLICY_RELATIVE_PATH)
            with self.assertRaises(bundle.ProductionAuthorityBundleError) as caught:
                bundle.verify_v7_4_authority_bundle(fixture.dir)
            self.assertEqual(caught.exception.status, "V7_4_AUTHORITY_ARTIFACT_MISSING")
            self.assertIn(".gitattributes", str(caught.exception))

    def test_altered_gitattributes_fails_the_production_verifier_closed(self) -> None:
        """Negative control B: one byte is enough."""

        with _DisposableRepo() as fixture:
            fixture.contained_write(
                lc.EOL_POLICY_RELATIVE_PATH,
                (fixture.dir / lc.EOL_POLICY_RELATIVE_PATH).read_bytes() + b"\n",
            )
            with self.assertRaises(bundle.ProductionAuthorityBundleError) as caught:
                bundle.verify_v7_4_authority_bundle(fixture.dir)
            self.assertEqual(caught.exception.status, "V7_4_AUTHORITY_HASH_FAIL")
            self.assertIn("repository_eol_policy", str(caught.exception))

    def test_substituted_gitattributes_fails_the_production_verifier_closed(
        self,
    ) -> None:
        """Negative control B': a different real file at the same path."""

        with _DisposableRepo() as fixture:
            fixture.contained_write(lc.EOL_POLICY_RELATIVE_PATH, b"* text=auto\n")
            with self.assertRaises(bundle.ProductionAuthorityBundleError) as caught:
                bundle.verify_v7_4_authority_bundle(fixture.dir)
            self.assertEqual(caught.exception.status, "V7_4_AUTHORITY_HASH_FAIL")

    def test_omitting_a_group_from_the_traversal_fails_parity(self) -> None:
        """Negative control C: simulate the R3 defect and prove parity catches it.

        The production verifier is NOT mocked into success; a group is removed
        from an ISOLATED copy of the declaration and the parity computation —
        the same comparison the verifier performs — is shown to fail. The live
        ``bundle.PIN_GROUPS`` is restored unconditionally.
        """

        original = bundle.PIN_GROUPS
        try:
            reduced = {
                name: group
                for name, group in original.items()
                if name != "repository_governance_authority"
            }
            bundle.PIN_GROUPS = reduced  # type: ignore[assignment]
            verified = [pin.label for group in reduced.values() for pin in group]
            declared = {pin.label for group in original.values() for pin in group}
            unverified = sorted(declared - set(verified))
            self.assertEqual(unverified, ["repository_eol_policy"])
            self.assertNotEqual(len(verified), len(declared))
        finally:
            bundle.PIN_GROUPS = original  # type: ignore[assignment]
        # The live declaration is intact and still verifies.
        self.assertIn("repository_governance_authority", bundle.PIN_GROUPS)
        self.assertEqual(
            len(bundle.declared_pin_inventory()["declared_labels"]), len(declared)
        )

    def test_a_duplicate_declared_pin_is_refused_before_hashing(self) -> None:
        """A duplicate label makes "verified exactly once" unprovable."""

        original = bundle.PIN_GROUPS
        try:
            duplicated = dict(original)
            duplicated["duplicate_probe"] = original["repository_governance_authority"]
            bundle.PIN_GROUPS = duplicated  # type: ignore[assignment]
            inventory = bundle.declared_pin_inventory()
            self.assertFalse(inventory["integrity_ok"])
            self.assertEqual(inventory["duplicate_labels"], ["repository_eol_policy"])
            with _DisposableRepo() as fixture:
                with self.assertRaises(bundle.ProductionAuthorityBundleError) as caught:
                    bundle.verify_v7_4_authority_bundle(fixture.dir)
                self.assertEqual(
                    caught.exception.status, "V7_4_AUTHORITY_PIN_DECLARATION_INVALID"
                )
        finally:
            bundle.PIN_GROUPS = original  # type: ignore[assignment]
        self.assertTrue(bundle.declared_pin_inventory()["integrity_ok"])

    def test_a_complete_pin_set_passes(self) -> None:
        """Negative controls are only meaningful if the positive control passes."""

        with _DisposableRepo() as fixture:
            report = bundle.verify_v7_4_authority_bundle(fixture.dir)
        self.assertEqual(report["status"], "PASS")
        self.assertEqual(
            report["verified_pin_count"], len(bundle.declared_pin_inventory()["declared_labels"])
        )


# ---------------------------------------------------------------------------
# R4-AUD-01: the closed-world candidate-manifest identity contract
# ---------------------------------------------------------------------------
#
# Candidate R4 failed on R4-AUD-01: its manifest froze a snapshot of the LIVE
# durable-publication report, so it carried stale digests for the checkpoint
# and for its OWN path while asserting that both matched, and no production
# validator read those fields. Every control below drives the REAL production
# validator. Defects are injected into an in-memory copy of the manifest, or
# into a DISPOSABLE copy of the files the validator reads; nothing in the
# source repository is written, and no validator is patched into success.

GEN = lc.CURRENT_GENERATION
R4_MANIFEST_REL = lc.FULL81_PREFLIGHT_AUTH_GUARD_R1_CANDIDATE_R4_MANIFEST_PATH
R4_CHECKPOINT_REL = lc.FULL81_PREFLIGHT_AUTH_GUARD_R1_CANDIDATE_R4_CHECKPOINT_PATH
R4_STOP_RECORD_REL = (
    lc.CANDIDATE_PRESERVATION_PACKAGES[
        "MAIN_FULL81_PREFLIGHT_AUTHORIZATION_GUARD_CANDIDATE_R4"
    ]["directory"]
    + "/independent_audit_stop_record.json"
)
R5_ID = "MAIN_FULL81_PREFLIGHT_AUTHORIZATION_GUARD_CANDIDATE_R5"
R5_MANIFEST_REL = lc.FULL81_PREFLIGHT_AUTH_GUARD_R1_CANDIDATE_R5_MANIFEST_PATH
R5_CHECKPOINT_REL = lc.FULL81_PREFLIGHT_AUTH_GUARD_R1_CANDIDATE_R5_CHECKPOINT_PATH
R6_ID = "MAIN_FULL81_PREFLIGHT_AUTHORIZATION_GUARD_CANDIDATE_R6"
R6_MANIFEST_REL = lc.FULL81_PREFLIGHT_AUTH_GUARD_R1_CANDIDATE_R6_MANIFEST_PATH
R6_CHECKPOINT_REL = lc.FULL81_PREFLIGHT_AUTH_GUARD_R1_CANDIDATE_R6_CHECKPOINT_PATH
R6_LEDGER_REL = lc.FULL81_PREFLIGHT_AUTH_GUARD_R1_CANDIDATE_R6_CHANGE_LEDGER_PATH
R7_ID = lc.R7_CANDIDATE_ID
R7_MANIFEST_REL = lc.FULL81_PREFLIGHT_AUTH_GUARD_R1_CANDIDATE_R7_MANIFEST_PATH
R7_CHECKPOINT_REL = lc.FULL81_PREFLIGHT_AUTH_GUARD_R1_CANDIDATE_R7_CHECKPOINT_PATH
R7_LEDGER_REL = lc.FULL81_PREFLIGHT_AUTH_GUARD_R1_CANDIDATE_R7_CHANGE_LEDGER_PATH
#: Contract V4 (R7-AUD-01): the status of EVERY historical-role disagreement -
#: a candidate claim (or the candidate table) against the external derivation.
EXTERNAL_MISMATCH = lc.EXTERNAL_HISTORICAL_AUTHORITY_MISMATCH
CANDIDATE_PACKAGE = lc.CANDIDATE_MANIFEST_MODE_CANDIDATE_PACKAGE
GATE = lc.CANDIDATE_MANIFEST_MODE_GATE
SELF_IDENTITY = "U06_CANDIDATE_MANIFEST_SELF_IDENTITY_REJECTED"
UNACCOUNTED = "U06_CANDIDATE_MANIFEST_IDENTITY_UNACCOUNTED"


def _encode(payload: object) -> bytes:
    """The candidate manifest's own serialization convention."""

    return (json.dumps(payload, indent=2) + "\n").encode("utf-8")


class _DisposableCandidateRoot(_DisposableRoot):
    """A disposable copy of what GATE-mode validation reads, outside the repo.

    Exactly a clean published checkout's view: the implementation paths, the
    durable-publication paths and the validation suites. Deliberately NO
    preservation package and NO predecessor artifact - those are ignored and
    unpublished, which is precisely the condition ``R6-AUD-01`` exploited.
    """

    def __enter__(self) -> "_DisposableCandidateRoot":
        for relative in (
            *lc.ACCEPTED_IMPLEMENTATION_PATHS,
            *lc.REQUIRED_DURABLE_PUBLICATION_PATHS,
            *lc.VALIDATION_IDENTITY_PATHS,
        ):
            self.contained_copy_in(ROOT / relative, relative)
        return self


def external_evidence_paths() -> tuple[str, ...]:
    """Every file the contract-V4 GATE reads beyond a clean checkout.

    Derived from the external historical authority itself, never listed by
    hand: the trust root, the binding it selects, every R1-R7 preservation and
    predecessor file its roles describe, and R7's whole preserved surface (the
    predecessor change set is computed over it).
    """

    authority = lc.resolve_external_historical_authority(ROOT)
    paths = {authority["trust_root"]["path"], authority["binding"]["path"]}
    paths.update(path for path, _ in authority["roles"].values() if path is not None)
    paths.update(authority["predecessor_surface"])
    return tuple(sorted(paths))


def git_metadata_files() -> tuple[tuple[str, bytes], ...]:
    """A minimal repository view: HEAD, refs and a READ-ONLY shared object store.

    The object store is reached through ``objects/info/alternates`` pointing at
    the source repository's objects, so the fixture writes no Git object and
    the source repository is only ever read.  Refs are copied as bytes, so a
    control can move or delete one inside the fixture with a contained write.
    """

    git = ROOT / ".git"
    files = [(".git/HEAD", (git / "HEAD").read_bytes())]
    if (git / "packed-refs").is_file():
        files.append((".git/packed-refs", (git / "packed-refs").read_bytes()))
    for directory, _, names in os.walk(git / "refs"):
        for name in names:
            path = Path(directory) / name
            files.append((".git/" + path.relative_to(git).as_posix(), path.read_bytes()))
    files.append((".git/config", b"[core]\n\trepositoryformatversion = 0\n\tbare = false\n"))
    files.append(
        (
            ".git/objects/info/alternates",
            (git / "objects").resolve().as_posix().encode("utf-8") + b"\n",
        )
    )
    return tuple(files)


class _DisposableExternalAuthorityRoot(_DisposableRoot):
    """A disposable GATE view WITH the external historical authority.

    A clean checkout's files plus exactly what contract V4 requires: the
    Git-frozen trust root reachable through Git (refs + shared read-only
    objects), the R7 binding it selects, and the R1-R7 preserved evidence.
    Every byte is written through the containment primitive.
    """

    def __enter__(self) -> "_DisposableExternalAuthorityRoot":
        for relative in sorted(
            {
                *lc.ACCEPTED_IMPLEMENTATION_PATHS,
                *lc.REQUIRED_DURABLE_PUBLICATION_PATHS,
                *lc.VALIDATION_IDENTITY_PATHS,
                *external_evidence_paths(),
            }
        ):
            self.contained_copy_in(ROOT / relative, relative)
        for relative, data in git_metadata_files():
            self.contained_write(relative, data)
        return self


class CandidateManifestIdentityContractTests(unittest.TestCase):
    """NC-01..NC-17 against the production candidate-manifest validator."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.raw = (ROOT / GEN.candidate_manifest_path).read_bytes()
        cls.manifest = json.loads(cls.raw)
        cls.r4_raw = (ROOT / R4_MANIFEST_REL).read_bytes()
        cls.r4 = json.loads(cls.r4_raw)
        r4_entries = cls.r4["required_durable_publication"]["entries"]
        # The exact stale values R4 recorded, read from R4's immutable bytes.
        cls.r4_checkpoint_stale = r4_entries[R4_CHECKPOINT_REL]["live_sha256"]
        cls.r4_manifest_own_stale = r4_entries[R4_MANIFEST_REL]["live_sha256"]

    # -- helpers ------------------------------------------------------------

    def mutated(self, mutate) -> bytes:
        payload = copy.deepcopy(self.manifest)
        mutate(payload)
        return _encode(payload)

    def rejected(
        self, manifest_bytes: bytes, *, mode: str = CANDIDATE_PACKAGE, root: Path = ROOT
    ) -> lc.U06LifecycleError:
        with self.assertRaises(lc.U06LifecycleError) as caught:
            lc.validate_candidate_manifest_identity_contract(
                root,
                GEN.candidate_manifest_path,
                generation=GEN,
                mode=mode,
                manifest_bytes=manifest_bytes,
            )
        return caught.exception

    @staticmethod
    def entries(payload: dict) -> dict:
        return payload["durable_publication_declaration"]["entries"]

    # -- NC-10: positive controls --------------------------------------------

    def test_nc10_the_lawful_candidate_package_passes_in_candidate_package_mode(
        self,
    ) -> None:
        report = lc.validate_candidate_manifest_identity_contract(
            ROOT, GEN.candidate_manifest_path, mode=CANDIDATE_PACKAGE
        )
        identities, hidden = lc.collect_identity_pointers(self.manifest)
        self.assertEqual(hidden, [])
        self.assertEqual(
            report["contract"],
            lc.FULL81_PREFLIGHT_AUTH_GUARD_R1_CANDIDATE_MANIFEST_CONTRACT_V4,
        )
        self.assertEqual(report["role_bound_identity_count"], len(identities))
        self.assertTrue(report["historical_pins_proved_against_preserved_bytes"])
        self.assertEqual(report["collected_identity_count"], len(identities))
        self.assertEqual(report["verified_identity_count"], len(identities))
        self.assertEqual(report["structural_identity_count"], 0)
        self.assertEqual(report["unaccounted_identity_count"], 0)
        self.assertEqual(report["conflict_count"], 0)
        self.assertEqual(
            report["obligation_classes"],
            ["C1", "C2", "C3", "C4", "C5", "C6", "C7", "C9"],
        )
        self.assertEqual(report["forbidden_identity_class"], "C8")
        ledger = report["change_ledger"]
        self.assertEqual(ledger["unaccounted_identity_count"], 0)
        self.assertEqual(ledger["structural_identity_count"], 0)
        self.assertEqual(
            ledger["verified_identity_count"], ledger["collected_identity_count"]
        )
        self.assertGreater(report["checkpoint_identity_claim_count"], 0)
        self.assertEqual(report["checkpoint_unclassified_identity_count"], 0)
        # Re-encoding the parsed manifest reproduces its exact bytes, so every
        # mutation below differs from the lawful manifest by the mutation only.
        self.assertEqual(_encode(self.manifest), self.raw)

    def test_nc10_gate_mode_binds_every_identity_to_the_external_authority(
        self,
    ) -> None:
        """R6-AUD-01 / R7-AUD-01: no structural identity, no candidate-held history.

        Under contract V2 this control asserted a NON-ZERO structural count in
        GATE mode; under V3 it asserted that GATE PASSED in a clean-checkout
        copy with no preservation package and no predecessor artifact - which is
        exactly the condition in which V3's GATE took historical truth from the
        candidate's own table (R7-AUD-01). Under V4 a clean checkout WITHOUT the
        external historical evidence fails closed, and every identity binds -
        in the live tree and in a copy that carries the evidence and the
        Git-frozen trust root - with every historical value derived externally.
        """

        with _DisposableCandidateRoot() as clean:
            for package in lc.CANDIDATE_PRESERVATION_PACKAGES.values():
                self.assertFalse((clean.dir / package["directory"]).exists())
            self.assertFalse(
                (clean.dir / lc.CONTRACT_V4_PREDECESSOR_DEFECT["manifest_path"]).exists()
            )
            with self.assertRaises(lc.U06LifecycleError) as caught:
                lc.validate_candidate_manifest_identity_contract(
                    clean.dir, GEN.candidate_manifest_path, mode=GATE
                )
            self.assertIn(
                caught.exception.status,
                {
                    lc.TRUST_ROOT_GIT_AUTHORITY_INVALID,
                    lc.EXTERNAL_HISTORICAL_AUTHORITY_UNAVAILABLE,
                },
            )
        with _DisposableExternalAuthorityRoot() as fixture:
            for root in (ROOT, fixture.dir):
                with self.subTest(root=str(root)):
                    report = lc.validate_candidate_manifest_identity_contract(
                        root, GEN.candidate_manifest_path, mode=GATE
                    )
                    self.assertEqual(report["unaccounted_identity_count"], 0)
                    self.assertEqual(report["structural_identity_count"], 0)
                    self.assertEqual(report["structural_pointers"], [])
                    self.assertEqual(
                        report["verified_identity_count"],
                        report["collected_identity_count"],
                    )
                    self.assertEqual(
                        report["role_bound_identity_count"],
                        report["collected_identity_count"],
                    )
                    self.assertFalse(
                        report["historical_pins_proved_against_preserved_bytes"]
                    )
                    self.assertTrue(
                        report["external_historical_authority"]["authenticated"]
                    )
                    self.assertFalse(
                        report["computed_binding_facts"][
                            "structural_only_identities_accepted"
                        ]
                    )
                    self.assertEqual(
                        report["change_ledger"]["structural_identity_count"], 0
                    )
                    roles = report["identity_roles"]
                    for pointer in (
                        "candidate_preservation_packages."
                        "MAIN_FULL81_PREFLIGHT_AUTHORIZATION_GUARD_CANDIDATE_R5."
                        "archive_sha256",
                        "candidate_preservation_packages."
                        "MAIN_FULL81_PREFLIGHT_AUTHORIZATION_GUARD_CANDIDATE_R7."
                        "stop_record_sha256",
                        "package_binding.predecessor_defect."
                        "predecessor_candidate_manifest.raw_sha256",
                        "implementation_identity.predecessor_digest",
                    ):
                        self.assertIn(pointer, roles)
                        self.assertTrue(lc.is_historical_role(roles[pointer]))

    # -- NC-01: R4-style stale checkpoint publication identity ---------------

    def test_nc01_stale_checkpoint_publication_identity_fails(self) -> None:
        stale = self.r4_checkpoint_stale
        self.assertNotEqual(stale, sha(ROOT / GEN.candidate_checkpoint_path))

        def frozen_live(p: dict) -> None:
            self.entries(p)[GEN.candidate_checkpoint_path]["live_sha256"] = stale

        def duplicate_expected(p: dict) -> None:
            self.entries(p)[GEN.candidate_checkpoint_path]["expected_raw_sha256"] = stale

        def stale_binding(p: dict) -> None:
            p["candidate_checkpoint"]["sha256"] = stale

        for label, mutate, status in (
            ("frozen_live_sha256", frozen_live, "U06_ROLE_SCHEMA_INVALID"),
            ("duplicate_checkpoint_digest", duplicate_expected, "U06_ROLE_SCHEMA_INVALID"),
            ("stale_primary_binding", stale_binding, "U06_ROLE_TARGET_MISMATCH"),
        ):
            with self.subTest(defect=label):
                self.assertEqual(self.rejected(self.mutated(mutate)).status, status)

    # -- NC-02 / NC-03: the manifest's own identity --------------------------

    def test_nc02_stale_own_sha_labelled_live_and_canonical_fails(self) -> None:
        def mutate(p: dict) -> None:
            own = self.entries(p)[GEN.candidate_manifest_path]
            own["live_sha256"] = self.r4_manifest_own_stale
            own["live_content_matches_canonical"] = True

        self.assertEqual(self.rejected(self.mutated(mutate)).status, SELF_IDENTITY)

    def test_nc03_any_own_path_identity_fails(self) -> None:
        own_path = GEN.candidate_manifest_path
        own_digest = sha(ROOT / own_path)

        def own_entry_digest(p: dict) -> None:
            self.entries(p)[own_path]["expected_raw_sha256"] = own_digest

        def own_path_anywhere(p: dict) -> None:
            p["lifecycle_state"]["own_identity"] = {"path": own_path, "sha256": own_digest}

        def own_entry_claim_without_digest(p: dict) -> None:
            self.entries(p)[own_path]["live_content_matches_canonical"] = True

        def own_entry_other_source(p: dict) -> None:
            self.entries(p)[own_path]["identity_source"] = "AUTHORITY_BUNDLE_PIN"

        for label, mutate in (
            ("own_entry_digest", own_entry_digest),
            ("own_path_anywhere", own_path_anywhere),
            ("own_entry_claim_without_digest", own_entry_claim_without_digest),
            ("own_entry_other_source", own_entry_other_source),
        ):
            with self.subTest(defect=label):
                self.assertEqual(self.rejected(self.mutated(mutate)).status, SELF_IDENTITY)

    # -- NC-04: live_content_matches_canonical -------------------------------

    def test_nc04_frozen_content_match_claim_fails(self) -> None:
        def mutate(p: dict) -> None:
            self.entries(p)[GEN.candidate_checkpoint_path][
                "live_content_matches_canonical"
            ] = True

        self.assertEqual(
            self.rejected(self.mutated(mutate)).status, "U06_ROLE_SCHEMA_INVALID"
        )

    def test_nc04_live_report_compares_content_and_never_trusts_presence(self) -> None:
        checkpoint = GEN.candidate_checkpoint_path
        own = GEN.candidate_manifest_path
        with _DisposableCandidateRoot() as fixture:
            report = lc.durable_publication_requirements(fixture.dir)
            self.assertIs(report["entries"][checkpoint]["live_content_matches_canonical"], True)
            self.assertIsNone(report["entries"][own]["live_content_matches_canonical"])

            # One byte appended: the file still EXISTS, its content no longer
            # matches the manifest's binding.
            fixture.contained_write(
                checkpoint, (ROOT / checkpoint).read_bytes() + b"\n"
            )
            report = lc.durable_publication_requirements(fixture.dir)
            entry = report["entries"][checkpoint]
            self.assertTrue(entry["live_present"])
            self.assertIs(entry["live_content_matches_canonical"], False)
            self.assertEqual(
                entry["canonical_identity_source"], "MANIFEST_CANDIDATE_CHECKPOINT_FIELD"
            )
            self.assertFalse(report["all_requirements_satisfied"])
            self.assertIsNone(report["entries"][own]["live_content_matches_canonical"])

            # No readable manifest binding: the comparison fails, it never passes.
            fixture.contained_write(own, b"{}\n")
            report = lc.durable_publication_requirements(fixture.dir)
            self.assertIs(
                report["entries"][checkpoint]["live_content_matches_canonical"], False
            )
            self.assertIsNone(report["entries"][checkpoint]["expected_sha256"])

    # -- NC-05: R4-style self-labels -----------------------------------------

    def test_nc05_self_label_claiming_no_stale_identity_is_forbidden(self) -> None:
        for key in ("placeholder_or_stale_sha_used", "manifest_records_own_sha256"):
            with self.subTest(self_label=key):
                def mutate(p: dict, key: str = key) -> None:
                    p["package_binding"][key] = False

                self.assertEqual(
                    self.rejected(self.mutated(mutate)).status, "U06_ROLE_SCHEMA_INVALID"
                )

    def test_nc05_r4_no_stale_self_label_is_contradicted_by_computation(self) -> None:
        # What R4 claimed about itself.
        self.assertIs(self.r4["package_binding"]["placeholder_or_stale_sha_used"], False)
        # What a semantic traversal of R4's own bytes computes, judged against
        # R4-ERA bytes: the audited R4 STOP archive member where one exists,
        # else the unchanged live file. Judging against today's tree would
        # misreport files R5 legitimately advanced (e.g. .gitattributes).
        package = lc.CANDIDATE_PRESERVATION_PACKAGES[
            "MAIN_FULL81_PREFLIGHT_AUTHORIZATION_GUARD_CANDIDATE_R4"
        ]
        with zipfile.ZipFile(
            ROOT / package["directory"] / package["archive"]
        ) as archive:
            members = {
                name: hashlib.sha256(archive.read(name)).hexdigest()
                for name in archive.namelist()
            }
        identities, _ = lc.collect_identity_pointers(self.r4)
        stale = sorted(
            pointer[2]
            for pointer, value in identities
            if pointer[:2] == ("required_durable_publication", "entries")
            and pointer[-1] == "live_sha256"
            and members.get(pointer[2], sha(ROOT / pointer[2])) != value
        )
        self.assertEqual(stale, sorted([R4_CHECKPOINT_REL, R4_MANIFEST_REL]))
        # Exactly the two the independent audit named, from its STOP record.
        stop = json.loads((ROOT / R4_STOP_RECORD_REL).read_text(encoding="utf-8"))
        named = {
            record["claimed_live_sha256"]
            for record in stop["blocking_findings"]["R4-AUD-01"][
                "observed_inconsistent_records"
            ]
            if "claimed_live_sha256" in record
        }
        self.assertEqual(named, {self.r4_checkpoint_stale, self.r4_manifest_own_stale})
        # HISTORICAL EVIDENCE: the immutable Candidate R5 manifest recorded
        # exactly that contradiction as typed R4-AUD-01 evidence. Candidate R6
        # does not restate it (its predecessor evidence is R5's); the record
        # stays provable from R4's and R5's preserved bytes.
        r5 = json.loads((ROOT / R5_MANIFEST_REL).read_bytes())
        defect = r5["package_binding"]["predecessor_defect"]
        self.assertEqual(defect["finding"], "R4-AUD-01")
        self.assertEqual(
            {e["recorded_value"] for e in defect["predecessor_stale_recorded_values"]},
            named,
        )
        labels = {
            tuple(e["predecessor_manifest_json_pointer"]): e["recorded_value"]
            for e in defect["predecessor_false_self_labels"]
        }
        self.assertIs(labels[("package_binding", "placeholder_or_stale_sha_used")], False)

    def test_nc05_corrupted_predecessor_evidence_is_rejected(self) -> None:
        """V4 predecessor evidence (R7) given lawful values of a DIFFERENT role.

        Rejected in BOTH modes.  The manifest alone is corrupted here, so the
        lawful ledger's predecessor values - themselves bound to the external
        historical authority - refuse it first through the ledger/manifest
        cross-consistency check, exactly as under V3.  The consistent
        manifest+ledger+claims variant is refused by the external authority
        itself (``SemanticRoleOwnershipTests`` and ``test_21k``).
        """

        r6_checkpoint = sha(ROOT / R6_CHECKPOINT_REL)
        r6_digest = json.loads((ROOT / R6_MANIFEST_REL).read_bytes())[
            "implementation_identity_digest"
        ]

        def r6_checkpoint_as_r7(p: dict) -> None:
            p["package_binding"]["predecessor_defect"][
                "predecessor_candidate_checkpoint"
            ]["raw_sha256"] = r6_checkpoint

        def r6_digest_as_r7(p: dict) -> None:
            p["implementation_identity"]["predecessor_digest"] = r6_digest

        for label, mutate in (
            ("r6_checkpoint_presented_as_r7", r6_checkpoint_as_r7),
            ("r6_digest_presented_as_r7", r6_digest_as_r7),
        ):
            for mode in (CANDIDATE_PACKAGE, GATE):
                with self.subTest(defect=label, mode=mode):
                    self.assertEqual(
                        self.rejected(self.mutated(mutate), mode=mode).status,
                        "U06_ROLE_TARGET_MISMATCH",
                    )

    def test_nc05_v4_predecessor_evidence_is_the_immediate_predecessor(self) -> None:
        defect = self.manifest["package_binding"]["predecessor_defect"]
        self.assertEqual(defect["predecessor_candidate_id"], R7_ID)
        self.assertEqual(defect["findings"], ["R7-AUD-01"])
        self.assertEqual(
            defect["predecessor_candidate_checkpoint"],
            {"path": R7_CHECKPOINT_REL, "raw_sha256": sha(ROOT / R7_CHECKPOINT_REL)},
        )
        self.assertEqual(
            defect["predecessor_candidate_manifest"],
            {"path": R7_MANIFEST_REL, "raw_sha256": sha(ROOT / R7_MANIFEST_REL)},
        )
        self.assertEqual(
            self.manifest["implementation_identity"]["predecessor_digest"],
            json.loads((ROOT / R7_MANIFEST_REL).read_bytes())[
                "implementation_identity_digest"
            ],
        )
        for removed in (
            "predecessor_stale_recorded_values",
            "predecessor_false_self_labels",
            "finding",
        ):
            self.assertNotIn(removed, defect)

    # -- NC-06: validator coverage parity ------------------------------------

    def test_nc06_a_no_op_obligation_verifier_fails_parity(self) -> None:
        verifiers = lc.CANDIDATE_MANIFEST_OBLIGATION_VERIFIERS
        original = verifiers["durable_pinned"]
        try:
            verifiers["durable_pinned"] = lambda context, items: (set(), set())
            error = self.rejected(self.raw)
            self.assertEqual(error.status, UNACCOUNTED)
            self.assertIn("parity", str(error))
        finally:
            verifiers["durable_pinned"] = original
        lc.validate_candidate_manifest_identity_contract(
            ROOT, GEN.candidate_manifest_path, mode=CANDIDATE_PACKAGE
        )

    def test_nc06_an_identity_whose_obligation_is_removed_is_unaccounted(self) -> None:
        original = lc.CANDIDATE_MANIFEST_IDENTITY_OBLIGATIONS
        try:
            lc.CANDIDATE_MANIFEST_IDENTITY_OBLIGATIONS = tuple(
                o for o in original if o.kind != "durable_pinned"
            )
            self.assertEqual(self.rejected(self.raw).status, UNACCOUNTED)
        finally:
            lc.CANDIDATE_MANIFEST_IDENTITY_OBLIGATIONS = original
        lc.validate_candidate_manifest_identity_contract(
            ROOT, GEN.candidate_manifest_path, mode=CANDIDATE_PACKAGE
        )

    def test_nc06_obligations_verifiers_and_identity_fields_are_in_bijection(self) -> None:
        obligations = lc.CANDIDATE_MANIFEST_IDENTITY_OBLIGATIONS
        self.assertEqual(
            {o.kind for o in obligations}, set(lc.CANDIDATE_MANIFEST_OBLIGATION_VERIFIERS)
        )
        self.assertEqual(
            {o.obligation_class for o in obligations},
            {"C1", "C2", "C3", "C4", "C5", "C6", "C7", "C9"},
        )
        self.assertEqual(lc.CANDIDATE_MANIFEST_FORBIDDEN_IDENTITY_CLASS, "C8")
        identity_fields = {
            field
            for field, cls in lc.CANDIDATE_MANIFEST_FIELD_CLASSES.items()
            if cls == lc.FIELD_CLASS_IDENTITY
        }
        self.assertEqual({o.pattern[0] for o in obligations}, identity_fields)
        for obligation in obligations:
            with self.subTest(pattern=obligation.pattern):
                # R6-AUD-01: an obligation names an independent AUTHORITY, never
                # a mode in which it may be skipped.
                self.assertIn(obligation.authority, lc.IDENTITY_AUTHORITY_SOURCES)
                self.assertFalse(hasattr(obligation, "scope"))
                owners = [
                    other
                    for other in obligations
                    if other is not obligation
                    and lc._pointer_matches(other.pattern, obligation.pattern)
                ]
                self.assertEqual(owners, [])

    # -- NC-09: predecessor substituted into the R5 role ---------------------

    def test_nc09_r4_payload_cannot_satisfy_the_current_contract(self) -> None:
        # (a) R4 exactly as written: it was written under no content contract.
        self.assertEqual(self.rejected(self.r4_raw).status, "U06_ROLE_SCHEMA_INVALID")
        # (b) Maximally cooperative relabel: every R4 identity string becomes
        # its current counterpart and the contract marker is added. R4's
        # schema still asserts a stale digest for the manifest's own path.
        text = self.r4_raw.decode("utf-8")
        for old, new in (
            (R4_MANIFEST_REL, GEN.candidate_manifest_path),
            (R4_CHECKPOINT_REL, GEN.candidate_checkpoint_path),
            (
                "MAIN_FULL81_PREFLIGHT_AUTHORIZATION_GUARD_CANDIDATE_R4",
                GEN.candidate_id,
            ),
        ):
            text = text.replace(old, new)
        relabelled = json.loads(text)
        relabelled["candidate_revision"] = GEN.candidate_id.rsplit("_", 1)[-1]
        relabelled["candidate_manifest_contract"] = GEN.candidate_manifest_contract
        self.assertEqual(self.rejected(_encode(relabelled)).status, SELF_IDENTITY)
        # (c) Marker added, R4 paths kept: the frozen live report is forbidden.
        marked = copy.deepcopy(self.r4)
        marked["candidate_manifest_contract"] = GEN.candidate_manifest_contract
        self.assertEqual(self.rejected(_encode(marked)).status, "U06_ROLE_SCHEMA_INVALID")

    def test_nc09_r5_payload_cannot_satisfy_the_current_contract(self) -> None:
        """R5 under its own V1 marker, and relabelled to the current candidate."""

        r5_raw = (ROOT / R5_MANIFEST_REL).read_bytes()
        # (a) As written: V1 is not a contract any generation may use now.
        error = self.rejected(r5_raw)
        self.assertEqual(error.status, "U06_ROLE_SCHEMA_INVALID")
        self.assertIn("candidate_manifest_contract", str(error))
        # (b) Maximally cooperative relabel to the current candidate and the V2
        # marker: R5's schema still lacks the bound change ledger and still
        # carries V1-only predecessor evidence, so it cannot fill the role.
        text = r5_raw.decode("utf-8")
        for old, new in (
            (R5_MANIFEST_REL, GEN.candidate_manifest_path),
            (R5_CHECKPOINT_REL, GEN.candidate_checkpoint_path),
            (R5_ID, GEN.candidate_id),
        ):
            text = text.replace(old, new)
        relabelled = json.loads(text)
        relabelled["candidate_revision"] = GEN.candidate_id.rsplit("_", 1)[-1]
        relabelled["candidate_manifest_contract"] = GEN.candidate_manifest_contract
        self.assertEqual(
            self.rejected(_encode(relabelled)).status, "U06_ROLE_SCHEMA_INVALID"
        )

    def test_nc09_r6_payload_cannot_satisfy_the_current_contract(self) -> None:
        """R6 under its own V2 marker, and relabelled to the current candidate."""

        r6_raw = (ROOT / R6_MANIFEST_REL).read_bytes()
        error = self.rejected(r6_raw)
        self.assertEqual(error.status, "U06_ROLE_SCHEMA_INVALID")
        self.assertIn("candidate_manifest_contract", str(error))
        text = r6_raw.decode("utf-8")
        for old, new in (
            (R6_MANIFEST_REL, GEN.candidate_manifest_path),
            (R6_CHECKPOINT_REL, GEN.candidate_checkpoint_path),
            (R6_LEDGER_REL, GEN.candidate_change_ledger_path),
            (R6_ID, GEN.candidate_id),
        ):
            text = text.replace(old, new)
        relabelled = json.loads(text)
        relabelled["candidate_revision"] = GEN.candidate_id.rsplit("_", 1)[-1]
        relabelled["candidate_manifest_contract"] = GEN.candidate_manifest_contract
        for mode in (CANDIDATE_PACKAGE, GATE):
            with self.subTest(mode=mode):
                self.assertIn(
                    self.rejected(_encode(relabelled), mode=mode).status,
                    {"U06_ROLE_SCHEMA_INVALID", "U06_ROLE_TARGET_MISMATCH"},
                )

    def test_nc09_r7_payload_cannot_satisfy_the_current_contract(self) -> None:
        """R7 under its own V3 marker, and relabelled to the current candidate."""

        r7_raw = (ROOT / R7_MANIFEST_REL).read_bytes()
        error = self.rejected(r7_raw)
        self.assertEqual(error.status, "U06_ROLE_SCHEMA_INVALID")
        self.assertIn("candidate_manifest_contract", str(error))
        text = r7_raw.decode("utf-8")
        for old, new in (
            (R7_MANIFEST_REL, GEN.candidate_manifest_path),
            (R7_CHECKPOINT_REL, GEN.candidate_checkpoint_path),
            (R7_LEDGER_REL, GEN.candidate_change_ledger_path),
            (R7_ID, GEN.candidate_id),
        ):
            text = text.replace(old, new)
        relabelled = json.loads(text)
        relabelled["candidate_revision"] = GEN.candidate_id.rsplit("_", 1)[-1]
        relabelled["candidate_manifest_contract"] = GEN.candidate_manifest_contract
        for mode in (CANDIDATE_PACKAGE, GATE):
            with self.subTest(mode=mode):
                self.assertIn(
                    self.rejected(_encode(relabelled), mode=mode).status,
                    {"U06_ROLE_SCHEMA_INVALID", "U06_ROLE_TARGET_MISMATCH", EXTERNAL_MISMATCH},
                )

    def test_nc09_no_predecessor_manifest_can_fill_the_current_role(self) -> None:
        """Every predecessor manifest of this lineage is barred, R1 through R7."""

        live_digest = lc.implementation_identity_digest(ROOT)
        predecessors = (
            lc.FULL81_PREFLIGHT_AUTH_GUARD_R1_CANDIDATE_MANIFEST_PATH,
            lc.FULL81_PREFLIGHT_AUTH_GUARD_R1_CANDIDATE_R2_MANIFEST_PATH,
            lc.FULL81_PREFLIGHT_AUTH_GUARD_R1_CANDIDATE_R3_MANIFEST_PATH,
            R4_MANIFEST_REL,
            R5_MANIFEST_REL,
            R6_MANIFEST_REL,
            R7_MANIFEST_REL,
        )
        for relative in predecessors:
            with self.subTest(predecessor=relative):
                self.assertIn(relative, GEN.candidate_artifact_paths)
                # By location: the role is pinned to the current manifest path.
                with self.assertRaises(lc.U06LifecycleError) as caught:
                    lc._validate_role_path(
                        "implementation_candidate",
                        relative,
                        GEN.accepted_lifecycle_record_path,
                        GEN,
                    )
                self.assertEqual(caught.exception.status, "U06_ROLE_TARGET_MISMATCH")
                raw = (ROOT / relative).read_bytes()
                payload = json.loads(raw)
                # By content, presented AS the current role record: the envelope
                # refuses a superseded candidate (or a foreign type/schema).
                with self.assertRaises(lc.U06LifecycleError) as caught:
                    lc.validate_role_envelope(
                        ROOT,
                        "implementation_candidate",
                        GEN.candidate_manifest_path,
                        payload,
                        live_digest=live_digest,
                        generation=GEN,
                    )
                self.assertIn(
                    caught.exception.status,
                    {
                        "U06_SUPERSEDED_CANDIDATE_REJECTED",
                        "U06_ROLE_ARTIFACT_TYPE_MISMATCH",
                        "U06_ROLE_SCHEMA_MISMATCH",
                    },
                )
                # And by the R5 content contract, which none was written under.
                self.assertEqual(self.rejected(raw).status, "U06_ROLE_SCHEMA_INVALID")

    def test_nc07_missing_or_altered_external_binding_declaration_is_rejected(
        self,
    ) -> None:
        """The manifest must declare exactly where its identity is bound."""

        own = GEN.candidate_manifest_path
        declared = list(lc.candidate_manifest_external_binding_fields(GEN))
        self.assertEqual(
            self.entries(self.manifest)[own]["external_binding_fields"], declared
        )

        def drop_audit_binding(p: dict) -> None:
            self.entries(p)[own]["external_binding_fields"].remove(declared[0])

        def drop_lifecycle_binding(p: dict) -> None:
            self.entries(p)[own]["external_binding_fields"].remove(declared[-1])

        def empty(p: dict) -> None:
            self.entries(p)[own]["external_binding_fields"] = []

        def foreign_binding(p: dict) -> None:
            self.entries(p)[own]["external_binding_fields"].append(
                "candidate_checkpoint.sha256"
            )

        for label, mutate, status in (
            ("drop_audit_binding", drop_audit_binding, "U06_ROLE_SCHEMA_INVALID"),
            ("drop_lifecycle_binding", drop_lifecycle_binding, "U06_ROLE_SCHEMA_INVALID"),
            ("empty", empty, "U06_ROLE_SCHEMA_INVALID"),
            ("foreign_binding", foreign_binding, "U06_ROLE_SCHEMA_INVALID"),
        ):
            with self.subTest(defect=label):
                self.assertEqual(self.rejected(self.mutated(mutate)).status, status)

        def no_declaration(p: dict) -> None:
            del self.entries(p)[own]["external_binding_fields"]

        # Removing the declaration altogether leaves the own entry asserting
        # something other than its external binding: a self-identity claim.
        self.assertEqual(self.rejected(self.mutated(no_declaration)).status, SELF_IDENTITY)

    # -- NC-11 / NC-12 / NC-13 ----------------------------------------------

    def test_nc11_duplicate_json_keys_are_rejected(self) -> None:
        decoy = '  "durable_publication_declaration": {"semantics": "LIVE_SNAPSHOT"},\n'
        injected = self.raw.decode("utf-8").replace("{\n", "{\n" + decoy, 1).encode("utf-8")
        # A lenient parser silently keeps the LAST key and sees a valid manifest.
        self.assertEqual(json.loads(injected), self.manifest)
        error = self.rejected(injected)
        self.assertEqual(error.status, "U06_ROLE_SCHEMA_INVALID")
        self.assertIn("duplicate JSON object key", str(error))

    def test_nc12_duplicate_missing_or_extra_durable_paths_are_rejected(self) -> None:
        extra = "data/reference/not_a_required_path.csv"

        def duplicate(p: dict) -> None:
            paths = p["durable_publication_declaration"]["required_paths"]
            paths.append(paths[0])

        def extra_path(p: dict) -> None:
            p["durable_publication_declaration"]["required_paths"].append(extra)

        def missing_path(p: dict) -> None:
            p["durable_publication_declaration"]["required_paths"].remove(
                GEN.candidate_checkpoint_path
            )

        def extra_entry(p: dict) -> None:
            self.entries(p)[extra] = {"identity_source": "AUTHORITY_BUNDLE_PIN"}

        def missing_entry(p: dict) -> None:
            del self.entries(p)[".gitattributes"]

        for label, mutate in (
            ("duplicate_path", duplicate),
            ("extra_path", extra_path),
            ("missing_path", missing_path),
            ("extra_entry", extra_entry),
            ("missing_entry", missing_entry),
        ):
            with self.subTest(defect=label):
                self.assertEqual(
                    self.rejected(self.mutated(mutate)).status, "U06_ROLE_SCHEMA_INVALID"
                )

    def test_nc13_conflicting_identities_for_one_path_are_rejected(self) -> None:
        # The R4-era EOL policy digest, read from R4's immutable bytes.
        r4_policy = self.r4["repository_eol_policy"]["sha256"]
        self.assertNotEqual(r4_policy, self.manifest["repository_eol_policy"]["sha256"])

        def restated(p: dict) -> None:
            p["repository_eol_policy"]["sha256"] = r4_policy

        def declared(p: dict) -> None:
            self.entries(p)[".gitattributes"]["expected_raw_sha256"] = r4_policy

        for label, mutate in (("restated_pin", restated), ("durable_declaration", declared)):
            with self.subTest(reference=label):
                error = self.rejected(self.mutated(mutate))
                self.assertEqual(error.status, "U06_ROLE_TARGET_MISMATCH")
                self.assertIn("conflicting identities", str(error))

    # -- NC-14: envelope constants -------------------------------------------

    def test_nc14_wrong_type_candidate_or_generation_is_rejected(self) -> None:
        cases = (
            ("artifact_type", "FULL81_PREFLIGHT_AUTH_GUARD_R1_INDEPENDENT_AUDIT_PASS",
             "U06_ROLE_ARTIFACT_TYPE_MISMATCH"),
            ("role", "independent_audit_pass", "U06_ROLE_ARTIFACT_TYPE_MISMATCH"),
            ("schema_version", "iris-thesis-u06-r3-implementation-candidate-v1",
             "U06_ROLE_SCHEMA_MISMATCH"),
            ("generation_id", "MAIN_FULL81_AUTHORIZATION_MECHANISM_R2",
             "U06_LINEAGE_MISMATCH"),
            ("lineage_id", "MAIN_FULL81_AUTHORIZATION_MECHANISM_R1",
             "U06_LINEAGE_MISMATCH"),
            ("candidate_id", "MAIN_FULL81_PREFLIGHT_AUTHORIZATION_GUARD_CANDIDATE_R3",
             "U06_SUPERSEDED_CANDIDATE_REJECTED"),
            ("target_candidate_id", "MAIN_FULL81_PREFLIGHT_AUTHORIZATION_GUARD_CANDIDATE_R4",
             "U06_SUPERSEDED_CANDIDATE_REJECTED"),
            ("candidate_id", "MAIN_FULL81_PREFLIGHT_AUTHORIZATION_GUARD_CANDIDATE_R6",
             "U06_SUPERSEDED_CANDIDATE_REJECTED"),
            ("candidate_id", "MAIN_FULL81_PREFLIGHT_AUTHORIZATION_GUARD_CANDIDATE_R7",
             "U06_SUPERSEDED_CANDIDATE_REJECTED"),
            ("candidate_id", "MAIN_FULL81_PREFLIGHT_AUTHORIZATION_GUARD_CANDIDATE_R9",
             "U06_ROLE_TARGET_MISMATCH"),
            ("self_accepted", True, "U06_SELF_ACCEPTANCE_REJECTED"),
        )
        for field, value, status in cases:
            with self.subTest(field=field, value=value):
                def mutate(p: dict, field: str = field, value: object = value) -> None:
                    p[field] = value

                self.assertEqual(self.rejected(self.mutated(mutate)).status, status)

    # -- NC-15: back-edges ---------------------------------------------------

    def test_nc15_a_lifecycle_identity_embedded_in_the_candidate_is_unaccounted(
        self,
    ) -> None:
        future_audit = hashlib.sha256(b"a future independent audit record").hexdigest()

        def mutate(p: dict) -> None:
            p["lifecycle_state"]["independent_audit_record"] = {
                "path": "results/provenance/future_audit/independent_audit_pass_record.json",
                "sha256": future_audit,
            }

        self.assertEqual(self.rejected(self.mutated(mutate)).status, UNACCOUNTED)

    def test_nc15_no_authority_or_policy_file_embeds_a_candidate_identity(self) -> None:
        candidate_paths = set(GEN.candidate_artifact_paths) | {
            GEN.accepted_lifecycle_record_path
        }
        pinned = {pin.relative_path for pin in bundle.all_pins()}
        self.assertEqual(pinned & candidate_paths, set())
        identities = {
            sha(ROOT / GEN.candidate_checkpoint_path),
            sha(ROOT / GEN.candidate_manifest_path),
            sha(ROOT / GEN.candidate_change_ledger_path),
        }
        for relative in sorted(
            set(lc.ACCEPTED_IMPLEMENTATION_PATHS)
            | pinned
            | set(lc.VALIDATION_IDENTITY_PATHS)
            | {lc.EOL_POLICY_RELATIVE_PATH}
        ):
            text = (ROOT / relative).read_bytes().decode("latin-1")
            for value in identities:
                with self.subTest(path=relative, identity=value[:12]):
                    self.assertNotIn(value, text)
        # The ledger is finalized before the checkpoint and the manifest, so it
        # may carry neither of their identities.
        ledger_text = (ROOT / GEN.candidate_change_ledger_path).read_text(encoding="utf-8")
        for value in (
            sha(ROOT / GEN.candidate_checkpoint_path),
            sha(ROOT / GEN.candidate_manifest_path),
        ):
            self.assertNotIn(value, ledger_text)

    # -- NC-16 / NC-17: identities hidden where none may be ------------------

    def test_nc16_raw_identity_hidden_in_prose_is_unaccounted(self) -> None:
        hidden = sha(ROOT / GEN.candidate_checkpoint_path)

        def in_scope(p: dict) -> None:
            p["scope"] = p["scope"] + f" (checkpoint {hidden})"

        def in_observation(p: dict) -> None:
            p["carried_findings"]["N-03"] = f"see {hidden}"

        def uppercase_identity(p: dict) -> None:
            p["lifecycle_state"]["note"] = hidden.upper()

        for label, mutate in (
            ("prose", in_scope),
            ("observation", in_observation),
            ("uppercase", uppercase_identity),
        ):
            with self.subTest(location=label):
                self.assertEqual(self.rejected(self.mutated(mutate)).status, UNACCOUNTED)

    def test_nc17_foreign_identity_injected_into_the_checkpoint_is_unaccounted(
        self,
    ) -> None:
        checkpoint = GEN.candidate_checkpoint_path
        for label, foreign in (
            ("stale_manifest_draft", hashlib.sha256(self.raw + b" ").hexdigest()),
            ("final_manifest_back_edge", sha(ROOT / GEN.candidate_manifest_path)),
            ("unrelated", hashlib.sha256(b"unrelated").hexdigest()),
        ):
            with self.subTest(identity=label), _DisposableExternalAuthorityRoot() as fixture:
                rebound = fixture.contained_write(
                    checkpoint,
                    (ROOT / checkpoint).read_bytes()
                    + f"\nManifest SHA-256: `{foreign}`\n".encode("utf-8"),
                )
                payload = copy.deepcopy(self.manifest)
                payload["candidate_checkpoint"]["sha256"] = rebound
                error = self.rejected(_encode(payload), mode=GATE, root=fixture.dir)
                self.assertEqual(error.status, UNACCOUNTED)
                self.assertIn(foreign, str(error))


# ---------------------------------------------------------------------------
# R5-AUD-01 / R5-AUD-02: semantic identity claims, the change ledger, and
# disposable-write containment
# ---------------------------------------------------------------------------


class CheckpointSemanticIdentityClaimTests(unittest.TestCase):
    """R5-AUD-01: a checkpoint identity is accepted only with its VERIFIED role.

    Every control runs the REAL production validator in GATE mode against a
    disposable copy of the candidate package (Candidate R8: carrying the
    external historical evidence contract V4 requires) whose checkpoint is mutated and
    whose manifest lawfully re-binds the mutated checkpoint - exactly the
    reproduction the R5 independent audit used. Nothing is mocked.
    """

    @classmethod
    def setUpClass(cls) -> None:
        cls.manifest = json.loads((ROOT / GEN.candidate_manifest_path).read_bytes())
        cls.checkpoint = (ROOT / GEN.candidate_checkpoint_path).read_text(
            encoding="utf-8"
        )
        identities, _ = lc.collect_identity_pointers(cls.manifest)
        cls.owned = {lc.rfc6901_pointer(p): v for p, v in identities}
        cls.claimed = {
            pointer
            for _, pointer, _ in lc.parse_checkpoint_identity_claims(cls.checkpoint)[
                "claims"
            ]
        }
        cls.digest = cls.manifest["implementation_identity_digest"]
        cls.ledger_digest = cls.manifest["candidate_change_ledger"]["sha256"]

    def status_of(self, checkpoint_text: str) -> str:
        with _DisposableExternalAuthorityRoot() as fixture:
            rebound = fixture.contained_write(
                GEN.candidate_checkpoint_path, checkpoint_text.encode("utf-8")
            )
            payload = copy.deepcopy(self.manifest)
            payload["candidate_checkpoint"]["sha256"] = rebound
            try:
                lc.validate_candidate_manifest_identity_contract(
                    fixture.dir,
                    GEN.candidate_manifest_path,
                    generation=GEN,
                    mode=GATE,
                    manifest_bytes=_encode(payload),
                )
            except lc.U06LifecycleError as exc:
                return exc.status
            return "PASS"

    @staticmethod
    def with_claims(text: str, *lines: str) -> str:
        return text + "\n```identity-claims\n" + "\n".join(lines) + "\n```\n"

    def unclaimed(self, *, shares_value_with_claimed: bool = False) -> str:
        """An owned identity pointer the lawful checkpoint does not claim."""

        claimed_values = {self.owned[p] for p in self.claimed}
        for pointer, value in sorted(self.owned.items()):
            if pointer in self.claimed or pointer == lc.CHECKPOINT_SELF_IDENTITY_POINTER:
                continue
            if shares_value_with_claimed and value not in claimed_values:
                continue
            return pointer
        self.fail("the lawful checkpoint leaves no identity pointer unclaimed")

    # -- positive controls ---------------------------------------------------

    def test_the_lawful_checkpoint_passes_the_gate(self) -> None:
        self.assertEqual(self.status_of(self.checkpoint), "PASS")
        parsed = lc.parse_checkpoint_identity_claims(self.checkpoint)
        self.assertGreater(len(parsed["claims"]), 0)
        self.assertEqual(parsed["outside_identities"], [])

    def test_lawful_value_under_its_correct_role_passes(self) -> None:
        pointer = self.unclaimed()
        self.assertEqual(
            self.status_of(self.with_claims(self.checkpoint, f"{pointer} {self.owned[pointer]}")),
            "PASS",
        )
        # The same digest lawfully held at two roles may be claimed at both:
        # that exact role/value binding is explicitly lawful in the manifest.
        shared = self.unclaimed(shares_value_with_claimed=True)
        self.assertIn(self.owned[shared], {self.owned[p] for p in self.claimed})
        self.assertEqual(
            self.status_of(self.with_claims(self.checkpoint, f"{shared} {self.owned[shared]}")),
            "PASS",
        )

    # -- R5-AUD-01: the audit's exact reproduction ----------------------------

    def test_the_exact_r5_audit_reproduction_now_fails(self) -> None:
        # Under V1 this passed: the value is a member of the manifest's
        # identity values. Membership is no longer what is checked.
        self.assertIn(self.digest, set(self.owned.values()))
        injected = self.checkpoint + f"\nManifest SHA-256: `{self.digest}`\n"
        self.assertEqual(self.status_of(injected), UNACCOUNTED)

    def test_lawful_value_under_a_wrong_role_fails(self) -> None:
        # (a) The canonical claim of one role carrying another role's digest.
        lines = self.checkpoint.split("\n")
        claim_line = f"/implementation_identity_digest {self.digest}"
        self.assertIn(claim_line, lines)
        swapped = "\n".join(
            f"/implementation_identity_digest {self.ledger_digest}"
            if line == claim_line
            else line
            for line in lines
        )
        self.assertEqual(self.status_of(swapped), "U06_ROLE_TARGET_MISMATCH")
        # (b) A new claim giving an unclaimed role a lawful digest of another.
        pointer = self.unclaimed()
        other = next(v for v in self.owned.values() if v != self.owned[pointer])
        self.assertEqual(
            self.status_of(self.with_claims(self.checkpoint, f"{pointer} {other}")),
            "U06_ROLE_TARGET_MISMATCH",
        )
        # (c) The implementation digest presented as a manifest identity: the
        # manifest has no such field, so there is no role it could hold.
        self.assertEqual(
            self.status_of(
                self.with_claims(self.checkpoint, f"/candidate_manifest/sha256 {self.digest}")
            ),
            UNACCOUNTED,
        )
        # (d) ... or as the checkpoint's own identity.
        self.assertEqual(
            self.status_of(
                self.with_claims(
                    self.checkpoint, f"{lc.CHECKPOINT_SELF_IDENTITY_POINTER} {self.digest}"
                )
            ),
            SELF_IDENTITY,
        )

    def test_unknown_value_fails(self) -> None:
        unknown = hashlib.sha256(b"a digest owned by nothing").hexdigest()
        self.assertNotIn(unknown, set(self.owned.values()))
        pointer = self.unclaimed()
        for label, text, status in (
            (
                "known_role_unknown_value",
                self.with_claims(self.checkpoint, f"{pointer} {unknown}"),
                "U06_ROLE_TARGET_MISMATCH",
            ),
            ("unknown_value_in_prose", self.checkpoint + f"\nSee `{unknown}`.\n", UNACCOUNTED),
            (
                "non_identity_field",
                self.with_claims(self.checkpoint, f"/scope {self.digest}"),
                UNACCOUNTED,
            ),
            (
                "non_canonical_pointer_spelling",
                self.with_claims(
                    self.checkpoint,
                    "/implementation_identity/paths/scripts/08_calibrate_kappa.py "
                    + self.manifest["implementation_identity"]["paths"][
                        "scripts/08_calibrate_kappa.py"
                    ],
                ),
                UNACCOUNTED,
            ),
        ):
            with self.subTest(defect=label):
                self.assertEqual(self.status_of(text), status)

    def test_duplicate_or_conflicting_ownership_fails(self) -> None:
        pointer = sorted(self.claimed)[0]
        other = next(v for v in self.owned.values() if v != self.owned[pointer])
        for label, line in (
            ("duplicate_claim", f"{pointer} {self.owned[pointer]}"),
            ("conflicting_claim", f"{pointer} {other}"),
        ):
            with self.subTest(defect=label):
                self.assertEqual(
                    self.status_of(self.with_claims(self.checkpoint, line)),
                    "U06_ROLE_SCHEMA_INVALID",
                )

    def test_hidden_or_unclassified_identity_fails(self) -> None:
        digest = self.digest
        for label, text in (
            ("table_cell", self.checkpoint + f"\n| Manifest SHA-256 | `{digest}` |\n"),
            ("other_fence", self.checkpoint + f"\n```text\n{digest}\n```\n"),
            (
                "labelled_claim_line",
                self.with_claims(
                    self.checkpoint, f"/implementation_identity/implementation_digest {digest} # Manifest SHA-256"
                ),
            ),
            (
                "uppercase_claim",
                self.with_claims(
                    self.checkpoint, f"/implementation_identity/implementation_digest {digest.upper()}"
                ),
            ),
            ("oversized_hex_run", self.checkpoint + f"\n{digest}0\n"),
            (
                "unterminated_block",
                self.checkpoint
                + f"\n```identity-claims\n/implementation_identity/implementation_digest {digest}\n",
            ),
            (
                "indented_fence",
                self.checkpoint
                + f"\n ```identity-claims\n/implementation_identity/implementation_digest {digest}\n```\n",
            ),
        ):
            with self.subTest(defect=label):
                self.assertEqual(self.status_of(text), UNACCOUNTED)

    def test_the_immutable_r5_checkpoint_has_unclassified_identities(self) -> None:
        """HISTORICAL: R5 stated digests in prose tables, roles unverified."""

        parsed = lc.parse_checkpoint_identity_claims(
            (ROOT / R5_CHECKPOINT_REL).read_text(encoding="utf-8")
        )
        self.assertEqual(parsed["claims"], [])
        self.assertGreater(len(parsed["outside_identities"]), 0)


class CandidateChangeLedgerTests(unittest.TestCase):
    """The change ledger is manifest-bound (C9) and closed-world."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.manifest = json.loads((ROOT / GEN.candidate_manifest_path).read_bytes())
        cls.raw = (ROOT / GEN.candidate_change_ledger_path).read_bytes()
        cls.ledger = json.loads(cls.raw)
        package = lc.CANDIDATE_PRESERVATION_PACKAGES[R7_ID]
        cls.r7_index = json.loads(
            (ROOT / package["directory"] / package["index"]).read_bytes()
        )
        with zipfile.ZipFile(ROOT / package["directory"] / package["archive"]) as archive:
            cls.r7_members = {
                name: hashlib.sha256(archive.read(name)).hexdigest()
                for name in archive.namelist()
            }

    def status_of(self, ledger: dict, mode: str = CANDIDATE_PACKAGE) -> str:
        try:
            lc.validate_candidate_change_ledger(
                ROOT, _encode(ledger), self.manifest, GEN, mode=mode
            )
        except lc.U06LifecycleError as exc:
            return exc.status
        return "PASS"

    def mutated(self, mutate) -> dict:
        ledger = copy.deepcopy(self.ledger)
        mutate(ledger)
        return ledger

    def modified(self, ledger: dict, path: str) -> dict:
        return next(e for e in ledger["modified_files"] if e["path"] == path)

    # -- positive controls ---------------------------------------------------

    def test_the_lawful_ledger_passes_in_both_modes(self) -> None:
        self.assertEqual(_encode(self.ledger), self.raw)
        package = lc.validate_candidate_change_ledger(
            ROOT, self.raw, self.manifest, GEN, mode=CANDIDATE_PACKAGE
        )
        self.assertEqual(package["structural_identity_count"], 0)
        self.assertEqual(
            package["verified_identity_count"], package["collected_identity_count"]
        )
        gate = lc.validate_candidate_change_ledger(
            ROOT, self.raw, self.manifest, GEN, mode=GATE
        )
        # R6-AUD-01: no ledger identity is structural in GATE mode any more.
        self.assertEqual(gate["structural_identity_count"], 0)
        self.assertEqual(gate["verified_identity_count"], gate["collected_identity_count"])
        self.assertEqual(gate["role_bound_identity_count"], gate["collected_identity_count"])
        self.assertFalse(gate["historical_pins_proved_against_preserved_bytes"])
        self.assertTrue(package["historical_pins_proved_against_preserved_bytes"])

    def test_the_ledger_reconstructs_the_r7_to_r8_change_set(self) -> None:
        """Independent recomputation: R7 index + R7 archive versus live bytes."""

        self.assertEqual(self.ledger["predecessor"]["candidate_id"], R7_ID)
        preserved = self.ledger["predecessor"]["preserved_identity"]
        self.assertEqual(
            preserved["implementation_digest"],
            self.r7_index["preserved_implementation_digest"],
        )
        self.assertEqual(
            preserved["checkpoint"]["raw_sha256"],
            self.r7_index["candidate_checkpoint"]["raw_sha256"],
        )
        self.assertEqual(
            preserved["manifest"]["raw_sha256"],
            self.r7_index["candidate_manifest"]["raw_sha256"],
        )
        eol = [
            m for m in self.r7_index["members"]
            if m["original_repository_path"] == lc.EOL_POLICY_RELATIVE_PATH
        ]
        self.assertEqual(len(eol), 1)
        self.assertEqual(preserved["repository_eol_policy"]["raw_sha256"], eol[0]["raw_sha256"])
        surface = {m["original_repository_path"]: m["raw_sha256"] for m in self.r7_index["members"]}
        for section in ("referenced_not_duplicated", "head_identical_dependencies"):
            surface.update({e["path"]: e["raw_sha256"] for e in self.r7_index[section]})
        changed = sorted(p for p, digest in surface.items() if sha(ROOT / p) != digest)
        self.assertEqual([e["path"] for e in self.ledger["modified_files"]], changed)
        for entry in self.ledger["modified_files"]:
            with self.subTest(path=entry["path"]):
                self.assertEqual(entry["predecessor_raw_sha256"], self.r7_members[entry["path"]])
                self.assertEqual(entry["candidate_raw_sha256"], sha(ROOT / entry["path"]))
        # The externally derived change set, and the candidate table's DIAGNOSTIC
        # assertion of it, are both exactly this independent recomputation.
        authority = lc.resolve_external_historical_authority(ROOT)
        self.assertEqual(sorted(lc.external_predecessor_change_set(ROOT, authority)), changed)
        asserted = sorted(
            e.relative_path
            for e in bundle.HISTORICAL_ROLE_IDENTITIES
            if e.role.startswith(lc.PREDECESSOR_MODIFIED_FILE_ROLE_PREFIX)
        )
        self.assertEqual(asserted, changed)
        self.assertEqual(
            self.ledger["candidate_artifact_paths"],
            {
                "checkpoint": GEN.candidate_checkpoint_path,
                "manifest": GEN.candidate_manifest_path,
                "change_ledger": GEN.candidate_change_ledger_path,
            },
        )
        for flag in ("production_solve", "main_full81_execution", "real_21c", "real_21d"):
            self.assertIs(self.ledger["execution_status"][flag], False)

    def test_the_manifest_binds_the_exact_ledger_bytes(self) -> None:
        report = lc.validate_candidate_manifest_identity_contract(
            ROOT, GEN.candidate_manifest_path, mode=CANDIDATE_PACKAGE
        )
        self.assertIn("candidate_change_ledger.sha256", report["verified_pointers"])
        payload = copy.deepcopy(self.manifest)
        payload["candidate_change_ledger"]["sha256"] = hashlib.sha256(
            self.raw + b"\n"
        ).hexdigest()
        with self.assertRaises(lc.U06LifecycleError) as caught:
            lc.validate_candidate_manifest_identity_contract(
                ROOT,
                GEN.candidate_manifest_path,
                generation=GEN,
                mode=GATE,
                manifest_bytes=_encode(payload),
            )
        self.assertEqual(caught.exception.status, "U06_ROLE_TARGET_MISMATCH")

    # -- negative controls ---------------------------------------------------

    def test_wrong_or_incomplete_change_records_fail(self) -> None:
        overlay = "src/production_authority_lifecycle_u06.py"
        with zipfile.ZipFile(
            ROOT
            / lc.CANDIDATE_PRESERVATION_PACKAGES[R6_ID]["directory"]
            / "candidate_r6_raw_bytes.zip"
        ) as archive:
            r6_overlay = hashlib.sha256(archive.read(overlay)).hexdigest()
        bundle_sha = sha(ROOT / "src/production_authority_bundle_v7_4.py")

        def r6_bytes_as_predecessor(ledger: dict) -> None:
            self.modified(ledger, overlay)["predecessor_raw_sha256"] = r6_overlay

        def omitted_file(ledger: dict) -> None:
            ledger["modified_files"] = [
                e for e in ledger["modified_files"] if e["path"] != overlay
            ]

        def wrong_candidate_identity(ledger: dict) -> None:
            self.modified(ledger, overlay)["candidate_raw_sha256"] = bundle_sha

        # R6-AUD-01: every one of these fails in GATE mode too.  R7-AUD-01: the
        # two historical defects (a predecessor value, the change set itself)
        # are refused by the EXTERNAL historical authority; the candidate-side
        # defect by live bytes.
        for label, mutate, status in (
            ("r6_bytes_as_predecessor", r6_bytes_as_predecessor, EXTERNAL_MISMATCH),
            ("omitted_modified_file", omitted_file, EXTERNAL_MISMATCH),
            ("wrong_candidate_identity", wrong_candidate_identity, "U06_ROLE_TARGET_MISMATCH"),
        ):
            for mode in (CANDIDATE_PACKAGE, GATE):
                with self.subTest(defect=label, mode=mode):
                    self.assertEqual(self.status_of(self.mutated(mutate), mode), status)

    def test_a_ledger_identity_of_a_later_artifact_is_rejected(self) -> None:
        def states_checkpoint(ledger: dict) -> None:
            ledger["modified_files"].append(
                {
                    "path": GEN.candidate_checkpoint_path,
                    "predecessor_raw_sha256": hashlib.sha256(b"before").hexdigest(),
                    "candidate_raw_sha256": sha(ROOT / GEN.candidate_checkpoint_path),
                    "classification": "CANDIDATE_POINTER_ADVANCE",
                    "summary": "attempted back-edge",
                }
            )
            ledger["modified_files"].sort(key=lambda e: e["path"])

        self.assertEqual(self.status_of(self.mutated(states_checkpoint)), SELF_IDENTITY)

    def test_unclassified_or_self_labelled_ledger_content_fails(self) -> None:
        digest = self.manifest["implementation_identity_digest"]

        def hex_in_summary(ledger: dict) -> None:
            ledger["modified_files"][0]["summary"] += f" ({digest})"

        def identity_in_prose_field(ledger: dict) -> None:
            ledger["modified_files"][0]["summary"] = digest

        def type_confused_status(ledger: dict) -> None:
            ledger["execution_status"]["production_solve"] = 0

        def solve_recorded(ledger: dict) -> None:
            ledger["execution_status"]["optimize_calls"] = 1

        def self_accepted(ledger: dict) -> None:
            ledger["lifecycle_status"]["independent_audit"] = "PASS"

        def inconsistent_result(ledger: dict) -> None:
            ledger["tests_executed"][0]["failures"] = 1

        def not_run_with_counts(ledger: dict) -> None:
            ledger["tests_executed"][0].update(
                {"ran": 0, "failures": 1, "errors": 0, "skipped": 0, "result": "NOT_RUN"}
            )

        for label, mutate, status in (
            ("hex_in_summary", hex_in_summary, UNACCOUNTED),
            ("identity_in_prose_field", identity_in_prose_field, UNACCOUNTED),
            ("type_confused_status", type_confused_status, "U06_ROLE_SCHEMA_INVALID"),
            ("solve_recorded", solve_recorded, "U06_ROLE_SCHEMA_INVALID"),
            ("self_accepted", self_accepted, "U06_ROLE_SCHEMA_INVALID"),
            ("inconsistent_result", inconsistent_result, "U06_ROLE_SCHEMA_INVALID"),
            ("not_run_with_counts", not_run_with_counts, "U06_ROLE_SCHEMA_INVALID"),
        ):
            with self.subTest(defect=label):
                self.assertEqual(self.status_of(self.mutated(mutate)), status)

    def test_duplicate_ledger_keys_are_rejected(self) -> None:
        decoy = '  "candidate_id": "MAIN_FULL81_PREFLIGHT_AUTHORIZATION_GUARD_CANDIDATE_R5",\n'
        injected = self.raw.decode("utf-8").replace("{\n", "{\n" + decoy, 1).encode("utf-8")
        with self.assertRaises(lc.U06LifecycleError) as caught:
            lc.validate_candidate_change_ledger(
                ROOT, injected, self.manifest, GEN, mode=CANDIDATE_PACKAGE
            )
        self.assertEqual(caught.exception.status, "U06_ROLE_SCHEMA_INVALID")

    def test_a_no_op_ledger_verifier_fails_parity(self) -> None:
        verifiers = lc.CANDIDATE_CHANGE_LEDGER_OBLIGATION_VERIFIERS
        self.assertEqual(
            set(verifiers),
            {o.kind for o in lc.CANDIDATE_CHANGE_LEDGER_IDENTITY_OBLIGATIONS},
        )
        original = verifiers["ledger_modified_files"]
        try:
            verifiers["ledger_modified_files"] = lambda context, items: (set(), set())
            self.assertEqual(self.status_of(self.ledger), UNACCOUNTED)
        finally:
            verifiers["ledger_modified_files"] = original
        self.assertEqual(self.status_of(self.ledger), "PASS")


class SemanticRoleOwnershipTests(unittest.TestCase):
    """R6-AUD-01: lawful digests, existing objects, PERMUTED roles -> never PASS.

    The attacker here is the strongest one the audit described: it may move
    any lawful digest into any other role, rewrite the manifest, the change
    ledger and every checkpoint claim consistently, and re-bind the ledger and
    checkpoint hashes so the package is internally coherent.  Every control
    drives the REAL production validator, in GATE mode against a disposable
    copy of the published checkout plus the external historical evidence
    contract V4 requires (Candidate R8; under V3 the copy deliberately had NO
    preservation package - which is now the fail-closed control in NC-10) and,
    where stated, in CANDIDATE_PACKAGE mode against the live tree.  Nothing is
    mocked.  The adversary that ALSO rewrites the candidate table and the
    implementation identity is attacked in ``test_21k``.
    """

    MISMATCH = "U06_ROLE_TARGET_MISMATCH"
    #: R7-AUD-01 / contract V4: a historical role's value is established by the
    #: external historical authority, so a permuted historical value is refused
    #: with this status.
    HISTORICAL = EXTERNAL_MISMATCH
    #: A permuted value is refused as "not this role's value": by the role
    #: binding, by the external historical authority, or - when the role is a
    #: live implementation path or digest - by the implementation-identity check
    #: that establishes that value.
    ROLE_REJECTIONS = frozenset(
        {MISMATCH, HISTORICAL, "U06_IMPLEMENTATION_IDENTITY_DRIFT"}
    )

    @classmethod
    def setUpClass(cls) -> None:
        cls.manifest = json.loads((ROOT / GEN.candidate_manifest_path).read_bytes())
        cls.ledger = json.loads((ROOT / GEN.candidate_change_ledger_path).read_bytes())
        cls.checkpoint = (ROOT / GEN.candidate_checkpoint_path).read_text(encoding="utf-8")
        identities, _ = lc.collect_identity_pointers(cls.manifest)
        cls.identities = {lc.rfc6901_pointer(p): v for p, v in identities}
        cls.rebound = {
            lc.rfc6901_pointer(("candidate_checkpoint", "sha256")),
            lc.rfc6901_pointer(("candidate_change_ledger", "sha256")),
        }
        cls.fixture = _DisposableExternalAuthorityRoot()
        cls.fixture.__enter__()

    @classmethod
    def tearDownClass(cls) -> None:
        cls.fixture.teardown()

    # -- the attacker ------------------------------------------------------------

    @staticmethod
    def pointer(*segments: str) -> str:
        return lc.rfc6901_pointer(segments)

    @staticmethod
    def preservation(candidate: str, field: str) -> str:
        return lc.rfc6901_pointer(("candidate_preservation_packages", candidate, field))

    @staticmethod
    def set_pointer(payload: dict, pointer: str, value: str) -> None:
        tokens = lc.parse_rfc6901_pointer(pointer)
        node = payload
        for token in tokens[:-1]:
            node = node[token]
        node[tokens[-1]] = value

    @staticmethod
    def with_claim_values(text: str, values: dict[str, str]) -> str:
        """Rebind existing claims of ``values``' pointers; append the others."""

        lines = text.split("\n")
        seen: set[str] = set()
        for index, line in enumerate(lines):
            pointer = line.split(" ")[0]
            if pointer in values and re.fullmatch(r"/\S* [0-9a-f]{64}", line):
                lines[index] = f"{pointer} {values[pointer]}"
                seen.add(pointer)
        out = "\n".join(lines)
        extra = [f"{p} {v}" for p, v in values.items() if p not in seen]
        if extra:
            out += "\n```identity-claims\n" + "\n".join(extra) + "\n```\n"
        return out

    @staticmethod
    def with_claims(text: str, *lines: str) -> str:
        return text + "\n```identity-claims\n" + "\n".join(lines) + "\n```\n"

    @staticmethod
    def swap_everywhere(text: str, a: str, b: str) -> str:
        marker = "\x00SWAP\x00"
        return text.replace(a, marker).replace(b, a).replace(marker, b)

    def consistent_swap(self, a: str, b: str) -> tuple[dict, dict, str]:
        """Exchange two lawful digests in EVERY artifact and EVERY claim."""

        return (
            json.loads(self.swap_everywhere(json.dumps(self.manifest), a, b)),
            json.loads(self.swap_everywhere(json.dumps(self.ledger), a, b)),
            self.swap_everywhere(self.checkpoint, a, b),
        )

    def run_package(
        self,
        manifest: dict | None = None,
        ledger: dict | None = None,
        checkpoint: str | None = None,
        *,
        mode: str = GATE,
    ) -> str:
        """Write the package into the clean fixture, RE-BOUND, and validate it."""

        fixture = self.fixture
        manifest = copy.deepcopy(self.manifest if manifest is None else manifest)
        ledger_bytes = _encode(self.ledger if ledger is None else ledger)
        fixture.contained_write(GEN.candidate_change_ledger_path, ledger_bytes)
        ledger_sha = hashlib.sha256(ledger_bytes).hexdigest()
        manifest["candidate_change_ledger"]["sha256"] = ledger_sha
        checkpoint = self.with_claim_values(
            self.checkpoint if checkpoint is None else checkpoint,
            {self.pointer("candidate_change_ledger", "sha256"): ledger_sha},
        )
        manifest["candidate_checkpoint"]["sha256"] = fixture.contained_write(
            GEN.candidate_checkpoint_path, checkpoint.encode("utf-8")
        )
        manifest_bytes = _encode(manifest)
        fixture.contained_write(GEN.candidate_manifest_path, manifest_bytes)
        try:
            lc.validate_candidate_manifest_identity_contract(
                fixture.dir,
                GEN.candidate_manifest_path,
                generation=GEN,
                mode=mode,
                manifest_bytes=manifest_bytes,
            )
        except lc.U06LifecycleError as exc:
            return exc.status
        return "PASS"

    def assert_permutation_fails(self, label: str, *package) -> None:
        with self.subTest(attack=label):
            status = self.run_package(*package)
            self.assertNotEqual(status, "PASS", f"{label} reached PASS")
            self.assertIn(status, self.ROLE_REJECTIONS, label)

    # -- positive controls -------------------------------------------------------

    def test_the_canonical_package_passes_in_both_modes(self) -> None:
        self.assertEqual(self.run_package(), "PASS")
        report = lc.validate_candidate_manifest_identity_contract(
            ROOT, GEN.candidate_manifest_path, mode=CANDIDATE_PACKAGE
        )
        self.assertEqual(report["structural_identity_count"], 0)
        self.assertEqual(report["role_bound_identity_count"], len(self.identities))

    def test_every_historical_role_is_externally_derived_and_true(self) -> None:
        """Every historical value comes from the external chain and is TRUE.

        The derivation covers exactly the declared role schema plus the
        externally derived change set; the candidate table merely asserts it;
        and every file-describing value is proved against the immutable bytes.
        """

        binding = lc._RoleBinding(ROOT, CANDIDATE_PACKAGE, "test")
        derived = binding.historical_roles()
        self.assertEqual(derived, lc.historical_role_identities(label="test"))
        prefix = lc.PREDECESSOR_MODIFIED_FILE_ROLE_PREFIX
        self.assertEqual(
            {r for r in derived if not r.startswith(prefix)},
            set(lc.required_historical_roles()),
        )
        for role, (path, digest) in derived.items():
            with self.subTest(role=role):
                self.assertEqual(binding.historical(role), digest)
                if role.startswith("preservation:") or role in (
                    lc.PREDECESSOR_ROLE_CHECKPOINT,
                    lc.PREDECESSOR_ROLE_MANIFEST,
                ):
                    self.assertEqual(sha(ROOT / path), digest)
        self.assertEqual(binding._proved, set(derived))

    # -- (1)/(2) the R6-AUD-01 reproductions -----------------------------------

    def test_r5_archive_index_swap_with_original_and_rebound_claims_fails(self) -> None:
        archive = self.preservation(R5_ID, "archive_sha256")
        index = self.preservation(R5_ID, "index_sha256")
        a, b = self.identities[archive], self.identities[index]
        swapped = copy.deepcopy(self.manifest)
        self.set_pointer(swapped, archive, b)
        self.set_pointer(swapped, index, a)
        original_claims = self.with_claims(self.checkpoint, f"{archive} {a}", f"{index} {b}")
        rebound_claims = self.with_claims(self.checkpoint, f"{archive} {b}", f"{index} {a}")
        self.assert_permutation_fails("r5_swap_no_claims", swapped)
        self.assert_permutation_fails("r5_swap_original_claims", swapped, None, original_claims)
        self.assert_permutation_fails("r5_swap_rebound_claims", swapped, None, rebound_claims)
        # ... and the claims alone, against the lawful manifest.
        self.assert_permutation_fails("r5_rebound_claims_only", None, None, rebound_claims)

    def test_immediate_predecessor_stop_swap_mirrored_in_the_ledger_fails(self) -> None:
        """The audit's exact shape, on the immediate predecessor (now R7)."""

        a = self.identities[self.preservation(R7_ID, "archive_sha256")]
        b = self.identities[self.preservation(R7_ID, "index_sha256")]
        manifest, ledger, checkpoint = self.consistent_swap(a, b)
        stop = ledger["predecessor"]["preserved_identity"]["stop_package"]
        self.assertEqual((stop["archive_sha256"], stop["index_sha256"]), (b, a))
        self.assertIn(f"{self.preservation(R7_ID, 'archive_sha256')} {b}", checkpoint)
        self.assert_permutation_fails("r7_swap_everywhere", manifest, ledger, checkpoint)
        for mode in (GATE, CANDIDATE_PACKAGE):
            with self.subTest(mode=mode):
                self.assertEqual(
                    self.run_package(manifest, ledger, checkpoint, mode=mode), self.HISTORICAL
                )

    # -- (3) other lawful semantic digests exchanged ----------------------------

    def test_other_lawful_digests_exchanged_between_roles_fail(self) -> None:
        pins = self.manifest["authority_bundle"]["pins"]
        defect = self.manifest["package_binding"]["predecessor_defect"]
        paths = self.manifest["implementation_identity"]["paths"]
        pairs = {
            "framework_vs_registry": (
                pins["framework_v7_4"]["sha256"], pins["registry_v7_4"]["sha256"]
            ),
            "predecessor_checkpoint_vs_manifest": (
                defect["predecessor_candidate_checkpoint"]["raw_sha256"],
                defect["predecessor_candidate_manifest"]["raw_sha256"],
            ),
            "two_implementation_paths": (
                paths["src/production_authority_lifecycle_u06.py"],
                paths["src/production_authority_bundle_v7_4.py"],
            ),
            "r1_vs_r2_stop_records": (
                self.identities[self.preservation(
                    "MAIN_FULL81_PREFLIGHT_AUTHORIZATION_GUARD_CANDIDATE_R1", "stop_record_sha256"
                )],
                self.identities[self.preservation(
                    "MAIN_FULL81_PREFLIGHT_AUTHORIZATION_GUARD_CANDIDATE_R2", "stop_record_sha256"
                )],
            ),
            "predecessor_digest_vs_r6_stop_record": (
                self.manifest["implementation_identity"]["predecessor_digest"],
                self.identities[self.preservation(R6_ID, "stop_record_sha256")],
            ),
            "eol_policy_vs_parameter_registry": (
                pins["repository_eol_policy"]["sha256"], pins["parameter_registry"]["sha256"]
            ),
        }
        for label, (a, b) in pairs.items():
            self.assertNotEqual(a, b, label)
            self.assert_permutation_fails(label, *self.consistent_swap(a, b))

    # -- (4)-(6) structural-only, wrong digest, wrong pointer --------------------

    def test_no_formerly_structural_identity_is_claimable_with_a_foreign_value(self) -> None:
        """The pointers contract V2 left STRUCTURAL in GATE mode, attacked."""

        self.assertEqual(self.run_package(), "PASS")
        report = lc.validate_candidate_manifest_identity_contract(
            self.fixture.dir, GEN.candidate_manifest_path, mode=GATE
        )
        self.assertEqual(report["structural_pointers"], [])
        formerly_structural = sorted(
            p for p in self.identities
            if p.startswith(("/candidate_preservation_packages/", "/package_binding/"))
            or p == "/implementation_identity/predecessor_digest"
        )
        self.assertEqual(len(formerly_structural), 3 * len(lc.CANDIDATE_PRESERVATION_PACKAGES) + 3)
        values = [self.identities[p] for p in formerly_structural]
        for position, pointer in enumerate(formerly_structural):
            foreign = values[(position + 1) % len(values)]
            with self.subTest(pointer=pointer):
                self.assertEqual(
                    self.run_package(None, None, self.with_claim_values(
                        self.checkpoint, {pointer: foreign}
                    )),
                    self.HISTORICAL,
                )

    def test_correct_pointer_with_wrong_lawful_digest_and_vice_versa_fail(self) -> None:
        archive = self.preservation(R6_ID, "archive_sha256")
        index = self.preservation(R6_ID, "index_sha256")
        r5_archive = self.preservation(R5_ID, "archive_sha256")
        for label, values, status in (
            ("correct_pointer_wrong_digest", {archive: self.identities[index]}, self.HISTORICAL),
            ("wrong_pointer_correct_digest", {r5_archive: self.identities[archive]}, self.HISTORICAL),
            ("checkpoint_role_given_ledger_digest", {
                "/implementation_identity_digest": self.manifest["candidate_change_ledger"]["sha256"]
            }, self.MISMATCH),
        ):
            with self.subTest(attack=label):
                self.assertEqual(
                    self.run_package(None, None, self.with_claim_values(self.checkpoint, values)),
                    status,
                )

    # -- (7)-(13) pointer grammar, duplicates, unknown roles ---------------------

    def test_container_noncanonical_malformed_and_unknown_pointers_fail(self) -> None:
        digest = self.identities[self.preservation(R6_ID, "archive_sha256")]
        overlay = self.manifest["implementation_identity"]["paths"][
            "src/production_authority_lifecycle_u06.py"
        ]
        for label, line in (
            ("container", f"/candidate_preservation_packages/{R6_ID} {digest}"),
            ("container_paths", f"/implementation_identity/paths {overlay}"),
            ("document_root", f"/ {digest}"),
            ("unescaped_slash", f"/implementation_identity/paths/src/production_authority_lifecycle_u06.py {overlay}"),
            ("tilde_zero_alias", f"/implementation_identity/paths/src~0production_authority_lifecycle_u06.py {overlay}"),
            ("trailing_slash", f"{self.preservation(R6_ID, 'archive_sha256')}/ {digest}"),
            ("double_slash", f"/candidate_preservation_packages//{R6_ID}/archive_sha256 {digest}"),
            ("percent_encoded", f"/implementation_identity/paths/src%2Fproduction_authority_lifecycle_u06.py {overlay}"),
            ("uri_fragment", f"#/candidate_preservation_packages/{R6_ID}/archive_sha256 {digest}"),
            ("bad_escape_2", f"/implementation_identity/paths/src~2production_authority_lifecycle_u06.py {overlay}"),
            ("trailing_tilde", f"/implementation_identity/paths/src~ {overlay}"),
            ("unknown_role", f"/candidate_manifest/sha256 {digest}"),
            ("unknown_section", f"/role_that_does_not_exist/sha256 {digest}"),
            ("non_identity_field", f"/scope {digest}"),
            ("manifest_self_path_field", f"/candidate_manifest_path {digest}"),
            ("case_variant", f"{self.preservation(R6_ID.lower(), 'archive_sha256')} {digest}"),
        ):
            with self.subTest(attack=label):
                status = self.run_package(None, None, self.with_claims(self.checkpoint, line))
                self.assertEqual(status, UNACCOUNTED, label)

    def test_duplicate_and_conflicting_same_role_claims_fail(self) -> None:
        # The immediate predecessor's package (R7 since Candidate R8) is the one
        # the checkpoint claims, so a further claim of it is a duplicate.
        archive = self.preservation(R7_ID, "archive_sha256")
        lawful = self.identities[archive]
        other = self.identities[self.preservation(R7_ID, "index_sha256")]
        digest = self.manifest["implementation_identity_digest"]
        for label, text, status in (
            ("duplicate_claim", self.with_claims(self.checkpoint, f"{archive} {lawful}"),
             "U06_ROLE_SCHEMA_INVALID"),
            ("conflicting_claim", self.with_claims(self.checkpoint, f"{archive} {other}"),
             "U06_ROLE_SCHEMA_INVALID"),
            ("conflicting_twin_role",
             self.with_claims(
                 self.checkpoint, f"/implementation_identity/implementation_digest {other}"
             ), self.MISMATCH),
            ("outside_claim_block", self.checkpoint + f"\nR6 archive: `{lawful}`\n",
             UNACCOUNTED),
            ("checkpoint_self_identity",
             self.with_claims(self.checkpoint, f"/candidate_checkpoint/sha256 {digest}"),
             SELF_IDENTITY),
        ):
            with self.subTest(attack=label):
                self.assertEqual(self.run_package(None, None, text), status)

    # -- (15)/(16) self identity and the ledger's digest in other roles ---------

    def test_manifest_self_identity_and_ledger_digest_in_other_roles_fail(self) -> None:
        ledger_sha = hashlib.sha256(_encode(self.ledger)).hexdigest()

        def own(p: dict) -> None:
            p["durable_publication_declaration"]["entries"][GEN.candidate_manifest_path][
                "expected_raw_sha256"
            ] = ledger_sha

        own_payload = copy.deepcopy(self.manifest)
        own(own_payload)
        self.assertEqual(self.run_package(own_payload), SELF_IDENTITY)
        # The R7 predecessor manifest and digest also live in the lawful ledger,
        # whose cross-consistency check refuses a manifest-only change first;
        # the R6 STOP record lives only in the manifest, so the external
        # historical authority refuses it.
        for pointer, status in (
            (
                "/package_binding/predecessor_defect/predecessor_candidate_manifest/raw_sha256",
                self.MISMATCH,
            ),
            (self.preservation(R6_ID, "stop_record_sha256"), self.HISTORICAL),
            ("/implementation_identity/predecessor_digest", self.MISMATCH),
            ("/authority_bundle/pins/framework_v7_4/sha256", self.MISMATCH),
        ):
            payload = copy.deepcopy(self.manifest)
            self.set_pointer(payload, pointer, ledger_sha)
            with self.subTest(pointer=pointer):
                self.assertEqual(
                    self.run_package(
                        payload, None, self.with_claim_values(self.checkpoint, {pointer: ledger_sha})
                        if pointer in self.checkpoint else None,
                    ),
                    status,
                )

    # -- (17) the invariant itself ----------------------------------------------

    def test_every_identity_role_permuted_with_another_lawful_value_fails(self) -> None:
        """EVERY identity pointer, in turn, takes another role's lawful digest.

        The exchange is applied consistently to the manifest, the ledger and
        every checkpoint claim, and the package is re-bound - so every digest
        is individually lawful and every referenced object exists.  The
        invariant is that semantic ownership, not lawfulness, decides.
        """

        distinct = sorted(
            {v for p, v in self.identities.items() if p not in self.rebound}
        )
        self.assertGreater(len(distinct), 40)
        attacked = 0
        for pointer, value in sorted(self.identities.items()):
            if pointer in self.rebound:
                continue
            partner = distinct[(distinct.index(value) + 1) % len(distinct)]
            self.assert_permutation_fails(
                f"{pointer}<->{partner[:12]}", *self.consistent_swap(value, partner)
            )
            attacked += 1
        self.assertEqual(attacked, len(self.identities) - len(self.rebound))

    def test_a_full_derangement_of_all_lawful_values_fails(self) -> None:
        distinct = sorted(
            {v for p, v in self.identities.items() if p not in self.rebound}
        )
        rotation = dict(zip(distinct, distinct[1:] + distinct[:1]))
        pattern = re.compile("|".join(map(re.escape, distinct)))

        def rotate(text: str) -> str:
            return pattern.sub(lambda m: rotation[m.group(0)], text)

        manifest = json.loads(rotate(json.dumps(self.manifest)))
        ledger = json.loads(rotate(json.dumps(self.ledger)))
        checkpoint = rotate(self.checkpoint)
        for mode in (GATE, CANDIDATE_PACKAGE):
            with self.subTest(mode=mode):
                self.assertEqual(
                    self.run_package(manifest, ledger, checkpoint, mode=mode), self.MISMATCH
                )
        historical = sorted(
            v for p, v in self.identities.items()
            if p.startswith(("/candidate_preservation_packages/", "/package_binding/"))
            or p == "/implementation_identity/predecessor_digest"
        )
        cycle = dict(zip(historical, historical[1:] + historical[:1]))
        only = re.compile("|".join(map(re.escape, historical)))
        manifest = json.loads(only.sub(lambda m: cycle[m.group(0)], json.dumps(self.manifest)))
        ledger = json.loads(only.sub(lambda m: cycle[m.group(0)], json.dumps(self.ledger)))
        checkpoint = only.sub(lambda m: cycle[m.group(0)], self.checkpoint)
        self.assertEqual(self.run_package(manifest, ledger, checkpoint), self.HISTORICAL)

    def test_ledger_only_role_permutations_fail_in_gate_mode(self) -> None:
        overlay = "src/production_authority_lifecycle_u06.py"

        def predecessor_candidate_swap(ledger: dict) -> None:
            entry = next(e for e in ledger["modified_files"] if e["path"] == overlay)
            entry["predecessor_raw_sha256"], entry["candidate_raw_sha256"] = (
                entry["candidate_raw_sha256"], entry["predecessor_raw_sha256"]
            )

        def two_suites_swapped(ledger: dict) -> None:
            first, second = ledger["tests_executed"][0], ledger["tests_executed"][1]
            first["raw_sha256"], second["raw_sha256"] = second["raw_sha256"], first["raw_sha256"]

        def predecessor_checkpoint_manifest_swap(ledger: dict) -> None:
            preserved = ledger["predecessor"]["preserved_identity"]
            preserved["checkpoint"]["raw_sha256"], preserved["manifest"]["raw_sha256"] = (
                preserved["manifest"]["raw_sha256"], preserved["checkpoint"]["raw_sha256"]
            )

        def two_modified_files_swapped(ledger: dict) -> None:
            a, b = ledger["modified_files"][0], ledger["modified_files"][1]
            a["predecessor_raw_sha256"], b["predecessor_raw_sha256"] = (
                b["predecessor_raw_sha256"], a["predecessor_raw_sha256"]
            )

        for label, mutate in (
            ("predecessor_candidate_swap", predecessor_candidate_swap),
            ("two_suites_swapped", two_suites_swapped),
            ("predecessor_checkpoint_manifest_swap", predecessor_checkpoint_manifest_swap),
            ("two_modified_files_swapped", two_modified_files_swapped),
        ):
            ledger = copy.deepcopy(self.ledger)
            mutate(ledger)
            self.assert_permutation_fails(label, None, ledger)

    # -- the pinned authority itself ---------------------------------------------

    def test_a_tampered_or_incomplete_historical_pin_table_fails_closed(self) -> None:
        """The candidate table is a DIAGNOSTIC assertion of the external truth.

        Candidate R8 / contract V4 (R7-AUD-01): the table is never a source of
        value, so every tampering that keeps it well-formed - swapped, missing,
        unknown, or re-pathed roles - is refused as a disagreement with the
        external derivation, in BOTH modes; a malformed (duplicated) table is
        still refused as such.  Under V3 several of these cases were refused
        only because the table's own closed-world schema caught them.
        """

        original = bundle.HISTORICAL_ROLE_IDENTITIES
        by_role = {e.role: e for e in original}
        archive = lc.preservation_role(R5_ID, "archive")
        index = lc.preservation_role(R5_ID, "index")
        swapped = tuple(
            bundle.HistoricalRoleIdentity(e.role, e.relative_path, by_role[index].sha256)
            if e.role == archive
            else bundle.HistoricalRoleIdentity(e.role, e.relative_path, by_role[archive].sha256)
            if e.role == index
            else e
            for e in original
        )
        cases = (
            # Pins swapped: the lawful manifest no longer matches them (GATE),
            # and CANDIDATE_PACKAGE refutes the pins from the preserved bytes.
            ("swapped_pins_gate", swapped, GATE, self.HISTORICAL),
            ("swapped_pins_candidate_package", swapped, CANDIDATE_PACKAGE, self.HISTORICAL),
            ("missing_role", tuple(e for e in original if e.role != archive), GATE, self.HISTORICAL),
            ("duplicate_role", original + (by_role[archive],), GATE, "U06_ROLE_SCHEMA_INVALID"),
            ("unknown_role", original + (
                bundle.HistoricalRoleIdentity("preservation:UNKNOWN:archive", "x", "0" * 64),
            ), GATE, self.HISTORICAL),
            ("role_for_another_path", tuple(
                bundle.HistoricalRoleIdentity(e.role, by_role[index].relative_path, e.sha256)
                if e.role == archive else e
                for e in original
            ), GATE, self.HISTORICAL),
        )
        try:
            for label, table, mode, status in cases:
                bundle.HISTORICAL_ROLE_IDENTITIES = table  # type: ignore[assignment]
                with self.subTest(attack=label):
                    if mode == CANDIDATE_PACKAGE:
                        # A manifest that AGREES with the tampered pins: only the
                        # proof against preserved bytes can refute it.
                        payload = copy.deepcopy(self.manifest)
                        a = self.preservation(R5_ID, "archive_sha256")
                        b = self.preservation(R5_ID, "index_sha256")
                        self.set_pointer(payload, a, self.identities[b])
                        self.set_pointer(payload, b, self.identities[a])
                        with self.assertRaises(lc.U06LifecycleError) as caught:
                            lc.validate_candidate_manifest_identity_contract(
                                ROOT, GEN.candidate_manifest_path, generation=GEN,
                                mode=mode, manifest_bytes=_encode(payload),
                            )
                        self.assertEqual(caught.exception.status, status)
                    else:
                        self.assertEqual(self.run_package(mode=mode), status)
        finally:
            bundle.HISTORICAL_ROLE_IDENTITIES = original  # type: ignore[assignment]
        self.assertEqual(self.run_package(), "PASS")


# ---------------------------------------------------------------------------
# R6-AUD-02: defence-in-depth mutation lint (NOT the safety boundary)
# ---------------------------------------------------------------------------
#
# The runtime primitive above is what keeps every mutation contained.  This
# lint only keeps mutation-capable APIs OUT of the rest of this module, so that
# every mutation is forced through the primitive.  It matches by attribute and
# function NAME wherever a mutation API could be reached - through any module
# alias, any ``from`` import, ``Path`` methods, builtin aliases, ``getattr``
# and dynamic import - and it refuses a second class claiming the primitive's
# name.  It cannot see dispatch through data structures or foreign code, and
# it does not claim to: correctness never depends on it.

_PRIMITIVE_CLASS = "_DisposableRoot"

#: Every attribute / function name that can mutate the filesystem (or run code
#: that can) in the standard library APIs this module could reach.
_MUTATING_NAMES = frozenset(
    {
        "open", "fdopen", "write", "writelines", "write_text", "write_bytes",
        "writestr", "touch", "mkdir", "makedirs", "mkdtemp", "mkstemp",
        "TemporaryDirectory", "NamedTemporaryFile", "TemporaryFile",
        "SpooledTemporaryFile", "unlink", "removedirs", "rmdir",
        "rmtree", "rename", "renames", "move", "copyfile", "copy2", "copytree",
        "copyfileobj", "copymode", "copystat", "symlink", "symlink_to",
        "hardlink_to", "link", "link_to", "CreateJunction", "truncate",
        "ftruncate", "chmod", "lchmod", "chown", "lchown", "utime", "extract",
        "extractall", "system", "popen", "startfile", "spawnv", "spawnl",
        "execv", "execl", "Popen", "check_call", "check_output",
    }
)
#: Names that are ALSO harmless methods (``str.replace``, ``dict.copy``,
#: ``list.remove``): they
#: are flagged when reached through a module alias, or when called with the
#: argument shape of the mutating API.
_AMBIGUOUS_MUTATING_NAMES = frozenset({"replace", "copy", "remove", "run", "call"})
_MODULES = frozenset(
    {
        "os", "shutil", "pathlib", "io", "tempfile", "zipfile", "_winapi",
        "builtins", "subprocess", "ctypes", "nt", "posix", "importlib",
    }
)
#: Modules whose mere import outside the primitive is a lint failure.
_FORBIDDEN_IMPORTS = frozenset(
    {"subprocess", "ctypes", "_winapi", "importlib", "builtins", "io", "nt", "posix"}
)
_FORBIDDEN_CALLS = frozenset({"setattr", "delattr", "__import__", "eval", "exec", "compile"})


def _primitive_spans(
    tree: ast.AST,
) -> tuple[list[tuple[int, int]], list[str], set[str]]:
    spans: list[tuple[int, int]] = []
    problems: list[str] = []
    private_methods: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == _PRIMITIVE_CLASS:
            spans.append((node.lineno, getattr(node, "end_lineno", node.lineno)))
            private_methods |= {
                item.name
                for item in node.body
                if isinstance(item, ast.FunctionDef)
                and item.name.startswith("_")
                and not item.name.startswith("__")
            }
    if len(spans) > 1:
        problems.append(f"{len(spans)} classes claim the primitive name {_PRIMITIVE_CLASS}")
    return spans, problems, private_methods


def _write_guard_violations(tree: ast.AST) -> list[str]:
    """Every mutation-capable API reference outside the containment primitive.

    Defence-in-depth for ``R6-AUD-02``; see the section comment.  Returns a
    list of human-readable violations (empty when clean).
    """

    spans, violations, private_methods = _primitive_spans(tree)

    def inside(node: ast.AST) -> bool:
        line = getattr(node, "lineno", -1)
        return any(start <= line <= end for start, end in spans)

    aliases: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                root_module = alias.name.split(".")[0]
                if root_module in _MODULES:
                    aliases.add(alias.asname or root_module)
                if root_module in _FORBIDDEN_IMPORTS and not inside(node):
                    violations.append(f"line {node.lineno}: imports {alias.name}")
        elif isinstance(node, ast.ImportFrom):
            module = (node.module or "").split(".")[0]
            for alias in node.names:
                if alias.name == "*" or alias.name in _MUTATING_NAMES | _AMBIGUOUS_MUTATING_NAMES:
                    violations.append(
                        f"line {node.lineno}: imports writer {alias.name} from {module}"
                    )
                if alias.name in _MODULES:
                    aliases.add(alias.asname or alias.name)
            if module in _FORBIDDEN_IMPORTS and not inside(node):
                violations.append(f"line {node.lineno}: imports from {module}")

    for node in ast.walk(tree):
        if inside(node):
            continue
        line = getattr(node, "lineno", "?")
        if isinstance(node, ast.Name) and node.id in (_MUTATING_NAMES | _FORBIDDEN_CALLS):
            violations.append(f"line {line}: references {node.id}")
        elif isinstance(node, ast.Attribute):
            receiver_is_module = isinstance(node.value, ast.Name) and node.value.id in aliases
            if node.attr in _MUTATING_NAMES:
                violations.append(f"line {line}: references .{node.attr}")
            elif node.attr in _AMBIGUOUS_MUTATING_NAMES and receiver_is_module:
                violations.append(f"line {line}: references module .{node.attr}")
            elif node.attr in {"__dict__", "__builtins__", "__setattr__"}:
                violations.append(f"line {line}: references .{node.attr}")
            elif node.attr in private_methods:
                # The primitive's internals are reachable only through its
                # public, self-validating mutators.
                violations.append(f"line {line}: calls primitive internal .{node.attr}")
        elif isinstance(node, ast.Subscript):
            key = node.slice
            if (
                isinstance(key, ast.Constant)
                and isinstance(key.value, str)
                and key.value in _MUTATING_NAMES | _AMBIGUOUS_MUTATING_NAMES
            ):
                violations.append(f"line {line}: looks up writer {key.value!r} by name")
        elif isinstance(node, ast.Call):
            func = node.func
            if isinstance(func, ast.Attribute) and func.attr in _AMBIGUOUS_MUTATING_NAMES:
                positional = len(node.args)
                if (func.attr == "replace" and positional == 1) or (
                    func.attr == "copy" and (positional or node.keywords)
                ):
                    violations.append(f"line {line}: .{func.attr}() with a writer's shape")
            if isinstance(func, ast.Name) and func.id == "getattr":
                name = node.args[1] if len(node.args) > 1 else None
                if not (isinstance(name, ast.Constant) and isinstance(name.value, str)):
                    violations.append(f"line {line}: getattr with a dynamic name")
                elif name.value in _MUTATING_NAMES | _AMBIGUOUS_MUTATING_NAMES:
                    violations.append(f"line {line}: getattr of writer {name.value}")
            callee = func.attr if isinstance(func, ast.Attribute) else getattr(func, "id", None)
            if callee == "ZipFile":
                mode = node.args[1] if len(node.args) > 1 else next(
                    (k.value for k in node.keywords if k.arg == "mode"), None
                )
                if mode is not None and not (
                    isinstance(mode, ast.Constant) and mode.value == "r"
                ):
                    violations.append(f"line {line}: ZipFile opened for writing")
    return violations


# ---------------------------------------------------------------------------
# R6-AUD-02: runtime containment - the authoritative boundary, attacked
# ---------------------------------------------------------------------------

#: The primitive's complete mutating surface.  A coverage test proves this is
#: every public method that can mutate, so a new mutating method cannot be
#: added without joining the adversarial matrix below.
_PRIMITIVE_MUTATORS = (
    "contained_write",
    "contained_copy_in",
    "contained_unlink",
    "contained_rename",
    "contained_replace",
    "contained_remove_tree",
    "contained_link",
    "teardown",
)


def _unsafe_operands(outside: _DisposableRoot) -> dict[str, str]:
    """One operand per unsafe class, each aimed at a real outside target."""

    target = outside.dir / "sentinel.txt"
    return {
        "absolute": str(target),
        "absolute_posix": target.as_posix(),
        "rooted": "\\" + target.as_posix().split(":", 1)[-1].lstrip("/"),
        "rooted_posix": "/" + target.as_posix().split(":", 1)[-1].lstrip("/"),
        "drive_qualified": f"{target.drive}{target.relative_to(target.anchor).as_posix()}",
        "unc": "\\\\localhost\\" + str(target).replace(":", "$", 1),
        "unc_posix": "//localhost/" + target.as_posix().replace(":", "$", 1),
        "parent_traversal": f"../{outside.dir.name}/sentinel.txt",
        "normalized_traversal": f"a/../../{outside.dir.name}/sentinel.txt",
        "backslash_traversal": f"a\\..\\..\\{outside.dir.name}\\sentinel.txt",
        "trailing_dot_traversal": f".. /{outside.dir.name}/sentinel.txt",
        "repository_root": str(ROOT / "r7_escape.txt"),
        "repository_relative": "../" * 12 + ROOT.relative_to(ROOT.anchor).as_posix()
        + "/r7_escape.txt",
        "alternate_stream": "sentinel.txt:stream",
        "reserved_device": "NUL",
        "nul_byte": "a\x00b.txt",
        "empty": "",
        "dot": ".",
    }


class DisposableWriteContainmentTests(unittest.TestCase):
    """R5-AUD-02 / R6-AUD-02: the runtime primitive refuses every escape.

    Each control aims a REAL mutation at a REAL outside target (a sentinel in
    a separate disposable root, never the repository) and proves both that the
    primitive refuses it and that the outside target is byte-identical after.
    """

    def snapshot(self, root: _DisposableRoot) -> dict[str, bytes | None]:
        out: dict[str, bytes | None] = {}
        for path in sorted(root.dir.rglob("*")):
            out[path.relative_to(root.dir).as_posix()] = (
                path.read_bytes() if path.is_file() else None
            )
        return out

    def assert_refused(self, call, outside: _DisposableRoot, label: str) -> None:
        before = self.snapshot(outside)
        repository_probe = ROOT / "r7_escape.txt"
        with self.subTest(attack=label):
            with self.assertRaises(_DisposableEscape):
                call()
            self.assertEqual(self.snapshot(outside), before, f"{label}: outside changed")
            self.assertFalse(repository_probe.exists(), f"{label}: repository touched")

    # -- positive controls -----------------------------------------------------

    def test_contained_mutations_and_teardown_work(self) -> None:
        with _DisposableDir() as fixture:
            digest = fixture.contained_write("a/b/c.txt", b"inside")
            self.assertEqual(digest, hashlib.sha256(b"inside").hexdigest())
            self.assertEqual((fixture.dir / "a/b/c.txt").read_bytes(), b"inside")
            fixture.contained_copy_in(ROOT / lc.EOL_POLICY_RELATIVE_PATH, "copy/policy")
            fixture.contained_rename("a/b/c.txt", "a/b/d.txt")
            fixture.contained_write("a/e.txt", b"e")
            fixture.contained_replace("a/e.txt", "a/b/d.txt")
            self.assertEqual((fixture.dir / "a/b/d.txt").read_bytes(), b"e")
            fixture.contained_unlink("a/b/d.txt")
            fixture.contained_remove_tree("copy")
            self.assertEqual(sorted(p.name for p in fixture.dir.iterdir()), ["a"])
            root = fixture.dir
        self.assertFalse(root.exists(), "teardown left the disposable root behind")

    def test_the_mutating_surface_is_exactly_the_attacked_matrix(self) -> None:
        public = {
            name
            for name, value in vars(_DisposableRoot).items()
            if callable(value) and not name.startswith("_")
        }
        self.assertEqual(public, set(_PRIMITIVE_MUTATORS))

    # -- every mutator x every unsafe operand class -----------------------------

    def test_every_mutator_refuses_every_unsafe_operand(self) -> None:
        with _DisposableDir() as outside, _DisposableDir() as fixture:
            outside.contained_write("sentinel.txt", b"untouched")
            fixture.contained_write("inside.txt", b"inside")
            fixture.contained_write("a/keep.txt", b"keep")
            for name, operand in _unsafe_operands(outside).items():
                for label, call in (
                    ("write", lambda o=operand: fixture.contained_write(o, b"escape")),
                    ("copy_in", lambda o=operand: fixture.contained_copy_in(ROOT / ".gitattributes", o)),
                    ("unlink", lambda o=operand: fixture.contained_unlink(o)),
                    ("rename_source", lambda o=operand: fixture.contained_rename(o, "stolen.txt")),
                    ("rename_destination", lambda o=operand: fixture.contained_rename("inside.txt", o)),
                    ("replace_source", lambda o=operand: fixture.contained_replace(o, "stolen.txt")),
                    ("replace_destination", lambda o=operand: fixture.contained_replace("inside.txt", o)),
                    ("remove_tree", lambda o=operand: fixture.contained_remove_tree(o)),
                    ("link", lambda o=operand: fixture.contained_link(o, outside, kind="junction")),
                ):
                    self.assert_refused(call, outside, f"{label}:{name}")
            self.assertEqual((fixture.dir / "inside.txt").read_bytes(), b"inside")
            self.assertFalse((fixture.dir / "stolen.txt").exists())

    def test_a_junction_component_is_refused_for_every_mutator(self) -> None:
        """The real Windows reparse path, exercised on every mutator."""

        with _DisposableDir() as outside, _DisposableDir() as fixture:
            outside.contained_write("sentinel.txt", b"untouched")
            outside.contained_write("sub/deep.txt", b"deep")
            fixture.contained_write("inside.txt", b"inside")
            fixture.contained_link("j", outside, kind="junction")
            self.assertTrue((fixture.dir / "j" / "sentinel.txt").is_file())
            for operand in ("j", "j/sentinel.txt", "j/new.txt", "j/sub", "j/sub/deep.txt"):
                for label, call in (
                    ("write", lambda o=operand: fixture.contained_write(o, b"escape")),
                    ("copy_in", lambda o=operand: fixture.contained_copy_in(ROOT / ".gitattributes", o)),
                    ("unlink", lambda o=operand: fixture.contained_unlink(o)),
                    ("rename_source", lambda o=operand: fixture.contained_rename(o, "stolen.txt")),
                    ("rename_destination", lambda o=operand: fixture.contained_rename("inside.txt", o)),
                    ("replace_source", lambda o=operand: fixture.contained_replace(o, "stolen.txt")),
                    ("replace_destination", lambda o=operand: fixture.contained_replace("inside.txt", o)),
                    ("remove_tree", lambda o=operand: fixture.contained_remove_tree(o)),
                    ("link", lambda o=operand: fixture.contained_link(o, outside, kind="junction")),
                ):
                    self.assert_refused(call, outside, f"{label}:{operand}")

    def test_symlink_escape_is_refused_before_any_write(self) -> None:
        """Where the account may create symbolic links; skipped otherwise.

        The skip is never silent coverage: the SAME decision function is driven
        deterministically by :meth:`test_link_decision_logic_is_deterministic`,
        and a real junction (a reparse point, exactly like a Windows symbolic
        link) exercises the real path in the test above.
        """

        with _DisposableDir() as outside, _DisposableDir() as fixture:
            outside.contained_write("sentinel.txt", b"untouched")
            fixture.contained_link("s", outside, kind="symlink")
            for operand in ("s", "s/sentinel.txt", "s/new.txt"):
                self.assert_refused(
                    lambda o=operand: fixture.contained_write(o, b"escape"), outside, f"symlink:{operand}"
                )
                self.assert_refused(
                    lambda o=operand: fixture.contained_unlink(o), outside, f"symlink-unlink:{operand}"
                )

    def test_link_decision_logic_is_deterministic(self) -> None:
        """Lower-level control of the ONE link decision, platform-independent."""

        from types import SimpleNamespace

        plain_dir = SimpleNamespace(st_mode=stat.S_IFDIR | 0o755, st_file_attributes=0x10)
        plain_file = SimpleNamespace(st_mode=stat.S_IFREG | 0o644, st_file_attributes=0x20)
        posix_symlink = SimpleNamespace(st_mode=stat.S_IFLNK | 0o777)
        windows_symlink = SimpleNamespace(
            st_mode=stat.S_IFLNK | 0o777, st_file_attributes=0x400, st_reparse_tag=0xA000000C
        )
        junction = SimpleNamespace(
            st_mode=stat.S_IFDIR | 0o755, st_file_attributes=0x410, st_reparse_tag=0xA0000003
        )
        other_reparse = SimpleNamespace(st_mode=stat.S_IFREG, st_file_attributes=0x420)
        tag_only = SimpleNamespace(st_mode=stat.S_IFDIR, st_reparse_tag=0x80000017)
        for label, st, expected in (
            ("plain_dir", plain_dir, False),
            ("plain_file", plain_file, False),
            ("posix_symlink", posix_symlink, True),
            ("windows_symlink", windows_symlink, True),
            ("junction", junction, True),
            ("other_reparse_point", other_reparse, True),
            ("reparse_tag_only", tag_only, True),
        ):
            with self.subTest(entry=label):
                self.assertIs(_is_link_or_reparse(st), expected)
        # ... and the live junction is classified by the same function.
        with _DisposableDir() as outside, _DisposableDir() as fixture:
            junction_path = fixture.contained_link("j", outside, kind="junction")
            self.assertTrue(_is_link_or_reparse(os.lstat(junction_path)))
            self.assertFalse(_is_link_or_reparse(os.lstat(fixture.dir)))

    # -- teardown and cleanup ------------------------------------------------

    def test_teardown_removes_an_unregistered_junction_never_its_target(self) -> None:
        """R6-AUD-02's live failure: teardown through an outside-root junction."""

        with _DisposableDir() as outside:
            outside.contained_write("sentinel.txt", b"untouched")
            outside.contained_write("sub/deep.txt", b"deep")
            before = self.snapshot(outside)
            fixture = _DisposableDir()
            fixture.contained_write("a/b/file.txt", b"x")
            fixture.contained_link("top", outside, kind="junction")
            fixture.contained_link("a/b/nested", outside, kind="junction")
            root = fixture.dir
            fixture.teardown()
            self.assertFalse(os.path.lexists(root))
            self.assertEqual(self.snapshot(outside), before)

    def test_teardown_and_cleanup_refuse_a_rebound_or_linked_root(self) -> None:
        """A cleanup aimed anywhere but the root this fixture created is refused."""

        with _DisposableDir() as outside, _DisposableDir() as holder:
            outside.contained_write("sentinel.txt", b"untouched")
            junction = holder.contained_link("root_link", outside, kind="junction")
            fixture = _DisposableDir()
            own = fixture._path
            try:
                for label, rebound in (
                    ("another_disposable_root", outside.dir),
                    ("junction_to_outside", junction),
                    ("system_tempdir", Path(tempfile.gettempdir()).resolve()),
                    ("repository_root", ROOT.resolve()),
                ):
                    fixture._path = rebound
                    self.assert_refused(fixture.teardown, outside, f"teardown:{label}")
                    self.assert_refused(
                        lambda: fixture.contained_remove_tree("sentinel.txt"), outside, f"cleanup:{label}"
                    )
                    self.assert_refused(
                        lambda: fixture.contained_write("x.txt", b"escape"), outside, f"write:{label}"
                    )
            finally:
                fixture._path = own
            fixture.teardown()
            self.assertFalse(own.exists())

    def test_remove_tree_and_unlink_never_reach_outside(self) -> None:
        with _DisposableDir() as outside, _DisposableDir() as fixture:
            outside.contained_write("sentinel.txt", b"untouched")
            fixture.contained_write("sub/file.txt", b"x")
            fixture.contained_link("sub/j", outside, kind="junction")
            before = self.snapshot(outside)
            # The subtree holds a junction: it is removed as a link only.
            fixture.contained_remove_tree("sub")
            self.assertFalse(os.path.lexists(fixture.dir / "sub"))
            self.assertEqual(self.snapshot(outside), before)
            for operand in (
                f"../{outside.dir.name}",
                str(outside.dir),
                str(outside.dir / "sentinel.txt"),
            ):
                self.assert_refused(
                    lambda o=operand: fixture.contained_remove_tree(o), outside, f"rmtree:{operand}"
                )
                self.assert_refused(
                    lambda o=operand: fixture.contained_unlink(o), outside, f"unlink:{operand}"
                )

    def test_a_hard_link_to_an_outside_file_is_never_written_through(self) -> None:
        with _DisposableDir() as outside:
            outside.contained_write("sentinel.txt", b"untouched")
            with _DisposableDir() as fixture:
                try:
                    fixture.contained_link(
                        "hard.txt", outside, kind="hardlink", outside_file="sentinel.txt"
                    )
                except OSError as exc:  # pragma: no cover - no hard links here
                    self.skipTest(f"hard links unavailable here: {exc}")
                self.assert_refused(
                    lambda: fixture.contained_write("hard.txt", b"escape"),
                    outside,
                    "write:hardlink",
                )
                self.assert_refused(
                    lambda: fixture.contained_copy_in(ROOT / ".gitattributes", "hard.txt"),
                    outside,
                    "copy_in:hardlink",
                )
            # Teardown removed the inside NAME only, never the outside bytes.
            self.assertEqual((outside.dir / "sentinel.txt").read_bytes(), b"untouched")

    # -- alias and helper indirection at runtime -------------------------------

    def test_aliased_and_helper_indirected_mutators_are_still_contained(self) -> None:
        with _DisposableDir() as outside, _DisposableDir() as fixture:
            outside.contained_write("sentinel.txt", b"untouched")
            fixture.contained_write("inside.txt", b"inside")
            escape = f"../{outside.dir.name}/sentinel.txt"
            writer = fixture.contained_write
            mover = getattr(fixture, "contained_rename")

            def helper(target: str) -> None:
                fixture.contained_write(target, b"via helper")

            def cleanup(target: str) -> None:
                fixture.contained_remove_tree(target)

            for label, call in (
                ("bound_method_alias", lambda: writer(escape, b"escape")),
                ("getattr_alias", lambda: mover("inside.txt", escape)),
                ("helper_indirection", lambda: helper(escape)),
                ("cleanup_helper", lambda: cleanup(f"../{outside.dir.name}")),
                ("subclass_method", lambda: _DisposableRepo.contained_write(fixture, escape, b"x")),
            ):
                self.assert_refused(call, outside, label)

    def test_containment_members_cannot_be_overridden_or_rebound(self) -> None:
        """A subclass cannot replace the decision; the root identity is write-once."""

        for member in ("_operand", "_require_root", "_remove_entry", "contained_write", "teardown"):
            with self.subTest(override=member):
                with self.assertRaises(_DisposableEscape):
                    type("Bypass", (_DisposableRoot,), {member: lambda self, *a, **k: None})
        with _DisposableDir() as outside, _DisposableDir() as fixture:
            outside.contained_write("sentinel.txt", b"untouched")
            st = os.lstat(outside.dir)
            with self.assertRaises(_DisposableEscape):
                fixture._identity = (st.st_dev, st.st_ino)
            own = fixture._path
            fixture._path = outside.dir
            try:
                self.assert_refused(fixture.teardown, outside, "teardown:rebound_path")
            finally:
                fixture._path = own

    def test_a_non_str_operand_is_refused(self) -> None:
        """Operands are exactly ``str``: no subclass can lie to the decision."""

        class Sneaky(str):
            def replace(self, *args: object) -> str:  # noqa: D401 - attack shape
                return "inside.txt"

            def split(self, *args: object) -> list[str]:
                return ["inside.txt"]

        with _DisposableDir() as outside, _DisposableDir() as fixture:
            outside.contained_write("sentinel.txt", b"untouched")
            for operand in (
                Sneaky(f"../{outside.dir.name}/sentinel.txt"),
                outside.dir / "sentinel.txt",
                Path("relative.txt"),
                b"relative.txt",
                None,
                7,
            ):
                self.assert_refused(
                    lambda o=operand: fixture.contained_write(o, b"escape"),
                    outside,
                    f"operand_type:{type(operand).__name__}",
                )

    def test_the_repository_and_tempdir_are_never_disposable_roots(self) -> None:
        for root in (ROOT, ROOT / "tests", Path(tempfile.gettempdir())):
            with self.subTest(root=root):
                fixture = _DisposableDir()
                own = fixture._path
                try:
                    fixture._path = Path(root).resolve()
                    with self.assertRaises(_DisposableEscape):
                        fixture.contained_write("r7_escape.txt", b"escape")
                    with self.assertRaises(_DisposableEscape):
                        fixture.teardown()
                finally:
                    fixture._path = own
                    fixture.teardown()
        self.assertFalse((ROOT / "r7_escape.txt").exists())
        self.assertFalse((ROOT / "tests" / "r7_escape.txt").exists())

    # -- the defence-in-depth lint -----------------------------------------------

    def test_every_mutation_in_this_module_is_inside_the_primitive(self) -> None:
        tree = ast.parse(Path(__file__).read_text(encoding="utf-8"))
        self.assertEqual(_write_guard_violations(tree), [])

    def test_the_lint_detects_every_known_unsafe_writer_pattern(self) -> None:
        """The R6 preserver's eleven patterns, and further alternate APIs."""

        patterns = {
            "module_alias": "import shutil as sh\ndef helper(p):\n    sh.rmtree(p)\n",
            "from_import": "from os import remove\ndef helper(p):\n    remove(p)\n",
            "io_open": "import io\ndef helper(p):\n    io.open(p, 'w').write('x')\n",
            "path_open": "from pathlib import Path\ndef helper(p):\n    Path(p).open('w').write('x')\n",
            "path_rename": "from pathlib import Path\ndef helper(p, q):\n    Path(p).rename(q)\n",
            "os_open": "import os\ndef helper(p):\n    os.open(p, os.O_CREAT | os.O_WRONLY)\n",
            "dynamic_getattr": (
                "from pathlib import Path\ndef helper(p):\n"
                "    getattr(Path(p), 'write_text')('x')\n"
            ),
            "dynamic_getattr_variable": "def helper(o, n):\n    getattr(o, n)('x')\n",
            "builtin_alias": "def helper(p):\n    w = open\n    w(p, 'w')\n",
            "zipfile_write": (
                "import zipfile\ndef helper(p):\n"
                "    zipfile.ZipFile(p, 'w').writestr('a', 'b')\n"
            ),
            "zipfile_mode_keyword": (
                "import zipfile\ndef helper(p):\n    zipfile.ZipFile(p, mode='a')\n"
            ),
            "os_truncate": "import os\ndef helper(p):\n    os.truncate(p, 0)\n",
            "allowlisted_name_uncontained_target": (
                "from pathlib import Path\nclass X:\n"
                "    def __enter__(self):\n"
                "        _require_disposable_root(self.dir)\n"
                "        Path('C:/outside.txt').write_text('x')\n"
            ),
            "os_replace": "import os\ndef helper(p, q):\n    os.replace(p, q)\n",
            "path_replace": "from pathlib import Path\ndef helper(p, q):\n    Path(p).replace(q)\n",
            "shutil_copy_alias": "import shutil as s\ndef helper(p, q):\n    s.copy(p, q)\n",
            "shutil_move": "import shutil\ndef helper(p, q):\n    shutil.move(p, q)\n",
            "tempfile_dir": "import tempfile\ndef helper():\n    tempfile.mkdtemp()\n",
            "dunder_import": "def helper(p):\n    __import__('os').remove(p)\n",
            "importlib": (
                "import importlib\ndef helper(p):\n"
                "    importlib.import_module('shutil').rmtree(p)\n"
            ),
            "subprocess": "import subprocess\ndef helper(p):\n    subprocess.run(['del', p])\n",
            "winapi_junction": "import _winapi\ndef helper(a, b):\n    _winapi.CreateJunction(a, b)\n",
            "touch_mkdir": "from pathlib import Path\ndef helper(p):\n    Path(p).touch()\n",
            "second_primitive_class": (
                "class _DisposableRoot:\n    pass\n"
                "class _DisposableRoot:\n    def w(self, p):\n        open(p, 'w')\n"
            ),
            "vars_lookup": "import os\ndef helper(p):\n    vars(os)['remove'](p)\n",
            "dict_lookup": "import shutil\ndef helper(p):\n    shutil.__dict__['rmtree'](p)\n",
            "primitive_internal_call": (
                "class _DisposableRoot:\n    def _remove_entry(self, p):\n        pass\n"
                "def helper(fixture, p):\n    fixture._remove_entry(p)\n"
            ),
            "subclass_writes_directly": (
                "class _DisposableRoot:\n    pass\n"
                "class Sub(_DisposableRoot):\n"
                "    def w(self, p):\n        (self.dir / p).write_bytes(b'x')\n"
            ),
        }
        for label, source in patterns.items():
            with self.subTest(pattern=label):
                self.assertTrue(_write_guard_violations(ast.parse(source)), label)
        clean = (
            "import copy, os\nfrom pathlib import Path\n"
            "def helper(p, fixture):\n"
            "    text = Path(p).read_text().replace('a', 'b')\n"
            "    data = copy.deepcopy({'a': 1}).copy()\n"
            "    os.lstat(p)\n"
            "    fixture.contained_write('x', b'y')\n"
            "    return getattr(p, 'lineno', None), text, data\n"
        )
        self.assertEqual(_write_guard_violations(ast.parse(clean)), [])


# ---------------------------------------------------------------------------
# Candidate / lifecycle state, and the no-solve boundary
# ---------------------------------------------------------------------------


class CandidateR8StateTests(unittest.TestCase):
    """The candidate state this suite is written against must be truthful."""

    def test_current_candidate_is_r8_and_unaudited(self) -> None:
        """CURRENT POINTER, advanced R7 -> R8; R4 through R7 asserted historically."""

        generation = lc.CURRENT_GENERATION
        self.assertEqual(
            generation.candidate_id,
            "MAIN_FULL81_PREFLIGHT_AUTHORIZATION_GUARD_CANDIDATE_R8",
        )
        self.assertEqual(generation.candidate_audit_state, "NOT_YET_PERFORMED")
        for predecessor in (
            "MAIN_FULL81_PREFLIGHT_AUTHORIZATION_GUARD_CANDIDATE_R4",
            R5_ID,
            R6_ID,
            R7_ID,
        ):
            with self.subTest(predecessor=predecessor):
                self.assertIn(predecessor, generation.superseded_candidate_ids)
                record = lc.PREFLIGHT_AUTH_GUARD_CANDIDATE_AUDIT_HISTORY[predecessor]
                self.assertEqual(record["independent_audit"], "FAIL_NO_GO")
                self.assertEqual(
                    record["disposition"], "REJECTED_HISTORICAL_CANDIDATE_IMMUTABLE"
                )

    def test_predecessor_stop_packages_are_bound_and_unchanged(self) -> None:
        """R8 binds the preserved R4, R5, R6 and R7 STOP identities exactly."""

        manifest = json.loads(
            (ROOT / lc.CURRENT_GENERATION.candidate_manifest_path).read_text(
                encoding="utf-8"
            )
        )
        stops = {}
        for candidate in (
            "MAIN_FULL81_PREFLIGHT_AUTHORIZATION_GUARD_CANDIDATE_R4", R5_ID, R6_ID, R7_ID
        ):
            package = manifest["candidate_preservation_packages"][candidate]
            for kind in ("archive", "index", "stop_record"):
                with self.subTest(candidate=candidate, file=kind):
                    self.assertEqual(
                        sha(ROOT / package[f"{kind}_path"]), package[f"{kind}_sha256"]
                    )
            stop = json.loads(
                (ROOT / package["stop_record_path"]).read_text(encoding="utf-8")
            )
            self.assertEqual(
                stop["preservation_package"]["archive_sha256"], package["archive_sha256"]
            )
            self.assertEqual(
                stop["preservation_package"]["byte_index_sha256"], package["index_sha256"]
            )
            self.assertEqual(stop["independent_audit"]["verdict_code"], "FAIL_NO_GO")
            stops[candidate] = stop
        r4_stop = stops["MAIN_FULL81_PREFLIGHT_AUTHORIZATION_GUARD_CANDIDATE_R4"]
        self.assertEqual(r4_stop["candidate_checkpoint"]["sha256"], sha(ROOT / R4_CHECKPOINT_REL))
        self.assertEqual(r4_stop["candidate_manifest"]["sha256"], sha(ROOT / R4_MANIFEST_REL))
        r5_stop = stops[R5_ID]
        self.assertEqual(r5_stop["candidate_checkpoint"]["sha256"], sha(ROOT / R5_CHECKPOINT_REL))
        self.assertEqual(r5_stop["candidate_manifest"]["sha256"], sha(ROOT / R5_MANIFEST_REL))
        r6_stop = stops[R6_ID]
        self.assertEqual(r6_stop["candidate_checkpoint"]["sha256"], sha(ROOT / R6_CHECKPOINT_REL))
        self.assertEqual(r6_stop["candidate_manifest"]["sha256"], sha(ROOT / R6_MANIFEST_REL))
        self.assertEqual(
            r6_stop["candidate_change_ledger"]["sha256"], sha(ROOT / R6_LEDGER_REL)
        )
        r7_stop = stops[R7_ID]
        defect = manifest["package_binding"]["predecessor_defect"]
        self.assertEqual(
            r7_stop["candidate_checkpoint"]["sha256"],
            defect["predecessor_candidate_checkpoint"]["raw_sha256"],
        )
        self.assertEqual(
            r7_stop["candidate_manifest"]["sha256"],
            defect["predecessor_candidate_manifest"]["raw_sha256"],
        )
        self.assertEqual(
            r7_stop["candidate_change_ledger"]["sha256"], sha(ROOT / R7_LEDGER_REL)
        )
        self.assertEqual(
            r7_stop["candidate_implementation_digest"],
            manifest["implementation_identity"]["predecessor_digest"],
        )
        self.assertEqual(
            sorted(r7_stop["blocking_findings"]), sorted(defect["findings"])
        )

    def test_n_r5d_04_is_carried_as_a_later_gate_blocker(self) -> None:
        """The acceptance-time EOL path problem is carried, not solved."""

        manifest = json.loads(
            (ROOT / lc.CURRENT_GENERATION.candidate_manifest_path).read_text(
                encoding="utf-8"
            )
        )
        carried = manifest["carried_findings"]["N-R5D-04"]
        self.assertEqual(carried["status"], "OPEN")
        self.assertEqual(carried["candidacy"], "NONBLOCKING")
        self.assertEqual(
            carried["blocking_before"], "ACCEPTANCE_LIFECYCLE_CONSTRUCTION"
        )
        self.assertFalse(carried["speculative_future_role_paths_created"])
        # No future acceptance role path is pre-declared or pre-covered.
        policy = (ROOT / lc.EOL_POLICY_RELATIVE_PATH).read_text(encoding="utf-8")
        for fragment in ("independent_audit_pass_record", "acceptance_closure", "re_freeze"):
            for line in policy.splitlines():
                if "main_full81_preflight_authorization_guard" in line:
                    with self.subTest(line=line, fragment=fragment):
                        self.assertNotIn(fragment, line)

    def test_same_generation_advance_was_lawful(self) -> None:
        lawfulness = lc.same_generation_advance_lawfulness(ROOT)
        self.assertTrue(lawfulness["same_generation_advance_lawful"])
        self.assertFalse(lawfulness["new_generation_created"])
        self.assertFalse(lawfulness["accepted_lifecycle_record_exists"])

    def test_nothing_is_accepted_or_frozen(self) -> None:
        live = lc.resolve_u06_lifecycle(ROOT)
        self.assertEqual(live["accepted_lifecycle_overlay"], "ABSENT")
        self.assertEqual(live["u06_acceptance_status"], "NOT_ACCEPTED")
        self.assertEqual(live["production_authority_freeze_status"], "NOT_FROZEN")
        self.assertFalse(lc.is_frozen(live))

    def test_main_full81_is_not_granted_and_a2_is_hard_blocked(self) -> None:
        state = bundle.main_full81_authorization_state(None)
        self.assertEqual(state["main_full81_authorization"], "NOT_GRANTED")
        with self.assertRaises(bundle.A2ExecutionHardBlocked):
            bundle.require_a2_hard_block("a2")
        with self.assertRaises(bundle.Full81AuthorizationNotGranted):
            bundle.require_full81_scope_authorization("full81", authorization=None)

    def test_fullstack_01_sentinel_is_carried(self) -> None:
        self.assertEqual(len(lc.FULLSTACK_01_PATHS), 4)
        self.assertIn("BLOCKING", lc.FULLSTACK_01_STATUS)
        self.assertIn("NONBLOCKING", lc.FULLSTACK_01_STATUS)
        manifest = json.loads(
            (ROOT / lc.CURRENT_GENERATION.candidate_manifest_path).read_text(
                encoding="utf-8"
            )
        )
        carried = manifest["carried_findings"]["FULLSTACK-01"]
        self.assertEqual(sorted(carried["paths"]), sorted(lc.FULLSTACK_01_PATHS))
        self.assertFalse(carried["published_or_modified_by_this_candidate"])
        self.assertFalse(carried["licensing_or_data_governance_decision_changed"])

    def test_this_suite_constructs_no_model_and_calls_no_solver(self) -> None:
        """Zero-solve control, tested on EXECUTABLE code rather than raw text.

        A raw substring scan would match this module's own prose — the
        docstring above says the suite calls no ``optimize()`` — and would
        either fail vacuously or have to be weakened to pass. The module is
        parsed instead, so the assertion is about what the code can actually
        reach.
        """

        tree = ast.parse(Path(__file__).read_text(encoding="utf-8"))

        imported: set[str] = set()
        called: set[str] = set()
        attributes: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported.update(alias.name.split(".")[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported.add(node.module.split(".")[0])
            elif isinstance(node, ast.Attribute):
                attributes.add(node.attr)
            elif isinstance(node, ast.Call):
                func = node.func
                if isinstance(func, ast.Name):
                    called.add(func.id)
                elif isinstance(func, ast.Attribute):
                    called.add(func.attr)

        for solver_module in ("gurobipy", "pyomo", "pulp"):
            self.assertNotIn(solver_module, imported)
        for solver_call in (
            "optimize",
            "Model",
            "run_layer_a_production",
            "build_annual_model",
            "run_annual_design_model",
        ):
            with self.subTest(symbol=solver_call):
                self.assertNotIn(solver_call, called)
                self.assertNotIn(solver_call, attributes)

        # Nothing in this suite writes to the source repository either: every
        # filesystem write is inside a guarded writer that containment-checks
        # its target (R5-AUD-02). Strictly stronger than the R5 name-only check.
        self.assertEqual(_write_guard_violations(tree), [])


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
