import os

from distutils.util import strtobool

SECRET_KEY = os.environ["SECRET_KEY"]
DEBUG = bool(strtobool(os.getenv("FLASK_DEBUG", "false")))
WERKZEUG_DEBUG_PIN = "off"

SERVER_NAME = os.getenv(
    "SERVER_NAME", "localhost:{0}".format(os.getenv("PORT", "8000"))
)
# SQLAlchemy.
SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:////app/data/marrow_blog.db")
SQLALCHEMY_TRACK_MODIFICATIONS = False


# Celery.
CELERY_CONFIG = {
    "broker_url": os.getenv("CELERY_BROKER_URL", "sqla+sqlite:///data/celery-broker.db"),
    "result_backend": os.getenv("CELERY_RESULT_BACKEND", "db+sqlite:///data/celery-results.db"),
    "include": [],
}
