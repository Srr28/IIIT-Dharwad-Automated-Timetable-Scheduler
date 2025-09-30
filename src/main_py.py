# main.py
"""Main script to run the timetable scheduler"""

import os
import sys
from datetime import datetime
import config
from utils import DataLoader, TimetableExporter
from scheduler import TimetableScheduler

def ensure_output_directory():
    """Create output directory if it doesn't exist"""
    if not os.path.exists(config.OUTPUT_DIR):
        os.makedirs(config.OUTPUT_DIR)
        print(f"✓ Created output directory: {config.OUTPUT_DIR}")

def print_banner():
    """Print welcome banner"""
    print("\n" + "="*70)
    print(" "*15 + "IIIT DHARWAD TIMETABLE SCHEDULER")
    print("="*70)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70 + "\n")

def print_summary(all_timetables):
    """Print summary statistics"""
    print("\n" + "="*70)
    print("SCHEDULING SUMMARY")
    print("="*70)
    
    total_sessions = 0
    for batch, timetable in all_timetables.items():
        sessions = len(timetable)
        total_sessions += sessions
        print(f"  {batch:20s}: {sessions:3d} sessions")
    
    print("-"*70)
    print(f"  Total Batches: {len(all_timetables)}")
    print(f"  Total Sessions Scheduled: {total_sessions}")
    print("="*70 + "\n")

def validate_input_files():
    """Check if all required input files exist"""
    required_files = [
        config.COURSES_FILE,
        config.CLASSROOMS_FILE,
        config.PROFESSORS_FILE
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print("✗ Error: Missing required input files:")
        for file in missing_files:
            print(f"  - {file}")
        print("\nPlease ensure all required Excel files are present in the data/ directory.")
        return False
    
    print("✓ All input files found")
    return True

def main():
    """Main execution function"""
    try:
        # Print banner
        print_banner()
        
        # Ensure output directory exists
        ensure_output_directory()
        
        # Validate input files
        if not validate_input_files():
            sys.exit(1)
        
        # Load data
        print("\n[1/4] Loading data...")
        data_loader = DataLoader()
        courses_df, classrooms_df, professors_df = data_loader.load_data()
        
        print(f"  • Courses: {len(courses_df)}")
        print(f"  • Classrooms: {len(classrooms_df)}")
        print(f"  • Professors: {len(professors_df)}")
        
        # Initialize scheduler
        print("\n[2/4] Initializing scheduler...")
        scheduler = TimetableScheduler(courses_df, classrooms_df, professors_df)
        print("  ✓ Scheduler initialized")
        
        # Generate timetables
        print("\n[3/4] Generating timetables...")
        all_timetables = scheduler.schedule_all_batches()
        
        # Export timetables
        print("\n[4/4] Exporting timetables...")
        
        # Export individual batch timetables
        TimetableExporter.export_all_timetables(
            all_timetables, 
            config.OUTPUT_DIR
        )
        
        # Export master timetable (all batches in one file)
        master_file = config.OUTPUT_DIR + f"master_timetable_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        TimetableExporter.export_master_timetable(all_timetables, master_file)
        
        # Print summary
        print_summary(all_timetables)
        
        print("="*70)
        print("✓ TIMETABLE GENERATION COMPLETED SUCCESSFULLY")
        print(f"Output files saved in: {config.OUTPUT_DIR}")
        print("="*70 + "\n")
        
    except KeyboardInterrupt:
        print("\n\n✗ Process interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Error occurred: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
