import pandas as pd
import json
from sqlalchemy.sql import text
from logs import setup_logging, get_logger
from comms import test_connections, check_schema

log = get_logger()

DATA_PATH = "../data"

def get_batch_data() -> pd.DataFrame:
   """Returns a pandas dataframe for the batch orders parquet"""
   return pd.read_parquet(f"{DATA_PATH}/batch_orders.parquet")

def get_streaming_json() -> list:
   """Returns a list of dictionaries of the streaming messages"""
   with open(f"{DATA_PATH}/streaming_orders.json", "r") as fh:
      messages = json.load(fh)
   return messages

# IMPLEMENT THIS METHOD
def ingest_data():
   df = get_batch_data()
   log.info(f'{df.head()}')
   messages = get_streaming_json()
   log.info(f'{messages[0]}')

if __name__ == "__main__":
   setup_logging()
   test_connections()
   check_schema()
   ingest_data()
