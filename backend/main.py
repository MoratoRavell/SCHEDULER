from fastapi import FastAPI, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, FileResponse, JSONResponse

from pydantic import BaseModel
import psycopg2
import subprocess
import threading
import os
import zipfile
import tempfile
import json
import io
import csv

from auth import router as auth_router

from load_input import load_data, replace_solution_entry, connect_to_db


class APIcallRequest(BaseModel):
    user_id: int
    solution_id: str


app = FastAPI()

app.include_router(auth_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


process_ref = None # Store process reference
lock = threading.Lock()  # Prevent race conditions when running/stopping the model


# Database connection
def connect_to_db():
    return psycopg2.connect(
        dbname="scheduling_app",
        user="postgres",
        password="221214",
        host="localhost",
        port="5432"
    )


@app.get("/")
def read_root():
    return {"message": "FastAPI is running!"}


@app.post("/run-model")
def run_model(payload: dict = Body(...)):
    user_id = payload["user_id"]
    input_data = payload["data"]

    def load_input_data_directly(user_id, input_data):
        conn = connect_to_db()
        cursor = conn.cursor()

        try:
            replace_solution_entry(cursor, user_id, 'temp_sol')

            load_data_from_memory(input_data.get('students', []), 'students', cursor, user_id)
            load_data_from_memory(input_data.get('teachers', []), 'teachers', cursor, user_id)
            load_data_from_memory(input_data.get('rooms', []), 'rooms', cursor, user_id)
            load_data_from_memory(input_data.get('courses', []), 'courses', cursor, user_id)
            load_data_from_memory(input_data.get('instruments', []), 'instruments', cursor, user_id)

            conn.commit()
        except Exception as e:
            conn.rollback()
            raise
        finally:
            cursor.close()
            conn.close()

    def load_data_from_memory(data, table_name, cursor, user_id, solution_id='temp_sol'):
        success_count = 0
        fail_count = 0

        for entry in data:
            try:
                entry['user_id'] = user_id
                entry['solution_id'] = solution_id

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
            except Exception:
                fail_count += 1
                traceback.print_exc()

    load_input_data_directly(user_id, input_data)

    global process_ref

    def stream_output():
        global process_ref
        with lock:
            if process_ref is not None:
                yield "Another process is already running. Stop it first.\n"
                return

            process_ref = subprocess.Popen(
                ["python", "-u", "model_appver.py", str(user_id)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1
            )

        for line in iter(process_ref.stdout.readline, ""):
            yield line
            process_ref.stdout.flush()

        for line in iter(process_ref.stderr.readline, ""):
            yield f"ERROR: {line}"
            process_ref.stderr.flush()

        with lock:
            process_ref = None

    return StreamingResponse(stream_output(), media_type="text/plain")


@app.post("/stop-model")
def stop_model():
    global process_ref
    with lock: # Only one request can modidy process_ref at a time
        if process_ref and process_ref.poll() is None:  # If running
            process_ref.terminate()  # Graceful stop
            process_ref.wait()  # Wait for cleanup
            process_ref = None
            return {"message": "Model process stopped."}
        return {"message": "No process is running."}


@app.post("/validate-solution")
def validate_solution(payload: dict = Body(...)):
    user_id = payload["user_id"]
    solution_id = payload["solution_id"]

    tables_required = [
        "solution_assignments",
        "solution_insights",
        "student_index_mapping",
        "teacher_index_mapping",
        "course_index_mapping",
        "room_index_mapping",
        "instrument_index_mapping",
        "student_count",
    ]

    try:
        conn = connect_to_db()
        cursor = conn.cursor()

        for table in tables_required:
            cursor.execute(
                f"SELECT 1 FROM {table} WHERE user_id = %s AND solution_id = %s LIMIT 1",
                (user_id, solution_id)
            )
            if not cursor.fetchone():
                cursor.close()
                conn.close()
                return {"valid": False}

        cursor.close()
        conn.close()
        return {"valid": True}
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)


@app.post("/get-solution")
def get_solution(solutionId: str = Body(..., media_type="text/plain")):
    conn = connect_to_db()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT class_name, start_time, end_time, room_id, max_capacity, current_capacity,
                   teacher_id, contract_type, load, student_id,
                   instrument_penalty, antiquity_day_penalty,
                   antiquity_deviation_penalty, sibling_mismatch_penalty
            FROM temp_solution_assignments
        """)
        rows = cursor.fetchall()

        with open("C:/Users/joanm/Documents/SCHEDULER/debug_rows_count.txt", "w") as f:
            f.write(f"Row count: {len(rows)}\n")

        if not rows:
            return {"message": "No temporary solution available."}

        colnames = [desc[0] for desc in cursor.description]

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(colnames)
        writer.writerows(rows)
        output.seek(0)

        return StreamingResponse(output, media_type="text/csv", headers={
            "Content-Disposition": "attachment; filename=model_solution_appver.csv"
        })

    except Exception as e:
        return {"message": f"An error occurred: {str(e)}"}


@app.post("/custom-get-solution")
def custom_get_solution(request: APIcallRequest):
    user_id = request.user_id
    solution_id = request.solution_id

    conn = connect_to_db()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT * FROM solution_assignments WHERE user_id = %s AND solution_id = %s LIMIT 1", (user_id, solution_id))
        filtered_colnames = [desc[0] for desc in cursor.description if desc[0] not in ('solution_id', 'user_id', 'id')]
        if not filtered_colnames:
            return {"message": "Saved solution not found."}

        col_str = ", ".join(filtered_colnames)
        cursor.execute(
            f"SELECT {col_str} FROM solution_assignments WHERE user_id = %s AND solution_id = %s",
            (user_id, solution_id)
        )
        rows = cursor.fetchall()

        if not rows:
            return {"message": "Saved solution not found."}

        colnames = [desc[0] for desc in cursor.description]

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(colnames)
        writer.writerows(rows)
        output.seek(0)

        return StreamingResponse(output, media_type="text/csv", headers={"Content-Disposition": "attachment; filename=model_solution_appver.csv"})

    except ValueError:
        return {"message": "Invalid solution selection (must be integer)."}

@app.get("/get-insights")
def get_insights():
    conn = connect_to_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM temp_solution_insights")
    rows = cursor.fetchall()

    if not rows:
        return {"message": "No temporary insights available."}

    colnames = [desc[0] for desc in cursor.description]

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(colnames)
    writer.writerows(rows)
    output.seek(0)

    return StreamingResponse(output, media_type="text/csv", headers={"Content-Disposition": "attachment; filename=model_insights_appver.csv"})


@app.post("/custom-get-insights")
def custom_get_insights(request: APIcallRequest):
    user_id = request.user_id
    solution_id = request.solution_id

    conn = connect_to_db()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT * FROM solution_insights WHERE user_id = %s AND solution_id = %s LIMIT 1", (user_id, solution_id))
        filtered_colnames = [desc[0] for desc in cursor.description if desc[0] not in ('solution_id', 'user_id', 'id')]
        if not filtered_colnames:
            return {"message": "Saved solution not found."}

        col_str = ", ".join(filtered_colnames)
        cursor.execute(
            f"SELECT {col_str} FROM solution_insights WHERE user_id = %s AND solution_id = %s",
            (user_id, solution_id)
        )
        rows = cursor.fetchall()

        if not rows:
            return {"message": "Saved insights not found."}

        colnames = [desc[0] for desc in cursor.description]

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(colnames)
        writer.writerows(rows)
        output.seek(0)

        return StreamingResponse(output, media_type="text/csv", headers={"Content-Disposition": "attachment; filename=model_insights_appver.csv"})

    except ValueError:
        return {"message": "Invalid solution selection (must be integer)."}


@app.get("/get-student-names")
def get_student_names():
    conn = connect_to_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM temp_student_index_mapping")
    rows = cursor.fetchall()

    if not rows:
        return {"message": "Student names not found."}

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([desc[0] for desc in cursor.description])
    writer.writerows(rows)
    output.seek(0)

    return StreamingResponse(output, media_type="text/csv", headers={"Content-Disposition": "attachment; filename=student_index_mapping.csv"})


@app.post("/custom-get-student-names")
def custom_get_student_names(request: APIcallRequest):
    user_id = request.user_id
    solution_id = request.solution_id

    conn = connect_to_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM student_index_mapping WHERE user_id = %s AND solution_id = %s LIMIT 1", (user_id, solution_id))
    filtered_colnames = [desc[0] for desc in cursor.description if desc[0] not in ('solution_id', 'user_id', 'id')]
    if not filtered_colnames:
        return {"message": "Saved solution not found."}

    # Step 2: Fetch only the filtered columns
    col_str = ", ".join(filtered_colnames)
    cursor.execute(
        f"SELECT {col_str} FROM student_index_mapping WHERE user_id = %s AND solution_id = %s",
        (user_id, solution_id)
    )
    rows = cursor.fetchall()

    if not rows:
        return {"message": "Student names not found."}

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([desc[0] for desc in cursor.description])
    writer.writerows(rows)
    output.seek(0)

    return StreamingResponse(output, media_type="text/csv", headers={"Content-Disposition": "attachment; filename=student_index_mapping.csv"})


@app.get("/get-teacher-names")
def get_teacher_names():
    conn = connect_to_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM temp_teacher_index_mapping")
    rows = cursor.fetchall()

    if not rows:
        return {"message": "Teacher names not found."}

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([desc[0] for desc in cursor.description])
    writer.writerows(rows)
    output.seek(0)

    return StreamingResponse(output, media_type="text/csv", headers={"Content-Disposition": "attachment; filename=teacher_index_mapping.csv"})


@app.post("/custom-get-teacher-names")
def custom_get_teacher_names(request: APIcallRequest):
    user_id = request.user_id
    solution_id = request.solution_id

    conn = connect_to_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM teacher_index_mapping WHERE user_id = %s AND solution_id = %s LIMIT 1", (user_id, solution_id))
    filtered_colnames = [desc[0] for desc in cursor.description if desc[0] not in ('solution_id', 'user_id', 'id')]
    if not filtered_colnames:
        return {"message": "Saved solution not found."}

    col_str = ", ".join(filtered_colnames)
    cursor.execute(
        f"SELECT {col_str} FROM teacher_index_mapping WHERE user_id = %s AND solution_id = %s",
        (user_id, solution_id)
    )
    rows = cursor.fetchall()

    if not rows:
        return {"message": "Teacher names not found."}

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([desc[0] for desc in cursor.description])
    writer.writerows(rows)
    output.seek(0)

    return StreamingResponse(output, media_type="text/csv", headers={"Content-Disposition": "attachment; filename=teacher_index_mapping.csv"})


@app.get("/get-room-names")
def get_room_names():
    conn = connect_to_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM temp_room_index_mapping")
    rows = cursor.fetchall()

    if not rows:
        return {"message": "Room names not found."}

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([desc[0] for desc in cursor.description])
    writer.writerows(rows)
    output.seek(0)

    return StreamingResponse(output, media_type="text/csv", headers={"Content-Disposition": "attachment; filename=room_index_mapping.csv"})


@app.post("/custom-get-room-names")
def custom_get_room_names(request: APIcallRequest):
    user_id = request.user_id
    solution_id = request.solution_id

    conn = connect_to_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM room_index_mapping WHERE user_id = %s AND solution_id = %s LIMIT 1", (user_id, solution_id))
    filtered_colnames = [desc[0] for desc in cursor.description if desc[0] not in ('solution_id', 'user_id', 'id')]
    if not filtered_colnames:
        return {"message": "Saved solution not found."}

    col_str = ", ".join(filtered_colnames)
    cursor.execute(
        f"SELECT {col_str} FROM room_index_mapping WHERE user_id = %s AND solution_id = %s",
        (user_id, solution_id)
    )
    rows = cursor.fetchall()

    if not rows:
        return {"message": "Room names not found."}

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([desc[0] for desc in cursor.description])
    writer.writerows(rows)
    output.seek(0)

    return StreamingResponse(output, media_type="text/csv", headers={"Content-Disposition": "attachment; filename=room_index_mapping.csv"})


@app.get("/get-course-names")
def get_course_names():
    conn = connect_to_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM temp_course_index_mapping")
    rows = cursor.fetchall()

    if not rows:
        return {"message": "Course names not found."}

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([desc[0] for desc in cursor.description])
    writer.writerows(rows)
    output.seek(0)

    return StreamingResponse(output, media_type="text/csv", headers={"Content-Disposition": "attachment; filename=course_index_mapping.csv"})


@app.post("/custom-get-course-names")
def custom_get_course_names(request: APIcallRequest):
    user_id = request.user_id
    solution_id = request.solution_id

    conn = connect_to_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM course_index_mapping WHERE user_id = %s AND solution_id = %s LIMIT 1", (user_id, solution_id))
    filtered_colnames = [desc[0] for desc in cursor.description if desc[0] not in ('solution_id', 'user_id', 'id')]
    if not filtered_colnames:
        return {"message": "Saved solution not found."}

    col_str = ", ".join(filtered_colnames)
    cursor.execute(
        f"SELECT {col_str} FROM course_index_mapping WHERE user_id = %s AND solution_id = %s",
        (user_id, solution_id)
    )
    rows = cursor.fetchall()

    if not rows:
        return {"message": "Course names not found."}

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([desc[0] for desc in cursor.description])
    writer.writerows(rows)
    output.seek(0)

    return StreamingResponse(output, media_type="text/csv", headers={"Content-Disposition": "attachment; filename=course_index_mapping.csv"})


@app.get("/get-instrument-names")
def get_instrument_names():
    conn = connect_to_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM temp_instrument_index_mapping")
    rows = cursor.fetchall()

    if not rows:
        return {"message": "Instrument names not found."}

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([desc[0] for desc in cursor.description])
    writer.writerows(rows)
    output.seek(0)

    return StreamingResponse(output, media_type="text/csv", headers={"Content-Disposition": "attachment; filename=instrument_index_mapping.csv"})


@app.post("/custom-get-instrument-names")
def custom_get_instrument_names(request: APIcallRequest):
    user_id = request.user_id
    solution_id = request.solution_id

    conn = connect_to_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM instrument_index_mapping WHERE user_id = %s AND solution_id = %s LIMIT 1", (user_id, solution_id))
    filtered_colnames = [desc[0] for desc in cursor.description if desc[0] not in ('solution_id', 'user_id', 'id')]
    if not filtered_colnames:
        return {"message": "Saved solution not found."}

    # Step 2: Fetch only the filtered columns
    col_str = ", ".join(filtered_colnames)
    cursor.execute(
        f"SELECT {col_str} FROM instrument_index_mapping WHERE user_id = %s AND solution_id = %s",
        (user_id, solution_id)
    )
    rows = cursor.fetchall()

    if not rows:
        return {"message": "Instrument names not found."}

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([desc[0] for desc in cursor.description])
    writer.writerows(rows)
    output.seek(0)

    return StreamingResponse(output, media_type="text/csv", headers={"Content-Disposition": "attachment; filename=instrument_index_mapping.csv"})


@app.get("/get-student-count")
def get_student_count():
    conn = connect_to_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM temp_student_count")
    rows = cursor.fetchall()

    if not rows:
        return {"message": "No temporary student count available."}

    colnames = [desc[0] for desc in cursor.description]

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(colnames)
    writer.writerows(rows)
    output.seek(0)

    return StreamingResponse(output, media_type="text/csv", headers={"Content-Disposition": "attachment; filename=student_count.csv"})


@app.post("/custom-get-student-count")
def custom_get_student_count(request: APIcallRequest):
    user_id = request.user_id
    solution_id = request.solution_id
    
    conn = connect_to_db()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT * FROM student_count WHERE user_id = %s AND solution_id = %s LIMIT 1", (user_id, solution_id))
        filtered_colnames = [desc[0] for desc in cursor.description if desc[0] not in ('solution_id', 'user_id', 'id')]
        if not filtered_colnames:
            return {"message": "Saved solution not found."}

        col_str = ", ".join(filtered_colnames)
        cursor.execute(
        f"SELECT {col_str} FROM student_count WHERE user_id = %s AND solution_id = %s",
            (user_id, solution_id)
        )
        rows = cursor.fetchall()

        if not rows:
            return {"message": "Saved student count not found."}

        colnames = [desc[0] for desc in cursor.description]

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(colnames)
        writer.writerows(rows)
        output.seek(0)

        return StreamingResponse(output, media_type="text/csv", headers={"Content-Disposition": "attachment; filename=student_count.csv"})

    except ValueError:
        return {"message": "Invalid solution selection (must be integer)."}


@app.post("/save-solution")
def save_solution(payload: dict = Body(...)):
    user_id = payload["user_id"]
    new_solution_id = payload["solution_id"]
    temp_solution_id = "temp_sol"

    tables = [
        "solution_assignments",
        "solution_insights",
        "student_index_mapping",
        "teacher_index_mapping",
        "course_index_mapping",
        "room_index_mapping",
        "instrument_index_mapping",
        "student_count",
    ]

    try:
        conn = connect_to_db()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO solutions (user_id, solution_id)
            VALUES (%s, %s)
            ON CONFLICT DO NOTHING
        """, (user_id, new_solution_id))

        for table in tables:
            cursor.execute(f"SELECT * FROM {table} LIMIT 0")
            cols = [desc[0] for desc in cursor.description]
            insert_cols = [col for col in cols if col != "id"]

            cursor.execute(f"""
                DELETE FROM {table}
                WHERE user_id = %s AND solution_id = %s
            """, (user_id, new_solution_id))

            insert_cols_str = ", ".join(insert_cols)
            select_cols_str = ", ".join([
                "%s AS user_id" if col == "user_id" else
                "%s AS solution_id" if col == "solution_id" else
                col
                for col in insert_cols
            ])

            cursor.execute(f"""
                INSERT INTO {table} ({insert_cols_str})
                SELECT {select_cols_str}
                FROM {table}
                WHERE user_id = %s AND solution_id = %s
            """, (user_id, new_solution_id, user_id, temp_solution_id))

        conn.commit()
        cursor.close()
        conn.close()
        return {"message": f"Solution '{new_solution_id}' saved successfully from 'temp_sol'."}

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.get("/get-solutions-list")
def get_solutions_list(user_id: str):
    try:
        conn = connect_to_db()
        cursor = conn.cursor()
        cursor.execute("SELECT solution_id FROM solutions WHERE user_id = %s ORDER BY created_at DESC;", (user_id,))
        rows = cursor.fetchall()
        solution_ids = [row[0] for row in rows]
        cursor.close()
        conn.close()

        solution_ids = [row[0] for row in rows if row[0] != "temp_sol"]
        return solution_ids

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.post("/delete-solution")
def delete_solution(payload: dict = Body(...)):
    user_id = payload["user_id"]
    solution_id = payload["solution_id"]

    try:
        conn = connect_to_db()
        cursor = conn.cursor()

        tables = [
            "solution_assignments",
            "solution_insights",
            "room_index_mapping",
            "student_index_mapping",
            "teacher_index_mapping",
            "instrument_index_mapping",
            "course_index_mapping",
            "student_count"
        ]

        for table in tables:
            cursor.execute(f"DELETE FROM {table} WHERE user_id = %s AND solution_id = %s", (user_id, solution_id))

        cursor.execute("DELETE FROM solutions WHERE user_id = %s AND solution_id = %s", (user_id, solution_id))

        conn.commit()
        cursor.close()
        conn.close()
        return JSONResponse(status_code=200, content={"message": "Deleted successfully."})

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
