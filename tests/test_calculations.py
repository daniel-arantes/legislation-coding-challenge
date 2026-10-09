import unittest

import pandas as pd
from pandas.testing import assert_frame_equal

from legislative.calculations import create_bill_report, create_legislator_report
from legislative.models import LegislativeData
from legislative.reports import BillReport, LegislatorReport


def sample_data() -> LegislativeData:
    return LegislativeData(
        legislators=pd.DataFrame({
            "id": pd.Series([3, 1, 2], dtype="Int64"),
            "name": pd.Series(["Carol", "Alice", "Bob"], dtype="string"),
        }),
        bills=pd.DataFrame({
            "id": pd.Series([20, 30, 10], dtype="Int64"),
            "title": pd.Series(["Bill two", "Unvoted bill", "Bill, one"], dtype="string"),
            "sponsor_id": pd.Series([999, 2, 1], dtype="Int64"),
        }),
        votes=pd.DataFrame({
            "id": pd.Series([200, 100], dtype="Int64"),
            "bill_id": pd.Series([10, 20], dtype="Int64"),
        }),
        vote_results=pd.DataFrame({
            "id": pd.Series([1, 2, 3], dtype="Int64"),
            "legislator_id": pd.Series([1, 1, 2], dtype="Int64"),
            "vote_id": pd.Series([100, 200, 200], dtype="Int64"),
            "vote_type": pd.Series([1, 2, 1], dtype="Int8"),
        }),
    )


def expected_legislators() -> pd.DataFrame:
    return pd.DataFrame({
        "id": pd.Series([3, 1, 2], dtype="Int64"),
        "name": pd.Series(["Carol", "Alice", "Bob"], dtype="string"),
        "num_supported_bills": pd.Series([0, 1, 1], dtype="Int64"),
        "num_opposed_bills": pd.Series([0, 1, 0], dtype="Int64"),
    })


def expected_bills() -> pd.DataFrame:
    return pd.DataFrame({
        "id": pd.Series([20, 30, 10], dtype="Int64"),
        "title": pd.Series(["Bill two", "Unvoted bill", "Bill, one"], dtype="string"),
        "supporter_count": pd.Series([1, 0, 1], dtype="Int64"),
        "opposer_count": pd.Series([0, 0, 1], dtype="Int64"),
        "primary_sponsor": pd.Series(["Unknown", "Bob", "Alice"], dtype="string"),
    })


class CalculationTests(unittest.TestCase):
    def test_legislator_report(self):
        report = create_legislator_report(sample_data())
        self.assertIsInstance(report, LegislatorReport)
        assert_frame_equal(report.data, expected_legislators())

    def test_bill_report(self):
        report = create_bill_report(sample_data())
        self.assertIsInstance(report, BillReport)
        assert_frame_equal(report.data, expected_bills())

    def test_legislator_report_without_results(self):
        data = sample_data()
        data.vote_results = data.vote_results.iloc[:0].copy()
        expected = expected_legislators()
        expected["num_supported_bills"] = pd.Series([0, 0, 0], dtype="Int64")
        expected["num_opposed_bills"] = pd.Series([0, 0, 0], dtype="Int64")
        assert_frame_equal(create_legislator_report(data).data, expected)

    def test_bill_report_without_results(self):
        data = sample_data()
        data.vote_results = data.vote_results.iloc[:0].copy()
        expected = expected_bills()
        expected["supporter_count"] = pd.Series([0, 0, 0], dtype="Int64")
        expected["opposer_count"] = pd.Series([0, 0, 0], dtype="Int64")
        assert_frame_equal(create_bill_report(data).data, expected)

    def test_empty_legislator_report(self):
        data = sample_data()
        for name in ("legislators", "bills", "votes", "vote_results"):
            setattr(data, name, getattr(data, name).iloc[:0].copy())
        assert_frame_equal(create_legislator_report(data).data,
                           expected_legislators().iloc[:0].copy())

    def test_empty_bill_report(self):
        data = sample_data()
        for name in ("legislators", "bills", "votes", "vote_results"):
            setattr(data, name, getattr(data, name).iloc[:0].copy())
        assert_frame_equal(create_bill_report(data).data,
                           expected_bills().iloc[:0].copy())


if __name__ == "__main__":
    unittest.main()
