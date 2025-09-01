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

# Generate time slots for the matrix
def generate_time_slots():
    times = [f"{hour:02d}:{minute:02d}" for hour in range(16, 21) for minute in [0, 15, 30, 45]]
    days = ['MON', 'TUE', 'WED', 'THU', 'FRI']
    return [f"{day} {time}" for day in days for time in times]

# Convert a time range string to a list of 15-minute intervals
def time_range_to_slots(day, start_time, end_time, time_slots):
    start = datetime.strptime(start_time, "%H:%M")
    end = datetime.strptime(end_time, "%H:%M")
    current = start
    intervals = []
    while current < end:
        intervals.append(current.strftime("%H:%M"))
        current += timedelta(minutes=15)
    return [f"{day.upper()} {time}" for time in intervals if f"{day.upper()} {time}" in time_slots]

# Process availability JSONB and convert to a binary row
def process_availability(student_availability, time_slots):
    availability_row = [0] * len(time_slots)
    for entry in student_availability:
        day, time_range = entry
        start_time, end_time = time_range.split('-')
        slots = time_range_to_slots(day, start_time, end_time, time_slots)
        for slot in slots:
            if slot in time_slots:
                availability_row[time_slots.index(slot)] = 1
    return availability_row

# Process antiquity JSONB and convert to a binary row
def process_antiquity(student_antiquity, time_slots):
    antiquity_row = [0] * len(time_slots)
    if student_antiquity:
        for entry in student_antiquity:
            _, *time_ranges = entry
            for day, time_range in time_ranges:
                start_time, end_time = time_range.split('-')
                slots = time_range_to_slots(day, start_time, end_time, time_slots)
                for slot in slots:
                    if slot in time_slots:
                        antiquity_row[time_slots.index(slot)] = 1
    return antiquity_row

# Check instrument continuity (match with antiquity)
def check_continuity(antiquity, instrument):
    if not antiquity:  # Handle null or empty antiquity
        return False
    for entry in antiquity:
        if entry[0] == instrument:
            return True
    return False

# Calculate priorities for instruments
def calculate_instrument_priorities(student):
    antiquity = student.get('antiquity', [])
    requested_instruments = student.get('instruments', [])
    
    instrument_1_priority = 0
    instrument_2_priority = 0
    
    if requested_instruments:
        if check_continuity(antiquity, requested_instruments[0]):
            instrument_1_priority = 2  # Continuity match
        else:
            instrument_1_priority = 1  # No continuity match
        
        if len(requested_instruments) > 1:
            instrument_2_priority = 0.5  # Second choice, lower priority
    
    return requested_instruments[0] if requested_instruments else None, instrument_1_priority, \
           requested_instruments[1] if len(requested_instruments) > 1 else None, instrument_2_priority

# Create priority table for requested courses and instruments
def create_priority_matrix(students, courses, instruments):
    priority_data = []
    for _, student in students.iterrows():
        student_id = student['student_id']
        
        # Create an empty row for the student
        priority_row = [student_id]
        
        # Set course preferences (1 for requested courses)
        course_requested = student.get('courses', [None])
        for course in courses:
            if course in course_requested:
                priority_row.append(1)  # Course requested
            else:
                priority_row.append(0)  # Course not requested
        
        # Set instrument preferences
        instrument_1, instrument_1_priority, instrument_2, instrument_2_priority = calculate_instrument_priorities(student)
        
        # First instrument (1 if chosen)
        for instrument in instruments:
            if instrument == instrument_1:
                priority_row.append(1)  # First choice instrument
            else:
                priority_row.append(0)
        
        # Second instrument (1 if chosen)
        for instrument in instruments:
            if instrument == instrument_2:
                priority_row.append(1)  # Second choice instrument
            else:
                priority_row.append(0)
        
        # Priority for instruments
        priority_row.append(instrument_1_priority)
        priority_row.append(instrument_2_priority)
        
        priority_data.append(priority_row)
    
    # Define column names for course and instrument columns with IDs
    course_ids = [0, 1, 2, 3]  # Map to course IDs (FIX: do not)
    instrument_ids = [501, 502, 503, 504, 505, 506, 507, 508]  # Map to instrument IDs
    columns = ['student_id'] + [f'course_{course_id}' for course_id in course_ids] + \
              [f'instrument_1_{instrument_id}' for instrument_id in instrument_ids] + \
              [f'instrument_2_{instrument_id}' for instrument_id in instrument_ids] + \
              ['instrument_1_priority', 'instrument_2_priority']
    
    return pd.DataFrame(priority_data, columns=columns)

# Create the availability matrix for students
def create_availability_matrix(students, time_slots):
    matrix = []
    for _, student in students.iterrows():
        availability_row = process_availability(student['availability'], time_slots)
        matrix.append([student['student_id']] + availability_row)  # Add student_id as the first column
    return np.array(matrix)

# Create the antiquity matrix for students
def create_antiquity_matrix(students, time_slots):
    matrix = []
    for _, student in students.iterrows():
        antiquity_row = process_antiquity(student['antiquity'], time_slots)
        matrix.append([student['student_id']] + antiquity_row)  # Add student_id as the first column
    return np.array(matrix)

# Extract sibling relationships
def create_sibling_table(students):
    sibling_data = []
    for _, student in students.iterrows():
        student_id = student['student_id']
        siblings = student.get('siblings', [])
        sibling_data.append({'student_id': student_id, 'siblings': siblings})
    return pd.DataFrame(sibling_data)

# Course continuity
def calculate_next_course(students):
    course_continuity = []
    for _, student in students.iterrows():
        student_id = student['student_id']
        antiquity = student['antiquity']

        if antiquity:
            for antique_class in antiquity:
                if "music theory 1" == antique_class[0]:
                    next_course_id = 402
                    break
                elif "music theory 2" in antique_class:
                    next_course_id = 403
                    break
                elif "music theory 3" in antique_class:
                    next_course_id = 403
                    break
                elif "choir" in antique_class:
                    next_course_id = 404
                    break
                else:
                    next_course_id = 0
        else:
            next_course_id = 0

        course_continuity.append({'student_id': student_id, 'next_course': next_course_id})
    return pd.DataFrame(course_continuity)

# Main preprocessing function
def preprocess_students(user_id):
    conn = connect_to_db()

    query = """
        SELECT student_id, name, availability, antiquity, siblings, courses, instruments
        FROM students
        WHERE user_id = %s AND solution_id = %s
        ORDER BY student_id
    """
    students = pd.read_sql_query(query, conn, params=(user_id, 'temp_sol'))

    conn.close()
    
    # Convert JSONB columns to Python lists
    for field in ['availability', 'antiquity', 'siblings', 'courses', 'instruments']:
        students[field] = students[field].apply(lambda x: json.loads(x) if isinstance(x, str) else x)
    
    # List of courses and instruments
    courses = ["music theory 1", "music theory 2", "music theory 3", "choir"]
    instruments = ["guitar", "piano", "drums", "violin", "flute", "clarinet", "cello", "trumpet"]
    
    # Generate time slots
    time_slots = generate_time_slots()
    
    # Create and save availability matrix
    availability_matrix = create_availability_matrix(students, time_slots)
    availability_df = pd.DataFrame(availability_matrix, columns=['student_id'] + time_slots)
    #availability_df.to_csv("student_availability_matrix.csv", index=False)

    # Create and save antiquity matrix
    antiquity_matrix = create_antiquity_matrix(students, time_slots)
    antiquity_df = pd.DataFrame(antiquity_matrix, columns=['student_id'] + time_slots)
    #antiquity_df.to_csv("student_antiquity_matrix.csv", index=False)
    
    # Create and save priority table
    priority_table = create_priority_matrix(students, courses, instruments)
    #priority_table.to_csv("student_priority_matrix.csv", index=False)

    # Create and save sibling table
    sibling_table = create_sibling_table(students)
    #sibling_table.to_csv("student_sibling_table.csv", index=False)

    # Create and save sibling table
    course_antiquity_table = calculate_next_course(students)
    #course_antiquity_table.to_csv("course_antiquity_table.csv", index=False)

    return availability_df, antiquity_df, priority_table, sibling_table, course_antiquity_table

def generate_student_index_csv(user_id):
    conn = connect_to_db()

    conn = connect_to_db()

    query = """
        SELECT student_id, name
        FROM students
        WHERE user_id = %s AND solution_id = %s
        ORDER BY student_id
    """
    student_index_mapping = pd.read_sql_query(query, conn, params=(user_id, 'temp_sol'))

    conn.close()
    
    # Add index column
    student_index_mapping.insert(0, 'index', range(len(student_index_mapping)))
    
    # Save to CSV
    #student_index_mapping.to_csv("student_index_mapping.csv", index=False)

    return student_index_mapping
    
  
# Run preprocessing
#if __name__ == "__main__":
def load_students_data(user_id):
    availability_df, antiquity_df, priority_table, sibling_table, course_antiquity_table = preprocess_students(user_id)
    student_index_mapping = generate_student_index_csv(user_id)
    return availability_df, antiquity_df, priority_table, sibling_table, course_antiquity_table, student_index_mapping
