#pip install -r requirements.txt

from flask import Blueprint, Flask, render_template, request, url_for, flash, redirect, session
from flask_login import login_required, UserMixin, LoginManager, login_user, logout_user, current_user
from flask_mail import Mail
from views.auth import auth_bp, setup_google, setup_facebook, add_or_get_user
from views.additems import additems_bp
from views.helpers import helpers_bp, mail
from views.generator import generator_bp
from views.dashboard import dashboard_bp
from views.profile import profile_bp
from context_processors import get_table_owner_status

from models import get_db_connection
from math import floor

import logging 
from logging.handlers import RotatingFileHandler

# Creating the instance of the Flask application with the name app
app = Flask(__name__)
app.config.from_object('config')

# Set up logging
handler = RotatingFileHandler('logger.log', maxBytes=10000, backupCount=1)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
app.logger.addHandler(handler)

# Creates the authentication
setup_google(app)
setup_facebook(app)

# Register the blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(additems_bp)
app.register_blueprint(helpers_bp)
app.register_blueprint(generator_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(profile_bp)

# Importing mail object
mail.init_app(app)
mail = Mail(app)

# At this point only God understands what is happening
# Custom Jinja2 filter to floor a number
def floor(value):
    """Return the floor of the value."""
    import math
    return math.floor(value)
app.jinja_env.filters['floor'] = floor


# Using the app instance to handle incoming requests and send answers
@app.route("/")
def main():
    conn = get_db_connection()
    cursor = conn.cursor()
    user_id = session.get('user_id')

    table_owner_info = get_table_owner_status()
    is_table_owner = table_owner_info["is_table_owner"]
    
    if current_user.is_authenticated:
        # Fetch the user's times_logged value
        user_record = cursor.execute("SELECT times_logged FROM users WHERE user_id = ?", (user_id,)).fetchone()
        times_logged = user_record[0] if user_record else None

        # If times_logged is 0, check if the user has tasks assigned
        if times_logged == 0:
            tasks_assigned = cursor.execute("SELECT id FROM task_table WHERE task_owner = ?", (user_id,)).fetchone()
            if tasks_assigned:
                return redirect(url_for("dashboard_bp.dashboard"))  # User has tasks assigned
            else:
                return render_template('housestatus.html')  # User doesn't have tasks assigned

        try:
            task_table = cursor.execute("SELECT * FROM task_table WHERE table_owner = ?", (user_id,)).fetchall()
        except:
            task_table = []

        if len(task_table) > 0:  # If task table has been generated
            return redirect(url_for("dashboard_bp.dashboard"))
        else:  # If task table has not been generated
            if is_table_owner == 1:
                return redirect(url_for("additems_bp.add_items"))
            else:
                return render_template('dashboard.html', total_tasks=0, is_table_owner=is_table_owner)
    else:
        return render_template('index.html')  # For guests



@app.route("/about")
def about():
    return render_template("about.html")

# To have the user status as a home master or member available #
@app.context_processor
def inject_table_owner():
    return get_table_owner_status()

# Check if this is the main module being executed.
if __name__ == "__main__":
    app.run(port=5000, debug=True) 


