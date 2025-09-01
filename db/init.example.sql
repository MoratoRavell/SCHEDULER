--
-- PostgreSQL database dump
--

-- Dumped from database version 17.2
-- Dumped by pg_dump version 17.2

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: course_index_mapping; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.course_index_mapping (
    index integer NOT NULL,
    user_id integer,
    solution_id character varying(63) NOT NULL,
    course_id integer,
    name character varying(100)
);


--
-- Name: courses; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.courses (
    course_id integer,
    id integer NOT NULL,
    user_id integer,
    solution_id character varying(63),
    name character varying(100),
    duration jsonb,
    capacity integer,
    features jsonb
);


--
-- Name: courses_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.courses_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: courses_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.courses_id_seq OWNED BY public.courses.id;


--
-- Name: instrument_index_mapping; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.instrument_index_mapping (
    index integer NOT NULL,
    user_id integer,
    solution_id character varying(63) NOT NULL,
    instrument_id integer,
    name character varying(100)
);


--
-- Name: instruments; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.instruments (
    instrument_id integer,
    id integer NOT NULL,
    user_id integer,
    solution_id character varying(63),
    name character varying(100),
    duration jsonb,
    capacity integer,
    features jsonb
);


--
-- Name: instruments_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.instruments_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: instruments_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.instruments_id_seq OWNED BY public.instruments.id;


--
-- Name: room_index_mapping; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.room_index_mapping (
    index integer NOT NULL,
    user_id integer,
    solution_id character varying(63) NOT NULL,
    room_id integer,
    name character varying(100)
);


--
-- Name: rooms; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.rooms (
    room_id integer,
    id integer NOT NULL,
    user_id integer,
    solution_id character varying(63),
    name character varying(100),
    capacity integer,
    features jsonb
);


--
-- Name: rooms_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.rooms_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: rooms_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.rooms_id_seq OWNED BY public.rooms.id;


--
-- Name: solution_assignments; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.solution_assignments (
    id integer NOT NULL,
    user_id integer,
    solution_id character varying(63),
    class_name character varying(100),
    start_time integer,
    end_time integer,
    room_id integer,
    max_capacity integer,
    current_capacity integer,
    teacher_id integer,
    contract_type integer,
    load integer,
    student_id integer,
    instrument_penalty integer,
    antiquity_day_penalty integer,
    antiquity_deviation_penalty integer,
    sibling_mismatch_penalty integer
);


--
-- Name: solution_assignments_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.solution_assignments_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: solution_assignments_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.solution_assignments_id_seq OWNED BY public.solution_assignments.id;


--
-- Name: solution_insights; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.solution_insights (
    id integer NOT NULL,
    user_id integer,
    solution_id character varying(63),
    workload_balance_index double precision,
    daily_workload_deviation jsonb,
    underutilized_teachers jsonb,
    overloaded_teachers jsonb,
    student_distribution_score double precision,
    room_utilization_rate double precision,
    peak_hour_congestion jsonb,
    room_underuse jsonb,
    missing_course_students jsonb,
    missing_instrument_students jsonb
);


--
-- Name: solution_insights_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.solution_insights_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: solution_insights_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.solution_insights_id_seq OWNED BY public.solution_insights.id;


--
-- Name: solutions; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.solutions (
    user_id integer NOT NULL,
    solution_id character varying(63) NOT NULL,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: student_count; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.student_count (
    time_slot integer NOT NULL,
    user_id integer,
    solution_id character varying(63) NOT NULL,
    students integer
);


--
-- Name: student_index_mapping; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.student_index_mapping (
    index integer NOT NULL,
    user_id integer,
    solution_id character varying(63) NOT NULL,
    student_id integer,
    name character varying(100)
);


--
-- Name: students; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.students (
    student_id integer,
    id integer NOT NULL,
    user_id integer,
    solution_id character varying(63),
    name character varying(100),
    availability jsonb,
    antiquity jsonb,
    siblings jsonb,
    courses jsonb,
    instruments jsonb
);


--
-- Name: students_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.students_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: students_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.students_id_seq OWNED BY public.students.id;


--
-- Name: teacher_index_mapping; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.teacher_index_mapping (
    index integer NOT NULL,
    user_id integer,
    solution_id character varying(63) NOT NULL,
    teacher_id integer,
    name character varying(100)
);


--
-- Name: teachers; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.teachers (
    teacher_id integer,
    id integer NOT NULL,
    user_id integer,
    solution_id character varying(63),
    name character varying(100),
    availability jsonb,
    contract jsonb,
    courses jsonb,
    instruments jsonb
);


--
-- Name: teachers_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.teachers_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: teachers_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.teachers_id_seq OWNED BY public.teachers.id;


--
-- Name: temp_course_index_mapping; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.temp_course_index_mapping (
    index integer NOT NULL,
    user_id integer,
    solution_id character varying(63) NOT NULL,
    course_id integer,
    name character varying(100)
);


--
-- Name: temp_input; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.temp_input (
    user_id integer NOT NULL,
    solution_id character varying(63) NOT NULL,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: temp_instrument_index_mapping; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.temp_instrument_index_mapping (
    index integer NOT NULL,
    user_id integer,
    solution_id character varying(63) NOT NULL,
    instrument_id integer,
    name character varying(100)
);


--
-- Name: temp_room_index_mapping; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.temp_room_index_mapping (
    index integer NOT NULL,
    user_id integer,
    solution_id character varying(63) NOT NULL,
    room_id integer,
    name character varying(100)
);


--
-- Name: temp_solution_assignments; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.temp_solution_assignments (
    id integer NOT NULL,
    user_id integer,
    solution_id character varying(63),
    class_name character varying(100),
    start_time integer,
    end_time integer,
    room_id integer,
    max_capacity integer,
    current_capacity integer,
    teacher_id integer,
    contract_type integer,
    load integer,
    student_id integer,
    instrument_penalty integer,
    antiquity_day_penalty integer,
    antiquity_deviation_penalty integer,
    sibling_mismatch_penalty integer
);


--
-- Name: temp_solution_assignments_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.temp_solution_assignments_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: temp_solution_assignments_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.temp_solution_assignments_id_seq OWNED BY public.temp_solution_assignments.id;


--
-- Name: temp_solution_insights; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.temp_solution_insights (
    id integer NOT NULL,
    user_id integer,
    solution_id character varying(63),
    workload_balance_index double precision,
    daily_workload_deviation jsonb,
    underutilized_teachers jsonb,
    overloaded_teachers jsonb,
    student_distribution_score double precision,
    room_utilization_rate double precision,
    peak_hour_congestion jsonb,
    room_underuse jsonb,
    missing_course_students jsonb,
    missing_instrument_students jsonb
);


--
-- Name: temp_solution_insights_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.temp_solution_insights_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: temp_solution_insights_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.temp_solution_insights_id_seq OWNED BY public.temp_solution_insights.id;


--
-- Name: temp_solutions; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.temp_solutions (
    user_id integer NOT NULL,
    solution_id character varying(63) NOT NULL,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: temp_student_count; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.temp_student_count (
    time_slot integer NOT NULL,
    user_id integer,
    solution_id character varying(63) NOT NULL,
    students integer
);


--
-- Name: temp_student_index_mapping; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.temp_student_index_mapping (
    index integer NOT NULL,
    user_id integer,
    solution_id character varying(63) NOT NULL,
    student_id integer,
    name character varying(100)
);


--
-- Name: temp_teacher_index_mapping; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.temp_teacher_index_mapping (
    index integer NOT NULL,
    user_id integer,
    solution_id character varying(63) NOT NULL,
    teacher_id integer,
    name character varying(100)
);


--
-- Name: users; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.users (
    user_id integer NOT NULL,
    username character varying(100) NOT NULL,
    hashed_password character varying(200) NOT NULL,
    name character varying(100),
    surname character varying(100),
    email character varying(150),
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: users_user_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.users_user_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: users_user_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.users_user_id_seq OWNED BY public.users.user_id;


--
-- Name: courses id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.courses ALTER COLUMN id SET DEFAULT nextval('public.courses_id_seq'::regclass);


--
-- Name: instruments id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.instruments ALTER COLUMN id SET DEFAULT nextval('public.instruments_id_seq'::regclass);


--
-- Name: rooms id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.rooms ALTER COLUMN id SET DEFAULT nextval('public.rooms_id_seq'::regclass);


--
-- Name: solution_assignments id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.solution_assignments ALTER COLUMN id SET DEFAULT nextval('public.solution_assignments_id_seq'::regclass);


--
-- Name: solution_insights id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.solution_insights ALTER COLUMN id SET DEFAULT nextval('public.solution_insights_id_seq'::regclass);


--
-- Name: students id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.students ALTER COLUMN id SET DEFAULT nextval('public.students_id_seq'::regclass);


--
-- Name: teachers id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.teachers ALTER COLUMN id SET DEFAULT nextval('public.teachers_id_seq'::regclass);


--
-- Name: temp_solution_assignments id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.temp_solution_assignments ALTER COLUMN id SET DEFAULT nextval('public.temp_solution_assignments_id_seq'::regclass);


--
-- Name: temp_solution_insights id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.temp_solution_insights ALTER COLUMN id SET DEFAULT nextval('public.temp_solution_insights_id_seq'::regclass);


--
-- Name: users user_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users ALTER COLUMN user_id SET DEFAULT nextval('public.users_user_id_seq'::regclass);


--
-- Data for Name: course_index_mapping; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.course_index_mapping (index, user_id, solution_id, course_id, name) FROM stdin;
0	1	temp_sol	401	music 1
1	1	temp_sol	402	music 2
2	1	temp_sol	403	music 3
3	1	temp_sol	404	choir
0	1	sample_data	401	music 1
1	1	sample_data	402	music 2
2	1	sample_data	403	music 3
3	1	sample_data	404	choir
\.


--
-- Data for Name: courses; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.courses (course_id, id, user_id, solution_id, name, duration, capacity, features) FROM stdin;
401	1	1	temp_sol	music 1	[2, 60]	15	["desks", "projector", "whiteboard"]
402	2	1	temp_sol	music 2	[2, 90]	12	["desks", "whiteboard"]
403	3	1	temp_sol	music 3	[1, 120]	10	["projector", "desks", "whiteboard"]
404	4	1	temp_sol	choir	[1, 60]	20	["microphones", "soundproof walls"]
\.


--
-- Data for Name: instrument_index_mapping; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.instrument_index_mapping (index, user_id, solution_id, instrument_id, name) FROM stdin;
0	1	temp_sol	501	guitar
1	1	temp_sol	502	piano
2	1	temp_sol	503	drums
3	1	temp_sol	504	violin
4	1	temp_sol	505	flute
5	1	temp_sol	506	clarinet
6	1	temp_sol	507	cello
7	1	temp_sol	508	trumpet
0	1	sample_data	501	guitar
1	1	sample_data	502	piano
2	1	sample_data	503	drums
3	1	sample_data	504	violin
4	1	sample_data	505	flute
5	1	sample_data	506	clarinet
6	1	sample_data	507	cello
7	1	sample_data	508	trumpet
\.


--
-- Data for Name: instruments; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.instruments (instrument_id, id, user_id, solution_id, name, duration, capacity, features) FROM stdin;
501	1	1	temp_sol	guitar	[1, 45]	3	["music stands", "amplifier", "projector"]
502	2	1	temp_sol	piano	[1, 60]	2	["piano", "microphones"]
503	3	1	temp_sol	drums	[1, 90]	2	["drums", "soundproof walls"]
504	4	1	temp_sol	violin	[1, 30]	4	["music stands", "whiteboard"]
505	5	1	temp_sol	flute	[1, 90]	2	["music stands"]
506	6	1	temp_sol	clarinet	[1, 30]	4	["soundproof walls", "music stands"]
507	7	1	temp_sol	cello	[1, 45]	1	["cello", "music stands"]
508	8	1	temp_sol	trumpet	[1, 90]	1	["desks", "music stands"]
\.


--
-- Data for Name: room_index_mapping; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.room_index_mapping (index, user_id, solution_id, room_id, name) FROM stdin;
0	1	temp_sol	301	Room A
1	1	temp_sol	302	Room B
2	1	temp_sol	303	Room C
3	1	temp_sol	304	Room D
0	1	sample_data	301	Room A
1	1	sample_data	302	Room B
2	1	sample_data	303	Room C
3	1	sample_data	304	Room D
\.


--
-- Data for Name: rooms; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.rooms (room_id, id, user_id, solution_id, name, capacity, features) FROM stdin;
301	1	1	temp_sol	Room A	20	["piano", "projector", "whiteboard", "desks", "music stands", "drums", "amplifier", "soundproof walls", "cello", "microphones"]
302	2	1	temp_sol	Room B	15	["drums", "amplifier", "soundproof walls", "music stands"]
303	3	1	temp_sol	Room C	12	["cello", "microphones", "projector", "music stands"]
304	4	1	temp_sol	Room D	25	["desks", "projector", "whiteboard"]
\.


--
-- Data for Name: solution_assignments; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.solution_assignments (id, user_id, solution_id, class_name, start_time, end_time, room_id, max_capacity, current_capacity, teacher_id, contract_type, load, student_id, instrument_penalty, antiquity_day_penalty, antiquity_deviation_penalty, sibling_mismatch_penalty) FROM stdin;
1	1	temp_sol	Course 0	15	18	0	15	1	0	60	50	7	0	1	0	0
2	1	temp_sol	Course 0	21	24	0	15	2	1	80	35	4	0	2	0	0
3	1	temp_sol	Course 0	21	24	0	15	2	1	80	35	14	0	2	0	0
4	1	temp_sol	Course 0	69	72	0	15	3	1	80	35	4	0	2	0	0
5	1	temp_sol	Course 0	69	72	0	15	3	1	80	35	7	0	2	0	0
6	1	temp_sol	Course 0	69	72	0	15	3	1	80	35	14	0	2	0	0
7	1	temp_sol	Course 1	5	10	0	12	1	0	60	50	0	0	2	0	0
8	1	temp_sol	Course 1	49	54	0	12	2	0	60	50	0	0	2	0	0
9	1	temp_sol	Course 1	49	54	0	12	2	0	60	50	6	0	2	0	0
10	1	temp_sol	Course 1	81	86	0	12	1	0	60	50	6	0	1	0	0
11	1	temp_sol	Course 2	29	36	0	10	1	1	80	35	2	0	1	0	0
12	1	temp_sol	Course 2	41	48	0	10	1	0	60	50	9	0	1	0	0
13	1	temp_sol	Course 3	73	76	0	20	1	0	60	50	5	0	1	0	0
14	1	temp_sol	Course 3	87	90	0	20	2	1	80	35	1	0	1	0	0
15	1	temp_sol	Course 3	87	90	0	20	2	1	80	35	11	0	1	0	0
16	1	temp_sol	Course 3	93	96	0	20	1	1	80	35	8	0	1	0	0
17	1	temp_sol	Instrument 0	56	58	0	3	1	0	60	50	1	0	1	0	0
18	1	temp_sol	Instrument 0	64	66	0	3	1	1	80	35	7	0	1	0	0
19	1	temp_sol	Instrument 1	1	4	0	2	2	0	60	50	0	0	2	0	0
20	1	temp_sol	Instrument 1	1	4	0	2	2	0	60	50	10	0	2	0	0
21	1	temp_sol	Instrument 1	25	28	0	2	2	1	80	35	4	0	2	0	0
22	1	temp_sol	Instrument 1	25	28	0	2	2	1	80	35	14	0	2	0	0
23	1	temp_sol	Instrument 3	67	68	0	4	2	1	80	35	5	0	1	0	0
24	1	temp_sol	Instrument 3	67	68	0	4	2	1	80	35	9	0	1	0	0
25	1	temp_sol	Instrument 5	91	92	0	4	2	1	80	35	3	1	1	0	0
26	1	temp_sol	Instrument 5	91	92	0	4	2	1	80	35	13	1	1	0	0
27	1	temp_sol	Instrument 2	23	28	1	2	1	0	60	50	2	0	1	0	0
28	1	temp_sol	Instrument 6	69	71	1	1	1	0	60	50	12	0	1	0	0
29	1	sample_data	Course 0	15	18	0	15	1	0	60	50	7	0	1	0	0
30	1	sample_data	Course 0	21	24	0	15	2	1	80	35	4	0	2	0	0
31	1	sample_data	Course 0	21	24	0	15	2	1	80	35	14	0	2	0	0
32	1	sample_data	Course 0	69	72	0	15	3	1	80	35	4	0	2	0	0
33	1	sample_data	Course 0	69	72	0	15	3	1	80	35	7	0	2	0	0
34	1	sample_data	Course 0	69	72	0	15	3	1	80	35	14	0	2	0	0
35	1	sample_data	Course 1	5	10	0	12	1	0	60	50	0	0	2	0	0
36	1	sample_data	Course 1	49	54	0	12	2	0	60	50	0	0	2	0	0
37	1	sample_data	Course 1	49	54	0	12	2	0	60	50	6	0	2	0	0
38	1	sample_data	Course 1	81	86	0	12	1	0	60	50	6	0	1	0	0
39	1	sample_data	Course 2	29	36	0	10	1	1	80	35	2	0	1	0	0
40	1	sample_data	Course 2	41	48	0	10	1	0	60	50	9	0	1	0	0
41	1	sample_data	Course 3	73	76	0	20	1	0	60	50	5	0	1	0	0
42	1	sample_data	Course 3	87	90	0	20	2	1	80	35	1	0	1	0	0
43	1	sample_data	Course 3	87	90	0	20	2	1	80	35	11	0	1	0	0
44	1	sample_data	Course 3	93	96	0	20	1	1	80	35	8	0	1	0	0
45	1	sample_data	Instrument 0	56	58	0	3	1	0	60	50	1	0	1	0	0
46	1	sample_data	Instrument 0	64	66	0	3	1	1	80	35	7	0	1	0	0
47	1	sample_data	Instrument 1	1	4	0	2	2	0	60	50	0	0	2	0	0
48	1	sample_data	Instrument 1	1	4	0	2	2	0	60	50	10	0	2	0	0
49	1	sample_data	Instrument 1	25	28	0	2	2	1	80	35	4	0	2	0	0
50	1	sample_data	Instrument 1	25	28	0	2	2	1	80	35	14	0	2	0	0
51	1	sample_data	Instrument 3	67	68	0	4	2	1	80	35	5	0	1	0	0
52	1	sample_data	Instrument 3	67	68	0	4	2	1	80	35	9	0	1	0	0
53	1	sample_data	Instrument 5	91	92	0	4	2	1	80	35	3	1	1	0	0
54	1	sample_data	Instrument 5	91	92	0	4	2	1	80	35	13	1	1	0	0
55	1	sample_data	Instrument 2	23	28	1	2	1	0	60	50	2	0	1	0	0
56	1	sample_data	Instrument 6	69	71	1	1	1	0	60	50	12	0	1	0	0
\.


--
-- Data for Name: solution_insights; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.solution_insights (id, user_id, solution_id, workload_balance_index, daily_workload_deviation, underutilized_teachers, overloaded_teachers, student_distribution_score, room_utilization_rate, peak_hour_congestion, room_underuse, missing_course_students, missing_instrument_students) FROM stdin;
1	1	temp_sol	0.048765984909417075	"{\\"0\\": 3.6782348707914077, \\"1\\": 3.9378339157095508}"	"{\\"0\\": 0.8333333333333334, \\"1\\": 0.4375}"	"{}"	0.47140452079103173	0.5277777777777778	"{\\"69\\": 4, \\"1\\": 2, \\"87\\": 2, \\"21\\": 2, \\"49\\": 2, \\"25\\": 2, \\"67\\": 2, \\"91\\": 2, \\"5\\": 1, \\"15\\": 1, \\"56\\": 1, \\"41\\": 1, \\"29\\": 1, \\"23\\": 1, \\"73\\": 1, \\"64\\": 1, \\"81\\": 1, \\"93\\": 1}"	"{\\"0\\": 1.1, \\"1\\": 0.09}"	"[3, 10, 12, 13]"	"[6, 8, 11]"
2	1	sample_data	0.048765984909417075	"{\\"0\\": 3.6782348707914077, \\"1\\": 3.9378339157095508}"	"{\\"0\\": 0.8333333333333334, \\"1\\": 0.4375}"	"{}"	0.47140452079103173	0.5277777777777778	"{\\"69\\": 4, \\"1\\": 2, \\"87\\": 2, \\"21\\": 2, \\"49\\": 2, \\"25\\": 2, \\"67\\": 2, \\"91\\": 2, \\"5\\": 1, \\"15\\": 1, \\"56\\": 1, \\"41\\": 1, \\"29\\": 1, \\"23\\": 1, \\"73\\": 1, \\"64\\": 1, \\"81\\": 1, \\"93\\": 1}"	"{\\"0\\": 1.1, \\"1\\": 0.09}"	"[3, 10, 12, 13]"	"[6, 8, 11]"
\.


--
-- Data for Name: solutions; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.solutions (user_id, solution_id, created_at) FROM stdin;
1	temp_sol	2025-09-01 16:52:45.470313
1	sample_data	2025-09-01 17:00:52.617435
\.


--
-- Data for Name: student_count; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.student_count (time_slot, user_id, solution_id, students) FROM stdin;
0	1	temp_sol	0
1	1	temp_sol	2
2	1	temp_sol	2
3	1	temp_sol	2
4	1	temp_sol	2
5	1	temp_sol	1
6	1	temp_sol	1
7	1	temp_sol	1
8	1	temp_sol	1
9	1	temp_sol	1
10	1	temp_sol	1
11	1	temp_sol	0
12	1	temp_sol	0
13	1	temp_sol	0
14	1	temp_sol	0
15	1	temp_sol	1
16	1	temp_sol	1
17	1	temp_sol	1
18	1	temp_sol	1
19	1	temp_sol	0
20	1	temp_sol	0
21	1	temp_sol	2
22	1	temp_sol	2
23	1	temp_sol	3
24	1	temp_sol	3
25	1	temp_sol	3
26	1	temp_sol	3
27	1	temp_sol	3
28	1	temp_sol	3
29	1	temp_sol	1
30	1	temp_sol	1
31	1	temp_sol	1
32	1	temp_sol	1
33	1	temp_sol	1
34	1	temp_sol	1
35	1	temp_sol	1
36	1	temp_sol	1
37	1	temp_sol	0
38	1	temp_sol	0
39	1	temp_sol	0
40	1	temp_sol	0
41	1	temp_sol	1
42	1	temp_sol	1
43	1	temp_sol	1
44	1	temp_sol	1
45	1	temp_sol	1
46	1	temp_sol	1
47	1	temp_sol	1
48	1	temp_sol	1
49	1	temp_sol	2
50	1	temp_sol	2
51	1	temp_sol	2
52	1	temp_sol	2
53	1	temp_sol	2
54	1	temp_sol	2
55	1	temp_sol	0
56	1	temp_sol	1
57	1	temp_sol	1
58	1	temp_sol	1
59	1	temp_sol	0
60	1	temp_sol	0
61	1	temp_sol	0
62	1	temp_sol	0
63	1	temp_sol	0
64	1	temp_sol	1
65	1	temp_sol	1
66	1	temp_sol	1
67	1	temp_sol	2
68	1	temp_sol	2
69	1	temp_sol	4
70	1	temp_sol	4
71	1	temp_sol	4
72	1	temp_sol	3
73	1	temp_sol	1
74	1	temp_sol	1
75	1	temp_sol	1
76	1	temp_sol	1
77	1	temp_sol	0
78	1	temp_sol	0
79	1	temp_sol	0
80	1	temp_sol	0
81	1	temp_sol	1
82	1	temp_sol	1
83	1	temp_sol	1
84	1	temp_sol	1
85	1	temp_sol	1
86	1	temp_sol	1
87	1	temp_sol	2
88	1	temp_sol	2
89	1	temp_sol	2
90	1	temp_sol	2
91	1	temp_sol	2
92	1	temp_sol	2
93	1	temp_sol	1
94	1	temp_sol	1
95	1	temp_sol	1
96	1	temp_sol	1
97	1	temp_sol	0
98	1	temp_sol	0
99	1	temp_sol	0
0	1	sample_data	0
1	1	sample_data	2
2	1	sample_data	2
3	1	sample_data	2
4	1	sample_data	2
5	1	sample_data	1
6	1	sample_data	1
7	1	sample_data	1
8	1	sample_data	1
9	1	sample_data	1
10	1	sample_data	1
11	1	sample_data	0
12	1	sample_data	0
13	1	sample_data	0
14	1	sample_data	0
15	1	sample_data	1
16	1	sample_data	1
17	1	sample_data	1
18	1	sample_data	1
19	1	sample_data	0
20	1	sample_data	0
21	1	sample_data	2
22	1	sample_data	2
23	1	sample_data	3
24	1	sample_data	3
25	1	sample_data	3
26	1	sample_data	3
27	1	sample_data	3
28	1	sample_data	3
29	1	sample_data	1
30	1	sample_data	1
31	1	sample_data	1
32	1	sample_data	1
33	1	sample_data	1
34	1	sample_data	1
35	1	sample_data	1
36	1	sample_data	1
37	1	sample_data	0
38	1	sample_data	0
39	1	sample_data	0
40	1	sample_data	0
41	1	sample_data	1
42	1	sample_data	1
43	1	sample_data	1
44	1	sample_data	1
45	1	sample_data	1
46	1	sample_data	1
47	1	sample_data	1
48	1	sample_data	1
49	1	sample_data	2
50	1	sample_data	2
51	1	sample_data	2
52	1	sample_data	2
53	1	sample_data	2
54	1	sample_data	2
55	1	sample_data	0
56	1	sample_data	1
57	1	sample_data	1
58	1	sample_data	1
59	1	sample_data	0
60	1	sample_data	0
61	1	sample_data	0
62	1	sample_data	0
63	1	sample_data	0
64	1	sample_data	1
65	1	sample_data	1
66	1	sample_data	1
67	1	sample_data	2
68	1	sample_data	2
69	1	sample_data	4
70	1	sample_data	4
71	1	sample_data	4
72	1	sample_data	3
73	1	sample_data	1
74	1	sample_data	1
75	1	sample_data	1
76	1	sample_data	1
77	1	sample_data	0
78	1	sample_data	0
79	1	sample_data	0
80	1	sample_data	0
81	1	sample_data	1
82	1	sample_data	1
83	1	sample_data	1
84	1	sample_data	1
85	1	sample_data	1
86	1	sample_data	1
87	1	sample_data	2
88	1	sample_data	2
89	1	sample_data	2
90	1	sample_data	2
91	1	sample_data	2
92	1	sample_data	2
93	1	sample_data	1
94	1	sample_data	1
95	1	sample_data	1
96	1	sample_data	1
97	1	sample_data	0
98	1	sample_data	0
99	1	sample_data	0
\.


--
-- Data for Name: student_index_mapping; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.student_index_mapping (index, user_id, solution_id, student_id, name) FROM stdin;
0	1	temp_sol	101	Alice Johnson
1	1	temp_sol	102	Bob Johnson
2	1	temp_sol	103	Charlie Smith
3	1	temp_sol	104	Diana White
4	1	temp_sol	105	Ethan Brown
5	1	temp_sol	106	Fiona Brown
6	1	temp_sol	107	George Miller
7	1	temp_sol	108	Hannah Davis
8	1	temp_sol	109	Ian Wilson
9	1	temp_sol	110	Julia Anderson
10	1	temp_sol	111	Lionel Messi
11	1	temp_sol	112	Raphina
12	1	temp_sol	113	Lamine Yamal
13	1	temp_sol	114	Robert Lewandowsky
14	1	temp_sol	115	Dani Olmo
15	1	temp_sol	116	Frenkie de Jong
16	1	temp_sol	117	Pau Cubarsí
17	1	temp_sol	118	Iñígo Martínez
18	1	temp_sol	119	Jules Koundé
19	1	temp_sol	120	Alejandro Balde
20	1	temp_sol	121	Pau Víctor
21	1	temp_sol	122	Pablo Torre
22	1	temp_sol	123	Pedri González
23	1	temp_sol	124	Pablo Gavi
24	1	temp_sol	125	Ronald Araujo
25	1	temp_sol	126	Gerard Martín
26	1	temp_sol	127	Marc Casadó
27	1	temp_sol	128	Marc-André Ter Stegen
28	1	temp_sol	129	Hector Fort
29	1	temp_sol	130	Andreas Christensen
0	1	sample_data	101	Alice Johnson
1	1	sample_data	102	Bob Johnson
2	1	sample_data	103	Charlie Smith
3	1	sample_data	104	Diana White
4	1	sample_data	105	Ethan Brown
5	1	sample_data	106	Fiona Brown
6	1	sample_data	107	George Miller
7	1	sample_data	108	Hannah Davis
8	1	sample_data	109	Ian Wilson
9	1	sample_data	110	Julia Anderson
10	1	sample_data	111	Lionel Messi
11	1	sample_data	112	Raphina
12	1	sample_data	113	Lamine Yamal
13	1	sample_data	114	Robert Lewandowsky
14	1	sample_data	115	Dani Olmo
15	1	sample_data	116	Frenkie de Jong
16	1	sample_data	117	Pau Cubarsí
17	1	sample_data	118	Iñígo Martínez
18	1	sample_data	119	Jules Koundé
19	1	sample_data	120	Alejandro Balde
20	1	sample_data	121	Pau Víctor
21	1	sample_data	122	Pablo Torre
22	1	sample_data	123	Pedri González
23	1	sample_data	124	Pablo Gavi
24	1	sample_data	125	Ronald Araujo
25	1	sample_data	126	Gerard Martín
26	1	sample_data	127	Marc Casadó
27	1	sample_data	128	Marc-André Ter Stegen
28	1	sample_data	129	Hector Fort
29	1	sample_data	130	Andreas Christensen
\.


--
-- Data for Name: students; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.students (student_id, id, user_id, solution_id, name, availability, antiquity, siblings, courses, instruments) FROM stdin;
101	1	1	temp_sol	Alice Johnson	[["Mon", "16:00-19:00"], ["Wed", "17:00-20:30"], ["Fri", "16:30-18:30"]]	[["music theory 1", ["Tue", "17:30-18:30"], ["Thu", "17:30-18:30"]], ["guitar", ["Tue", "18:45-19:30"]]]	[102]	["music theory 2"]	["piano", "violin"]
102	2	1	temp_sol	Bob Johnson	[["Mon", "16:00-19:00"], ["Wed", "17:00-20:30"], ["Fri", "16:30-18:30"]]	[["guitar", ["Fri", "16:45-18:00"]]]	[101]	["choir"]	["guitar"]
103	3	1	temp_sol	Charlie Smith	[["Tue", "16:00-20:00"], ["Thu", "18:00-21:00"]]	[["music theory 2", ["Mon", "17:30-18:30"], ["Wed", "17:30-18:30"]], ["guitar", ["Fri", "19:45-20:30"]]]	[]	["music theory 3"]	["drums"]
104	4	1	temp_sol	Diana White	[["Mon", "16:30-20:00"], ["Fri", "17:00-19:30"]]	[["trumpet", ["Wed", "16:45-17:45"]]]	[]	["music theory 3"]	["flute", "clarinet"]
105	5	1	temp_sol	Ethan Brown	[["Tue", "16:00-19:00"], ["Thu", "17:30-20:30"], ["Fri", "16:00-18:00"]]	null	[106]	["music theory 1"]	["piano"]
106	6	1	temp_sol	Fiona Brown	[["Tue", "16:00-19:00"], ["Thu", "17:30-20:30"], ["Fri", "16:00-18:00"]]	null	[105]	["choir"]	["violin", "cello"]
107	7	1	temp_sol	George Miller	[["Wed", "16:00-19:30"], ["Fri", "16:00-18:00"]]	[["music theory 2", ["Mon", "17:30-18:30"], ["Wed", "17:30-18:30"]], ["guitar", ["Fri", "19:45-20:30"]]]	[]	["music theory 2"]	["trumpet"]
108	8	1	temp_sol	Hannah Davis	[["Mon", "17:00-20:30"], ["Thu", "16:00-19:30"]]	[["music theory 1", ["Tue", "17:30-18:30"], ["Thu", "17:30-18:30"]], ["guitar", ["Tue", "18:45-19:30"]]]	[]	["music theory 1"]	["guitar", "drums"]
109	9	1	temp_sol	Ian Wilson	[["Tue", "16:00-19:30"], ["Fri", "19:00-21:00"]]	null	[]	["choir"]	["piano"]
110	10	1	temp_sol	Julia Anderson	[["Wed", "16:00-18:30"], ["Thu", "17:00-20:00"]]	[["music theory 1", ["Tue", "17:30-18:30"], ["Thu", "17:30-18:30"]], ["guitar", ["Tue", "18:45-19:30"]]]	[]	["music theory 3"]	["violin", "guitar"]
111	11	1	temp_sol	Lionel Messi	[["Mon", "16:00-19:00"], ["Wed", "17:00-20:30"], ["Fri", "16:30-18:30"]]	null	[112]	["music theory 1"]	["piano"]
112	12	1	temp_sol	Raphina	[["Mon", "16:00-19:00"], ["Wed", "17:00-20:30"], ["Fri", "16:30-18:30"]]	null	[111]	["choir"]	["flute"]
113	13	1	temp_sol	Lamine Yamal	[["Tue", "16:00-20:00"], ["Thu", "18:00-21:00"]]	null	[]	["music theory 2"]	["cello", "flute"]
114	14	1	temp_sol	Robert Lewandowsky	[["Mon", "16:30-20:00"], ["Fri", "17:00-19:30"]]	null	[]	["music theory 3"]	["flute", "clarinet"]
115	15	1	temp_sol	Dani Olmo	[["Tue", "16:00-19:00"], ["Thu", "17:30-20:30"], ["Fri", "16:00-18:00"]]	null	[]	["music theory 1"]	["piano"]
116	16	1	temp_sol	Frenkie de Jong	[["Tue", "16:00-19:00"], ["Thu", "17:30-20:30"], ["Fri", "16:00-18:00"]]	null	[]	["choir"]	["violin", "cello"]
117	17	1	temp_sol	Pau Cubarsí	[["Wed", "16:00-19:30"], ["Fri", "16:00-18:00"]]	null	[]	["music theory 2"]	["trumpet"]
118	18	1	temp_sol	Iñígo Martínez	[["Mon", "17:00-20:30"], ["Thu", "16:00-19:30"]]	null	[]	["music theory 1"]	["guitar", "drums"]
119	19	1	temp_sol	Jules Koundé	[["Tue", "16:00-19:30"], ["Fri", "19:00-21:00"]]	null	[]	["choir"]	["piano"]
120	20	1	temp_sol	Alejandro Balde	[["Wed", "16:00-18:30"], ["Thu", "17:00-20:00"]]	[["music theory 1", ["Tue", "17:30-18:30"], ["Thu", "17:30-18:30"]], ["guitar", ["Tue", "18:45-19:30"]]]	[]	["music theory 3"]	["violin", "flute"]
121	21	1	temp_sol	Pau Víctor	[["Mon", "16:00-19:00"], ["Wed", "17:00-20:30"], ["Fri", "16:30-18:30"]]	[["music theory 2", ["Mon", "17:30-18:30"], ["Thu", "17:30-18:30"]], ["guitar", ["Thu", "16:30-17:30"]]]	[]	["music theory 1"]	["cello", "violin"]
122	22	1	temp_sol	Pablo Torre	[["Mon", "16:00-19:00"], ["Wed", "17:00-20:30"], ["Fri", "16:30-18:30"]]	[["music theory 2", ["Mon", "17:30-18:30"], ["Thu", "17:30-18:30"]], ["flute", ["Tue", "18:45-19:30"]]]	[]	["choir"]	["guitar"]
123	23	1	temp_sol	Pedri González	[["Tue", "16:00-20:00"], ["Thu", "18:00-21:00"]]	[["drums", ["Mon", "16:15-17:30"]]]	[]	["music theory 2"]	["drums"]
124	24	1	temp_sol	Pablo Gavi	[["Mon", "16:30-20:00"], ["Fri", "17:00-19:30"]]	[["drums", ["Mon", "16:15-17:30"]]]	[130]	["music theory 3"]	["flute", "clarinet"]
125	25	1	temp_sol	Ronald Araujo	[["Tue", "16:00-19:00"], ["Thu", "17:30-20:30"], ["Fri", "16:00-18:00"]]	[["cello", ["Thu", "16:15-17:30"]]]	[]	["music theory 1"]	["piano"]
126	26	1	temp_sol	Gerard Martín	[["Tue", "16:00-19:00"], ["Thu", "17:30-20:30"], ["Fri", "16:00-18:00"]]	null	[]	["choir"]	["violin", "trumpet"]
127	27	1	temp_sol	Marc Casadó	[["Wed", "16:00-19:30"], ["Fri", "16:00-18:00"]]	[["violin", ["Thu", "16:15-17:30"]]]	[]	["music theory 2"]	["trumpet"]
128	28	1	temp_sol	Marc-André Ter Stegen	[["Mon", "17:00-20:30"], ["Thu", "16:00-19:30"]]	[["violin", ["Thu", "16:15-17:30"]]]	[]	["music theory 1"]	["flute"]
129	29	1	temp_sol	Hector Fort	[["Tue", "16:00-19:30"], ["Fri", "19:00-21:00"]]	null	[]	["choir"]	["piano"]
130	30	1	temp_sol	Andreas Christensen	[["Wed", "16:00-18:30"], ["Thu", "17:00-20:00"]]	[["music theory 1", ["Tue", "17:30-18:30"], ["Thu", "17:30-18:30"]], ["guitar", ["Tue", "18:45-19:30"]]]	[124]	["music theory 3"]	["violin", "flute"]
\.


--
-- Data for Name: teacher_index_mapping; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.teacher_index_mapping (index, user_id, solution_id, teacher_id, name) FROM stdin;
0	1	temp_sol	201	Hansi Flick
1	1	temp_sol	202	Michael Rodriguez
2	1	temp_sol	203	Sophia Lee
3	1	temp_sol	204	David Patel
4	1	temp_sol	205	Andrés Iniesta
5	1	temp_sol	206	Neymar jr.
0	1	sample_data	201	Hansi Flick
1	1	sample_data	202	Michael Rodriguez
2	1	sample_data	203	Sophia Lee
3	1	sample_data	204	David Patel
4	1	sample_data	205	Andrés Iniesta
5	1	sample_data	206	Neymar jr.
\.


--
-- Data for Name: teachers; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.teachers (teacher_id, id, user_id, solution_id, name, availability, contract, courses, instruments) FROM stdin;
201	1	1	temp_sol	Hansi Flick	[["Mon", "16:00-20:30"], ["Tue", "16:00-20:30"], ["Wed", "16:00-20:30"], ["Thu", "16:00-20:30"], ["Fri", "16:00-20:30"]]	[900, 240]	["music theory 1", "music theory 3", "music theory 2", "choir"]	["piano", "guitar", "violin", "cello", "drums", "trumpet", "flute", "clarinet"]
202	2	1	temp_sol	Michael Rodriguez	[["Tue", "16:00-20:00"], ["Thu", "16:00-19:00"], ["Fri", "17:00-20:00"]]	[1200, 360]	["choir", "music theory 3"]	["violin", "cello"]
203	3	1	temp_sol	Sophia Lee	[["Mon", "16:00-20:00"], ["Wed", "16:00-19:30"], ["Fri", "16:00-18:30"]]	[1500, 300]	["music theory 1", "choir"]	["flute", "clarinet"]
204	4	1	temp_sol	David Patel	[["Tue", "16:00-19:00"], ["Thu", "17:00-20:00"], ["Fri", "18:00-21:00"]]	[1050, 270]	["music theory 2", "music theory 3"]	["drums", "trumpet"]
205	5	1	temp_sol	Andrés Iniesta	[["Mon", "16:00-19:30"], ["Tue", "16:00-18:30"], ["Wed", "17:00-20:30"]]	[900, 240]	["music theory 1", "music theory 2"]	["piano", "guitar"]
206	6	1	temp_sol	Neymar jr.	[["Tue", "16:00-20:00"], ["Thu", "16:00-19:00"], ["Fri", "17:00-20:00"]]	[1200, 360]	["choir", "music theory 3"]	["violin", "cello"]
\.


--
-- Data for Name: temp_course_index_mapping; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.temp_course_index_mapping (index, user_id, solution_id, course_id, name) FROM stdin;
\.


--
-- Data for Name: temp_input; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.temp_input (user_id, solution_id, created_at) FROM stdin;
\.


--
-- Data for Name: temp_instrument_index_mapping; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.temp_instrument_index_mapping (index, user_id, solution_id, instrument_id, name) FROM stdin;
\.


--
-- Data for Name: temp_room_index_mapping; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.temp_room_index_mapping (index, user_id, solution_id, room_id, name) FROM stdin;
\.


--
-- Data for Name: temp_solution_assignments; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.temp_solution_assignments (id, user_id, solution_id, class_name, start_time, end_time, room_id, max_capacity, current_capacity, teacher_id, contract_type, load, student_id, instrument_penalty, antiquity_day_penalty, antiquity_deviation_penalty, sibling_mismatch_penalty) FROM stdin;
\.


--
-- Data for Name: temp_solution_insights; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.temp_solution_insights (id, user_id, solution_id, workload_balance_index, daily_workload_deviation, underutilized_teachers, overloaded_teachers, student_distribution_score, room_utilization_rate, peak_hour_congestion, room_underuse, missing_course_students, missing_instrument_students) FROM stdin;
\.


--
-- Data for Name: temp_solutions; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.temp_solutions (user_id, solution_id, created_at) FROM stdin;
\.


--
-- Data for Name: temp_student_count; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.temp_student_count (time_slot, user_id, solution_id, students) FROM stdin;
\.


--
-- Data for Name: temp_student_index_mapping; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.temp_student_index_mapping (index, user_id, solution_id, student_id, name) FROM stdin;
\.


--
-- Data for Name: temp_teacher_index_mapping; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.temp_teacher_index_mapping (index, user_id, solution_id, teacher_id, name) FROM stdin;
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.users (user_id, username, hashed_password, name, surname, email, created_at) FROM stdin;
1	sample	$2b$12$Zj8c2K7/Xh.8annZxAVcTeN68lT5DW0iz/lFOwvvv5elL/wIOe/Ea	Sample	Data	sample@data.com	2025-09-01 16:52:07.491462
\.


--
-- Name: courses_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.courses_id_seq', 4, true);


--
-- Name: instruments_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.instruments_id_seq', 8, true);


--
-- Name: rooms_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.rooms_id_seq', 4, true);


--
-- Name: solution_assignments_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.solution_assignments_id_seq', 56, true);


--
-- Name: solution_insights_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.solution_insights_id_seq', 2, true);


--
-- Name: students_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.students_id_seq', 30, true);


--
-- Name: teachers_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.teachers_id_seq', 6, true);


--
-- Name: temp_solution_assignments_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.temp_solution_assignments_id_seq', 1, false);


--
-- Name: temp_solution_insights_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.temp_solution_insights_id_seq', 1, false);


--
-- Name: users_user_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.users_user_id_seq', 1, true);


--
-- Name: course_index_mapping course_index_mapping_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.course_index_mapping
    ADD CONSTRAINT course_index_mapping_pkey PRIMARY KEY (solution_id, index);


--
-- Name: courses courses_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.courses
    ADD CONSTRAINT courses_pkey PRIMARY KEY (id);


--
-- Name: instrument_index_mapping instrument_index_mapping_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.instrument_index_mapping
    ADD CONSTRAINT instrument_index_mapping_pkey PRIMARY KEY (solution_id, index);


--
-- Name: instruments instruments_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.instruments
    ADD CONSTRAINT instruments_pkey PRIMARY KEY (id);


--
-- Name: room_index_mapping room_index_mapping_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.room_index_mapping
    ADD CONSTRAINT room_index_mapping_pkey PRIMARY KEY (solution_id, index);


--
-- Name: rooms rooms_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.rooms
    ADD CONSTRAINT rooms_pkey PRIMARY KEY (id);


--
-- Name: solution_assignments solution_assignments_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.solution_assignments
    ADD CONSTRAINT solution_assignments_pkey PRIMARY KEY (id);


--
-- Name: solution_insights solution_insights_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.solution_insights
    ADD CONSTRAINT solution_insights_pkey PRIMARY KEY (id);


--
-- Name: solutions solutions_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.solutions
    ADD CONSTRAINT solutions_pkey PRIMARY KEY (user_id, solution_id);


--
-- Name: student_count student_count_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.student_count
    ADD CONSTRAINT student_count_pkey PRIMARY KEY (solution_id, time_slot);


--
-- Name: student_index_mapping student_index_mapping_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.student_index_mapping
    ADD CONSTRAINT student_index_mapping_pkey PRIMARY KEY (solution_id, index);


--
-- Name: students students_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.students
    ADD CONSTRAINT students_pkey PRIMARY KEY (id);


--
-- Name: teacher_index_mapping teacher_index_mapping_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.teacher_index_mapping
    ADD CONSTRAINT teacher_index_mapping_pkey PRIMARY KEY (solution_id, index);


--
-- Name: teachers teachers_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.teachers
    ADD CONSTRAINT teachers_pkey PRIMARY KEY (id);


--
-- Name: temp_course_index_mapping temp_course_index_mapping_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.temp_course_index_mapping
    ADD CONSTRAINT temp_course_index_mapping_pkey PRIMARY KEY (solution_id, index);


--
-- Name: temp_input temp_input_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.temp_input
    ADD CONSTRAINT temp_input_pkey PRIMARY KEY (user_id, solution_id);


--
-- Name: temp_instrument_index_mapping temp_instrument_index_mapping_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.temp_instrument_index_mapping
    ADD CONSTRAINT temp_instrument_index_mapping_pkey PRIMARY KEY (solution_id, index);


--
-- Name: temp_room_index_mapping temp_room_index_mapping_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.temp_room_index_mapping
    ADD CONSTRAINT temp_room_index_mapping_pkey PRIMARY KEY (solution_id, index);


--
-- Name: temp_solution_assignments temp_solution_assignments_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.temp_solution_assignments
    ADD CONSTRAINT temp_solution_assignments_pkey PRIMARY KEY (id);


--
-- Name: temp_solution_insights temp_solution_insights_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.temp_solution_insights
    ADD CONSTRAINT temp_solution_insights_pkey PRIMARY KEY (id);


--
-- Name: temp_solutions temp_solutions_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.temp_solutions
    ADD CONSTRAINT temp_solutions_pkey PRIMARY KEY (user_id, solution_id);


--
-- Name: temp_student_count temp_student_count_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.temp_student_count
    ADD CONSTRAINT temp_student_count_pkey PRIMARY KEY (solution_id, time_slot);


--
-- Name: temp_student_index_mapping temp_student_index_mapping_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.temp_student_index_mapping
    ADD CONSTRAINT temp_student_index_mapping_pkey PRIMARY KEY (solution_id, index);


--
-- Name: temp_teacher_index_mapping temp_teacher_index_mapping_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.temp_teacher_index_mapping
    ADD CONSTRAINT temp_teacher_index_mapping_pkey PRIMARY KEY (solution_id, index);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (user_id);


--
-- Name: users users_username_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_username_key UNIQUE (username);


--
-- Name: course_index_mapping course_index_mapping_user_id_solution_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.course_index_mapping
    ADD CONSTRAINT course_index_mapping_user_id_solution_id_fkey FOREIGN KEY (user_id, solution_id) REFERENCES public.solutions(user_id, solution_id);


--
-- Name: courses courses_user_id_solution_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.courses
    ADD CONSTRAINT courses_user_id_solution_id_fkey FOREIGN KEY (user_id, solution_id) REFERENCES public.solutions(user_id, solution_id);


--
-- Name: instrument_index_mapping instrument_index_mapping_user_id_solution_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.instrument_index_mapping
    ADD CONSTRAINT instrument_index_mapping_user_id_solution_id_fkey FOREIGN KEY (user_id, solution_id) REFERENCES public.solutions(user_id, solution_id);


--
-- Name: instruments instruments_user_id_solution_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.instruments
    ADD CONSTRAINT instruments_user_id_solution_id_fkey FOREIGN KEY (user_id, solution_id) REFERENCES public.solutions(user_id, solution_id);


--
-- Name: room_index_mapping room_index_mapping_user_id_solution_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.room_index_mapping
    ADD CONSTRAINT room_index_mapping_user_id_solution_id_fkey FOREIGN KEY (user_id, solution_id) REFERENCES public.solutions(user_id, solution_id);


--
-- Name: rooms rooms_user_id_solution_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.rooms
    ADD CONSTRAINT rooms_user_id_solution_id_fkey FOREIGN KEY (user_id, solution_id) REFERENCES public.solutions(user_id, solution_id);


--
-- Name: solution_assignments solution_assignments_user_id_solution_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.solution_assignments
    ADD CONSTRAINT solution_assignments_user_id_solution_id_fkey FOREIGN KEY (user_id, solution_id) REFERENCES public.solutions(user_id, solution_id);


--
-- Name: solution_insights solution_insights_user_id_solution_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.solution_insights
    ADD CONSTRAINT solution_insights_user_id_solution_id_fkey FOREIGN KEY (user_id, solution_id) REFERENCES public.solutions(user_id, solution_id);


--
-- Name: solutions solutions_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.solutions
    ADD CONSTRAINT solutions_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(user_id);


--
-- Name: student_count student_count_user_id_solution_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.student_count
    ADD CONSTRAINT student_count_user_id_solution_id_fkey FOREIGN KEY (user_id, solution_id) REFERENCES public.solutions(user_id, solution_id);


--
-- Name: student_index_mapping student_index_mapping_user_id_solution_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.student_index_mapping
    ADD CONSTRAINT student_index_mapping_user_id_solution_id_fkey FOREIGN KEY (user_id, solution_id) REFERENCES public.solutions(user_id, solution_id);


--
-- Name: students students_user_id_solution_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.students
    ADD CONSTRAINT students_user_id_solution_id_fkey FOREIGN KEY (user_id, solution_id) REFERENCES public.solutions(user_id, solution_id);


--
-- Name: teacher_index_mapping teacher_index_mapping_user_id_solution_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.teacher_index_mapping
    ADD CONSTRAINT teacher_index_mapping_user_id_solution_id_fkey FOREIGN KEY (user_id, solution_id) REFERENCES public.solutions(user_id, solution_id);


--
-- Name: teachers teachers_user_id_solution_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.teachers
    ADD CONSTRAINT teachers_user_id_solution_id_fkey FOREIGN KEY (user_id, solution_id) REFERENCES public.solutions(user_id, solution_id);


--
-- Name: temp_course_index_mapping temp_course_index_mapping_user_id_solution_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.temp_course_index_mapping
    ADD CONSTRAINT temp_course_index_mapping_user_id_solution_id_fkey FOREIGN KEY (user_id, solution_id) REFERENCES public.temp_solutions(user_id, solution_id);


--
-- Name: temp_instrument_index_mapping temp_instrument_index_mapping_user_id_solution_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.temp_instrument_index_mapping
    ADD CONSTRAINT temp_instrument_index_mapping_user_id_solution_id_fkey FOREIGN KEY (user_id, solution_id) REFERENCES public.temp_solutions(user_id, solution_id);


--
-- Name: temp_room_index_mapping temp_room_index_mapping_user_id_solution_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.temp_room_index_mapping
    ADD CONSTRAINT temp_room_index_mapping_user_id_solution_id_fkey FOREIGN KEY (user_id, solution_id) REFERENCES public.temp_solutions(user_id, solution_id);


--
-- Name: temp_solution_assignments temp_solution_assignments_user_id_solution_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.temp_solution_assignments
    ADD CONSTRAINT temp_solution_assignments_user_id_solution_id_fkey FOREIGN KEY (user_id, solution_id) REFERENCES public.temp_solutions(user_id, solution_id);


--
-- Name: temp_solution_insights temp_solution_insights_user_id_solution_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.temp_solution_insights
    ADD CONSTRAINT temp_solution_insights_user_id_solution_id_fkey FOREIGN KEY (user_id, solution_id) REFERENCES public.temp_solutions(user_id, solution_id);


--
-- Name: temp_student_count temp_student_count_user_id_solution_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.temp_student_count
    ADD CONSTRAINT temp_student_count_user_id_solution_id_fkey FOREIGN KEY (user_id, solution_id) REFERENCES public.temp_solutions(user_id, solution_id);


--
-- Name: temp_student_index_mapping temp_student_index_mapping_user_id_solution_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.temp_student_index_mapping
    ADD CONSTRAINT temp_student_index_mapping_user_id_solution_id_fkey FOREIGN KEY (user_id, solution_id) REFERENCES public.temp_solutions(user_id, solution_id);


--
-- Name: temp_teacher_index_mapping temp_teacher_index_mapping_user_id_solution_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.temp_teacher_index_mapping
    ADD CONSTRAINT temp_teacher_index_mapping_user_id_solution_id_fkey FOREIGN KEY (user_id, solution_id) REFERENCES public.temp_solutions(user_id, solution_id);


--
-- PostgreSQL database dump complete
--

