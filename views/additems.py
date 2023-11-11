from flask import Blueprint, render_template, redirect, url_for, request, session, flash, current_app
from flask_login import login_required, UserMixin, LoginManager, login_user, logout_user, current_user
from flask_oauthlib.client import OAuth
from flask_mail import Message


from models import User, get_db_connection
from views.auth import add_or_get_user
from views.helpers import mail

from views.html_helpers import email_text

additems_bp = Blueprint('additems_bp', __name__)

# Parent route #
@additems_bp.route("/add", methods=["GET", "POST"])
@login_required
def add_items():

    user_id = session.get('user_id') 
    conn = get_db_connection()
    cursor = conn.cursor()
    tasks = conn.execute("SELECT * FROM tasks WHERE user_id = ? ORDER BY id DESC", (user_id, )).fetchall()
    rooms = conn.execute("SELECT * FROM rooms WHERE user_id = ? ORDER BY id DESC LIMIT 10 ", (user_id, )).fetchall()
    flatmates = conn.execute("SELECT * FROM flatmates WHERE user_id = ? ORDER BY id DESC LIMIT 10 ", (user_id, )).fetchall()
    popular_tasks = conn.execute("SELECT description FROM tasks GROUP BY description ORDER BY COUNT(description) DESC LIMIT 100").fetchall()
    task_table_exists = conn.execute("SELECT 1 FROM task_table WHERE table_owner = ? LIMIT 1", (user_id,)).fetchone() is not None

    template_data = {
        "tasks": tasks,
        "rooms": rooms,
        "flatmates": flatmates,
        "user_email": user_id,
        "popular_tasks": popular_tasks,
        "task_table_exists": task_table_exists
    }

    return render_template('add.html', template_data = template_data) # For logged-in users

@additems_bp.route("/addtask", methods=("GET", "POST"))
@login_required
def add_task():
    if request.method == 'POST':
        description = request.form['description'].capitalize()
        points = int(request.form["points"])
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
        
        conn = get_db_connection()
        try:
            # Check if the room already exists
            cursor = conn.cursor()
            cursor.execute('SELECT id FROM rooms WHERE user_id = ? AND name = ?', (user_id, room))
            room_exists = cursor.fetchone()

            if not room_exists:
                # Insert new room
                conn.execute('INSERT INTO rooms (user_id, name) VALUES (?, ?)', (user_id, room))

            # Check if the task description already exists
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

            flash('Task added successfully!', 'success')
        except Exception as e:
            current_app.logger.error(f"Failed to add task due to {e}")
            flash('An error occurred. Please try again.', 'danger')
        finally:
            conn.close()

        return redirect(url_for('additems_bp.add_items'))  # Redirect to user's dashboard

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
        user_id = session.get('user_id')
        flatmate_email = request.form["email"]

        conn = get_db_connection()
        try:
            # Check if flatmate already exists
            existing_flatmate = conn.execute('SELECT email FROM flatmates WHERE email = ? AND user_id = ?', (flatmate_email, user_id)).fetchone()
            if existing_flatmate:
                flash('Flatmate already exists and cloning is but a distant dream!', 'danger')
                return redirect(url_for('additems_bp.add_items'))  # Redirect to user's dashboard

            # Check if the flatmate is already a House Master
            house_master_check = conn.execute('SELECT table_owner FROM users WHERE user_id = ?', (flatmate_email,)).fetchone()
            if house_master_check and house_master_check[0] == 1:
                flash('This person is already a House Master!', 'warning')
                return redirect(url_for('additems_bp.add_items'))  # Redirect to user's dashboard

            # If not, proceed with adding the flatmate
            conn.execute('INSERT INTO flatmates (user_id, email) VALUES (?, ?)', (user_id, flatmate_email))
            conn.commit()

            # Send an email to the flatmate
            try:
                msg = Message("Welcome to DivideNDust! Stop procrastinating... from tomorrow!", sender=current_app.config['MAIL_USERNAME'], recipients=[flatmate_email])
                # msg.body = 'You have been added as a flatmate in our app. Welcome aboard!'
                msg.html = email_text
                mail.send(msg)
            except:
                flash("Email could not be sent, please ask your flatmate to login as normal", "warning")

            flash('Flatmate added successfully!', 'success')
        except Exception as e:
            current_app.logger.error(f"Failed to add flatmate due to {e}")
            flash('An error occurred. I am very bad at this, errors are very common!', 'danger')
        finally:
            conn.close()

        return redirect(url_for('additems_bp.add_items'))  # Redirect to user's dashboard

