import pytest

from config import settings
from marrow_blog.app import create_app
from marrow_blog.extensions import db as _db


@pytest.fixture(scope="session")
def app():
    """
    Setup our flask test app, this only gets executed once.

    :return: Flask app
    """
    db_uri = settings.SQLALCHEMY_DATABASE_URI

    if "?" in db_uri:
        db_uri = db_uri.replace("?", "_test?")
    else:
        db_uri = f"{db_uri}_test"

    params = {
        "DEBUG": False,
        "TESTING": True,
        "WTF_CSRF_ENABLED": False,
        "SQLALCHEMY_DATABASE_URI": db_uri,
    }

    _app = create_app(settings_override=params)

    # Establish an application context before running the tests.
    ctx = _app.app_context()
    ctx.push()

    yield _app

    ctx.pop()


@pytest.fixture(scope="function")
def client(app):
    """
    Setup an app client, this gets executed for each test function.

    :param app: Pytest fixture
    :return: Flask app client
    """
    # Create test client with fresh session
    client = app.test_client()
    
    # Ensure no authentication state persists between tests
    with client.session_transaction() as sess:
        sess.clear()
    
    yield client


@pytest.fixture(scope="session")
def db(app):
    """
    Setup our database, this only gets executed once per session.

    :param app: Pytest fixture
    :return: SQLAlchemy database session
    """
    _db.drop_all()
    _db.create_all()

    # Create admin users for various test scenarios
    from marrow_blog.blueprints.admin.models import AdminUser
    admin_users = [
        {"username": "test_admin", "password": "password"},
        {"username": "test_admin_mfa", "password": "password", "mfa_secret": "TESTSECRETABC234"},
        {"username": "test_editor", "password": "password"},
    ]
    
    for admin_data in admin_users:
        admin = AdminUser(username=admin_data["username"])
        admin.set_password(admin_data["password"])
        if "mfa_secret" in admin_data:
            admin.mfa_secret = admin_data["mfa_secret"]
        admin.save()

    # Create test posts for various scenarios
    from marrow_blog.blueprints.posts.models import Post
    
    # Get the first admin user to assign as author
    admin = AdminUser.query.first()
    
    test_posts = [
        {
            "title": "Test Post 1",
            "slug": "test-post-1", 
            "markdown_content": "# Test Content\n\nThis is a test post.",
            "excerpt": "Test excerpt",
            "published": True,
            "author_id": admin.id
        },
        {
            "title": "Draft Post",
            "slug": "draft-post",
            "markdown_content": "# Draft Content\n\nThis is a draft post.",
            "excerpt": "Draft excerpt",
            "published": False,
            "author_id": admin.id
        },
        {
            "title": "Tagged Post",
            "slug": "tagged-post",
            "markdown_content": "# Tagged Content\n\nThis post has tags.",
            "excerpt": "Tagged excerpt", 
            "tags": "test,blog",
            "published": True,
            "author_id": admin.id
        },
    ]
    
    for post_data in test_posts:
        post = Post(**post_data)
        post.save()

    _db.session.commit()
    return _db


@pytest.fixture(scope="function")
def session(db):
    """
    Allow very fast tests by using rollbacks and nested sessions. This does
    require that your database supports SQL savepoints, and Postgres does.

    Read more about this at:
    http://stackoverflow.com/a/26624146

    :param db: Pytest fixture
    :return: None
    """
    db.session.begin_nested()

    yield db.session

    db.session.rollback()


@pytest.fixture(scope="function")
def clean_session(session):
    """
    Clean rollback for each test - preserves session data, rolls back changes.
    
    :param session: Pytest fixture
    :return: SQLAlchemy session
    """
    session.begin_nested()
    yield session
    session.rollback()
