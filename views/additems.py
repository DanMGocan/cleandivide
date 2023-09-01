from flask import Blueprint, render_template, redirect, url_for, request, session, flash
from flask_login import login_required, UserMixin, LoginManager, login_user, logout_user, current_user
from flask_oauthlib.client import OAuth
from models import User, get_db_connection
from views.auth import add_or_get_user

additems_bp = Blueprint('additems_bp', __name__)


@additems_bp.route("/addtask", methods=("GET", "POST"))
@login_required
def add_task():
    if request.method == 'POST':
        description = request.form['description'].lower()
        points = request.form["points"]
        room = request.form["room"]
        frequency = request.form["frequency"]
        user_id = session.get('user_id')  

        # Switch cases, to modify the points value in accordance with frequency #
        frequency_multiplier = {
            "Daily": 3,
            "Twice Weekly": 2,
            "Weekly": 1,
            "Twice Monthly": 0.75,
            "Monthly": 0.5
        }

        points *= frequency_multiplier.get(frequency, 1)
        
        # Check if the task description already exists
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM tasks WHERE user_id = ? AND description = ?', (user_id, description))
        task_exists = cursor.fetchone()

        if task_exists:
            # Increment the used_count for the task
            conn.execute('UPDATE tasks SET used_count = used_count + 1 WHERE id = ?', (task_exists[0],))
        else:
            # Insert new task
            conn.execute('INSERT INTO tasks (user_id, description, points, room, frequency) VALUES (?, ?, ?, ?, ?)', 
                         (user_id, description, points, room, frequency))

        conn.commit()
        conn.close()

        flash('Task added successfully!', 'success')
        return redirect(url_for('main'))  # Redirect to user's dashboard



@additems_bp.route("/addroom", methods=("GET", "POST"))
@login_required
def add_room():
    if request.method == 'POST':
        name = request.form['name']
        user_id = session.get('user_id')  # Assuming you stored user's ID in session upon login
        
        # Add task to database
        conn = get_db_connection()
        conn.execute('INSERT INTO rooms (user_id, name) VALUES (?, ?)', (user_id, name))
        conn.commit()
        conn.close()

        flash('Room added successfully!', 'success')
        return redirect(url_for('main'))  # Redirect to user's dashboard

@additems_bp.route("/addflatmate", methods=("GET", "POST"))
@login_required
def add_flatmate():
    if request.method == 'POST':
        name = request.form['name']
        user_id = session.get('user_id')
        flatmate_email = request.form["email"]  
        
        # Add task to database
        conn = get_db_connection()
        conn.execute('INSERT INTO flatmates (user_id, name, email) VALUES (?, ?, ?)', (user_id, name, flatmate_email))
        conn.commit()
        conn.close()

        flash('Flatmate added successfully!', 'success')
        return redirect(url_for('main'))  # Redirect to user's dashboard
