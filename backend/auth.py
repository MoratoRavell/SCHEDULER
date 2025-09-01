from fastapi import APIRouter, HTTPException, Response, Request
from fastapi.responses import JSONResponse

from pydantic import BaseModel, EmailStr
from passlib.context import CryptContext
from jose import jwt
import time
import psycopg2
import psycopg2.extras
from typing import Optional


# Secret key for JWT
SECRET_KEY = "CHANGE_THIS_TO_A_RANDOM_SECRET"

# Setup password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# Define API router
router = APIRouter()


# Database connection
def connect_to_db():
    return psycopg2.connect(
        dbname="scheduling_app",
        user="postgres",
        password="221214",
        host="localhost",
        port="5432"
    )


# Request model
class UserCreate(BaseModel):
    username: str
    password: str
    name: str
    surname: str
    email: EmailStr

class LoginUser(BaseModel):
    username: str
    password: str


@router.post("/signup")
def signup(user: UserCreate):
    conn = connect_to_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    cur.execute("SELECT * FROM users WHERE username = %s", (user.username,))
    if cur.fetchone():
        conn.close()
        raise HTTPException(status_code=400, detail="Username already taken")

    hashed_pw = pwd_context.hash(user.password)
    cur.execute("""
        INSERT INTO users (username, hashed_password, name, surname, email)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING user_id
    """, (user.username, hashed_pw, user.name, user.surname, user.email))

    user_id = cur.fetchone()[0]
    conn.commit()
    conn.close()

    return {"msg": "User created successfully", "user_id": user_id}


@router.post("/login")
def login(user: LoginUser, response: Response):
    conn = connect_to_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    cur.execute("SELECT * FROM users WHERE username = %s", (user.username,))
    row = cur.fetchone()
    conn.close()

    if not row or not pwd_context.verify(user.password, row["hashed_password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    user_id = row["user_id"]
    token = jwt.encode({"user_id": user_id, "exp": time.time() + 60*60*6}, SECRET_KEY, algorithm="HS256")
    response.set_cookie(key="auth", value=token, httponly=True, max_age=60*60*6)

    return {"user_id": user_id}


@router.post("/logout")
def logout(response: Response):
    response.delete_cookie("auth")
    return {"msg": "Logged out"}


@router.get("/check-username")
def check_username(username: str):
    conn = connect_to_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    cur.execute("SELECT 1 FROM users WHERE username = %s", (username,))
    exists = cur.fetchone() is not None

    conn.close()

    return {"exists": exists}
