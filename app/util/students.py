#!/usr/bin/env python3.11
import json
import csv
from app.util.estimateGrade import estimateStudentGrade
from app.util.globals import flex

# sort data into usable dictionary
def getStudents(
  data_dir:    str,
  log:         bool = False,
  totalBlocks: int  = 10,
  log_dir:     str  = './output/raw/students.json'
) -> list[ dict[ str: any ] ]:
  
  students: list[ dict[ str: any ] ] = []

  with open(data_dir, newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
      exists = False
      for student in students:
        exists = True if student["Pupil #"] == row["Pupil #"] else False
        if exists: break
      alternate = True if row["Alternate?"] == 'TRUE' else False
      if exists:
        if len(students[student["studentIndex"]]["requests"]) >= totalBlocks and not alternate and row["CrsNo"] not in flex: alternate = True
        students[student["studentIndex"]]["requests"].append({
          "CrsNo": row["CrsNo"],
          "Description": row["Description"],
          "alt": alternate
        })
        if row["CrsNo"] not in flex and not alternate and students[student["studentIndex"]]["expectedClasses"] < 10:
          students[student["studentIndex"]]["expectedClasses"] += 1
      else:
        newStudent = {
          "Pupil #": row["Pupil #"],
          "requests": [{
            "CrsNo": row["CrsNo"],
            "Description": row["Description"],
            "alt": alternate
          }],
          "schedule": {},
          "expectedClasses": 1,
          "classes": 0,
          "remainingAlts": [],
          "studentIndex": len(students)
        }
        for i in range(1, totalBlocks+1): newStudent["schedule"][f'block{i}'] = []
        students.append(newStudent)

  # Estimate student grades
  for student in students:
    student["gradelevel"] = estimateStudentGrade(student)

  if log:
    with open(log_dir, "w") as outfile:
      json.dump(students, outfile, indent=2)

  return students

# Writes all students data to csv file
def writeStudentsToCSV(students: dict, output_dir: str='./output/raw/csv/students.csv') -> None:
  with open(output_dir, 'w') as file:
    writer = csv.writer(file)
    # Write header
    data = ("Pupil #", "# of Classes", "Grade")
    writer.writerow(data)

    for student in students:
      studentData = (student["Pupil #"], student["classes"], student["gradelevel"])
      writer.writerow(studentData)
