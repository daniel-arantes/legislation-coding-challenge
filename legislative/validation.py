import pandas as pd

from legislative.models import LegislativeData, VoteType
from legislative.schemas import BILLS, LEGISLATORS, VOTES, VOTE_RESULTS, RecordT, TableSchema


class DataValidationError(ValueError):
    pass


def validate_table(frame: pd.DataFrame, schema: TableSchema[RecordT], name: str) -> pd.DataFrame:
    if not frame.columns.is_unique:
        raise DataValidationError(f"{name}: duplicate column names")
    missing = set(schema.columns) - set(frame.columns)
    if missing:
        raise DataValidationError(f"{name}: missing columns: {', '.join(sorted(missing))}")
    frame = frame.loc[:, list(schema.columns)].copy().reset_index(drop=True)
    for column, dtype in schema.fields:
        values = frame[column]
        text = values.astype("string")
        blank = values.isna() | text.str.strip().eq("")
        if blank.any():
            raise DataValidationError(f"{name}: record {blank[blank].index[0] + 1}: {column} is required")
        if dtype == "string":
            if not all(isinstance(value, str) for value in values):
                raise DataValidationError(f"{name}: {column} must contain text")
            frame[column] = text
            continue
        stripped = text.str.strip()
        invalid = ~stripped.str.fullmatch(r"[+-]?[0-9]+")
        if invalid.any():
            raise DataValidationError(f"{name}: record {invalid[invalid].index[0] + 1}: {column} must be an integer")
        try:
            integers = stripped.map(int)
        except ValueError as error:
            raise DataValidationError(f"{name}: {column} contains an invalid integer") from error
        lower, upper = (-128, 127) if dtype == "Int8" else (-(2**63), 2**63 - 1)
        outside = (integers < lower) | (integers > upper)
        if outside.any():
            raise DataValidationError(f"{name}: record {outside[outside].index[0] + 1}: {column} is outside {dtype} range")
        frame[column] = integers.astype(dtype)

    if frame["id"].duplicated().any():
        raise DataValidationError(f"{name}: duplicate id")
    return frame


def validate_relationships(data: LegislativeData) -> None:
    relationships = (
        ("votes", data.votes, "bill_id", data.bills),
        ("vote_results", data.vote_results, "legislator_id", data.legislators),
        ("vote_results", data.vote_results, "vote_id", data.votes),
    )
    for filename, table, column, referenced in relationships:
        invalid = ~table[column].isin(referenced["id"])
        if invalid.any():
            value = table.loc[invalid, column].iloc[0]
            raise DataValidationError(f"{filename}: unknown {column} {value}")
    if data.votes["bill_id"].duplicated().any():
        raise DataValidationError("votes: more than one vote for the same bill")
    if not data.vote_results["vote_type"].isin([VoteType.Y, VoteType.N]).all():
        raise DataValidationError("vote_results: vote_type must be 1 or 2")
    if data.vote_results.duplicated(["legislator_id", "vote_id"]).any():
        raise DataValidationError("vote_results: duplicate legislator/vote pair")

def validate_data(data: LegislativeData) -> LegislativeData:
    validated = LegislativeData(
        legislators=validate_table(data.legislators, LEGISLATORS, "legislators"),
        bills=validate_table(data.bills, BILLS, "bills"),
        votes=validate_table(data.votes, VOTES, "votes"),
        vote_results=validate_table(data.vote_results, VOTE_RESULTS, "vote_results"),
    )
    validate_relationships(validated)
    return validated
