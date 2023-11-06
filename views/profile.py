
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

    # Extract awards from the DB #
    cursor.execute("SELECT * FROM awards WHERE user_id=?", (user_id,))
    awards_data = cursor.fetchone()

    awards_dict = {
        'logged_in!': bool(awards_data["logged_in"]),
        'completed_five_tasks_in_a_day': bool(awards_data['five_tasks_day']),
        'completed_ten_tasks_in_a_day': bool(awards_data['ten_tasks_day']),
        'completed_fifteen_tasks_in_a_day': bool(awards_data['fifteen_tasks_day']),
        'member_for_30_days': bool(awards_data['member_30_days']),
        'member_for_120_days': bool(awards_data['member_120_days']),
        'member_for_365_days': bool(awards_data['member_365_days']),
        'had_500_points_unspent': bool(awards_data['check_500_points']),
        'had_1000_points_unspent': bool(awards_data['check_1000_points']),
        'had_2500_points_unspent': bool(awards_data['check_2500_points']),
        'completed_100_tasks': bool(awards_data['completed_100_tasks']),
        'completed_250_tasks': bool(awards_data['completed_250_tasks']),
        'completed_750_tasks': bool(awards_data['completed_750_tasks']),
        'completed_1500_tasks': bool(awards_data['completed_1500_tasks']),
        'completed_2500_tasks': bool(awards_data['completed_2500_tasks']),
}



    # Extract user data #
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
            'points': user_data[6],
            'awards': user_data[7],
            'first_login': formatted_first_login,
            'times_logged': user_data[3]
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
            completed_tasks=completed_tasks,
            awards=awards_dict

        )


def purchase_tools(total_points):
    points_based_awards = {}


