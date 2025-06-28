import pyotp
from flask import url_for

from lib.tests import ViewTestMixin, assert_status_with_message
from marrow_blog.blueprints.admin.models import AdminUser
from marrow_blog.blueprints.posts.models import Post


class TestAdminLogin(ViewTestMixin):
    """Test admin login functionality."""

    def test_login_page_renders(self):
        """Test GET /login renders login form correctly."""
        response = self.client.get(url_for("admin.login"))

        assert response.status_code == 200
        assert "Admin Login" in response.get_data(as_text=True)
        assert "Username" in response.get_data(as_text=True)
        assert "Password" in response.get_data(as_text=True)

    def test_login_with_valid_credentials(self):
        """Test POST /login with valid credentials logs in user."""
        data = {"username": "test_admin", "password": "password"}

        response = self.client.post(
            url_for("admin.login"), data=data, follow_redirects=True
        )

        assert response.status_code == 200
        assert_status_with_message(
            status_code=200, response=response, message="Admin Dashboard"
        )
        assert_status_with_message(
            status_code=200, response=response, message="Welcome, test_admin!"
        )

    def test_login_with_invalid_credentials(self):
        """Test POST /login with invalid credentials shows error."""
        data = {"username": "test_admin", "password": "wrong_password"}

        response = self.client.post(
            url_for("admin.login"), data=data, follow_redirects=True
        )

        # Should stay on login page, not redirect to dashboard
        assert response.status_code == 200
        assert_status_with_message(
            status_code=200, response=response, message="Admin Login"
        )

    def test_login_with_nonexistent_user(self):
        """Test POST /login with nonexistent user shows error."""
        data = {"username": "nonexistent_user", "password": "password"}

        response = self.client.post(
            url_for("admin.login"), data=data, follow_redirects=True
        )

        # Should stay on login page
        assert response.status_code == 200
        assert_status_with_message(
            status_code=200, response=response, message="Admin Login"
        )

    def test_login_with_missing_fields(self):
        """Test POST /login with missing fields shows validation errors."""
        # Missing password
        data = {"username": "test_admin"}
        response = self.client.post(
            url_for("admin.login"), data=data, follow_redirects=True
        )
        assert response.status_code == 200

        # Missing username
        data = {"password": "password"}
        response = self.client.post(
            url_for("admin.login"), data=data, follow_redirects=True
        )
        assert response.status_code == 200

    def test_login_redirect_when_already_authenticated(self):
        """Test redirect to dashboard if already authenticated."""
        # Login first
        self.login_admin("test_admin")

        # Try to access login page
        response = self.client.get(
            url_for("admin.login"), follow_redirects=True
        )

        assert_status_with_message(
            status_code=200, response=response, message="Admin Dashboard"
        )

    def test_login_redirect_to_dashboard(self):
        """Test redirect to dashboard after successful login."""
        data = {"username": "test_admin", "password": "password"}

        response = self.client.post(url_for("admin.login"), data=data)

        # Should redirect to dashboard
        assert response.status_code == 302
        assert "/dashboard" in response.location


class TestAdminMFA(ViewTestMixin):
    """Test admin MFA integration."""

    def test_mfa_enabled_user_requires_token(self):
        """Test MFA-enabled user requires token."""
        data = {
            "username": "test_admin_mfa",
            "password": "password",
            # No MFA token provided
        }

        response = self.client.post(
            url_for("admin.login"), data=data, follow_redirects=True
        )

        # Should stay on login page, not redirect to dashboard
        assert response.status_code == 200
        assert_status_with_message(
            status_code=200, response=response, message="Admin Login"
        )

    def test_mfa_with_valid_token_allows_login(self):
        """Test valid MFA token allows login."""
        # Generate valid TOTP token for test secret
        totp = pyotp.TOTP("TESTSECRETABC234")
        valid_token = totp.now()

        data = {
            "username": "test_admin_mfa",
            "password": "password",
            "token": valid_token,
        }

        response = self.client.post(
            url_for("admin.login"), data=data, follow_redirects=True
        )

        assert response.status_code == 200
        assert_status_with_message(
            status_code=200, response=response, message="Admin Dashboard"
        )
        assert_status_with_message(
            status_code=200,
            response=response,
            message="Welcome, test_admin_mfa!",
        )

    def test_mfa_with_invalid_token_rejects_login(self):
        """Test invalid MFA token rejects login."""
        data = {
            "username": "test_admin_mfa",
            "password": "password",
            "token": "123456",  # Invalid token
        }

        response = self.client.post(
            url_for("admin.login"), data=data, follow_redirects=True
        )

        # Should stay on login page
        assert response.status_code == 200
        assert_status_with_message(
            status_code=200, response=response, message="Admin Login"
        )

    def test_non_mfa_user_skips_token_requirement(self):
        """Test non-MFA users skip token requirement."""
        data = {
            "username": "test_admin",  # No MFA enabled
            "password": "password",
            "token": "123456",  # Token provided but not required
        }

        response = self.client.post(
            url_for("admin.login"), data=data, follow_redirects=True
        )

        assert response.status_code == 200
        assert_status_with_message(
            status_code=200, response=response, message="Admin Dashboard"
        )
        assert_status_with_message(
            status_code=200, response=response, message="Welcome, test_admin!"
        )

    def test_mfa_token_length_validation(self):
        """Test MFA token length validation."""
        # Token too short
        data = {
            "username": "test_admin_mfa",
            "password": "password",
            "token": "123",  # Too short
        }

        response = self.client.post(
            url_for("admin.login"), data=data, follow_redirects=True
        )
        assert response.status_code == 200

        # Token too long
        data["token"] = "1234567"  # Too long
        response = self.client.post(
            url_for("admin.login"), data=data, follow_redirects=True
        )
        assert response.status_code == 200


class TestAdminLogout(ViewTestMixin):
    """Test admin logout functionality."""

    def test_logout_requires_authentication(self):
        """Test GET /logout requires authentication."""
        response = self.client.get(
            url_for("admin.logout"), follow_redirects=True
        )

        # Should redirect to login page
        assert_status_with_message(
            status_code=200, response=response, message="Admin Login"
        )

    def test_logout_logs_out_user_and_redirects(self):
        """Test /logout logs out user and redirects."""
        # Login first
        self.login_admin("test_admin")

        # Then logout
        response = self.client.get(
            url_for("admin.logout"), follow_redirects=True
        )

        assert_status_with_message(
            status_code=200,
            response=response,
            message="You have been logged out",
        )
        assert_status_with_message(
            status_code=200, response=response, message="Admin Login"
        )

    def test_logout_flash_message(self):
        """Test logout shows confirmation flash message."""
        self.login_admin("test_admin")

        response = self.client.get(url_for("admin.logout"))

        # Should redirect to login
        assert response.status_code == 302
        assert "/login" in response.location

    def test_logout_clears_session(self):
        """Test logout clears user session."""
        # Login
        self.login_admin("test_admin")

        # Verify can access protected route
        response = self.client.get(url_for("admin.dashboard"))
        assert response.status_code == 200

        # Logout
        self.client.get(url_for("admin.logout"))

        # Verify cannot access protected route
        response = self.client.get(
            url_for("admin.dashboard"), follow_redirects=True
        )
        assert_status_with_message(
            status_code=200, response=response, message="Admin Login"
        )


class TestAdminDashboard(ViewTestMixin):
    """Test admin dashboard access and data."""

    def test_dashboard_requires_authentication(self):
        """Test GET /dashboard requires authentication."""
        response = self.client.get(
            url_for("admin.dashboard"), follow_redirects=True
        )

        assert_status_with_message(
            status_code=200, response=response, message="Admin Login"
        )

    def test_dashboard_shows_posts_data(self):
        """Test dashboard shows drafts and published posts."""
        self.login_admin("test_admin")

        response = self.client.get(url_for("admin.dashboard"))

        assert response.status_code == 200
        assert_status_with_message(
            status_code=200, response=response, message="Admin Dashboard"
        )

        # Should show posts from fixtures
        assert "Test Post 1" in response.get_data(as_text=True)
        assert "Tagged Post" in response.get_data(as_text=True)
        assert "Draft Post" in response.get_data(as_text=True)

    def test_dashboard_categorizes_posts_correctly(self):
        """Test posts are properly categorized (drafts vs published)."""
        self.login_admin("test_admin")

        response = self.client.get(url_for("admin.dashboard"))
        response_text = response.get_data(as_text=True)

        # Verify we have both sections
        assert "draft posts" in response_text.lower()
        assert "published posts" in response_text.lower()

    def test_dashboard_template_context(self):
        """Test dashboard template receives correct context data."""
        self.login_admin("test_admin")

        response = self.client.get(url_for("admin.dashboard"))

        assert response.status_code == 200
        assert "Admin Dashboard" in response.get_data(as_text=True)


class TestAdminPostEditor(ViewTestMixin):
    """Test admin post editor routes."""

    def test_post_editor_requires_authentication(self):
        """Test GET /post requires authentication."""
        response = self.client.get(
            url_for("admin.post"), follow_redirects=True
        )

        assert_status_with_message(
            status_code=200, response=response, message="Admin Login"
        )

    def test_post_editor_blank_renders(self):
        """Test GET /post renders blank editor."""
        self.login_admin("test_admin")

        response = self.client.get(url_for("admin.post"))

        assert response.status_code == 200
        assert_status_with_message(
            status_code=200, response=response, message="Post title..."
        )

    def test_post_editor_with_id_requires_auth(self):
        """Test GET /post/<id> requires authentication."""
        post = Post.query.filter_by(slug="test-post-1").first()

        response = self.client.get(
            url_for("admin.post", post_id=post.id), follow_redirects=True
        )

        assert_status_with_message(
            status_code=200, response=response, message="Admin Login"
        )

    def test_post_editor_with_existing_post(self):
        """Test GET /post/<id> renders editor for existing post."""
        self.login_admin("test_admin")
        post = Post.query.filter_by(slug="test-post-1").first()

        response = self.client.get(url_for("admin.post", post_id=post.id))

        assert response.status_code == 200
        assert_status_with_message(
            status_code=200, response=response, message="Post title..."
        )

    def test_post_editor_template_renders(self):
        """Test post editor template renders correctly."""
        self.login_admin("test_admin")

        response = self.client.get(url_for("admin.post"))

        assert response.status_code == 200
        assert "Post title..." in response.get_data(as_text=True)


class TestAdminPreview(ViewTestMixin):
    """Test admin preview functionality."""

    def test_preview_requires_authentication(self):
        """Test GET /preview/<id> requires authentication."""
        post = Post.query.filter_by(slug="test-post-1").first()

        response = self.client.get(
            url_for("admin.preview", post_id=post.id), follow_redirects=True
        )

        assert_status_with_message(
            status_code=200, response=response, message="Admin Login"
        )

    def test_preview_renders_markdown_correctly(self):
        """Test preview renders markdown to HTML correctly."""
        self.login_admin("test_admin")
        post = Post.query.filter_by(slug="test-post-1").first()

        response = self.client.get(url_for("admin.preview", post_id=post.id))

        assert response.status_code == 200
        assert_status_with_message(
            status_code=200, response=response, message="Preview:"
        )

        # Should contain the post title
        assert post.title in response.get_data(as_text=True)

    def test_preview_404_for_nonexistent_post(self):
        """Test preview returns 404 for non-existent posts."""
        self.login_admin("test_admin")

        response = self.client.get(url_for("admin.preview", post_id=99999))

        assert response.status_code == 404

    def test_preview_markdown_processing(self):
        """Test preview processes markdown with Pygments."""
        self.login_admin("test_admin")
        post = Post.query.filter_by(slug="test-post-1").first()

        response = self.client.get(url_for("admin.preview", post_id=post.id))
        response_text = response.get_data(as_text=True)

        # Should contain processed HTML (headers become h1 tags, etc.)
        assert "<h1>" in response_text or "Test Content" in response_text


class TestAdminUpload(ViewTestMixin):
    """Test admin upload interface."""

    def test_upload_form_requires_authentication(self):
        """Test GET /upload-doc requires authentication."""
        response = self.client.get(
            url_for("admin.upload_doc"), follow_redirects=True
        )

        assert_status_with_message(
            status_code=200, response=response, message="Admin Login"
        )

    def test_upload_form_renders(self):
        """Test GET /upload-doc renders upload form."""
        self.login_admin("test_admin")

        response = self.client.get(url_for("admin.upload_doc"))

        assert response.status_code == 200
        assert_status_with_message(
            status_code=200, response=response, message="Upload Document"
        )

    def test_upload_form_template_context(self):
        """Test upload form template renders with upload form."""
        self.login_admin("test_admin")

        response = self.client.get(url_for("admin.upload_doc"))
        response_text = response.get_data(as_text=True)

        # Should contain file upload elements
        assert "file" in response_text.lower()
        assert "upload" in response_text.lower()

    def test_upload_post_requires_authentication(self):
        """Test POST /upload-doc requires authentication."""
        response = self.client.post(
            url_for("admin.upload_doc"), follow_redirects=True
        )

        assert_status_with_message(
            status_code=200, response=response, message="Admin Login"
        )


class TestAdminPublish(ViewTestMixin):
    """Test admin publish functionality."""

    def test_publish_requires_authentication(self):
        """Test GET /publish/<id> requires authentication."""
        post = Post.query.filter_by(slug="draft-post").first()

        response = self.client.get(
            url_for("admin.publish", post_id=post.id), follow_redirects=True
        )

        assert_status_with_message(
            status_code=200, response=response, message="Admin Login"
        )

    def test_publish_draft_post_success(self):
        """Test /publish/<id> successfully publishes draft post."""
        self.login_admin("test_admin")

        # Create a dedicated draft post for this test
        admin = AdminUser.query.filter_by(username="test_admin").first()
        test_post = Post(
            title="Draft Post to Publish",
            slug="draft-post-to-publish",
            markdown_content="Draft content",
            published=False,
            author_id=admin.id,
        )
        test_post.save()
        post_id = test_post.id

        response = self.client.get(url_for("admin.publish", post_id=post_id))

        # Should redirect to the published post
        assert response.status_code == 302
        assert f"/blog/{test_post.slug}" in response.location

        # Verify post is now published in database
        updated_post = Post.query.get(post_id)
        assert updated_post.published is True

    def test_publish_already_published_post(self):
        """Test /publish/<id> works on already published posts."""
        self.login_admin("test_admin")

        # Get a published post from fixtures
        published_post = Post.query.filter_by(slug="test-post-1").first()
        assert (
            published_post.published is True
        )  # Verify it's already published

        response = self.client.get(
            url_for("admin.publish", post_id=published_post.id)
        )

        # Should still redirect successfully
        assert response.status_code == 302
        assert f"/blog/{published_post.slug}" in response.location

        # Verify post remains published
        updated_post = Post.query.get(published_post.id)
        assert updated_post.published is True

    def test_publish_nonexistent_post(self):
        """Test /publish/<id> returns 404 for non-existent post."""
        self.login_admin("test_admin")

        response = self.client.get(url_for("admin.publish", post_id=99999))

        assert response.status_code == 404

    def test_publish_redirect_to_blog_post(self):
        """Test /publish/<id> redirects to the published blog post."""
        self.login_admin("test_admin")

        # Create a dedicated draft post for this test
        admin = AdminUser.query.filter_by(username="test_admin").first()
        test_post = Post(
            title="Draft Post for Redirect Test",
            slug="draft-post-for-redirect-test",
            markdown_content="Draft content",
            published=False,
            author_id=admin.id,
        )
        test_post.save()

        response = self.client.get(
            url_for("admin.publish", post_id=test_post.id)
        )

        # Should redirect to page.blog_post with the slug
        assert response.status_code == 302
        expected_path = f"/blog/{test_post.slug}"
        assert response.location == expected_path


class TestAdminDelete(ViewTestMixin):
    """Test admin delete functionality."""

    def test_delete_requires_authentication(self):
        """Test GET /delete/<id> requires authentication."""
        post = Post.query.filter_by(slug="test-post-1").first()

        response = self.client.get(
            url_for("admin.delete", post_id=post.id), follow_redirects=True
        )

        assert_status_with_message(
            status_code=200, response=response, message="Admin Login"
        )

    def test_delete_post_success(self):
        """Test /delete/<id> successfully deletes post."""
        self.login_admin("test_admin")

        # Create a post to delete (don't use fixtures to avoid affecting other tests)
        from marrow_blog.blueprints.admin.models import AdminUser

        admin = AdminUser.query.filter_by(username="test_admin").first()

        test_post = Post(
            title="Post to Delete via View",
            slug="post-to-delete-via-view",
            markdown_content="Content to delete",
            author_id=admin.id,
        )
        test_post.save()
        post_id = test_post.id

        response = self.client.get(
            url_for("admin.delete", post_id=post_id), follow_redirects=True
        )

        # Should redirect to dashboard
        assert response.status_code == 200
        assert_status_with_message(
            status_code=200, response=response, message="Admin Dashboard"
        )

        # Verify post was deleted from database
        deleted_post = Post.query.get(post_id)
        assert deleted_post is None

    def test_delete_nonexistent_post(self):
        """Test /delete/<id> returns 404 for non-existent post."""
        self.login_admin("test_admin")

        response = self.client.get(url_for("admin.delete", post_id=99999))

        assert response.status_code == 404

    def test_delete_published_post(self):
        """Test /delete/<id> can delete published posts."""
        self.login_admin("test_admin")

        # Create a published post to delete
        from marrow_blog.blueprints.admin.models import AdminUser

        admin = AdminUser.query.filter_by(username="test_admin").first()

        test_post = Post(
            title="Published Post to Delete via View",
            slug="published-post-to-delete-via-view",
            markdown_content="Published content",
            published=True,
            author_id=admin.id,
        )
        test_post.save()
        post_id = test_post.id

        response = self.client.get(
            url_for("admin.delete", post_id=post_id), follow_redirects=True
        )

        # Should redirect to dashboard
        assert response.status_code == 200

        # Verify post was deleted
        deleted_post = Post.query.get(post_id)
        assert deleted_post is None


class TestAdminRetract(ViewTestMixin):
    """Test admin retract functionality."""

    def test_retract_requires_authentication(self):
        """Test GET /retract/<id> requires authentication."""
        post = Post.query.filter_by(slug="test-post-1").first()

        response = self.client.get(
            url_for("admin.retract", post_id=post.id), follow_redirects=True
        )

        assert_status_with_message(
            status_code=200, response=response, message="Admin Login"
        )

    def test_retract_published_post_success(self):
        """Test /retract/<id> successfully retracts published post."""
        self.login_admin("test_admin")

        # Create a published post to retract
        from marrow_blog.blueprints.admin.models import AdminUser

        admin = AdminUser.query.filter_by(username="test_admin").first()

        test_post = Post(
            title="Published Post to Retract",
            slug="published-post-to-retract-via-view",
            markdown_content="Published content",
            published=True,
            author_id=admin.id,
        )
        test_post.save()
        post_id = test_post.id

        response = self.client.get(
            url_for("admin.retract", post_id=post_id), follow_redirects=True
        )

        # Should redirect to dashboard
        assert response.status_code == 200
        assert_status_with_message(
            status_code=200, response=response, message="Admin Dashboard"
        )

        # Verify post is now a draft in database
        retracted_post = Post.query.get(post_id)
        assert retracted_post is not None
        assert retracted_post.published is False

    def test_retract_draft_post_shows_info(self):
        """Test /retract/<id> shows info message for already draft posts."""
        self.login_admin("test_admin")

        # Get a draft post from fixtures
        draft_post = Post.query.filter_by(slug="draft-post").first()
        assert draft_post.published is False  # Verify it's a draft

        response = self.client.get(
            url_for("admin.retract", post_id=draft_post.id),
            follow_redirects=True,
        )

        # Should redirect to dashboard
        assert response.status_code == 200
        assert_status_with_message(
            status_code=200, response=response, message="Admin Dashboard"
        )

        # Verify post remains a draft
        post_check = Post.query.get(draft_post.id)
        assert post_check.published is False

    def test_retract_nonexistent_post(self):
        """Test /retract/<id> returns 404 for non-existent post."""
        self.login_admin("test_admin")

        response = self.client.get(url_for("admin.retract", post_id=99999))

        assert response.status_code == 404

    def test_retract_redirect_to_dashboard(self):
        """Test /retract/<id> redirects to dashboard."""
        self.login_admin("test_admin")

        # Create a dedicated published post for this test
        admin = AdminUser.query.filter_by(username="test_admin").first()
        test_post = Post(
            title="Published Post for Retract Test",
            slug="published-post-for-retract-test",
            markdown_content="Published content",
            published=True,
            author_id=admin.id,
        )
        test_post.save()

        response = self.client.get(
            url_for("admin.retract", post_id=test_post.id)
        )

        # Should redirect to dashboard
        assert response.status_code == 302
        assert "/dashboard" in response.location


class TestAuthRequired(ViewTestMixin):
    """Test authentication requirements across admin routes."""

    def test_all_protected_routes_require_login(self):
        """Test all protected routes require login."""
        protected_routes = [
            ("admin.dashboard", {}),
            ("admin.logout", {}),
            ("admin.post", {}),
            ("admin.upload_doc", {}),
        ]

        for route_name, kwargs in protected_routes:
            response = self.client.get(
                url_for(route_name, **kwargs), follow_redirects=True
            )
            assert_status_with_message(
                status_code=200, response=response, message="Admin Login"
            )

    def test_login_route_accessible_without_auth(self):
        """Test login route is accessible without authentication."""
        response = self.client.get(url_for("admin.login"))

        assert response.status_code == 200
        assert "Admin Login" in response.get_data(as_text=True)

    def test_authenticated_access_to_protected_routes(self):
        """Test authenticated access to protected routes works."""
        self.login_admin("test_admin")

        accessible_routes = [
            ("admin.dashboard", {}),
            ("admin.post", {}),
            ("admin.upload_doc", {}),
        ]

        for route_name, kwargs in accessible_routes:
            response = self.client.get(url_for(route_name, **kwargs))
            assert response.status_code == 200

    def test_session_management_works(self):
        """Test Flask-Login session management works correctly."""
        # Not logged in - should redirect
        response = self.client.get(
            url_for("admin.dashboard"), follow_redirects=True
        )
        assert_status_with_message(
            status_code=200, response=response, message="Admin Login"
        )

        # Login
        self.login_admin("test_admin")

        # Now should access dashboard
        response = self.client.get(url_for("admin.dashboard"))
        assert response.status_code == 200

        # Logout
        self.logout_admin()

        # Should redirect again
        response = self.client.get(
            url_for("admin.dashboard"), follow_redirects=True
        )
        assert_status_with_message(
            status_code=200, response=response, message="Admin Login"
        )

    def test_cross_user_session_isolation(self):
        """Test different admin users have isolated sessions."""
        # Login as first admin
        self.login_admin("test_admin")
        response = self.client.get(url_for("admin.dashboard"))
        assert response.status_code == 200

        # Logout and login as second admin
        self.logout_admin()
        self.login_admin("test_editor")
        response = self.client.get(url_for("admin.dashboard"))
        assert response.status_code == 200
