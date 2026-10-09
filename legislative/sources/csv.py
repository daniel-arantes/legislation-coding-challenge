import csv
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from legislative.models import LegislativeData
from legislative.schemas import BILLS, LEGISLATORS, VOTES, VOTE_RESULTS, RecordT, TableSchema
from legislative.validation import DataValidationError


def read_table(path: Path, schema: TableSchema[RecordT]) -> pd.DataFrame:
    try:
        with path.open(encoding="utf-8-sig", newline="") as source:
            reader = csv.reader(source, strict=True)
            headers = next(reader, [])
            if len(headers) != len(set(headers)):
                raise DataValidationError(f"{path.name}: duplicate column names")
            for row in reader:
                if len(row) != len(headers):
                    raise DataValidationError(f"{path.name}: line {reader.line_num}: row width does not match header")
            if not headers:
                return pd.DataFrame()
            source.seek(0)
            return pd.read_csv(source, usecols=lambda column: column in schema.columns,
                               dtype="string", na_filter=False, skip_blank_lines=False)
    except (OSError, UnicodeError, csv.Error, pd.errors.ParserError) as error:
        raise DataValidationError(f"{path.name}: {error}") from error


@dataclass(frozen=True)
class CsvDataSource:
    input_dir: Path

    def load(self) -> LegislativeData:
        return LegislativeData(
            legislators=read_table(self.input_dir / "legislators.csv", LEGISLATORS),
            bills=read_table(self.input_dir / "bills.csv", BILLS),
            votes=read_table(self.input_dir / "votes.csv", VOTES),
            vote_results=read_table(self.input_dir / "vote_results.csv", VOTE_RESULTS),
        )
