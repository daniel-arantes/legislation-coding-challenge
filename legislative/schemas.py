"""Ordered columns and explicit pandas dtypes for inputs and reports.

Schema declarations describe tables; validation is implemented in a later
milestone. Nullable dtypes allow joins and parsing to represent missing values
until those values are rejected or filled according to the data contract.
"""

from dataclasses import dataclass, fields
from typing import Generic, Literal, TypeVar

from legislative.models import (
    BillDTO,
    LegislatorDTO,
    VoteDTO,
    VoteResultDTO,
)
from legislative.reports import BillReportDTO, LegislatorReportDTO


RecordT = TypeVar("RecordT", LegislatorDTO, BillDTO, VoteDTO, VoteResultDTO,
                  LegislatorReportDTO, BillReportDTO)
PandasDtype = Literal["Int64", "Int8", "string"]


@dataclass(frozen=True)
class TableSchema(Generic[RecordT]):
    record_type: type[RecordT]
    fields: tuple[tuple[str, PandasDtype], ...]

    def __post_init__(self) -> None:
        expected = tuple(field.name for field in fields(self.record_type))
        if self.columns != expected:
            raise ValueError(f"Schema columns must match {self.record_type.__name__}: {expected}")

    @property
    def columns(self) -> tuple[str, ...]:
        return tuple(name for name, _ in self.fields)

    @property
    def dtypes(self) -> dict[str, PandasDtype]:
        return dict(self.fields)


LEGISLATORS = TableSchema(LegislatorDTO, (
    ("id", "Int64"),
    ("name", "string"),
))

BILLS = TableSchema(BillDTO, (
    ("id", "Int64"),
    ("title", "string"),
    ("sponsor_id", "Int64"),
))

VOTES = TableSchema(VoteDTO, (
    ("id", "Int64"),
    ("bill_id", "Int64"),
))

VOTE_RESULTS = TableSchema(VoteResultDTO, (
    ("id", "Int64"),
    ("legislator_id", "Int64"),
    ("vote_id", "Int64"),
    ("vote_type", "Int8"),
))

LEGISLATOR_REPORT = TableSchema(LegislatorReportDTO, (
    ("id", "Int64"),
    ("name", "string"),
    ("num_supported_bills", "Int64"),
    ("num_opposed_bills", "Int64"),
))

BILL_REPORT = TableSchema(BillReportDTO, (
    ("id", "Int64"),
    ("title", "string"),
    ("supporter_count", "Int64"),
    ("opposer_count", "Int64"),
    ("primary_sponsor", "string"),
))
