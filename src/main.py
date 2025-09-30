import config
from scheduler import TimetableScheduler
from utils import load_excel, save_timetables

def main():
    # Load input data
    classrooms = load_excel(config.CLASSROOMS_FILE)
    courses = load_excel(config.COURSES_FILE)
    professors = load_excel(config.PROFESSORS_FILE)

    # Initialize scheduler
    scheduler = TimetableScheduler(classrooms, courses, professors)

    # Generate timetables
    timetables = scheduler.generate()

    # Save to Excel
    save_timetables(timetables, config.OUTPUT_FILE)

    print("✅ Timetable generated successfully! Check", config.OUTPUT_FILE)

if __name__ == "__main__":
    main()
