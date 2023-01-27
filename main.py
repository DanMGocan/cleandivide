import sqlite3
import os
from flask import Flask, render_template, request, url_for, flash, redirect
from werkzeug.exceptions import abort

# Creating the instance of the Flask application with the name app
app = Flask(__name__)
app.config["SECRET KEY"] = os.urandom(24)

# Create the connection to the database
def get_db_connection():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row # Database connections will return rows that 
                                # behave like Python dictionaries
    return conn

def get_post(post_id):
    conn = get_db_connection()
    post = conn.execute("SELECT * FROM tasks WHERE id=?", (post_id,)).fetchone() # Watch the comma!
    conn.close()

    if post is None:
        abort(404)
    return post

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

@app.route("/<int:post_id>")
def post(post_id):
    post = get_post(post_id)
    return render_template("task.html", post=post)

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
