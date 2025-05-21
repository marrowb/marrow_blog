from flask_classful import FlaskView

class V1FlaskView(FlaskView):
    route_prefix = '/api/v1/'
    # decorators = [login_required] # Example, if all V1 views are protected
