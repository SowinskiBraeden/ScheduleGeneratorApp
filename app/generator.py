#!/usr/bin/env python3
import json
import random
from string import hexdigits
from dataclasses import dataclass

from app.util.globals import flex, Error
from app.util.estimateGrade import getGrade
from app.util.students import Student, studentsToDict
from app.util.courses import Course, coursesToDict

@dataclass
class Conflict:
  PupilNum: str
  Email:    str
  Type:     str
  Code:     str
  Conflict: str
  Missing:  list = None

# Takes in information to create or add a new conflict
# Returns if the particular student has a previous error
def newConflict(
  pupilNum:     str, 
  email:        str, 
  conflictType: str, 
  code:         str, 
  description:  str,
  logs:         dict[str: list[Conflict]]
) -> bool:
  exists = True if pupilNum in logs else False
  log = Conflict(
    pupilNum,
    email,
    conflictType,
    code,
    description
  )
  if exists: logs[pupilNum].append(log)
  else: logs[pupilNum] = [log]
  return exists if conflictType == "Critical" else False

def insertConflictSolutions(
  pupilNum: str, 
  logs:     dict[str: list[Conflict]], 
  data:     list[dict[str: any]]
) -> None:
  for conflict in logs[pupilNum]:
    if conflict.Type == "Critical":
      conflict.Missing = data
      break

# V3 differs a lot by V1/2 as it does not focus on fitting the classes
# into the time table first.
# It starts by trying to get all classes full and give all students a full class list.
# Then it starts to attempt to fit all classes into a timetable, making corretions along
# the way. Corrections being moving a students class
def generateScheduleV3(
  students:        list[Student],     # Refer to /util/students.py to see the students list structure
  courses:         dict[str: Course], # Refer to /util/courses.py to see the courses dictionary structure
  minReq:          int = 18,          # minimum requests for a class to run
  classCap:        int = 30,          # maximum students per class
  blockClassLimit: int = 40,          # Block class limit is the number of classrooms available per block. Default 40 classes per block
  totalBlocks:     int = 10,          # total blocks between two semesters -> default is 10 for 5 per semester... or this can be 8 for 4 blocks per semester
  studentsDir:     str = "../output/raw/students.json",
  conflictsDir:    str = "../output/raw/conflicts.json",
  coursesDir:      str = "../output/raw/courses.json"
) -> tuple[dict, Error]: # Returns the completed 'running' dictionary

  # Return error that totalBlocks is invalid
  if totalBlocks not in (10, 8):
    totalBlockError = Error('Invalid totalBlocks', 'An invalid \'totalBlocks\' value was provided -> must be 10 or 8')
    return (None, totalBlockError) # return none and signal failure

  # First we need to setup some values
  median:      int             = (minReq + classCap) // 2
  blockPerSem: int             = int(totalBlocks / 2)
  running:     dict[str: dict] = {f'block{i}': {} for i in range(1, totalBlocks + 1)}

  def equal(l: list) -> list: # Used to equalize list of numbers
    q,r = divmod(sum(l),len(l))
    return [q+1]*r + [q]*(len(l)-r)


  # Step 1 - Calculate which classes can run
  activeCourses: dict[str: dict] = {}
  for student in students:
    # Tally class request
    for request in (request for request in student.Requests if not request.Alt and request.CrsNo not in flex):
      code = request.CrsNo
      courses[code].Requests += 1
      # Add course to active list if enough requests
      if courses[code].Requests > minReq and courses[code].CrsNo not in activeCourses:
        activeCourses[code] = courses[code]


  # Step 2 - Generate empty classes
  allClassRunCounts: list[int]       = []
  courseRunInfo:     dict[str: dict] = {} # Generated now, used in step 4
  emptyClasses:      dict[str: dict] = {} # List of all classes with how many students should be entered during step 3
  
  # calculate number of times to run class
  for i in range(len(activeCourses)):
    index: Course = list(activeCourses)[i]
    if index not in emptyClasses: emptyClasses[index] = {}
    classRunCount: int = activeCourses[index].Requests // median
    remaining:     int = activeCourses[index].Requests % median

    # Put number of classRunCount classes in emptyClasses
    for j in range(classRunCount):
      emptyClasses[index][f"{index}-{hexdigits[j]}"] = {
        "CrsNo": index,
        "Description": activeCourses[index].Description,
        "expectedLen": median # Number of students expected in this class / may be altered later
      }

    # If remaining fit in open slots in existing classes
    if remaining <= classRunCount * (classCap - median):
      # Equally disperse remaining into existing classes
      while remaining > 0:
        for j in range(classRunCount):
          if remaining == 0: break
          emptyClasses[index][f"{index}-{hexdigits[j]}"]["expectedLen"] += 1
          remaining -= 1
      if remaining > 0: print("step 2 logic error", remaining, "remaining")

    # If we can create a class using remaining, create class
    elif remaining >= minReq:
      # Create a class using remaining
      emptyClasses[index][f"{index}-{hexdigits[classRunCount]}"] = {
        "CrsNo": index,
        "Description": activeCourses[index].Description,
        "expectedLen": remaining
      }

      classRunCount += 1
      # If a class previously existed
      if classRunCount >= 2:
        # Equalize (level) class expectedLen's
        expectedLengths = [emptyClasses[index][f"{index}-{hexdigits[j]}"]["expectedLen"] for j in range(classRunCount)]
        newExpectedLens = equal(expectedLengths)
        for j in range(len(newExpectedLens)):
          emptyClasses[index][f"{index}-{hexdigits[j]}"]["expectedLen"] = newExpectedLens[j]

    # Else if we can't fit remaining into available slots in existing classes,
    # and it's unable to create its own class,
    # and the required amount (minReq - remaining) to make a class is less than
    # the number that existing classes can provide (classRunCount * (median - minReq))
    elif minReq - remaining < classRunCount * (median - minReq):
      # Take 1 from each class till min requirment met
      for j in range(classRunCount):
        emptyClasses[index][f"{index}-{hexdigits[j]}"]["expectedLen"] -= 1
        remaining += 1
        if remaining == minReq: break

      # Create a class using remaining + required amount from existing classes
      emptyClasses[index][f"{index}-{hexdigits[classRunCount]}"] = {
        "CrsNo": index,
        "Description": activeCourses[index].Description,
        "expectedLen": remaining
      }
      
      classRunCount += 1

      # Equalize (level) class expectedLen's
      expectedLengths = [emptyClasses[index][f"{index}-{hexdigits[j]}"]["expectedLen"] for j in range(classRunCount)]
      newExpectedLens = equal(expectedLengths)
      for j in range(len(newExpectedLens)):
        emptyClasses[index][f"{index}-{hexdigits[j]}"]["expectedLen"] = newExpectedLens[j]

    else:
      # In the case that the remaining requests are unable to be resolved
      # Fill as many requests into existing classes. Any left that can't fit,
      # Will need to be ignored so later we can fold them into their alternative
      # requests
      for j in range(classRunCount):
        if remaining == 0: break
        if emptyClasses[index][f"{index}-{hexdigits[j]}"]["expectedLen"] < classCap: 
          emptyClasses[index][f"{index}-{hexdigits[j]}"]["expectedLen"] += 1
          remaining -= 1

    courseRunInfo[index] = {
      "Total": classRunCount,
      "CrsNo": index
    }
    allClassRunCounts.append(classRunCount)

  
  # Step 3 - Fill 'emptyClasses' with Students
  selectedCourses: dict[str: dict] = {}
  tempStudents:    list[Student]   = list(students)

  while len(tempStudents) > 0:
    # Choose random student to prevent any success
    # bias to students at the top of the list
    student = tempStudents[random.randint(0, len(tempStudents)-1)]

    alternates = [request for request in student.Requests if request.Alt]
    for request in (request for request in student.Requests if not request.Alt and request.CrsNo not in flex):
      course = request.CrsNo
      getAvailableCourse = True
      isAlt = False
      while getAvailableCourse:
        if course in emptyClasses:
          # if course exists, get first available class
          for cname in emptyClasses[course]:
            if cname in selectedCourses:
              if isAlt and emptyClasses[course][cname]["expectedLen"] < classCap:
                emptyClasses[course][cname]["expectedLen"] += 1
              if len(selectedCourses[cname]["students"]) < emptyClasses[course][cname]["expectedLen"]:
                # Class exists with room for student
                selectedCourses[cname]["students"].append({
                  "Pupil #": student.PupilNum,
                  "index": student.StudentIndex
                })
                getAvailableCourse = False
                break
              elif len(selectedCourses[cname]["students"]) == emptyClasses[course][cname]["expectedLen"]:
                # If class is full, and there's no more classes available for that course
                if cname[len(cname)-1] == f"{len(emptyClasses[course])-1}":
                  if len(alternates) > 0:
                    # Use alternate
                    course = alternates[0].CrsNo
                    alternates.remove(alternates[0])
                    isAlt = True
                    break
                  else:
                    # Force break loop, ignore and let an admin
                    # handle options to solve for missing class
                    getAvailableCourse = False
                    break
            elif cname not in selectedCourses:
              selectedCourses[cname] = {
                "students": [{
                  "Pupil #": student.PupilNum,
                  "index": student.StudentIndex
                }],
                "CrsNo": course,
                "Description": courses[course].Description
              }
              getAvailableCourse = False
              break

        elif course not in emptyClasses:
          if len(alternates) > 0:
            # Use alternate
            course = alternates[0].CrsNo
            alternates.remove(alternates[0])
            isAlt = True
          else:
            # Force break loop, ignore and let an admin
            # handle options to solve for missing class
            getAvailableCourse = False

    students[student.StudentIndex].RemainingAlts = alternates
    tempStudents.remove(student)


  # Step 4 - Attempt to fit classes into timetable
  def stepIndex(offset: int, stepType: int) -> int:
    # ALl this logic handles taking the # of blocks per semester, 4 or 5 and calculating
    # the number used to step between the index of the first or second semester

    # stepType 0 is for stepping between first and second semester
    if stepType == 0: return blockPerSem if offset in (0, (-1 * (blockPerSem - 1))) else (-1 * (blockPerSem - 1))
    
    # stepType 1 is for stepping between second and first semester
    elif stepType == 1: return (-1 * blockPerSem) if offset in (0, (blockPerSem + 1)) else (blockPerSem + 1)

    # Return Error if code is altered to cause error
    else:
      invalidStepTypeError = Error('Invalid stepType', 'An invalid \'stepType\' was passed to func \'stepIndex\'')
      return (None, invalidStepTypeError)

  # Create copy for step 6
  courseRunInfoCopy: dict[str: dict] = dict(courseRunInfo)

  while len(allClassRunCounts) > 0:
    # Get highest resource class (most times run)
    index:  int = allClassRunCounts.index(max(allClassRunCounts))
    course: str = list(courseRunInfo)[index]

    # Tally first and second semester
    allSemBlockLens: list[int] = [len(running[f'block{i}']) for i in range(1, totalBlocks + 1)]
  
    # If there is more than one class Running
    if allClassRunCounts[index] > 1:
      blockIndex: int = allSemBlockLens.index(min(allSemBlockLens))
      stepType:   int = 0 if blockIndex < blockPerSem else 1
      offset:     int = 0

      # Spread classes throughout both semesters
      for i in range(courseRunInfo[course]["Total"]):
        cname = f"{course}-{hexdigits[i]}"
        classInserted = False
        while not classInserted:
          blockIndex += offset
          if len(running[f'block{blockIndex+1}']) < blockClassLimit:
            running[list(running)[blockIndex]][cname] = {
              "CrsNo": course,
              "Description": emptyClasses[course][cname]["Description"],
              "students": selectedCourses[cname]["students"]
            }
            allClassRunCounts[index] -= 1
            classInserted = True

          offset = stepIndex(offset, stepType)

          if blockIndex >= (totalBlocks - 1):
            blockIndex = 0 if stepType == 0 else blockPerSem
            offset = 0

    # If the class only runs once, place in semester with least classes
    elif allClassRunCounts[index] == 1:
      # Equally disperse into semesters classes

      # Get block with least classes
      leastBlock = allSemBlockLens.index(min(allSemBlockLens)) + 1
      cname = f"{course}-0"

      running[f"block{leastBlock}"][cname] = {
        "CrsNo": course,
        "Description": emptyClasses[course][cname]["Description"],
        "students": selectedCourses[cname]["students"],
      }

      allClassRunCounts[index] -= 1

    # Remove course when fully inserted
    if allClassRunCounts[index] == 0:
      allClassRunCounts.remove(allClassRunCounts[index])
      courseRunInfo.pop(list(courseRunInfo)[index])

  # Step 5 - Fill student schedule
  for block in running:
    for cname in running[block]:
      for student in running[block][cname]["students"]:
        students[student["index"]].Schedule[block].append(cname)
        students[student["index"]].Classes += 1


  # Step 6 - Evaluate, move students to fix conflicts
  conflictLogs: dict[str: list[Conflict]] = {}
  criticalCount, acceptableCount = 0, 0
  c_mc_count, c_cr_count, a_mc_count = 0, 0, 0
  studentsCritical, studentsAcceptable = 0, 0

  for student in students:
    blocks:       list[list] = [student.Schedule[block] for block in student.Schedule]
    hasConflicts: bool       = True if sum(1 for b in blocks if len(b)>1) > 0 else False
    
    # If there is no conflicts
    # and classes inserted to is equal to expectedClasses
    # or classes the student is inserted to is missing
    # no more than two classes:
    # continue to next student
    if not hasConflicts and student.Classes == student.ExpectedClasses: continue
    elif not hasConflicts and (student.ExpectedClasses-2) <= student.Classes < student.ExpectedClasses:
      # TODO: Insert alternates if available?
      a_mc_count += 1
      acceptableCount += 1
      if not newConflict(student.PupilNum, "", "Acceptable", "A-MC", "Missing 1-2 Classses", conflictLogs): studentsAcceptable += 1
      continue
    
    studentData: dict[str: any] = {
      "Pupil #": student.PupilNum,
      "index": student.StudentIndex
    }

    if hasConflicts:
      student.Classes = 0
      missing: list[str] = []

      # Clear student schedule to restructure
      for block in student.Schedule:
        [running[block][cname]["students"].remove(studentData) for cname in student.Schedule[block]]
        student.Schedule[block] = []

      # Find class in student schedule that's run the least
      classes, runCounts = [], []
      for block in blocks:
        for cname in block:
          classes.append(cname[:-2])
          runCounts.append(courseRunInfoCopy[cname[:-2]]["Total"])

      # Rebuild student schedule
      availableBlocks = [f'block{i}' for i in range(1, totalBlocks + 1)]
      while len(classes) > 0:
        index = runCounts.index(min(runCounts)) # Get class least run
        found = False

        # find slot for class
        for block in availableBlocks:
          if found: break
          for cname in running[block]:
            if cname[:-2] == classes[index] and len(running[block][cname]["students"]) < classCap:
              running[block][cname]["students"].append(studentData)
              student.Schedule[block].append(cname)
              availableBlocks.remove(block)
              student.Classes += 1
              found = True
              break

        if not found:
          # Determine all places class exists
          existsIn, existingClassNames = [], []
          for block in running:
            for cname in running[block]:
              if cname[:-2] == classes[index] and len(running[block][cname]["students"]) < classCap:
                existsIn.append(block)
                existingClassNames.append(cname)

          # Attempt to fix
          solution = False
          if len(existsIn) > 0:
            for i, existing in enumerate(existsIn):
              if solution: break
              classOut = student.Schedule[existing][0]
              for block in running:
                if solution: break
                if block == existing or block not in availableBlocks: continue
                for cname in running[block]:
                  if cname[:-2] == classOut[:-2] and len(running[block][cname]["students"]) < classCap:
                    student.Classes += 1

                    # Move to existing class elsewhere
                    student.Schedule[block].append(cname)
                    running[block][cname]["students"].append(studentData)

                    # Overwrite old class
                    running[existing][student.Schedule[existing][0]]["students"].remove(studentData)
                    student.Schedule[existing][0] = existingClassNames[i]
                    running[existing][existingClassNames[i]]["students"].append(studentData)

                    solution = True
                    break

          if not solution:
            # Try alternate
            alternates = [alt.CrsNo for alt in students[student.StudentIndex].RemainingAlts if alt.CrsNo not in flex and alt.CrsNo in courseRunInfoCopy]
            if len(alternates) == 0: # If no alternates, create critical error
              c_cr_count += 1
              criticalCount += 1

              missing.append({
                "block": f'block{index + 1}',
                "CrsNo": classes[index]
              })

              if not newConflict(
                student.PupilNum,
                "", # Student Email
                "Critical", # Err type
                "C-CR", # Err code
                "Couldn't Resolve", # Err msg
                conflictLogs): # logs dir
                  studentsCritical += 1

            else:
              # Get alternate least run
              altRunCounts = [courseRunInfoCopy[alt]["Total"] for alt in alternates]
              altIndex = altRunCounts.index(min(altRunCounts))

              # add alternate
              classes.append(alternates[altIndex])
              runCounts.append(altRunCounts[altIndex])

              # Remove alternate from remaining alternates
              for remaining in students[student.StudentIndex].RemainingAlts:
                if remaining.CrsNo == alternates[altIndex]:
                  students[student.StudentIndex].RemainingAlts.remove(remaining)

        # Remove class after inserted or failed to insert
        classes.remove(classes[index])
        runCounts.remove(runCounts[index])

      # Collect missing course data and 

      if len(missing) > 0:
        data = []

        if student.Gradelevel is None:
          for obj in missing:
            data.append({
              "CrsNo": obj["CrsNo"],
              "block": obj['block'],
              "solutions": None,
              "error": "Unable to find solutions, err no grade"
            })

        else:
          for obj in missing:
            blockSolution = { "CrsNo": obj["CrsNo"], "block": obj['block'], "solutions": [] }
            for cname in running[obj['block']]:
              courseInfo = running[obj['block']][cname]
              courseGrade = getGrade(courseInfo['CrsNo'], courseInfo['Description'])
              if courseGrade is None: continue
              if (student.Gradelevel == courseGrade) or (student.Gradelevel == 12 and courseGrade == 11):
                if len(running[obj['block']][cname]["students"]) < classCap:
                  blockSolution["solutions"].append({
                    "CrsNo": cname,
                    "Description": running[obj['block']][cname]["Description"]
                  })

            data.append(blockSolution)

        insertConflictSolutions(student.PupilNum, conflictLogs, data)

    metSelfRequirements = True if student.Classes == student.ExpectedClasses else False
    if not metSelfRequirements:
      
      if (student.ExpectedClasses - 2) <= student.Classes < student.ExpectedClasses:
        a_mc_count += 1
        acceptableCount += 1
        if not newConflict(student.PupilNum, "", "Acceptable", "A-MC", "Missing 1-2 Classses", conflictLogs): studentsAcceptable += 1

      elif student.Classes < (student.ExpectedClasses - 2):
        # Difference between classes inserted to and
        # expected classes is too great
        if student.PupilNum in conflictLogs:
          c_mc_count += 1
          criticalCount += 1
          if not newConflict(student.PupilNum, "", "Critical", "C-MC", "Missing too many Classses", conflictLogs): studentsCritical += 1

  finalConflictLogs: dict[str: any] = {
    "Conflicts": {s: [c.__dict__ for c in conflictLogs[s]] for s in conflictLogs},
    "Critical": {
      "Total": criticalCount,
      "Students": studentsCritical,
      "Errors": [{
        "Total": c_mc_count,
        "Description": "Missing too many Classes",
        "Code": "C-MC"
      }, {
        "Total": c_cr_count,
        "Description": "Couldn't Resolve",
        "Code": "C-CR"
      }]
    },
    "Acceptable": {
      "Total": acceptableCount,
      "Students": studentsAcceptable,
      "Errors": [{
        "Total": a_mc_count,
        "Description": "Missing 1-2 Classes",
        "Code": "A-MC"
      }]
    }
  }

  # Log Conflict to records
  with open(conflictsDir, "w") as outfile:
    json.dump(finalConflictLogs, outfile, indent=2)

  # Insert flex (spare) course codes to empty blocks
  for student in students:
    for block in student.Schedule:
      if len(student.Schedule[block]) == 0:
        i = 0 if int(block[5:]) <= blockPerSem else 1
        student.Schedule[block].append(flex[i])

  # Read timetable and collect data on courses
  for block in running:
    for course in running[block]:
      c = running[block][course]["CrsNo"]
      if int(block[5:]) <= blockPerSem: courses[c].Sem1 += 1
      else: courses[c].Sem2 += 1
      courses[c].Occupied += len(running[block][course]["students"])

  for course in courses:
    courses[course].Total = courses[course].Sem1 + courses[course].Sem2
    courses[course].Seats = courses[course].Total * classCap

  # Update/log new student records
  with open(studentsDir, "w") as outfile:
    json.dump(studentsToDict(students), outfile, indent=2)
  
  # Update/log new course records
  with open(coursesDir, "w") as outfile:
    json.dump(coursesToDict(courses), outfile, indent=2)

  # Save timetable to json
  with open('./output/raw/json/timetable.json', 'w') as outfile:
    json.dump(running, outfile, indent=2)

  return (running, None)
