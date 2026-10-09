import csv
import io
import shutil
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest.mock import patch

from legislative.cli import main


ROOT = Path(__file__).resolve().parents[1]


class CliTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name)
        self.input = self.directory / "legislative" / "input"
        self.output = self.directory / "legislative" / "output"
        shutil.copytree(ROOT / "legislative", self.directory / "legislative",
                        ignore=shutil.ignore_patterns("__pycache__", "output"))

    def run_main(self, arguments):
        stdout, stderr = io.StringIO(), io.StringIO()
        with patch("legislative.cli.INPUT_DIR", self.input), patch("legislative.cli.OUTPUT_DIR", self.output), \
                redirect_stdout(stdout), redirect_stderr(stderr):
            status = main(arguments)
        return status, stdout.getvalue(), stderr.getvalue()

    def test_each_report_is_selected_independently(self):
        cases = (
            ("legislators", "create_bill_report", "legislators-support-oppose-count.csv"),
            ("bills", "create_legislator_report", "bills.csv"),
        )
        for selection, other_calculation, filename in cases:
            with self.subTest(selection=selection):
                destination = self.directory / selection
                arguments = ["--report", selection]
                self.output = destination
                with patch(f"legislative.cli.{other_calculation}") as unselected:
                    status, _, stderr = self.run_main(arguments)
                    unselected.assert_not_called()
                self.assertEqual(status, 0, stderr)
                self.assertEqual([path.name for path in destination.iterdir()], [filename])

    def test_module_entry_point_exports_both_reports(self):
        result = subprocess.run([sys.executable, "-m", "legislative"],
                                cwd=self.directory, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual({path.name for path in self.output.iterdir()},
                         {"bills.csv", "legislators-support-oppose-count.csv"})
        with (self.output / "bills.csv").open(encoding="utf-8", newline="") as source:
            bills = list(csv.DictReader(source))
        self.assertEqual([(row["supporter_count"], row["opposer_count"]) for row in bills],
                         [("6", "13"), ("13", "6")])
        with (self.output / "legislators-support-oppose-count.csv").open(encoding="utf-8", newline="") as source:
            people = list(csv.DictReader(source))
        self.assertEqual(len(people), 20)
        for person in people:
            expected = "0" if person["id"] == "412211" else "1"
            self.assertEqual((person["num_supported_bills"], person["num_opposed_bills"]),
                             (expected, expected))

    def test_invalid_input_does_not_create_reports(self):
        (self.input / "votes.csv").write_text("id,bill_id\n1,999\n", encoding="utf-8")
        status, stdout, stderr = self.run_main([])
        self.assertEqual(status, 1)
        self.assertEqual(stdout, "")
        self.assertIn("unknown bill_id", stderr)
        self.assertFalse(self.output.exists())

    def test_input_directory_cannot_be_output_directory(self):
        originals = {path.name: path.read_bytes() for path in self.input.iterdir()}
        self.output = self.input
        status, _, stderr = self.run_main([])
        self.assertEqual(status, 1)
        self.assertIn("separate input and output", stderr)
        self.assertEqual({path.name: path.read_bytes() for path in self.input.iterdir()}, originals)

    def test_invalid_selection_is_rejected(self):
        with redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as error:
            main(["--report", "unknown"])
        self.assertEqual(error.exception.code, 2)
        self.assertFalse(self.output.exists())

    def test_path_options_are_not_supported(self):
        for option in ("--input-dir", "--output-dir"):
            with self.subTest(option=option):
                with redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as error:
                    main([option, str(self.directory)])
                self.assertEqual(error.exception.code, 2)


if __name__ == "__main__":
    unittest.main()
