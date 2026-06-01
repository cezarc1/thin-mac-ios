import tempfile
import unittest
from pathlib import Path

from ios_linux_harness.hygiene import scan_for_forbidden_paths


class HygieneTests(unittest.TestCase):
    def test_forbidden_apple_and_signing_artifacts_are_reported(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "fixture/iPhoneSimulator.sdk/System").mkdir(parents=True)
            (root / "fixture/result.xcresult").mkdir(parents=True)
            (root / "fixture/AuthKey_TEST.p8").write_text("secret", encoding="utf-8")
            (root / "fixture/profile.mobileprovision").write_text("profile", encoding="utf-8")
            (root / "README.md").write_text("safe", encoding="utf-8")

            findings = scan_for_forbidden_paths(root)
            found = {finding.kind for finding in findings}

            self.assertEqual(
                {"apple_sdk", "xcresult_bundle", "signing_key", "provisioning_profile"},
                found,
            )

    def test_allowed_source_files_are_clean(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "Sources").mkdir()
            (root / "Sources/App.swift").write_text("import SwiftUI\n", encoding="utf-8")

            self.assertEqual([], scan_for_forbidden_paths(root))


if __name__ == "__main__":
    unittest.main()
