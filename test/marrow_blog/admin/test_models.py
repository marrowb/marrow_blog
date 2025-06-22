import pytest
from sqlalchemy.exc import IntegrityError
from datetime import datetime
from werkzeug.security import check_password_hash

from marrow_blog.blueprints.admin.models import AdminUser
from marrow_blog.extensions import db
from lib.tests import ViewTestMixin


class TestAdminUserModel(ViewTestMixin):
    """Test basic AdminUser model functionality."""

    def test_admin_user_creation_with_required_fields(self, clean_session):
        """Test creating an admin user with required fields."""
        admin = AdminUser(username="new_admin")
        admin.set_password("test_password")

        assert admin.username == "new_admin"
        assert admin.password_hash is not None
        assert admin.password_hash != "test_password"  # Should be hashed
        assert admin.mfa_secret is None  # Default value

    def test_admin_user_save_method(self, clean_session):
        """Test AdminUser save method commits to database."""
        admin = AdminUser(username="saved_admin")
        admin.set_password("password")

        # Before save, should not be in database
        assert AdminUser.query.filter_by(username="saved_admin").first() is None

        result = admin.save()

        # After save, should be in database
        saved_admin = AdminUser.query.filter_by(username="saved_admin").first()
        assert saved_admin is not None
        assert saved_admin.username == "saved_admin"
        assert result == admin  # save() returns self

    def test_admin_user_delete_method(self, clean_session):
        """Test AdminUser delete method removes from database."""
        admin = AdminUser(username="to_delete")
        admin.set_password("password")
        admin.save()

        # Verify it exists
        assert AdminUser.query.filter_by(username="to_delete").first() is not None

        admin.delete()

        # Verify it's deleted
        assert AdminUser.query.filter_by(username="to_delete").first() is None

    def test_admin_user_repr(self, clean_session):
        """Test AdminUser __repr__ method."""
        admin = AdminUser(username="repr_test")

        repr_str = repr(admin)
        assert "AdminUser" in repr_str
        assert "repr_test" in repr_str

    def test_admin_user_from_fixtures(self, session):
        """Test accessing admin users from session fixtures."""
        # Test basic admin
        admin = AdminUser.query.filter_by(username="test_admin").first()
        assert admin is not None
        assert admin.username == "test_admin"
        assert admin.check_password("password") is True
        assert admin.mfa_secret is None

        # Test MFA admin
        mfa_admin = AdminUser.query.filter_by(username="test_admin_mfa").first()
        assert mfa_admin is not None
        assert mfa_admin.username == "test_admin_mfa"
        assert mfa_admin.mfa_secret == "TESTSECRETABC234"

    def test_admin_user_posts_relationship(self, session):
        """Test AdminUser has posts relationship."""
        admin = AdminUser.query.filter_by(username="test_admin").first()

        # Should have posts collection
        assert hasattr(admin, "posts")
        posts = admin.posts.all()
        assert len(posts) >= 3  # Our fixture posts


class TestAdminUserPassword(ViewTestMixin):
    """Test AdminUser password management."""

    def test_set_password_hashes_password(self, clean_session):
        """Test set_password method hashes passwords properly."""
        admin = AdminUser(username="hash_test")

        admin.set_password("my_password")

        assert admin.password_hash is not None
        assert admin.password_hash != "my_password"
        assert len(admin.password_hash) > 20  # Werkzeug hashes are long

    def test_check_password_validates_correct_password(self, clean_session):
        """Test check_password method validates correct passwords."""
        admin = AdminUser(username="password_test")
        admin.set_password("correct_password")

        assert admin.check_password("correct_password") is True

    def test_check_password_rejects_incorrect_password(self, clean_session):
        """Test check_password method rejects incorrect passwords."""
        admin = AdminUser(username="password_test")
        admin.set_password("correct_password")

        assert admin.check_password("wrong_password") is False
        assert admin.check_password("") is False
        assert admin.check_password("CORRECT_PASSWORD") is False  # Case sensitive

    def test_password_hashing_not_reversible(self, clean_session):
        """Test password hashing is not reversible."""
        admin = AdminUser(username="security_test")
        original_password = "secret123"

        admin.set_password(original_password)

        # Hash should not contain original password
        assert original_password not in admin.password_hash
        assert admin.password_hash != original_password

    def test_multiple_users_same_password_different_hashes(self, clean_session):
        """Test multiple users can have same password with different hashes."""
        admin1 = AdminUser(username="user1")
        admin2 = AdminUser(username="user2")

        same_password = "shared_password"
        admin1.set_password(same_password)
        admin2.set_password(same_password)

        # Both should validate the password
        assert admin1.check_password(same_password) is True
        assert admin2.check_password(same_password) is True

        # But hashes should be different (salt makes them unique)
        assert admin1.password_hash != admin2.password_hash

    def test_password_with_special_characters(self, clean_session):
        """Test passwords with special characters work correctly."""
        admin = AdminUser(username="special_test")
        complex_password = "P@ssw0rd!#$%^&*()_+-=[]{}|;:,.<>?"

        admin.set_password(complex_password)

        assert admin.check_password(complex_password) is True
        assert admin.check_password("P@ssw0rd") is False

    def test_empty_password_handling(self, clean_session):
        """Test handling of empty passwords."""
        admin = AdminUser(username="empty_test")

        # Empty password should still create a hash
        admin.set_password("")
        assert admin.password_hash is not None
        assert admin.check_password("") is True
        assert admin.check_password("anything") is False

    def test_werkzeug_hash_format(self, clean_session):
        """Test that password hash uses Werkzeug format."""
        admin = AdminUser(username="format_test")
        admin.set_password("test123")

        # Werkzeug hashes start with method identifier
        assert admin.password_hash.startswith(("pbkdf2:", "scrypt:", "bcrypt:"))

        # Should be verifiable with Werkzeug directly
        assert check_password_hash(admin.password_hash, "test123") is True


class TestAdminUserMFA(ViewTestMixin):
    """Test AdminUser MFA functionality."""

    def test_is_mfa_enabled_false_when_no_secret(self, clean_session):
        """Test is_mfa_enabled property returns False when mfa_secret is None."""
        admin = AdminUser(username="no_mfa")
        admin.set_password("password")

        assert admin.mfa_secret is None
        assert admin.is_mfa_enabled is False

    def test_is_mfa_enabled_true_when_secret_set(self, clean_session):
        """Test is_mfa_enabled property returns True when mfa_secret is set."""
        admin = AdminUser(username="with_mfa")
        admin.set_password("password")
        admin.mfa_secret = "TESTMFASECRET123456789012"

        assert admin.mfa_secret is not None
        assert admin.is_mfa_enabled is True

    def test_mfa_secret_can_be_set_and_retrieved(self, clean_session):
        """Test MFA secret can be set and retrieved."""
        admin = AdminUser(username="mfa_test")
        admin.set_password("password")

        test_secret = "JBSWY3DPEHPK3PXP"  # Valid base32
        admin.mfa_secret = test_secret

        assert admin.mfa_secret == test_secret

    def test_mfa_secret_optional(self, clean_session):
        """Test MFA secret is optional (can be None)."""
        admin = AdminUser(username="optional_mfa")
        admin.set_password("password")
        admin.save()

        # Should save successfully without MFA secret
        saved_admin = AdminUser.query.filter_by(username="optional_mfa").first()
        assert saved_admin is not None
        assert saved_admin.mfa_secret is None
        assert saved_admin.is_mfa_enabled is False

    def test_mfa_secret_from_fixtures(self, session):
        """Test MFA secret from fixture data."""
        mfa_admin = AdminUser.query.filter_by(username="test_admin_mfa").first()

        assert mfa_admin.mfa_secret == "TESTSECRETABC234"
        assert mfa_admin.is_mfa_enabled is True

    def test_mfa_secret_length_constraint(self, clean_session):
        """Test MFA secret respects length constraints."""
        admin = AdminUser(username="mfa_length")
        admin.set_password("password")

        # Test within limit (32 chars)
        valid_secret = "A" * 32
        admin.mfa_secret = valid_secret
        admin.save()

        saved_admin = AdminUser.query.filter_by(username="mfa_length").first()
        assert saved_admin.mfa_secret == valid_secret


class TestAdminUserAuth(ViewTestMixin):
    """Test AdminUser Flask-Login integration."""

    def test_usermixin_provides_required_methods(self, clean_session):
        """Test UserMixin provides required Flask-Login methods."""
        admin = AdminUser(username="auth_test")
        admin.set_password("password")

        # Should have Flask-Login required methods
        assert hasattr(admin, "get_id")
        assert hasattr(admin, "is_authenticated")
        assert hasattr(admin, "is_active")
        assert hasattr(admin, "is_anonymous")

    def test_get_id_returns_string_id(self, clean_session):
        """Test get_id method returns string ID."""
        admin = AdminUser(username="id_test")
        admin.set_password("password")
        admin.save()

        user_id = admin.get_id()
        assert isinstance(user_id, str)
        assert user_id == str(admin.id)

    def test_is_authenticated_property(self, clean_session):
        """Test is_authenticated property works correctly."""
        admin = AdminUser(username="auth_prop_test")
        admin.set_password("password")

        # UserMixin default behavior
        assert admin.is_authenticated is True

    def test_is_active_property(self, clean_session):
        """Test is_active property works correctly."""
        admin = AdminUser(username="active_test")
        admin.set_password("password")

        # UserMixin default behavior
        assert admin.is_active is True

    def test_is_anonymous_property(self, clean_session):
        """Test is_anonymous property works correctly."""
        admin = AdminUser(username="anon_test")
        admin.set_password("password")

        # UserMixin default behavior
        assert admin.is_anonymous is False

    def test_flask_login_integration_with_fixtures(self, session):
        """Test Flask-Login integration with fixture users."""
        admin = AdminUser.query.filter_by(username="test_admin").first()

        assert admin.is_authenticated is True
        assert admin.is_active is True
        assert admin.is_anonymous is False
        assert admin.get_id() == str(admin.id)


class TestAdminUserConstraints(ViewTestMixin):
    """Test AdminUser database constraints."""

    def test_username_uniqueness_constraint(self, clean_session):
        """Test username must be unique across admin users."""
        # Create first admin
        admin1 = AdminUser(username="unique_user")
        admin1.set_password("password1")
        admin1.save()

        # Try to create second admin with same username
        admin2 = AdminUser(username="unique_user")
        admin2.set_password("password2")

        with pytest.raises(IntegrityError):
            admin2.save()

    def test_username_required_constraint(self, clean_session):
        """Test username is required (not null)."""
        admin = AdminUser()  # No username provided
        admin.set_password("password")

        with pytest.raises(IntegrityError):
            admin.save()

    def test_password_hash_required_constraint(self, clean_session):
        """Test password_hash is required (not null)."""
        admin = AdminUser(username="no_password")
        # Don't set password, so password_hash remains None

        with pytest.raises(IntegrityError):
            admin.save()

    def test_username_length_limits(self, clean_session):
        """Test username respects length constraints."""
        # Test within limit (80 chars)
        valid_username = "a" * 80
        admin = AdminUser(username=valid_username)
        admin.set_password("password")
        admin.save()

        saved_admin = AdminUser.query.filter_by(username=valid_username).first()
        assert saved_admin is not None
        assert len(saved_admin.username) == 80

    def test_case_sensitive_usernames(self, clean_session):
        """Test usernames are case-sensitive."""
        admin1 = AdminUser(username="TestUser")
        admin1.set_password("password")
        admin1.save()

        admin2 = AdminUser(username="testuser")
        admin2.set_password("password")
        admin2.save()

        # Both should exist
        assert AdminUser.query.filter_by(username="TestUser").first() is not None
        assert AdminUser.query.filter_by(username="testuser").first() is not None

    def test_whitespace_in_usernames(self, clean_session):
        """Test usernames can contain whitespace."""
        admin = AdminUser(username="user with spaces")
        admin.set_password("password")
        admin.save()

        saved_admin = AdminUser.query.filter_by(username="user with spaces").first()
        assert saved_admin is not None


class TestAdminUserTimestamps(ViewTestMixin):
    """Test AdminUser ResourceMixin inherited functionality."""

    def test_timestamps_auto_population(self, clean_session):
        """Test created_on and updated_on are automatically set."""
        admin = AdminUser(username="timestamp_test")
        admin.set_password("password")

        # Before save, timestamps should be None
        assert admin.created_on is None
        assert admin.updated_on is None

        admin.save()

        # After save, timestamps should be set
        assert admin.created_on is not None
        assert admin.updated_on is not None
        assert isinstance(admin.created_on, datetime)
        assert isinstance(admin.updated_on, datetime)

    def test_updated_on_changes_on_update(self, clean_session):
        """Test updated_on changes when admin user is modified."""
        admin = AdminUser(username="update_test")
        admin.set_password("password")
        admin.save()

        original_updated = admin.updated_on

        # Modify and save again
        admin.mfa_secret = "NEWSECRET123"
        admin.save()

        assert admin.updated_on > original_updated

    def test_resource_mixin_str_method(self, clean_session):
        """Test inherited __str__ method from ResourceMixin."""
        admin = AdminUser(username="str_test")
        admin.set_password("password")
        admin.save()

        str_repr = str(admin)

        # Should contain class name and field values
        assert "AdminUser" in str_repr
        assert "str_test" in str_repr

    def test_timestamps_are_datetime_objects(self, clean_session):
        """Test timestamps are proper datetime objects."""
        admin = AdminUser(username="datetime_test")
        admin.set_password("password")
        admin.save()

        # Timestamps should be datetime objects
        assert isinstance(admin.created_on, datetime)
        assert isinstance(admin.updated_on, datetime)

        # Should be recent (within last minute)
        now = datetime.now()
        time_diff = (now - admin.created_on.replace(tzinfo=None)).total_seconds()
        assert time_diff < 60  # Should be very recent

    def test_fixture_admin_timestamps(self, session):
        """Test fixture admin users have proper timestamps."""
        admin = AdminUser.query.filter_by(username="test_admin").first()

        assert admin.created_on is not None
        assert admin.updated_on is not None
        assert isinstance(admin.created_on, datetime)
        assert isinstance(admin.updated_on, datetime)

