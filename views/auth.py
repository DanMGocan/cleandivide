from flask import Blueprint, render_template, redirect, url_for, request, session
from flask_login import login_required, UserMixin, LoginManager, login_user, logout_user, current_user
from flask_oauthlib.client import OAuth
from models import User, get_db_connection
from datetime import datetime

facebook = None
google = None
auth_bp = Blueprint('auth_bp', __name__)

def add_or_get_user(user_email, function):
    conn = get_db_connection()
    cursor = conn.cursor()

    if function not in ["login", "flatmate_update"]:
        raise ValueError("Invalid function parameter")

    cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_email,))
    user = cursor.fetchone()

    if user:
        if function == "login":
            cursor.execute("UPDATE users SET times_logged = times_logged + 1 WHERE user_id = ?", (user_email,))
            # Check if this is the first login
            if user['times_logged'] == 0:
                cursor.execute("UPDATE users SET first_login = ? WHERE user_id = ?", (datetime.now(), user_email,))
            
    else:
        # User doesn't exist, add them to 'users' table
        cursor.execute('INSERT INTO users (user_id, first_login, table_owner) VALUES (?, ?, ?)', (user_email, datetime.now(), 0))  # Set first_login at user creation

        # Add the default awards to user #
        cursor.execute('SELECT 1 FROM awards WHERE user_id = ?', (user_email,))
        has_awards = cursor.fetchone()

        if not has_awards:
            # No awards record found for the user, so insert a new record with default values
            cursor.execute('INSERT INTO awards (user_id) VALUES (?)', (user_email,))

        # Check for table participant and owner status
        cursor.execute("SELECT 1 FROM task_table WHERE task_owner = ?", (user_email,))
        table_participant = cursor.fetchone()

        cursor.execute("SELECT 1 FROM task_table WHERE table_owner = ?", (user_email,))
        table_owner = cursor.fetchone()

        if table_participant and not table_owner:
            cursor.execute("UPDATE users SET table_owner = 0 WHERE user_id = ?", (user_email,))

    # Update the last login time
    cursor.execute("UPDATE users SET last_login = ? WHERE user_id = ?", (datetime.now(), user_email))

    conn.commit()

    # Fetch the updated user
    cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_email,))
    user = cursor.fetchone()

    conn.close()
    return user

# To be deleted in production, maybe #
def give_premium(user_email):
    if user_email == "gocandan@gmail.com":
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET premium_user = ? WHERE user_id = ?", (1, user_email))
        conn.close()
    else:
        pass

def setup_google(app):
    global google
    from flask_oauthlib.client import OAuth
    oauth = OAuth(app)
    google = oauth.remote_app(
    'google',
    consumer_key=app.config["CONSUMER_KEY"],
    consumer_secret=app.config["CONSUMER_SECRET"],
    request_token_params={
        'scope': 'email',
    },
    base_url='https://www.googleapis.com/oauth2/v1/userinfo',
    request_token_url=None,
    access_token_method='POST',
    access_token_url='https://accounts.google.com/o/oauth2/token',
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    )
    
    @google.tokengetter
    def get_google_oauth_token():
        return session.get('google_token')

    login_manager = LoginManager()
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        if "user_id" in session:
            return User(session["user_id"])
        return None

@auth_bp.route("/login")
def login():
    return google.authorize(callback=url_for('auth_bp.authorized', _external=True, _scheme="https"))

@auth_bp.route("/logout")
def logout():
    logout_user()  
    return redirect(url_for('main', _external=True))
    # return redirect('https://www.google.com/accounts/Logout?continue=https://appengine.google.com/_ah/logout?continue=' + url_for('main', _external=True))

@auth_bp.route('/login/callback')
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
    if user_email in ["gocandan@gmail.com"]:
        session["is_admin"] = True
    user = User(user_email)
    login_user(user)
    session["user_id"] = user_email
    add_or_get_user(user_email, "login")
    give_premium(user_email)
    return redirect(url_for("main"))

def setup_facebook(app):
    global facebook
    oauth = OAuth(app)
    facebook = oauth.remote_app(
        'facebook',
        consumer_key=app.config["FACEBOOK_APP_ID"],  # Facebook App ID
        consumer_secret=app.config["FACEBOOK_APP_SECRET"],  # Facebook App Secret
        request_token_params={
            'scope': 'email',
        },
        base_url='https://graph.facebook.com/v11.0/',  # Make sure the version (v11.0) is current
        request_token_url=None,
        access_token_method='GET',
        access_token_url='https://graph.facebook.com/v11.0/oauth/access_token',
        authorize_url='https://www.facebook.com/v11.0/dialog/oauth',
    )

    @facebook.tokengetter
    def get_facebook_oauth_token():
        return session.get('facebook_token')

    login_manager = LoginManager()
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        if "user_id" in session:
            return User(session["user_id"])
        return None

@auth_bp.route("/login/facebook")
def login_facebook():
    return facebook.authorize(callback=url_for('auth_bp.authorized_facebook', _external=True, _scheme='https'))

@auth_bp.route("/logout/facebook")
def logout_facebook():
    logout_user()  
    return redirect(url_for('main', _external=True))

@auth_bp.route('/login/facebook/callback')
def authorized_facebook():
    response = facebook.authorized_response()
    if response is None or response.get('access_token') is None:
        return 'Access denied: reason={} error={}'.format(
            request.args['error_reason'],
            request.args['error_description']
        )

    session['facebook_token'] = (response['access_token'], '')
    user_info = facebook.get('/me?fields=id,email')  # Get user ID and email
    user_email = user_info.data["email"]
    if user_email in ["gocandan@gmail.com"]:
        session["is_admin"] = True
    user = User(user_email)
    login_user(user)
    session["user_id"] = user_email
    add_or_get_user(user_email, "login")
    give_premium(user_email)
    return redirect(url_for("main"))