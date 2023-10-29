
from flask import Blueprint, redirect, url_for, session, render_template, flash, abort
from flask_login import login_required
from models import get_db_connection
from context_processors import get_table_owner_status
from flask_mail import Mail
from datetime import datetime

profile_bp = Blueprint('profile_bp', __name__)
#TODO: Add tasks completed, tasks assigned, 
@profile_bp.route('/profile/<user_id>')
@login_required
def user_profile(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    user_data = cursor.fetchone()

    if user_data is None:
        conn.close()
        abort(404)  # User not found
    else:
        # Convert the first_login string to a datetime object
        first_login_datetime = datetime.strptime(user_data['first_login'], '%Y-%m-%d %H:%M:%S.%f')
    
         # Now format the datetime object to a string
        formatted_first_login = first_login_datetime.strftime('%A, %B %d, %Y')
        
        user_dict = {
            'id': user_data[0],
            'username': user_data[1],
            'table_owner': user_data[5],
            'points': user_data[7],
            'awards': user_data[8],
            'first_login': formatted_first_login,
            'times_logged': user_data[4]
        }

        # Get the total tasks assigned to the user
        cursor.execute(
            "SELECT COUNT(*) FROM task_table WHERE task_owner = ?",
            (user_id,)
        )
        total_tasks = cursor.fetchone()[0]

        # Get the total tasks completed by the user
        cursor.execute(
            "SELECT COUNT(*) FROM task_table WHERE task_owner = ? AND task_complete = 1",
            (user_id,)
        )
        completed_tasks = cursor.fetchone()[0]

        conn.close()

        return render_template(
            'profile.html',
            user=user_dict,
            total_tasks=total_tasks,
            completed_tasks=completed_tasks
        )


def purchase_tools(total_points):
    points_based_awards = {}


