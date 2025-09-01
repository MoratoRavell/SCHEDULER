# |||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
# ||||||||||||||||||||||||||||||||||||||||||||||||||||||||| SCHEDULER: Model Body |||||||||||||||||||||||||||||||||||||||||||||||||||||||||
# |||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||


# |||||||||| IMPORT LIBRARIES |||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
from ortools.sat.python import cp_model
import pandas as pd
import math
import os
import logging
import ast
import time
import json
import psycopg2


# |||||||||| IMPORT FUNCTIONS ||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
import constraints as cns

from preprocess_school import load_school_data
from preprocess_students import load_students_data
from preprocess_teachers import load_teachers_data

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


# |||||||||| LOAD PREPROCESSED DATA |||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
def load_data(user_id):
    rooms, courses, instruments, course_index_mapping, instrument_index_mapping, room_index_mapping = load_school_data(user_id)
    teacher_availability, teacher_info, teacher_index_mapping = load_teachers_data(user_id)
    student_availability, antiquity, priorities, siblings_df, course_continuity, student_index_mapping = load_students_data(user_id)
    # Print all variables
    print("courses:", courses)
    print("instruments:", instruments)
    print("rooms:", rooms)
    print("course_index_mapping:", course_index_mapping)
    print("instrument_index_mapping:", instrument_index_mapping)
    print("room_index_mapping:", room_index_mapping)

    print("teacher_availability:", teacher_availability)
    print("teacher_info:", teacher_info)
    print("teacher_index_mapping:", teacher_index_mapping)

    print("student_availability:", student_availability)
    print("antiquity:", antiquity)
    print("priorities:", priorities)
    print("siblings_df:", siblings_df)
    print("course_continuity:", course_continuity)
    print("student_index_mapping:", student_index_mapping)

    ''' Function used for loading all preprocessed data. As of now, json files populate an SQL database, which then is used to
    generate the following .csv files containing preprocess data generated in the preprocessing scripts. This is done this way to
    simulate the extraction of forms data and storing of the same in a database. In the future, the .csv file creation step could be
    eliminated, directly preprocessing the extracted SQL data in the same "main" workflow. '''

    # For easier debugging, using '.iloc[:n]' we limit the amount of students, teachers or rooms that we work with.

    #student_availability = pd.read_csv('student_availability_matrix.csv', index_col=0).iloc[:3]
    #antiquity = pd.read_csv('student_antiquity_matrix.csv', index_col=0).iloc[:3]
    #priorities = pd.read_csv('student_priority_matrix.csv', index_col=0).iloc[:3]
    #siblings_df = pd.read_csv('student_sibling_table.csv', index_col=0).iloc[:3]
    #course_continuity = pd.read_csv('course_antiquity_table.csv', index_col=0).iloc[:3]
    #teacher_availability = pd.read_csv('teacher_availability_matrix.csv', index_col=0).iloc[:1]
    #teacher_info = pd.read_csv('teacher_details_matrix.csv', index_col=0).iloc[:1]
    #courses = pd.read_csv('courses_matrix.csv', index_col=0)
    #instruments = pd.read_csv('instruments_matrix.csv', index_col=0)
    #rooms = pd.read_csv('rooms_matrix.csv', index_col=0).iloc[:1]

    # Slicing for debugging
    student_availability = student_availability.iloc[:15]
    antiquity = antiquity.iloc[:15]
    priorities = priorities.iloc[:15]
    siblings_df = siblings_df.iloc[:15]
    course_continuity = course_continuity.iloc[:15]
    teacher_availability = teacher_availability.iloc[:2]
    teacher_info = teacher_info.iloc[:2]
    rooms = rooms.iloc[:2]

    conn = connect_to_db()
    cursor = conn.cursor()

    # Delete existing rows for this user and solution in each mapping table before inserting
    cursor.execute("DELETE FROM room_index_mapping WHERE user_id = %s AND solution_id = %s", (user_id, 'temp_sol'))
    cursor.execute("DELETE FROM course_index_mapping WHERE user_id = %s AND solution_id = %s", (user_id, 'temp_sol'))
    cursor.execute("DELETE FROM instrument_index_mapping WHERE user_id = %s AND solution_id = %s", (user_id, 'temp_sol'))
    cursor.execute("DELETE FROM student_index_mapping WHERE user_id = %s AND solution_id = %s", (user_id, 'temp_sol'))
    cursor.execute("DELETE FROM teacher_index_mapping WHERE user_id = %s AND solution_id = %s", (user_id, 'temp_sol'))

    for _, row in room_index_mapping.iterrows():
        cursor.execute("""
            INSERT INTO room_index_mapping (index, user_id, solution_id, room_id, name)
            VALUES (%s, %s, %s, %s, %s)
        """, (row['index'], user_id, 'temp_sol', row['room_id'], row['name']))

    for _, row in course_index_mapping.iterrows():
        cursor.execute("""
            INSERT INTO course_index_mapping (index, user_id, solution_id, course_id, name)
            VALUES (%s, %s, %s, %s, %s)
        """, (row['index'], user_id, 'temp_sol', row['course_id'], row['name']))

    for _, row in instrument_index_mapping.iterrows():
        cursor.execute("""
            INSERT INTO instrument_index_mapping (index, user_id, solution_id, instrument_id, name)
            VALUES (%s, %s, %s, %s, %s)
        """, (row['index'], user_id, 'temp_sol', row['instrument_id'], row['name']))

    for _, row in student_index_mapping.iterrows():
        cursor.execute("""
            INSERT INTO student_index_mapping (index, user_id, solution_id, student_id, name)
            VALUES (%s, %s, %s, %s, %s)
        """, (row['index'], user_id, 'temp_sol', row['student_id'], row['name']))

    for _, row in teacher_index_mapping.iterrows():
        cursor.execute("""
            INSERT INTO teacher_index_mapping (index, user_id, solution_id, teacher_id, name)
            VALUES (%s, %s, %s, %s, %s)
        """, (row['index'], user_id, 'temp_sol', row['teacher_id'], row['name']))

    conn.commit()
    cursor.close()
    conn.close()

    return student_availability, antiquity, priorities, siblings_df, teacher_availability, teacher_info, courses, instruments, rooms, course_continuity


# |||||||||| CREATE MODEL |||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
def create_model(student_availability, antiquity, priorities, siblings_df, teacher_availability, teacher_info, courses, instruments, rooms, course_continuity):
    ''' Function used to create the model, including variable, constraint and objective function definition. The model is later solved
    using the solve_model function. '''
    
    # Create a Constraint Problem optimization model
    model = cp_model.CpModel()

    num_students = student_availability.shape[0]
    num_teachers = teacher_availability.shape[0]
    num_slots = student_availability.shape[1] - 1
    num_courses = courses.shape[0]
    num_instruments = instruments.shape[0]
    num_rooms = rooms.shape[0]


    # |||||||||| DECISION VARIABLES |||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
    # Each of the following variables represents a different class type the model can assign
    # More variables are defined on the go, but they are only used to store penaly data to punish the model for not following certain constraints

    gx = {}  # Grouping decision variable for course assignments (s, e, r, c, t)
    gx2 = {}  # Grouping decision variable for biweekly course assignments (s, e, r, c, t)

    gy = {}  # Grouping decision variable for instrument assignments (s, e, r, i, t)
    gy2 = {}  # Grouping decision variable for biweekly instrument assignments (s, e, r, i, t)

    gz = {}  # Grouping decision variable for lower priority instrument assignments (s, e, r, i, t)
    gz2 = {}  # Grouping decision variable for biweekly lower priority instrument assignments (s, e, r, i, t)


    # |||||||||| CONSTRAINTS ||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
    print('START')
    model, gx, gx2, gy, gy2, gz, gz2 = cns.initialize_variables(model, gx, gx2, gy, gy2, gz, gz2, num_teachers, num_rooms, courses, instruments, num_students, num_courses, num_slots, num_instruments, student_availability, teacher_availability)
    print('initialization')
    model, gx, gx2, gy, gy2, gz, gz2, y_ins, z_ins, continuity, course_priorization = cns.continuity_and_priorization(model, gx, gx2, gy, gy2, gz, gz2, num_teachers, num_rooms, priorities, course_continuity, student_availability, courses, instruments, num_students, num_courses, num_slots, num_instruments)
    print('continuity')
    model, gx, gx2, gy, gy2, gz, gz2, st_valid_starting_slots, tch_valid_starting_slots = cns.student_class_duration(model, gx, gx2, gy, gy2, gz, gz2, num_teachers, num_rooms, student_availability, teacher_availability, courses, instruments, num_students, num_courses, num_slots, num_instruments)
    print('duration')
    model, gx, gx2, gy, gy2, gz, gz2 = cns.single_class_type(model, gx, gx2, gy, gy2, gz, gz2, priorities, student_availability, courses, instruments, num_teachers, num_rooms, num_students, num_courses, num_slots, num_instruments, y_ins, z_ins, continuity, course_priorization)
    print('type')
    warm_start_model, gx_w, gx2_w, gy_w, gy2_w, gz_w, gz2_w = model, gx, gx2, gy, gy2, gz, gz2  # Store the model and its variables before adding more constraints
    print('warm')
    model, gx, gx2, gy, gy2, gz, gz2 = cns.priority_assignment(model, gx, gx2, gy, gy2, gz, gz2, num_teachers, num_rooms, courses, instruments, num_students, num_courses, num_slots, num_instruments, st_valid_starting_slots, tch_valid_starting_slots)
    print('priority')
    model, gx, gx2, gy, gy2, gz, gz2 = cns.student_overlaps(model, gx, gx2, gy, gy2, gz, gz2, num_teachers, num_rooms, courses, instruments, num_students, num_courses, num_slots, num_instruments, st_valid_starting_slots, tch_valid_starting_slots)    
    # THE OVERLAPS CONSTRAINT IS EXTREMELY UNDEROPTIMIZED, BUT I AM PRETTY SURE IT WORKS AS EXPECTED AT LAST
    print('overlaps')
    model, gx, gx2, gy, gy2, gz, gz2 = cns.contract(model, gx, gx2, gy, gy2, gz, gz2, teacher_info, courses, instruments, num_teachers, num_courses, num_slots, num_instruments, num_students, num_rooms)
    print('contract')
    model, gx, gx2, gy, gy2, gz, gz2 = cns.features(model, gx, gx2, gy, gy2, gz, gz2, courses, instruments, rooms, num_rooms, num_courses, num_instruments, num_slots, num_students, num_teachers)
    print('features')
    model, gx, gx2, gy, gy2, gz, gz2 = cns.class_capacity(model, gx, gx2, gy, gy2, gz, gz2, courses, instruments, num_teachers, num_rooms, num_students, num_courses, num_instruments, num_slots)
    print('capacity')
    model, gx, gx2, gy, gy2, gz, gz2, students_with_antiquity, day_penalties, deviation_penalties, first_class_time_var, deviation_var, students_with_antiquity = cns.antiquity_soft(model, gx, gx2, gy, gy2, gz, gz2, student_availability, antiquity, courses, instruments, num_students, num_courses, num_slots, num_instruments, num_teachers, num_rooms)
    print('antiquity')
    model, gx, gx2, gy, gy2, gz, gz2, siblings, total_sibling_penalty, sibling_day_penalties, siblings, sibling_day_vars, mismatch_vars = cns.siblings_soft (model, gx, gx2, gy, gy2, gz, gz2, siblings_df, courses, instruments, num_students, num_courses, num_slots, num_instruments, num_teachers, num_rooms)
    print('siblings')
    print('FINISH')


    # |||||||||| OBJECTIVE FUNCTION ||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
    # Weights for the objective components
    assignment_weight = 10
    instrument_priority_penalty_weight = 7
    sibling_day_mismatch_weight = 4
    day_weight = 2
    deviation_weight = 1
    
    # Total successful assignments (courses and instruments)
    total_assignments = (
        sum(
            gx[s, e, r, c, t] for s in range(num_students)
            for e in range(num_teachers)
            for r in range(num_rooms)
            for c in range(num_courses)
            for t in range(num_slots)
            if (s, e, r, c, t) in gx and student_availability.iloc[s, t] == 1
        ) +
        sum(
            gx2[s, e, r, c, t] for s in range(num_students)
            for e in range(num_teachers)
            for r in range(num_rooms)
            for c in range(num_courses)
            for t in range(num_slots)
            if (s, e, r, c, t) in gx2 and student_availability.iloc[s, t] == 1
        ) +
        sum(
            gy[s, e, r, i, t] for s in range(num_students)
            for e in range(num_teachers)
            for r in range(num_rooms)
            for i in range(num_instruments)
            for t in range(num_slots)
            if (s, e, r, i, t) in gy and student_availability.iloc[s, t] == 1
        ) +
        sum(
            gy2[s, e, r, i, t] for s in range(num_students)
            for e in range(num_teachers)
            for r in range(num_rooms)
            for i in range(num_instruments)
            for t in range(num_slots)
            if (s, e, r, i, t) in gy2 and student_availability.iloc[s, t] == 1
        ) +
        sum(
            gz[s, e, r, i, t] for s in range(num_students)
            for e in range(num_teachers)
            for r in range(num_rooms)
            for i in range(num_instruments)
            for t in range(num_slots)
            if (s, e, r, i, t) in gz and student_availability.iloc[s, t] == 1
        ) +
        sum(
            gz2[s, e, r, i, t] for s in range(num_students)
            for e in range(num_teachers)
            for r in range(num_rooms)
            for i in range(num_instruments)
            for t in range(num_slots)
            if (s, e, r, i, t) in gz2 and student_availability.iloc[s, t] == 1
        )
    )

    # Total low-priority instrument assignment (z and z2) penalties according to instrument priorization
    total_instrument_priority_penalty = (
        sum(
            gz[s, e, r, i, t] for s in range(num_students)
            for e in range(num_teachers)
            for r in range(num_rooms)
            for i in range(num_instruments)
            for t in range(num_slots)
            if (s, e, r, i, t) in gz and student_availability.iloc[s, t] == 1
        ) +
        sum(
            gz2[s, e, r, i, t] for s in range(num_students)
            for e in range(num_teachers)
            for r in range(num_rooms)
            for i in range(num_instruments)
            for t in range(num_slots)
            if (s, e, r, i, t) in gz2 and student_availability.iloc[s, t] == 1
        )
    )

    # Total penalties for days when classes should not have been scheduled according to antiquity
    total_day_penalties = sum(
        day_penalties[(s, day)]
        for (s, day) in day_penalties
    )

    # Total deviation penalties for starting times according in matching days according to antiquity
    total_time_deviation_penalties = sum(
        deviation_penalties[(s, day)]
        for (s, day) in deviation_penalties
    )

    # Objective function: maximize assignments while minimizing penalties (maximizing student satisfaction)
    model.Maximize(
        assignment_weight * total_assignments
        - instrument_priority_penalty_weight * total_instrument_priority_penalty
        - day_weight * total_day_penalties
        - deviation_weight * total_time_deviation_penalties
        - sibling_day_mismatch_weight * total_sibling_penalty
    )

    return model, gx, gx2, gy, gy2, gz, gz2, num_students, num_teachers, num_rooms, num_courses, num_instruments, num_slots, day_penalties, deviation_penalties, sibling_day_penalties, warm_start_model, gx_w, gx2_w, gy_w, gy2_w, gz_w, gz2_w


# |||||||||| SOLVE MODEL ||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
class SolutionPrinter(cp_model.CpSolverSolutionCallback):
    def __init__(self, model, gx, gx2, gy, gy2, gz, gz2, num_students, num_teachers, num_rooms, num_courses, num_instruments, num_slots, day_penalties, deviation_penalties, sibling_day_penalties):
        super().__init__()
        self.gx = gx
        self.gx2 = gx2
        self.gy = gy
        self.gy2 = gy2
        self.gz = gz
        self.gz2 = gz2
        self.num_students = num_students
        self.num_teachers = num_teachers
        self.num_rooms = num_rooms
        self.num_courses = num_courses
        self.num_instruments = num_instruments
        self.num_slots = num_slots
        self.solution_count = 0  
        self.final_solution = []  # Store only the last solution

        # Time tracking
        self.start_time = time.time()  # Start time of solver
        self.last_improvement_time = self.start_time  # Last improvement time
        self.best_objective = float('inf')  # Track best objective value

    def OnSolutionCallback(self):
        """Called each time the solver finds a solution."""
        current_time = time.time()
        elapsed_time = current_time - self.start_time
        time_since_last_improvement = current_time - self.last_improvement_time

        # Get current objective value
        current_objective = self.ObjectiveValue()

        # Check if this solution is an improvement
        if current_objective < self.best_objective:
            self.best_objective = current_objective
            self.last_improvement_time = current_time  # Reset improvement timer
            print(f"New solution {self.solution_count+1}: Objective = {self.best_objective}, Time = {elapsed_time:.2f}s")

        # Stop if 100 seconds have passed without improvement
        if time_since_last_improvement > 100:
            print(f"Stopping solver after {elapsed_time:.2f}s (no improvement for 100s).")
            self.StopSearch()  # Immediately stop solver

        self.solution_count += 1
        print(f"\n--- Solution {self.solution_count} ---\n")

        # Overwrite previous solution
        self.final_solution = []

        # Print and store assigned courses
        for s in range(self.num_students):
            for e in range(self.num_teachers):
                for r in range(self.num_rooms):
                    for c in range(self.num_courses):
                        for t in range(self.num_slots):
                            if (s, e, r, c, t) in self.gx and self.Value(self.gx[s, e, r, c, t]) > 0:
                                print(f"Student {s}: Teacher {e}, Course {c}, Room {r}, Time Slot {t}")
                                self.final_solution.append([s, e, r, f"Course {c}", t])
                            if (s, e, r, c, t) in self.gx2 and self.Value(self.gx2[s, e, r, c, t]) > 0:
                                print(f"Student {s}: Teacher {e}, Course {c}, Room {r}, Time Slot {t}, SECOND")
                                self.final_solution.append([s, e, r, f"Course {c}", t])

        # Print and store assigned instruments
        for s in range(self.num_students):
            for e in range(self.num_teachers):
                for r in range(self.num_rooms):
                    for i in range(self.num_instruments):
                        for t in range(self.num_slots):
                            if (s, e, r, i, t) in self.gy and self.Value(self.gy[s, e, r, i, t]) > 0:
                                print(f"Student {s}: Teacher {e}, Instrument {i}, Room {r}, Time Slot {t}")
                                self.final_solution.append([s, e, r, f"Instrument {i}", t])
                            if (s, e, r, i, t) in self.gy2 and self.Value(self.gy2[s, e, r, i, t]) > 0:
                                print(f"Student {s}: Teacher {e}, Instrument {i}, Room {r}, Time Slot {t}, SECOND")
                                self.final_solution.append([s, e, r, f"Instrument {i}", t])
                            if (s, e, r, i, t) in self.gz and self.Value(self.gz[s, e, r, i, t]) > 0:
                                print(f"Student {s}: Teacher {e}, Instrument {i} (Low Priority), Room {r}, Time Slot {t}")
                                self.final_solution.append([s, e, r, f"Instrument {i}", t])
                            if (s, e, r, i, t) in self.gz2 and self.Value(self.gz2[s, e, r, i, t]) > 0:
                                print(f"Student {s}: Teacher {e}, Instrument {i}, Room {r}, Time Slot {t}, SECOND")
                                self.final_solution.append([s, e, r, f"Instrument {i}", t])

def solve_warm_start(warm_model, gx_w, gx2_w, gy_w, gy2_w, gz_w, gz2_w, student_availability, courses, instruments, num_students, num_teachers, num_rooms, num_slots, num_courses, num_instruments):
    assignment_weight = 10
    instrument_priority_penalty_weight = 4

    total_assignments = (
        sum(
            gx_w[s, e, r, c, t] for s in range(num_students)
            for e in range(num_teachers)
            for r in range(num_rooms)
            for c in range(num_courses)
            for t in range(num_slots)
            if (s, e, r, c, t) in gx_w and student_availability.iloc[s, t] == 1
        ) +
        sum(
            gx2_w[s, e, r, c, t] for s in range(num_students)
            for e in range(num_teachers)
            for r in range(num_rooms)
            for c in range(num_courses)
            for t in range(num_slots)
            if (s, e, r, c, t) in gx2_w and student_availability.iloc[s, t] == 1
        ) +
        sum(
            gy_w[s, e, r, i, t] for s in range(num_students)
            for e in range(num_teachers)
            for r in range(num_rooms)
            for i in range(num_instruments)
            for t in range(num_slots)
            if (s, e, r, i, t) in gy_w and student_availability.iloc[s, t] == 1
        ) +
        sum(
            gy2_w[s, e, r, i, t] for s in range(num_students)
            for e in range(num_teachers)
            for r in range(num_rooms)
            for i in range(num_instruments)
            for t in range(num_slots)
            if (s, e, r, i, t) in gy2_w and student_availability.iloc[s, t] == 1
        ) +
        sum(
            gz_w[s, e, r, i, t] for s in range(num_students)
            for e in range(num_teachers)
            for r in range(num_rooms)
            for i in range(num_instruments)
            for t in range(num_slots)
            if (s, e, r, i, t) in gz_w and student_availability.iloc[s, t] == 1
        ) +
        sum(
            gz2_w[s, e, r, i, t] for s in range(num_students)
            for e in range(num_teachers)
            for r in range(num_rooms)
            for i in range(num_instruments)
            for t in range(num_slots)
            if (s, e, r, i, t) in gz2_w and student_availability.iloc[s, t] == 1
        )
    )

    # Total low-priority instrument assignment (z and z2) penalties according to instrument priorization
    total_instrument_priority_penalty = (
        sum(
            gz_w[s, e, r, i, t] for s in range(num_students)
            for e in range(num_teachers)
            for r in range(num_rooms)
            for i in range(num_instruments)
            for t in range(num_slots)
            if (s, e, r, i, t) in gz_w and student_availability.iloc[s, t] == 1
        ) +
        sum(
            gz2_w[s, e, r, i, t] for s in range(num_students)
            for e in range(num_teachers)
            for r in range(num_rooms)
            for i in range(num_instruments)
            for t in range(num_slots)
            if (s, e, r, i, t) in gz2_w and student_availability.iloc[s, t] == 1
        )
    )

    warm_model.Maximize(
        assignment_weight * total_assignments
        - instrument_priority_penalty_weight * total_instrument_priority_penalty
    )

    warm_solver = cp_model.CpSolver()
    #warm_solver.parameters.max_time_in_seconds = 3.0  # Quick solve does not even allow for solver initiallization unfortunately
    warm_solver.parameters.log_search_progress = True
    warm_solver.parameters.enumerate_all_solutions = True
    
    warm_start_solution = {}

    # Solve the simplified model
    status = warm_solver.Solve(warm_model)

    if status in [cp_model.OPTIMAL, cp_model.FEASIBLE]:
        print("Warm start solution found!")
        for key in gx.keys():
            if warm_solver.Value(gx_w[key]) > 0:
                warm_start_solution[key] = 1  # Store assigned variables
        for key in gx2.keys():
            if warm_solver.Value(gx2_w[key]) > 0:
                warm_start_solution[key] = 1
        for key in gy.keys():
            if warm_solver.Value(gy_w[key]) > 0:
                warm_start_solution[key] = 1
        for key in gy2.keys():
            if warm_solver.Value(gy2_w[key]) > 0:
                warm_start_solution[key] = 1
        for key in gz.keys():
            if warm_solver.Value(gz_w[key]) > 0:
                warm_start_solution[key] = 1
        for key in gz2.keys():
            if warm_solver.Value(gz2_w[key]) > 0:
                warm_start_solution[key] = 1

    return warm_start_solution

def solve_model(model, gx, gx2, gy, gy2, gz, gz2, num_students, num_teachers, num_rooms, num_courses, num_instruments, num_slots, day_penalties, deviation_penalties, sibling_day_penalties, warm_start_solution, student_availability):
    print('----------STARTING SOLVER----------')

    solver = cp_model.CpSolver()

    solver.parameters.log_search_progress = True

    solver.parameters.enumerate_all_solutions = False

    solver.parameters.symmetry_level = 0
    #solver.parameters.relative_gap_limit = 0.5  # Stop if within 5% of best known solution CHANGE OR REMOVE IN THE FUTURE
    solver.parameters.num_search_workers = 8  # Use multiple threads
    #solver.parameters.random_seed = 42  # Randomize search direction slightly
    #solver.parameters.max_time_in_seconds = 300  # Allow more search time to refine the solution

    print('printing warm start solution:')
    print(warm_start_solution)
    if warm_start_solution:
        partial_hint_keys = list(warm_start_solution.keys())[:len(warm_start_solution) // 2]  # Only hint at half of the variables
        partial_hint_values = [warm_start_solution[key] for key in partial_hint_keys]

        solver.SetHint(partial_hint_keys, partial_hint_values)

    # Create the callback instance
    solution_printer = SolutionPrinter(model, gx, gx2, gy, gy2, gz, gz2, num_students, num_teachers, num_rooms, num_courses, num_instruments, num_slots,
                                       day_penalties, deviation_penalties, sibling_day_penalties)

    # Solve with callback
    status = solver.SolveWithSolutionCallback(model, solution_printer)

    if status in [cp_model.OPTIMAL, cp_model.FEASIBLE]:
        print("\nSolution found.")
            
        # Save the final solution
        df = pd.DataFrame(solution_printer.final_solution, columns=["STUDENT", "TEACHER", "ROOM", "CLASS", "START TIME"])
        df.to_csv("schedule_solution.csv", index=False)
        solution_df = df
        print("\nFinal solution saved to schedule_solution.csv")

        students_with_priority_penalty = set()

        for s in range(num_students):
            for e in range(num_teachers):
                for r in range(num_rooms):
                    for i in range(num_instruments):
                        for t in range(num_slots):
                            if (s, e, r, i, t) in gz and solution_printer.Value(gz[s, e, r, i, t]) > 0 and student_availability.iloc[s, t] == 1:
                                students_with_priority_penalty.add(s)
                            if (s, e, r, i, t) in gz2 and solution_printer.Value(gz2[s, e, r, i, t]) > 0 and student_availability.iloc[s, t] == 1:
                                students_with_priority_penalty.add(s)

        # Store penalties (ONLY for the final solution)
        penalties_data = []

        for s in students_with_priority_penalty:
            penalties_data.append([s, "INSTRUMENT PRIORITIZATION"])

        for (s, _), var in day_penalties.items():  # Ignore day (d)
            if solution_printer.Value(var) > 0:
                penalties_data.append([s, "ANTIQUITY DAY"])

        for (s, _), var in deviation_penalties.items():  # Ignore day (d)
            if solution_printer.Value(var) > 0:
                penalties_data.append([s, "ANTIQUITY DEVIATION"])

        for (group, _), penalty_var in sibling_day_penalties.items():  # Ignore day (d)
            if solution_printer.Value(penalty_var) > 0:
                for s in group:
                    penalties_data.append([s, "SIBLING MISMATCH"])

        # Save penalties data to CSV (without the "DAY" column)
        penalties_df = pd.DataFrame(penalties_data, columns=["STUDENT", "PENALTY TYPE"])
        penalties_df.to_csv("schedule_penalties.csv", index=False)
        print("\nPenalties saved to penalties.csv")

    else:
        print("\nNo solution found.")

    print('----------FINISHED SOLVING----------')

    return solution_df, penalties_df
