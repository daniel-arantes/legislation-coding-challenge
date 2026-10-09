import tempfile
import unittest
from pathlib import Path

from legislative.loading import load_data
from legislative.sources.csv import CsvDataSource
from legislative.validation import DataValidationError


class LoadingTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name)
        self.inputs = {
            "legislators.csv": "id,name\n2,Bob\n1,Alice\n",
            "bills.csv": 'id,title,sponsor_id\n10,"Bill, one",1\n20,Bill two,999\n',
            "votes.csv": "id,bill_id\n100,20\n200,10\n",
            "vote_results.csv": "id,legislator_id,vote_id,vote_type\n1,1,100,1\n2,2,200,2\n",
        }
        for name, text in self.inputs.items():
            self.write(name, text)

    def write(self, name: str, text: str):
        (self.directory / name).write_text(text, encoding="utf-8", newline="")

    def test_valid_data(self):
        data = load_data(CsvDataSource(self.directory))
        self.assertEqual(data.legislators["id"].tolist(), [2, 1])
        self.assertEqual(data.bills["title"].tolist(), ["Bill, one", "Bill two"])
        self.assertEqual(data.bills["sponsor_id"].tolist(), [1, 999])
        for table in (data.legislators, data.bills, data.votes, data.vote_results):
            self.assertEqual(str(table["id"].dtype), "Int64")
        self.assertEqual(str(data.vote_results["vote_type"].dtype), "Int8")
        self.assertEqual(str(data.legislators["name"].dtype), "string")

    def test_bom_extra_columns_and_literal_na(self):
        self.write("legislators.csv", '\ufeffname,extra,id\nNA,x,2\n" Alice ",y,1\n')
        data = load_data(CsvDataSource(self.directory))
        self.assertEqual(list(data.legislators.columns), ["id", "name"])
        self.assertEqual(data.legislators["name"].tolist(), ["NA", " Alice "])

    def test_empty_tables(self):
        for name, text in self.inputs.items():
            self.write(name, text.splitlines()[0] + "\n")
        data = load_data(CsvDataSource(self.directory))
        self.assertTrue(all(table.empty for table in
                            (data.legislators, data.bills, data.votes, data.vote_results)))
        self.assertEqual(str(data.vote_results["vote_type"].dtype), "Int8")

    def test_multiline_text(self):
        self.write("bills.csv", 'id,title,sponsor_id\n10,"Bill\none",1\n20,Bill two,999\n')
        self.assertEqual(load_data(CsvDataSource(self.directory)).bills["title"].iloc[0], "Bill\none")

    def test_integer_precision_and_boundaries(self):
        for identifier in (2**53 + 1, 2**63 - 1, -(2**63)):
            with self.subTest(identifier=identifier):
                self.write("legislators.csv", f"id,name\n2,Bob\n1,Alice\n{identifier},Carol\n")
                self.assertEqual(load_data(CsvDataSource(self.directory)).legislators["id"].iloc[-1], identifier)

    def test_invalid_inputs(self):
        cases = [
            ("legislators.csv", "id\n1\n", "missing columns"),
            ("legislators.csv", "id,name,name\n1,Alice,Alice\n", "duplicate column"),
            ("legislators.csv", "id,name\n1,Alice,extra\n", "row width"),
            ("legislators.csv", "id,name\n1\n", "row width"),
            ("legislators.csv", 'id,name\n1,"Alice\n', "unexpected end"),
            ("legislators.csv", "id,name\n1,   \n", "required"),
            ("legislators.csv", "id,name\n1.5,Alice\n", "integer"),
            ("legislators.csv", "id,name\n1.0,Alice\n", "integer"),
            ("legislators.csv", "id,name\n1e2,Alice\n", "integer"),
            ("legislators.csv", "id,name\n1,Alice\n01,Bob\n", "duplicate id"),
            ("legislators.csv", f"id,name\n{2**63},Alice\n", "outside Int64"),
            ("legislators.csv", f"id,name\n{-2**63-1},Alice\n", "outside Int64"),
            ("bills.csv", "id,title,sponsor_id\n10,Bill,\n", "required"),
            ("votes.csv", "id,bill_id\n100,999\n", "unknown bill_id"),
            ("votes.csv", "id,bill_id\n100,10\n200,10\n", "more than one vote"),
            ("vote_results.csv", "id,legislator_id,vote_id,vote_type\n1,999,100,1\n", "unknown legislator_id"),
            ("vote_results.csv", "id,legislator_id,vote_id,vote_type\n1,1,999,1\n", "unknown vote_id"),
            ("vote_results.csv", "id,legislator_id,vote_id,vote_type\n1,1,100,3\n", "vote_type"),
            ("vote_results.csv", "id,legislator_id,vote_id,vote_type\n1,1,100,257\n", "outside Int8"),
            ("vote_results.csv", "id,legislator_id,vote_id,vote_type\n1,1,100,1\n2,1,100,2\n", "duplicate legislator/vote"),
            ("vote_results.csv", "id,legislator_id,vote_id,vote_type\n1,1,100,1\n1,2,200,2\n", "duplicate id"),
        ]
        for name, text, message in cases:
            with self.subTest(name=name, message=message):
                self.write(name, text)
                with self.assertRaisesRegex(DataValidationError, message):
                    load_data(CsvDataSource(self.directory))
                self.write(name, self.inputs[name])

    def test_missing_file(self):
        (self.directory / "votes.csv").unlink()
        with self.assertRaisesRegex(DataValidationError, "votes.csv"):
            load_data(CsvDataSource(self.directory))

    def test_supplied_data(self):
        data = load_data(CsvDataSource(Path(__file__).resolve().parents[1] / "legislative" / "input"))
        self.assertEqual(tuple(len(table) for table in
                               (data.legislators, data.bills, data.votes, data.vote_results)),
                         (20, 2, 2, 38))


if __name__ == "__main__":
    unittest.main()
