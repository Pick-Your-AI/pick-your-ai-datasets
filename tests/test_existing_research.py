"""Structural guards for DATA-01.05's version-pinned upstream ownership map.

These are documentation reference checks, NOT independent external-source
verification or acceptance of the research boundary.
"""
from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "research" / "EXISTING_RESEARCH.md"


class ExistingResearchAuditTests(unittest.TestCase):
    def test_audit_has_pinned_upstream_source_links(self):
        text = AUDIT.read_text(encoding="utf-8")
        refs = re.findall(
            r"https://github[.]com/Pick-Your-AI/[A-Za-z0-9_.-]+/blob/([^/\s)]+)/",
            text,
        )
        self.assertGreaterEqual(len(refs), 9)
        for ref in refs:
            with self.subTest(ref=ref):
                self.assertRegex(ref, r"^[0-9a-f]{40}$")

    def test_audit_preserves_upstream_owner_and_acceptance_gates(self):
        text = AUDIT.read_text(encoding="utf-8")
        for owner in (
            "pick-your-ai-research",
            "pick-your-ai-papers",
            "pick-your-ai-applications",
        ):
            with self.subTest(owner=owner):
                self.assertIn("Pick-Your-AI/" + owner, text)
        for gate in ("DATA-01.05", "DATA-10.01", "proposed", "null"):
            with self.subTest(gate=gate):
                self.assertIn(gate, text)


if __name__ == "__main__":
    unittest.main()
