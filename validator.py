import os
import json
import pandas as pd

from auto_scheduler import generate_schedule


DATA_FOLDER = "data"
OUTPUT_FILE = "val.csv"


def load_json(path):

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    groups = data["groups"]
    rooms = data["rooms"]
    classes = data["classes"]

    return groups, rooms, classes

# проверки конфликтов

def check_teacher_conflicts(schedule):

    grouped = schedule.groupby(["Teacher", "Day", "Slot"])

    for _, group in grouped:
        if len(group) > 1:
            return False

    return True


def check_group_conflicts(schedule):

    grouped = schedule.groupby(["Group", "Day", "Slot"])

    for _, group in grouped:
        if len(group) > 1:
            return False

    return True


def check_room_conflicts(schedule):

    grouped = schedule.groupby(["Room", "Day", "Slot"])

    for _, group in grouped:
        if len(group) > 1:
            return False

    return True

# основная проверка

def validate_schedule(schedule):

    if not check_teacher_conflicts(schedule):
        return False, "teacher_conflict"

    if not check_group_conflicts(schedule):
        return False, "group_conflict"

    if not check_room_conflicts(schedule):
        return False, "room_conflict"

    return True, "ok"

# основной цикл

def run_validation():

    results = []

    for file in os.listdir(DATA_FOLDER):

        if not file.endswith(".json"):
            continue

        path = os.path.join(DATA_FOLDER, file)

        try:

            groups, rooms, classes = load_json(path)

            schedule = generate_schedule(groups, rooms, classes)

            valid, message = validate_schedule(schedule)

            results.append({
                "file": file,
                "valid": valid,
                "message": message
            })

        except Exception as e:

            results.append({
                "file": file,
                "valid": False,
                "message": str(e)
            })

    df = pd.DataFrame(results)

    df.to_csv(OUTPUT_FILE, index=False)


if __name__ == "__main__":
    run_validation()