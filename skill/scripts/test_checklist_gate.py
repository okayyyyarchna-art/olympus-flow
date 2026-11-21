import contextlib
import importlib.util
import io
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch


SCRIPT = Path(__file__).resolve().parents[1] / "tools/checklist_gate.py"
spec = importlib.util.spec_from_file_location("checklist_gate", SCRIPT)
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)

HEAD = "| Cell | Contract | Entry point | Change kind or mode | Copy or data state | Lifecycle edge | Expected result | Disposition |\n|---|---|---|---|---|---|---|---|\n"


class Gate(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(dir=Path(__file__).parent)
        self.addCleanup(self.tmp.cleanup)
        self.task = Path(self.tmp.name)
        (self.task / "pkg").mkdir()
        (self.task / "pkg/description.md").write_text("Scans skip local copies.\nOther tools stay  as they are.\n")
        (self.task / "pkg/test.patch").write_text("+func TestScanSkips(t *testing.T) {}\n")
        self.ledger("M01 | C01 | scan | added | local | none | skipped | TESTED TestScanSkips")
        gate.make_sheet(self.task)

    def ledger(self, *cells):
        body = "".join(f"| {cell} |\n" for cell in cells)
        (self.task / "ledger.md").write_text(
            "## Contract and meanings\n\n| ID | Quote | Effect | Outside | Separator | Status |\n|---|---|---|---|---|---|\n"
            "| C01 | a | b | c | d | PLANNED |\n\n## Blueprint\n\n" + HEAD + body + "\n## Tests\n")

    def fill(self, status="APPLIED", where="C01", note=""):
        path = gate.sheet_path(self.task)
        lines = []
        for line in path.read_text().splitlines():
            row = gate.cells(line) if line.startswith("|") else []
            if len(row) == 7 and row[0] not in ("Rule",) and not set(row[0]) <= set("-: "):
                row[4:7] = [status, where, note]
                line = "| " + " | ".join(row) + " |"
            lines.append(line)
        path.write_text("\n".join(lines) + "\n")

    def problems(self, through=5):
        return gate.check_sheet(self.task, through)[0] + gate.check_blueprint(self.task, through)

    def test_real_checklist_gives_a_row_for_every_rule(self):
        found = gate.rules(gate.CHECKLIST.read_text(encoding="utf-8"))
        self.assertGreater(len(found), 45)
        self.assertEqual({r["section"] for r in found}, set(range(1, 9)))
        self.assertTrue(any(r["text"].startswith("**Multiplicity**") for r in found))

    def test_blank_sheet_fails_and_filled_one_passes(self):
        self.assertTrue(any("not filled" in p for p in self.problems()))
        self.fill()
        self.assertEqual(self.problems(), [])

    def test_vague_location_and_unexplained_na_fail(self):
        self.fill(where="see above")
        self.assertTrue(any("Where must name" in p for p in self.problems()))
        self.fill(status="NA", where="", note="no")
        self.assertTrue(any("NA needs a reason" in p for p in self.problems()))

    def test_cited_ledger_row_must_exist(self):
        self.fill(where="C99")
        self.assertTrue(any("C99 is not a row" in p for p in self.problems()))

    def test_blueprint_closures(self):
        self.fill()
        for cell, expected in (
                ("M01 | C01 | scan | added | local | none | skipped | Fill", "must be TESTED"),
                ("M01 | C01 | Fill | added | local | none | skipped | TESTED TestScanSkips", "Entry point is blank"),
                ('M01 | C01 | scan | added | local | none | skipped | OUT "not in the text"', "quote is not in"),
                ("M01 | C01 | scan | added | local | none | skipped | OUT because rare", "OUT needs"),
                ("M01 | C01 | scan | added | local | none | skipped | SAME M01 same thing here", "another cell")):
            with self.subTest(expected):
                self.ledger(cell)
                self.assertTrue(any(expected in p for p in self.problems()), self.problems())

    def test_out_quote_ignores_line_breaks_and_same_needs_a_target(self):
        self.fill()
        self.ledger('M01 | C01 | scan | added | local | none | n/a | OUT "local copies. Other tools stay as they are."',
                    "M02 | C01 | report | added | local | none | n/a | SAME M01 the report reads the same rows")
        self.assertEqual(self.problems(), [])

    def test_contract_row_without_a_cell_fails(self):
        self.fill()
        self.ledger("M01 | C02 | scan | added | local | none | skipped | TESTED TestScanSkips")
        self.assertTrue(any("contract C01" in p for p in self.problems()))

    def test_planned_test_may_be_absent_until_the_build_gate(self):
        self.fill()
        self.ledger("M01 | C01 | scan | added | local | none | skipped | TESTED TestNotWrittenYet")
        self.assertEqual(self.problems(5), [])
        self.assertTrue(any("not in test.patch" in p for p in self.problems(7)))

    def test_rerun_keeps_filled_rows(self):
        self.fill()
        gate.make_sheet(self.task)
        self.assertEqual(self.problems(), [])

    def test_stray_pipe_is_reported_by_cell_count_and_the_sheet_command_heals_it(self):
        self.fill(note="run ./test.sh base|new first")
        problems = self.problems()
        self.assertTrue(any("row 1.1 has 8 cells, expected 7 (a | in a cell?" in p for p in problems), problems)
        self.assertFalse(any("no row in the sheet" in p for p in problems))
        with contextlib.redirect_stdout(io.StringIO()):
            gate.make_sheet(self.task)
        self.assertIn("base \\| new", gate.sheet_path(self.task).read_text(encoding="utf-8"))
        self.assertEqual(self.problems(), [])
        rows = gate.read_sheet(gate.sheet_path(self.task))
        self.assertEqual(rows[next(iter(rows))]["note"], "run ./test.sh base | new first")  # cells are stripped

    def test_sheet_command_names_the_rules_blanked_by_a_checklist_edit(self):
        self.fill()
        text = gate.CHECKLIST.read_text(encoding="utf-8")
        rule = next(r for r in gate.rules(text) if r["text"] in text)
        edited = self.task / "build-checklist.md"
        edited.write_text(text.replace(rule["text"], rule["text"] + " (edited)", 1), encoding="utf-8")
        out = io.StringIO()
        with patch.object(gate, "CHECKLIST", edited), contextlib.redirect_stdout(out):
            gate.make_sheet(self.task)
        self.assertIn(f"blank rows (rule text changed or rule new since the earlier sheet): {rule['id']}", out.getvalue())
        self.assertTrue(any(f"rule {rule['id']}: not filled" in p for p in self.problems()) or
                        any("checklist changed" in p for p in self.problems()))


if __name__ == "__main__":
    unittest.main()
