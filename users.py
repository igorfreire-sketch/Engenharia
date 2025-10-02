from sqlalchemy import Table, Column, Integer, String, MetaData
from db import engine, SessionLocal
from auth import hash_password, verify_password
from sqlalchemy.exc import OperationalError

metadata = MetaData()

users = Table(
    "users", metadata,
    Column("id", Integer, primary_key=True),
    Column("username", String, unique=True, nullable=False),
    Column("password", String, nullable=False),
    Column("role", String, default="comum")
)

metadata.create_all(engine)

def create_user(username, password, role="comum"):
    session = SessionLocal()
    hashed = hash_password(password)
    session.execute(users.insert().values(username=username, password=hashed, role=role))
    session.commit()
    session.close()

def authenticate_user(username, password):
    try:
        session = SessionLocal()
        user = session.execute(users.select().where(users.c.username == username)).fetchone()
        if user and verify_password(password, user.password):
            return {"username": user.username, "role": user.role}
    except OperationalError:
        return "connection_error"
    return None

def get_all_users_for_auth():
    try:
        session = SessionLocal()
        rows = session.execute(users.select()).fetchall()
        credentials = {}
        for row in rows:
            credentials[row.username] = {
                "name": row.username,
                "email": row.username,
                "password": row.password,
                "role": row.role,
            }
        return credentials
    except OperationalError:
        return None
