#pip install -r requirements.txt

from flask import Blueprint, Flask, render_template, request, url_for, flash, redirect, session
from flask_login import login_required, UserMixin, LoginManager, login_user, logout_user, current_user
from views.auth import auth_bp, setup_google
from models import get_db_connection

# Creating the instance of the Flask application with the name app
app = Flask(__name__)
app.config.from_object('config')

# Creates the authentication
setup_google(app)
app.register_blueprint(auth_bp)

# Using the app instance to handle incoming requests and send answers
@app.route("/") # decorator -> transforms functions' return value in an HTTP response. This function will respond to the "/" URL requests 
def main():
    # conn = get_db_connection()
    # tasks = conn.execute("SELECT * FROM tasks").fetchall()
    # conn.close()
    
    if current_user.is_authenticated:
        return render_template('dashboard.html') # For logged-in users
    else:
        return render_template('index.html') # For guests

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/add", methods=("GET", "POST"))
def add():
    if request.method == "POST":
        task = request.form["content"]
        points = request.form["points"]
        room = request.form["room"]

        if not task:
            flash("Task is required!")
        else:
            conn = get_db_connection()
            conn.execute("INSERT INTO tasks (points, room, content) VALUES (?, ?, ?)",
                        (points, room, task))
            conn.commit()
            conn.close()

            return redirect(url_for("main"))

    return render_template("add.html")

if __name__ == '__main__':
    app.run()