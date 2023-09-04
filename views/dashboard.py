from flask import Blueprint, redirect, url_for, session, render_template, flash
from flask_login import login_required
from models import get_db_connection
from datetime import datetime, timedelta
from itertools import groupby
from views.auth import add_or_get_user
from sqlite3 import IntegrityError
from datetime import datetime
from models import get_db_connection
import sqlite3





calendar = {}
dashboard_bp = Blueprint('dashboard_bp', __name__)

@dashboard_bp.route("/dashboard", methods=["GET", "POST"])
@login_required
def dashboard():
    user_id = session.get('user_id')
    if not user_id:
        return "Please login first", 401

    conn = get_db_connection()
    cursor = conn.cursor()


    # Ensure rows are returned as dictionaries, not tuples
    cursor.row_factory = sqlite3.Row

    # Find the table_owner for the current user
    cursor.execute("SELECT DISTINCT table_owner FROM task_table WHERE table_owner = ? OR task_owner = ?", (user_id, user_id))
    table_owner_row = cursor.fetchone()

    if not table_owner_row:
        return "Table owner not found", 404

    table_owner = table_owner_row['table_owner']

    # Fetch all the flatmate IDs added by the same table_owner or by themselves
    cursor.execute("SELECT DISTINCT task_owner FROM task_table WHERE table_owner = ?", (table_owner,))
    flatmate_ids_row = cursor.fetchall()
    flatmate_ids = [str(row['task_owner']) for row in flatmate_ids_row]

    # Use placeholders and parameterized query to fetch tasks for today and tomorrow
    placeholders = ', '.join(['?' for _ in flatmate_ids])

    # Get tasks for today
    cursor.execute(f"SELECT * FROM task_table WHERE task_owner IN ({placeholders}) AND task_date = DATE('now')", flatmate_ids)
    tasks_today = cursor.fetchall()

    # Get tasks for tomorrow
    cursor.execute(f"SELECT * FROM task_table WHERE task_owner IN ({placeholders}) AND task_date = DATE('now', '+1 day')", flatmate_ids)
    tasks_tomorrow = cursor.fetchall()

    conn.close()

    # Separate the tasks
    own_tasks_today = [task for task in tasks_today if task['task_owner'] == str(user_id)]
    own_tasks_tomorrow = [task for task in tasks_tomorrow if task['task_owner'] == str(user_id)]
    flatmates_tasks_today = [task for task in tasks_today if task['task_owner'] != str(user_id)]

    return render_template(
        'dashboard.html', 
        table_owner=table_owner,
        own_tasks_today=own_tasks_today, 
        flatmates_tasks_today=flatmates_tasks_today, 
        own_tasks_tomorrow=own_tasks_tomorrow
    )


@dashboard_bp.route("/dashboard_monthly", methods=["GET", "POST"])
@login_required
def dashboard_monthly():
    user_id = session.get('user_id')
    if not user_id:
        return "Please login first", 401

    conn = get_db_connection()
    cursor = conn.cursor()

    today = datetime.now().strftime('%Y-%m-%d')
    thirty_days_later = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')

    cursor.execute("""
    SELECT * FROM task_table WHERE task_owner = ? 
    AND task_date BETWEEN ? AND ?;
    """, (user_id, today, thirty_days_later))

    tasks = cursor.fetchall()
    tasks_by_date = {}
    for task in tasks:
        task_date = task['task_date']
        if task_date not in tasks_by_date:
            tasks_by_date[task_date] = []
        tasks_by_date[task_date].append(task)

    conn.close()

    next_30_days = [(datetime.now() + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(30)]

    return render_template('monthly.html', tasks_by_date=tasks_by_date, next_30_days=next_30_days)





