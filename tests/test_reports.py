import tempfile
import unittest
from pathlib import Path

from ios_linux_harness.prior_art import run_audit
from ios_linux_harness.reports import render_markdown_report, write_report_bundle


class ReportTests(unittest.TestCase):
    def test_report_leads_with_prior_art_boundary(self) -> None:
        audit = run_audit(prior_art_root=None)

        markdown = render_markdown_report(audit)

        self.assertIn("Not first to cross-compile iOS from Linux", markdown)
        self.assertIn("Candidate Deltas", markdown)
        self.assertIn("Swift Testing", markdown)

    def test_report_bundle_writes_markdown_and_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out_dir = Path(tmp) / "results"
            audit = run_audit(prior_art_root=None)

            paths = write_report_bundle(audit, out_dir)

            self.assertTrue(paths.markdown.exists())
            self.assertTrue(paths.json.exists())
            self.assertIn("publish_gate", paths.json.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
