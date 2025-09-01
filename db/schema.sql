CREATE DATABASE scheduling_app;

\c scheduling_app

-- Drop dependent tables first or use CASCADE
DROP TABLE IF EXISTS students CASCADE;
DROP TABLE IF EXISTS teachers CASCADE;
DROP TABLE IF EXISTS rooms CASCADE;
DROP TABLE IF EXISTS courses CASCADE;
DROP TABLE IF EXISTS instruments CASCADE;

-- Drop solution data tables

DROP TABLE IF EXISTS student_count CASCADE;
DROP TABLE IF EXISTS course_index_mapping CASCADE;
DROP TABLE IF EXISTS instrument_index_mapping CASCADE;
DROP TABLE IF EXISTS teacher_index_mapping CASCADE;
DROP TABLE IF EXISTS student_index_mapping CASCADE;
DROP TABLE IF EXISTS room_index_mapping CASCADE;
DROP TABLE IF EXISTS solution_insights CASCADE;
DROP TABLE IF EXISTS solution_assignments CASCADE;

-- Drop solution tracking and users last
DROP TABLE IF EXISTS solutions CASCADE;
DROP TABLE IF EXISTS users CASCADE;


CREATE TABLE IF NOT EXISTS users (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    hashed_password VARCHAR(200) NOT NULL,
    name VARCHAR(100),
    surname VARCHAR(100),
    email VARCHAR(150),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- SAVED SOLUTIONS
CREATE TABLE solutions (
    user_id INTEGER REFERENCES users(user_id),
    solution_id VARCHAR(63),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, solution_id)
);

-- TABLES FOR INPUT DATA
CREATE TABLE students (
    student_id INTEGER,
    id SERIAL PRIMARY KEY,
    user_id INTEGER,
    solution_id VARCHAR(63),
    name VARCHAR(100),
    availability JSONB,
    antiquity JSONB,
    siblings JSONB,
    courses JSONB,
    instruments JSONB,
    FOREIGN KEY (user_id, solution_id) REFERENCES solutions(user_id, solution_id)
);

CREATE TABLE teachers (
    teacher_id INTEGER,
    id SERIAL PRIMARY KEY,
    user_id INTEGER,
    solution_id VARCHAR(63),
    name VARCHAR(100),
    availability JSONB,
    contract JSONB,
    courses JSONB,
    instruments JSONB,
    FOREIGN KEY (user_id, solution_id) REFERENCES solutions(user_id, solution_id)
);

CREATE TABLE rooms (
    room_id INTEGER,
    id SERIAL PRIMARY KEY,
    user_id INTEGER,
    solution_id VARCHAR(63),
    name VARCHAR(100),
    capacity INT,
    features JSONB,
    FOREIGN KEY (user_id, solution_id) REFERENCES solutions(user_id, solution_id)
);

CREATE TABLE courses (
    course_id INTEGER,
    id SERIAL PRIMARY KEY,
    user_id INTEGER,
    solution_id VARCHAR(63),
    name VARCHAR(100),
    duration JSONB,
    capacity INT,
    features JSONB,
    FOREIGN KEY (user_id, solution_id) REFERENCES solutions(user_id, solution_id)
);

CREATE TABLE instruments (
    instrument_id INTEGER,
    id SERIAL PRIMARY KEY,
    user_id INTEGER,
    solution_id VARCHAR(63),
    name VARCHAR(100),
    duration JSONB,
    capacity INT,
    features JSONB,
    FOREIGN KEY (user_id, solution_id) REFERENCES solutions(user_id, solution_id)
);

-- TABLES FOR SAVED SOLUTIONS
CREATE TABLE solution_assignments (
    id SERIAL PRIMARY KEY,
    user_id INTEGER,
    solution_id VARCHAR(63),
    class_name VARCHAR(100),
    start_time INTEGER,
    end_time INTEGER,
    room_id INTEGER,
    max_capacity INTEGER,
    current_capacity INTEGER,
    teacher_id INTEGER,
    contract_type INTEGER,
    load INTEGER,
    student_id INTEGER,
    instrument_penalty INTEGER,
    antiquity_day_penalty INTEGER,
    antiquity_deviation_penalty INTEGER,
    sibling_mismatch_penalty INTEGER,
    FOREIGN KEY (user_id, solution_id) REFERENCES solutions(user_id, solution_id)
);

CREATE TABLE solution_insights (
    id SERIAL PRIMARY KEY,
    user_id INTEGER,
    solution_id VARCHAR(63),
    workload_balance_index FLOAT,
    daily_workload_deviation JSONB,
    underutilized_teachers JSONB,
    overloaded_teachers JSONB,
    student_distribution_score FLOAT,
    room_utilization_rate FLOAT,
    peak_hour_congestion JSONB,
    room_underuse JSONB,
    missing_course_students JSONB,
    missing_instrument_students JSONB,
    FOREIGN KEY (user_id, solution_id) REFERENCES solutions(user_id, solution_id)
);

CREATE TABLE room_index_mapping (
    index INTEGER,
    user_id INTEGER,
    solution_id VARCHAR(63),
    room_id INTEGER,
    name VARCHAR(100),
    PRIMARY KEY (solution_id, index),
    FOREIGN KEY (user_id, solution_id) REFERENCES solutions(user_id, solution_id)
);

CREATE TABLE student_index_mapping (
    index INTEGER,
    user_id INTEGER,
    solution_id VARCHAR(63),
    student_id INTEGER,
    name VARCHAR(100),
    PRIMARY KEY (solution_id, index),
    FOREIGN KEY (user_id, solution_id) REFERENCES solutions(user_id, solution_id)
);

CREATE TABLE teacher_index_mapping (
    index INTEGER,
    user_id INTEGER,
    solution_id VARCHAR(63),
    teacher_id INTEGER,
    name VARCHAR(100),
    PRIMARY KEY (solution_id, index),
    FOREIGN KEY (user_id, solution_id) REFERENCES solutions(user_id, solution_id)
);

CREATE TABLE instrument_index_mapping (
    index INTEGER,
    user_id INTEGER,
    solution_id VARCHAR(63),
    instrument_id INTEGER,
    name VARCHAR(100),
    PRIMARY KEY (solution_id, index),
    FOREIGN KEY (user_id, solution_id) REFERENCES solutions(user_id, solution_id)
);

CREATE TABLE course_index_mapping (
    index INTEGER,
    user_id INTEGER,
    solution_id VARCHAR(63),
    course_id INTEGER,
    name VARCHAR(100),
    PRIMARY KEY (solution_id, index),
    FOREIGN KEY (user_id, solution_id) REFERENCES solutions(user_id, solution_id)
);

CREATE TABLE student_count (
    time_slot INTEGER,
    user_id INTEGER,
    solution_id VARCHAR(63),
    students INTEGER,
    PRIMARY KEY (solution_id, time_slot),
    FOREIGN KEY (user_id, solution_id) REFERENCES solutions(user_id, solution_id)
);
