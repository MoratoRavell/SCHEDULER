import psycopg2
import pandas as pd
import numpy as np
import json
from datetime import datetime, timedelta

# Database connection
def connect_to_db():
    return psycopg2.connect(
        dbname="scheduling_app",
        user="postgres",
        password="221214",
        host="localhost",
        port="5432"
    )

# Generate time slots for the matrix (same as for students)
def generate_time_slots():
    times = [f"{hour:02d}:{minute:02d}" for hour in range(16, 21) for minute in [0, 15, 30, 45]]
    days = ['MON', 'TUE', 'WED', 'THU', 'FRI']
    return [f"{day} {time}" for day in days for time in times]

# Convert a time range string to a list of 15-minute intervals (same as for students)
def time_range_to_slots(day, start_time, end_time, time_slots):
    start = datetime.strptime(start_time, "%H:%M")
    end = datetime.strptime(end_time, "%H:%M")
    current = start
    intervals = []
    while current < end:
        intervals.append(current.strftime("%H:%M"))
        current += timedelta(minutes=15)
    return [f"{day.upper()} {time}" for time in intervals if f"{day.upper()} {time}" in time_slots]

# Process availability JSON and convert to a binary row
def process_availability(teacher_availability, time_slots):
    availability_row = [0] * len(time_slots)
    for entry in teacher_availability:
        day, time_range = entry
        start_time, end_time = time_range.split('-')
        slots = time_range_to_slots(day, start_time, end_time, time_slots)
        for slot in slots:
            if slot in time_slots:
                availability_row[time_slots.index(slot)] = 1
    return availability_row

# Create the availability matrix for teachers
def create_availability_matrix(teachers, time_slots):
    matrix = []
    for _, teacher in teachers.iterrows():
        availability_row = process_availability(teacher['availability'], time_slots)
        matrix.append([teacher['teacher_id']] + availability_row)
    return np.array(matrix)

# Convert courses and instruments to binary matrices
def process_teacher_details(teachers, courses, instruments, course_mapping, instrument_mapping):
    teacher_data = []

    for _, teacher in teachers.iterrows():
        teacher_id = teacher['teacher_id']
        contract = teacher['contract']
        
        # Create binary columns for courses with IDs
        courses_row = [1 if course in teacher['courses'] else 0 for course in courses]
        
        # Create binary columns for instruments with IDs
        instruments_row = [1 if instrument in teacher['instruments'] else 0 for instrument in instruments]
        
        teacher_data.append([teacher_id, contract] + courses_row + instruments_row)

    # Replace column names with course and instrument IDs
    columns = ['teacher_id', 'contract'] + \
              [f'course_{course_mapping[course]}' for course in courses] + \
              [f'instrument_{instrument_mapping[instrument]}' for instrument in instruments]
    
    return pd.DataFrame(teacher_data, columns=columns)

# Preprocess teacher data
def preprocess_teachers(user_id):
    conn = connect_to_db()

    query = """
        SELECT teacher_id, name, availability, contract, courses, instruments
        FROM teachers
        WHERE user_id = %s AND solution_id = %s
        ORDER BY teacher_id
    """
    teachers = pd.read_sql_query(query, conn, params=(user_id, 'temp_sol'))

    conn.close()
    
    # Convert JSONB columns to Python lists
    for field in ['availability', 'contract', 'courses', 'instruments']:
        teachers[field] = teachers[field].apply(lambda x: json.loads(x) if isinstance(x, str) else x)
    
    # Generate time slots
    time_slots = generate_time_slots()
    
    # Create and save availability matrix
    availability_matrix = create_availability_matrix(teachers, time_slots)
    availability_df = pd.DataFrame(availability_matrix, columns=['teacher_id'] + time_slots)
    #availability_df.to_csv("teacher_availability_matrix.csv", index=False)
    
    # Course and instrument mappings
    course_mapping = {
        "music theory 1": 401,
        "music theory 2": 402,
        "music theory 3": 403,
        "choir": 404
    }
    
    instrument_mapping = {
        "guitar": 501,
        "piano": 502,
        "drums": 503,
        "violin": 504,
        "flute": 505,
        "clarinet": 506,
        "cello": 507,
        "trumpet": 508
    }
    
    # Courses and instruments list
    courses = ["music theory 1", "music theory 2", "music theory 3", "choir"]
    instruments = ["guitar", "piano", "drums", "violin", "flute", "clarinet", "cello", "trumpet"]
    
    # Create and save teacher details binary matrix with ID mappings
    teacher_details_matrix = process_teacher_details(teachers, courses, instruments, course_mapping, instrument_mapping)
    #teacher_details_matrix.to_csv("teacher_details_matrix.csv", index=False)

    return availability_df, teacher_details_matrix

def generate_teacher_index_csv(user_id):
    conn = connect_to_db()

    query = """
        SELECT teacher_id, name
        FROM teachers
        WHERE user_id = %s AND solution_id = %s
        ORDER BY teacher_id
    """
    teacher_index_mapping = pd.read_sql_query(query, conn, params=(user_id, 'temp_sol'))

    conn.close()
    
    # Add index column
    teacher_index_mapping.insert(0, 'index', range(len(teacher_index_mapping)))
    
    # Save to CSV
    #teacher_index_mapping.to_csv("teacher_index_mapping.csv", index=False)
    
    return teacher_index_mapping

    
# Run preprocessing
#if __name__ == "__main__":
def load_teachers_data(user_id):
    availability_df, teacher_details_matrix = preprocess_teachers(user_id)
    teacher_index_mapping = generate_teacher_index_csv(user_id)
    return availability_df, teacher_details_matrix, teacher_index_mapping
