#!/usr/bin/env python3.11
import json
import csv
from app.util.estimateGrade import getGrade

# Get all requested courses from data
def getCourses(
  data_dir: str,
  log:      int = False,
  log_dir:  str = './output/raw/courses.json',
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
        grade = getGrade(row["CrsNo"], row["Description"])
        courses[row["CrsNo"]] = {
          "CrsNo": row["CrsNo"],
          "Requests": 0,
          "Description": row["Description"],
          "Sem1": 0,
          "Sem2":0,
          "Grade": grade
        }

  if log:
    with open(log_dir, "w") as outfile:
      json.dump(courses, outfile, indent=2)
        
  return courses

# Writes all course data to csv file
def writeCoursesToCSV(courses: dict, output_dir: str='./output/raw/csv/courses.csv') -> None:
  with open(output_dir, 'w') as file:
    writer = csv.writer(file)
    # Write header
    data = ("CrsNo", "Description", "Grade", "Requests", "First sem. # of Classes", "Second sem. # of Classes", "Total # of Classes")
    writer.writerow(data)

    for course in courses:
      courseData = (
        courses[course]["CrsNo"],
        courses[course]["Description"],
        courses[course]["Grade"],
        courses[course]["Requests"],
        courses[course]["Sem1"],
        courses[course]["Sem2"],
        (courses[course]["Sem1"] + courses[course]["Sem2"])
      )
      writer.writerow(courseData)
