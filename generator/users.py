import numpy as np

USERS = [
   "John Doe",
   "Jane Doe",
   "Richard Feynman",
   "Michael Bolton",
   "Michael Scott",
   "JL Picard",
   "Doug Unicorn",
   "Racecar Palindrome"
]

class User:
   def __init__(self, first_name: str, last_name: str):
      self.first_name = first_name
      self.last_name = last_name

   def get_name(self):
      return f'{self.first_name.lower()}.{self.last_name.lower()}'

   def get_name_random_format(self):

      p = np.random.random()
      if p < .34:
         return f'{self.first_name} {self.last_name}'
      elif p < .67:
         return f'{self.last_name}, {self.first_name}'
      else:
         return self.get_name()

def get_users():
   users = []
   for user in USERS:
      names = user.split()
      users.append(User(names[0], names[1]))
   return users
