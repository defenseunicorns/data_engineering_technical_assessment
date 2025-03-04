# Defense Unicorns - Data Engineering Practical

## Quickstart
* Clone this repository
* Create a branch `git branch submission/first-last` / `git switch submission/first-last`
* Develop and test your solution
   * You can write 
* Run `make submit` to create the pg_dump file
* Run `make ingest` to test full ingestion in docker compose
   * WARNING: This will reset your postgres database
* push your branch: `git commit` and `git push origin submission/first-last`

## Overview

This exercise is designed to assess a data engineering candidate’s ability to manipulate data programmatically, analyze insights, and demonstrate their thought process in designing data systems. Candidates should complete the assessment within a four-hour time limit for code submission.

Please note that this exercise is solely for evaluation purposes and will not be used in real-world applications by Defense Unicorns.

### Domain Overview

This exercise involves building a system to track parts orders for truck components. The company, which manufactures trucks, previously relied on a legacy ordering system that was lost due to poor disaster planning. The only remaining data is in the /data folder as extracts.

A DBA has designed a new PostgreSQL schema to store the recovered legacy data and track new orders. The system processes priority orders via a message queue and regular orders through nightly batch processing.

Your task is to write scripts to clean and ingest the legacy data, simulating both batch and stream processing. You should spend no more than four hours on the coding portion. Be prepared to discuss your approach during the assessment, but you do not need to submit written answers to the questions.

### Evaluation criteria
To "pass" the assessment, there must be valid entries in the `components`, `parts`, and `users` table for each element in the data.  To be considered competetive, there should be an entry in the `orders` table for each `order_uuid` in the raw data.  There will be other automated tests to check for valid cleaning and formatting as well.  There will also be a general assessment of code quality and complexity, but the highest weight is getting the right data into the database.

### Questions
Be prepared to answer questions about the design and implementation of the storage.  Examples include:
* Are there any important pieces of legacy information lost in the current schema?
* Assuming a year of orders are kept in the database before being moved to cold storage, how many orders per year would you feel comfortable supporting with this architecture?
* If you needed to build a REST API to serve data about Orders, what main endpoint would you use and how would you design it (query params, http method(s) etc)?
* If you could design the storage from scratch, what would you change?

## Data diagram

![connections in schema and parquet dump](./docs/schema.png "Data Schema")

## Data descriptions - Postgres schema

The following are the descriptions of the fields in the new postgres schema.  Keep in mind the legacy data may or may not meet these descriptions / types, or could have nonstandard formatting (names may appear in multiple places with different capitalization, for example).  The schema can be seen in `postgres/schema.sql`

### Comoponent

A component is a part that can be used for business purposes (install in a truck).  Fields:
* `component_id`: database assigned integer primary key
* `component_name`: VARCHAR(64) name of component
* `system_name`: VARCHAR(64) name of system (valid names are `HYDRAULIC`, `ELECTRICAL`, `TRANSMISSION`, `NAVIGATION`)

### Part

A part is something that can be ordered, like a bolt or a chassis.  Parts are generalized to a manufacturer and part number, not specified to a serial number (physical instance of a part).  The fields are:
* `part_id`: database assigned integer primary key
* `manufacturer_id`: integer id for a manufacturer
* `part_no`: Manufacturer's part number for the specific part
The `manufacturer_id` and `part_no` tuples must be unique

### Allowed Parts

When ordering parts against components, it is important that the parts are allowed to be ordered against that component.  Unfortunately, only the current allowed parts list survived the disaster so the deprecated parts parings must be inferred from the orders.  You can assume a pairing that is not in `data/allowed_parts.csv` is deprecated.  Allowed parts mappings:
* `component_id`: References components table
* `part_id`: References parts table
* `deprecated`: Whether this component / part pairing is currently in the allowed parts list
`component_id` and `part_id` tuples must be unique (and serve as the primary key)

### Users

This is a simple lookup table to hold user information.  Fields:
* `user_id`: database assigned integer primary key
* `user_name`: VARCHAR(32) format should be `first_name.last_name`

### Orders

This is the main table to track orders.  It has the following fields:
* `order_id`: database assigned integer primary key
* `component_id`: References components table
* `part_id`: References parts table
* `serial_no`: Integer serial number of part ordered
* `comp_priority`: Boolean, set to true if this is a priority order
* `order_date`: Datetime the date status was set to `ORDERED`
* `ordered_by`: References `users.user_id` that submitted the order
* `status`: VARCHAR(16), current order status. valid entries are `PENDING`, `ORDERED`, `SHIPPED`, and `RECEIVED`
* `status_date`: Datetime the `status` field was set or updated
* an `order_id` is uniquely defined by the combination of `comopnent_id`, `part_id`, and `serial_no`.
* The `component_id`, `part_id` pairing must exist in the `allowed_parts` table

## Data descriptions - Data dumps

### Allowed parts list
Current allowed parts list has the following format / aggregation challenges and can be found in the `data/allowed_parts.csv`

* `component_name`: string lower case name of component with underscores
* `manufacturer_id`: integer manufacturer id
* `part_no`: integer part number

### Batch Order Data
The batch processing dump is in the `data/batch_orders.parquet` file and the streaming dump is in the `data/streaming_orders.json`.  Both have the following general fields, as well as the type of cleaning needed to be completed
* `order_uuid`: UUID the shipping system uses to keep track of orders
* `component_name`: name of the component (multiple cases, spaces may be `_` characters)
* `system_name`: name of the system (no cleaning required)
* `manufacturer_id`: integer id of the manufactuer (no cleaning required)
* `part_no`: integer part number (no cleaning required)
* `serial_no`: integer serial number (no cleaning required)
* `status`: status of order (no cleaning required)
* `status_date`: datetime of update
* `ordered_by`: Name of user who ordered part (only shows in `PENDING` rows for parquet or `ORDERED` messages for the streaming format, different name formats)

### Priority (streaming) Order Data
The streaming data json has the following schema:
```json
{
   "order_uuid" : "string",
   "datetime" : "string, fmt: MM-DD-YYYY HH:MM:SS",
   "status": "string",
   "details":
   {
      "component_name": "string",
      "system_name": "string",
      "manufacturer_id": "int",
      "part_number": "int",
      "serial_number": "int",
      "ordered_by": "string"
   }
}
```
The `details` field is optional and is only included on `ORDERED` status messages.  For a given order, the messages are found in chronological order in the json dump, although the orders themselves are jumbled.  Process these message by message to simulate receiving streaming data.

### Cleaning required
* Transform the component names into `lowercase_with_underscore_spaces` format
* Transform the user names into `first_name.last_name` format
* Ensure there is a valid entry in the `allowed_parts` table prior to attempting to insert an order
* The `ordered_by` field in `data/batch_orders.parquet` may have some corrupt entries, be sure to pull from valid rows.

## Development and Evaluation
Most of the setup can be done via Make targets.  Here is a list of the relevant targets:
* `make help` - shows major targets
* `make help-dev` - shows helper targets
* `make dev-up` - stands up a new postgres instance with the correct table schema in `postgres/schema.sql`
* `make ingest` - builds the solution image from the `/src` folder and runs it using docker-compose

Your ingestion script's entrypoint is in the method `ingest_data()` in `src/ingest.py`.

During development, feel free to push commits to your branch.  The automated tests will not be run until after the time has expired.

### Development Environment
Requirements:
* Internet connection (for pulling images from DockerHub)
* Docker
* Python 3.8+: If you need to use a lower version of python, make sure to change the `/rc/Dockerfile` and `requirements.txt` as the ingestion script will be run by that image.

Use `make dev-up` to stand up the database.  Here is a list of files for the solution:
* `src/ingest.py` entrypoint for ingestion, modify the `ingest_data()` method.
* `src/comms.py` contains a framework to connect to the postgres instance.
* `src/requirements.txt` keep track of dependencies here for the solution image to build.

If you include additionaly libraries or dependencies in your ingestion script, make sure you add them to `/src/requirements.txt` for the docker image to build and run successfully.

### Testing your solution

You may develop tests for your solution in the `/src/tests.py` file.  The default way these are implemented are using pytest, which will run any method that begins with `test`.  To run the tests, you can run `make run-tests` from the parent directory or `python -m pytest tests.py` from `src/`.

It is recommended for you to run an end-2-end test using docker compose.  This will tear down and rebuild the postgres database from scratch using the ingestion image.  You can run this test with `make ingest`, which will also save the logs from the ingestion container to `solution_logs.txt`.  This is not required to pass but is recommended to ensure the automated tests run successfully.

### Submission

The primary way we will evaluate your submission is to build and run the solution image against postgres using docker-compose, similar to the `make ingest` target.  We will then run some automated tests against the data in postgres.

As a backup, please run `make submit` prior to making and pushing your submission commit which will build the following artifacts as a tarball (again this is a backup if there are problems with the container image)
* `submission/pg_dump.tar.gz` - pg_dump of orders database
* `src.tar.gz` - tarball of the `src` directory

Once you are satisifed with your solution and have created the pg_dump file, push your full solution to your branch.
