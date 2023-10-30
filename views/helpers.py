from flask import Blueprint, redirect, url_for, session, render_template, flash, request, jsonify
from flask_login import login_required
from models import get_db_connection
from context_processors import get_table_owner_status
from flask_mail import Mail
from random import choice 
from views.dashboard import power_costs
from datetime import datetime, timedelta

helpers_bp = Blueprint('helpers_bp', __name__)

# Helper for Mail logic
mail = Mail()

@helpers_bp.route('/clear_db', methods=['POST'])
@login_required
def clear_db():
    user_id = session.get('user_id') 
    conn = get_db_connection()
    cursor = conn.cursor()

    # Enable foreign key constraint enforcement
    cursor.execute("PRAGMA foreign_keys = ON;")

    # Delete data from the tables in the right order
    cursor.execute("DELETE FROM task_table;")
    cursor.execute("DELETE FROM daily_bonus;")
    cursor.execute("DELETE FROM tasks;")
    cursor.execute("DELETE FROM flatmates;")
    cursor.execute("DELETE FROM rooms;")

    # Reset auto-increment counters
    cursor.execute("DELETE FROM SQLITE_SEQUENCE WHERE name='tasks'")
    cursor.execute("DELETE FROM SQLITE_SEQUENCE WHERE name='flatmates'")
    cursor.execute("DELETE FROM SQLITE_SEQUENCE WHERE name='rooms'")
    cursor.execute("DELETE FROM SQLITE_SEQUENCE WHERE name='task_table'")

    # Reset user's default_database column value
    cursor.execute("UPDATE users SET default_database=? WHERE user_id=?", (0, user_id))
    
    conn.commit()
    conn.close()

    flash('Database cleared successfully!', 'success')
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

    user_id_to_delete = conn.execute("SELECT email FROM flatmates WHERE id=?", (id_to_delete,)).fetchone()
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

@helpers_bp.route('/mark_complete', methods=["GET", "POST"])
@login_required
def mark_complete():
    try:
        id = int(request.form.get('id'))  # Cast to int
        conn = get_db_connection()
        cursor = conn.cursor()
        user_id = session["user_id"]

        # Logic to check the awards and assign them as necessary #
        cursor.execute("SELECT * FROM awards WHERE user_id = ?", (user_id,))
        user_awards = cursor.fetchone()

        # Tasks per day award #
        if not user_awards['five_tasks_day'] or not user_awards["ten_tasks_day"] or not user_awards["fifteen_tasks_day"]:
            cursor.execute("SELECT COUNT(id) FROM task_table WHERE task_owner = ? AND task_date = DATE('now') AND task_complete = 1", (user_id,))
            completed_tasks_today = cursor.fetchone()[0]
            if completed_tasks_today >= 5:
                cursor.execute("UPDATE awards SET five_tasks_day = 1 WHERE user_id = ?", (user_id,))
            if completed_tasks_today >= 10:
                cursor.execute("UPDATE awards SET ten_tasks_day = 1 WHERE user_id = ?", (user_id,))
            if completed_tasks_today >= 15:
                cursor.execute("UPDATE awards SET fifteen_tasks_day = 1 WHERE user_id = ?", (user_id,))

        # Completed Tasks Award #
        if not user_awards['completed_100_tasks'] or not user_awards["completed_250_tasks"] or not user_awards["completed_750_tasks"] or not user_awards["completed_1500_tasks"] or not user_awards["completed_2500_tasks"]:
            cursor.execute("SELECT COUNT(id) FROM task_table WHERE task_owner = ? AND task_complete = 1", (user_id,))
            total_completed_tasks = cursor.fetchone()[0]
            if total_completed_tasks >= 100:
                cursor.execute("UPDATE awards SET completed_100_tasks = 1 WHERE user_id = ?", (user_id,))
            if total_completed_tasks >= 250:
                cursor.execute("UPDATE awards SET completed_250_tasks = 1 WHERE user_id = ?", (user_id,))
            if total_completed_tasks >= 750:
                cursor.execute("UPDATE awards SET completed_750_tasks = 1 WHERE user_id = ?", (user_id,))
            if total_completed_tasks >= 1500:
                cursor.execute("UPDATE awards SET completed_1500_tasks = 1 WHERE user_id = ?", (user_id,))
            if total_completed_tasks >= 2500:
                cursor.execute("UPDATE awards SET completed_2500_tasks = 1 WHERE user_id = ?", (user_id,))

        # Membership Days Awards:
        cursor.execute("SELECT julianday(DATE('now')) - julianday(first_login) FROM users WHERE user_id = ?", (user_id,))
        membership_days = cursor.fetchone()[0]

        if not user_awards['member_30_days'] and membership_days >= 30:
            cursor.execute("UPDATE awards SET member_30_days = 1 WHERE user_id = ?", (user_id,))

        if not user_awards['member_120_days'] and membership_days >= 120:
            cursor.execute("UPDATE awards SET member_120_days = 1 WHERE user_id = ?", (user_id,))

        if not user_awards['member_365_days'] and membership_days >= 365:
            cursor.execute("UPDATE awards SET member_365_days = 1 WHERE user_id = ?", (user_id,))

        # Points-based Awards:
        cursor.execute("SELECT points FROM users WHERE user_id = ?", (user_id,))
        user_points = cursor.fetchone()[0]

        if not user_awards['check_500_points'] and user_points >= 500:
            cursor.execute("UPDATE awards SET check_500_points = 1 WHERE user_id = ?", (user_id,))

        if not user_awards['check_1000_points'] and user_points >= 1000:
            cursor.execute("UPDATE awards SET check_1000_points = 1 WHERE user_id = ?", (user_id,))

        if not user_awards['check_2500_points'] and user_points >= 2500:
            cursor.execute("UPDATE awards SET check_2500_points = 1 WHERE user_id = ?", (user_id,))

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

    try:
        # Delete the user from the flatmates table if they are there as a flatmate
        cursor.execute('DELETE FROM flatmates WHERE email = ?', (user_id,))

        # Fetch the current times_logged value
        user_record = cursor.execute("SELECT times_logged FROM users WHERE user_id = ?", (user_id,)).fetchone()
        times_logged = user_record[0] if user_record else 0

        # Add user to 'flatmates' table if not already present under their own user_id
        cursor.execute('SELECT * FROM flatmates WHERE user_id = ?', (user_id,))
        flatmate = cursor.fetchone()
        if not flatmate:
            cursor.execute('INSERT INTO flatmates (user_id, email) VALUES (?, ?)', (user_id, user_id))

        # Update the table_owner value to 1 and increment times_logged by 1
        cursor.execute("UPDATE users SET table_owner = 1, times_logged = ? WHERE user_id = ?", (times_logged + 1, user_id,))

        # Commit the transaction
        conn.commit()

    except Exception as e:
        # If any error occurs, rollback the transaction
        conn.rollback()
        flash(f"An error occurred: {e}", "danger")

    finally:
        # Always close the connection
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
    user_id = session["user_id"]
    cost = power_costs["skip"]  # Define the cost variable
    try:
        task_id = int(request.form.get('id'))  # Cast to int
        conn = get_db_connection()
        cursor = conn.cursor()

        # Verify the existence of the task
        cursor.execute("SELECT * FROM task_table WHERE id = ?", (task_id,))
        task = cursor.fetchone()
        if not task:
            flash("No such task", "warning")
            return redirect(url_for("dashboard_bp.dashboard"))
        
        # Delete the task for the day
        cursor.execute("DELETE FROM task_table WHERE id = ?", (task_id,))
        
        # Decrease points from the user for the skip action
        cursor.execute("UPDATE users SET points = points - ? WHERE user_id = ?", (cost, user_id))

        conn.commit()
        conn.close()

        if cursor.rowcount:
            flash(f"Task skipped for the day, {cost} points deducted", "success")
        else:
            flash("Failed to skip the task", "warning")
    except Exception as e:
        print("An error occurred:", str(e))
        flash("An error occurred while skipping the task", "error")

    return redirect(url_for("dashboard_bp.dashboard"))



@helpers_bp.route('/procrastinate_task', methods=["GET", 'POST'])
@login_required
def procrastinate_task():
    user_id = session["user_id"]
    cost = power_costs["procrastinate"]
    try:
        task_id = int(request.form.get('id'))  # Cast to int
        conn = get_db_connection()
        cursor = conn.cursor()

        # Verify the existence of the task and get its current due date
        cursor.execute("SELECT task_date FROM task_table WHERE id = ?", (task_id,))
        task = cursor.fetchone()
        if not task:
            flash("No such task", "warning")
            return redirect(url_for("dashboard_bp.dashboard"))

        current_due_date = datetime.strptime(task[0], '%Y-%m-%d')
        new_due_date = current_due_date + timedelta(days=1)
        new_due_date_str = new_due_date.strftime('%Y-%m-%d')

        # Update the due date of the task to the following day
        cursor.execute(
            "UPDATE task_table SET task_date = ? WHERE id = ?",
            (new_due_date_str, task_id)
        )

        # Decrease points from the user for the skip action
        cursor.execute("UPDATE users SET points = points - ? WHERE user_id = ?", (cost, user_id))

        conn.commit()
        conn.close()

        if cursor.rowcount:
            flash(f"Task {task_id} procrastinated to {new_due_date_str}", "success")
        else:
            flash("Failed to procrastinate the task", "warning")
    except Exception as e:
        print("An error occurred:", str(e))
        flash("An error occurred while procrastinating the task", "error")

    return redirect(url_for("dashboard_bp.dashboard"))

@helpers_bp.route('/daily_bonus', methods=['POST'])
@login_required
def daily_bonus():
    user_id = session["user_id"]
    today = datetime.now().date().isoformat()  # Get today's date in YYYY-MM-DD format

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Check if the user has already clicked the button today
        cursor.execute(
            "SELECT * FROM daily_bonus WHERE user_id = ? AND date = ?",
            (user_id, today)
        )
        already_clicked = cursor.fetchone()

        if already_clicked:
            flash("You have already claimed your daily bonus", "warning")
        else:
            # Award 5 points to the user
            cursor.execute(
                "UPDATE users SET points = points + 5 WHERE user_id = ?",
                (user_id,)
            )

            # Log the bonus claim
            cursor.execute(
                "INSERT INTO daily_bonus (user_id, date, points_awarded) VALUES (?, ?, 5)",
                (user_id, today)
            )

            flash("5 points have been added to your account", "success")

        conn.commit()
        conn.close()

    except Exception as e:
        print("An error occurred:", str(e))
        flash("An error occurred while processing your request", "error")

    return redirect(url_for("dashboard_bp.dashboard"))