
# |||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
# ||||||||||||||||||||||||||||||||||||||||||||||||||||||||||| SCHEDULER:  Model |||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
# |||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||


# |||||||||| IMPORT LIBRARIES |||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
import pandas as pd
import json
import psycopg2
import numpy as np
import math
import sys
import builtins


# |||||||||| IMPORT FUNCTIONS ||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
import solution as sol
from model_body_appver import (
    load_data,
    create_model,
    solve_warm_start,
    solve_model,
)

from load_input import load_input_data

# Database connection
def connect_to_db():
    return psycopg2.connect(
        dbname="scheduling_app",
        user="postgres",
        password="221214",
        host="localhost",
        port="5432"
    )

conn = connect_to_db()
cursor = conn.cursor()

DEBUG_FILE = r"c:\Users\joanm\Documents\SCHEDULER DATA\debug_file.txt"

def print(*args, **kwargs):
    """Wrapper around built-in print that also logs to file."""
    # Always print to console
    builtins.print(*args, **kwargs)

    # Prepare same formatting as normal print
    sep = kwargs.get("sep", " ")
    end = kwargs.get("end", "\n")

    # Join args into a string (like print does)
    output = sep.join(str(a) for a in args) + end

    # Append to debug file
    with open(DEBUG_FILE, "a", encoding="utf-8") as f:
        f.write(output)

def main():
    user_id = None
    if len(sys.argv) > 1:
        user_id = sys.argv[1]
    print(f"Received user_id: {user_id}")

    return user_id
    

# |||||||||| LOAD, CREATE AND SOLVE ||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
# Get user ID
user_id = main()
#user_id = '1' ####################### REMOVE

# Load input data to the database
#load_input_data(user_id)  # NOW DONE ON ENDPOINT

# Load and preprocess input data from the database
student_availability, antiquity, priorities, siblings_df, teacher_availability, teacher_info, courses, instruments, rooms, course_continuity = load_data(user_id)

# Show all columns
pd.set_option('display.max_columns', None)

print(priorities)
print(course_continuity)

# Create model
model, gx, gx2, gy, gy2, gz, gz2, num_students, num_teachers, num_rooms, num_courses, num_instruments, num_slots, day_penalties, deviation_penalties, sibling_day_penalties, warm_start_model, gx_w, gx2_w, gy_w, gy2_w, gz_w, gz2_w = create_model(student_availability, antiquity, priorities, siblings_df, teacher_availability, teacher_info, courses, instruments, rooms, course_continuity)

warm_start_solution = {}
# Generate warm start (DEACTIVATED)
#warm_start_solution = solve_warm_start(warm_start_model, gx_w, gx2_w, gy_w, gy2_w, gz_w, gz2_w, student_availability, courses, instruments, num_students, num_teachers, num_rooms, num_slots, num_courses, num_instruments)

# Solve model
solution, penalties = solve_model(model, gx, gx2, gy, gy2, gz, gz2, num_students, num_teachers, num_rooms, num_courses, num_instruments, num_slots, day_penalties, deviation_penalties, sibling_day_penalties, warm_start_solution, student_availability)
print(f'raw solution: {solution}')

# |||||||||| FORMAT AND STORE SOLUTION |||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
# SOLUTION ANALYSIS (solution.py)
#solution, penalties = sol.load_data()
class_groups = sol.structure_data(solution, penalties, courses, instruments, teacher_info)
print(f'raw class groups: {class_groups}')

# Display students that are missing assignments
missing_course_students, missing_instrument_students = sol.find_missing_students_with_requests(solution, num_students, priorities, courses, instruments)

# Remove unavoidable sibling penalties for better insights
s_groups = sol.create_sibling_groups(siblings_df)
min_days = sol.get_student_schedule(courses, instruments, student_availability, priorities, num_students, num_courses, num_instruments)
missmatch_days = sol.compare_sibling_schedules(s_groups, min_days, num_students)
class_groups = sol.update_sibling_penalties(class_groups, missmatch_days)

# Extract penalties first, before modifying "STUDENT"
class_groups["INSTRUMENT PENALTY"] = class_groups["STUDENT"].apply(lambda x: list(x[0].values())[0]["instrument_prioritization"])
class_groups["ANTIQUITY DAY PENALTY"] = class_groups["STUDENT"].apply(lambda x: list(x[0].values())[0]["antiquity_day"])
class_groups["ANTIQUITY DEVIATION PENALTY"] = class_groups["STUDENT"].apply(lambda x: list(x[0].values())[0]["antiquity_deviation"])
class_groups["SIBLING MISMATCH PENALTY"] = class_groups["STUDENT"].apply(lambda x: list(x[0].values())[0]["sibling_mismatch"])

class_groups = class_groups.explode("STUDENT").reset_index(drop=True)
class_groups["STUDENT"] = class_groups["STUDENT"].apply(lambda d: list(d.keys())[0])
print(f'formatted class groups: {class_groups}')

antiquity_penalty_dict, sibling_penalty_dict = sol.extract_penalties(class_groups)

insights = {
    "Workload Balance Index": sol.workload_balance_index(class_groups),
    "Daily Workload Deviation": sol.daily_workload_deviation(class_groups),
    "Underutilized Teachers": sol.underutilized_teachers(class_groups),
    "Overloaded Teachers": sol.overloaded_teachers(class_groups),
    "Student Distribution Score": sol.student_distribution_score(class_groups),
    "Room Utilization Rate": sol.room_utilization_rate(class_groups),
    "Peak Hour Congestion": sol.peak_hour_congestion(class_groups),
    "Room Underuse": sol.room_underuse(class_groups),
    "Missing Course Students": missing_course_students,
    "Missing Instrument Students": missing_instrument_students,
    "Antiquiy Penalties": antiquity_penalty_dict,
    "Sibling Penalties": sibling_penalty_dict,
}

# print in CMD to debug (remove afterwards)
# ///
pd.set_option('display.max_rows', None)  # Show all rows
pd.set_option('display.max_columns', None)  # Show all columns
pd.set_option('display.max_colwidth', None)  # Show full column content
print(class_groups)
# ///

class_groups.to_csv("debug_model_solution.csv", index=False)
conn = connect_to_db()
cursor = conn.cursor()

cursor.execute("""
    DELETE FROM solution_assignments
    WHERE user_id = %s AND solution_id = %s
""", (user_id, 'temp_sol'))

for _, row in class_groups.iterrows():
    cursor.execute("""
        INSERT INTO solution_assignments (
            user_id, solution_id,
            class_name, start_time, end_time, room_id, max_capacity, current_capacity,
            teacher_id, contract_type, load, student_id,
            instrument_penalty, antiquity_day_penalty,
            antiquity_deviation_penalty, sibling_mismatch_penalty
        ) VALUES (
            %s, %s,
            %s, %s, %s, %s, %s, %s,
            %s, %s, %s, %s,
            %s, %s,
            %s, %s
        )
    """, (
        user_id, 'temp_sol',
        row["CLASS"], row["START TIME"], row["END TIME"], row["ROOM"], row["MAX CAPACITY"], row["CURRENT CAPACITY"],
        row["TEACHER"], row["CONTRACT"], row["LOAD"], row["STUDENT"],
        row["INSTRUMENT PENALTY"], row["ANTIQUITY DAY PENALTY"],
        row["ANTIQUITY DEVIATION PENALTY"], row["SIBLING MISMATCH PENALTY"]
    ))

conn.commit()
cursor.close()
conn.close()

# Prepare insights for CSV
insights_data = {
    "Workload Balance Index": [insights["Workload Balance Index"]],
    "Daily Workload Deviation": [json.dumps(insights["Daily Workload Deviation"].to_dict())],  # Ensure valid JSON
    "Underutilized Teachers": [json.dumps(insights["Underutilized Teachers"].to_dict())],
    "Overloaded Teachers": [json.dumps(insights["Overloaded Teachers"].to_dict())],
    "Student Distribution Score": [insights["Student Distribution Score"]],
    "Room Utilization Rate": [insights["Room Utilization Rate"]],
    "Peak Hour Congestion": [json.dumps(insights["Peak Hour Congestion"].to_dict())],
    "Room Underuse": [json.dumps(insights["Room Underuse"].to_dict())],
    "Missing Course Students": [json.dumps(insights["Missing Course Students"])],
    "Missing Instrument Students": [json.dumps(insights["Missing Instrument Students"])],
    "Antiquiy Penalties": [json.dumps(insights["Antiquiy Penalties"])],
    "Sibling Penalties": [json.dumps(insights["Sibling Penalties"])],
}

# Convert to DataFrame
insights_df = pd.DataFrame(insights_data)

print(insights_df)

# Save to CSV
#insights_df.to_csv("model_insights.csv", index=False, quotechar='"')

def safe_float(val):
    if pd.isna(val) or val == "NaN":
        return None
    if isinstance(val, (float, int)):
        return float(val)
    if isinstance(val, np.generic):  # np.float64, np.int64, etc.
        return float(val.item())
    try:
        return float(val)
    except Exception as e:
        print(f"⚠️ safe_float failed on: {val} ({type(val)}): {e}")
        return None

def clean_for_json(obj):
    if isinstance(obj, dict):
        return {k: clean_for_json(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [clean_for_json(i) for i in obj]
    elif isinstance(obj, (np.generic, np.float64, np.int64)):
        return obj.item()
    elif pd.isna(obj):
        return None
    else:
        return obj

row = insights_df.iloc[0]

values = (
    float(safe_float(row["Workload Balance Index"])) if safe_float(row["Workload Balance Index"]) is not None else None,
    json.dumps(clean_for_json(row["Daily Workload Deviation"])),
    json.dumps(clean_for_json(row["Underutilized Teachers"])),
    json.dumps(clean_for_json(row["Overloaded Teachers"])),
    float(safe_float(row["Student Distribution Score"])) if safe_float(row["Student Distribution Score"]) is not None else None,
    float(safe_float(row["Room Utilization Rate"])) if safe_float(row["Room Utilization Rate"]) is not None else None,
    json.dumps(clean_for_json(row["Peak Hour Congestion"])),
    json.dumps(clean_for_json(row["Room Underuse"])),
    json.dumps(clean_for_json(row["Missing Course Students"])),
    json.dumps(clean_for_json(row["Missing Instrument Students"]))
)

# 🔍 Debug: check types and values
for i, v in enumerate(values):
    print(f"Value {i}: {v} (type: {type(v)})")

conn = connect_to_db()
cursor = conn.cursor()

cursor.execute("""
    DELETE FROM solution_insights
    WHERE user_id = %s AND solution_id = %s
""", (user_id, 'temp_sol'))

cursor.execute("""
    INSERT INTO solution_insights (
        user_id, solution_id,
        workload_balance_index, daily_workload_deviation, underutilized_teachers,
        overloaded_teachers, student_distribution_score, room_utilization_rate,
        peak_hour_congestion, room_underuse, missing_course_students, missing_instrument_students
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
""", (user_id, 'temp_sol') + values)

conn.commit()
cursor.close()
conn.close()

# print in CMD to debug (remove afterwards)
# ///
for key, value in insights.items():
    print(f"{key}:\n{value}\n")
# ///

student_count = sol.count_students_per_timeslot(class_groups)
student_count_df = pd.DataFrame(list(student_count.items()), columns=["Time Slot", "Students"])
#student_count_df.to_csv("student_count.csv", index=False, quotechar='"')

conn = connect_to_db()
cursor = conn.cursor()

cursor.execute("""
    DELETE FROM student_count
    WHERE user_id = %s AND solution_id = %s
""", (user_id, 'temp_sol'))

for _, row in student_count_df.iterrows():
    time_slot = int(row["Time Slot"]) if pd.notna(row["Time Slot"]) else None
    students = int(row["Students"]) if pd.notna(row["Students"]) else None

    cursor.execute("""
        INSERT INTO student_count (time_slot, students, user_id, solution_id)
        VALUES (%s, %s, %s, %s)
    """, (time_slot, students, user_id, 'temp_sol'))

conn.commit()
cursor.close()
conn.close()