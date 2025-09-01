
# |||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
# |||||||||||||||||||||||||||||||||||||||||||||||||||||||||| SCHEDULER: Solution ||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
# |||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||


# |||||||||| IMPORT LIBRARIES |||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
import pandas as pd
import os
import logging
import ast
import re


# |||||||||| LOAD SCHEDULER SOLUTION ||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
def load_data():
    ''' Load the Scheduler's solution and other required data. '''
    solution = pd.read_csv('schedule_solution.csv')
    penalties = pd.read_csv('schedule_penalties.csv')

    return solution, penalties


# |||||||||| PROCESS SOLUTION ||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
def safe_eval(val):
    ''' Safely evaluate a string containing a list representation. '''
    try:
        return ast.literal_eval(val)
    except (ValueError, SyntaxError):
        return [0]  # Default to [0] if parsing fails

def structure_data(solution, penalties, courses, instruments, teacher_info):
    ''' Group by ROOM, CLASS, START TIME, TEACHER, and aggregate student lists.
    Each student entry consists of a dictionary of penalties with the following structure: 
    {student: {"instrument_prioritization": count, "antiquity_day": count, "antiquity_deviation": count, "sibling_mismatch": count}}.
    The value of each penalty represents how many times it was applied to the student. 
    Also calculates END TIME based on session duration. Includes MAX CAPACITY, CURRENT CAPACITY, CONTRACT, and LOAD. '''

    # Define a mapping of penalty types to structured dictionary keys
    penalty_mapping = {
        "INSTRUMENT PRIORITIZATION": "instrument_prioritization",
        "ANTIQUITY DAY": "antiquity_day",
        "ANTIQUITY DEVIATION": "antiquity_deviation",
        "SIBLING MISMATCH": "sibling_mismatch"
    }

    # Create a dictionary to store penalties per student
    student_penalty_dict = {}

    for _, row in penalties.iterrows():
        student = row["STUDENT"]
        penalty_type = row["PENALTY TYPE"]

        if student not in student_penalty_dict:
            student_penalty_dict[student] = {
                "instrument_prioritization": 0,
                "antiquity_day": 0,
                "antiquity_deviation": 0,
                "sibling_mismatch": 0
            }

        student_penalty_dict[student][penalty_mapping[penalty_type]] += 1

    # Map class durations and capacities from courses and instruments (convert minutes to time slots)
    course_durations = {c: courses.iloc[c]["course_duration_minutes_per_session"] // 15 for c in range(len(courses))}
    instrument_durations = {i: instruments.iloc[i]["instrument_duration_minutes_per_session"] // 15 for i in range(len(instruments))}
    course_capacities = {c: courses.iloc[c]["course_capacity"] for c in range(len(courses))}
    instrument_capacities = {i: instruments.iloc[i]["instrument_capacity"] for i in range(len(instruments))}

    # Parse contract column for teacher max weekly hours
    teacher_info['contract']

    teacher_contracts = {t: teacher_info.iloc[t]['contract'][0] // 15 for t in range(len(teacher_info))}

    # Group schedule solution by ROOM, CLASS, START TIME, TEACHER
    class_groups = solution.groupby(["ROOM", "CLASS", "START TIME", "TEACHER"]).agg({"STUDENT": list}).reset_index()

    # Extract durations and capacities from the CLASS column correctly
    def get_class_info(class_name):
        match = re.match(r"(Course|Instrument) (\d+)", class_name)
        if not match:
            return 0, 0  # Default duration and capacity if class name is unrecognized
        class_type, index = match.groups()
        index = int(index)
        if class_type == "Course":
            return course_durations.get(index, 0), course_capacities.get(index, 0)
        else:
            return instrument_durations.get(index, 0), instrument_capacities.get(index, 0)

    # Calculate END TIME and MAX CAPACITY
    class_groups[["DURATION", "MAX CAPACITY"]] = class_groups["CLASS"].apply(lambda class_name: pd.Series(get_class_info(class_name)))
    class_groups["END TIME"] = class_groups["START TIME"] + class_groups["DURATION"] - 1  # the end time slot is also active

    # Compute CURRENT CAPACITY (number of students assigned)
    class_groups["CURRENT CAPACITY"] = class_groups["STUDENT"].apply(len)

    # Compute CONTRACT column (max weekly working hours per teacher in time slots)
    class_groups["CONTRACT"] = class_groups["TEACHER"].map(teacher_contracts)

    # Compute LOAD column (total time slots assigned per teacher)
    teacher_loads = class_groups.groupby("TEACHER")["DURATION"].sum().to_dict()
    class_groups["LOAD"] = class_groups["TEACHER"].map(teacher_loads)

    # Attach student penalty details
    class_groups["STUDENT"] = class_groups["STUDENT"].apply(
        lambda students: [
            {student: student_penalty_dict.get(student, {
                "instrument_prioritization": 0,
                "antiquity_day": 0,
                "antiquity_deviation": 0,
                "sibling_mismatch": 0
            })}
            for student in students
        ]
    )

    # Reorder columns to have CONTRACT and LOAD right after TEACHER
    class_groups = class_groups[[
        "CLASS", "START TIME", "END TIME", "ROOM", "MAX CAPACITY", "CURRENT CAPACITY", "TEACHER", "CONTRACT", "LOAD", "STUDENT"
    ]]

    return class_groups

def workload_balance_index(class_groups):
    ''' Standard deviation of workload balance between teachers; the lower the better. One single score. '''
    workload = class_groups.groupby("TEACHER")[["LOAD"]].sum()
    return (workload.std() / workload.mean()).iloc[0]

def daily_workload_deviation(class_groups):
    ''' Standard deviation of teacher workload; the lower the better. Each teacher has their own score. '''
    class_groups = class_groups.assign(DURATION=class_groups["END TIME"] - class_groups["START TIME"] + 1)
    daily_load = class_groups.groupby(["TEACHER", "START TIME"])["DURATION"].sum().unstack(fill_value=0)
    return daily_load.std(axis=1)

def underutilized_teachers(class_groups):
    ''' Identifies and sorts teachers by their workload utilization. '''
    teacher_utilization = class_groups.groupby("TEACHER")["LOAD"].first() / class_groups.groupby("TEACHER")["CONTRACT"].first()
    
    # Sort teachers from greatest to least utilization
    return teacher_utilization.sort_values(ascending=False)  # Sorting in descending order

def overloaded_teachers(class_groups):
    ''' Finds teachers nearing their contract limit. '''
    teacher_utilization = class_groups.groupby("TEACHER")["LOAD"].first() / class_groups.groupby("TEACHER")["CONTRACT"].first()
    return teacher_utilization[teacher_utilization > 0.9]  # Threshold: exceeding 90%

def student_distribution_score(class_groups):
    ''' Measures student distribution fairness among teachers; the lower the better. One single score. '''
    student_counts = class_groups.groupby("TEACHER")["CURRENT CAPACITY"].sum()
    return student_counts.std() / student_counts.mean()  # Lower is better

def room_utilization_rate(class_groups):
    ''' Measures room utilization rate; the higher the better. '''
    class_groups = class_groups.assign(DURATION=class_groups["END TIME"] - class_groups["START TIME"])
    
    # Count how many rooms are actually occupied in each time slot
    occupied_slots = class_groups.groupby(["ROOM", "START TIME"]).size().count()
    
    # Compute the total available slots based on rooms and unique start times
    total_slots = len(class_groups["START TIME"].unique()) * len(class_groups["ROOM"].unique())
    
    return occupied_slots / total_slots  # No need for min(), since this prevents overestimation

def peak_hour_congestion(class_groups):
    ''' Identifies peak congestion hours, along with number of rooms booked simultaneously. '''
    hourly_usage = class_groups.groupby("START TIME")["ROOM"].count()
    
    # Sort values in descending order and get the top 10 by usage
    sorted_usage = hourly_usage.sort_values(ascending=False)
    
    # Find the usage count at the 10th position
    threshold = sorted_usage.iloc[9] if len(sorted_usage) > 9 else sorted_usage.iloc[-1]
    
    # Keep all hours with the same usage as the 10th highest
    peak_hours = sorted_usage[sorted_usage >= threshold]
    
    return peak_hours

def room_underuse(class_groups):
    ''' Detects underused rooms, along with total usage time (in full time slots) across all week. '''
    # 7 time slots of duration equals to a range like 2-8, since both ends are always counted.
    class_groups = class_groups.assign(DURATION=class_groups["END TIME"] - class_groups["START TIME"] + 1)
    
    # Calculate the total usage for each room
    room_usage = class_groups.groupby("ROOM")["DURATION"].sum()
    
    # Calculate the maximum possible usage (assuming 100 as the max possible)
    max_possible_usage = 100  # You can replace this with the actual maximum if needed
    
    # Normalize the usage to the percentage of maximum possible usage
    actual_room_usage = (room_usage / max_possible_usage)
    
    # Sort rooms by their actual usage from greater to lesser
    return actual_room_usage.sort_values(ascending=False)  # Sorting in descending order

def find_missing_students_with_requests(solution, num_students, priorities, courses, instruments):
    ''' Identify students who requested a course or instrument but were not scheduled. These students will always be students that do not 
    have respective continuity, since that would immediately turn the model infeasible. If a student is not scheduled to any instrument,
    but that is because they did not request any, they are obviously not considered missing. '''

    assigned_course_students = set()
    assigned_instrument_students = set()

    for _, row in solution.iterrows():
        class_name = row["CLASS"]
        students = row["STUDENT"]

        # Ensure we always get student IDs in set format
        if isinstance(students, int):  
            student_indices = {students}  # If stored as a single integer
        elif isinstance(students, list):
            if all(isinstance(s, dict) for s in students):  
                student_indices = {list(s.keys())[0] for s in students}  # Extract student ID from dict
            else:
                student_indices = set(students)  # If stored as list of integers
        else:
            student_indices = set()  # If empty or unknown type, ignore

        if class_name.startswith("Course"):
            assigned_course_students.update(student_indices)
        elif class_name.startswith("Instrument"):
            assigned_instrument_students.update(student_indices)

    all_students = set(range(num_students))

    # --- Course Requests Check ---
    requested_course_students = set()
    for s in range(num_students):
        student_id = priorities.index[s]
        for c in range(len(courses)):  # Check all courses
            column_name = f'course_{courses.index[c]}'
            if column_name in priorities.columns and priorities.loc[student_id, column_name] == 1:
                requested_course_students.add(s)
                break  # If they requested any course, add them and stop checking further

    missing_course_students = sorted(requested_course_students - assigned_course_students)

    # --- Instrument Requests Check ---
    requested_instrument_students = set()
    for s in range(num_students):
        student_id = priorities.index[s]
        
        first_option_columns = [col for col in priorities.columns if col.startswith("instrument_1_")]
        second_option_columns = [col for col in priorities.columns if col.startswith("instrument_2_")]

        first_requested = any(priorities.loc[student_id, col] == 1 for col in first_option_columns)
        second_requested = any(priorities.loc[student_id, col] == 1 for col in second_option_columns)

        if first_requested or second_requested:
            requested_instrument_students.add(s)

    missing_instrument_students = sorted(requested_instrument_students - assigned_instrument_students)

    # Print missing students separately
    print("\nStudents Missing a Scheduled Course (but Requested One):", missing_course_students)
    print("Students Missing a Scheduled Instrument (but Requested One):", missing_instrument_students)

    return missing_course_students, missing_instrument_students

def create_sibling_groups(siblings_df):
    ''' Function used to create a list of unique sibling groups in order to apply the Siblings constraint. In the raw data, as well as in
    the preprocessed data, the sibling groups repeat as many times as siblings are in the group. '''

    student_index_map = {student_id: idx for idx, student_id in enumerate(siblings_df.index)}

    sibling_groups = {}
    for student_id, sibling_list in siblings_df["siblings"].items():
        if isinstance(sibling_list, str):
            sibling_list = eval(sibling_list)
        if not sibling_list:
            continue 

        current_index = student_index_map[student_id]
        sibling_indices = [student_index_map[sibling_id] for sibling_id in sibling_list if sibling_id in student_index_map]
        
        if sibling_indices:
            current_group = set([current_index] + sibling_indices)
            # Find any existing groups that overlap with the current group
            overlapping_groups = [group for group in sibling_groups.values() if group & current_group]
            if overlapping_groups:
                # Merge all overlapping groups into one
                merged_group = set.union(*overlapping_groups, current_group)
                # Remove the old groups
                for group in overlapping_groups:
                    for member in group:
                        sibling_groups.pop(member, None)
                for member in merged_group:
                    sibling_groups[member] = merged_group
            else:
                # No overlapping groups, create a new group
                for member in current_group:
                    sibling_groups[member] = current_group
    
    # Extract unique sibling groups as a list of tuples, ignoring single-person groups
    unique_sibling_groups = {tuple(sorted(group)) for group in sibling_groups.values() if len(group) > 1}
    
    return list(unique_sibling_groups)

def priority_instrument(student_availability, priorities):
    ''' Function used for determining the high-priority instrument (y) and the low priority instrument (z) for all students. '''

    num_students = student_availability.shape[0]
    y_ins = {}
    z_ins = {}

    for s in range(num_students):
        student_id = priorities.index[s]
        first_option_columns = [col for col in priorities.columns if col.startswith("instrument_1_")]
        second_option_columns = [col for col in priorities.columns if col.startswith("instrument_2_")]
        first_requested_instruments = [i for i, col in enumerate(first_option_columns) if priorities.loc[student_id, col] == 1]
        second_requested_instruments = [i for i, col in enumerate(second_option_columns) if priorities.loc[student_id, col] == 1]
        first_priority_weight = priorities.loc[student_id, 'instrument_1_priority']
        second_priority_weight = priorities.loc[student_id, 'instrument_2_priority']

        # Determine the instruments to assign to `y` and `z` based on priority weights
        if first_priority_weight >= second_priority_weight:
            y_instrument = first_requested_instruments[0] if first_requested_instruments else None
            z_instrument = second_requested_instruments[0] if second_requested_instruments else None
        else:
            y_instrument = second_requested_instruments[0] if second_requested_instruments else None
            z_instrument = first_requested_instruments[0] if first_requested_instruments else None

        y_ins[s] = y_instrument
        z_ins[s] = z_instrument
    
    return y_ins, z_ins

def get_student_schedule(courses, instruments, student_availability, priorities, num_students, num_courses, num_instruments):
    ''' Compute the theoretical minimum amount of days a student should attend class considering their firs-option requests.
    Later, use this information to update sibling penalty data by removing a penalty for each unavoidable mismatching day. '''
    i_s, i_z = priority_instrument(student_availability, priorities)

    min_days = {}

    for s in range(num_students):
        student_id = student_availability.index[s]
        course_days = 0
        for c in range(num_courses):
            column_name = f'course_{courses.index[c]}'
            if column_name in priorities.columns and student_id in priorities.index:
                if priorities.loc[student_id, column_name] == 1:
                    # Requested course
                    if courses.iloc[c]["course_duration_times_per_week"] == 2:
                        # Biweekly course
                        course_days = 2
                    else:
                        # Not a biweekly course
                        course_days = 1
        instrument_days = 0
        for i in range(num_instruments):
            if i_s[s] == i:
                if instruments.iloc[i]["instrument_duration_times_per_week"] == 2:
                    # Biweekly instrument
                    instrument_days = 2
                else:
                    # Not a biweekly instrument
                    instrument_days = 1
        
        # Compute the minimum amount of days required per student assuming full shcedule of their first-option requested classes.
        total_min_days = 0

        if course_days == 2 and instrument_days == 2:
            total_min_days = 2
        elif course_days == 2 and instrument_days == 1 or course_days == 1 and instrument_days == 2:
            total_min_days = 2

        elif course_days == 1 and instrument_days == 1:
            total_min_days = 1
        elif course_days == 1 and instrument_days == 0 or course_days == 0 and instrument_days == 1:
            total_min_days = 1

        else:
            total_min_days = 0
        
        min_days[s] = total_min_days

    return min_days

def compare_sibling_schedules(s_groups, min_days, num_students):
    ''' Compare sibling minimum required attendance days to later remove unavoidable penalties. Only implemented for pairs of siblings. '''
    
    missmatch_days = {}

    for s in range(num_students):
        missmatch_days[s] = 0  # Default value that does not change sibling penalties

    for group in s_groups:
        d_list = []
        for s in group:
            d_list.append(min_days[s])
        
        if len(d_list) == 2:
            if d_list[0] == d_list[1]:
                missmatch = 0
            elif d_list[0] > d_list[1] or d_list[0] < d_list[1]:
                missmatch = abs(d_list[0] - d_list[1])
        else:
            # We do not apply this penalty removing logic in cases of more than two silblings in a group; at least for now.
            continue
        
        for s in group:
            missmatch_days[s] = missmatch

    return missmatch_days

def update_sibling_penalties(class_groups, missmatch_days):
    ''' Update sibling penalty data by removing a penalty for each unavoidable mismatching day between siblings assuming full shcedule 
    of their first-option requested classes. '''

    for index, row in class_groups.iterrows():
        for student_info in row["STUDENT"]:
            for student, penalties in student_info.items():
                d = missmatch_days[student]
                if penalties["sibling_mismatch"] - d >= 0:
                    penalties["sibling_mismatch"] = penalties["sibling_mismatch"] - d
                else:
                    continue

    return class_groups

import numpy as np

def count_students_per_timeslot(class_groups):
    # Initialize a dictionary to store the number of students at each time slot
    student_count = {t: 0 for t in range(100)}
    
    # Iterate through each row of the dataframe
    for _, row in class_groups.iterrows():
        start_time, end_time = row['START TIME'], row['END TIME']
        
        # Add students to each time slot within the class duration
        for t in range(start_time, end_time + 1):
            student_count[t] += 1
    
    return student_count

def extract_penalties(class_groups):
    """Creates two dictionaries with the latest penalty values for each student."""
    antiquity_penalty_dict = {}
    sibling_penalty_dict = {}

    for _, row in class_groups.iterrows():
        student_id = row["STUDENT"]
        
        # Override with the latest penalty values
        antiquity_penalty_dict[student_id] = row["ANTIQUITY DAY PENALTY"]
        sibling_penalty_dict[student_id] = row["SIBLING MISMATCH PENALTY"]

    return antiquity_penalty_dict, sibling_penalty_dict
