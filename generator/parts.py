import numpy as np
import pandas as pd


NUM_PARTS = 300
NUM_MANUFACTURERS = 10

class Part:
   def __init__(self, manufacturer:int, partno:int):
      self.manufacturer = manufacturer
      self.partno = partno


   def get_manufacturer_id(self):
      return self.manufacturer
   
   def get_partno(self):
      return self.partno
   
def get_parts():
   parts = []
   manufacturers = list(np.random.randint(1000,9999, size=NUM_MANUFACTURERS))
   manu_parts = np.random.normal(NUM_PARTS/NUM_MANUFACTURERS, 20, size=10).astype(np.int16)
   for i in range(NUM_MANUFACTURERS):
      manufacturer = manufacturers[i]
      num_manu_parts = manu_parts[i]
      for p in range(num_manu_parts):
         partno = int(np.random.randint(100000, 999999, size=1))
         parts.append(Part(manufacturer, partno))
   return parts
