#!/usr/bin/env python3.11
import json
import csv

# Get all requested courses from data
def getCourses(
  data_dir: str,
  log: int=False,
  log_dir: str='./output/raw/courses.json',
) -> dict[dict[str: any]]:

  courses = {}

  with open(data_dir, newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
      exists = False
      for course in courses:
        exists = True if courses[course]["CrsNo"] == row["CrsNo"] else False
        if exists: break
      if not exists:
        courses[row["CrsNo"]] = {
          "CrsNo": row["CrsNo"],
          "Requests": 0,
          "Description": row["Description"]
        }

  if log:
    with open(log_dir, "w") as outfile:
      json.dump(courses, outfile, indent=2)
        
  return courses
