#!/usr/bin/env python3.11
from app.util.globals import Error

def validateInputData(inputFileDir: str) -> Error:
  with open(inputFileDir, newline='') as csvfile:
    includes = ['Pupil #', 'CrsNo', 'Description', 'Alternate?']
    data = csvfile.readline().replace('\n', '').split(',')
    missing = [e for e in includes if e not in data]
    if len(missing) > 0:
      description = 'You are missing the following: '
      for i in range(len(missing)):
        if i != len(missing) - 1: description += f'{missing[i]}, '
        else: description += f'{missing[i]}'
      missingErr = Error('Missing Required Fields', description)

      return missingErr
    
  return None
