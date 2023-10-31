from flask import Blueprint, redirect, url_for, session, render_template, flash
from flask_login import login_required
from models import get_db_connection
from datetime import datetime, timedelta
import random
from itertools import groupby
from sqlite3 import IntegrityError
from context_processors import get_table_owner_status


admin_bp = Blueprint('admin_bp', __name__)

@admin_bp.route("/admin", methods=["GET", "POST"])
@login_required
def admin():
    conn = get_db_connection()
    cursor = conn.cursor()
    user_id = session["user_id"]
    if get_table_owner_status()["is_table_owner"] == 1:
        
        # Check if a task_table has been created
        cursor.execute("SELECT COUNT(*) FROM task_table WHERE table_owner = ?", (user_id,))
        table_exists = cursor.fetchone()[0] > 0

        if not table_exists:
            flash("No task table has been created yet.", "warning")
            conn.close()
            return redirect(url_for("main"))  # User has tasks assigned
        
        else:


            try:
                # Get the total points per user #
                cursor.execute('''
                    SELECT task_owner, SUM(task_points) AS total_points
                    FROM task_table
                    GROUP BY task_owner
                ''')
                flatmate_points_results = cursor.fetchall()

                # Get a list of all flatmates
                cursor.execute("SELECT id, email FROM flatmates WHERE user_id =?", (user_id,))
                flatmates = cursor.fetchall()

                completion_rates = {}  # Dictionary to store completion rates for each flatmate

                for flatmate in flatmates:
                    flatmate_id, flatmate_email = flatmate

                    # Get the total number of tasks assigned to the flatmate up to today
                    cursor.execute(
                        "SELECT COUNT(*) FROM task_table WHERE task_owner = ? AND task_date <= DATE('now')",
                        (flatmate_email,)
                    )
                    total_tasks = cursor.fetchone()[0]

                    # Get the total number of completed tasks for the flatmate up to today
                    cursor.execute(
                        "SELECT COUNT(*) FROM task_table WHERE task_owner = ? AND task_complete = 1 AND task_date <= DATE('now')",
                        (flatmate_email,)
                    )
                    completed_tasks = cursor.fetchone()[0]

                    # Avoid division by zero if no tasks are assigned
                    if total_tasks > 0:
                        completion_rate = (completed_tasks / total_tasks) * 100
                    else:
                        completion_rate = 100

                    # Store the completion rate
                    completion_rates[flatmate_email] = f"{completion_rate:.2f}%"

            except Exception as e:
                print("An error occurred:", str(e))
                flash("An error occurred while calculating completion rates", "error")
                return redirect(url_for("dashboard_bp.dashboard"))

            try:

                # Get today's date in YYYY-MM-DD format
                today = datetime.now().strftime('%Y-%m-%d')

                # Execute a query to get all of today's tasks across all users along with their completion status
                cursor.execute("""
                    SELECT 
                        users.user_id,
                        flatmates.email as flatmate_email,
                        task_table.task_description,
                        CASE WHEN task_table.task_complete = 1 THEN 'Complete' ELSE 'Incomplete' END as status
                    FROM 
                        task_table
                    JOIN 
                        users ON task_table.table_owner = users.user_id
                    JOIN
                        flatmates ON task_table.task_owner = flatmates.email
                    WHERE 
                        task_table.task_date = ?
                """, (today,))

                
                today_tasks = cursor.fetchall()
                conn.close()

            except Exception as e:
                print("An error occurred:", str(e))
                flash("An error occurred while fetching today's tasks", "error")
                return redirect(url_for("dashboard_bp.dashboard"))
            
            # Pass the completion rates to the template
            return render_template("admin.html", completion_rates=completion_rates, today_tasks = today_tasks, flatmate_points_results=flatmate_points_results)
    else:
        return redirect(url_for("dashboard_bp.dashboard"))
