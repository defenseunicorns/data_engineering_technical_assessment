from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.sql import text
from logs import get_logger, setup_logging

import pandas as pd

log = get_logger()

ENGINES = dict()
USER = "orders"
PWD = "s3cr3tp455w0rd"
DB = "orders"

def get_connection_string():
   user = USER
   host = "localhost"
   pwd = PWD
   db = DB
   con_str = f"postgresql+psycopg2://{user}:{pwd}@{host}:5432/{db}"
   return con_str

def get_engine():
   if "local" not in ENGINES:
      ENGINES["local"] = create_engine(get_connection_string())
   else:
      eng = ENGINES["local"]
      try:
         with eng.connect() as con:
            con.execute(text("SELECT 1"))
      except Exception as e:
         log.warning(f'Error connectin to postgres engine: {e}')
         ENGINES["local"] = create_engine(get_connection_string())
   return ENGINES["local"]
