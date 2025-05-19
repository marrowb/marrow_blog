from celery import Celery, Task
from flask import Flask
from werkzeug.debug import DebuggedApplication
from werkzeug.middleware.proxy_fix import ProxyFix

from marrow_blog.blueprints.admin.models import AdminUser
from cli.commands.cmd_admin import init_app as init_admin_cli

from marrow_blog.extensions import db, debug_toolbar, flask_static_digest, login_manager
from marrow_blog.blueprints.page import page
from marrow_blog.blueprints.up import up
from marrow_blog.blueprints.admin import admin


def create_celery_app(app=None):
    """
    Create a new Celery app and tie together the Celery config to the app's
    config. Wrap all tasks in the context of the application.

    :param app: Flask app
    :return: Celery app
    """
    app = app or create_app()

    class FlaskTask(Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery = Celery(app.import_name, task_cls=FlaskTask)
    celery.conf.update(app.config.get("CELERY_CONFIG", {}))
    celery.set_default()
    app.extensions["celery"] = celery

    return celery


def create_app(settings_override=None):
    """
    Create a Flask application using the app factory pattern.

    :param settings_override: Override settings
    :return: Flask app
    """
    app = Flask(__name__, static_folder="../public", static_url_path="")

    app.config.from_object("config.settings")

    if settings_override:
        app.config.update(settings_override)

    middleware(app)

    if app.debug:
        app.wsgi_app = DebuggedApplication(app.wsgi_app, evalex=True)

    app.register_blueprint(up)
    app.register_blueprint(page)
    app.register_blueprint(admin)

    extensions(app)
    authentication(app, AdminUser)
    init_admin_cli(app)

    return app


def extensions(app):
    """
    Register 0 or more extensions (mutates the app passed in).

    :param app: Flask application instance
    :return: None
    """
    debug_toolbar.init_app(app)
    db.init_app(app)
    flask_static_digest.init_app(app)
    login_manager.init_app(app)
    return None


def authentication(app, user_model):
    login_manager.login_view = "admin.login"
    login_manager.login_message_category = "info"
    login_manager.login_message = "Please log in to access this page."

    @login_manager.user_loader
    def load_user(uid):
        return user_model.query.get(int(uid))
    return None


def middleware(app):
    """
    Register 0 or more middleware (mutates the app passed in).

    :param app: Flask application instance
    :return: None
    """
    # Enable the Flask interactive debugger in the brower for development.
    if app.debug:
        app.wsgi_app = DebuggedApplication(app.wsgi_app, evalex=True)

    # Set the real IP address into request.remote_addr when behind a proxy.
    app.wsgi_app = ProxyFix(app.wsgi_app)

    return None


celery_app = create_celery_app()
