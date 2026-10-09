import argparse
import sys
from collections.abc import Callable, Sequence
from pathlib import Path

from legislative.calculations import create_bill_report, create_legislator_report
from legislative.exporters.csv import CsvReportExporter
from legislative.exporting import export_report
from legislative.loading import load_data
from legislative.models import LegislativeData
from legislative.reports import BillReport, LegislatorReport
from legislative.sources.csv import CsvDataSource


INPUT_DIR = Path(__file__).resolve().parent / "input"
OUTPUT_DIR = Path(__file__).resolve().parent / "output"


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate legislative support and opposition reports")
    parser.add_argument("--report", choices=("legislators", "bills", "all"), default="all")
    args = parser.parse_args(argv)
    protected = tuple(INPUT_DIR / name for name in
                      ("legislators.csv", "bills.csv", "votes.csv", "vote_results.csv"))
    selected: list[tuple[Callable[[LegislativeData], LegislatorReport | BillReport], CsvReportExporter]] = []
    if args.report in ("legislators", "all"):
        selected.append((create_legislator_report,
                         CsvReportExporter(OUTPUT_DIR / "legislators-support-oppose-count.csv", protected)))
    if args.report in ("bills", "all"):
        selected.append((create_bill_report, CsvReportExporter(OUTPUT_DIR / "bills.csv", protected)))
    try:
        if OUTPUT_DIR.resolve() == INPUT_DIR.resolve():
            raise ValueError("Use separate input and output directories")
        for _, exporter in selected:
            exporter.validate_path()
        data = load_data(CsvDataSource(INPUT_DIR))
        for create_report, exporter in selected:
            export_report(create_report(data), exporter)
            print(f"Wrote {exporter.path}")
    except (ValueError, OSError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1
    return 0
