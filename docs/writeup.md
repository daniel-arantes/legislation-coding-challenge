# Solution writeup

## 1. Discuss your solution’s time complexity. What tradeoffs did you make?

Pandas adds flexibility and ease of implementation on the cost of performance and memory usage, specially true for small datasets as the examples given. It's a solid baseline for working with this kind of data without over-engineering a solution, that natively support useful features like aggregates and joins. If performance becomes a bottleneck, pandas can be replaced by a more performant library like Polars or Dask, depending on the scale of data.

Another benefit from using a library like this is the possibility of processing these files in chunks, to bypass memory limitations if needed. It is not implemented now, since it's not required, but it's easy to implement and could be an option when memory usage becomes a concern.

Currently the time complexity is O(n) with respect to the number of rows in the input files, and the space complexity is O(n) with respect to the number of rows in the input files, and O(n+m) with respect to the number of bills and legislators. The main tradeoff made was the choice of library, pandas, to prioritize ease of implementation and flexibility over performance and memory usage.

## 2. How would you change your solution to account for future columns that might be requested, such as “Bill Voted On Date” or “Co-Sponsors”?

A change on columns would require first DTO and schema updates, always accounting for previous schema, contracts and DTOs, without breaking existing code. This means some sort of versioning in handling the source files (so that the old ones don't "stop working" with the newly updated schema, but it is still supported even if the information missing is reported as null, etc)

For example for "bill voted on date" field: This would require an optional date field on "votes" source (since bill can be voted multiple times) that would require specific validation (date not after today, or empty). To report on it, a business decision could be made to either report on the latest voted date, keeping 1:1 cardinality on bill report, change it to 1:N with each row representing one vote date, or exporting on a different format (for example JSON) that accepts arrays to represent fields, so multiple vote dates can be represented and linked to the same bill.

A similar approach would be needed for co-sponsors, except for the specific validation, it is a change that potentially affects cardinality and is potentially requiring a different output format.

## 3. How would you change your solution if instead of receiving CSVs of data, you were given a list of legislators or bills that you should generate a CSV for?

Current solution is extensible, since it uses adapters for different formats, both for input and output. If the request format is expected to be part of an HTTP request for example, it can be easily adapt to accept JSON or XML content, without affecting or refactoring anything. It is the same for txt files, excel spreadsheets, etc.

For output, the same, report can be exported to different formats by creating new adapters, as long as it follows the same protocol and contracts.

## 4. How long did you spend working on the assignment?

Approximately 2.5 hours, including implementation, review, and testing. Development used an AI coding assistant, with human plan, direction, documenting and review. The approach used for this coding task is the same as a real case scenario, with multi-step planning, task being split into multiple smaller, incremental sub-tasks, and frequent validation and steering before it reaches to the goal, as a team would do with small AI-coded pull requests.