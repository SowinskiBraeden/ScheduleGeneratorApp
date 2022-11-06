#!/usr/bin/env python3.11
import eel
from app.generator import generateScheduleV3
from app.util.globals import Error
from app.util.getCourses import getCourses
from app.util.getStudents import getStudents

eel.init('template')

@eel.expose  
def start(
  input_file_dir: str,
  min_req: int,
  class_cap: int,
  block_class_limit: int,
  total_blocks: int,
) -> Error:
  
  # Ensure params are of correct type
  input_file_dir    = str(input_file_dir)
  min_req           = int(min_req)
  class_cap         = int(class_cap)
  block_class_limit = int(block_class_limit)
  total_blocks      = int(total_blocks)

  err = None

  # call pre-algorithm functions read raw data into a processable format
  students = getStudents(input_file_dir, log=True, totalBlocks=total_blocks)
  courses = getCourses(input_file_dir, log=True)

  # call algorithm to sort data
  master_timetable, err = generateScheduleV3(
    students,
    courses,
    minReq=min_req,
    classCap=class_cap,
    blockClassLimit=block_class_limit,
    totalBlocks=total_blocks,
    studentsDir='./output/raw/students.json',
    conflictsDir='./output/raw/conflicts.json'
  )

  # TODO: log master_timetable

  # TODO: call post-algorithm functions to present sorted data

  return err

eel.start('index.html', size=(800, 1000))
