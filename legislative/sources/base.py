from typing import Protocol

from legislative.models import LegislativeData


class LegislativeDataSource(Protocol):
    def load(self) -> LegislativeData: ...
