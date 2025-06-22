import pytest
from flask import url_for


def assert_status_with_message(status_code=200, response=None, message=None):
    """
    Check to see if a message is contained within a response.

    :param status_code: Status code that defaults to 200
    :type status_code: int
    :param response: Flask response
    :type response: str
    :param message: String to check for
    :type message: str
    :return: None
    """
    assert response.status_code == status_code
    assert message in str(response.data)


class ViewTestMixin(object):
    """
    Automatically load in a session and client, this is common for a lot of
    tests that work with views.
    """

    @pytest.fixture(autouse=True)
    def set_common_fixtures(self, session, client):
        self.session = session
        self.client = client
        
        # Ensure each test starts with no authenticated user
        self._ensure_logged_out()
    
    def _ensure_logged_out(self):
        """
        Ensure no user is logged in by attempting logout.
        This handles both regular users and admin users.
        """
        try:
            # Try to logout admin user (most common in admin tests)
            self.client.get("/logout", follow_redirects=False)
        except:
            # If admin logout fails, try regular user logout
            try:
                self.client.get("/user/logout", follow_redirects=False) 
            except:
                # If both fail, clear session manually
                pass
        
        # Clear session state to ensure clean start
        with self.client.session_transaction() as sess:
            sess.clear()

    def login(
        self, identity="solo_practicioner@email.com", password="password"
    ):
        """
        Login a specific user.

        :return: Flask response
        """
        return login(self.client, identity, password)

    def logout(self):
        """
        Logout a specific user.

        :return: Flask response
        """
        return logout(self.client)

    def login_admin(self, username="test_admin", password="password"):
        """
        Login a specific admin user.

        :param username: The admin username
        :type username: str
        :param password: The admin password
        :type password: str
        :return: Flask response
        """
        return login_admin(self.client, username, password)

    def logout_admin(self):
        """
        Logout a specific admin user.

        :return: Flask response
        """
        return logout_admin(self.client)


def login(client, username="", password=""):
    """
    Log a specific user in.

    :param client: Flask client
    :param username: The username
    :type username: str
    :param password: The password
    :type password: str
    :return: Flask response
    """
    user = dict(identity=username, password=password)

    response = client.post(
        url_for("user.login"), data=user, follow_redirects=True
    )

    return response


def logout(client):
    """
    Log a specific user out.

    :param client: Flask client
    :return: Flask response
    """
    return client.get(url_for("user.logout"), follow_redirects=True)


def login_admin(client, username="test_admin", password="password"):
    """
    Log a specific admin user in.

    :param client: Flask client
    :param username: The admin username
    :type username: str
    :param password: The admin password
    :type password: str
    :return: Flask response
    """
    user = dict(username=username, password=password)

    response = client.post(
        url_for("admin.login"), data=user, follow_redirects=True
    )

    return response


def logout_admin(client):
    """
    Log a specific admin user out.

    :param client: Flask client
    :return: Flask response
    """
    return client.get(url_for("admin.logout"), follow_redirects=True)
