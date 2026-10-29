from contextlib import closing
import sqlite3

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
            password TEXT NOT NULL
            )""")
            self.conn.execute("""
            CREATE TABLE IF NOT EXISTS files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_name TEXT NOT NULL,
            creator_id INTEGER NOT NULL,
            contents TEXT,
            public BOOLEAN NOT NULL DEFAULT 0,
            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            last_modified_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
            )""")

    def add_user(self, username, hashed_pwd):
        try:
            with self.conn:
                self.conn.execute(
                "INSERT INTO users (username, password) VALUES (?, ?)",
                (username, hashed_pwd)
                )
            return True
        except sqlite3.IntegrityError:
            return False
        
    def get_password(self, username: str) -> str | None:
        with self.conn, closing(self.conn.cursor()) as cursor:
            row = cursor.execute("SELECT password FROM users WHERE username = ?",(username,)).fetchone()
            return row[0] if row is not None else None
    
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
                    "UPDATE files SET contents = ?, last_modified_at = CURRENT_TIMESTAMP WHERE id = ?",
                    (new_contents, file_id)
                )
            return True
        except sqlite3.Error:
            return False

    def get_file_by_id(self, file_id: int):
        with self.conn, closing(self.conn.cursor()) as cursor:
            row = cursor.execute("SELECT * FROM files WHERE id = ?", (file_id,)).fetchone()
            return row if row is not None else None

    def get_files_by_user(self, user_id: int):
        with self.conn, closing(self.conn.cursor()) as cursor:
            rows = cursor.execute("SELECT * FROM files WHERE creator_id = ?", (user_id,)).fetchall()
            return rows if rows is not None else []

    def delete_file(self, file_id: int):
        try:
            with self.conn:
                self.conn.execute("DELETE FROM files WHERE id = ?", (file_id,))
            return True
        except sqlite3.Error:
            return False

    def get_public_files(self):
        with self.conn, closing(self.conn.cursor()) as cursor:
            rows = cursor.execute("SELECT * FROM files WHERE public = 1").fetchall()
            return rows if rows is not None else []