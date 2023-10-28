from flask import Blueprint, redirect, url_for, session, render_template, flash
from flask_login import login_required
from models import get_db_connection
from datetime import datetime, timedelta
from itertools import groupby
from sqlite3 import IntegrityError
from datetime import datetime
import sqlite3
from context_processors import get_table_owner_status


power_costs = {
    "reassign": 60,
    "skip": 75,
    "procrastinate": 35
}

calendar = {}
dashboard_bp = Blueprint('dashboard_bp', __name__)

@dashboard_bp.route("/dashboard", methods=["GET", "POST"])
@login_required
def dashboard():

    conn = get_db_connection()
    cursor = conn.cursor()
    user_id = session.get('user_id')
    today_date = datetime.now().strftime('%d/%m/%Y')


    # Check if a task table has been created #
    cursor.execute(f"SELECT * FROM task_table WHERE table_owner = ?", (user_id,))
    task_table_created_placeholder = cursor.fetchone()
    if task_table_created_placeholder:
        task_table_created = True
    else:
        task_table_created = False

    # Check if the user is a table owner #
    table_owner_status_placeholder = get_table_owner_status()["is_table_owner"]
    if table_owner_status_placeholder:
        table_owner_status = True
    else:
        table_owner_status = False
        
    # Check how many times the user logged in #
    cursor.execute('SELECT times_logged FROM users WHERE user_id = ?', (user_id,))
    row = cursor.fetchone()
    times_logged = row['times_logged']



    # Ensure rows are returned as dictionaries, not tuples
    cursor.row_factory = sqlite3.Row

    # Find the table_owner for the current user
    cursor.execute("SELECT DISTINCT table_owner FROM task_table WHERE table_owner = ? OR task_owner = ?", (user_id, user_id))
    table_owner_row = cursor.fetchone()

    if task_table_created == False and table_owner_status == False:
    # Handle this case appropriately, e.g., by showing an error message or redirecting the user
        return render_template(
            'dashboard.html',
            total_tasks=0, 
            table_owner_status=table_owner_status,
            own_tasks_today=[], 
            flatmates_tasks_today=[], 
            own_tasks_tomorrow=[],
            today_date=today_date,
            times_logged=times_logged    
            )

    if task_table_created == False and table_owner_status == True:
        return redirect(url_for("additems_bp.add_items"))


    table_owner = table_owner_row['table_owner']

    # Fetch all the flatmate IDs added by the same table_owner or by themselves
    cursor.execute("SELECT DISTINCT task_owner FROM task_table WHERE table_owner = ?", (table_owner,))
    flatmate_ids_row = cursor.fetchall()
    flatmate_ids = [str(row['task_owner']) for row in flatmate_ids_row]

    # Use placeholders and parameterized query to fetch tasks for today and tomorrow
    placeholders = ', '.join(['?' for _ in flatmate_ids])

    # Get tasks in total
    cursor.execute(f"SELECT * FROM task_table WHERE task_owner = ?", (table_owner,))
    tasks_total = cursor.fetchall()

    # Get tasks for today
    cursor.execute(f"SELECT * FROM task_table WHERE task_owner IN ({placeholders}) AND task_date = DATE('now')", flatmate_ids)
    tasks_today = cursor.fetchall()

    # Get tasks for tomorrow
    cursor.execute(f"SELECT * FROM task_table WHERE task_owner IN ({placeholders}) AND task_date = DATE('now', '+1 day')", flatmate_ids)
    tasks_tomorrow = cursor.fetchall()

    conn.close()

    # Separate the tasks
    total_tasks = [task for task in tasks_total]
    own_tasks_today = [task for task in tasks_today if task['task_owner'] == str(user_id)]
    own_tasks_tomorrow = [task for task in tasks_tomorrow if task['task_owner'] == str(user_id)]
    flatmates_tasks_today = [task for task in tasks_today if task['task_owner'] != str(user_id)]
    return render_template(
        'dashboard.html',
        total_tasks=total_tasks, 
        table_owner=table_owner,
        own_tasks_today=own_tasks_today, 
        flatmates_tasks_today=flatmates_tasks_today, 
        own_tasks_tomorrow=own_tasks_tomorrow,
        power_costs=power_costs,
        today_date = today_date
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



