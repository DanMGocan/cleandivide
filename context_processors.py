from flask import session
from models import get_db_connection

def get_table_owner_status():
    user_id = session.get('user_id')
    is_table_owner = 0
    table_owner_title = ""

    if user_id:

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT table_owner FROM users WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()
        conn.close()

        is_table_owner = row["table_owner"]
        table_owner_title = ""

        if is_table_owner == 1:
            table_owner_title = "House Master"
        else:
            table_owner_title = "House Member"
            
    return dict(user_id=user_id, is_table_owner=is_table_owner, table_owner_title=table_owner_title)
