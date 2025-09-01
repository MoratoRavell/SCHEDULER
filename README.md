# SCHEDULER
A scheduling web app that optimizes student–teacher–room assignments using OR-Tools, built with React (frontend), FastAPI (backend), and PostgreSQL (database).

Example covering a real case for a music school in Barcelona.

## App Functionalities
- Loading data and running the optimization model
- Accessing the computed solution and useful solution insights
- Storing and loading precomputed solutions under the user's account

## Features
- User login system (FastAPI + JWT auth)
- Automatic scheduling using Google OR-Tools (CP-SAT solver)
- Database storage of solutions with save/load functionality
- Database integration with PostgreSQL
- Interactive calendar to visualize class schedules
- Insights cards for an in-depth analysis of the solution

## Tech Stack
- **Frontend:** React, TailwindCSS, ShadCN UI
- **Backend:** FastAPI (Python), OR-Tools
- **Database:** PostgreSQL

## Repository Structure
```
frontend/   - React app
backend/    - Optimization model
db/         - Database schema
docs/       - Screenshots, diagrams, and additional documentation
```


## HOW TO RUN LOCALLY
_None of this has yet been tested_

### 1. Clone the repository
```bash
git clone https://github.com/MoratoRavell/SCHEDULER.git
cd SCHEDULER
```
## 2. Run Everything with Docker Compose
```bash
docker-compose up --build
```
The database schema and example in db/init.example.sql are automatically loaded.

This will start the **frontend (React)**, **backend (FastAPI)**, and **Postgres database** together.

## 3. Sample data
Use user 'sample' and password 'Sample1234' to access a precomputed solution using sample data. Load the sample_data solution.

_Delete before uploading_
To create the sample database file (init.example.sql) run the following prompt inside the project's folder:

pg_dump -U your_user -d scheduling_app -f db/init.example.sql --no-owner
_Current sample database needs revising_



## SREENSHOTS
_Screenshots/GIFs of the app's UI here (TO DO)_  
- Load data/Load precomputed solution:
- Compute solution (run model):
- Solution assignments:
- Solution insights: 



## WHAT I LEARNED
- Taught myself **React** from zero to build the frontend and connect it to the backend
- Learned **databases and SQL** from scratch to design schema, queries, and integrations
- How to integrate **React + FastAPI + PostgreSQL** in a full-stack app
- Applied **optimization with OR-Tools** to real scheduling problems
- Built Dockerized environments for reproducibility



## LICENSE
This project is licensed under the MIT License.
