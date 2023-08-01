#pip install -r requirements.txt

import sqlite3
import os
from flask import Flask, render_template, request, url_for, flash, redirect, session
from flask_oauthlib.client import OAuth
from flask_login import login_required, UserMixin, LoginManager, login_user
from werkzeug.exceptions import abort

# Creating the instance of the Flask application with the name app
app = Flask(__name__)
app.secret_key = os.urandom(24)
oauth = OAuth(app)

login_manager = LoginManager()
login_manager.init_app(app)

class User(UserMixin):
    def __init__(self, id):
        self.id = id

@login_manager.user_loader
def load_user(user_id):
    if "user_id" in session:
        return User(session["user_id"])
    return None


google = oauth.remote_app(
    'google',
    consumer_key='236830913630-ek9uioi8bbo97akshfoe9tk17kf5h6dd.apps.googleusercontent.com',
    consumer_secret='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',
    request_token_params={
        'scope': 'email',
    },
    base_url='https://www.googleapis.com/oauth2/v1/userinfo',
    request_token_url=None,
    access_token_method='POST',
    access_token_url='https://accounts.google.com/o/oauth2/token',
    authorize_url='https://accounts.google.com/o/oauth2/auth',
)

# Create the connection to the database
def get_db_connection():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row # Database connections will return rows that 
                                # behave like Python dictionaries
    return conn

@app.route("/login")
def login():
    return google.authorize(callback=url_for('authorized', _external=True))

@app.route('/login/callback')
def authorized():
    response = google.authorized_response()
    if response is None or response.get('access_token') is None:
        return 'Access denied: reason={} error={}'.format(
            request.args['error_reason'],
            request.args['error_description']
        )

    session['google_token'] = (response['access_token'], '')
    user_info = google.get('https://www.googleapis.com/oauth2/v1/userinfo')
    user_email = user_info.data["email"]
    user = User(user_email)
    login_user(user)
    session["user_id"] = user_email
    return render_template("index.html")

@google.tokengetter
def get_google_oauth_token():
    return session.get('google_token')


# Using the app instance to handle incoming requests and send answers
@app.route("/") # decorator -> transforms functions' return value in an HTTP response. This function will respond to the "/" URL requests 
def main():
    conn = get_db_connection()
    tasks = conn.execute("SELECT * FROM tasks").fetchall()
    conn.close()
    return render_template("index.html", tasks=tasks)

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

@app.route("/logintesting")
@login_required
def testing():
    return "You are logged in and it's working"

if __name__ == '__main__':
    app.run()