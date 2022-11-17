#!/usr/bin/env python3.11
import json
import csv

# Calculate Errors and log to .csv file
def writeErrorsToCSV(
  studentsLen:  int,
  conflictsDir: str = './output/raw/json/conflicts.json',
  outputDir:    str = './output/raw/csv/errors.csv'
) -> None:
  # Error Table calulation / output  
  with open(conflictsDir) as file:
    conflicts = json.load(file)

  totalCritical = conflicts["Critical"]["Students"]
  totalAcceptable = conflicts["Acceptable"]["Students"]

  with open(outputDir, 'w') as file:
    writer = csv.writer(file)
    # Write header
    data = (
      "Error Type",
      "Error %",
      "Success %",
      "Student Error Ratio"
    )
    writer.writerow(data)

    errorsC  = round(totalCritical / studentsLen * 100, 2)
    errorsA  = round(totalAcceptable / studentsLen * 100, 2)
    successC = round(100 - errorsC, 2)
    successA = round(100 - errorsA, 2)

    criticalData = (
      'Critical',
      f'{errorsC} %',
      f'{successC} %',
      f'{totalCritical}/{studentsLen} Students'
    )
    writer.writerow(criticalData)

    acceptableData = (
      'Acceptable',
      f'{errorsA} %',
      f'{successA} %',
      f'{totalAcceptable}/{studentsLen} Students'
    )
    writer.writerow(acceptableData)
