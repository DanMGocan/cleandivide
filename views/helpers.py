from flask import Blueprint, redirect, url_for, session, render_template, flash
from flask_login import login_required
from models import get_db_connection

helpers_bp = Blueprint('helpers_bp', __name__)

boilerplate_tasks = [
    ('Cleaning the garage', 2, 'Bedroom', 'Daily'),
    ('Making the bed', 4, 'Office', 'Weekly'),
    ('Trimming the hedge', 9, 'Garage', 'Weekly'),
    ('Cleaning the bathroom', 9, 'Bathroom', 'Monthly'),
    ('Changing air filters', 4, 'Living Room', 'Daily'),
    ('Wiping down electronics', 4, 'Office', 'Twice Monthly'),
    ('Cleaning the fish tank', 1, 'Garden', 'Twice Monthly'),
    ('Cleaning baseboards', 10, 'Office', 'Weekly'),
    ('Raking leaves', 4, 'Kitchen', 'Twice Monthly'),
    ('Cleaning the garage', 6, 'Living Room', 'Weekly'),
    ('Cleaning blinds', 10, 'Bathroom', 'Daily'),
    ('Doing the dishes', 7, 'Garden', 'Monthly'),
    ('Cleaning the garage', 4, 'Garage', 'Twice Monthly'),
    ('Ironing clothes', 1, 'Bedroom', 'Twice Weekly'),
    ('Polishing shoes', 5, 'Bathroom', 'Twice Monthly'),
    ('Polishing woodwork', 11, 'Bedroom', 'Weekly'),
    ('Sweeping the floor', 9, 'Living Room', 'Twice Weekly'),
    ('Cleaning the windows', 9, 'Garden', 'Daily'),
    ('Polishing woodwork', 2, 'Kitchen', 'Weekly'),
    ('Vacuuming the carpet', 4, 'Kitchen', 'Weekly'),
    ('Raking leaves', 1, 'Living Room', 'Weekly'),
    ('Cleaning the bathroom', 12, 'Bathroom', 'Weekly'),
    ('Cleaning blinds', 3, 'Bedroom', 'Twice Monthly'),
    ('Dusting the furniture', 12, 'Living Room', 'Twice Monthly'),
    ('Cleaning coffee maker', 4, 'Kitchen', 'Daily'),
    ('Sweeping the floor', 6, 'Bedroom', 'Monthly'),
    ('Cleaning door knobs', 4, 'Living Room', 'Daily'),
    ('Washing walls', 2, 'Kitchen', 'Twice Weekly'),
    ('Cleaning the windows', 12, 'Office', 'Monthly'),
    ('Washing rugs', 4, 'Garage', 'Twice Monthly'),
    ('Cleaning the microwave', 6, 'Office', 'Weekly'),
    ('Cleaning the garage', 11, 'Living Room', 'Twice Weekly'),
    ('Wiping down electronics', 4, 'Bathroom', 'Twice Weekly'),
    ('Changing air filters', 10, 'Living Room', 'Twice Monthly'),
    ('Cleaning baseboards', 6, 'Garden', 'Weekly'),
    ('Cleaning blinds', 5, 'Bathroom', 'Monthly'),
    ('Cleaning light fixtures', 11, 'Bedroom', 'Twice Monthly'),
    ('Mopping the floor', 9, 'Garden', 'Monthly'),
    ('Cleaning the fish tank', 9, 'Bedroom', 'Monthly'),
    ('Cleaning the microwave', 9, 'Office', 'Monthly'),
    ('Cleaning shower curtain', 11, 'Bedroom', 'Monthly'),
    ('Cleaning air vents', 1, 'Living Room', 'Daily'),
    ('Washing the dog', 8, 'Bathroom', 'Twice Monthly'),
    ('Watering plants', 2, 'Bedroom', 'Daily'),
    ('Cleaning the stove', 4, 'Bathroom', 'Monthly'),
    ('Vacuuming the carpet', 11, 'Office', 'Daily'),
    ('Cleaning gutters', 2, 'Garage', 'Monthly'),
    ('Raking leaves', 5, 'Garage', 'Twice Weekly'),
    ('Polishing woodwork', 1, 'Living Room', 'Weekly'),
    ('Cleaning gutters', 2, 'Living Room', 'Monthly'),
    ('Cleaning gutters', 6, 'Office', 'Twice Weekly'),
    ('Washing the dog', 1, 'Office', 'Twice Monthly'),
    ('Cleaning curtains', 6, 'Bedroom', 'Daily'),
    ('Wiping down electronics', 5, 'Garden', 'Monthly'),
    ('Washing walls', 10, 'Kitchen', 'Monthly'),
    ('Folding laundry', 10, 'Living Room', 'Twice Monthly'),
    ('Cleaning drains', 7, 'Living Room', 'Twice Weekly'),
    ('Cleaning baseboards', 3, 'Living Room', 'Daily'),
    ('Washing the dog', 4, 'Office', 'Daily'),
    ('Cleaning light fixtures', 6, 'Kitchen', 'Twice Monthly'),
    ('Cleaning coffee maker', 8, 'Office', 'Monthly'),
    ('Cleaning baseboards', 8, 'Bathroom', 'Twice Monthly'),
    ('Sweeping the floor', 11, 'Living Room', 'Twice Monthly'),
    ('Making the bed', 4, 'Bathroom', 'Twice Monthly'),
    ('Cleaning the bathroom', 10, 'Office', 'Monthly'),
    ('Making the bed', 2, 'Garden', 'Twice Monthly'),
    ('Raking leaves', 7, 'Kitchen', 'Monthly'),
    ('Cleaning the grill', 2, 'Bathroom', 'Weekly'),
    ('Taking out the trash', 4, 'Garage', 'Monthly'),
    ('Wiping down electronics', 2, 'Bedroom', 'Twice Monthly'),
    ('Ironing clothes', 7, 'Office', 'Monthly'),
    ('Doing the dishes', 7, 'Bathroom', 'Daily'),
    ('Making the bed', 1, 'Bathroom', 'Daily'),
    ('Washing the dog', 5, 'Garage', 'Weekly'),
    ('Washing walls', 4, 'Kitchen', 'Twice Monthly'),
    ('Cleaning blinds', 10, 'Garage', 'Twice Monthly'),
    ('Polishing shoes', 8, 'Garden', 'Twice Monthly'),
    ('Sweeping the floor', 3, 'Garage', 'Twice Weekly'),
    ('Washing walls', 11, 'Living Room', 'Twice Monthly'),
    ('Cleaning the windows', 11, 'Garage', 'Twice Monthly'),
    ('Folding laundry', 7, 'Garage', 'Twice Weekly'),
    ('Washing the car', 11, 'Garden', 'Daily'),
    ('Cleaning blinds', 6, 'Living Room', 'Weekly'),
    ('Watering plants', 2, 'Office', 'Monthly'),
    ('Cleaning door knobs', 3, 'Bedroom', 'Weekly'),
    ('Cleaning the fish tank', 12, 'Garage', 'Weekly'),
    ('Cleaning curtains', 9, 'Office', 'Monthly'),
    ('Cleaning door knobs', 7, 'Garage', 'Daily'),
    ('Cleaning shower curtain', 12, 'Office', 'Daily'),
    ('Washing bed linens', 9, 'Kitchen', 'Weekly'),
    ('Cleaning coffee maker', 8, 'Office', 'Twice Monthly'),
    ('Cleaning air vents', 1, 'Kitchen', 'Twice Monthly'),
    ('Cleaning the garage', 9, 'Bathroom', 'Weekly'),
    ('Cleaning the garage', 3, 'Bathroom', 'Twice Weekly'),
    ('Cleaning the microwave', 12, 'Garage', 'Twice Weekly'),
    ('Shoveling snow', 3, 'Office', 'Twice Weekly'),
    ('Cleaning curtains', 7, 'Kitchen', 'Daily'),
    ('Washing bed linens', 4, 'Office', 'Twice Weekly'),
    ('Making the bed', 3, 'Living Room', 'Monthly'),
    ('Cleaning air vents', 9, 'Kitchen', 'Daily')
]

boilerplate_rooms = [
    ("Kitchen", 2),
    ("Bedroom_1", 1),
    ("Bedroom_2", 1),
    ("Bathroom", 4),
    ("Garage", 1),
    ("Garden", 1),
    ("Upstairs Bathroom", 3),
    ("Terrace", 2),
    ("Atic", 4)
]

# Populate DB button, with the standard items
@helpers_bp.route('/populate_db', methods=['POST'])
@login_required
def populate_db():
    user_id = session.get('user_id') 
    conn = get_db_connection()
    cursor = conn.cursor()
    tasks_with_email = [(user_id,) + task_tuple for task_tuple in boilerplate_tasks]
    rooms_with_email = [(user_id,) + room_tuple for room_tuple in boilerplate_rooms]

    # Your function to populate the database
    cursor.executemany('INSERT INTO tasks (user_id, description, points, room, frequency) VALUES (?, ?, ?, ?, ?)', tasks_with_email)
    cursor.executemany('INSERT INTO rooms (user_id, name, modifier) VALUES (?, ?, ?)', rooms_with_email)
    cursor.execute("UPDATE users SET default_database=? WHERE user_id=?", (1, user_id))
    conn.commit()
    conn.close()

    flash('Standard database updated succesfully!', 'success')
    return redirect(url_for('main'))

@helpers_bp.route('/clear_db', methods=['POST'])
@login_required
def clear_db():
    user_id = session.get('user_id') 
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tasks;")
    cursor.execute("DELETE FROM rooms;")
    cursor.execute("DELETE FROM flatmates;")

    cursor.execute("DELETE FROM SQLITE_SEQUENCE WHERE name='tasks';")
    cursor.execute("DELETE FROM SQLITE_SEQUENCE WHERE name='rooms';")
    cursor.execute("DELETE FROM SQLITE_SEQUENCE WHERE name='flatmates';")
    cursor.execute("UPDATE users SET default_database=? WHERE user_id=?", (0, user_id))
    conn.commit()
    conn.close()

    flash('Database cleared successfully :( ', 'success')
    return redirect(url_for('main'))

@helpers_bp.route('/viewdata')
@login_required
def viewdata():
    conn = get_db_connection()
    tasks = conn.execute("SELECT * FROM tasks ORDER BY id DESC ;").fetchall()
    rooms = conn.execute("SELECT * FROM rooms ORDER BY id DESC ;").fetchall()
    flatmates = conn.execute("SELECT * FROM flatmates ORDER BY id DESC ").fetchall()
    return render_template('viewdata.html', rooms=rooms, tasks=tasks, flatmates=flatmates)
