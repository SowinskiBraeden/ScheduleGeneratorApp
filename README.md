# ScheduleGeneratorApp
The Desktop Application for my schedule-generator algorithm, allowing users to easily interact with the algorithm and its variables to generate schedules as documents for students indivually as well as the master timetable.

If you would like to try the application out for yourself, an example course selection .csv file is in the `/example/` folder. This is the minimum data that needs to be provided for the algorithm to function.

After running the algorithm, all output can be found in `/output/`. There you can find raw json data used by the algorithm, as well as parsed csv files with valuable information in the `/output/raw/` folder. You can ignore the `/output/temp/` folder as it is a copy of the file contents that was provided to the algorithm to be read. Any and all final parsed output, such as student schedules as .docx files, master timetable as an excel file, and parsed conflict data can all be found in the `/output/final/` folder.

If you wish to compile this yourself seen in https://github.com/SowinskiBraeden/ScheduleGeneratorEXE You can do so using the following command.
```
python -m eel main.py template --windowed -F
```
