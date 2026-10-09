import unittest
from dataclasses import dataclass

import pandas as pd
from pandas.testing import assert_frame_equal

from legislative.loading import load_data
from legislative.models import LegislativeData
from legislative.sources.base import LegislativeDataSource
from legislative.validation import DataValidationError


@dataclass
class InMemorySource:
    data: LegislativeData

    def load(self) -> LegislativeData:
        return self.data


def memory_data() -> LegislativeData:
    return LegislativeData(
        legislators=pd.DataFrame({"id": [2, 1], "name": ["Bob", "Alice"]}),
        bills=pd.DataFrame({"id": [10], "title": ["Bill"], "sponsor_id": [999]}),
        votes=pd.DataFrame({"id": [100], "bill_id": [10]}),
        vote_results=pd.DataFrame({"id": [1], "legislator_id": [1], "vote_id": [100], "vote_type": [1]}),
    )


class SourceTests(unittest.TestCase):
    def test_in_memory_source_uses_shared_loading(self):
        source: LegislativeDataSource = InMemorySource(memory_data())
        loaded = load_data(source)
        self.assertEqual(loaded.legislators["id"].tolist(), [2, 1])
        self.assertEqual(loaded.bills["sponsor_id"].tolist(), [999])
        self.assertEqual(str(loaded.legislators["id"].dtype), "Int64")
        self.assertEqual(str(loaded.legislators["name"].dtype), "string")
        self.assertEqual(str(loaded.vote_results["vote_type"].dtype), "Int8")

    def test_loading_does_not_mutate_source_tables(self):
        data = memory_data()
        originals = {name: getattr(data, name).copy(deep=True)
                     for name in ("legislators", "bills", "votes", "vote_results")}
        load_data(InMemorySource(data))
        for name, original in originals.items():
            assert_frame_equal(getattr(data, name), original)

    def test_shared_validation_rejects_invalid_memory_records(self):
        cases = [
            ("legislators", "id", [1, 1], "duplicate id"),
            ("legislators", "id", [True, False], "integer"),
            ("legislators", "id", [2.0, 1.0], "integer"),
            ("legislators", "name", ["Bob", None], "required"),
            ("legislators", "name", [12, "Alice"], "text"),
            ("votes", "bill_id", [999], "unknown bill_id"),
            ("vote_results", "legislator_id", [999], "unknown legislator_id"),
            ("vote_results", "vote_type", [3], "vote_type"),
        ]
        for table, column, values, message in cases:
            with self.subTest(table=table, column=column, message=message):
                data = memory_data()
                getattr(data, table)[column] = values
                with self.assertRaisesRegex(DataValidationError, message):
                    load_data(InMemorySource(data))

    def test_shared_validation_checks_columns(self):
        data = memory_data()
        data.bills = data.bills.drop(columns="title")
        with self.assertRaisesRegex(DataValidationError, "missing columns: title"):
            load_data(InMemorySource(data))


if __name__ == "__main__":
    unittest.main()
