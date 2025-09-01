import json
import psycopg2
import traceback

# Database connection
def connect_to_db():
    return psycopg2.connect(
        dbname="scheduling_app",
        user="postgres",
        password="221214",
        host="localhost",
        port="5432"
    )

def replace_solution_entry(cursor, user_id, solution_id):
    # Delete if exists
    cursor.execute("DELETE FROM students WHERE user_id = %s AND solution_id = %s", (user_id, solution_id))
    cursor.execute("DELETE FROM teachers WHERE user_id = %s AND solution_id = %s", (user_id, solution_id))
    cursor.execute("DELETE FROM rooms WHERE user_id = %s AND solution_id = %s", (user_id, solution_id))
    cursor.execute("DELETE FROM courses WHERE user_id = %s AND solution_id = %s", (user_id, solution_id))
    cursor.execute("DELETE FROM instruments WHERE user_id = %s AND solution_id = %s", (user_id, solution_id))
    cursor.execute("DELETE FROM solution_assignments WHERE user_id = %s AND solution_id = %s", (user_id, solution_id))
    cursor.execute("DELETE FROM solution_insights WHERE user_id = %s AND solution_id = %s", (user_id, solution_id))
    cursor.execute("DELETE FROM student_count WHERE user_id = %s AND solution_id = %s", (user_id, solution_id))
    cursor.execute("DELETE FROM student_index_mapping WHERE user_id = %s AND solution_id = %s", (user_id, solution_id))
    cursor.execute("DELETE FROM teacher_index_mapping WHERE user_id = %s AND solution_id = %s", (user_id, solution_id))
    cursor.execute("DELETE FROM room_index_mapping WHERE user_id = %s AND solution_id = %s", (user_id, solution_id))
    cursor.execute("DELETE FROM course_index_mapping WHERE user_id = %s AND solution_id = %s", (user_id, solution_id))
    cursor.execute("DELETE FROM instrument_index_mapping WHERE user_id = %s AND solution_id = %s", (user_id, solution_id))

    cursor.execute(
        "DELETE FROM solutions WHERE user_id = %s AND solution_id = %s",
        (user_id, solution_id)
    )
    # Insert fresh
    cursor.execute(
        "INSERT INTO solutions (user_id, solution_id) VALUES (%s, %s)",
        (user_id, solution_id)
    )


def load_data(file_path, table_name, cursor, user_id, solution_id='temp_sol'):
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
    except Exception as e:
        traceback.print_exc()
        return

    success_count = 0
    fail_count = 0

    for i, entry in enumerate(data):
        try:
            entry['user_id'] = user_id
            entry['solution_id'] = solution_id

            # Convert complex fields to JSON strings
            if table_name in ['students', 'teachers']:
                for field in ['availability', 'antiquity', 'siblings', 'courses', 'instruments', 'contract', 'features', 'duration']:
                    if field in entry:
                        entry[field] = json.dumps(entry[field])
            elif table_name in ['rooms', 'courses', 'instruments']:
                for field in ['features', 'duration']:
                    if field in entry:
                        entry[field] = json.dumps(entry[field])

            keys = ', '.join(entry.keys())
            values_placeholders = ', '.join(['%s'] * len(entry))
            query = f"INSERT INTO {table_name} ({keys}) VALUES ({values_placeholders})"
            cursor.execute(query, list(entry.values()))
            success_count += 1
        except Exception as e:
            traceback.print_exc()
            fail_count += 1

def load_input_data(user_id):
    conn = connect_to_db()
    cursor = conn.cursor()

    try:
        replace_solution_entry(cursor, user_id, 'temp_sol')

        load_data('students.json', 'students', cursor, user_id)
        load_data('teachers.json', 'teachers', cursor, user_id)
        load_data('rooms.json', 'rooms', cursor, user_id)
        load_data('courses.json', 'courses', cursor, user_id)
        load_data('instruments.json', 'instruments', cursor, user_id)

        conn.commit()
    except Exception as e:
        conn.rollback()
        traceback.print_exc()
    finally:
        cursor.close()
        conn.close()
