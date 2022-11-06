#!/usr/bin/env python3.11
from app.util.globals import flex

most_frequent = lambda l : max(set(l), key = l.count)

def getGradeFromCourseCode(code: str) -> int:
  grades = [int(s) for s in code.split("-") if s.isdigit()]
  return None if len(grades) == 0 else most_frequent(grades)

def getEstimatedGrade(pupil: dict) -> int:
  grades = [] # List of all possible grades
  for request in (r for r in pupil["requests"] if r not in flex):
    for extractedGrade in [int(s) for s in request["CrsNo"].split("-") if s.isdigit()]:
      grades.append(extractedGrade)

  return None if len(grades) == 0 else most_frequent(grades) # Final estimate of grade
