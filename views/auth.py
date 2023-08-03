from flask import Blueprint, render_template, redirect, url_for, request, session
from flask_login import login_required, UserMixin, LoginManager, login_user, logout_user, current_user
from flask_oauthlib.client import OAuth
from models import User

google = None
auth_bp = Blueprint('auth_bp', __name__)

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
    return google.authorize(callback=url_for('auth_bp.authorized', _external=True))

@auth_bp.route("/logout")
def logout():
    logout_user()  
    return redirect('https://www.google.com/accounts/Logout?continue=https://appengine.google.com/_ah/logout?continue=' + url_for('main', _external=True))

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
    return render_template("dashboard.html", user_email=user_email)





