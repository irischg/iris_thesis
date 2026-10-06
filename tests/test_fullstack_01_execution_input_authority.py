"""No-solve controls for FULLSTACK-01 execution-input authority binding."""

from __future__ import annotations

import inspect
import os
import runpy
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from src import main_full81_authorization_v7_4 as auth


ROOT = Path(__file__).resolve().parents[1]


class Fullstack01ExecutionInputAuthorityTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory(
            prefix=".fullstack01_", dir=ROOT
        )
        self.fixture_root = Path(self.tempdir.name)
        for pin in auth.FULL81_EXECUTION_INPUT_AUTHORITY_PINS:
            target = self.fixture_root / pin.relative_path
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / pin.relative_path, target)

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def authenticate(self) -> dict:
        with patch.object(auth, "REPOSITORY_ROOT", self.fixture_root):
            return auth.authenticate_full81_execution_inputs()

    def assert_authority_fails(self, expected_status: str) -> None:
        with self.assertRaises(auth.Full81AuthorizationError) as caught:
            self.authenticate()
        self.assertEqual(caught.exception.status, expected_status)

    def test_positive_all_four_exact_canonical_inputs_pass(self) -> None:
        report = self.authenticate()
        self.assertEqual(report["status"], "FULL81_EXECUTION_INPUT_AUTHORITY_PASS")
        self.assertEqual(
            report["fullstack_01_remediation_status"],
            "REMEDIATION_CANDIDATE_READY_FOR_FRESH_INDEPENDENT_AUDIT",
        )
        self.assertEqual(report["input_count"], 4)
        self.assertFalse(report["path_override_allowed"])
        self.assertFalse(report["wildcard_or_discovery_fallback"])
        self.assertEqual(
            report["canonical_path_sha256"],
            {
                pin.relative_path: pin.sha256
                for pin in auth.FULL81_EXECUTION_INPUT_AUTHORITY_PINS
            },
        )
        for item in report["inputs"]:
            self.assertEqual(item["sha256"], item["reproduced_sha256"])
            self.assertGreater(item["byte_count"], 0)

    def test_authority_pins_equal_accepted_script_15d_identities(self) -> None:
        driver = runpy.run_path(
            str(ROOT / "scripts" / "15d_run_corrected_eob_v7_2.py")
        )
        script_15d = {
            pin.path: pin.sha256 for pin in driver["DEPENDENCY_PINS"]
        }
        self.assertEqual(
            {
                pin.relative_path: pin.sha256
                for pin in auth.FULL81_EXECUTION_INPUT_AUTHORITY_PINS
            },
            {
                pin.relative_path: script_15d[pin.relative_path]
                for pin in auth.FULL81_EXECUTION_INPUT_AUTHORITY_PINS
            },
        )

    def test_each_one_byte_mutation_fails(self) -> None:
        for pin in auth.FULL81_EXECUTION_INPUT_AUTHORITY_PINS:
            with self.subTest(path=pin.relative_path):
                path = self.fixture_root / pin.relative_path
                original = path.read_bytes()
                path.write_bytes(original[:-1] + bytes([original[-1] ^ 1]))
                self.assert_authority_fails(
                    "FULL81_EXECUTION_INPUT_AUTHORITY_HASH_MISMATCH"
                )
                path.write_bytes(original)

    def test_one_required_file_absent_fails_closed(self) -> None:
        pin = auth.FULL81_EXECUTION_INPUT_AUTHORITY_PINS[2]
        (self.fixture_root / pin.relative_path).unlink()
        self.assert_authority_fails("FULL81_EXECUTION_INPUT_AUTHORITY_MISSING")

    def test_same_schema_wrong_file_at_canonical_path_fails(self) -> None:
        pin = auth.FULL81_EXECUTION_INPUT_AUTHORITY_PINS[0]
        path = self.fixture_root / pin.relative_path
        # JSON permits trailing whitespace, so this remains schema-readable but
        # is not the accepted raw-byte identity.
        path.write_bytes(path.read_bytes() + b" ")
        self.assert_authority_fails(
            "FULL81_EXECUTION_INPUT_AUTHORITY_HASH_MISMATCH"
        )

    def test_exact_file_at_alternate_path_cannot_replace_missing_canonical(self) -> None:
        pin = auth.FULL81_EXECUTION_INPUT_AUTHORITY_PINS[1]
        canonical = self.fixture_root / pin.relative_path
        alternate = self.fixture_root / "alternate" / canonical.name
        alternate.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(canonical, alternate)
        canonical.unlink()
        self.assert_authority_fails("FULL81_EXECUTION_INPUT_AUTHORITY_MISSING")

    def test_ancestor_junction_resolving_outside_repository_fails_closed(self) -> None:
        reference = self.fixture_root / "data" / "reference"
        with tempfile.TemporaryDirectory(
            prefix=".fullstack01_external_", dir=ROOT
        ) as external_name:
            external_reference = Path(external_name) / "reference"
            shutil.copytree(reference, external_reference)
            shutil.rmtree(reference)
            if os.name == "nt":
                subprocess.run(
                    [
                        "cmd",
                        "/c",
                        "mklink",
                        "/J",
                        str(reference),
                        str(external_reference),
                    ],
                    check=True,
                    capture_output=True,
                    text=True,
                )
            else:
                reference.symlink_to(external_reference, target_is_directory=True)
            try:
                self.assert_authority_fails(
                    "FULL81_EXECUTION_INPUT_AUTHORITY_REPARSE_ESCAPE"
                )
            finally:
                reference.rmdir()

    def test_caller_path_override_is_not_an_api(self) -> None:
        parameters = inspect.signature(
            auth.authenticate_full81_execution_inputs
        ).parameters
        self.assertEqual(parameters, {})
        with self.assertRaises(TypeError):
            auth.authenticate_full81_execution_inputs(
                economic_interface_path=self.fixture_root / "alternate.json"
            )

    def test_execution_interlock_consumes_authority_before_retained_refusal(self) -> None:
        with patch.object(auth, "REPOSITORY_ROOT", self.fixture_root):
            with self.assertRaises(auth.Full81AuthorizationError) as caught:
                auth.require_full81_execution_authorization(None)
        self.assertEqual(caught.exception.status, "FULL81_EXECUTION_NOT_AUTHORIZED")
        self.assertIn("FULL81_EXECUTION_INPUT_AUTHORITY_PASS", str(caught.exception))

        pin = auth.FULL81_EXECUTION_INPUT_AUTHORITY_PINS[3]
        (self.fixture_root / pin.relative_path).unlink()
        with patch.object(auth, "REPOSITORY_ROOT", self.fixture_root):
            with self.assertRaises(auth.Full81AuthorizationError) as caught:
                auth.require_full81_execution_authorization(None)
        self.assertEqual(
            caught.exception.status, "FULL81_EXECUTION_INPUT_AUTHORITY_MISSING"
        )


if __name__ == "__main__":
    unittest.main()
