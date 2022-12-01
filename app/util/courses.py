#!/usr/bin/env python3.11
import json
import csv
from dataclasses import dataclass, asdict
from app.util.estimateGrade import getGrade

@dataclass
class Request:
  CrsNo:       str
  Description: str
  Alt:         bool

@dataclass
class Course:
  CrsNo:       str
  Description: str
  Grade:       int
  Requests:    int = 0 # number of requests for this
  Sem1:        int = 0 # number of classes running in sem1
  Sem2:        int = 0 # number of classes running in sem2
  Total:       int = 0 # total number of classes running
  Seats:       int = 0 # total number of seats
  Occupied:    int = 0 # number of occupied seats

def coursesToDict(courses: dict[str: Course]) -> dict[str: dict]:
  return [asdict(courses[c]) for c in courses]

# Get all requested courses from data
def getCourses(
  data_dir: str,
  log:      int = False,
  log_dir:  str = './output/raw/courses.json',
) -> dict[str: Course]:

  courses: dict[str: Course] = {}

  with open(data_dir, newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
      exists = False
      for course in courses:
        exists = True if courses[course].CrsNo == row["CrsNo"] else False
        if exists: break
      if not exists:
        grade = getGrade(row["CrsNo"], row["Description"])
        courses[row["CrsNo"]] = Course(
          row["CrsNo"],
          row["Description"],
          grade
        )

  if log:
    with open(log_dir, "w") as outfile:
      json.dump(coursesToDict(courses), outfile, indent=2)
        
  return courses

# Writes all course data to csv file
def writeCoursesToCSV(
  courses:    dict[str: Course], 
  output_dir: str = './output/raw/csv/courses.csv'
) -> None:
  with open(output_dir, 'w') as file:
    writer = csv.writer(file)
    # Write header
    data = (
      "CrsNo",
      "Description",
      "Grade",
      "Requests",
      "First sem. # of Classes",
      "Second sem. # of Classes",
      "Total # of Classes",
      "Total # of Seats",
      "# of Seats Occupied"
    )
    writer.writerow(data)

    for course in courses:
      courseData = (
        courses[course].CrsNo,
        courses[course].Description,
        courses[course].Grade,
        courses[course].Requests,
        courses[course].Sem1,
        courses[course].Sem2,
        courses[course].Total,
        courses[course].Seats,
        courses[course].Occupied
      )
      writer.writerow(courseData)
