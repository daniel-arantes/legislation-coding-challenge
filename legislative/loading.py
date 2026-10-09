from legislative.models import LegislativeData
from legislative.sources.base import LegislativeDataSource
from legislative.validation import validate_data


def load_data(source: LegislativeDataSource) -> LegislativeData:
    return validate_data(source.load())
