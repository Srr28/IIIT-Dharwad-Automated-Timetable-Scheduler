"""
Configuration file for the Automated Timetable Scheduler
"""

# Time slots for the timetable (Monday to Friday)
TIME_SLOTS = [
    "08:00-09:00",
    "09:00-10:00",
    "10:00-11:00",
    "11:00-12:00",
    "12:00-13:00",
    "13:00-14:00",  # Lunch break
    "14:00-15:00",
    "15:00-16:00",
    "16:00-17:00",
    "17:00-18:00"
]

DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]

# Lunch break slot (index in TIME_SLOTS)
LUNCH_BREAK_SLOT = 5

# Lab session duration (number of consecutive slots)
LAB_DURATION = 2  # 2 hours for lab sessions
LECTURE_DURATION = 1  # 1 hour for lectures

# Maximum teaching hours per day for professors
MAX_PROF_HOURS_PER_DAY = 6

# Data file paths
DATA_DIR = "data"
OUTPUT_DIR = "data/output"
COURSES_FILE = f"{DATA_DIR}/courses.xlsx"
CLASSROOMS_FILE = f"{DATA_DIR}/classrooms.xlsx"
PROFESSORS_FILE = f"{DATA_DIR}/professors.xlsx"

# Constraints
MIN_GAP_BETWEEN_LABS = 1  # Minimum gap between two lab sessions for same batch
PREFERRED_LAB_SLOTS = [1, 2, 6, 7, 8]  # Preferred time slots for labs (avoid first and lunch)
