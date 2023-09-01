from flask import Blueprint, redirect, url_for, session, render_template, flash, request, jsonify
from flask_login import login_required
from models import get_db_connection

helpers_bp = Blueprint('helpers_bp', __name__)

boilerplate_tasks = [
    ('cleaning the garage', 2, 'Garage', 'Daily'),
    ('making the bed', 4, 'Bedroom', 'Weekly'),
    ('trimming the hedge', 9, 'Garden', 'Weekly'),
    ('cleaning the bathroom', 9, 'Bathroom', 'Monthly'),
    ('changing air filters', 4, 'Living Room', 'Daily'),
    ('wiping down electronics', 4, 'Office', 'Twice Monthly'),
    ('wleaning the fish tank', 1, 'Garden', 'Twice Monthly'),
    ('cleaning baseboards', 10, 'Office', 'Weekly'),
    ('raking leaves', 4, 'Garden', 'Twice Monthly'),
    ('cleaning blinds', 10, 'Bathroom', 'Daily'),
    ('doing the dishes', 7, 'Kitchen', 'Monthly'),
    ('ironing clothes', 1, 'Bedroom', 'Twice Weekly'),
    ('polishing shoes', 5, 'Closet', 'Twice Monthly'),
    ('polishing woodwork', 11, 'Living Room', 'Weekly'),
    ('sweeping the floor', 9, 'Living Room', 'Twice Weekly'),
    ('dusting the furniture', 12, 'Living Room', 'Twice Monthly'),
    ('Cleaning coffee maker', 4, 'Kitchen', 'Daily'),
    ('Cleaning door knobs', 4, 'All Rooms', 'Daily'),
    ('Washing walls', 2, 'Hallway', 'Twice Weekly'),
    ('Washing rugs', 4, 'Laundry Room', 'Twice Monthly'),
    ('Cleaning the microwave', 6, 'Kitchen', 'Weekly'),
    ('Cleaning light fixtures', 11, 'Bedroom', 'Twice Monthly'),
    ('Mopping the floor', 9, 'Kitchen', 'Monthly'),
    ('Cleaning shower curtain', 11, 'Bathroom', 'Monthly'),
    ('Cleaning air vents', 1, 'All Rooms', 'Daily'),
    ('Washing the dog', 8, 'Garden', 'Twice Monthly'),
    ('Watering plants', 2, 'Garden', 'Daily'),
    ('Cleaning the stove', 4, 'Kitchen', 'Monthly'),
    ('Cleaning gutters', 2, 'Outside', 'Monthly'),
    ('Washing the car', 11, 'Driveway', 'Daily'),
    ('Cleaning curtains', 6, 'Living Room', 'Daily'),
    ('Folding laundry', 10, 'Laundry Room', 'Twice Monthly'),
    ('Cleaning drains', 7, 'Bathroom', 'Twice Weekly'),
    ('Washing bed linens', 9, 'Laundry Room', 'Weekly'),
    ('Shoveling snow', 3, 'Driveway', 'Seasonal'),
    ('Scrubbing the grill', 6, 'Garden', 'Weekly'),
    ('Taking out the trash', 4, 'Kitchen', 'Daily'),
    ('Feeding the pets', 1, 'All Rooms', 'Daily'),
    ('Composting', 5, 'Garden', 'Weekly'),
    ('Sanitizing toys', 4, 'Children\'s Room', 'Weekly'),
    ('Polishing silverware', 7, 'Dining Room', 'Monthly'),
    ('Oiling hinges', 3, 'All Rooms', 'Monthly'),
    ('Cleaning the fridge', 12, 'Kitchen', 'Monthly'),
    ('Cleaning the oven', 11, 'Kitchen', 'Quarterly'),
    ('Weeding the garden', 8, 'Garden', 'Weekly'),
    ('Reorganizing bookshelves', 5, 'Living Room', 'Monthly'),
    ('Cleaning out the pantry', 6, 'Kitchen', 'Monthly'),
    ('Sanitizing remote controls', 2, 'Living Room', 'Weekly'),
    ('Cleaning computer keyboards', 4, 'Office', 'Weekly'),
    ('Washing pillows', 9, 'Bedroom', 'Monthly'),
    ('Changing batteries in smoke alarms', 3, 'All Rooms', 'Quarterly'),
    ('Emptying the dishwasher', 2, 'Kitchen', 'Daily'),
    ('Cleaning out gutters', 10, 'Outside', 'Quarterly'),
    ('Cleaning the pool', 12, 'Garden', 'Weekly'),
    ('Mowing the lawn', 7, 'Garden', 'Weekly'),
    ('Cleaning fans', 5, 'All Rooms', 'Monthly'),
    ('Dusting light bulbs', 4, 'All Rooms', 'Monthly'),
    ('Cleaning under furniture', 8, 'Living Room', 'Monthly'),
    ('Sanitizing doorbells', 2, 'Outside', 'Weekly'),
    ('Cleaning lampshades', 3, 'Living Room', 'Monthly'),
    ('Polishing kitchenware', 6, 'Kitchen', 'Weekly'),
    ('Cleaning pet areas', 8, 'All Rooms', 'Weekly'),
    ('Cleaning out closets', 10, 'Bedroom', 'Quarterly'),
    ('Repotting plants', 5, 'Garden', 'Quarterly'),
    ('Sanitizing bathroom', 8, 'Bathroom', 'Weekly'),
    ('Cleaning gaming controllers', 2, 'Living Room', 'Weekly'),
    ('Cleaning toothbrush holders', 5, 'Bathroom', 'Monthly'),
    ('Cleaning hair brushes', 3, 'Bathroom', 'Monthly'),
    ('Cleaning makeup brushes', 4, 'Bathroom', 'Weekly'),
    ('Organizing shoes', 9, 'Closet', 'Monthly'),
    ('Disinfecting toys', 6, 'Children\'s Room', 'Twice Monthly'),
    ('Cleaning yoga mats', 2, 'Home Gym', 'Weekly'),
    ('Cleaning up litter', 5, 'All Rooms', 'Daily'),
    ('Cleaning headphones', 2, 'All Rooms', 'Weekly'),
    ('Washing towels', 6, 'Laundry Room', 'Weekly'),
    ('Cleaning garden tools', 7, 'Garden', 'Monthly'),
    ('Sharpening kitchen knives', 4, 'Kitchen', 'Monthly'),
    ('Sorting mail', 1, 'Office', 'Daily'),
    ('Cleaning the fireplace', 8, 'Living Room', 'Quarterly'),
    ('Cleaning camera lenses', 3, 'Office', 'Monthly'),
    ('Cleaning phone screens', 2, 'All Rooms', 'Daily'),
    ('Cleaning sports equipment', 7, 'Garage', 'Monthly'),
    ('Cleaning wheelchairs', 5, 'All Rooms', 'Weekly'),
    ('Cleaning bird feeders', 4, 'Garden', 'Weekly'),
    ('Cleaning the shed', 9, 'Garden', 'Monthly'),
    ('Washing showerheads', 6, 'Bathroom', 'Monthly'),
    ('Cleaning attic', 10, 'Attic', 'Quarterly'),
    ('Cleaning bicycle', 7, 'Garage', 'Monthly')
]

boilerplate_rooms = [
    ("Kitchen",),
    ("Bedroom_1",),
    ("Bedroom_2",),
    ("Bathroom",)
]

# Populate DB button, with the standard items
@helpers_bp.route('/populate_db', methods=['GET', 'POST'])
@login_required
def populate_db():
    user_id = session.get('user_id') 
    conn = get_db_connection()
    cursor = conn.cursor()
    tasks_with_email = [(user_id,) + task_tuple for task_tuple in boilerplate_tasks]
    rooms_with_email = [(user_id,) + room_tuple for room_tuple in boilerplate_rooms]

    # Your function to populate the database
    cursor.executemany('INSERT INTO rooms (user_id, name) VALUES (?, ?)', rooms_with_email)
    cursor.executemany('INSERT INTO tasks (user_id, description, points, room, frequency) VALUES (?, ?, ?, ?, ?)', tasks_with_email)
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

    cursor.execute("DELETE FROM SQLITE_SEQUENCE WHERE name='tasks'")
    cursor.execute("DELETE FROM SQLITE_SEQUENCE WHERE name='rooms'")
    cursor.execute("DELETE FROM SQLITE_SEQUENCE WHERE name='flatmates'")
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




@helpers_bp.route('/delete', methods=['POST'])
@login_required
def delete_entry():
    table_name = request.form.get('table_name')
    id_to_delete = int(request.form.get('id'))  # Cast to int
    print(f"Deleting id {id_to_delete} from table {table_name}")  # Debugging
    conn = get_db_connection()

    # Safeguard against SQL Injection for table_name
    if table_name not in ['tasks', 'flatmates', 'rooms']:
        flash("Invalid table name", "danger")
        return redirect(url_for("main"))

    cursor = conn.cursor()
    cursor.execute(f"DELETE FROM {table_name} WHERE id=?", (id_to_delete,))
    conn.commit()
    conn.close()

    if cursor.rowcount:
        flash("Entry successfully deleted", "success")
    else:
        flash("No such entry", "warning")
  
    return_url = request.referrer or url_for("main")
    print(return_url)
    return redirect(return_url)
