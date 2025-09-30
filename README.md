# Automated Timetable Scheduling for IIIT Dharwad

## Project Overview
This project automates the generation of timetables for IIIT Dharwad students.  
It takes course, classroom, and professor data as input and produces conflict-free timetables for all batches while respecting constraints like room capacity, professor availability, lecture/lab hours (LTPSC), and elective courses.

---

## Features
- Generates timetables for **16 batches** across all years and branches.  
- Handles **lecture and lab sessions** with correct room assignments.  
- Supports **full-semester and half-semester courses**.  
- Ensures **no clashes** for professors or classrooms.  
- Reads data from Excel files (`courses.xlsx`, `classrooms.xlsx`, `professors.xlsx`).  
- Outputs generated timetables as Excel files.

---

## Folder Structure
```text
Automated-TimeTable-IIITD/
├── data/                 
│   ├── courses.xlsx
│   ├── classrooms.xlsx
│   ├── professors.xlsx
│   └── output/          # Generated timetable Excel files
├── src/                  
│   ├── main.py
│   ├── scheduler.py
│   ├── utils.py
│   └── config.py
├── docs/                 
│   ├── slides.pdf
│   └── design_notes.md
├── tests/                
│   ├── test_scheduler.py
│   └── test_utils.py
├── requirements.txt      
└── README.md
```
## Requirement
- Python 3.10+
- Packages
  - pandas
  - numpy
  - openpyxl
## Installation
- Clone the repository
  ```
  git clone <repo_url>
  cd Automated-TimeTable-IIITD
- Install dependencies
  ```
  pip install -r requirements.txt
## Usage
- Run the main script to generate timetables:
  ```
  python src/main.py

- The output Excel files with timetables will be saved in data/output/.
## Input Data Format
- Courses.xlsx
  - | CourseCode | CourseName | Batches | LTPSC | Professor | Semester | RoomType | LabType | Students_Per_Batch | Duration | Batch_Prof_Map |
- Classrooms.xlsx
  - | RoomCode | Type | Capacity | BatchAllowed |
- Professors.xlsx
  - | Professor | Courses | AssignedHours | MaxHoursPerDay |
##Sample YAML Configuration
```
courses:
  - code: CSE101
    name: Data Structures
    batches: [A, B]
    ltpsc: [3, 0, 0, 0, 2]  # L, T, P, S, C
    professor: Prof. Smith
    semester: 1
    room_type: Lecture
    students_per_batch: [60, 55]

classrooms:
  - room_code: C101
    type: Lecture
    capacity: 60
    batch_allowed: [A, B]

professors:
  - name: Prof. Smith
    courses: [CSE101, CSE102]
    max_hours_per_day: 4
```
## Future Work
- Add a web interface to select courses and download timetables.
- Generate PDF timetables for easier sharing.
- Dynamically assign elective courses based on student enrollment.
## Authors
- [Sama Ruthveek Reddy](https://github.com/Srr28)
- [RAVVA SWATI](https://github.com/RavvaSwati)
- [SIDDHANT KUMAR](https://github.com/siddhantkumar101)
- [YASHAS A S](https://github.com/Yashas-2005) 
