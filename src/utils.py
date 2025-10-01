"""
Utility functions for data loading and validation
"""

import pandas as pd
import os
from typing import Dict, List, Tuple
import config
import ast


def load_courses() -> pd.DataFrame:
    """Load courses data from Excel file"""
    try:
        df = pd.read_excel(config.COURSES_FILE)
        required_columns = ['CourseCode', 'CourseName', 'Batches', 'LTPSC', 
                          'Professor', 'Semester', 'RoomType']
        
        for col in required_columns:
            if col not in df.columns:
                raise ValueError(f"Missing required column: {col}")
        
        print(f"✓ Loaded {len(df)} courses from {config.COURSES_FILE}")
        return df
    except FileNotFoundError:
        raise FileNotFoundError(f"Courses file not found at {config.COURSES_FILE}")


def load_classrooms() -> pd.DataFrame:
    """Load classrooms data from Excel file"""
    try:
        df = pd.read_excel(config.CLASSROOMS_FILE)
        required_columns = ['RoomCode', 'Type', 'Capacity']
        
        for col in required_columns:
            if col not in df.columns:
                raise ValueError(f"Missing required column: {col}")
        
        print(f"✓ Loaded {len(df)} classrooms from {config.CLASSROOMS_FILE}")
        return df
    except FileNotFoundError:
        raise FileNotFoundError(f"Classrooms file not found at {config.CLASSROOMS_FILE}")


def load_professors() -> pd.DataFrame:
    """Load professors data from Excel file"""
    try:
        df = pd.read_excel(config.PROFESSORS_FILE)
        required_columns = ['Professor', 'Courses']
        
        for col in required_columns:
            if col not in df.columns:
                raise ValueError(f"Missing required column: {col}")
        
        # Set default max hours per day if not provided
        if 'MaxHoursPerDay' not in df.columns:
            df['MaxHoursPerDay'] = config.MAX_PROF_HOURS_PER_DAY
        
        print(f"✓ Loaded {len(df)} professors from {config.PROFESSORS_FILE}")
        return df
    except FileNotFoundError:
        raise FileNotFoundError(f"Professors file not found at {config.PROFESSORS_FILE}")


def parse_ltpsc(ltpsc_str: str) -> Tuple[int, int, int, int, int]:
    """
    Parse LTPSC string to tuple of integers
    Input format: "[3, 0, 2, 0, 4]" or "3-0-2-0-4"
    Returns: (L, T, P, S, C)
    """
    try:
        if isinstance(ltpsc_str, str):
            # Remove brackets and spaces
            ltpsc_str = ltpsc_str.strip('[]() ')
            # Try comma-separated first
            if ',' in ltpsc_str:
                parts = [int(x.strip()) for x in ltpsc_str.split(',')]
            # Try dash-separated
            elif '-' in ltpsc_str:
                parts = [int(x.strip()) for x in ltpsc_str.split('-')]
            else:
                raise ValueError(f"Invalid LTPSC format: {ltpsc_str}")
            
            if len(parts) != 5:
                raise ValueError(f"LTPSC must have 5 values, got {len(parts)}")
            
            return tuple(parts)
        elif isinstance(ltpsc_str, (list, tuple)):
            if len(ltpsc_str) != 5:
                raise ValueError(f"LTPSC must have 5 values, got {len(ltpsc_str)}")
            return tuple(int(x) for x in ltpsc_str)
        else:
            raise ValueError(f"Invalid LTPSC type: {type(ltpsc_str)}")
    except Exception as e:
        raise ValueError(f"Error parsing LTPSC '{ltpsc_str}': {e}")


def parse_batches(batches_str) -> List[str]:
    """
    Parse batches string to list
    Input format: "['CSE_1A', 'CSE_1B']" or "CSE_1A,CSE_1B"
    """
    try:
        if isinstance(batches_str, str):
            # Try to evaluate as Python list
            try:
                batches = ast.literal_eval(batches_str)
                if isinstance(batches, list):
                    return [str(b).strip() for b in batches]
            except:
                pass
            
            # Try comma-separated
            if ',' in batches_str:
                return [b.strip() for b in batches_str.split(',')]
            else:
                return [batches_str.strip()]
        elif isinstance(batches_str, list):
            return [str(b).strip() for b in batches_str]
        else:
            return [str(batches_str).strip()]
    except Exception as e:
        raise ValueError(f"Error parsing batches '{batches_str}': {e}")


def parse_batch_prof_map(map_str) -> Dict[str, str]:
    """
    Parse batch-professor mapping
    Input format: "{'CSE_1A': 'Prof. A', 'CSE_1B': 'Prof. B'}"
    """
    if pd.isna(map_str) or map_str == '' or map_str is None:
        return {}
    
    try:
        if isinstance(map_str, str):
            return ast.literal_eval(map_str)
        elif isinstance(map_str, dict):
            return map_str
        else:
            return {}
    except:
        return {}


def parse_students_per_batch(students_str, batches: List[str]) -> Dict[str, int]:
    """
    Parse students per batch
    Input: "[60, 55]" or "60" or "{'CSE_1A': 60, 'CSE_1B': 55}"
    """
    if pd.isna(students_str) or students_str == '':
        return {batch: 60 for batch in batches}  # Default
    
    try:
        if isinstance(students_str, str):
            # Try dictionary format
            try:
                result = ast.literal_eval(students_str)
                if isinstance(result, dict):
                    return result
            except:
                pass
            
            # Try list format
            students_str = students_str.strip('[]() ')
            if ',' in students_str:
                counts = [int(x.strip()) for x in students_str.split(',')]
                return {batch: counts[i] if i < len(counts) else counts[0] 
                       for i, batch in enumerate(batches)}
            else:
                count = int(students_str)
                return {batch: count for batch in batches}
        elif isinstance(students_str, (int, float)):
            return {batch: int(students_str) for batch in batches}
        elif isinstance(students_str, list):
            return {batch: int(students_str[i]) if i < len(students_str) else int(students_str[0])
                   for i, batch in enumerate(batches)}
        elif isinstance(students_str, dict):
            return students_str
        else:
            return {batch: 60 for batch in batches}
    except Exception as e:
        print(f"Warning: Error parsing students '{students_str}': {e}. Using default.")
        return {batch: 60 for batch in batches}


def ensure_output_dir():
    """Create output directory if it doesn't exist"""
    os.makedirs(config.OUTPUT_DIR, exist_ok=True)


def get_batches_from_data(courses_df: pd.DataFrame) -> List[str]:
    """Extract all unique batches from courses data"""
    all_batches = set()
    for batches_str in courses_df['Batches']:
        batches = parse_batches(batches_str)
        all_batches.update(batches)
    return sorted(list(all_batches))


def validate_data(courses_df: pd.DataFrame, classrooms_df: pd.DataFrame, 
                 professors_df: pd.DataFrame) -> bool:
    """Validate loaded data"""
    print("\n=== Validating Data ===")
    
    # Validate courses
    print(f"Total courses: {len(courses_df)}")
    
    # Validate classrooms
    print(f"Total classrooms: {len(classrooms_df)}")
    print(f"  - Lecture rooms: {len(classrooms_df[classrooms_df['Type'] == 'Lecture'])}")
    print(f"  - Lab rooms: {len(classrooms_df[classrooms_df['Type'] == 'Lab'])}")
    
    # Validate professors
    print(f"Total professors: {len(professors_df)}")
    
    # Extract unique batches
    batches = get_batches_from_data(courses_df)
    print(f"Total batches: {len(batches)}")
    print(f"Batches: {', '.join(batches)}")
    
    print("✓ Data validation complete\n")
    return True
