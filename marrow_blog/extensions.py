from flask_debugtoolbar import DebugToolbarExtension
from flask_flatpages import FlatPages
from flask_login import LoginManager
from flask_marshmallow import Marshmallow
from flask_sqlalchemy import SQLAlchemy
from flask_static_digest import FlaskStaticDigest

debug_toolbar = DebugToolbarExtension()
db = SQLAlchemy()
flask_static_digest = FlaskStaticDigest()
login_manager = LoginManager()
marshmallow = Marshmallow()
flat_pages = FlatPages()
