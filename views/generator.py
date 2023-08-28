from flask import Blueprint, redirect, url_for, session, render_template, flash
from flask_login import login_required
from models import get_db_connection
from datetime import datetime, timedelta
import random
from itertools import groupby

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
    flatmates = [dict(id=row[0], name=row[2]) for row in flatmates_db]

    # Control point, if it's only one task, the program will error #
    if len(tasks_db) == 1:
        flash("You have added only one task, you don't need us. Plus, the algorithm is literally incapable of solving for one task", "warning")
        return redirect(url_for("main"))

    average_points = sum(task["points"] for task in tasks) / len(flatmates)
    sorted_tasks = sorted(tasks, key=lambda x: x['room'])

    # Initialize dictionaries to hold assigned tasks and points per flatmate
    assigned_tasks = {flatmate["name"]: [] for flatmate in flatmates}
    points_per_name = {flatmate["name"]: 0 for flatmate in flatmates}

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

    # print(sorted_tasks)
    # Write the results to a file
    # Write the results to a file
    with open("task_assignments.txt", "w") as f:
        for element in sorted_tasks:
            f.write(f"{element}:\n")

    introductions = [
        "On this magnificent day ",
        "Today ",
        "I reckon that it is time that ",
        "They might not like it, but ",
        "In the spirit of avoiding procrastination, ",
        "By the power vested in me, ",
        "The stars have aligned and ",
        "It's not you, it's me saying that ",
        "Lo and behold, ",
        "For the greater good of the household, ",
        "With utmost urgency, ",
        "As foretold by the ancients, ",
        "Without further ado, ",
        "They will absolutely seize the day and, ",
        "The time has come and ",
        "Under the watchful eyes of the cleaning gods, ",
        "Ding, ding, ding! We have a winner, and ",
        "Be warned, for ",
        "Y'all won't believe it but ",
        "In a world where chores never end, ",
        "As a sign of my benevolence, ",
        "According to my calculations, ",
        "In an unprecedented move, "
    ]

    for i in range(31):
        date = datetime.now() + timedelta(days=i)
        day_str = date.strftime('%Y-%m-%d')
        
        calendar[day_str] = []
        
        # Add daily tasks
        for task in daily_tasks:
            calendar[day_str].append({"introduction": random.choice(introductions), 'task': task['description'], 'owner': task['assigned_to'], "frequency": task["frequency"]})

        # Add twice-weekly tasks
        if i == 4:
            for task in twice_weekly_tasks:
                calendar[day_str].append({"introduction": random.choice(introductions), 'task': task['description'], 'owner': task['assigned_to'], "frequency": task["frequency"]})
        
        # Add weekly tasks
        if i % 7 == 0:
            for task in weekly_tasks:
                calendar[day_str].append({"introduction": random.choice(introductions), 'task': task['description'], 'owner': task['assigned_to'], "frequency": task["frequency"]})
        
        # Add twice monthly tasks
        if i == 0 or i == 15:
            for task in twice_monthly_tasks:
                calendar[day_str].append({"introduction": random.choice(introductions), 'task': task['description'], 'owner': task['assigned_to'], "frequency": task["frequency"]})
        
        # Add monthly tasks:
        random_value = random.randint(16, 31)
        if i == random_value:
            for task in monthly_tasks:
                calendar[day_str].append({"introduction": random.choice(introductions), 'task': task['description'], 'owner': task['assigned_to'], "frequency": task["frequency"]})


    grouped_by_date = {}
    for day, tasks in calendar.items():
        grouped_by_date[day] = {}
        tasks.sort(key=lambda x: x['owner'])
        for owner, owner_tasks in groupby(tasks, key=lambda x: x['owner']):
            grouped_by_date[day][owner] = list(owner_tasks)

    print(calendar)
    return render_template("generator.html", calendar=grouped_by_date)