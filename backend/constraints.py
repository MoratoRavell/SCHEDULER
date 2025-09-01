
# |||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
# |||||||||||||||||||||||||||||||||||||||||||||||||||||||| SCHEDULER:  Constraints ||||||||||||||||||||||||||||||||||||||||||||||||||||||||
# |||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||

# This newer version of the constraints script aims at reducing model model size and memory usage so that the model does not crash on the
# solving step due to memory issues, which happend to me with as little as 30 students, 5 teachers and 5 rooms.

# I first set custom paging size for my PC, allocating about 10.000 more MB to virtual memory. I also set a custom callback solver that
# prints solutions to free memory space during the solving process, which is yet to be tested. The last step is to optimize the constraints
# to reduce model size by eliminating those variables that are quickly set to 0 by the more direct constraints that are applied at the
# beginnig of the process. If all of this fails, the last resort would be to use Google Colab or a similar service that allows for
# programs to be run in cloud servers. This option would most likely require paying for extra compute.


# |||||||||| IMPORT LIBRARIES |||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
from ortools.sat.python import cp_model
import pandas as pd
import math
import os
import logging
import ast
import builtins

DEBUG_FILE = r"c:\Users\joanm\Documents\SCHEDULER DATA\debug_file.txt"

def print(*args, **kwargs):
    """Wrapper around built-in print that also logs to file."""
    builtins.print(*args, **kwargs)  # normal console print
    with open(DEBUG_FILE, "a", encoding="utf-8") as f:
        builtins.print(*args, **kwargs, file=f)


# |||||||||| SETUP LOGGING ||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
if not os.path.exists('logs'):
    os.makedirs('logs')

def log_to_file(file_name, data):
    ''' Function used for logging the solution in a specific file inside the logs directory. '''
    with open(file_name, 'a') as f:
        f.write(data + "\n")

# Initiate logging for debugging purposes
# As of now the "logging" library is not used anywhere, but it is incredibly useful during the implementation process of any part
logging.basicConfig(filename="debug_log.txt", level=logging.DEBUG, filemode='w')


# |||||||||| HELPER FUNCTIONS |||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
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

def safe_eval(val):
    ''' Apparently, as teacher contract is right know the sometimes i get a list sometimes a string for [900, 240],
    which maxes save_eval needed to choose dinamically how to extract max_weekly_minutes. '''
    if isinstance(val, str):  # Apply only if it's a string
        return ast.literal_eval(val)
    return val

def is_same_day(t, duration):
    day_slot_ranges = {
        0: range(0, 20),    # Monday
        1: range(20, 40),   # Tuesday
        2: range(40, 60),   # Wednesday
        3: range(60, 80),   # Thursday
        4: range(80, 100),   # Friday 
        # For some reason 100 reaises keyError while 99 works fine, no class is ever going to be ever assigned to t = 100 anyways
    }

    t_end = t + duration - 1  # Compute the end time slot

    # Find the day for t
    start_day = next(day for day, slots in day_slot_ranges.items() if t in slots)

    # Find the day for t_end
    end_day = next(day for day, slots in day_slot_ranges.items() if t_end in slots)

    return start_day == end_day

def precompute_starting_slots(student_availability, num_slots, num_courses, num_instruments, courses, instruments):
    ''' Function used for determining all time slots the model can actually assign for each student, given individual availability and
    class duration, thus implementing the Class duration constraint and the Overlaps constraint. The model works by assigning individual
    time slots to the different class types (x, x2, y, y2, z, z2). However, classes span accross multiple time slots (1 slot = 15 min),
    the number of which depends on the corresponding class duration. To ensure classes are not assigned when the student the model is
    working with will not be able to finish it, and in order to avoid scheduling overlapping classes, the precompute_starting_slots function
    computes all possible time slots the model can assign for every student and class type combination. '''

    durations = {
        "course": [courses.iloc[c]["course_duration_minutes_per_session"] for c in range(num_courses)],
        "instrument": [instruments.iloc[i]["instrument_duration_minutes_per_session"] for i in range(num_instruments)]
    }

    valid_starting_slots = {}

    for s in range(len(student_availability)):
        valid_starting_slots[s] = {}

        for c in range(len(durations["course"])):
            valid_starting_slots[s][f'course_{c}'] = []
            duration = durations["course"][c]
            duration = int(duration / 15)

            for t in range(num_slots):
                # Check if the student is available for the full duration starting at `t`
                if t + duration <= num_slots:
                    availability_slice = student_availability.iloc[s, t:t + duration]
                    # Ensure we check per day, if the slice crosses into the next day, it should be invalid
                    doesitcross = is_same_day(t, duration)
                    if not doesitcross:  # This slice spans two different days
                        continue  # Skip this starting point
                    if all(availability_slice == 1):  # Ensure the student is available for the entire duration
                        valid_starting_slots[s][f'course_{c}'].append(t)

        for i in range(len(durations["instrument"])):
            valid_starting_slots[s][f'instrument_{i}'] = []
            duration = durations["instrument"][i]
            duration = int(duration / 15)

            for t in range(num_slots):
                # Check if the student is available for the full duration starting at `t`
                if t + duration <= num_slots:
                    availability_slice = student_availability.iloc[s, t:t + duration]

                    # Ensure we check per day, if the slice crosses into the next day, it should be invalid
                    doesitcross = is_same_day(t, duration)

                    if not doesitcross:  # This slice spans two different days
                        continue  # Skip this starting point

                    if all(availability_slice == 1):  # Ensure the student is available for the entire duration
                        valid_starting_slots[s][f'instrument_{i}'].append(t)

    return valid_starting_slots

def antique_students(student_availability, antiquity):
    ''' Funtion used for storing class days and starting time for those class days for all students with antiquity, looking
    exclussively to their feasible antique schedule (overlap between antique schedule and current availability). '''

    antique_schedule_dict = {}

    for student_id, row in antiquity.iterrows():
        # Check the availability of the student for each slot
        daily_start_times = []
        day_index = 0

        for day in ['MON', 'TUE', 'WED', 'THU', 'FRI']:
            day_slots = [col for col in antiquity.columns if col.startswith(day)]
            
            # Check if the student is available on the given day and if they have a scheduled class
            first_slot = None
            for slot in day_slots:
                # Check if the student has an availability of 1 for the slot in both matrices
                if student_availability.loc[student_id, slot] == 1 and row[slot] == 1:
                    first_slot = slot
                    break

            # Extract the time part from the slot name or use 'none' if no class is found
            if first_slot:
                start_time = first_slot.split()[1]  # Time part after the space (e.g., "16:00")
            else:
                start_time = "none"

            daily_start_times.append((day_index, start_time))
            day_index += 1

        antique_schedule_dict[student_id] = daily_start_times
    
    return antique_schedule_dict

def priority_instrument(student_availability, priorities):
    ''' Function used for determining the high-priority instrument (y) and the low priority instrument (z) for all students.
    The Instrument priority constraint and the Continuity constraint penalize the model for assigning low-priority instruments to the 
    students, while ensuring students with a continuity value of 1 always get the high-priority instrument for continuity reasons 
    (students who have already attended the requested instrument's classes the previous year shall continue to do so if requested
    as first option; otherwise is considered that the student whishes to change isntruments). '''

    num_students = student_availability.shape[0]
    y_ins = {}
    z_ins = {}
    continuity = {}

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
            if first_priority_weight == 2:
                continuity[s] = 1
            else:
                continuity[s] = 0
        else:
            y_instrument = second_requested_instruments[0] if second_requested_instruments else None
            z_instrument = first_requested_instruments[0] if first_requested_instruments else None
            if second_priority_weight == 2:
                continuity[s] = 1
            else:
                continuity[s] = 0

        y_ins[s] = y_instrument
        z_ins[s] = z_instrument
    
    return y_ins, z_ins, continuity

def get_minimum_days(s, x, x2, y, y2, z, z2, num_courses, num_instruments, num_slots, model):
    ''' Function used for avoiding sibling penalties in those cases where class days among sibling groups will never fully match.
    Such is the case of siblings with different class assignments, where a sibling might require additional class days. 
    This function is currently unused due to the enormous complexity of the proposed siblings constraint, which has seen its logic 
    unfortunately simplified. The get_min_days function has been left in the script in case the constraint can be expanded in the future.

    The function returns the theoretical minimum amount of days a certain student (s) would be required to attend class given its class
    type assignments (x, x2, y, y2, z, z2). Student availability is not checked, meaning as the function stands right now, the theoretical
    minimum might not be the actual minimum for the student (theoretical minimum <= real minimum). This could be updated in the future. 
    
    Since adding teachers (e) and rooms (r) to the model, this function got outdated. Nevertheless, for now I will still keep it here for
    a bit longer, just in case. '''

    # Create boolean variables for conditions
    has_weekly_course = model.NewBoolVar(f'has_weekly_course_{s}')
    has_biweekly_course = model.NewBoolVar(f'has_biweekly_course_{s}')
    has_weekly_instrument = model.NewBoolVar(f'has_weekly_instrument_{s}')
    has_biweekly_instrument = model.NewBoolVar(f'has_biweekly_instrument_{s}')

    # Assign values to these boolean variables
    model.Add(sum(x[s, c, t] for c in range(num_courses) for t in range(num_slots)) > 0).OnlyEnforceIf(has_weekly_course)
    model.Add(sum(x[s, c, t] for c in range(num_courses) for t in range(num_slots)) == 0).OnlyEnforceIf(has_weekly_course.Not())

    model.Add(sum(x2[s, c, t] for c in range(num_courses) for t in range(num_slots)) > 0).OnlyEnforceIf(has_biweekly_course)
    model.Add(sum(x2[s, c, t] for c in range(num_courses) for t in range(num_slots)) == 0).OnlyEnforceIf(has_biweekly_course.Not())

    model.Add(sum(y[s, i, t] for i in range(num_instruments) for t in range(num_slots)) > 0).OnlyEnforceIf(has_weekly_instrument)
    model.Add(sum(y[s, i, t] for i in range(num_instruments) for t in range(num_slots)) == 0).OnlyEnforceIf(has_weekly_instrument.Not())

    model.Add(sum(y2[s, i, t] for i in range(num_instruments) for t in range(num_slots)) > 0).OnlyEnforceIf(has_biweekly_instrument)
    model.Add(sum(y2[s, i, t] for i in range(num_instruments) for t in range(num_slots)) == 0).OnlyEnforceIf(has_biweekly_instrument.Not())

    # Create an integer variable for minimum days
    min_days = model.NewIntVar(0, 2, f'min_days_{s}')

    # Add constraints for determining minimum days
    model.Add(min_days == 1).OnlyEnforceIf([
        has_weekly_course,
        has_weekly_instrument.Not(),
        has_biweekly_instrument.Not()
    ])
    model.Add(min_days == 1).OnlyEnforceIf([
        has_weekly_instrument,
        has_weekly_course.Not(),
        has_biweekly_course.Not()
    ])
    model.Add(min_days == 1).OnlyEnforceIf([
        has_weekly_course,
        has_weekly_instrument
    ])
    model.Add(min_days == 2).OnlyEnforceIf([
        has_biweekly_course,
        has_weekly_instrument.Not(),
        has_biweekly_instrument.Not()
    ])
    model.Add(min_days == 2).OnlyEnforceIf([
        has_biweekly_instrument,
        has_weekly_course.Not(),
        has_biweekly_course.Not()
    ])
    model.Add(min_days == 2).OnlyEnforceIf([
        has_biweekly_course,
        has_weekly_instrument
    ])
    model.Add(min_days == 2).OnlyEnforceIf([
        has_biweekly_instrument,
        has_weekly_course
    ])
    model.Add(min_days == 2).OnlyEnforceIf([
        has_biweekly_course,
        has_biweekly_instrument
    ])

    return min_days


# |||||||||| CONSTRAINTS |||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
def initialize_variables(model, gx, gx2, gy, gy2, gz, gz2, num_teachers, num_rooms, courses, instruments, num_students, num_courses, num_slots, num_instruments, student_availability, teacher_availability):
    for s in range(num_students):
        for e in range(num_teachers):
            for r in range(num_rooms):
                for t in range(num_slots):
                    # Skip creating variables if student or teacher is unavailable
                    if student_availability.iloc[s, t] == 0 or teacher_availability.iloc[e, t] == 0:
                        continue

                    for c in range(num_courses):
                        gx[s, e, r, c, t] = model.NewBoolVar(f'gx_s{s}_e{e}_r{r}_c{c}_t{t}')
                        
                        # Only create gx2 if biweekly
                        if courses.iloc[c]["course_duration_times_per_week"] == 2:
                            gx2[s, e, r, c, t] = model.NewBoolVar(f'gx2_s{s}_e{e}_r{r}_c{c}_t{t}')

                    for i in range(num_instruments):
                        gy[s, e, r, i, t] = model.NewBoolVar(f'gy_s{s}_e{e}_r{r}_i{i}_t{t}')
                        gz[s, e, r, i, t] = model.NewBoolVar(f'gz_s{s}_e{e}_r{r}_i{i}_t{t}')
                        
                        # Only create gy2 and gz2 if biweekly
                        if instruments.iloc[i]["instrument_duration_times_per_week"] == 2:
                            gy2[s, e, r, i, t] = model.NewBoolVar(f'gy2_s{s}_e{e}_r{r}_i{i}_t{t}')
                            gz2[s, e, r, i, t] = model.NewBoolVar(f'gz2_s{s}_e{e}_r{r}_i{i}_t{t}')

    return model, gx, gx2, gy, gy2, gz, gz2

def continuity_and_priorization(model, gx, gx2, gy, gy2, gz, gz2, num_teachers, num_rooms, priorities, course_continuity, student_availability, courses, instruments, num_students, num_courses, num_slots, num_instruments):
    y_ins, z_ins, continuity = priority_instrument(student_availability, priorities)

    remove_gx, remove_gx2 = [], []
    remove_gy, remove_gy2, remove_gz, remove_gz2 = [], [], [], []

    # Course and instrument selection
    print(f'these are the columns to check {priorities.columns}')
    print(f'these are the students to check {priorities.index}')
    for s in range(num_students):
        student_id = student_availability.index[s]
        for e in range(num_teachers):
            for r in range(num_rooms):
                for c in range(num_courses):
                    column_name = f'course_{courses.index[c]}'
                    print(F'1. WE ARE HERE - {column_name} and {student_id}')
                    if column_name in priorities.columns and student_id in priorities.index:
                        print('2. NOW HERE')
                        if priorities.loc[student_id, column_name] == 0:
                            print('3. AND NOW HERE')
                            for t in range(num_slots):
                                if (s, e, r, c, t) in gx:
                                    print('4. FINALLY HERE')
                                    model.Add(gx[s, e, r, c, t] == 0)
                                    remove_gx.append((s, e, r, c, t))
                                if (s, e, r, c, t) in gx2:
                                    model.Add(gx2[s, e, r, c, t] == 0)
                                    remove_gx2.append((s, e, r, c, t))
                        elif priorities.loc[student_id, column_name] == 1:
                            continue

                if continuity[s] == 1:
                    # In this case the lower priority instrument must never be scheduled
                    for i in range(num_instruments):
                        for t in range(num_slots):
                            if (s, e, r, i, t) in gz:
                                model.Add(gz[s, e, r, i, t] == 0)
                                remove_gz.append((s, e, r, i, t))
                            if (s, e, r, i, t) in gz2:
                                model.Add(gz2[s, e, r, i, t] == 0)
                                remove_gz2.append((s, e, r, i, t))

                for i in range(num_instruments):
                    if i != y_ins[s]:
                        # If the instrument for the student is not assigned as `y_instrument`, set all `y` and `y2` variables to 0
                        for t in range(num_slots):
                            if (s, e, r, i, t) in gy:
                                model.Add(gy[s, e, r, i, t] == 0)
                                remove_gy.append((s, e, r, i, t))
                            if (s, e, r, i, t) in gy2:
                                model.Add(gy2[s, e, r, i, t] == 0)
                                remove_gy2.append((s, e, r, i, t))

                    if z_ins[s] is not None and i != z_ins[s]:
                        # If the instrument is not assigned as `z_instrument` for the student, set all `z` and `z2` variables to 0
                        for t in range(num_slots):
                            if (s, e, r, i, t) in gz:
                                model.Add(gz[s, e, r, i, t] == 0)
                                remove_gz.append((s, e, r, i, t))
                            if (s, e, r, i, t) in gz2:
                                model.Add(gz2[s, e, r, i, t] == 0)
                                remove_gz2.append((s, e, r, i, t))

                # If z_instrument for the student is None (no second requested instrument), eliminate all `z` and `z2` combinations
                if z_ins[s] is None:
                    for i in range(num_instruments):
                        for t in range(num_slots):
                            if (s, e, r, i, t) in gz:
                                model.Add(gz[s, e, r, i, t] == 0)
                                remove_gz.append((s, e, r, i, t))
                            if (s, e, r, i, t) in gz2:
                                model.Add(gz2[s, e, r, i, t] == 0)
                                remove_gz2.append((s, e, r, i, t))
            
    course_priorization = []
    for idx, next_course_id in enumerate(course_continuity['next_course']):
        if next_course_id > 0:
            course_priorization.append(idx)
 
    # Remove all zero variables from dictionaries
    for key in remove_gx:
        if key in gx:
            del gx[key]
    for key in remove_gx2:
        if key in gx2:
            del gx2[key]
    for key in remove_gy:
        if key in gy:
            del gy[key]
    for key in remove_gy2:
        if key in gy2:
            del gy2[key]
    for key in remove_gz:
        if key in gz:
            del gz[key]
    for key in remove_gz2:
        if key in gz2:
            del gz2[key]

    print(f'REMOVE GX {remove_gx}')
    print('XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX')
    print(f'REMOVE GX2 {remove_gx2}')
    print('XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX')
    print(f'REMOVE GY {remove_gy}')
    print('XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX')
    print(f'REMOVE GY2 {remove_gy2}')

    return model, gx, gx2, gy, gy2, gz, gz2, y_ins, z_ins, continuity, course_priorization

def student_class_duration(model, gx, gx2, gy, gy2, gz, gz2, num_teachers, num_rooms, student_availability, teacher_availability, courses, instruments, num_students, num_courses, num_slots, num_instruments):
    st_valid_starting_slots = precompute_starting_slots(student_availability, num_slots, num_courses, num_instruments, courses, instruments)
    tch_valid_starting_slots = precompute_starting_slots(teacher_availability, num_slots, num_courses, num_instruments, courses, instruments)

    remove_gx, remove_gx2 = [], []
    remove_gy, remove_gy2, remove_gz, remove_gz2 = [], [], [], []

    for s in range(num_students):
        for e in range(num_teachers):
            for r in range(num_rooms):
                for c in range(num_courses):
                    for t in range(num_slots):
                        if t not in st_valid_starting_slots[s].get(f'course_{c}', []) or t not in tch_valid_starting_slots[e].get(f'course_{c}', []):
                            if (s, e, r, c, t) in gx:
                                model.Add(gx[s, e, r, c, t] == 0)
                                remove_gx.append((s, e, r, c, t))
                            if (s, e, r, c, t) in gx2:
                                model.Add(gx2[s, e, r, c, t] == 0)
                                remove_gx2.append((s, e, r, c, t))

                for i in range(num_instruments):
                    for t in range(num_slots):
                        if t not in st_valid_starting_slots[s].get(f'instrument_{i}', []) or t not in tch_valid_starting_slots[e].get(f'instrument_{i}', []):
                            if (s, e, r, i, t) in gz:
                                model.Add(gz[s, e, r, i, t] == 0)
                                remove_gz.append((s, e, r, i, t))
                            if (s, e, r, i, t) in gz2:
                                model.Add(gz2[s, e, r, i, t] == 0)
                                remove_gz2.append((s, e, r, i, t))
                            if (s, e, r, i, t) in gy:
                                model.Add(gy[s, e, r, i, t] == 0)
                                remove_gy.append((s, e, r, i, t))
                            if (s, e, r, i, t) in gy2:
                                model.Add(gy2[s, e, r, i, t] == 0)
                                remove_gy2.append((s, e, r, i, t))
    
    # Remove all zero variables from dictionaries
    for key in remove_gx:
        if key in gx:
            del gx[key]
    for key in remove_gx2:
        if key in gx2:
            del gx2[key]
    for key in remove_gy:
        if key in gy:
            del gy[key]
    for key in remove_gy2:
        if key in gy2:
            del gy2[key]
    for key in remove_gz:
        if key in gz:
            del gz[key]
    for key in remove_gz2:
        if key in gz2:
            del gz2[key]

    return model, gx, gx2, gy, gy2, gz, gz2, st_valid_starting_slots, tch_valid_starting_slots

def single_class_type(model, gx, gx2, gy, gy2, gz, gz2, priorities, student_availability, courses, instruments, num_teachers, num_rooms, num_students, num_courses, num_slots, num_instruments, y_ins, z_ins, continuity, course_priorization):
    # Ensure each student attends up to one course and one instrument (up to one class type per student)

    for s in range(num_students):
        student_id = student_availability.index[s]

        # Extract instrument id for the given student
        if s in y_ins:
            i_s = y_ins[s]
        if s in z_ins:
            i_z = z_ins[s]

        if continuity[s] == 1:
            # If continuity[s] == 1 we must schedule the first-option instrument (gy/gy2)
            model.Add(sum(gy[s, e, r, i, t] for e in range(num_teachers) 
                        for r in range(num_rooms) 
                        for i in range(num_instruments) 
                        for t in range(num_slots) if (s, e, r, i, t) in gy) == 1)

            for i in range(num_instruments):
                if i_s == i: 
                    if instruments.iloc[i]["instrument_duration_times_per_week"] == 2:
                        # The requested instrument is biweekly
                        model.Add(sum(gy2[s, e, r, i, t] for e in range(num_teachers) 
                                    for r in range(num_rooms) 
                                    for i in range(num_instruments) 
                                    for t in range(num_slots) if (s, e, r, i, t) in gy2) == 1)
                    else:
                        # The requested instrument is not biweekly
                        model.Add(sum(gy2[s, e, r, i, t] for e in range(num_teachers) 
                                    for r in range(num_rooms) 
                                    for i in range(num_instruments) 
                                    for t in range(num_slots) if (s, e, r, i, t) in gy2) == 0)

        else:
            model.Add(sum(gy[s, e, r, i, t] for e in range(num_teachers) 
                        for r in range(num_rooms) 
                        for i in range(num_instruments) 
                        for t in range(num_slots) if (s, e, r, i, t) in gy) <= 1)

            model.Add(sum(gy2[s, e, r, i, t] for e in range(num_teachers) 
                        for r in range(num_rooms) 
                        for i in range(num_instruments) 
                        for t in range(num_slots) if (s, e, r, i, t) in gy2) <= 1)

            model.Add(sum(gz[s, e, r, i, t] for e in range(num_teachers) 
                        for r in range(num_rooms) 
                        for i in range(num_instruments) 
                        for t in range(num_slots) if (s, e, r, i, t) in gz) <= 1)

            model.Add(sum(gz2[s, e, r, i, t] for e in range(num_teachers) 
                        for r in range(num_rooms) 
                        for i in range(num_instruments) 
                        for t in range(num_slots) if (s, e, r, i, t) in gz2) <= 1)
            
            for i in range(num_instruments):
                if i_s == i: 
                    if instruments.iloc[i]["instrument_duration_times_per_week"] == 2:
                        # The requested instrument is biweekly
                        model.Add(
                            sum(gy[s, e, r, i, t] for e in range(num_teachers)
                                                for r in range(num_rooms)
                                                for i in range(num_instruments)
                                                for t in range(num_slots) if (s, e, r, i, t) in gy) 
                            == sum(gy2[s, e, r, i, t] for e in range(num_teachers)
                                                    for r in range(num_rooms)
                                                    for i in range(num_instruments)
                                                    for t in range(num_slots) if (s, e, r, i, t) in gy2)
                        )
                    else:
                        # The requested instrument is not biweekly
                        model.Add(sum(gy2[s, e, r, i, t] for e in range(num_teachers) 
                                    for r in range(num_rooms) 
                                    for i in range(num_instruments) 
                                    for t in range(num_slots) if (s, e, r, i, t) in gy2) == 0)
                if i_z == i: 
                    if instruments.iloc[i]["instrument_duration_times_per_week"] == 2:
                        # The requested instrument is biweekly
                        model.Add(
                            sum(gz[s, e, r, i, t] for e in range(num_teachers)
                                                for r in range(num_rooms)
                                                for i in range(num_instruments)
                                                for t in range(num_slots) if (s, e, r, i, t) in gz) 
                            == sum(gz2[s, e, r, i, t] for e in range(num_teachers)
                                                    for r in range(num_rooms)
                                                    for i in range(num_instruments)
                                                    for t in range(num_slots) if (s, e, r, i, t) in gz2)
                        )
                    else:
                        # The requested instrument is not biweekly
                        model.Add(sum(gz2[s, e, r, i, t] for e in range(num_teachers) 
                                    for r in range(num_rooms) 
                                    for i in range(num_instruments) 
                                    for t in range(num_slots) if (s, e, r, i, t) in gz2) == 0)

        if s in course_priorization:
            model.Add(sum(gx[s, e, r, c, t] for e in range(num_teachers) 
                        for r in range(num_rooms) 
                        for c in range(num_courses) 
                        for t in range(num_slots) if (s, e, r, c, t) in gx) == 1)

            for c in range(num_courses):
                column_name = f'course_{courses.index[c]}'
                if column_name in priorities.columns and student_id in priorities.index:
                    if priorities.loc[student_id, column_name] == 1:
                        # The student requested the course
                        if courses.iloc[c]["course_duration_times_per_week"] == 2:
                            # The requested course is biweekly
                            model.Add(sum(gx2[s, e, r, c, t] for e in range(num_teachers) 
                                        for r in range(num_rooms) 
                                        for c in range(num_courses) 
                                        for t in range(num_slots) if (s, e, r, c, t) in gx2) == 1)
                        else:
                            # The requested course is not biweekly
                            model.Add(sum(gx2[s, e, r, c, t] for e in range(num_teachers) 
                                        for r in range(num_rooms) 
                                        for c in range(num_courses) 
                                        for t in range(num_slots) if (s, e, r, c, t) in gx2) == 0)

        else:
            model.Add(sum(gx[s, e, r, c, t] for e in range(num_teachers) 
                        for r in range(num_rooms) 
                        for c in range(num_courses) 
                        for t in range(num_slots) if (s, e, r, c, t) in gx) <= 1)

            model.Add(sum(gx2[s, e, r, c, t] for e in range(num_teachers) 
                        for r in range(num_rooms) 
                        for c in range(num_courses) 
                        for t in range(num_slots) if (s, e, r, c, t) in gx2) <= 1)
            
            for c in range(num_courses):
                column_name = f'course_{courses.index[c]}'
                if column_name in priorities.columns and student_id in priorities.index:
                    if priorities.loc[student_id, column_name] == 1:
                        # The student requested the course
                        if courses.iloc[c]["course_duration_times_per_week"] == 2:
                            # The requested course is biweekly, either both classes are scheduled or none of the two
                            model.Add(
                                sum(gx2[s, e, r, c, t] for e in range(num_teachers) 
                                            for r in range(num_rooms) 
                                            for c in range(num_courses) 
                                            for t in range(num_slots) if (s, e, r, c, t) in gx2) 
                                == sum(gx[s, e, r, c, t] for e in range(num_teachers) 
                                            for r in range(num_rooms) 
                                            for c in range(num_courses) 
                                            for t in range(num_slots) if (s, e, r, c, t) in gx)
                            )
                        else:
                            # The requested course is not biweekly
                            model.Add(sum(gx2[s, e, r, c, t] for e in range(num_teachers) 
                                        for r in range(num_rooms) 
                                        for c in range(num_courses) 
                                        for t in range(num_slots) if (s, e, r, c, t) in gx2) == 0)

    return model, gx, gx2, gy, gy2, gz, gz2


def priority_assignment(model, gx, gx2, gy, gy2, gz, gz2, num_teachers, num_rooms, courses, instruments, num_students, num_courses, num_slots, num_instruments, st_valid_starting_slots, tch_valid_starting_slots):
    for s in range(num_students):
        # Helper variable to indicate whether student s has a high-priority (y) assignment
        has_y = model.NewBoolVar(f"has_y_s{s}")
        # Helper variable to indicate whether student s has a low-priority (z) assignment
        has_z = model.NewBoolVar(f"has_z_s{s}")

        # Define whether the student has been assigned a high-priority (y) instrument
        model.Add(sum(gy[s, e, r, i, t] for e in range(num_teachers)
                                        for r in range(num_rooms)
                                        for i in range(num_instruments)
                                        for t in range(num_slots) if (s, e, r, i, t) in gy) > 0).OnlyEnforceIf(has_y)
        model.Add(sum(gy[s, e, r, i, t] for e in range(num_teachers)
                                        for r in range(num_rooms)
                                        for i in range(num_instruments)
                                        for t in range(num_slots) if (s, e, r, i, t) in gy) == 0).OnlyEnforceIf(has_y.Not())

        # Define whether the student has been assigned a low-priority (z) instrument
        model.Add(sum(gz[s, e, r, i, t] for e in range(num_teachers)
                                        for r in range(num_rooms)
                                        for i in range(num_instruments)
                                        for t in range(num_slots) if (s, e, r, i, t) in gz) > 0).OnlyEnforceIf(has_z)
        model.Add(sum(gz[s, e, r, i, t] for e in range(num_teachers)
                                        for r in range(num_rooms)
                                        for i in range(num_instruments)
                                        for t in range(num_slots) if (s, e, r, i, t) in gz) == 0).OnlyEnforceIf(has_z.Not())

        # If any y/y2 is assigned, then z/z2 must not be assigned, and vice versa
        model.Add(has_y + has_z <= 1)

    return model, gx, gx2, gy, gy2, gz, gz2

def student_overlaps(model, gx, gx2, gy, gy2, gz, gz2, num_teachers, num_rooms, courses, instruments, num_students, num_courses, num_slots, num_instruments, st_valid_starting_slots, tch_valid_starting_slots):
    # Prevent overlapping time slots for students, teachers, and rooms

    # Define the time slot ranges for each day
    day_slot_ranges = {
        0: range(0, 20),    # Monday
        1: range(20, 40),   # Tuesday
        2: range(40, 60),   # Wednesday
        3: range(60, 80),   # Thursday
        4: range(80, 99),   # Friday 
        # For some reason 100 reaises keyError while 99 works fine, no class is ever going to be ever assigned to t = 100 anyways
    }

    for s in range(num_students):  # Iterate over all possible start times

        # Student overlaps (already implemented)
        for t in range(num_slots):
            student_classes = []

            # Course scheduling
            for c in range(num_courses):
                duration = int(courses.iloc[c]["course_duration_minutes_per_session"] / 15)
                for overlap in range(duration):
                    if t - overlap >= 0:
                        student_classes.extend([
                            gx[s, e, r, c, t - overlap]
                            for e in range(num_teachers) for r in range(num_rooms) if (s, e, r, c, t - overlap) in gx
                        ])
                        student_classes.extend([
                            gx2[s, e, r, c, t - overlap]
                            for e in range(num_teachers) for r in range(num_rooms) if (s, e, r, c, t - overlap) in gx2
                        ])

            # Instrument scheduling
            for i in range(num_instruments):
                duration = int(instruments.iloc[i]["instrument_duration_minutes_per_session"] / 15)
                for overlap in range(duration):
                    if t - overlap >= 0:
                        student_classes.extend([
                            gy[s, e, r, i, t - overlap]
                            for e in range(num_teachers) for r in range(num_rooms) if (s, e, r, i, t - overlap) in gy
                        ])
                        student_classes.extend([
                            gy2[s, e, r, i, t - overlap]
                            for e in range(num_teachers) for r in range(num_rooms) if (s, e, r, i, t - overlap) in gy2
                        ])
                        student_classes.extend([
                            gz[s, e, r, i, t - overlap]
                            for e in range(num_teachers) for r in range(num_rooms) if (s, e, r, i, t - overlap) in gz
                        ])
                        student_classes.extend([
                            gz2[s, e, r, i, t - overlap]
                            for e in range(num_teachers) for r in range(num_rooms) if (s, e, r, i, t - overlap) in gz2
                        ])

            if student_classes:
                model.Add(sum(student_classes) <= 1)

    # up until this point we ensured students are not scheduled to overlapping classes

    # now its time to ensure the same for rooms and teachers

    # while ensuring one single room is scheduled for each class (class = unique room - time slot combination)
    # as well as making sure an unlimited number of students can be scheduled to any given class

    for s in range(num_students):
        # we treat students separately to allow multilpe students per class
        # basically, the same teacher-room-time slot constraints are applied separately to each student
        # thus ensuring we can limit the number of overlapping combinations without including the number of students

        for t in range(num_slots):
            for r in range(num_rooms):
                for e in range(num_teachers):
                    # for each room-teacher-time slot combination for the given student

                    room_teacher_classes = []

                    for c in range(num_courses):
                        duration = int(courses.iloc[c]["course_duration_minutes_per_session"] / 15)
                        for overlap in range(duration):
                            if t - overlap >= 0:
                                if (s, e, r, c, t - overlap) in gx:
                                    room_teacher_classes.append(gx[s, e, r, c, t - overlap])
                                if (s, e, r, c, t - overlap) in gx2:
                                    room_teacher_classes.append(gx2[s, e, r, c, t - overlap])

                    for i in range(num_instruments):
                        duration = int(instruments.iloc[i]["instrument_duration_minutes_per_session"] / 15)
                        for overlap in range(duration):
                            if t - overlap >= 0:
                                if (s, e, r, i, t - overlap) in gy:
                                    room_teacher_classes.append(gy[s, e, r, i, t - overlap])
                                if (s, e, r, i, t - overlap) in gy2:
                                    room_teacher_classes.append(gy2[s, e, r, i, t - overlap])
                                if (s, e, r, i, t - overlap) in gz:
                                    room_teacher_classes.append(gz[s, e, r, i, t - overlap])
                                if (s, e, r, i, t - overlap) in gz2:
                                    room_teacher_classes.append(gz2[s, e, r, i, t - overlap])

                    if room_teacher_classes: 
                        model.Add(sum(room_teacher_classes) <= 1)

                        # we are still inside a room-teacher-time slot combination for a given student
                        # we ensure for that student-room-teacher-time slot combination gx, gx2, gy, gy2, gz, gz2 do not overlap

                        # we are missing the constraint about different students overlapping at one given room-teacher-time slot combination
                        model.Add(
                            sum([
                                gx[s, e, r, c, t] for c in range(num_courses) if (s, e, r, c, t) in gx
                            ] + [
                                gx2[s, e, r, c, t] for c in range(num_courses) if (s, e, r, c, t) in gx2
                            ]) +
                            sum([
                                gy[s, e, r, i, t] for i in range(num_instruments) if (s, e, r, i, t) in gy
                            ] + [
                                gy2[s, e, r, i, t] for i in range(num_instruments) if (s, e, r, i, t) in gy2
                            ] + [
                                gz[s, e, r, i, t] for i in range(num_instruments) if (s, e, r, i, t) in gz
                            ] + [
                                gz2[s, e, r, i, t] for i in range(num_instruments) if (s, e, r, i, t) in gz2
                            ])
                            <= 1
                        )

    # Prevent teachers from being assigned to overlapping classes across different rooms/courses/instruments
    for t in range(num_slots):
        for e in range(num_teachers):
            teacher_schedule = []  # Track all classes assigned to teacher e at time t: only one will be valid
            
            for r in range(num_rooms):
                for c in range(num_courses):
                    duration = int(courses.iloc[c]["course_duration_minutes_per_session"] / 15)
                    
                    for overlap in range(duration):  # Ensure full duration is checked
                        if t - overlap >= 0:
                            class_var = model.NewBoolVar(f"gx_{e}_{r}_{c}_{t - overlap}")
                            model.Add(sum(
                                gx[s, e, r, c, t - overlap] for s in range(num_students) if (s, e, r, c, t - overlap) in gx
                            ) > 0).OnlyEnforceIf(class_var)
                            model.Add(sum(
                                gx[s, e, r, c, t - overlap] for s in range(num_students) if (s, e, r, c, t - overlap) in gx
                            ) == 0).OnlyEnforceIf(class_var.Not())

                            teacher_schedule.append(class_var)

                            class_var = model.NewBoolVar(f"gx2_{e}_{r}_{c}_{t - overlap}")
                            model.Add(sum(
                                gx2[s, e, r, c, t - overlap] for s in range(num_students) if (s, e, r, c, t - overlap) in gx2
                            ) > 0).OnlyEnforceIf(class_var)
                            model.Add(sum(
                                gx2[s, e, r, c, t - overlap] for s in range(num_students) if (s, e, r, c, t - overlap) in gx2
                            ) == 0).OnlyEnforceIf(class_var.Not())

                            teacher_schedule.append(class_var)

                for i in range(num_instruments):
                    duration = int(instruments.iloc[i]["instrument_duration_minutes_per_session"] / 15)

                    for overlap in range(duration):  # Ensure full duration is checked
                        if t - overlap >= 0:
                            class_var = model.NewBoolVar(f"gy_{e}_{r}_{i}_{t - overlap}")
                            model.Add(sum(
                                gy[s, e, r, i, t - overlap] for s in range(num_students) if (s, e, r, i, t - overlap) in gy
                            ) > 0).OnlyEnforceIf(class_var)
                            model.Add(sum(
                                gy[s, e, r, i, t - overlap] for s in range(num_students) if (s, e, r, i, t - overlap) in gy
                            ) == 0).OnlyEnforceIf(class_var.Not())

                            teacher_schedule.append(class_var)

                            class_var = model.NewBoolVar(f"gy2_{e}_{r}_{i}_{t - overlap}")
                            model.Add(sum(
                                gy2[s, e, r, i, t - overlap] for s in range(num_students) if (s, e, r, i, t - overlap) in gy2
                            ) > 0).OnlyEnforceIf(class_var)
                            model.Add(sum(
                                gy2[s, e, r, i, t - overlap] for s in range(num_students) if (s, e, r, i, t - overlap) in gy2
                            ) == 0).OnlyEnforceIf(class_var.Not())

                            teacher_schedule.append(class_var)

                            class_var = model.NewBoolVar(f"gz_{e}_{r}_{i}_{t - overlap}")
                            model.Add(sum(
                                gz[s, e, r, i, t - overlap] for s in range(num_students) if (s, e, r, i, t - overlap) in gz
                            ) > 0).OnlyEnforceIf(class_var)
                            model.Add(sum(
                                gz[s, e, r, i, t - overlap] for s in range(num_students) if (s, e, r, i, t - overlap) in gz
                            ) == 0).OnlyEnforceIf(class_var.Not())

                            teacher_schedule.append(class_var)

                            class_var = model.NewBoolVar(f"gz2_{e}_{r}_{i}_{t - overlap}")
                            model.Add(sum(
                                gz2[s, e, r, i, t - overlap] for s in range(num_students) if (s, e, r, i, t - overlap) in gz2
                            ) > 0).OnlyEnforceIf(class_var)
                            model.Add(sum(
                                gz2[s, e, r, i, t - overlap] for s in range(num_students) if (s, e, r, i, t - overlap) in gz2
                            ) == 0).OnlyEnforceIf(class_var.Not())

                            teacher_schedule.append(class_var)

            # Ensure the teacher is not scheduled for overlapping classes across any room or subject
            model.Add(sum(teacher_schedule) <= 1)

    # Prevent rooms from being assigned to overlapping classes across different teachers/courses/instruments
    for t in range(num_slots):
        for r in range(num_rooms):
            room_schedule = []  # Track all classes assigned to room r at time t: only one will be valid
            
            for e in range(num_teachers):
                for c in range(num_courses):
                    duration = int(courses.iloc[c]["course_duration_minutes_per_session"] / 15)
                    
                    for overlap in range(duration):
                        if t - overlap >= 0:
                            class_var = model.NewBoolVar(f"room_gx_{e}_{r}_{c}_{t - overlap}")
                            model.Add(sum(
                                gx[s, e, r, c, t - overlap] for s in range(num_students) if (s, e, r, c, t - overlap) in gx
                            ) > 0).OnlyEnforceIf(class_var)
                            model.Add(sum(
                                gx[s, e, r, c, t - overlap] for s in range(num_students) if (s, e, r, c, t - overlap) in gx
                            ) == 0).OnlyEnforceIf(class_var.Not())
                            room_schedule.append(class_var)
                            
                            class_var = model.NewBoolVar(f"room_gx2_{e}_{r}_{c}_{t - overlap}")
                            model.Add(sum(
                                gx2[s, e, r, c, t - overlap] for s in range(num_students) if (s, e, r, c, t - overlap) in gx2
                            ) > 0).OnlyEnforceIf(class_var)
                            model.Add(sum(
                                gx2[s, e, r, c, t - overlap] for s in range(num_students) if (s, e, r, c, t - overlap) in gx2
                            ) == 0).OnlyEnforceIf(class_var.Not())
                            room_schedule.append(class_var)
                
                for i in range(num_instruments):
                    duration = int(instruments.iloc[i]["instrument_duration_minutes_per_session"] / 15)
                    
                    for overlap in range(duration):
                        if t - overlap >= 0:
                            class_var = model.NewBoolVar(f"room_gy_{e}_{r}_{i}_{t - overlap}")
                            model.Add(sum(
                                gy[s, e, r, i, t - overlap] for s in range(num_students) if (s, e, r, i, t - overlap) in gy
                            ) > 0).OnlyEnforceIf(class_var)
                            model.Add(sum(
                                gy[s, e, r, i, t - overlap] for s in range(num_students) if (s, e, r, i, t - overlap) in gy
                            ) == 0).OnlyEnforceIf(class_var.Not())
                            room_schedule.append(class_var)
                            
                            class_var = model.NewBoolVar(f"room_gy2_{e}_{r}_{i}_{t - overlap}")
                            model.Add(sum(
                                gy2[s, e, r, i, t - overlap] for s in range(num_students) if (s, e, r, i, t - overlap) in gy2
                            ) > 0).OnlyEnforceIf(class_var)
                            model.Add(sum(
                                gy2[s, e, r, i, t - overlap] for s in range(num_students) if (s, e, r, i, t - overlap) in gy2
                            ) == 0).OnlyEnforceIf(class_var.Not())
                            room_schedule.append(class_var)
                            
                            class_var = model.NewBoolVar(f"room_gz_{e}_{r}_{i}_{t - overlap}")
                            model.Add(sum(
                                gz[s, e, r, i, t - overlap] for s in range(num_students) if (s, e, r, i, t - overlap) in gz
                            ) > 0).OnlyEnforceIf(class_var)
                            model.Add(sum(
                                gz[s, e, r, i, t - overlap] for s in range(num_students) if (s, e, r, i, t - overlap) in gz
                            ) == 0).OnlyEnforceIf(class_var.Not())
                            room_schedule.append(class_var)
                            
                            class_var = model.NewBoolVar(f"room_gz2_{e}_{r}_{i}_{t - overlap}")
                            model.Add(sum(
                                gz2[s, e, r, i, t - overlap] for s in range(num_students) if (s, e, r, i, t - overlap) in gz2
                            ) > 0).OnlyEnforceIf(class_var)
                            model.Add(sum(
                                gz2[s, e, r, i, t - overlap] for s in range(num_students) if (s, e, r, i, t - overlap) in gz2
                            ) == 0).OnlyEnforceIf(class_var.Not())
                            room_schedule.append(class_var)
                
            # Ensure the room is not double-booked
            model.Add(sum(room_schedule) <= 1)

    # Prevent biweekly sessions from occurring on the same day
    for s in range(num_students):
        for c in range(num_courses):
            if courses.iloc[c]["course_duration_times_per_week"] == 2:
                for d in range(5):  # Iterate over days
                    model.Add(
                        sum(gx[s, e, r, c, t] for e in range(num_teachers) for r in range(num_rooms)
                            for t in st_valid_starting_slots[s][f'course_{c}'] if t in day_slot_ranges[d] and (s, e, r, c, t) in gx and t in tch_valid_starting_slots[e][f'course_{c}']) +
                        sum(gx2[s, e, r, c, t] for e in range(num_teachers) for r in range(num_rooms)
                            for t in st_valid_starting_slots[s][f'course_{c}'] if t in day_slot_ranges[d] and (s, e, r, c, t) in gx2 and t in tch_valid_starting_slots[e][f'course_{c}'])
                        <= 1
                    )

        for i in range(num_instruments):
            if instruments.iloc[i]["instrument_duration_times_per_week"] == 2:
                for d in range(5):  # Iterate over days
                    model.Add(
                        sum(gy[s, e, r, i, t] for e in range(num_teachers) for r in range(num_rooms)
                            for t in st_valid_starting_slots[s][f'instrument_{i}'] if t in day_slot_ranges[d] and (s, e, r, i, t) in gy and t in tch_valid_starting_slots[e][f'instrument_{i}']) +
                        sum(gy2[s, e, r, i, t] for e in range(num_teachers) for r in range(num_rooms)
                            for t in st_valid_starting_slots[s][f'instrument_{i}'] if t in day_slot_ranges[d] and (s, e, r, i, t) in gy2 and t in tch_valid_starting_slots[e][f'instrument_{i}'])
                        <= 1
                    )

                    model.Add(
                        sum(gz[s, e, r, i, t] for e in range(num_teachers) for r in range(num_rooms)
                            for t in st_valid_starting_slots[s][f'instrument_{i}'] if t in day_slot_ranges[d] and (s, e, r, i, t) in gz and t in tch_valid_starting_slots[e][f'instrument_{i}']) +
                        sum(gz2[s, e, r, i, t] for e in range(num_teachers) for r in range(num_rooms)
                            for t in st_valid_starting_slots[s][f'instrument_{i}'] if t in day_slot_ranges[d] and (s, e, r, i, t) in gz2 and t in tch_valid_starting_slots[e][f'instrument_{i}'])
                        <= 1
                    )

    return model, gx, gx2, gy, gy2, gz, gz2

def contract(model, gx, gx2, gy, gy2, gz, gz2, teacher_info, courses, instruments, num_teachers, num_courses, num_slots, num_instruments, num_students, num_rooms):
    for e in range(num_teachers):
        teacher_info['contract'] = teacher_info['contract'].apply(safe_eval)
        max_weekly_minutes = int(teacher_info.iloc[e]['contract'][0] / 15)

        total_teaching_minutes = []

        # Sum all courses assigned to this teacher
        for c in range(num_courses):
            duration = int(courses.iloc[c]["course_duration_minutes_per_session"] / 15)  # Convert to slot duration
            
            total_course_assignments = sum(
                (gx[s, e, r, c, t] if (s, e, r, c, t) in gx else 0) +
                (gx2[s, e, r, c, t] if (s, e, r, c, t) in gx2 else 0)
                for s in range(num_students) for r in range(num_rooms) for t in range(num_slots)
            )

            total_teaching_minutes.append(total_course_assignments * duration)

        # Sum all instruments assigned to this teacher
        for i in range(num_instruments):
            duration = int(instruments.iloc[i]["instrument_duration_minutes_per_session"] / 15)  # Convert to slot duration
            
            total_instrument_assignments = sum(
                (gy[s, e, r, i, t] if (s, e, r, i, t) in gy else 0) +
                (gy2[s, e, r, i, t] if (s, e, r, i, t) in gy2 else 0) +
                (gz[s, e, r, i, t] if (s, e, r, i, t) in gz else 0) +
                (gz2[s, e, r, i, t] if (s, e, r, i, t) in gz2 else 0)
                for s in range(num_students) for r in range(num_rooms) for t in range(num_slots)
            )

            total_teaching_minutes.append(total_instrument_assignments * duration)

        # Constraint: Total assigned minutes for teacher `e` ≤ max weekly minutes
        print(max_weekly_minutes)
        model.Add(sum(total_teaching_minutes) <= max_weekly_minutes)

    return model, gx, gx2, gy, gy2, gz, gz2

def features(model, gx, gx2, gy, gy2, gz, gz2, courses, instruments, rooms, num_rooms, num_courses, num_instruments, num_slots, num_students, num_teachers):
    feature_cols = [601, 602, 603, 604, 605, 606, 607, 608, 609]  # integers, not strings

    for r in range(num_rooms):
        for feature in feature_cols:
            room_has_feature = rooms.iloc[r][feature]  # Binary: 1 if room has the feature, 0 if not
            
            # Ensure all assigned courses match the room features
            for c in range(num_courses):
                course_needs_feature = courses.iloc[c][feature]  # Binary: 1 if course requires feature
                if course_needs_feature == 1:
                    for s in range(num_students):
                        for e in range(num_teachers):
                            for t in range(num_slots):
                                if (s, e, r, c, t) in gx:
                                    model.Add(gx[s, e, r, c, t] <= room_has_feature)
                                if (s, e, r, c, t) in gx2:
                                    model.Add(gx2[s, e, r, c, t] <= room_has_feature)

            # Ensure all assigned instrument classes match the room features
            for i in range(num_instruments):
                instrument_needs_feature = instruments.iloc[i][feature]  # Binary: 1 if instrument requires feature
                if instrument_needs_feature == 1:
                    for s in range(num_students):
                        for e in range(num_teachers):
                            for t in range(num_slots):
                                if (s, e, r, i, t) in gy:
                                    model.Add(gy[s, e, r, i, t] <= room_has_feature)
                                if (s, e, r, i, t) in gy2:
                                    model.Add(gy2[s, e, r, i, t] <= room_has_feature)
                                if (s, e, r, i, t) in gz:
                                    model.Add(gz[s, e, r, i, t] <= room_has_feature)
                                if (s, e, r, i, t) in gz2:
                                    model.Add(gz2[s, e, r, i, t] <= room_has_feature)

    return model, gx, gx2, gy, gy2, gz, gz2

def class_capacity(model, gx, gx2, gy, gy2, gz, gz2, courses, instruments, num_teachers, num_rooms, num_students, num_courses, num_instruments, num_slots):
    ''' I have not tested throughly this constraint given that i am currently using an oversimplified test database to
    minimize running time, hence why I cannnot guarantee the successful implementation of the class_capacity constraint. '''
    # Ensure no course class exceeds its max student capacity
    for c in range(num_courses):
        max_students = int(courses.iloc[c]["course_capacity"])  # Get course capacity
        
        for t in range(num_slots):
            model.Add(
                sum(gx[s, e, r, c, t] for s in range(num_students) for e in range(num_teachers) for r in range(num_rooms) if (s, e, r, c, t) in gx) +
                sum(gx2[s, e, r, c, t] for s in range(num_students) for e in range(num_teachers) for r in range(num_rooms) if (s, e, r, c, t) in gx2)
                <= max_students
            )

    # Ensure no instrument class exceeds its max student capacity
    for i in range(num_instruments):
        max_students = int(instruments.iloc[i]["instrument_capacity"])  # Get instrument capacity
        
        for t in range(num_slots):
            model.Add(
                sum(gy[s, e, r, i, t] for s in range(num_students) for e in range(num_teachers) for r in range(num_rooms) if (s, e, r, i, t) in gy) +
                sum(gy2[s, e, r, i, t] for s in range(num_students) for e in range(num_teachers) for r in range(num_rooms) if (s, e, r, i, t) in gy2) +
                sum(gz[s, e, r, i, t] for s in range(num_students) for e in range(num_teachers) for r in range(num_rooms) if (s, e, r, i, t) in gz) +
                sum(gz2[s, e, r, i, t] for s in range(num_students) for e in range(num_teachers) for r in range(num_rooms) if (s, e, r, i, t) in gz2)
                <= max_students
            )

    return model, gx, gx2, gy, gy2, gz, gz2

def antiquity_soft(model, gx, gx2, gy, gy2, gz, gz2, student_availability, antiquity, courses, instruments, num_students, num_courses, num_slots, num_instruments, num_teachers, num_rooms):
    students_with_antiquity = antique_students(student_availability, antiquity)
    # antique_students should ONLY give a list of students with antiquity; i say this because antiquity has everyone,
    # but if someone has all 0 should not be included in antique_students so to not add an unavoidable day penalty
    print(students_with_antiquity)

    # Define the time slot ranges for each day
    day_slot_ranges = {
        0: range(0, 20),    # Monday
        1: range(20, 40),   # Tuesday
        2: range(40, 60),   # Wednesday
        3: range(60, 80),   # Thursday
        4: range(80, 99),   # Friday  
    }

    first_class_time_var = {}
    deviation_var = {}

    day_penalties = {}
    deviation_penalties = {} 

    for s, (_, row) in enumerate(antiquity.iterrows()):  
        if (row == 0).all():  # Check if all values in the row are 0
            continue
        else:
            student_id = list(students_with_antiquity.keys())[s]
            for d, start_t in students_with_antiquity[student_id]:
                if start_t == "none":
                    # Day mismatch penalty
                    day_penalties[(s, d)] = model.NewBoolVar(f'penalty_{s}_{d}')
                    
                    scheduled_any = []
                    for t in day_slot_ranges[d]:
                        for c in range(num_courses):
                            for e in range(num_teachers):
                                for r in range(num_rooms):
                                    if (s, e, r, c, t) in gx:
                                        scheduled_any.append(gx.get((s, e, r, c, t), 0))
                                    if (s, e, r, c, t) in gx2:
                                        scheduled_any.append(gx2.get((s, e, r, c, t), 0))
                        for i in range(num_instruments):
                            for e in range(num_teachers):
                                for r in range(num_rooms):
                                    if (s, e, r, i, t) in gy:
                                        scheduled_any.append(gy.get((s, e, r, i, t), 0))
                                    if (s, e, r, i, t) in gy2:
                                        scheduled_any.append(gy2.get((s, e, r, i, t), 0))
                                    if (s, e, r, i, t) in gz:
                                        scheduled_any.append(gz.get((s, e, r, i, t), 0))
                                    if (s, e, r, i, t) in gz2:
                                        scheduled_any.append(gz2.get((s, e, r, i, t), 0))

                    # Penalize if any class is scheduled on this day
                    model.AddBoolOr(scheduled_any).OnlyEnforceIf(day_penalties[(s, d)])

                    # No penalty if no class is scheduled on this day
                    model.Add(sum(scheduled_any) == 0).OnlyEnforceIf(day_penalties[(s, d)].Not())
                    
                else:  # Time deviation penalty
                    antique_time_index = antiquity.columns.get_loc(f'{["MON", "TUE", "WED", "THU", "FRI"][d]} {start_t}')
                    print(f'antique_time_index is {antique_time_index}')

                    deviation_penalties[(s, d)] = model.NewBoolVar(f'deviation_penalty_{s}_{d}')

                    # Find the earliest scheduled time slot
                    first_class_time_var = model.NewIntVar(0, num_slots - 1, f'first_class_time_{s}_{d}')
                    
                    scheduled_times = []
                    
                    for t in day_slot_ranges[d]:
                        for c in range(num_courses):
                            for e in range(num_teachers):
                                for r in range(num_rooms):
                                    if (s, e, r, c, t) in gx:
                                        scheduled_times.append(t * gx[(s, e, r, c, t)])
                                    if (s, e, r, c, t) in gx2:
                                        scheduled_times.append(t * gx2[(s, e, r, c, t)])
                        for i in range(num_instruments):
                            for e in range(num_teachers):
                                for r in range(num_rooms):
                                    if (s, e, r, i, t) in gy:
                                        scheduled_times.append(t * gy[(s, e, r, i, t)])
                                    if (s, e, r, i, t) in gy2:
                                        scheduled_times.append(t * gy2[(s, e, r, i, t)])
                                    if (s, e, r, i, t) in gz:
                                        scheduled_times.append(t * gz[(s, e, r, i, t)])
                                    if (s, e, r, i, t) in gz2:
                                        scheduled_times.append(t * gz2[(s, e, r, i, t)])

                    # Ensure first_class_time_var is set correctly
                    if scheduled_times:
                        # Define a large value (upper bound for num_slots)
                        max_slot = num_slots - 1

                        # Create a new auxiliary variable to hold the minimum valid (nonzero) scheduled time
                        first_class_time_var = model.NewIntVar(0, max_slot, f'first_class_time_{s}_{d}')
                        
                        # Use an auxiliary list that will be forced to contain only valid times
                        valid_times = []

                        for t in day_slot_ranges[d]:
                            for c in range(num_courses):
                                for e in range(num_teachers):
                                    for r in range(num_rooms):
                                        if (s, e, r, c, t) in gx:
                                            valid_times.append(model.NewIntVar(0, max_slot, f'valid_time_{s}_{d}_{t}'))
                                            model.Add(valid_times[-1] == t).OnlyEnforceIf(gx[(s, e, r, c, t)])
                                            model.Add(valid_times[-1] == max_slot).OnlyEnforceIf(gx[(s, e, r, c, t)].Not())

                                        if (s, e, r, c, t) in gx2:
                                            valid_times.append(model.NewIntVar(0, max_slot, f'valid_time_{s}_{d}_{t}'))
                                            model.Add(valid_times[-1] == t).OnlyEnforceIf(gx2[(s, e, r, c, t)])
                                            model.Add(valid_times[-1] == max_slot).OnlyEnforceIf(gx2[(s, e, r, c, t)].Not())

                            for i in range(num_instruments):
                                for e in range(num_teachers):
                                    for r in range(num_rooms):
                                        if (s, e, r, i, t) in gy:
                                            valid_times.append(model.NewIntVar(0, max_slot, f'valid_time_{s}_{d}_{t}'))
                                            model.Add(valid_times[-1] == t).OnlyEnforceIf(gy[(s, e, r, i, t)])
                                            model.Add(valid_times[-1] == max_slot).OnlyEnforceIf(gy[(s, e, r, i, t)].Not())

                                        if (s, e, r, i, t) in gy2:
                                            valid_times.append(model.NewIntVar(0, max_slot, f'valid_time_{s}_{d}_{t}'))
                                            model.Add(valid_times[-1] == t).OnlyEnforceIf(gy2[(s, e, r, i, t)])
                                            model.Add(valid_times[-1] == max_slot).OnlyEnforceIf(gy2[(s, e, r, i, t)].Not())

                                        if (s, e, r, i, t) in gz:
                                            valid_times.append(model.NewIntVar(0, max_slot, f'valid_time_{s}_{d}_{t}'))
                                            model.Add(valid_times[-1] == t).OnlyEnforceIf(gz[(s, e, r, i, t)])
                                            model.Add(valid_times[-1] == max_slot).OnlyEnforceIf(gz[(s, e, r, i, t)].Not())

                                        if (s, e, r, i, t) in gz2:
                                            valid_times.append(model.NewIntVar(0, max_slot, f'valid_time_{s}_{d}_{t}'))
                                            model.Add(valid_times[-1] == t).OnlyEnforceIf(gz2[(s, e, r, i, t)])
                                            model.Add(valid_times[-1] == max_slot).OnlyEnforceIf(gz2[(s, e, r, i, t)].Not())

                        if valid_times:
                            model.AddMinEquality(first_class_time_var, valid_times)
                        else:
                            model.Add(first_class_time_var == max_slot)  # Default to max if no valid times exist

                        # Deviation calculations
                        deviation_var = model.NewIntVar(0, max_slot, f'deviation_{s}_{d}')
                        model.AddAbsEquality(deviation_var, first_class_time_var - antique_time_index)

                        # Penalize if deviation is greater than 3 slots
                        model.Add(deviation_var > 3).OnlyEnforceIf(deviation_penalties[(s, d)])
                        model.Add(deviation_var <= 3).OnlyEnforceIf(deviation_penalties[(s, d)].Not())

                    else:
                        deviation_penalties[(s, d)] = 0

    return model, gx, gx2, gy, gy2, gz, gz2, students_with_antiquity, day_penalties, deviation_penalties, first_class_time_var, deviation_var, students_with_antiquity


def siblings_soft (model, gx, gx2, gy, gy2, gz, gz2, siblings_df, courses, instruments, num_students, num_courses, num_slots, num_instruments, num_teachers, num_rooms):
    siblings = create_sibling_groups(siblings_df)

    # Initialize to avoid possible UnboundLocalError errors
    sibling_day_vars = []
    mismatch_vars = []

    day_slot_ranges = {
        0: range(0, 20),    # Monday
        1: range(20, 40),   # Tuesday
        2: range(40, 60),   # Wednesday
        3: range(60, 80),   # Thursday
        4: range(80, 99),   # Friday  
    }

    sibling_day_penalties = {}
    
    for group in siblings:
        sibling_day_vars = {s: [] for s in group}
        
        for d in range(5):  # Iterate over days
            for s in group:
                has_class = model.NewBoolVar(f'sibling_{s}_day_{d}')
                model.AddBoolOr([
                    gx[s, e, r, c, t] for e in range(num_teachers) for r in range(num_rooms) for c in range(num_courses) for t in day_slot_ranges[d] if (s, e, r, c, t) in gx
                ] + [
                    gx2[s, e, r, c, t] for e in range(num_teachers) for r in range(num_rooms) for c in range(num_courses) for t in day_slot_ranges[d] if (s, e, r, c, t) in gx2
                ] + [
                    gy[s, e, r, i, t] for e in range(num_teachers) for r in range(num_rooms) for i in range(num_instruments) for t in day_slot_ranges[d] if (s, e, r, i, t) in gy
                ] + [
                    gy2[s, e, r, i, t] for e in range(num_teachers) for r in range(num_rooms) for i in range(num_instruments) for t in day_slot_ranges[d] if (s, e, r, i, t) in gy2
                ] + [
                    gz[s, e, r, i, t] for e in range(num_teachers) for r in range(num_rooms) for i in range(num_instruments) for t in day_slot_ranges[d] if (s, e, r, i, t) in gz
                ] + [
                    gz2[s, e, r, i, t] for e in range(num_teachers) for r in range(num_rooms) for i in range(num_instruments) for t in day_slot_ranges[d] if (s, e, r, i, t) in gz2
                ]).OnlyEnforceIf(has_class)
                model.Add(sum([
                    gx[s, e, r, c, t] for e in range(num_teachers) for r in range(num_rooms) for c in range(num_courses) for t in day_slot_ranges[d] if (s, e, r, c, t) in gx
                ] + [
                    gx2[s, e, r, c, t] for e in range(num_teachers) for r in range(num_rooms) for c in range(num_courses) for t in day_slot_ranges[d] if (s, e, r, c, t) in gx2
                ] + [
                    gy[s, e, r, i, t] for e in range(num_teachers) for r in range(num_rooms) for i in range(num_instruments) for t in day_slot_ranges[d] if (s, e, r, i, t) in gy
                ] + [
                    gy2[s, e, r, i, t] for e in range(num_teachers) for r in range(num_rooms) for i in range(num_instruments) for t in day_slot_ranges[d] if (s, e, r, i, t) in gy2
                ] + [
                    gz[s, e, r, i, t] for e in range(num_teachers) for r in range(num_rooms) for i in range(num_instruments) for t in day_slot_ranges[d] if (s, e, r, i, t) in gz
                ] + [
                    gz2[s, e, r, i, t] for e in range(num_teachers) for r in range(num_rooms) for i in range(num_instruments) for t in day_slot_ranges[d] if (s, e, r, i, t) in gz2
                ]) == 0).OnlyEnforceIf(has_class.Not())
                
                sibling_day_vars[s].append(has_class)
        
        # Compute penalties for mismatched days
        for d in range(5):
            mismatch_vars = []  # Store all mismatches for the day
            for i in range(len(group) - 1):
                for j in range(i + 1, len(group)):
                    mismatch = model.NewBoolVar(f"mismatch_s{group[i]}_s{group[j]}_day_{d}")

                    # Enforce mismatch correctly by setting mismatch to 1 when they differ
                    model.Add(
                        sibling_day_vars[group[i]][d] + sibling_day_vars[group[j]][d] == 1
                    ).OnlyEnforceIf(mismatch)
                    
                    # Ensure that mismatch is 0 when both are the same
                    model.Add(
                        sibling_day_vars[group[i]][d] == sibling_day_vars[group[j]][d]
                    ).OnlyEnforceIf(mismatch.Not())

                    mismatch_vars.append(mismatch)  # Store mismatch vars

            # Sum all mismatches for the day
            if mismatch_vars:
                day_mismatch_penalty = model.NewIntVar(0, len(mismatch_vars), f"day_mismatch_penalty_{d}_{group}")
                model.Add(day_mismatch_penalty == sum(mismatch_vars))
                sibling_day_penalties[group, d] = day_mismatch_penalty
    
    total_sibling_penalty = model.NewIntVar(0, len(sibling_day_penalties) * 5, "total_sibling_penalty")
    model.Add(total_sibling_penalty == sum(sibling_day_penalties.values()))

    return model, gx, gx2, gy, gy2, gz, gz2, siblings, total_sibling_penalty, sibling_day_penalties, siblings, sibling_day_vars, mismatch_vars