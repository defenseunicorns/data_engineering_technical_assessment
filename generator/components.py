import numpy as np
import pandas as pd

SYSTEMS = {
   "HYDRAULIC": 20,
   "ELECTRICAL": 30,
   "TRANSMISSION": 10,
   "NAVIGATION": 8
}

TYPES = [
   "flange",
   "bolt",
   "o-ring",
   "filter",
   "pump",
   "drain",
   "chassis",
   "screw",
   "joint",
   "bearing",
   "wheel",
   "sensor",
   "casing",
   "weld",
   "wiring",
   "tank",
   "piston",
   "plug",
]

LOCATIONS = [
   "cabin",
   "wheel-well",
   "bed",
   "engine-bay",
   "passenger",
   "driver",
   "roof",
]

DESCRIPTORS = [
   "stabilizer",
   "cover",
   "bracket",
   "holder",
]

class Component:
   def __init__(self, name:str, system:str):
      self.name = name
      self.system = system.upper()

   def get_name(self):
      return self.name
   
   def get_randomized_name(self):
      name = self.name
      if np.random.random() < .5:
         name = name.replace("_", " ")
      if np.random.random() < .5:
         name = name.capitalize()
      return name
   
   def get_system(self):
      return self.system
   
   def get_randomized_system(self):
      system = self.system.upper()
      p = np.random.random()
      if p < .34:
         system = system.lower()
      elif p < .67:
         system = system[:3].upper()
      return system

def create_name(row, system):
   name = f"{row['location']}_{row['type']}"
   if row['mask']:
      name += f"_{row['description']}"
   return name + f"_{system[:3]}"

def get_name_aggs(row, names):
   if row['mask'] == 1:
      names.append(row['name'])
   else:
      for i in range(row['mask']):
         name = row['name']
         new_name = name + f'_{i+1:03d}'
         names.append(new_name)

def get_components():
   comps = []
   for system, num_components in SYSTEMS.items():
      locations = np.random.choice(LOCATIONS, num_components)
      types = np.random.choice(TYPES, num_components)
      descriptions = np.random.choice(DESCRIPTORS, num_components)
      mask = np.random.choice([True, False], size=num_components, p=[.1, .9])
      df = pd.DataFrame({"location":locations,
                        "type":types,
                        "description":descriptions,
                        "mask":mask})
      df['name'] = df.apply(create_name, axis=1, system=system)
      names = []
      df = df.groupby("name").count().reset_index()
      df.apply(get_name_aggs, names=names, axis=1)
      for name in names:
         comps.append(Component(name, system))
   return comps
