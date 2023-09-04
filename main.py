#pip install -r requirements.txt


from flask import Blueprint, Flask, render_template, request, url_for, flash, redirect, session
from flask_login import login_required, UserMixin, LoginManager, login_user, logout_user, current_user
from views.auth import auth_bp, setup_google, add_or_get_user
from views.additems import additems_bp
from views.helpers import helpers_bp
from views.generator import generator_bp
from views.dashboard import dashboard_bp
from models import get_db_connection
import logging 

# Creating the instance of the Flask application with the name app
app = Flask(__name__)
logging.basicConfig(filename='cleandivide.log', level=logging.DEBUG)
app.config.from_object('config')



# Creates the authentication
setup_google(app)
app.register_blueprint(auth_bp)
app.register_blueprint(additems_bp)
app.register_blueprint(helpers_bp)
app.register_blueprint(generator_bp)
app.register_blueprint(dashboard_bp)

# Using the app instance to handle incoming requests and send answers
@app.route("/") # decorator -> transforms functions' return value in an HTTP response. This function will respond to the "/" URL requests 
def main():

    conn = get_db_connection()
    cursor = conn.cursor()
    user_id = session.get('user_id')

    if current_user.is_authenticated:
        try:
            task_table = conn.execute("SELECT * FROM task_table WHERE table_owner = ?", (user_id, )).fetchall()
        except:
            task_table = 0
    
        if len(task_table) > 0:
            return redirect(url_for("dashboard_bp.dashboard")) # For users who have an active table
        
        else:
            return redirect(url_for("additems_bp.add_items")) # For users who have an active table

    else:
        return render_template('index.html') # For guests

@app.route("/about")
def about():
    return render_template("about.html")

# To have the user e-mail address available throughout the app #
@app.context_processor
def inject_user_email():
    user_id = session.get('user_id')
    return dict(user_id=user_id)

@app.context_processor
def inject_table_owner():
    user_id = session.get('user_id')
    is_table_owner = False  # Default value
    
    if user_id:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT table_owner FROM users WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row and row['table_owner'] == 1:
            is_table_owner = True
            
    return dict(user_id=user_id, is_table_owner=is_table_owner)

