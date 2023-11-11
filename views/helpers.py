from flask import Blueprint, redirect, url_for, session, render_template, flash, request, jsonify
from flask_login import login_required
from models import get_db_connection
from context_processors import get_table_owner_status
from flask_mail import Mail
import random
from random import choice
from datetime import datetime, timedelta

helpers_bp = Blueprint('helpers_bp', __name__)

# Helper for Mail logic
mail = Mail()

# Helper functions #
def get_power_costs(user_id):

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT reassign, skip, procrastinate, lower_reward_threshold, higher_reward_threshold FROM powercosts WHERE user_id = ?', (user_id,))
    power_costs_results = cursor.fetchone()

    if power_costs_results:
        power_costs = {
            "reassign": power_costs_results[0],
            "skip": power_costs_results[1],
            "procrastinate": power_costs_results[2],
            "lower_threshold": power_costs_results[3],
            "higher_threshold": power_costs_results[4]
        }
    else:
        power_costs = {
            "reassign": 0,
            "skip": 0,
            "procrastinate": 0,
            "lower_threshold": 0,
            "higher_threshold": 0
        }

    return power_costs

@helpers_bp.route('/clear_db', methods=['POST'])
@login_required
def clear_db():
    user_id = session.get('user_id')
    print(f"User ID from session: {user_id}")  # Debugging print

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("PRAGMA foreign_keys = ON;")

        # Delete data from other tables first
        cursor.execute("DELETE FROM task_table;")
        cursor.execute("DELETE FROM daily_bonus;")
        cursor.execute("DELETE FROM tasks;")
        cursor.execute("DELETE FROM rooms;")

        # Now, delete from flatmates but keep the current user's data
        cursor.execute("DELETE FROM flatmates WHERE email != ?", (user_id,))

        # Reset auto-increment counters
        cursor.execute("DELETE FROM SQLITE_SEQUENCE WHERE name != 'flatmates'")

        conn.commit()
        flash('Database cleared successfully, except for your data!', 'success')
    except Exception as e:
        print(f"Error occurred: {e}")  # Additional error logging
        conn.rollback()
        flash(f'An error occurred while clearing the database: {e}', 'error')
    finally:
        conn.close()

    return redirect(url_for('main'))





@helpers_bp.route('/viewdata')
@login_required
def viewdata():

    is_table_owner = get_table_owner_status()

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
    if user_id_to_delete and table_name == "flatmates" and user_id_to_delete[0] == user_id:
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
        id = int(request.form.get('task_id'))  # Cast to int
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
            cursor.execute("SELECT total_tasks_completed FROM users WHERE user_id = ?", (user_id,))
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

        # Retrieve the flatmate ID for the current user
        cursor.execute("SELECT id FROM flatmates WHERE email = ?", (user_id,))
        flatmate_result = cursor.fetchone()

        if not flatmate_result:
            flash("No flatmate account found for the current user", "warning")
            return redirect(request.referrer or url_for("dashboard"))

        flatmate_id = flatmate_result[0]
        # Update the task as complete
        cursor.execute("""
            UPDATE task_table 
            SET task_complete = 1 
            WHERE id = ? AND task_owner = ?
            """, (id, flatmate_id))

        # Increment total_tasks_completed for the user
        cursor.execute("""
            UPDATE users 
            SET total_tasks_completed = total_tasks_completed + 1 
            WHERE user_id = ?
            """, (user_id,))

        conn.commit()

        # Check if the task was successfully updated
        cursor.execute("SELECT task_id FROM task_table WHERE id = ? AND task_owner = ?", (id, flatmate_id))
        task_table_result = cursor.fetchone()

        if not task_table_result:
            flash("No such task or it's not owned by you", "warning")
            return redirect(request.referrer or url_for("dashboard"))

        task_id = task_table_result[0]

        # Get the points value of the task
        task_points_query = "SELECT points FROM tasks WHERE id = ?"
        cursor.execute(task_points_query, (task_id,))
        task_points_value = cursor.fetchone()

        if task_points_value:
            task_points_value = task_points_value[0]  # Extract points from the tuple
            power_costs = get_power_costs(user_id)
            task_points = round(random.uniform(task_points_value * power_costs["lower_threshold"], task_points_value * power_costs["higher_threshold"]))

            # Update the user's points
            cursor.execute("UPDATE users SET points = points + ? WHERE user_id = ?", (task_points, user_id))
            conn.commit()

            # Logic to check the awards and assign them as necessary
            cursor.execute("SELECT * FROM awards WHERE user_id = ?", (user_id,))
            user_awards = cursor.fetchone()

            flash(f"Task successfully marked as complete and {task_points} Dust Dollars awarded!", "success")
        else:
            flash("No such task found or it has already been marked as complete", "warning")

        conn.close()
        
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

        # Add the default power costs to user #
        cursor.execute('SELECT 1 FROM powercosts WHERE user_id = ?', (user_id,))
        power_costs_true = cursor.fetchone()

        if not power_costs_true:
            # No power costs record found for the user, so insert a new record with default values
            cursor.execute('INSERT INTO powercosts (user_id) VALUES (?)', (user_id,))

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
    user_id = session["user_id"]
    cost = get_power_costs(user_id)["reassign"]
    try:
        id = int(request.form.get('task_id'))  # Cast to int
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT t.description 
            FROM tasks t
            JOIN task_table tt ON t.id = tt.task_id
            WHERE tt.id = ?
        """, (id,))
        task_description_row = cursor.fetchone()
        task_description = task_description_row[0] if task_description_row else "Unknown Task"



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

        # Get the flatmate ID of the logged-in user
        cursor.execute("SELECT id FROM flatmates WHERE user_id = ?", (user_id,))
        current_user_flatmate_id = cursor.fetchone()
        current_user_flatmate_id = current_user_flatmate_id[0] if current_user_flatmate_id else None

        # Fetch all flatmates associated with the table_owner except the logged-in user
        cursor.execute("SELECT id, email FROM flatmates WHERE user_id = ?", (table_owner,))
        flatmates = cursor.fetchall()
        flatmates = [flatmate for flatmate in flatmates if flatmate[0] != current_user_flatmate_id]

        if not flatmates or len(flatmates) < 1:  # No other flatmates to reassign to
            flash("No other flatmates available for reassignment", "warning")
            return redirect(url_for("dashboard_bp.dashboard"))

        # Remove current task_owner from potential reassignment list
        cursor.execute("SELECT task_owner FROM task_table WHERE id = ?", (id,))
        current_task_owner = cursor.fetchone()[0]

        flatmates = [flatmate for flatmate in flatmates if flatmate[0] != current_task_owner]

        # Randomly select a flatmate
        flatmate_id, _ = choice(flatmates)

        # Reassign task to the new flatmate
        cursor.execute("UPDATE task_table SET task_owner = ? WHERE id = ?", (flatmate_id, id))

        # Decrease points from the user for the reassign action
        cursor.execute("UPDATE users SET points = points - ? WHERE user_id = ?", (cost, table_owner))


        conn.commit()

        # Check if the reassignment was successful
        if cursor.rowcount:
        # Fetch the email of the flatmate to whom the task was reassigned
            cursor.execute("SELECT email FROM flatmates WHERE id = ?", (flatmate_id,))
            flatmate_row = cursor.fetchone()
            reassigned_flatmate_email = flatmate_row[0] if flatmate_row else "Unknown Email"

            flash(f"Task '{task_description}' successfully reassigned to {reassigned_flatmate_email}", "success")
        else:
            flash("Reassignment failed", "warning")


    except Exception as e:
        print("An error occurred:", str(e))
        flash("An error occurred while reassigning the task", "error")

    conn.close()
    return redirect(url_for("dashboard_bp.dashboard"))


@helpers_bp.route('/skip_task', methods=["GET", 'POST'])
@login_required
def skip_task():
    user_id = session["user_id"]
    cost = get_power_costs(user_id)["skip"]  # Define the cost variable
    try:
        task_id = int(request.form.get('task_id'))  # Cast to int
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
    cost = get_power_costs(user_id)["procrastinate"]
    try:
        task_id = int(request.form.get('task_id'))  # Cast to int
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

# Function to assign user premium status #
@helpers_bp.route("/payment-successful", methods=['GET', 'POST'])
@login_required
def payment_successfull():
    user_id = session["user_id"]
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET premium_user = ? WHERE user_id = ?", (1, user_id))
    conn.commit()
    conn.close()
    flash("Payment was successful, THANK YOU IMMENSELY for your support!", "success")
    return redirect(url_for("main"))

# Function to assign user premium status #
@helpers_bp.route("/payment-unsuccessful", methods=['GET', 'POST'])
@login_required
def payment_unsuccessfull():
    user_id = session["user_id"]
    flash("Something went wrong, I am sorry", "warning")
    return redirect(url_for("main"))