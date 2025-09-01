import psycopg2
import pandas as pd
import json
import numpy as np

# Database connection
def connect_to_db():
    return psycopg2.connect(
        dbname="scheduling_app",
        user="postgres",
        password="221214",
        host="localhost",
        port="5432"
    )

# Map feature IDs to names
FEATURE_MAP = {
    601: "soundproof walls",
    602: "music stands",
    603: "piano",
    604: "drums",
    605: "projector",
    606: "desks",
    607: "whiteboard",
    608: "amplifier",
    609: "microphones"
}

# Generate the full list of unique equipment feature IDs
def generate_feature_ids():
    return list(FEATURE_MAP.keys())

# Process features into a binary matrix for rooms, courses, and instruments
def process_features_matrix(features, feature_map):
    feature_names = feature_map.values()
    feature_matrix = [1 if feature in features else 0 for feature in feature_names]
    return feature_matrix

# Preprocess the rooms, courses, instruments data and save matrices
def preprocess_school(user_id):
    conn = connect_to_db()

    rooms_query = """
        SELECT room_id, capacity, features
        FROM rooms
        WHERE user_id = %s AND solution_id = %s
        ORDER BY room_id
    """
    rooms = pd.read_sql_query(rooms_query, conn, params=(user_id, 'temp_sol'))

    courses_query = """
        SELECT course_id, capacity, duration, features
        FROM courses
        WHERE user_id = %s AND solution_id = %s
        ORDER BY course_id
    """
    courses = pd.read_sql_query(courses_query, conn, params=(user_id, 'temp_sol'))

    instruments_query = """
        SELECT instrument_id, capacity, duration, features
        FROM instruments
        WHERE user_id = %s AND solution_id = %s
        ORDER BY instrument_id
    """
    instruments = pd.read_sql_query(instruments_query, conn, params=(user_id, 'temp_sol'))

    conn.close()

    # Generate the list of equipment feature IDs
    feature_ids = generate_feature_ids()

    # Process the data into binary matrices for features
    rooms['features'] = rooms['features'].apply(lambda x: process_features_matrix(x, FEATURE_MAP))
    courses['features'] = courses['features'].apply(lambda x: process_features_matrix(x, FEATURE_MAP))
    instruments['features'] = instruments['features'].apply(lambda x: process_features_matrix(x, FEATURE_MAP))

    # Save processed data as matrices (binary), with capacity and duration first, followed by ID, and then binary matrix

    # Rooms matrix (no duration)
    rooms_matrix = pd.DataFrame(rooms['features'].tolist(), columns=feature_ids)
    rooms_matrix.insert(0, 'room_capacity', rooms['capacity'])
    rooms_matrix.insert(0, 'room_id', rooms['room_id'])  # Restored room_id
    #rooms_matrix.to_csv("rooms_matrix.csv", index=False)

    # Courses matrix
    courses_matrix = pd.DataFrame(courses['features'].tolist(), columns=feature_ids)
    courses_matrix.insert(0, 'course_id', courses['course_id'])  # Restored course_id
    courses_matrix.insert(0, 'course_capacity', courses['capacity'])
    courses_matrix['course_duration_times_per_week'] = courses['duration'].apply(lambda x: x[0] if isinstance(x, list) else None)
    courses_matrix['course_duration_minutes_per_session'] = courses['duration'].apply(lambda x: x[1] if isinstance(x, list) else None)
    # Reorder columns: id, capacity, duration, then binary matrix
    courses_matrix = courses_matrix[['course_id', 'course_capacity', 'course_duration_times_per_week', 'course_duration_minutes_per_session'] + feature_ids]
    #courses_matrix.to_csv("courses_matrix.csv", index=False)

    # Instruments matrix
    instruments_matrix = pd.DataFrame(instruments['features'].tolist(), columns=feature_ids)
    instruments_matrix.insert(0, 'instrument_id', instruments['instrument_id'])  # Restored instrument_id
    instruments_matrix.insert(0, 'instrument_capacity', instruments['capacity'])
    instruments_matrix['instrument_duration_times_per_week'] = instruments['duration'].apply(lambda x: x[0] if isinstance(x, list) else None)
    instruments_matrix['instrument_duration_minutes_per_session'] = instruments['duration'].apply(lambda x: x[1] if isinstance(x, list) else None)
    # Reorder columns: id, capacity, duration, then binary matrix
    instruments_matrix = instruments_matrix[['instrument_id', 'instrument_capacity', 'instrument_duration_times_per_week', 'instrument_duration_minutes_per_session'] + feature_ids]
    #instruments_matrix.to_csv("instruments_matrix.csv", index=False)

    return rooms_matrix, courses_matrix, instruments_matrix

def generate_course_index_csv(user_id):
    conn = connect_to_db()

    query = """
        SELECT course_id, name
        FROM courses
        WHERE user_id = %s AND solution_id = %s
        ORDER BY course_id
    """
    course_index_mapping = pd.read_sql_query(query, conn, params=(user_id, 'temp_sol'))
    conn.close()

    # Add index column
    course_index_mapping.insert(0, 'index', range(len(course_index_mapping)))
    
    # Save to CSV
    #course_index_mapping.to_csv("course_index_mapping.csv", index=False)
    
    return course_index_mapping

def generate_instrument_index_csv(user_id):
    conn = connect_to_db()

    query = """
        SELECT instrument_id, name
        FROM instruments
        WHERE user_id = %s AND solution_id = %s
        ORDER BY instrument_id
    """
    instrument_index_mapping = pd.read_sql_query(query, conn, params=(user_id, 'temp_sol'))
    conn.close()
    
    # Add index column
    instrument_index_mapping.insert(0, 'index', range(len(instrument_index_mapping)))
    
    # Save to CSV
    #instrument_index_mapping.to_csv("instrument_index_mapping.csv", index=False)

    return instrument_index_mapping

def generate_room_index_csv(user_id):
    conn = connect_to_db()

    query = """
        SELECT room_id, name
        FROM rooms
        WHERE user_id = %s AND solution_id = %s
        ORDER BY room_id
    """
    room_index_mapping = pd.read_sql_query(query, conn, params=(user_id, 'temp_sol'))
    conn.close()
    
    # Add index column
    room_index_mapping.insert(0, 'index', range(len(room_index_mapping)))
    
    # Save to CSV
    #room_index_mapping.to_csv("room_index_mapping.csv", index=False)

    return room_index_mapping
    

# Run preprocessing
#if __name__ == "__main__":
def load_school_data(user_id):
    rooms_matrix, courses_matrix, instruments_matrix = preprocess_school(user_id)
    course_index_mapping = generate_course_index_csv(user_id)
    instrument_index_mapping = generate_instrument_index_csv(user_id)
    room_index_mapping = generate_room_index_csv(user_id)
    return rooms_matrix, courses_matrix, instruments_matrix, course_index_mapping, instrument_index_mapping, room_index_mapping
