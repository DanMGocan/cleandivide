from flask import Blueprint, redirect, url_for, session, render_template, flash
from flask_login import login_required
from models import get_db_connection
from datetime import datetime, timedelta
from itertools import groupby
from sqlite3 import IntegrityError
from datetime import datetime
import sqlite3
from context_processors import get_table_owner_status
from views.helpers import get_power_costs

calendar = {}
dashboard_bp = Blueprint('dashboard_bp', __name__)

@dashboard_bp.route("/dashboard", methods=["GET", "POST"])
@login_required
def dashboard():
    user_id = session.get('user_id')
    table_owner = "absent"
    today_date = datetime.now().strftime('%Y-%m-%d')
    power_costs = {
    'reassign': 100, 
    'skip': 135, 
    'procrastinate': 75,
    'lower_reward_threshold': 0.25,
    'higher_reward_threshold': 0.75
}

    # Establish the database connection
    conn = get_db_connection()
    conn.row_factory = sqlite3.Row  # Fetches the rows as dictionaries
    cursor = conn.cursor()

    # Fetch power thresholds
    cursor.execute("SELECT lower_reward_threshold, higher_reward_threshold FROM powercosts WHERE user_id = ?", (user_id,))
    thresholds = cursor.fetchone()
    lower_threshold = thresholds['lower_reward_threshold'] if thresholds else 0
    higher_threshold = thresholds['higher_reward_threshold'] if thresholds else 0

    # Determine if the user is a house master
    house_master_status = cursor.execute("SELECT table_owner FROM users WHERE user_id = ?", (user_id,)).fetchone()['table_owner']

    # Fetch the number of times the user has logged in
    times_logged = cursor.execute('SELECT times_logged FROM users WHERE user_id = ?', (user_id,)).fetchone()['times_logged']

    # Check if the daily bonus has been collected
    already_clicked = cursor.execute(
        "SELECT 1 FROM daily_bonus WHERE user_id = ? AND date = ?", 
        (user_id, today_date)
    ).fetchone() is not None

   # Get power costs
   # power_costs = cursor.execute('SELECT reassign, skip, procrastinate FROM powercosts WHERE user_id = ?', (user_id,)).fetchone() or {'reassign': 0, 'skip': 0, 'procrastinate': 0}

    # Logic to get tasks for today and tomorrow
    # Fetch all tasks from the task table where the user is involved either as a creator or an assigned user
    tasks_total_query = """
    SELECT tt.* 
    FROM task_table AS tt 
    JOIN flatmates AS f ON tt.task_owner = f.id 
    WHERE f.user_id = ?
    """
    tasks_total = cursor.execute(tasks_total_query, (user_id,)).fetchall()

    # Fetch the flatmate ID for the current user_id
    flatmate_id_query = "SELECT id FROM flatmates WHERE email = ?"
    flatmate_id_result = cursor.execute(flatmate_id_query, (user_id,)).fetchone()
    flatmate_id = flatmate_id_result[0] if flatmate_id_result else None

    # Now use flatmate_id directly in the next query
    if flatmate_id:
        tasks_today_query = """
        SELECT tt.*, t.description, t.points, t.frequency FROM task_table AS tt
        INNER JOIN tasks AS t ON tt.task_id = t.id
        WHERE tt.task_owner = ? AND tt.task_date = ?
        """
        tasks_today = cursor.execute(tasks_today_query, (flatmate_id, today_date)).fetchall()
        tasks_today = [dict(task) for task in tasks_today]
        table_owner = tasks_today[0]["table_owner"] or None
        # # Query to find the table_owner for a task assigned to the logged-in user
        # table_owner_query = """
        # SELECT u.table_owner 
        # FROM task_table AS tt
        # JOIN flatmates AS f ON tt.task_owner = f.id
        # JOIN users AS u ON tt.table_owner = u.user_id
        # WHERE f.id = ?
        # LIMIT 1
        # """
        # table_owner_result = cursor.execute(table_owner_query, (flatmate_id,)).fetchone()
        # table_owner = table_owner_result[0] if table_owner_result else None

        if table_owner:
            # Fetch power costs for the table_owner
            power_costs_query = """
            SELECT reassign, skip, procrastinate, lower_reward_threshold, higher_reward_threshold 
            FROM powercosts 
            WHERE user_id = ?
            """
            power_costs = cursor.execute(power_costs_query, (table_owner,)).fetchone() or {
                'reassign': 0, 
                'skip': 0, 
                'procrastinate': 0,
                'lower_reward_threshold': 0.25,
                'higher_reward_threshold': 0.75
            }

    else:
        tasks_today = []  # No flatmate ID found, so the user has no tasks

    # No need to separate tasks anymore as all tasks fetched are owned by the user
    own_tasks_today = tasks_today  # This now contains all tasks for today where the logged-in user is the owner

    # Fetch the table owner for the current user's tasks
    
    
    return render_template(
        'dashboard.html',
        total_tasks=tasks_total,
        own_tasks_today=own_tasks_today,
        today_date=(datetime.strptime(today_date, '%Y-%m-%d')).strftime('%A, %d/%m/%Y'),
        times_logged=times_logged,
        already_clicked=already_clicked,
        lower_threshold=lower_threshold,
        higher_threshold=higher_threshold,
        power_costs=power_costs,
        house_master_status=house_master_status,
        table_owner=table_owner
        # Add any additional context variables needed by your template
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



