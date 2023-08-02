import sqlite3
from flask_login import UserMixin

class User(UserMixin):
    def __init__(self, id):
        self.id = id

def get_db_connection():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn