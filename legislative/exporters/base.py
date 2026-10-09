from typing import Protocol

from legislative.reports import BillReport, LegislatorReport


class ReportExporter(Protocol):
    def export(self, report: LegislatorReport | BillReport) -> None: ...
