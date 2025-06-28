from flask_classful import FlaskView
from flask_login import login_required


class V1FlaskView(FlaskView):
    route_prefix = "/api/v1/"
    decorators = [login_required]
