"""Adversarial result-integrity checks; no repository, Docker or network mutations."""

import unittest
from pathlib import Path

from certify import Invalid, fingerprint, inspect_junit, patch_paths


class JUnitIntegrity(unittest.TestCase):
    def check(self, xml, expected=None, expect="pass", code=0, skips=()):
        return inspect_junit(xml, ["suite::one"] if expected is None else expected,
                             expect, code, skips)

    def test_namespaced_nested_report(self):
        xml = '<testsuites xmlns="urn:junit" tests="1"><testsuite tests="1"><testcase classname="suite" name="one"/></testsuite></testsuites>'
        self.assertEqual(self.check(xml)["results"], {"suite::one": "pass"})

    def test_real_failure_and_build_error_remain_distinct(self):
        for kind in ("failure", "error"):
            xml = f'<testsuite><testcase classname="suite" name="one"><{kind}>actual diagnostic</{kind}></testcase></testsuite>'
            result = self.check(xml, expect="fail", code=1)
            self.assertEqual(result["results"]["suite::one"], kind)

    def test_missing_extra_duplicate_and_empty_ids_rejected(self):
        case = '<testcase classname="suite" name="one"/>'
        bad = [('<testsuite/>', ["suite::one"]),
               ('<testsuite>'+case+'</testsuite>', ["suite::one", "suite::two"]),
               ('<testsuite>'+case*2+'</testsuite>', ["suite::one"]),
               ('<testsuite>'+case+'</testsuite>', ["suite::other"]),
               ('<testsuite>'+case+'</testsuite>', []),
               ('<testsuite>'+case+'</testsuite>', ["suite::one", "suite::one"])]
        for xml, expected in bad:
            with self.subTest(xml=xml, expected=expected), self.assertRaises(Invalid):
                self.check(xml, expected)

    def test_unapproved_skip_and_partial_base_failure_rejected(self):
        for child in ('<skipped/>', ''):
            xml = '<testsuite><testcase classname="suite" name="one">'+child+'</testcase></testsuite>'
            with self.subTest(child=child), self.assertRaises(Invalid):
                self.check(xml, expect="fail", code=1)
        xml = '<testsuite><testcase classname="suite" name="one"><skipped/></testcase></testsuite>'
        with self.assertRaises(Invalid):
            self.check(xml)
        self.assertEqual(self.check(xml, skips=["suite::one"])["results"]["suite::one"], "skipped")

    def test_exit_and_report_cannot_disagree(self):
        passing = '<testsuite><testcase classname="suite" name="one"/></testsuite>'
        failing = '<testsuite><testcase classname="suite" name="one"><failure message="bad value"/></testcase></testsuite>'
        with self.assertRaises(Invalid):
            self.check(passing, code=2)
        with self.assertRaises(Invalid):
            self.check(failing, expect="fail", code=0)
        with self.assertRaises(Invalid):
            self.check(failing)

    def test_fabricated_aggregates_rejected(self):
        for attr in ('tests="0"', 'failures="1"', 'errors="1"', 'skipped="1"', 'tests="unknown"'):
            xml = f'<testsuite {attr}><testcase classname="suite" name="one"/></testsuite>'
            with self.subTest(attr=attr), self.assertRaises(Invalid):
                self.check(xml)

    def test_malformed_nameless_and_empty_diagnostics_rejected(self):
        cases = ['<testsuite>', '<report/>', '<testsuite><testcase/></testsuite>',
                 '<testsuite><testcase classname="suite" name="one"><failure/></testcase></testsuite>',
                 '<testsuite><testcase classname="suite" name="one"><failure>x</failure><skipped/></testcase></testsuite>']
        for xml in cases:
            with self.subTest(xml=xml), self.assertRaises(Invalid):
                self.check(xml, expect="fail", code=1)


class PatchSyntax(unittest.TestCase):
    def test_independent_sample_changes_fingerprint(self):
        source = Path(__file__)
        first = fingerprint([source], {"sample": "A"})
        self.assertEqual(first, fingerprint([source], {"sample": "A"}))
        self.assertNotEqual(first["key"], fingerprint([source], {"sample": "B"})["key"])

    def test_valid_patch_paths(self):
        patch = b'diff --git a/test.sh b/test.sh\nnew file mode 100755\n--- /dev/null\n+++ b/test.sh\n@@ -0,0 +1 @@\n+#!/bin/sh\n'
        self.assertEqual(patch_paths(patch), ["test.sh"])

    def test_corrupt_hunk_rejected(self):
        patch = b'diff --git a/x b/x\n--- a/x\n+++ b/x\n@@ -1 +1,9 @@\n-a\n+b\n'
        with self.assertRaises(Invalid):
            patch_paths(patch)


if __name__ == "__main__":
    unittest.main()
