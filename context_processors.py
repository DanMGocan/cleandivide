from flask import session
from models import get_db_connection

def get_table_owner_status():
    user_id = session.get('user_id')
    is_table_owner = 0
    table_owner_title = ""
    times_logged = 0
    premium_user = 0

    if user_id:
        conn = get_db_connection()
        cursor = conn.cursor()
        # Assuming 'times_logged_in' is a column in your 'users' table.
        cursor.execute("SELECT table_owner, times_logged, premium_user FROM users WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()
        conn.close()

        if row:
            is_table_owner = row["table_owner"]
            times_logged = row["times_logged"]  # Retrieve the times_logged_in value from the database
            premium_user = row["premium_user"]

            if is_table_owner == 1:
                table_owner_title = "House Master"
            else:
                table_owner_title = "House Member"

    print(dict(user_id=user_id, is_table_owner=is_table_owner, table_owner_title=table_owner_title, times_logged=times_logged, premium_user=premium_user))
    return dict(user_id=user_id, is_table_owner=is_table_owner, table_owner_title=table_owner_title, times_logged=times_logged, premium_user=premium_user)


