from flask import Blueprint, redirect, url_for, session, render_template, flash
from flask_login import login_required
from models import get_db_connection
from datetime import datetime, timedelta
import random
from itertools import groupby
from views.auth import add_or_get_user
from sqlite3 import IntegrityError

calendar = {}
generator_bp = Blueprint('generator_bp', __name__)

@generator_bp.route("/generate", methods=["GET", "POST"])
@login_required
def generate():

    conn = get_db_connection()
    cursor = conn.cursor()

    user_id = session.get('user_id')

    # Get all the relevant data
    tasks_db = conn.execute("SELECT * FROM tasks WHERE user_id = ? ORDER BY id", (user_id, )).fetchall()
    flatmates_db = conn.execute("SELECT * FROM flatmates WHERE user_id = ? ORDER BY id", (user_id, )).fetchall()
    conn.close()

    tasks = [dict(id=row[0], description=row[2], points=row[3], room=row[4], frequency=row[5]) for row in tasks_db]
    flatmates = [dict(id=row[0], email=row[2]) for row in flatmates_db]

    # Send e-mail invitations to all flatmates from the DB 
    for user in flatmates:
        add_or_get_user(user["email"], "flatmate_update")

    # Control point, if it's only one task, the program will error #
    if len(tasks_db) == 1:
        flash("You have added only one task, you don't need us. Plus, the algorithm is literally incapable of solving for one task", "warning")
        return redirect(url_for("main"))

    sorted_tasks = sorted(tasks, key=lambda x: x['room'])

    # Initialize dictionaries to hold assigned tasks and points per flatmate
    assigned_tasks = {flatmate["email"]: [] for flatmate in flatmates}
    points_per_name = {flatmate["email"]: 0 for flatmate in flatmates}

    # Function to find the flatmate with the least points who is also working in the same room if possible
    def find_suitable_flatmate(assigned_tasks, points_per_name, room):
        min_points = min(points_per_name.values())
        candidates = [name for name, points in points_per_name.items() if points == min_points]
        
        # Try to find a flatmate who is already working in the same room
        for name in candidates:
            if any(task["room"] == room for task in assigned_tasks[name]):
                return name
        
        return candidates[0]  # If no one is in the same room, return the flatmate with the least points


    # Distribute the tasks among the flatmates
    for task in sorted_tasks:
        task_description = task["description"]
        task_points = task["points"]
        task_room = task["room"]
        task_frequency = task["frequency"]

        suitable_flatmate = find_suitable_flatmate(assigned_tasks, points_per_name, task_room)
        task["assigned_to"] = suitable_flatmate

        assigned_tasks[suitable_flatmate].append(task)
        points_per_name[suitable_flatmate] += task_points

    daily_tasks = [task for task in sorted_tasks if task['frequency'] == 'Daily']
    twice_weekly_tasks = [task for task in sorted_tasks if task['frequency'] == 'Twice Weekly']
    weekly_tasks = [task for task in sorted_tasks if task['frequency'] == 'Weekly']
    twice_monthly_tasks = [task for task in sorted_tasks if task['frequency'] == 'Twice Monthly']
    monthly_tasks = [task for task in sorted_tasks if task['frequency'] == 'Monthly']

    with open("task_assignments.txt", "w") as f:
        for element in sorted_tasks:
            f.write(f"{element}:\n")

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
            try:
                cursor.execute("""
                    INSERT INTO task_table (table_owner, task_date, task_id, task_description, task_frequency, task_points, room_id, task_owner)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (user_id, date_str, task["id"], task['description'], task["frequency"], task["points"], task['room'], task['assigned_to']))
            except IntegrityError:
                conn.rollback()
                flash(f"Could not insert {task['frequency']} task into task_table", "error")
                continue

    # Loop over 31 days
    for i in range(31):
        date = datetime.now() + timedelta(days=i)
        day_str = date.strftime('%Y-%m-%d')
        day_of_week = date.weekday()  # 0 is Monday, 1 is Tuesday, etc.
        day_of_month = date.day

        # Add daily tasks
        insert_tasks(daily_tasks, day_str, user_id, cursor)

        # Add twice-weekly tasks
        if day_of_week in random.sample(range(0, 7), 2):  # Assuming tasks need to be done on Monday and Thursday
            insert_tasks(twice_weekly_tasks, day_str, user_id, cursor)

        # Add weekly tasks
        if day_of_week in random.sample(range(0, 7), 1):  # Assuming tasks need to be done every Monday
            insert_tasks(weekly_tasks, day_str, user_id, cursor)

        # Add twice-monthly tasks
        if day_of_month in random.sample(range(1, 32), 2):
            insert_tasks(twice_monthly_tasks, day_str, user_id, cursor)

        # Add monthly tasks
        if day_of_month in random.sample(range(1, 32), 1):  # Assuming tasks need to be done on the 1st of every month
            insert_tasks(monthly_tasks, day_str, user_id, cursor)



    conn.commit()
    conn.close()
        
    return redirect(url_for("main"))