from dataclasses import dataclass
from enum import IntEnum
from typing import NewType

import pandas as pd


LegislatorId = NewType("LegislatorId", int)
BillId = NewType("BillId", int)
VoteId = NewType("VoteId", int)
VoteResultId = NewType("VoteResultId", int)


class VoteType(IntEnum):
    Y = 1
    N = 2


@dataclass(frozen=True, slots=True)
class LegislatorDTO:
    id: LegislatorId
    name: str


@dataclass(frozen=True, slots=True)
class BillDTO:
    id: BillId
    title: str
    sponsor_id: LegislatorId


@dataclass(frozen=True, slots=True)
class VoteDTO:
    id: VoteId
    bill_id: BillId


@dataclass(frozen=True, slots=True)
class VoteResultDTO:
    id: VoteResultId
    legislator_id: LegislatorId
    vote_id: VoteId
    vote_type: VoteType


@dataclass(frozen=True, slots=True)
class LegislativeRecords:
    legislators: tuple[LegislatorDTO, ...]
    bills: tuple[BillDTO, ...]
    votes: tuple[VoteDTO, ...]
    vote_results: tuple[VoteResultDTO, ...]


@dataclass
class LegislativeData:
    legislators: pd.DataFrame
    bills: pd.DataFrame
    votes: pd.DataFrame
    vote_results: pd.DataFrame
