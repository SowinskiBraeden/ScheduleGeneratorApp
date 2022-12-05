#!/usr/bin/env python3.11
import json
import csv
from app.util.estimateGrade import estimateStudentGrade
from app.util.globals import flex
from app.util.courses import Request
from dataclasses import dataclass, asdict

@dataclass
class Student:
  PupilNum:        str
  Requests:        list[Request]
  Schedule:        dict[str: list]
  ExpectedClasses: int
  Classes:         int
  RemainingAlts:   list[Request]
  StudentIndex:    int
  Gradelevel:      int = None # set to None since we don't pass gradelevel

  # This function converst Student.Requests to an array of dictionaries from an array of Requests
  def RequestsToDict(self) -> None: self.Requests = [asdict(r) for r in self.Requests]
  
def studentsToDict(students: list[Student]) -> list[dict]:
  [s.RequestsToDict for s in students]
  return [asdict(s) for s in students]

# sort data into usable dictionary
def getStudents(
  data_dir:    str,
  log:         bool = False,
  totalBlocks: int  = 10,
  log_dir:     str  = './output/raw/students.json'
) -> list[ dict[ str: any ] ]:
  
  students: list[Student] = []

  with open(data_dir, newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
      exists = False
      for student in students:
        exists = True if student.PupilNum == row["Pupil #"] else False
        if exists: break
      alternate = True if str(row["Alternate?"]).upper() == 'TRUE' else False
      if exists:
        if len(students[student.StudentIndex].Requests) >= totalBlocks and not alternate and row["CrsNo"] not in flex: alternate = True
        students[student.StudentIndex].Requests.append(
          Request(
            row["CrsNo"],
            row["Description"],
            alternate
          ))
        if row["CrsNo"] not in flex and not alternate and students[student.StudentIndex].ExpectedClasses < 10:
          students[student.StudentIndex].ExpectedClasses += 1
      else:
        newStudent: Student = Student(
          row["Pupil #"],
          [Request(
            row["CrsNo"],
            row["Description"],
            alternate
          )],
          {}, 1, 0, [],
          len(students)
        )
        newStudent.Gradelevel = row.get("Grade") if row.get("Grade") is not None else row.get("grade")
        for i in range(1, totalBlocks+1): newStudent.Schedule[f'block{i}'] = []
        students.append(newStudent)

  # Estimate student grades
  for student in students:
    if student.Gradelevel is None: student.Gradelevel = estimateStudentGrade(student)

  if log:
    with open(log_dir, "w") as outfile:
      json.dump(studentsToDict(students), outfile, indent=2)

  return students

# Writes all students data to csv file
def writeStudentsToCSV(
  students:   list[Student], 
  output_dir: str = './output/raw/csv/students.csv'
) -> None:
  with open(output_dir, 'w') as file:
    writer = csv.writer(file)
    # Write header
    data = ("Pupil #", "# of Classes", "Grade")
    writer.writerow(data)

    for student in students:
      studentData = (student.PupilNum, student.Classes, student.Gradelevel)
      writer.writerow(studentData)
