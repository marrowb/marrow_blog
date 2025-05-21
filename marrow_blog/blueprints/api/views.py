from flask import Blueprint, url_for, request
from flask import current_app

from marrow_blog.extensions import db

api = Blueprint("api", __name__)

@api.before_request
@login_required
def check_access():
    """Protect all of the api endpoints."""
    pass

