#pip install -r requirements.txt

from flask import Blueprint, Flask, render_template, request, url_for, flash, redirect, session
from flask_login import login_required, UserMixin, LoginManager, login_user, logout_user, current_user
from views.auth import auth_bp, setup_google, add_or_get_user
from views.additems import additems_bp

# Creating the instance of the Flask application with the name app
app = Flask(__name__)
app.config.from_object('config')

# Creates the authentication
setup_google(app)
app.register_blueprint(auth_bp)
app.register_blueprint(additems_bp)

# Using the app instance to handle incoming requests and send answers
@app.route("/") # decorator -> transforms functions' return value in an HTTP response. This function will respond to the "/" URL requests 
def main():
    # conn = get_db_connection()
    # tasks = conn.execute("SELECT * FROM tasks").fetchall()
    # conn.close()
    
    user_email = session.get('user_id')
    if current_user.is_authenticated:
        return render_template('dashboard.html', user_email = user_email) # For logged-in users
    else:
        return render_template('index.html') # For guests

@app.route("/about")
def about():
    return render_template("about.html")





if __name__ == '__main__':
    app.run()