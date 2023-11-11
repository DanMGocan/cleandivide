#pip install -r requirements.txt

from flask import Blueprint, Flask, render_template, request, url_for, flash, redirect, session, jsonify
from flask_login import login_required, UserMixin, LoginManager, login_user, logout_user, current_user
from views.auth import auth_bp, setup_google, setup_facebook, add_or_get_user
from flask_mail import Mail
from views.additems import additems_bp
from views.helpers import helpers_bp, mail
from views.generator import generator_bp
from views.dashboard import dashboard_bp
from views.profile import profile_bp
from views.admin import admin_bp
from context_processors import get_table_owner_status
import config
import stripe


from models import get_db_connection
from math import floor

import logging 
from logging.handlers import RotatingFileHandler

# Creating the instance of the Flask application with the name app
app = Flask(__name__)
app.config.from_object('config')

# Set up logging
handler = RotatingFileHandler('logger.log', maxBytes=10000, backupCount=1)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
app.logger.addHandler(handler)

# Creates the authentication
setup_google(app)
setup_facebook(app)

# Register the blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(additems_bp)
app.register_blueprint(helpers_bp)
app.register_blueprint(generator_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(profile_bp)
app.register_blueprint(admin_bp)


# Importing mail object
mail.init_app(app)
mail = Mail(app)

# Stripe
stripe_keys = {
    "secret_key": app.config["STRIPE_SECRET_KEY"],
    "publishable_key": app.config["STRIPE_PUBLISHABLE_KEY"],
}
stripe.api_key = stripe_keys["secret_key"]


# At this point only God understands what is happening
# Custom Jinja2 filter to floor a number
def floor(value):
    """Return the floor of the value."""
    import math
    return math.floor(value)
app.jinja_env.filters['floor'] = floor


# Using the app instance to handle incoming requests and send answers
@app.route("/")
def main():
        
    if current_user.is_authenticated:
        return redirect(url_for("dashboard_bp.dashboard"))
    else:
        return render_template('index.html')  # For guests

@app.route("/about")
def about():
    return render_template("about.html")


@app.route('/create-checkout-session', methods=['POST'])
def create_checkout_session():
    YOUR_DOMAIN = request.url_root.rstrip('/')
    try:
        checkout_session = stripe.checkout.Session.create(
            line_items=[
                {
                    # Provide the exact Price ID (for example, pr_1234) of the product you want to sell
                    'price': 'price_1O9W4yGLjjHLFKTU4yf2kqFG',
                    'quantity': 1,
                },
            ],
            mode='payment',
            success_url=YOUR_DOMAIN + '/payment-successful',
            cancel_url=YOUR_DOMAIN + '/payment-unsuccessful',
        )
    except Exception as e:
        return str(e)

    return redirect(checkout_session.url, code=303)

@app.errorhandler(Exception)
def handle_exception(error):
    # You can use error.code here if you want to customize based on error type
    if hasattr(error, 'code'):
        error_code = error.code
    else:
        error_code = 500  # Default to 500 if error code is not set

    print(
            f'''
            "Error code: " {error_code}\n,
            "Error message: " {str(error)}
        ''')
          
    return render_template('error.html', error_code=error_code, error_message=str(error)), error_code


# To have the user status as a home master or member available #
@app.context_processor
def inject_table_owner():
    return get_table_owner_status()

# Check if this is the main module being executed.
if __name__ == "__main__":
    app.run(port=5000, debug=True) 


