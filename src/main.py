"""
Main entry point for the Automated Timetable Scheduler
"""

import sys
import os
from datetime import datetime
import utils
from scheduler import TimetableScheduler


def print_banner():
    """Print welcome banner"""
    print("=" * 60)
    print(" " * 10 + "IIIT Dharwad - Automated Timetable Scheduler")
    print("=" * 60)
    print()


def main():
    """Main function to run the timetable generation"""
    try:
        print_banner()
        
        # Load data from Excel files
        print("📂 Loading data from Excel files...\n")
        courses_df = utils.load_courses()
        classrooms_df = utils.load_classrooms()
        professors_df = utils.load_professors()
        
        # Validate data
        utils.validate_data(courses_df, classrooms_df, professors_df)
        
        # Create scheduler instance
        print("🔧 Initializing scheduler...\n")
        scheduler = TimetableScheduler(courses_df, classrooms_df, professors_df)
        
        # Generate timetables
        timetables = scheduler.generate_timetable()
        
        # Export to Excel
        scheduler.export_timetables()
        
        # Print summary
        print("=" * 60)
        print("✅ TIMETABLE GENERATION COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print(f"\n📊 Summary:")
        print(f"  - Total Batches: {len(scheduler.batches)}")
        print(f"  - Total Courses: {len(courses_df)}")
        print(f"  - Total Classrooms: {len(classrooms_df)}")
        print(f"  - Total Professors: {len(professors_df)}")
        print(f"\n📁 Output files saved in: {utils.config.OUTPUT_DIR}/")
        print(f"  - Individual batch timetables: timetable_<batch>.xlsx")
        print(f"  - Master timetable: timetable_master.xlsx")
        print("\n" + "=" * 60)
        
        return 0
        
    except FileNotFoundError as e:
        print(f"\n❌ Error: {e}")
        print("\nPlease ensure the following files exist:")
        print(f"  - {utils.config.COURSES_FILE}")
        print(f"  - {utils.config.CLASSROOMS_FILE}")
        print(f"  - {utils.config.PROFESSORS_FILE}")
        return 1
    
    except ValueError as e:
        print(f"\n❌ Data Validation Error: {e}")
        print("\nPlease check your Excel files for correct format.")
        return 1
    
    except Exception as e:
        print(f"\n❌ Unexpected Error: {e}")
        print("\nPlease check the error message above and verify your data files.")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
