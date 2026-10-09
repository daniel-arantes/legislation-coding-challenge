import csv
import tempfile
import unittest
from pathlib import Path

from pandas.testing import assert_frame_equal

from legislative.calculations import create_bill_report, create_legislator_report
from legislative.exporters.base import ReportExporter
from legislative.exporters.csv import CsvReportExporter
from legislative.exporting import export_report
from legislative.reports import BillReport, LegislatorReport
from legislative.validation import DataValidationError
from test_calculations import sample_data


class InMemoryExporter:
    def __init__(self):
        self.reports: list[LegislatorReport | BillReport] = []

    def export(self, report: LegislatorReport | BillReport) -> None:
        self.reports.append(report)


class ExportTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name)

    def test_csv_exports_each_report_independently(self):
        for create_report in (create_legislator_report, create_bill_report):
            with self.subTest(report=create_report.__name__):
                report = create_report(sample_data())
                path = self.directory / create_report.__name__ / "report.csv"
                export_report(report, CsvReportExporter(path, ()))
                with path.open(encoding="utf-8", newline="") as source:
                    reader = csv.DictReader(source)
                    rows = list(reader)
                self.assertEqual(reader.fieldnames, list(report.data.columns))
                self.assertEqual(rows, [
                    {key: str(value) for key, value in row.items()}
                    for row in report.data.to_dict("records")
                ])

    def test_empty_report_exports_headers(self):
        report = create_bill_report(sample_data())
        report.data = report.data.iloc[:0].copy()
        path = self.directory / "empty.csv"
        export_report(report, CsvReportExporter(path, ()))
        with path.open(encoding="utf-8", newline="") as source:
            rows = list(csv.reader(source))
        self.assertEqual(rows, [list(report.data.columns)])

    def test_another_exporter_uses_the_same_boundary(self):
        exporter = InMemoryExporter()
        boundary: ReportExporter = exporter
        report = create_legislator_report(sample_data())
        original = report.data.copy(deep=True)
        export_report(report, boundary)
        self.assertEqual(len(exporter.reports), 1)
        self.assertIsInstance(exporter.reports[0], LegislatorReport)
        assert_frame_equal(exporter.reports[0].data, original)
        assert_frame_equal(report.data, original)

    def test_invalid_report_does_not_reach_exporter(self):
        for invalid in ("missing_column", "negative_count", "missing_value"):
            with self.subTest(invalid=invalid):
                exporter = InMemoryExporter()
                report = create_bill_report(sample_data())
                if invalid == "missing_column":
                    report.data = report.data.drop(columns="title")
                elif invalid == "negative_count":
                    report.data.loc[0, "supporter_count"] = -1
                else:
                    report.data.loc[0, "primary_sponsor"] = None
                with self.assertRaises(DataValidationError):
                    export_report(report, exporter)
                self.assertEqual(exporter.reports, [])

    def test_input_files_are_protected(self):
        path = self.directory / "bills.csv"
        path.write_text("original input", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "overwrite input"):
            export_report(create_bill_report(sample_data()), CsvReportExporter(path, (path,)))
        self.assertEqual(path.read_text(encoding="utf-8"), "original input")

    def test_existing_output_is_replaced(self):
        path = self.directory / "report.csv"
        path.write_text("old output", encoding="utf-8")
        report = create_legislator_report(sample_data())
        export_report(report, CsvReportExporter(path, ()))
        self.assertTrue(path.read_text(encoding="utf-8").startswith("id,name,"))
        self.assertEqual(list(self.directory.iterdir()), [path])


if __name__ == "__main__":
    unittest.main()
