from contextlib import closing
import datetime
import sqlite3
import mssql_python
from flask import Flask, g
from .__constants import CONNECTION_STRING_VARIABLE, SESSION_LIFETIME_SECONDS
import os

def connect(db_name):
    return sqlite3.connect(db_name)

class Database:
    def __init__(self, db_name):
        self.conn = connect(db_name)
        self.create_tables()
    
    def create_tables(self):
        with self.conn:
            self.conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            displayname TEXT NOT NULL
            )""")
            self.conn.execute("""
            CREATE TABLE IF NOT EXISTS files (
            file_id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_name TEXT NOT NULL,
            creator_id INTEGER NOT NULL,
            contents TEXT,
            public BOOLEAN NOT NULL DEFAULT 0,
            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            last_modified_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
            )""")
            self.conn.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
            sessionid INTEGER PRIMARY KEY AUTOINCREMENT,
            userid INTEGER NOT NULL,
            expiry DATETIME NOT NULL 
            )""")

    def add_user(self, username, hashed_pwd, displayname):
        try:
            with self.conn:
                self.conn.execute(
                "INSERT INTO users (username, password, displayname) VALUES (?, ?, ?)",
                (username, hashed_pwd, displayname)
                )
            return True
        except sqlite3.IntegrityError:
            return False
        
    def get_password(self, username: str) -> str | None:
        with self.conn, closing(self.conn.cursor()) as cursor:
            row = cursor.execute("SELECT password FROM users WHERE username = ?",(username,)).fetchone()
            return row[0] if row is not None else None

    def username_exists(self, username: str) -> bool:
        """Return True if a user with this username is already in the database."""
        with self.conn as cursor:
            returner = cursor.execute("SELECT 1 FROM Users WHERE username = ?", (username,)).fetchone()
            return returner is not None

    def update_last_login(self, username: str) -> None:
        """Update the last login time for the specified user."""
        with self.conn:
                self.conn.execute(
                "UPDATE Users SET last_login = GETDATE() WHERE username = ?",
                (username,),
            )
        self.conn.commit()

    def create_session(self, user_id: int) -> str:
        """Add a session for this user to the Sessions table and return its ID.

        The database generates the ID (the NEWID() default on the sessionid
        column), and OUTPUT INSERTED.sessionid hands it back to us.
        """
        with self.conn:
                session_id = str(self.conn.execute(
                """
                INSERT INTO Sessions (userid, expiry)
                OUTPUT INSERTED.sessionid
                VALUES (?, DATEADD(SECOND, ?, GETDATE()))
                """,
                (user_id, SESSION_LIFETIME_SECONDS),
            ).fetchone()[0])
        self.conn.commit()
        return session_id

    def delete_session(self, session_id: str) -> None:
        """Remove a session from the Sessions table."""
        with self.conn:
                self.conn.execute("DELETE FROM Sessions WHERE sessionid = ?", (session_id,))
        self.conn.commit()

    def delete_all_sessions(self, session_id: str) -> None:
        """Remove all sessions for the user associated with the given session ID."""
        with self.conn:
                self.conn.execute("DELETE FROM Sessions WHERE userid = (SELECT userid FROM Sessions WHERE sessionid = ?)", (session_id,))
        self.conn.commit()

    def get_session_user(self, session_id: str):
        """Return the logged-in user's info for a session, or None if the session doesn't exist."""
        with self.conn:
            user = self.conn.execute(
                """
                SELECT Users.userid, Users.username, Users.display_name, Users.last_login,
                       Sessions.sessionid, Sessions.expiry
                FROM Sessions
                JOIN Users ON Users.userid = Sessions.userid
                WHERE Sessions.sessionid = ?
                """,
                (session_id,),
            ).fetchone()
            if user and user[5] < datetime.datetime.now():
                self.delete_session(session_id)
                return None
            return user
    
    def get_user_id(self, username: str) -> int | None:
        with self.conn, closing(self.conn.cursor()) as cursor:
            row = cursor.execute("SELECT id FROM users WHERE username = ?",(username,)).fetchone()
            return row[0] if row is not None else None

    def create_file(self, file_name: str, creator_id: int, public: bool):
        try:
            with self.conn:
                self.conn.execute(
                    "INSERT INTO files (file_name, creator_id, public) VALUES (?, ?, ?)",
                    (file_name, creator_id, public)
                )
            return True
        except sqlite3.Error:
            return False

    def modify_file(self, file_id: int, new_contents: str):
        try:
            with self.conn:
                self.conn.execute(
                    "UPDATE files SET contents = ?, last_modified_at = CURRENT_TIMESTAMP WHERE file_id = ?",
                    (new_contents, file_id)
                )
            return True
        except sqlite3.Error:
            return False

    def get_file_by_id(self, file_id: int):
        with self.conn, closing(self.conn.cursor()) as cursor:
            row = cursor.execute("SELECT * FROM files WHERE file_id = ?", (file_id,)).fetchone()
            return row if row is not None else None

    def get_files_by_user(self, user_id: int):
        with self.conn, closing(self.conn.cursor()) as cursor:
            rows = cursor.execute("SELECT * FROM files WHERE creator_id = ?", (user_id,)).fetchall()
            return rows if rows is not None else []

    def delete_file(self, file_id: int):
        try:
            with self.conn:
                self.conn.execute("DELETE FROM files WHERE file_id = ?", (file_id,))
            return True
        except sqlite3.Error:
            return False

    def get_public_files(self):
        with self.conn, closing(self.conn.cursor()) as cursor:
            rows = cursor.execute("SELECT * FROM files WHERE public = 1").fetchall()
            return rows if rows is not None else []

def get_db() -> Database:
    """Return this request's Database, connecting on first use."""
    if "db" not in g:
        g.db = Database("testing.db")#mssql_python.connect(os.environ[CONNECTION_STRING_VARIABLE]))
    return g.db