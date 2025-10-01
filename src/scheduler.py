"""
Main scheduling logic for timetable generation
"""

import pandas as pd
from typing import Dict, List, Tuple, Set, Optional
import config
import utils
import random


class TimetableScheduler:
    def __init__(self, courses_df: pd.DataFrame, classrooms_df: pd.DataFrame, 
                 professors_df: pd.DataFrame):
        self.courses_df = courses_df
        self.classrooms_df = classrooms_df
        self.professors_df = professors_df
        
        # Initialize timetable structure for all batches
        self.batches = utils.get_batches_from_data(courses_df)
        self.timetables = self._initialize_timetables()
        
        # Track professor and classroom availability
        self.professor_schedule = {}  # {professor: {day: {slot: course}}}
        self.classroom_schedule = {}  # {room: {day: {slot: course}}}
        
        # Track assigned hours for professors per day
        self.professor_daily_hours = {}  # {professor: {day: hours}}
        
        self._initialize_schedules()
    
    def _initialize_timetables(self) -> Dict:
        """Initialize empty timetables for all batches"""
        timetables = {}
        for batch in self.batches:
            timetables[batch] = {
                day: {slot: None for slot in range(len(config.TIME_SLOTS))}
                for day in config.DAYS
            }
        return timetables
    
    def _initialize_schedules(self):
        """Initialize professor and classroom schedules"""
        # Initialize professor schedule
        for _, prof_row in self.professors_df.iterrows():
            prof = prof_row['Professor']
            self.professor_schedule[prof] = {
                day: {slot: None for slot in range(len(config.TIME_SLOTS))}
                for day in config.DAYS
            }
            self.professor_daily_hours[prof] = {day: 0 for day in config.DAYS}
        
        # Initialize classroom schedule
        for _, room_row in self.classrooms_df.iterrows():
            room = room_row['RoomCode']
            self.classroom_schedule[room] = {
                day: {slot: None for slot in range(len(config.TIME_SLOTS))}
                for day in config.DAYS
            }
    
    def generate_timetable(self) -> Dict:
        """Main function to generate complete timetable"""
        print("\n=== Starting Timetable Generation ===\n")
        
        # Process each course
        for idx, course_row in self.courses_df.iterrows():
            course_code = course_row['CourseCode']
            course_name = course_row['CourseName']
            print(f"Processing: {course_code} - {course_name}")
            
            try:
                self._schedule_course(course_row)
            except Exception as e:
                print(f"  ⚠ Warning: Could not fully schedule {course_code}: {e}")
        
        print("\n✓ Timetable generation complete\n")
        return self.timetables
    
    def _schedule_course(self, course_row):
        """Schedule a single course for all its batches"""
        course_code = course_row['CourseCode']
        course_name = course_row['CourseName']
        batches = utils.parse_batches(course_row['Batches'])
        ltpsc = utils.parse_ltpsc(course_row['LTPSC'])
        professor = course_row['Professor']
        room_type = course_row['RoomType']
        
        # Get batch-specific professor mapping if exists
        batch_prof_map = utils.parse_batch_prof_map(
            course_row.get('Batch_Prof_Map', {})
        )
        
        # Get student counts per batch
        students_per_batch = utils.parse_students_per_batch(
            course_row.get('Students_Per_Batch', ''),
            batches
        )
        
        L, T, P, S, C = ltpsc
        
        # Schedule lectures (L)
        if L > 0:
            for batch in batches:
                batch_prof = batch_prof_map.get(batch, professor)
                self._schedule_lectures(
                    course_code, course_name, batch, batch_prof, 
                    L, room_type, students_per_batch.get(batch, 60)
                )
        
        # Schedule tutorials (T)
        if T > 0:
            for batch in batches:
                batch_prof = batch_prof_map.get(batch, professor)
                self._schedule_tutorials(
                    course_code, course_name, batch, batch_prof, 
                    T, students_per_batch.get(batch, 60)
                )
        
        # Schedule practicals/labs (P)
        if P > 0:
            lab_type = course_row.get('LabType', 'General')
            for batch in batches:
                batch_prof = batch_prof_map.get(batch, professor)
                self._schedule_labs(
                    course_code, course_name, batch, batch_prof, 
                    P, lab_type, students_per_batch.get(batch, 60)
                )
    
    def _schedule_lectures(self, course_code: str, course_name: str, 
                          batch: str, professor: str, num_lectures: int,
                          room_type: str, students: int):
        """Schedule lecture sessions for a course"""
        scheduled = 0
        attempts = 0
        max_attempts = 100
        
        while scheduled < num_lectures and attempts < max_attempts:
            attempts += 1
            
            # Find available slot
            day = random.choice(config.DAYS)
            slot = random.choice([i for i in range(len(config.TIME_SLOTS)) 
                                 if i != config.LUNCH_BREAK_SLOT])
            
            # Find suitable classroom
            room = self._find_available_room(day, slot, room_type, students, 
                                            duration=config.LECTURE_DURATION)
            
            if room and self._can_schedule(batch, professor, day, slot, 
                                          duration=config.LECTURE_DURATION):
                # Schedule the lecture
                self._assign_slot(batch, professor, room, day, slot, 
                                 course_code, course_name, "Lecture", 
                                 duration=config.LECTURE_DURATION)
                scheduled += 1
                print(f"  ✓ Scheduled lecture for {batch} on {day} at {config.TIME_SLOTS[slot]}")
    
    def _schedule_tutorials(self, course_code: str, course_name: str,
                           batch: str, professor: str, num_tutorials: int,
                           students: int):
        """Schedule tutorial sessions"""
        scheduled = 0
        attempts = 0
        max_attempts = 100
        
        while scheduled < num_tutorials and attempts < max_attempts:
            attempts += 1
            
            day = random.choice(config.DAYS)
            slot = random.choice([i for i in range(len(config.TIME_SLOTS)) 
                                 if i != config.LUNCH_BREAK_SLOT])
            
            room = self._find_available_room(day, slot, "Tutorial", students,
                                            duration=config.LECTURE_DURATION)
            
            if room and self._can_schedule(batch, professor, day, slot,
                                          duration=config.LECTURE_DURATION):
                self._assign_slot(batch, professor, room, day, slot,
                                 course_code, course_name, "Tutorial",
                                 duration=config.LECTURE_DURATION)
                scheduled += 1
                print(f"  ✓ Scheduled tutorial for {batch} on {day} at {config.TIME_SLOTS[slot]}")
    
    def _schedule_labs(self, course_code: str, course_name: str,
                      batch: str, professor: str, num_lab_hours: int,
                      lab_type: str, students: int):
        """Schedule lab sessions (2-hour slots)"""
        num_sessions = num_lab_hours // 2  # Each lab session is 2 hours
        scheduled = 0
        attempts = 0
        max_attempts = 100
        
        while scheduled < num_sessions and attempts < max_attempts:
            attempts += 1
            
            day = random.choice(config.DAYS)
            # Prefer afternoon slots for labs
            slot = random.choice(config.PREFERRED_LAB_SLOTS)
            
            # Check if we have 2 consecutive slots available
            if slot + 1 >= len(config.TIME_SLOTS):
                continue
            
            room = self._find_available_room(day, slot, "Lab", students,
                                            duration=config.LAB_DURATION,
                                            lab_type=lab_type)
            
            if room and self._can_schedule(batch, professor, day, slot,
                                          duration=config.LAB_DURATION):
                self._assign_slot(batch, professor, room, day, slot,
                                 course_code, course_name, f"Lab ({lab_type})",
                                 duration=config.LAB_DURATION)
                scheduled += 1
                print(f"  ✓ Scheduled lab for {batch} on {day} at {config.TIME_SLOTS[slot]}-{config.TIME_SLOTS[slot+1]}")
    
    def _find_available_room(self, day: str, slot: int, room_type: str,
                            students: int, duration: int = 1,
                            lab_type: str = None) -> Optional[str]:
        """Find an available classroom that meets requirements"""
        suitable_rooms = self.classrooms_df[
            (self.classrooms_df['Type'] == room_type) &
            (self.classrooms_df['Capacity'] >= students)
        ]
        
        for _, room_row in suitable_rooms.iterrows():
            room = room_row['RoomCode']
            
            # Check if room is available for all required slots
            available = True
            for s in range(slot, min(slot + duration, len(config.TIME_SLOTS))):
                if self.classroom_schedule[room][day][s] is not None:
                    available = False
                    break
            
            if available:
                return room
        
        return None
    
    def _can_schedule(self, batch: str, professor: str, day: str, 
                     slot: int, duration: int = 1) -> bool:
        """Check if a slot is available for batch and professor"""
        # Check batch availability
        for s in range(slot, min(slot + duration, len(config.TIME_SLOTS))):
            if self.timetables[batch][day][s] is not None:
                return False
        
        # Check professor availability
        for s in range(slot, min(slot + duration, len(config.TIME_SLOTS))):
            if self.professor_schedule[professor][day][s] is not None:
                return False
        
        # Check professor daily hours limit
        prof_max_hours = self.professors_df[
            self.professors_df['Professor'] == professor
        ]['MaxHoursPerDay'].values[0]
        
        if self.professor_daily_hours[professor][day] + duration > prof_max_hours:
            return False
        
        return True
    
    def _assign_slot(self, batch: str, professor: str, room: str,
                    day: str, slot: int, course_code: str, course_name: str,
                    session_type: str, duration: int = 1):
        """Assign a course to a time slot"""
        entry = {
            'course_code': course_code,
            'course_name': course_name,
            'professor': professor,
            'room': room,
            'type': session_type,
            'duration': duration
        }
        
        # Assign to all required slots
        for s in range(slot, min(slot + duration, len(config.TIME_SLOTS))):
            self.timetables[batch][day][s] = entry.copy()
            self.professor_schedule[professor][day][s] = f"{course_code}_{batch}"
            self.classroom_schedule[room][day][s] = f"{course_code}_{batch}"
        
        # Update professor daily hours
        self.professor_daily_hours[professor][day] += duration
    
    def export_timetables(self):
        """Export timetables to Excel files"""
        utils.ensure_output_dir()
        
        print("\n=== Exporting Timetables ===\n")
        
        for batch in self.batches:
            filename = f"{config.OUTPUT_DIR}/timetable_{batch}.xlsx"
            self._export_batch_timetable(batch, filename)
            print(f"✓ Exported timetable for {batch}")
        
        # Also create a master file with all timetables
        self._export_master_timetable()
        print(f"✓ Exported master timetable\n")
    
    def _export_batch_timetable(self, batch: str, filename: str):
        """Export timetable for a single batch"""
        data = []
        
        for day in config.DAYS:
            for slot_idx in range(len(config.TIME_SLOTS)):
                entry = self.timetables[batch][day][slot_idx]
                
                if entry is None:
                    if slot_idx == config.LUNCH_BREAK_SLOT:
                        row = {
                            'Day': day,
                            'Time': config.TIME_SLOTS[slot_idx],
                            'Course Code': 'LUNCH',
                            'Course Name': 'Lunch Break',
                            'Professor': '-',
                            'Room': '-',
                            'Type': 'Break'
                        }
                    else:
                        row = {
                            'Day': day,
                            'Time': config.TIME_SLOTS[slot_idx],
                            'Course Code': '-',
                            'Course Name': 'Free',
                            'Professor': '-',
                            'Room': '-',
                            'Type': '-'
                        }
                else:
                    row = {
                        'Day': day,
                        'Time': config.TIME_SLOTS[slot_idx],
                        'Course Code': entry['course_code'],
                        'Course Name': entry['course_name'],
                        'Professor': entry['professor'],
                        'Room': entry['room'],
                        'Type': entry['type']
                    }
                
                data.append(row)
        
        df = pd.DataFrame(data)
        df.to_excel(filename, index=False, sheet_name=batch)
    
    def _export_master_timetable(self):
        """Export master timetable with all batches"""
        filename = f"{config.OUTPUT_DIR}/timetable_master.xlsx"
        
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            for batch in self.batches:
                data = []
                
                for day in config.DAYS:
                    for slot_idx in range(len(config.TIME_SLOTS)):
                        entry = self.timetables[batch][day][slot_idx]
                        
                        if entry is None:
                            if slot_idx == config.LUNCH_BREAK_SLOT:
                                row = {
                                    'Day': day,
                                    'Time': config.TIME_SLOTS[slot_idx],
                                    'Course Code': 'LUNCH',
                                    'Course Name': 'Lunch Break',
                                    'Professor': '-',
                                    'Room': '-',
                                    'Type': 'Break'
                                }
                            else:
                                row = {
                                    'Day': day,
                                    'Time': config.TIME_SLOTS[slot_idx],
                                    'Course Code': '-',
                                    'Course Name': 'Free',
                                    'Professor': '-',
                                    'Room': '-',
                                    'Type': '-'
                                }
                        else:
                            row = {
                                'Day': day,
                                'Time': config.TIME_SLOTS[slot_idx],
                                'Course Code': entry['course_code'],
                                'Course Name': entry['course_name'],
                                'Professor': entry['professor'],
                                'Room': entry['room'],
                                'Type': entry['type']
                            }
                        
                        data.append(row)
                
                df = pd.DataFrame(data)
                # Truncate sheet name to 31 characters (Excel limit)
                sheet_name = batch[:31]
                df.to_excel(writer, sheet_name=sheet_name, index=False)
