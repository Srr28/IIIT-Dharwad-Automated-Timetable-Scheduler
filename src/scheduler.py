import random
import pandas as pd
import config
from utils import check_professor_availability

class TimetableScheduler:
    def __init__(self, classrooms, courses, professors):
        self.classrooms = classrooms
        self.courses = courses
        self.professors = professors
        self.days = config.DAYS
        self.slots = config.SLOTS
        self.max_hours = config.MAX_HOURS_PER_DAY

    def generate(self):
        """
        Generate timetables for all batches/sections.
        Returns dict {batch: timetable DataFrame}
        """
        timetables = {}

        for _, course in self.courses.iterrows():
            for batch in course["Batches"].split(","):
                if batch not in timetables:
                    timetables[batch] = pd.DataFrame(
                        "", index=self.days, columns=self.slots
                    )

                timetable = timetables[batch]

                sessions = int(course["L"]) + int(course["T"]) + int(course["P"])
                professor = course["Professor"]

                for _ in range(sessions):
                    assigned = False
                    attempts = 0

                    while not assigned and attempts < 100:
                        day = random.choice(self.days)
                        slot = random.choice(self.slots)

                        # Empty slot + professor available + daily hours not exceeded
                        if (
                            timetable.loc[day, slot] == ""
                            and check_professor_availability(timetables, day, slot, professor)
                            and (timetable.loc[day] != "").sum() < self.max_hours
                        ):
                            timetable.loc[day, slot] = (
                                f"{course['Course_Code']} ({professor})"
                            )
                            assigned = True

                        attempts += 1

                timetables[batch] = timetable

        return timetables
