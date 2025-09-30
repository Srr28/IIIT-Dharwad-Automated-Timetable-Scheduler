# scheduler.py
"""Core timetable scheduling algorithms"""

import random
from typing import Dict, List, Tuple, Optional
import pandas as pd
import config
from utils import DataLoader, ConflictChecker

class TimeSlot:
    """Represents a time slot in the timetable"""
    def __init__(self, day: str, time: str):
        self.day = day
        self.time = time
        
    def __repr__(self):
        return f"{self.day} {self.time}"


class SchedulingSession:
    """Represents a scheduled session"""
    def __init__(self, course_code: str, course_name: str, professor: str, 
                 room: str, batch: str, session_type: str, duration: int = 1):
        self.course_code = course_code
        self.course_name = course_name
        self.professor = professor
        self.room = room
        self.batch = batch
        self.session_type = session_type  # 'Lecture', 'Tutorial', 'Lab'
        self.duration = duration  # Number of consecutive slots


class TimetableScheduler:
    """Main scheduler class implementing constraint-based scheduling"""
    
    def __init__(self, courses_df: pd.DataFrame, classrooms_df: pd.DataFrame, 
                 professors_df: pd.DataFrame):
        self.courses_df = courses_df
        self.classrooms_df = classrooms_df
        self.professors_df = professors_df
        self.data_loader = DataLoader()
        self.conflict_checker = ConflictChecker()
        
        # Global scheduling state
        self.professor_schedule = {}  # {professor: {(day, slot): course}}
        self.room_schedule = {}  # {room: {(day, slot): course}}
        self.batch_schedules = {}  # {batch: {(day, slot): session_info}}
        
    def schedule_all_batches(self) -> Dict[str, Dict]:
        """Main scheduling function - schedules all batches"""
        print("\n" + "="*60)
        print("STARTING TIMETABLE GENERATION")
        print("="*60 + "\n")
        
        all_timetables = {}
        batches = self._get_all_batches()
        
        for i, batch in enumerate(batches, 1):
            print(f"[{i}/{len(batches)}] Scheduling batch: {batch}")
            timetable = self._schedule_batch(batch)
            all_timetables[batch] = timetable
            
        print("\n" + "="*60)
        print(f"✓ COMPLETED: Generated timetables for {len(batches)} batches")
        print("="*60 + "\n")
        
        return all_timetables
        
    def _get_all_batches(self) -> List[str]:
        """Extract all unique batches from courses data"""
        batches = set()
        for _, row in self.courses_df.iterrows():
            batch_list = self.data_loader.parse_batches(row['Batches'])
            batches.update(batch_list)
        return sorted(list(batches))
        
    def _schedule_batch(self, batch_name: str) -> Dict:
        """Schedule all courses for a single batch"""
        batch_timetable = {}
        courses = self.data_loader.get_courses_by_batch(batch_name)
        
        if courses.empty:
            print(f"  ⚠ Warning: No courses found for {batch_name}")
            return batch_timetable
            
        # Sort courses by priority (labs first, then lectures)
        courses = self._prioritize_courses(courses)
        
        for _, course in courses.iterrows():
            self._schedule_course(batch_name, course, batch_timetable)
            
        print(f"  ✓ Scheduled {len(batch_timetable)} sessions for {batch_name}")
        return batch_timetable
        
    def _prioritize_courses(self, courses: pd.DataFrame) -> pd.DataFrame:
        """Sort courses by scheduling priority (labs first, high credit courses)"""
        courses = courses.copy()
        courses['priority'] = 0
        
        for idx, row in courses.iterrows():
            ltpsc = self.data_loader.parse_ltpsc(row['LTPSC'])
            priority = 0
            
            # Labs have highest priority (need consecutive slots)
            if ltpsc['P'] > 0:
                priority += 100
                
            # Higher credits get higher priority
            priority += ltpsc['C'] * 10
            
            courses.at[idx, 'priority'] = priority
            
        return courses.sort_values('priority', ascending=False)
        
    def _schedule_course(self, batch_name: str, course: pd.Series, 
                        batch_timetable: Dict):
        """Schedule all sessions for a single course"""
        ltpsc = self.data_loader.parse_ltpsc(course['LTPSC'])
        professor = course['Professor']
        course_code = course['CourseCode']
        course_name = course['CourseName']
        room_type = course.get('RoomType', 'Lecture')
        
        # Get batch size
        batch_size = self._get_batch_size(batch_name, course)
        
        # Schedule lectures
        for _ in range(ltpsc['L']):
            self._schedule_session(batch_name, course_code, course_name, 
                                  professor, 'Lecture', room_type, 
                                  batch_size, batch_timetable, duration=1)
            
        # Schedule tutorials
        for _ in range(ltpsc['T']):
            self._schedule_session(batch_name, course_code, course_name, 
                                  professor, 'Tutorial', room_type, 
                                  batch_size, batch_timetable, duration=1)
            
        # Schedule labs (need consecutive slots)
        for _ in range(ltpsc['P']):
            lab_type = course.get('LabType', 'Computer')
            self._schedule_session(batch_name, course_code, course_name, 
                                  professor, 'Lab', lab_type, 
                                  batch_size, batch_timetable, 
                                  duration=config.LAB_SLOT_DURATION)
            
    def _schedule_session(self, batch_name: str, course_code: str, 
                         course_name: str, professor: str, session_type: str,
                         room_type: str, batch_size: int, 
                         batch_timetable: Dict, duration: int = 1):
        """Schedule a single session (lecture/tutorial/lab)"""
        # Find suitable room
        suitable_rooms = self._get_suitable_rooms(room_type, batch_size)
        
        if not suitable_rooms:
            print(f"  ⚠ Warning: No suitable rooms for {course_code} ({session_type})")
            return
            
        # Try to find a free slot
        scheduled = False
        attempts = 0
        max_attempts = 100
        
        while not scheduled and attempts < max_attempts:
            attempts += 1
            
            # Random day and slot selection
            day = random.choice(config.DAYS)
            slot_idx = random.randint(0, len(config.TIME_SLOTS) - duration)
            
            # Skip lunch break
            if slot_idx == config.LUNCH_BREAK_SLOT:
                continue
                
            # Check if batch doesn't exceed max lectures per day
            if self.conflict_checker.count_daily_lectures(batch_timetable, day) >= config.MAX_LECTURES_PER_DAY:
                continue
                
            # Try to schedule in available room
            for room in suitable_rooms:
                if self._can_schedule(day, slot_idx, duration, professor, 
                                     room, batch_timetable):
                    # Schedule the session
                    for i in range(duration):
                        slot = config.TIME_SLOTS[slot_idx + i]
                        key = (day, slot)
                        
                        session_info = {
                            'course_code': course_code,
                            'course_name': course_name,
                            'professor': professor,
                            'room': room,
                            'type': session_type,
                            'batch': batch_name
                        }
                        
                        batch_timetable[key] = session_info
                        
                        # Update global schedules
                        if professor not in self.professor_schedule:
                            self.professor_schedule[professor] = {}
                        self.professor_schedule[professor][key] = course_code
                        
                        if room not in self.room_schedule:
                            self.room_schedule[room] = {}
                        self.room_schedule[room][key] = course_code
                        
                    scheduled = True
                    break
                    
            if scheduled:
                break
                
        if not scheduled:
            print(f"  ⚠ Could not schedule {course_code} ({session_type}) for {batch_name}")
            
    def _can_schedule(self, day: str, slot_idx: int, duration: int, 
                     professor: str, room: str, batch_timetable: Dict) -> bool:
        """Check if session can be scheduled without conflicts"""
        for i in range(duration):
            slot = config.TIME_SLOTS[slot_idx + i]
            key = (day, slot)
            
            # Check batch conflict
            if key in batch_timetable:
                return False
                
            # Check professor conflict
            if professor in self.professor_schedule:
                if key in self.professor_schedule[professor]:
                    return False
                    
            # Check room conflict
            if room in self.room_schedule:
                if key in self.room_schedule[room]:
                    return False
                    
        return True
        
    def _get_suitable_rooms(self, room_type: str, batch_size: int) -> List[str]:
        """Get list of rooms suitable for the session"""
        suitable = []
        for _, room in self.classrooms_df.iterrows():
            if room['Type'] == room_type and room['Capacity'] >= batch_size:
                suitable.append(room['RoomCode'])
        return suitable
        
    def _get_batch_size(self, batch_name: str, course: pd.Series) -> int:
        """Get the size of a batch for a course"""
        # Check if course has Students_Per_Batch data
        if 'Students_Per_Batch' in course and pd.notna(course['Students_Per_Batch']):
            try:
                sizes = eval(course['Students_Per_Batch'])
                batches = self.data_loader.parse_batches(course['Batches'])
                idx = batches.index(batch_name)
                return sizes[idx]
            except:
                pass
                
        # Default batch sizes based on year
        if '_Y1_' in batch_name:
            return 60
        elif '_Y2_' in batch_name:
            return 55
        elif '_Y3_' in batch_name:
            return 50
        else:
            return 45
