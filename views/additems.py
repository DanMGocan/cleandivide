from flask import Blueprint, render_template, redirect, url_for, request, session, flash
from flask_login import login_required, UserMixin, LoginManager, login_user, logout_user, current_user
from flask_oauthlib.client import OAuth
from models import User, get_db_connection

additems_bp = Blueprint('additems_bp', __name__)

@additems_bp.route("/add", methods=("GET", "POST"))
@login_required
def add():
    if request.method == 'POST':
        description = request.form['description']
        points = request.form["points"]
        room = request.form["room"]
        user_id = session.get('user_id')  # Assuming you stored user's ID in session upon login

        if not user_id:
            flash('Please login first!', 'error')
            return redirect(url_for('main'))  # Redirect to a login page
        
        # Add task to database
        conn = get_db_connection()
        conn.execute('INSERT INTO tasks (user_id, description, points, room) VALUES (?, ?, ?, ?)', (user_id, description, points, room))
        conn.commit()
        conn.close()

        flash('Task added successfully!', 'success')
        return redirect(url_for('main'))  # Redirect to user's dashboard

    return render_template('add.html')


