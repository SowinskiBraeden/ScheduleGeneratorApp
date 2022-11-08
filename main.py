#!/usr/bin/env python3.11
import eel
import os
import json
from app.generator import generateScheduleV3
from app.util.globals import Error
from app.util.getCourses import getCourses
from app.util.getStudents import getStudents
from app.util.convertRawData import putScheduleToWord, putMasterTimetable

eel.init('template')
  
@eel.expose  
def start(
  raw_file_data: str,
  min_req: int,
  class_cap: int,
  block_class_limit: int,
  total_blocks: int,
) -> dict:

  eel.post_data('Ensuring Directories Exists...')
  # Ensure output paths exists
  if not os.path.exists('output'): os.makedirs('output')
  if not os.path.exists('output/temp'): os.makedirs('output/temp')
  if not os.path.exists('output/final'): os.makedirs('output/final')
  if not os.path.exists('output/final/student_schedules'): os.makedirs('output/final/student_schedules')
  if not os.path.exists('output/raw'): os.makedirs('output/raw')

  raw_data_dir = './output/temp/course_selection_data.csv'

  eel.post_data('Saving raw data to local file...')
  # save raw file data to local file
  with open(raw_data_dir, 'w') as raw_file:
    raw_file.write(raw_file_data)

  # Ensure params are of correct type
  min_req           = int(min_req)
  class_cap         = int(class_cap)
  block_class_limit = int(block_class_limit)
  total_blocks      = int(total_blocks)

  eel.post_data('Collecting student information...')
  # call pre-algorithm functions read raw data into a processable format
  students = getStudents(
    raw_data_dir,
    log=True,
    totalBlocks=total_blocks,
    log_dir='./output/raw/students.json'
  )
  eel.post_data('Collecting course information...')
  courses = getCourses(
    raw_data_dir,
    log=True,
    log_dir='./output/raw/courses.json'
  )

  eel.post_data('Generating timetables...')
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


  if err is not None:
    eel.post_data(f'An error has occured while generating the timetable: {err.Title}')
    return err.__dict__

  eel.post_data('Gathering latest data...')()
  # Get updated students
  with open('./output/raw/students.json', 'r') as studentFile: students = json.load(studentFile)

  eel.post_data('Writing timetables to .docx files...')
  # call post-algorithm functions to present sorted data
  for student in students:
    putScheduleToWord(courses, student, './output/final/student_schedules')

  # TODO: log master_timetable

  return err.__dict__ if err is not None else None

eel.start('index.html', size=(800, 1000))
