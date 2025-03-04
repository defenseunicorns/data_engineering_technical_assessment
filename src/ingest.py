import pandas as pd
from sqlalchemy.sql import text
from logs import setup_logging, get_logger
from comms import test_connections, check_schema

log = get_logger()

# IMPLEMENT THIS METHOD
def ingest_data():
   test_connections()

if __name__ == "__main__":
   setup_logging()
   test_connections()
   check_schema()
