from flask import Blueprint, redirect, url_for, session, render_template, flash
from flask_login import login_required
from models import get_db_connection
from datetime import datetime, timedelta
import random
from itertools import groupby
from sqlite3 import IntegrityError

generator_bp = Blueprint('generator_bp', __name__)

@generator_bp.route("/generate", methods=["GET", "POST"])
@login_required
def generate(days):

    conn = get_db_connection()
    cursor = conn.cursor()

    user_id = session.get('user_id')

    # Get all the relevant data
    tasks_db = conn.execute("SELECT * FROM tasks WHERE user_id = ? ORDER BY id", (user_id,)).fetchall()
    flatmates_db = conn.execute("SELECT * FROM flatmates WHERE user_id = ? ORDER BY id", (user_id,)).fetchall()
    conn.close()

    tasks = [dict(id=row[0], description=row[2], points=row[3], room=row[4], frequency=row[5]) for row in tasks_db]
    flatmates = [dict(id=row[0], email=row[2]) for row in flatmates_db]

    # Initialize dictionaries to hold assigned tasks and points per flatmate
    assigned_tasks = {flatmate["email"]: [] for flatmate in flatmates}
    points_per_name = {flatmate["email"]: 0 for flatmate in flatmates}

    def replicate_tasks_based_on_frequency(task):
        if task['frequency'] == 'Daily':
            return [(task, day) for day in range(1, 31)]
        
        elif task['frequency'] == 'Twice weekly':
            # Here, I'm randomly picking 8 days, you might want to fix these days based on your requirement
            due_days = list(range(1, 31, 4))
            return [(task, day) for day in due_days]
        
        elif task['frequency'] == 'Weekly':
            # This will pick 4 days in a month (like every Monday of the month if the month starts on a Monday)
            due_days = list(range(1, 31, 7))
            return [(task, day) for day in due_days]
        
        elif task['frequency'] == 'Twice monthly':
            # Here, I'm randomly picking 2 days in the month; adjust as needed
            due_days = list(range(1, 31, 15))
            return [(task, day) for day in due_days]
        
        elif task['frequency'] == 'Monthly':
            # As an example, this schedules the task for the first day of the month
            return [(task, 16)]
        
        else:
            return []

    # Expand tasks based on frequency and then sort them
    sorted_tasks = sorted(
        [item for task in tasks for item in replicate_tasks_based_on_frequency(task)], 
        key=lambda x: x[0]['room']
    )

    def find_flatmate_with_least_points(points_per_name, exclude=None):
        """Find the flatmate with the least points excluding the provided flatmate."""
        if exclude:
            points_per_name = {name: points for name, points in points_per_name.items() if name != exclude}
        
        # This will get the flatmate(s) with the minimum points
        min_points = min(points_per_name.values())
        min_point_flatmates = [name for name, points in points_per_name.items() if points == min_points]

        # Randomly select one of the flatmates with the minimum points
        return random.choice(min_point_flatmates)

    # Assigning tasks
    for task_tuple in sorted_tasks:
        task, due_day = task_tuple
        suitable_flatmate = find_flatmate_with_least_points(points_per_name)
        
        # Update the task assignment and points tally
        task_with_assignment = task.copy()
        task_with_assignment["assigned_to"] = suitable_flatmate
        
        # Replace the tuple in sorted_tasks
        index = sorted_tasks.index(task_tuple)
        sorted_tasks[index] = (task_with_assignment, due_day)
        
        assigned_tasks[suitable_flatmate].append(task_with_assignment)
        points_per_name[suitable_flatmate] += task["points"]

    conn = get_db_connection()
    cursor = conn.cursor()

    # Delete old entries for the user
    try:
        cursor.execute("DELETE FROM task_table WHERE table_owner = ?", (user_id,))
        conn.commit()
    except Exception as e:
        conn.rollback()
        flash(f"An error occurred while deleting old tasks: {e}", "error")

    # Function to insert tasks into the database
    def insert_tasks(tasks, date_str, user_id, cursor):
        for task in tasks:
            # Assuming 'task['room']' gives us the room name, we need to convert it to room_id.
            # To do that, we need to select the id from the rooms table where name matches 'task['room']'.
            cursor.execute("SELECT id FROM rooms WHERE name = ? AND user_id = ?", (task['room'], user_id))
            room_id = cursor.fetchone()[0]

            # Assuming 'task['assigned_to']' gives us the flatmate's email, we need to convert it to flatmate_id.
            # To do that, we need to select the id from the flatmates table where email matches 'task['assigned_to']'.
            cursor.execute("SELECT id FROM flatmates WHERE email = ? AND user_id = ?", (task['assigned_to'], user_id))
            flatmate_id = cursor.fetchone()[0]

            try:
                cursor.execute("""
                    INSERT INTO task_table (table_owner, task_date, task_id, task_complete, room_id, task_owner)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (user_id, date_str, task["id"], 0, room_id, flatmate_id))
            except IntegrityError:
                conn.rollback()
                flash(f"Could not insert task scheduled for {date_str} into task_table", "error")
                continue


    # Loop over 31 days
    for i in range(days):
        date = datetime.now() + timedelta(days=i)
        day_str = date.strftime('%Y-%m-%d')
        day_of_month = i + 1  # 1-indexed
        tasks_due_today = [task for task, due_day in sorted_tasks if due_day == day_of_month]
        insert_tasks(tasks_due_today, day_str, user_id, cursor)

    conn.commit()
    conn.close()

    # Render the template with the calendar data
    return redirect(url_for("main"))
