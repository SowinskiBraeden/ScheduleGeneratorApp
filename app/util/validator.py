#!/usr/bin/env python3
from app.util.globals import Error

# validate user's inputed csv file contains required fields
def validateInputData(inputFileDir: str) -> Error:
  with open(inputFileDir, newline='') as csvfile:
    includes = ['Pupil #', 'CrsNo', 'Description', 'Alternate?']
    data = csvfile.readline().replace('\n', '').replace('\r', '').split(',')
    missing = [e for e in includes if e not in data]
    if len(missing) > 0:
      description = 'You are missing the following: '
      for i in range(len(missing)):
        description = description + f'{missing[i]}, ' if i != len(missing) - 1 else description + f'{missing[i]}'
      missingErr = Error('Missing Required Fields', description)

      return missingErr
    
  return None
