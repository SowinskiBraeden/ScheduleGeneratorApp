#!/usr/bin/env python 3.11
from docx.shared import Inches
from app.util.globals import flex
import docx

def putMasterTimetable(timetable: dict) -> None:
	pass

def putScheduleToWord(courses: dict, student: dict, output_dir: str='./output/final/student_schedules') -> None:

	# create an instance of a word doc.
	doc = docx.Document()

	doc.add_heading(f'Schedule for Student {student["Pupil #"]}')

	# Create a table object
	table = doc.add_table(rows=1, cols=3)
	table.autofit = True
	table.style = 'Colorful List'

	# course name + (code) | block | semester
	row = table.rows[0].cells
	row[0].text = 'Course'
	row[1].text = 'Block'
	row[2].text = 'Sem.'
 
	table.columns[0].width = Inches(3.5)
	table.columns[1].width = Inches(0.75)
	table.columns[2].width = Inches(0.75)

	for block in student['schedule']:
		courseCode = student["schedule"][block][0]
		if courseCode in flex: courseName = 'Study'
		else: courseName = courses[courseCode[:-2]]["Description"]
		blockNum = int(block.split('block')[1])
		semester = 2 if blockNum > 5 else 1
		if blockNum > (len(student["schedule"])/2): blockNum -= (len(student["schedule"])/2)
		row = table.add_row().cells
		row[0].text = f'{courseName}\n({courseCode})'
		row[1].text = str(blockNum)
		row[2].text = str(semester)

	for row in table.rows:
		row.height = Inches(0.75)

	doc.save(f'{output_dir}/{student["Pupil #"]}_schedule.docx')
