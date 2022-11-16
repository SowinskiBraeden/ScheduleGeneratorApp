#!/usr/bin/env python3.11
from app.util.globals import flex

most_frequent = lambda l : max(set(l), key = l.count)

# extract a grade from a course code or description
def extractGrade(string: str) -> int:
  if string in flex: return 12

  grade = None
  for i in range(len(string)):
    # If this is a digit like 1 and the next character is a digit like 2 we know the grade is 12
    # or if this digit is 0 and the next digit is 9 we know the grade is 9
    if i != len(string) - 1 and string[i].isdigit() and string[i+1].isdigit():
      grade = int(f'{string[i]}{string[i+1]}')
      if grade >= 8: break

    # if the above condition is not met, and we know this is a single number, we can just return this single number as the grade
    elif string[i].isdigit():
      grade = int(string[i])
      if grade >= 8: break

  return grade if grade is not None and grade >= 8 else None

# Estimage students grade based off requests
def estimateStudentGrade(pupil: dict) -> int:
  grades = [] # List of all possible grades
  for request in (r for r in pupil["requests"] if r not in flex):
    extractedGrade = getGrade(request["CrsNo"], request["Description"])
    if extractedGrade is not None: grades.append(extractedGrade)

  return None if len(grades) == 0 else most_frequent(grades) # Final estimate of grade

# anlyse course code and description for best grade estimate
def getGrade(crsNo: str, crsDes: str) -> int:
  grade = extractGrade(crsDes)
  if grade is None: grade = extractGrade(crsNo)
  return grade
