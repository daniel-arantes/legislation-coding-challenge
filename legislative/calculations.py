from legislative.models import LegislativeData
from legislative.reports import BillReport, LegislatorReport


def create_legislator_report(data: LegislativeData) -> LegislatorReport:
    raise NotImplementedError


def create_bill_report(data: LegislativeData) -> BillReport:
    raise NotImplementedError
