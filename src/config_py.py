# config.py
"""Configuration settings for the timetable scheduler"""

# Time slots configuration
DAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
TIME_SLOTS = [
    '08:00-09:00',
    '09:00-10:00',
    '10:00-11:00',
    '11:00-12:00',
    '12:00-13:00',
    '13:00-14:00',  # Lunch break typically
    '14:00-15:00',
    '15:00-16:00',
    '16:00-17:00',
    '17:00-18:00'
]

# Lab session typically requires 2-3 consecutive slots
LAB_SLOT_DURATION = 3  # Number of consecutive time slots for a lab

# Branches and years
BRANCHES = ['CSE', 'ECE', 'DSAI']
YEARS = [1, 2, 3, 4]

# Semester configuration
FULL_SEMESTER = 'Full'
HALF_SEMESTER_1 = 'Half1'
HALF_SEMESTER_2 = 'Half2'

# File paths
DATA_DIR = 'data/'
OUTPUT_DIR = 'data/output/'
COURSES_FILE = DATA_DIR + 'courses.xlsx'
CLASSROOMS_FILE = DATA_DIR + 'classrooms.xlsx'
PROFESSORS_FILE = DATA_DIR + 'professors.xlsx'

# Scheduling constraints
MAX_LECTURES_PER_DAY = 5
MIN_BREAK_BETWEEN_LECTURES = 0  # Number of slots
LUNCH_BREAK_SLOT = 5  # Index of lunch break (12:00-13:00)

# Priority weights for optimization
PRIORITY_WEIGHTS = {
    'professor_load_balance': 0.3,
    'student_spread': 0.3,
    'room_utilization': 0.2,
    'preference_satisfaction': 0.2
}

# Batch configuration
def generate_batch_names():
    """Generate all batch names (e.g., CSE_Y1_A, CSE_Y1_B, etc.)"""
    batches = []
    for branch in BRANCHES:
        for year in YEARS:
            # Assuming 2 batches per year-branch combination (A and B)
            for section in ['A', 'B']:
                if year <= 2:  # More sections for lower years
                    batches.append(f"{branch}_Y{year}_{section}")
            # Add additional batches if needed
            if year == 1:  # Example: Year 1 might have more batches
                for section in ['C', 'D']:
                    batches.append(f"{branch}_Y{year}_{section}")
    return batches

ALL_BATCHES = generate_batch_names()

# Constraint violation penalties
PENALTIES = {
    'professor_clash': 1000,
    'room_clash': 1000,
    'student_clash': 1000,
    'room_capacity': 500,
    'max_hours_per_day': 300,
    'consecutive_lectures': 100
}
