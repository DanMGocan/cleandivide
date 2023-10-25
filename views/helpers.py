from flask import Blueprint, redirect, url_for, session, render_template, flash, request, jsonify
from flask_login import login_required
from models import get_db_connection
from context_processors import get_table_owner_status
from flask_mail import Mail
from random import choice 
from views.dashboard import power_costs

helpers_bp = Blueprint('helpers_bp', __name__)

# Helper for Mail logic
mail = Mail()

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

    is_table_owner = get_table_owner_status()
    print(is_table_owner)

    if is_table_owner["is_table_owner"] == 0:
        flash("You are not allowed here", "danger")
        return redirect(url_for("dashboard_bp.dashboard"))
    
    conn = get_db_connection()
    tasks = conn.execute("SELECT * FROM tasks ORDER BY id DESC ;").fetchall()
    rooms = conn.execute("SELECT * FROM rooms ORDER BY id DESC ;").fetchall()
    flatmates = conn.execute("SELECT * FROM flatmates ORDER BY id DESC ").fetchall()
    return render_template('viewdata.html', rooms=rooms, tasks=tasks, flatmates=flatmates)

@helpers_bp.route('/delete', methods=['POST'])
@login_required
def delete_entry():
    user_id = session["user_id"]
    table_name = request.form.get('table_name')
    id_to_delete = int(request.form.get('id'))  # Cast to int
    conn = get_db_connection()

    # Safeguard against SQL Injection for table_name
    if table_name not in ['tasks', 'flatmates', 'rooms']:
        flash("Invalid table name", "danger")
        return redirect(url_for("main"))

    user_id_to_delete = conn.execute("SELECT user_id FROM flatmates WHERE id=?", (id_to_delete,)).fetchone()
    if user_id_to_delete and user_id_to_delete[0] == user_id:
        flash("You cannot delete yourself...", "danger")
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
    return redirect(return_url)

@helpers_bp.route('/mark_complete', methods=['POST'])
@login_required
def mark_complete():
    try:
        id = int(request.form.get('id'))  # Cast to int
        conn = get_db_connection()
        cursor = conn.cursor()

        # Get the points value of the task
        cursor.execute("SELECT task_points FROM task_table WHERE id = ?", (id,))
        task_points = cursor.fetchone()

        if task_points:
            task_points = task_points[0]  # Extract points from the tuple
        else:
            flash("No such task", "warning")
            return redirect(request.referrer or url_for("dashboard"))

        # Mark the task as complete in 'task_table'
        cursor.execute("UPDATE task_table SET task_complete = 1 WHERE id = ?", (id,))

        # Update the user's points
        user_id = session.get('user_id')
        cursor.execute("UPDATE users SET points = points + ? WHERE user_id = ?", (task_points, user_id))


        conn.commit()
        conn.close()

        if cursor.rowcount:
            flash(f"Task {id} successfully marked as complete", "success")
        else:
            flash("No such task", "warning")
    except Exception as e:
        print("An error occurred:", str(e))
        flash("An error occurred while marking the task as complete", "error")

    return redirect(request.referrer or url_for("dashboard"))


@helpers_bp.route('/become_house_master', methods=["GET", 'POST'])
@login_required
def become_house_master():
    user_id = session.get('user_id')   

    # Establish a database connection and cursor
    conn = get_db_connection()
    cursor = conn.cursor()

    # Fetch the current times_logged value
    user_record = cursor.execute("SELECT times_logged FROM users WHERE user_id = ?", (user_id,)).fetchone()
    times_logged = user_record[0] if user_record else 0

    # Update the table_owner value to 1 and increment times_logged by 1
    cursor.execute("UPDATE users SET table_owner = 1, times_logged = ? WHERE user_id = ?", (times_logged + 1, user_id,))
    conn.commit()
    conn.close()

    return redirect(url_for('additems_bp.add_items'))


@helpers_bp.route('/become_house_member', methods=["GET", 'POST'])
@login_required
def become_house_member():
    user_id = session.get('user_id')

    # Establish a database connection and cursor
    conn = get_db_connection()
    cursor = conn.cursor()

    # Fetch the current times_logged value
    user_record = cursor.execute("SELECT times_logged FROM users WHERE user_id = ?", (user_id,)).fetchone()
    times_logged = user_record[0] if user_record else 0

    # Increment times_logged by 1
    cursor.execute("UPDATE users SET times_logged = ? WHERE user_id = ?", (times_logged + 1, user_id,))
    conn.commit()
    conn.close()

    return redirect(url_for('dashboard_bp.dashboard'))

@helpers_bp.route('/reassign_task', methods=["GET", 'POST'])
@login_required
def reassign_task():
    cost = power_costs["reassign"]
    user_id = session["user_id"]
    try:
        id = int(request.form.get('id'))  # Cast to int
        conn = get_db_connection()
        cursor = conn.cursor()

        # Get number of points of the user 
        cursor.execute("SELECT points FROM users WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()
        if row:
            available_points = row[0]
        else:
            # Handle the case where no matching row was found, e.g.:
            available_points = 0  # Or set a default value, or raise an error, etc.


        if available_points < cost:
            flash("Not enough points for this I am afraid", "warning")
            return redirect(url_for("dashboard_bp.dashboard"))

        # Get the table_owner of the task
        cursor.execute("SELECT table_owner FROM task_table WHERE id = ?", (id,))
        table_owner = cursor.fetchone()
        if not table_owner:
            flash("No such task", "warning")
            return redirect(url_for("dashboard_bp.dashboard"))
        table_owner = table_owner[0]

        # Retrieve all flatmates associated with the table_owner
        cursor.execute("SELECT id, email FROM flatmates WHERE user_id = ?", (table_owner,))
        flatmates = cursor.fetchall()

        if not flatmates or len(flatmates) <= 1:  # No other flatmates to reassign to
            flash("No other flatmates available for reassignment", "warning")
            return redirect(url_for("dashboard_bp.dashboard"))

        # Remove current task_owner from potential reassignment list
        cursor.execute("SELECT task_owner FROM task_table WHERE id = ?", (id,))
        current_task_owner = cursor.fetchone()[0]
        flatmates = [flatmate for flatmate in flatmates if flatmate[0] != current_task_owner]

        # Randomly select a flatmate
        flatmate_id, flatmate_email = choice(flatmates)

        # Reassign task to the new flatmate
        cursor.execute("UPDATE task_table SET task_owner = ? WHERE id = ?", (flatmate_email, id))

        # Decrease points from the user for the reassign action
        cursor.execute("UPDATE users SET points = points - ? WHERE user_id = ?", (cost, table_owner))


        conn.commit()
        conn.close()

        if cursor.rowcount:
            flash(f"Task {id} successfully reassigned to {flatmate_email}", "success")
        else:
            flash("Reassignment failed", "warning")
    except Exception as e:
        print("An error occurred:", str(e))
        flash("An error occurred while reassigning the task", "error")

    return redirect(url_for("dashboard_bp.dashboard"))


@helpers_bp.route('/skip_task', methods=["GET", 'POST'])
@login_required
def skip_task():
    pass

@helpers_bp.route('/procrastinate_task', methods=["GET", 'POST'])
@login_required
def procrastinate_task():
    pass