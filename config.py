# Do not forget to convert these to environment variables! 
# For example, in production, you'd want to replace 'your_email@example.com' and 'your_password' 
# with os.environ.get('MAIL_USERNAME') and os.environ.get('MAIL_PASSWORD') respectively, and then 
# set these environment variables in your production environment.

import os

SECRET_KEY = os.urandom(24)
# Google #
CONSUMER_KEY = '236830913630-ek9uioi8bbo97akshfoe9tk17kf5h6dd.apps.googleusercontent.com'
CONSUMER_SECRET = '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'

# Facebook #
FACEBOOK_APP_ID = "1022681442309327"
FACEBOOK_APP_SECRET = "cc6cbdf64fc6f954f67764181d0baf1e"

# Flask-Mail Configuration
MAIL_SERVER = 'smtp.gmail.com'
MAIL_PORT = 465
MAIL_USERNAME = 'dividendust@gmail.com'
MAIL_PASSWORD = 'zhix qbpo nfld vrpu' #Hann!bal202'
MAIL_USE_TLS = False
MAIL_USE_SSL = True

# Stripe 
STRIPE_PUBLISHABLE_KEY = 'pk_test_51GtxGZGLjjHLFKTUoCg8D1iwyAaftnINtHsJrwLIBecVm1RXgrZ3LutAWJuI9xz4jJimV8A6tgweunByV3D9rtWK00Y4IpDBzb'
STRIPE_SECRET_KEY = 'sk_test_51GtxGZGLjjHLFKTUqPFK79wnrvsW0MPhRbjMrcATk2INoUPs6MoCg2VmP5M078BgYiXyjUovoChncpj98ZiSuw2100wmlcbV2d'

# MAIL_SERVER ='sandbox.smtp.mailtrap.io'
# MAIL_PORT = 2525
# MAIL_USERNAME = 'd8a9b3a337b001'
# MAIL_PASSWORD = '5cb90ff0e48ccb'
# MAIL_USE_TLS = True
# MAIL_USE_SSL = False
