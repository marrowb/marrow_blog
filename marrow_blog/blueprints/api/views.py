from flask import Blueprint # Removed url_for, request, current_app as not used here
# from flask import current_app # Not used
from flask_login import login_required # Added import

from marrow_blog.extensions import db

api = Blueprint("api", __name__, url_prefix="/api") # Added url_prefix for clarity

@api.before_request
@login_required
def check_access():
    """Protect all of the api endpoints registered under this blueprint."""
    pass

