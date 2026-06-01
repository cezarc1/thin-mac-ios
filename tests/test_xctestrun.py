import plistlib
import tempfile
import unittest
from pathlib import Path

from ios_linux_harness.xctestrun import build_xctestrun_payload, write_xctestrun


class XCTestRunTests(unittest.TestCase):
    def test_ui_test_payload_contains_runner_and_app_paths(self) -> None:
        payload = build_xctestrun_payload(
            product_module_name="AccessibilityProbeUITests",
            test_bundle_path="__TESTROOT__/AccessibilityProbeUITests.xctest",
            test_host_path="__TESTROOT__/XCTRunner.app",
            ui_target_app_path="__TESTROOT__/ExampleApp.app",
            is_ui_test=True,
        )

        target = payload["TestConfigurations"][0]["TestTargets"][0]

        self.assertEqual("AccessibilityProbeUITests", target["ProductModuleName"])
        self.assertTrue(target["IsUITestBundle"])
        self.assertEqual("__TESTROOT__/ExampleApp.app", target["UITargetAppPath"])
        self.assertEqual("thin-mac-ios", payload["__xctestrun_metadata__"]["GeneratedBy"])

    def test_write_xctestrun_creates_plist(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "Probe.xctestrun"

            write_xctestrun(
                out,
                product_module_name="SmokeTests",
                test_bundle_path="__TESTROOT__/SmokeTests.xctest",
                test_host_path="__TESTROOT__/ExampleApp.app",
                ui_target_app_path=None,
                is_ui_test=False,
            )

            payload = plistlib.loads(out.read_bytes())
            target = payload["TestConfigurations"][0]["TestTargets"][0]
            self.assertTrue(target["IsAppHostedTestBundle"])
            self.assertNotIn("UITargetAppPath", target)


if __name__ == "__main__":
    unittest.main()
