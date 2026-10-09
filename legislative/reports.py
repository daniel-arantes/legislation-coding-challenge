from dataclasses import dataclass

import pandas as pd

from legislative.models import BillId, LegislatorId


@dataclass(frozen=True, slots=True)
class LegislatorReportDTO:
    id: LegislatorId
    name: str
    num_supported_bills: int
    num_opposed_bills: int


@dataclass(frozen=True, slots=True)
class BillReportDTO:
    id: BillId
    title: str
    supporter_count: int
    opposer_count: int
    primary_sponsor: str


@dataclass(frozen=True, slots=True)
class LegislatorReportRecords:
    rows: tuple[LegislatorReportDTO, ...]


@dataclass(frozen=True, slots=True)
class BillReportRecords:
    rows: tuple[BillReportDTO, ...]


@dataclass
class LegislatorReport:
    data: pd.DataFrame


@dataclass
class BillReport:
    data: pd.DataFrame
