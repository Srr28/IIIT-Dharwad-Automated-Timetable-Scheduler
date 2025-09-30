import pandas as pd

def load_excel(path):
    """Load Excel file into pandas DataFrame."""
    try:
        df = pd.read_excel(path)
        return df
    except Exception as e:
        print(f"❌ Error loading {path}: {e}")
        return pd.DataFrame()

def save_timetables(timetables, output_file):
    """Save timetables dict into Excel file (each batch = one sheet)."""
    with pd.ExcelWriter(output_file, engine="openpyxl") as writer:
        for batch, timetable in timetables.items():
            timetable.to_excel(writer, sheet_name=batch)

def check_professor_availability(timetable, day, slot, professor):
    """Check if professor is already teaching in another batch at the same time."""
    for _, df in timetable.items():
        if df.loc[day, slot] != "" and professor in df.loc[day, slot]:
            return False
    return True
