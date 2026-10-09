import pandas as pd

from legislative.models import LegislativeData, VoteType
from legislative.reports import BillReport, LegislatorReport
from legislative.schemas import BILL_REPORT, LEGISLATOR_REPORT


def count_votes(results: pd.DataFrame, key: str, supported: str, opposed: str) -> pd.DataFrame:
    counts = results.loc[:, [key]].assign(**{
        supported: results["vote_type"].eq(VoteType.Y).astype("Int64"),
        opposed: results["vote_type"].eq(VoteType.N).astype("Int64"),
    })
    return counts.groupby(key, sort=False)[[supported, opposed]].sum().reset_index()


def create_legislator_report(data: LegislativeData) -> LegislatorReport:
    supported, opposed = "num_supported_bills", "num_opposed_bills"
    counts = count_votes(data.vote_results, "legislator_id", supported, opposed)
    report = data.legislators.merge(counts, how="left", left_on="id",
                                    right_on="legislator_id", sort=False, validate="one_to_one")
    report[[supported, opposed]] = report[[supported, opposed]].fillna(0)
    report = report.loc[:, list(LEGISLATOR_REPORT.columns)].astype(LEGISLATOR_REPORT.dtypes)
    return LegislatorReport(report)


def create_bill_report(data: LegislativeData) -> BillReport:
    supported, opposed = "supporter_count", "opposer_count"
    results = data.vote_results.loc[:, ["vote_id", "vote_type"]].merge(
        data.votes.loc[:, ["id", "bill_id"]], how="left", left_on="vote_id",
        right_on="id", sort=False, validate="many_to_one",
    )
    counts = count_votes(results, "bill_id", supported, opposed)
    report = data.bills.merge(counts, how="left", left_on="id", right_on="bill_id",
                             sort=False, validate="one_to_one")
    sponsors = data.legislators.loc[:, ["id", "name"]].rename(
        columns={"id": "sponsor_id", "name": "primary_sponsor"},
    )
    report = report.merge(sponsors, how="left", on="sponsor_id", sort=False,
                          validate="many_to_one")
    report[[supported, opposed]] = report[[supported, opposed]].fillna(0)
    report["primary_sponsor"] = report["primary_sponsor"].fillna("Unknown")
    report = report.loc[:, list(BILL_REPORT.columns)].astype(BILL_REPORT.dtypes)
    return BillReport(report)
