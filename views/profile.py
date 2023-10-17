
from flask import Blueprint, redirect, url_for, session, render_template, flash, abort
from flask_login import login_required
from models import get_db_connection
from context_processors import get_table_owner_status
from flask_mail import Mail

profile_bp = Blueprint('profile_bp', __name__)

@profile_bp.route('/profile/<user_id>')
@login_required
def user_profile(user_id):
    #user_id = session["user_id"]
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    user_data = cursor.fetchone()

    if user_data is None:
        abort(404)  # User not found
    else:
        # Here, user_data will be a tuple containing the user's information.
        # You might want to convert it to a dictionary for easier access in the template.

        user_dict = {
            'id': user_data[0],
            'username': user_data[1],
            'table_ower': user_data[5],
            'points': user_data[6], 
            'awards': user_data[7]    
        }

        return render_template('profile.html', user=user_dict)

def purchase_tools(total_points):
    points_based_awards = {}


