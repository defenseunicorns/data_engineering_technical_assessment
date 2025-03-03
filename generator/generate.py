import numpy as np
import pandas as pd
import uuid
import json

from users import get_users
from components import get_components
from parts import get_parts

NUM_ORDERS = 500
STATUS = ['PENDING', 'ORDERED', 'SHIPPED', 'RECEIVED']
PRIORITY_PROB = .1
BASE_BREAK_PROB = .001
START_DATE = pd.to_datetime("1988-01-01")
END_DATE = pd.to_datetime("2025-01-01")

GENERATE_PATH = "../data/"

def get_random_dates(start, end, n):
    start_u = start.value//10**9
    end_u = end.value//10**9
    return pd.to_datetime((10**9*np.random.randint(start_u, end_u, n, np.int64)).view('M8[ns]'))

def generate_dummy_allowed_list(components, parts):
   comp_names = []
   manus = []
   partnos = []
   for comp in components:
      ps = np.random.choice(parts, 2, replace=False)
      comp_name = comp.get_name()
      comp_names += [comp_name, comp_name]
      manus += [part.get_manufacturer_id() for part in ps]
      partnos += [part.get_partno() for part in ps]
   df = pd.DataFrame({
      "component_name":comp_names,
      "manufacturer_id":manus,
      "part_no":partnos
   }).to_csv(f"{GENERATE_PATH}allowed_parts.csv", index=False)

def generate_allowed_list(components, parts, dates):
   comp_names = [comp.get_name() for comp in components]
   manus = [part.get_manufacturer_id() for part in parts]
   partnos = [part.get_partno() for part in parts]
   df = pd.read_csv(f"{GENERATE_PATH}allowed_parts.csv")
   frame = pd.DataFrame({
      "component_name":comp_names,
      "manufacturer_id":manus,
      "part_no":partnos,
      "date":dates
   })
   two_thirds = NUM_ORDERS*2//3
   cutoff_date = pd.to_datetime(frame["date"].nlargest(two_thirds).values[-1])
   frame = frame[frame["date"]>=cutoff_date].drop(columns=["date"])
   df = pd.concat([df,frame]).drop_duplicates()
   df.to_csv(f"{GENERATE_PATH}allowed_parts.csv", index=False)

def generate_arrays():
   components = get_components()
   parts = get_parts()
   users = get_users()
   generate_dummy_allowed_list(components, parts)
   orderers = np.random.choice(users, size=NUM_ORDERS, replace=True)
   comps = np.random.choice(components, size=NUM_ORDERS, replace=True)
   parts = np.random.choice(parts, size=NUM_ORDERS, replace=True)
   serials = np.random.choice(np.arange(1000,9999999), NUM_ORDERS, replace=False)
   dates = get_random_dates(START_DATE, END_DATE, NUM_ORDERS)
   priorities = np.random.choice([True, False], size=NUM_ORDERS, replace=True, p=[PRIORITY_PROB, 1-PRIORITY_PROB])
   generate_allowed_list(comps, parts, dates)
   return orderers, comps, parts, serials, dates, priorities

def generate_data():
   uuids = []
   comp_names = []
   system_names = []
   manufacturers = []
   partnos = []
   serialnos = []
   statuses = []
   status_dates = []
   ordered_by = []
   comp_pris = []
   users, components, parts, serials, dates, priorities = generate_arrays()
   for i in range(NUM_ORDERS):
      uid = str(uuid.uuid4())
      user = users[i].get_name_random_format()
      comp = components[i]
      comp_name = comp.get_randomized_name()
      system = comp.get_system()
      part = parts[i]
      serial = serials[i]
      manu = part.get_manufacturer_id()
      partno = part.get_partno()
      date = dates[i]
      pri = priorities[i]
      beginning_status = 0
      if pri:
         beginning_status = 1
      break_prob = 0
      for s in range(beginning_status, len(STATUS)):
         if np.random.random() < break_prob:
            break
         status = STATUS[s]
         date = get_random_dates(date, date+pd.Timedelta(days=10), 1)[0]
         uuids.append(uid)
         comp_names.append(comp_name)
         system_names.append(system)
         manufacturers.append(manu)
         partnos.append(partno)
         serialnos.append(serial)
         statuses.append(status)
         ordered_by.append(user)
         status_dates.append(date)
         comp_pris.append(pri)
         break_prob = BASE_BREAK_PROB*(4**s)
   return {
      "order_uuid":uuids,
      "component_name":comp_names,
      "system_name":system_names,
      "manufacturer_id":manufacturers,
      "part_no":partnos,
      "serial_no":serialnos,
      "status":statuses,
      "status_date":status_dates,
      "ordered_by":ordered_by,
      "comp_pri":comp_pris
   }

def update_json(row, json_updates):
    update = {
        "order_uuid":row['order_uuid'],
        "datetime":row["status_date"].strftime("%m-%d-%Y %H:%M:%S"),
        "status":row["status"]
    }
    if update["status"] == "ORDERED":
        update["details"] = {
            "component_name":row["component_name"],
            "system_name":row["system_name"],
            "manufacturer_id":row["manufacturer_id"],
            "part_number":row["part_no"],
            "serial_number":row["serial_no"],
            "ordered_by":row["ordered_by"]
        }
    json_updates.append(update)


def create_streaming(df:pd.DataFrame):
   pri_json = []
   pris = df[df['comp_pri']]
   pris.apply(update_json, json_updates=pri_json, axis=1)
   with open(f"{GENERATE_PATH}streaming_orders.json", "w") as fh:
      json.dump(pri_json, fh, indent=4)

def create_parquet(df):
   frame = df[~df['comp_pri']].reset_index(drop=True)
   frame.loc[frame["status"]!="PENDING", "ordered_by"] = None
   frame = frame.iloc[np.random.permutation(len(frame))]
   frame = frame.drop(columns=["comp_pri"])
   frame.to_csv(f"{GENERATE_PATH}batch_orders.csv", index=False)

def clean_component_name(row):
   comp = row["component_name"]
   return comp.replace(" ", "_").lower()


def generate():
   df = pd.DataFrame(generate_data())
   create_streaming(df)
   create_parquet(df)

if __name__ == '__main__':
   generate()
