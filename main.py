#pip install -r requirements.txt

from flask import Blueprint, Flask, render_template, request, url_for, flash, redirect, session
from flask_login import login_required, UserMixin, LoginManager, login_user, logout_user, current_user
from flask_mail import Mail
from views.auth import auth_bp, setup_google, setup_facebook, add_or_get_user
from views.additems import additems_bp
from views.helpers import helpers_bp
from views.generator import generator_bp
from views.dashboard import dashboard_bp
from context_processors import get_table_owner_status

from models import get_db_connection
# import logging 

# Creating the instance of the Flask application with the name app
app = Flask(__name__)
# logging.basicConfig(filename='cleandivide.log', level=logging.DEBUG)
app.config.from_object('config')

# Creates the authentication
setup_google(app)
setup_facebook(app)
app.register_blueprint(auth_bp)
app.register_blueprint(additems_bp)
app.register_blueprint(helpers_bp)
app.register_blueprint(generator_bp)
app.register_blueprint(dashboard_bp)

# Configuration for Flask-Mail
app.config['MAIL_SERVER'] = 'smtp.example.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = 'your_email@example.com'
app.config['MAIL_PASSWORD'] = 'your_password'
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False

mail = Mail(app)

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

        # If times_logged is 0, redirect the user to a different HTML page
        if times_logged == 0:
            return render_template('housestatus.html') 

        try:
            task_table = cursor.execute("SELECT * FROM task_table WHERE table_owner = ?", (user_id,)).fetchall()
        except:
            task_table = []

        if is_table_owner == 0:
            return redirect(url_for("dashboard_bp.dashboard"))  # For users who have an active table
        elif is_table_owner == 1:
            return redirect(url_for("additems_bp.add_items"))  # For users who don't have an active table
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
