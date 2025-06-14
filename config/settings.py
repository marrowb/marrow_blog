import os

from distutils.util import strtobool

ROOT_DIR = os.path.realpath(os.path.join(os.path.dirname(__file__), ".."))

SECRET_KEY = os.environ["SECRET_KEY"]
DEBUG = bool(strtobool(os.getenv("FLASK_DEBUG", "false")))
WERKZEUG_DEBUG_PIN = "off"
# WERKZEUG_DEBUG_PIN = os.environ["WERKZEUG_DEBUG_PIN"]

SERVER_NAME = os.getenv(
    "SERVER_NAME", "localhost:{0}".format(os.getenv("PORT", "8000"))
)
# SQLAlchemy.
SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:////app/data/marrow_blog.db")
SQLALCHEMY_TRACK_MODIFICATIONS = False

# DOC_UPLOAD_ALLOWED_EXTENSIONS = [".docx", ".txt", ".md"]
DOC_UPLOAD_ALLOWED_EXTENSIONS = {".md"}

# Celery.
CELERY_CONFIG = {
    "broker_url": os.getenv("CELERY_BROKER_URL", "sqla+sqlite:///data/celery-broker.db"),
    "result_backend": os.getenv("CELERY_RESULT_BACKEND", "db+sqlite:///data/celery-results.db"),
    "include": [],
}

FLATPAGES_AUTO_RELOAD = True
FLATPAGES_EXTENSION =  '.md'
FLATPAGES_ROOT = ROOT_DIR
FLATPAGES_MARKDOWN_EXTENSIONS = [
    'markdown.extensions.tables',           # For tables
    'markdown.extensions.fenced_code',      # For code blocks
    'markdown.extensions.footnotes',      # For code blocks
    'markdown.extensions.codehilite',       # For syntax highlighting
    'markdown.extensions.toc',              # For table of contents
    'markdown.extensions.attr_list',        # For attributes
]
FLATPAGES_EXTENSION_CONFIGS = {
    'codehilite': {
        'css_class': 'highlight',
        'linenums': False,
        'guess_lang': False
    },
    'pymdownx.highlight': {
        'use_pygments': True,
        'css_class': 'highlight',
        'linenums': False,
        'guess_lang': False
    }
}
