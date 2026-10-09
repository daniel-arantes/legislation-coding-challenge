from legislative.exporters.base import ReportExporter
from legislative.reports import BillReport, LegislatorReport
from legislative.schemas import BILL_REPORT, LEGISLATOR_REPORT
from legislative.validation import DataValidationError, validate_table


def export_report(report: LegislatorReport | BillReport, exporter: ReportExporter) -> None:
    validated: LegislatorReport | BillReport
    if isinstance(report, LegislatorReport):
        frame = validate_table(report.data, LEGISLATOR_REPORT, "legislator report")
        columns = ["num_supported_bills", "num_opposed_bills"]
        validated = LegislatorReport(frame)
    elif isinstance(report, BillReport):
        frame = validate_table(report.data, BILL_REPORT, "bill report")
        columns = ["supporter_count", "opposer_count"]
        validated = BillReport(frame)
    else:
        raise TypeError("Unsupported report type")
    if frame[columns].lt(0).any().any():
        raise DataValidationError("Report counts must not be negative")
    exporter.export(validated)
