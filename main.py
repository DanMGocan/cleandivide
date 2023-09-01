#pip install -r requirements.txt

from flask import Blueprint, Flask, render_template, request, url_for, flash, redirect, session
from flask_login import login_required, UserMixin, LoginManager, login_user, logout_user, current_user
from views.auth import auth_bp, setup_google, add_or_get_user
from views.additems import additems_bp
from views.helpers import helpers_bp
from views.generator import generator_bp
from models import get_db_connection



<<<<<<< HEAD
=======


>>>>>>> 1dd5863fae90134e8fd1276f8204a313c7863dd1
# Creating the instance of the Flask application with the name app
app = Flask(__name__)
app.config.from_object('config')

# Creates the authentication
setup_google(app)
app.register_blueprint(auth_bp)
app.register_blueprint(additems_bp)
app.register_blueprint(helpers_bp)
app.register_blueprint(generator_bp)

# Using the app instance to handle incoming requests and send answers
@app.route("/") # decorator -> transforms functions' return value in an HTTP response. This function will respond to the "/" URL requests 
def main():
    # conn = get_db_connection()
    # tasks = conn.execute("SELECT * FROM tasks").fetchall()
    # conn.close()
    user_id = session.get('user_id')
    if current_user.is_authenticated:

        conn = get_db_connection()
        cursor = conn.cursor()

        tasks = conn.execute("SELECT * FROM tasks WHERE user_id = ? ORDER BY id DESC LIMIT 10 ", (user_id, )).fetchall()
        rooms = conn.execute("SELECT * FROM rooms WHERE user_id = ? ORDER BY id DESC LIMIT 10 ", (user_id, )).fetchall()
        flatmates = conn.execute("SELECT * FROM flatmates WHERE user_id = ? ORDER BY id DESC LIMIT 10 ", (user_id, )).fetchall()
        popular_tasks = conn.execute("SELECT description FROM tasks GROUP BY description ORDER BY COUNT(description) DESC LIMIT 100").fetchall()

        cursor.execute("SELECT default_database FROM users WHERE user_id=?", (user_id, ))
        row = cursor.fetchone()
        default_database_bool = row[0]

        template_data = {
            "tasks": tasks,
            "rooms": rooms,
            "flatmates": flatmates,
            "user_email": user_id,
            "default_database_bool": default_database_bool,
            "popular_tasks": popular_tasks
        }

        return render_template('dashboard.html', template_data = template_data) # For logged-in users
    else:
        return render_template('index.html') # For guests

@app.route("/about")
def about():
    return render_template("about.html")

@app.context_processor
def inject_user_email():
    user_id = session.get('user_id')
    return dict(user_id=user_id)





if __name__ == '__main__':
    app.run()