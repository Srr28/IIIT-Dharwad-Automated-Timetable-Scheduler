# utils.py
"""Utility functions for data loading and validation"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
import config

class DataLoader:
    """Handles loading and validation of input data"""
    
    def __init__(self):
        self.courses_df = None
        self.classrooms_df = None
        self.professors_df = None
        
    def load_data(self) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """Load all Excel files and return dataframes"""
        try:
            self.courses_df = pd.read_excel(config.COURSES_FILE)
            self.classrooms_df = pd.read_excel(config.CLASSROOMS_FILE)
            self.professors_df = pd.read_excel(config.PROFESSORS_FILE)
            
            print("✓ Data loaded successfully")
            self._validate_data()
            return self.courses_df, self.classrooms_df, self.professors_df
            
        except FileNotFoundError as e:
            print(f"✗ Error: {e}")
            print("Please ensure all required Excel files are in the data/ directory")
            raise
            
    def _validate_data(self):
        """Validate loaded data for completeness and consistency"""
        # Check courses data
        required_course_cols = ['CourseCode', 'CourseName', 'Batches', 'LTPSC', 
                                'Professor', 'Semester', 'RoomType']
        self._check_columns(self.courses_df, required_course_cols, 'courses.xlsx')
        
        # Check classrooms data
        required_room_cols = ['RoomCode', 'Type', 'Capacity']
        self._check_columns(self.classrooms_df, required_room_cols, 'classrooms.xlsx')
        
        # Check professors data
        required_prof_cols = ['Professor', 'MaxHoursPerDay']
        self._check_columns(self.professors_df, required_prof_cols, 'professors.xlsx')
        
        print("✓ Data validation passed")
        
    def _check_columns(self, df: pd.DataFrame, required_cols: List[str], filename: str):
        """Check if dataframe has all required columns"""
        missing_cols = set(required_cols) - set(df.columns)
        if missing_cols:
            raise ValueError(f"Missing columns in {filename}: {missing_cols}")
            
    def parse_ltpsc(self, ltpsc_str: str) -> Dict[str, int]:
        """Parse LTPSC string into dictionary
        Example: "3-1-2-0-4" -> {'L': 3, 'T': 1, 'P': 2, 'S': 0, 'C': 4}
        """
        try:
            if isinstance(ltpsc_str, str):
                parts = [int(x.strip()) for x in ltpsc_str.replace('[','').replace(']','').split('-')]
            else:
                parts = ltpsc_str
                
            return {
                'L': parts[0],  # Lecture hours
                'T': parts[1],  # Tutorial hours
                'P': parts[2],  # Practical hours
                'S': parts[3],  # Self-study hours
                'C': parts[4]   # Credits
            }
        except Exception as e:
            print(f"Error parsing LTPSC '{ltpsc_str}': {e}")
            return {'L': 0, 'T': 0, 'P': 0, 'S': 0, 'C': 0}
            
    def parse_batches(self, batch_str: str) -> List[str]:
        """Parse batch string into list
        Example: "CSE_Y1_A,CSE_Y1_B" -> ['CSE_Y1_A', 'CSE_Y1_B']
        """
        if isinstance(batch_str, str):
            return [b.strip() for b in batch_str.split(',')]
        return []
        
    def get_courses_by_batch(self, batch_name: str) -> pd.DataFrame:
        """Get all courses for a specific batch"""
        courses = []
        for _, row in self.courses_df.iterrows():
            batches = self.parse_batches(row['Batches'])
            if batch_name in batches:
                courses.append(row)
        return pd.DataFrame(courses)


class TimetableExporter:
    """Handles exporting timetables to Excel"""
    
    @staticmethod
    def export_timetable(timetable: Dict, batch_name: str, output_path: str):
        """Export a single batch timetable to Excel"""
        # Create a DataFrame with days as rows and time slots as columns
        df = pd.DataFrame(index=config.DAYS, columns=config.TIME_SLOTS)
        
        for day in config.DAYS:
            for slot in config.TIME_SLOTS:
                key = (day, slot)
                if key in timetable:
                    entry = timetable[key]
                    df.loc[day, slot] = f"{entry['course_code']}\n{entry['course_name']}\n{entry['professor']}\n{entry['room']}"
                else:
                    df.loc[day, slot] = ""
        
        # Write to Excel
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name=batch_name)
            
        print(f"✓ Timetable exported for {batch_name}")
        
    @staticmethod
    def export_all_timetables(all_timetables: Dict[str, Dict], base_path: str):
        """Export all batch timetables to separate Excel files"""
        for batch_name, timetable in all_timetables.items():
            output_path = f"{base_path}{batch_name}_timetable.xlsx"
            TimetableExporter.export_timetable(timetable, batch_name, output_path)
            
    @staticmethod
    def export_master_timetable(all_timetables: Dict[str, Dict], output_path: str):
        """Export all timetables into a single Excel file with multiple sheets"""
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            for batch_name, timetable in all_timetables.items():
                df = pd.DataFrame(index=config.DAYS, columns=config.TIME_SLOTS)
                
                for day in config.DAYS:
                    for slot in config.TIME_SLOTS:
                        key = (day, slot)
                        if key in timetable:
                            entry = timetable[key]
                            df.loc[day, slot] = f"{entry['course_code']}\n{entry['professor']}\n{entry['room']}"
                        else:
                            df.loc[day, slot] = ""
                
                # Sanitize sheet name (Excel has 31 char limit)
                sheet_name = batch_name[:31]
                df.to_excel(writer, sheet_name=sheet_name)
                
        print(f"✓ Master timetable exported to {output_path}")


class ConflictChecker:
    """Utilities for checking scheduling conflicts"""
    
    @staticmethod
    def check_professor_conflict(professor: str, day: str, slot: str, 
                                 existing_schedule: Dict) -> bool:
        """Check if professor is already scheduled at this time"""
        for (d, s), entry in existing_schedule.items():
            if d == day and s == slot and entry['professor'] == professor:
                return True
        return False
        
    @staticmethod
    def check_room_conflict(room: str, day: str, slot: str, 
                           existing_schedule: Dict) -> bool:
        """Check if room is already booked at this time"""
        for (d, s), entry in existing_schedule.items():
            if d == day and s == slot and entry['room'] == room:
                return True
        return False
        
    @staticmethod
    def check_room_capacity(room_capacity: int, batch_size: int) -> bool:
        """Check if room can accommodate the batch"""
        return room_capacity >= batch_size
        
    @staticmethod
    def count_daily_lectures(batch_schedule: Dict, day: str) -> int:
        """Count number of lectures scheduled for a batch on a given day"""
        count = 0
        for (d, s), entry in batch_schedule.items():
            if d == day:
                count += 1
        return count
