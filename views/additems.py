from flask import Blueprint, render_template, redirect, url_for, request, session, flash
from flask_login import login_required, UserMixin, LoginManager, login_user, logout_user, current_user
from flask_oauthlib.client import OAuth
from models import User, get_db_connection

additems_bp = Blueprint('additems_bp', __name__)

@additems_bp.route("/add", methods=("GET", "POST"))
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





