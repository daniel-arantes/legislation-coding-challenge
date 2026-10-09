# Legislative Data Reports

Implementation of the Quorum legislative data challenge.

## Technical Decisions

- Consider CSV files as representation of data sources that could later be replaced with database, json files, avro, parquet, or other storage formats.
- Pandas will be used to handle the data, due to feature set, extension capabilities and support.

## Environment

Developed and tested with Python 3.11.

To install dependencies:

```sh
python -m pip install -r requirements.txt
```

## Files
- `legislative/models.py`: Typed input DTOs, entity ID types, vote values, and input containers.
- `legislative/reports.py`: Independent legislator and bill report DTOs and containers.
- `legislative/schemas.py`: Ordered DataFrame schemas bound to their DTO types.
- `legislative/input/`: The four supplied input CSVs.
- `docs/`: PDF with test definitions and expected outputs.
