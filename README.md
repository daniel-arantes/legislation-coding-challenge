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
- `legislative/sources/base.py`: Data-source protocol.
- `legislative/sources/csv.py`: CSV parsing adapter.
- `legislative/loading.py`: Source-independent loading entry point.
- `legislative/validation.py`: Shared schema normalization and relationship validation.
- `legislative/input/`: The four supplied input CSVs.
- `docs/`: PDF with test definitions and expected outputs.

## Tests

### Calculation tests:

Test the calculations independently from data loading and validation, using defined sample data in pandas DataFrame format.

```sh
python -m unittest discover -s tests -p test_calculations.py -v
```

Supported scenarios:

- Legislator report with vote results
- Bill report with vote results
- Legislator report without vote results
- Bill report without vote results
- Empty legislator report
- Empty bill report

### CSV Loading tests:

Test CSV parsing and shared validation together, using temporary CSV files and the supplied dataset.

```sh
python -m unittest discover -s tests -p test_loading.py -v
```

Supported scenarios:

- Valid CSV data with input ordering, explicit dtypes, quoted text, and missing sponsor references
- UTF-8 BOM, extra columns, reordered columns, literal NA values, and preserved text whitespace
- Header-only files producing empty typed tables
- Quoted multiline text
- Large integer precision and signed 64-bit boundaries
- Invalid inputs: missing or duplicate columns, malformed CSV rows and quoting, blank required values, invalid integers, duplicate IDs, out-of-range values, unknown references, multiple votes per bill, invalid vote types, and duplicate legislator/vote pairs
- Missing input files
- Supplied dataset containing 20 legislators, 2 bills, 2 votes, and 38 results

### Source tests:

Test the source-independent loading boundary and shared validation, using an in-memory adapter that implements the data-source protocol.

```sh
python -m unittest discover -s tests -p test_sources.py -v
```

Supported scenarios:

- In-memory source loading with canonical dtypes and missing sponsor references
- Source tables remaining unchanged after loading and validation
- Invalid in-memory records: duplicate IDs, boolean or floating-point IDs, missing or non-text names, unknown references, and invalid vote types
- Missing required columns
