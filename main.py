#!/usr/bin/env python3.11
import eel
import os
import json

from app.util.convertRawData import putScheduleToWord, putMasterTimetable
from app.generator import generateScheduleV3
from app.util.globals import Error
from app.util.courses import getCourses, writeCoursesToCSV
from app.util.students import getStudents, writeStudentsToCSV
from app.util.errorCalculator import writeErrorsToCSV
from app.util.validator import validateInputData

eel.init('template')

@eel.expose  
def start(
  raw_file_data:          str,
  min_req:                int,
  class_cap:              int,
  block_class_limit:      int,
  total_blocks:           int,
  save_student_schedules: bool
) -> Error.__dict__: # Return Error dataclass as dict

  raw_data_dir = './output/temp/course_selection_data.csv'
  raw_json_dir = './output/raw/json'

  # Ensure output paths exists
  eel.post_data('Ensuring Directories Exists...')

  if not os.path.exists('output'):                         os.makedirs('output')
  if not os.path.exists('output/temp'):                    os.makedirs('output/temp')
  if not os.path.exists('output/final'):                   os.makedirs('output/final')
  if not os.path.exists('output/raw'):                     os.makedirs('output/raw')
  if not os.path.exists('output/raw/json'):                os.makedirs('output/raw/json')
  if not os.path.exists('output/raw/csv'):                 os.makedirs('output/raw/csv')

  # Only ensure folder exists if we want to save student schedules to docx files
  if save_student_schedules and not os.path.exists('output/final/student_schedules'): os.makedirs('output/final/student_schedules')
  
  # save raw file data to local file
  eel.post_data('Saving raw data to local file...')
  with open(raw_data_dir, 'w') as raw_file:
    raw_file.write(raw_file_data)

  # Ensure params are of correct type
  min_req           = int(min_req)
  class_cap         = int(class_cap)
  block_class_limit = int(block_class_limit)
  total_blocks      = int(total_blocks)

  eel.post_data('Validating input file...')
  validateErr = validateInputData(raw_data_dir)
  if validateErr is not None: return validateErr.__dict__

  # call pre-algorithm functions read raw data into a processable format
  eel.post_data('Collecting student information...')
  students = getStudents(
    raw_data_dir,
    log         = True,
    totalBlocks = total_blocks,
    log_dir     = './output/raw/json/students.json'
  )
  eel.post_data('Collecting course information...')
  courses = getCourses(
    raw_data_dir,
    log     = True,
    log_dir = f'{raw_json_dir}/courses.json'
  )

  # call algorithm to sort data
  eel.post_data('Generating timetables...')
  master_timetable, err = generateScheduleV3(
    students,
    courses,
    minReq          = min_req,
    classCap        = class_cap,
    blockClassLimit = block_class_limit,
    totalBlocks     = total_blocks,
    studentsDir     = f'{raw_json_dir}/students.json',
    conflictsDir    = f'{raw_json_dir}/conflicts.json',
    coursesDir      = f'{raw_json_dir}/courses.json'
  )

  if err is not None:
    eel.post_data(f'An error has occured while generating the timetable: {err.Title}')
    return err.__dict__

  # Get updated students
  eel.post_data('Gathering latest data...')
  with open(f'{raw_json_dir}/students.json', 'r') as studentFile: students = json.load(studentFile)

  # call post-algorithm functions to present sorted data
  eel.post_data('Writing data to .csv files...')
  # get updated raw data
  with open(f'{raw_json_dir}/students.json', 'r') as sFile: students = json.load(sFile)
  with open(f'{raw_json_dir}/courses.json', 'r') as cFile: courses = json.load(cFile)
  writeStudentsToCSV(students, output_dir='./output/raw/csv/students.csv')
  writeCoursesToCSV(courses, output_dir='./output/raw/csv/courses.csv')
  writeErrorsToCSV(len(students), conflictsDir='./output/raw/json/conflicts.json', outputDir='./output/raw/csv/error_tracker.csv')

  eel.post_data('Writing master timetable to .xlsx file...')
  putMasterTimetable(master_timetable, './output/final')

  eel.post_data('Writing timetables to .docx files...')
  if save_student_schedules:
    for student in students:
      putScheduleToWord(courses, student, './output/final/student_schedules')

  return err.__dict__ if err is not None else None

def main():
  eel.start('index.html', size=(800, 1000))

if __name__ == '__main__':
  main()  
