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
Automated-TimeTable-IIITD/

├── data/

│   ├── courses.xlsx

│   ├── classrooms.xlsx

│   └── professors.xlsx

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

---

## Requirements
- Python 3.10+  
- Packages:
  pandas
  numpy
  openpyxl

---

## Installation
1. Clone the repository:
```bash
git clone <repo_url>
cd Automated-TimeTable-IIITD
