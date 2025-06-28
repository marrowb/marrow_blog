import json
import uuid

from lib.tests import ViewTestMixin
from marrow_blog.blueprints.posts.models import Post


class TestPostViewGet(ViewTestMixin):
    """Test POST API GET endpoints."""

    def test_get_post_by_id_success(self):
        """Test GET /api/v1/post/<id> returns post data."""
        self.login_admin("test_admin")

        post = Post.query.filter_by(slug="test-post-1").first()

        response = self.client.get(f"/api/v1/post/{post.id}/")

        assert response.status_code == 200
        data = response.get_json()
        assert data["id"] == post.id
        assert data["title"] == "Test Post 1"
        assert data["slug"] == "test-post-1"
        assert data["published"] is True

    def test_get_post_by_id_not_found(self):
        """Test GET /api/v1/post/<id> returns 404 for non-existent post."""
        self.login_admin("test_admin")

        response = self.client.get("/api/v1/post/99999/")

        assert response.status_code == 404

    def test_get_posts_index(self):
        """Test GET /api/v1/post/ returns list of posts."""
        self.login_admin("test_admin")

        response = self.client.get("/api/v1/post/")

        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)
        assert len(data) >= 3  # At least our fixture posts


class TestPostViewCreate(ViewTestMixin):
    """Test POST API creation endpoint."""

    def test_create_post_requires_authentication(self):
        """Test POST /api/v1/post/ requires authentication."""
        data = {"title": "Unauthorized Post"}

        response = self.client.post(
            "/api/v1/post/",
            data=json.dumps(data),
            content_type="application/json",
        )

        # Should redirect to login or return 401
        assert response.status_code in [302, 401]

    def test_create_post_success(self):
        """Test POST /api/v1/post/ creates new post successfully."""
        self.login_admin("test_admin")

        unique_id = str(uuid.uuid4())[:8]
        data = {
            "title": f"New API Post {unique_id}",
            "markdown_content": "# Content\n\nTest content",
        }

        response = self.client.post(
            "/api/v1/post/",
            data=json.dumps(data),
            content_type="application/json",
        )

        assert response.status_code == 201
        response_data = response.get_json()
        assert response_data["title"] == f"New API Post {unique_id}"
        assert response_data["published"] is False  # Default

        # Verify post was created in database
        created_post = Post.query.filter_by(
            title=f"New API Post {unique_id}"
        ).first()
        assert created_post is not None

    def test_create_post_invalid_data(self):
        """Test POST /api/v1/post/ validates required fields."""
        self.login_admin("test_admin")

        data = {}  # Missing required title

        response = self.client.post(
            "/api/v1/post/",
            data=json.dumps(data),
            content_type="application/json",
        )

        assert response.status_code == 400
        error_data = response.get_json()
        assert "error" in error_data


class TestPostViewDelete(ViewTestMixin):
    """Test POST API DELETE endpoint."""

    def test_delete_post_requires_authentication(self):
        """Test DELETE /api/v1/post/<id> requires authentication."""
        post = Post.query.filter_by(slug="test-post-1").first()

        response = self.client.delete(f"/api/v1/post/{post.id}/")

        # Should redirect to login or return 401
        assert response.status_code in [302, 401]

    def test_delete_post_requires_author(self):
        """Test DELETE /api/v1/post/<id> requires post author."""
        # Login as different admin than post author
        self.login_admin(
            "test_editor"
        )  # Different from test_admin who owns fixtures

        post = Post.query.filter_by(slug="test-post-1").first()

        response = self.client.delete(f"/api/v1/post/{post.id}/")

        assert response.status_code == 403
        error_data = response.get_json()
        assert "Forbidden" in error_data["error"]

    def test_delete_post_success(self):
        """Test DELETE /api/v1/post/<id> successfully deletes post."""
        self.login_admin("test_admin")  # Post author

        # Create a post to delete (don't use fixtures to avoid affecting other tests)
        unique_id = str(uuid.uuid4())[:8]
        new_post = Post(
            title=f"Post to Delete {unique_id}",
            slug=f"post-to-delete-{unique_id}",
            markdown_content="Content to delete",
            author_id=1,  # test_admin's ID
        )
        new_post.save()
        post_id = new_post.id

        response = self.client.delete(f"/api/v1/post/{post_id}/")

        assert response.status_code == 204

        # Verify post was deleted from database
        deleted_post = Post.query.get(post_id)
        assert deleted_post is None

    def test_delete_post_not_found(self):
        """Test DELETE /api/v1/post/<id> returns 404 for non-existent post."""
        self.login_admin("test_admin")

        response = self.client.delete("/api/v1/post/99999/")

        assert response.status_code == 404

    def test_delete_published_post(self):
        """Test DELETE /api/v1/post/<id> can delete published posts."""
        self.login_admin("test_admin")

        # Create a published post to delete
        unique_id = str(uuid.uuid4())[:8]
        new_post = Post(
            title=f"Published Post to Delete {unique_id}",
            slug=f"published-post-to-delete-{unique_id}",
            markdown_content="Published content",
            published=True,
            author_id=1,  # test_admin's ID
        )
        new_post.save()
        post_id = new_post.id

        response = self.client.delete(f"/api/v1/post/{post_id}/")

        assert response.status_code == 204

        # Verify post was deleted
        deleted_post = Post.query.get(post_id)
        assert deleted_post is None


class TestPostViewPatch(ViewTestMixin):
    """Test POST API PATCH endpoint for updates and retraction."""

    def test_patch_post_requires_authentication(self):
        """Test PATCH /api/v1/post/<id> requires authentication."""
        post = Post.query.filter_by(slug="test-post-1").first()

        data = {"title": "Updated Title"}
        response = self.client.patch(
            f"/api/v1/post/{post.id}/",
            data=json.dumps(data),
            content_type="application/json",
        )

        # Should redirect to login or return 401
        assert response.status_code in [302, 401]

    def test_patch_post_requires_author(self):
        """Test PATCH /api/v1/post/<id> requires post author."""
        # Login as different admin than post author
        self.login_admin("test_editor")

        post = Post.query.filter_by(slug="test-post-1").first()

        data = {
            "title": "Unauthorized Update",
            "updated_on": post.updated_on.isoformat(),
        }
        response = self.client.patch(
            f"/api/v1/post/{post.id}/",
            data=json.dumps(data),
            content_type="application/json",
        )

        assert response.status_code == 403
        error_data = response.get_json()
        assert "Forbidden" in error_data["error"]

    def test_patch_post_retract_published(self):
        """Test PATCH /api/v1/post/<id> can retract published post."""
        self.login_admin("test_admin")

        # Create a published post to retract
        unique_id = str(uuid.uuid4())[:8]
        new_post = Post(
            title=f"Published Post to Retract {unique_id}",
            slug=f"published-post-to-retract-{unique_id}",
            markdown_content="Published content",
            published=True,
            author_id=1,  # test_admin's ID
        )
        new_post.save()
        post_id = new_post.id

        # Retract the post (set published=False)
        data = {
            "published": False,
            "updated_on": new_post.updated_on.isoformat(),
        }
        response = self.client.patch(
            f"/api/v1/post/{post_id}/",
            data=json.dumps(data),
            content_type="application/json",
        )

        assert response.status_code == 200
        response_data = response.get_json()
        assert response_data["published"] is False

        # Verify in database
        updated_post = Post.query.get(post_id)
        assert updated_post.published is False

    def test_patch_post_publish_draft(self):
        """Test PATCH /api/v1/post/<id> can publish draft post."""
        self.login_admin("test_admin")

        # Create a draft post to publish
        unique_id = str(uuid.uuid4())[:8]
        new_post = Post(
            title=f"Draft Post to Publish {unique_id}",
            slug=f"draft-post-to-publish-{unique_id}",
            markdown_content="Draft content",
            published=False,
            author_id=1,  # test_admin's ID
        )
        new_post.save()
        post_id = new_post.id

        # Publish the post (set published=True)
        data = {
            "published": True,
            "updated_on": new_post.updated_on.isoformat(),
        }
        response = self.client.patch(
            f"/api/v1/post/{post_id}/",
            data=json.dumps(data),
            content_type="application/json",
        )

        assert response.status_code == 200
        response_data = response.get_json()
        assert response_data["published"] is True

        # Verify in database
        updated_post = Post.query.get(post_id)
        assert updated_post.published is True

    def test_patch_post_version_conflict(self):
        """Test PATCH /api/v1/post/<id> handles version conflicts."""
        self.login_admin("test_admin")

        # Create a post to test version conflict (don't modify fixtures)
        unique_id = str(uuid.uuid4())[:8]
        new_post = Post(
            title=f"Version Test Post {unique_id}",
            slug=f"version-test-post-{unique_id}",
            markdown_content="Original content",
            author_id=1,
        )
        new_post.save()

        # Use outdated timestamp to simulate conflict
        old_timestamp = "2020-01-01T12:00:00"
        data = {
            "title": f"Conflicted Update {unique_id}",
            "updated_on": old_timestamp,
        }
        response = self.client.patch(
            f"/api/v1/post/{new_post.id}/",
            data=json.dumps(data),
            content_type="application/json",
        )

        assert response.status_code == 409
        error_data = response.get_json()
        assert "modified since last load" in error_data["error"]

    def test_patch_post_partial_update(self):
        """Test PATCH /api/v1/post/<id> allows partial updates."""
        self.login_admin("test_admin")

        # Create a post to update
        unique_id = str(uuid.uuid4())[:8]
        new_post = Post(
            title=f"Original Title {unique_id}",
            slug=f"original-slug-{unique_id}",
            markdown_content="Original content",
            author_id=1,
        )
        new_post.save()
        post_id = new_post.id
        original_content = new_post.markdown_content

        # Update only title
        data = {
            "title": f"Updated Title Only {unique_id}",
            "updated_on": new_post.updated_on.isoformat(),
        }
        response = self.client.patch(
            f"/api/v1/post/{post_id}/",
            data=json.dumps(data),
            content_type="application/json",
        )

        assert response.status_code == 200
        response_data = response.get_json()
        assert response_data["title"] == f"Updated Title Only {unique_id}"

        # Verify other fields unchanged
        updated_post = Post.query.get(post_id)
        assert updated_post.title == f"Updated Title Only {unique_id}"
        assert updated_post.markdown_content == original_content
        assert updated_post.slug == f"original-slug-{unique_id}"

    def test_patch_post_not_found(self):
        """Test PATCH /api/v1/post/<id> returns 404 for non-existent post."""
        self.login_admin("test_admin")

        data = {
            "title": "Not Found Update",
            "updated_on": "2024-01-01T12:00:00",
        }
        response = self.client.patch(
            "/api/v1/post/99999/",
            data=json.dumps(data),
            content_type="application/json",
        )

        assert response.status_code == 404

    def test_patch_post_without_updated_on(self):
        """Test PATCH /api/v1/post/<id> works without updated_on field."""
        self.login_admin("test_admin")

        # Create a post to update (don't modify fixtures)
        unique_id = str(uuid.uuid4())[:8]
        new_post = Post(
            title=f"Test Update Post {unique_id}",
            slug=f"test-update-post-{unique_id}",
            markdown_content="Original content",
            author_id=1,
        )
        new_post.save()
        post_id = new_post.id

        # Update without updated_on field
        data = {"title": f"Updated Without Timestamp {unique_id}"}
        response = self.client.patch(
            f"/api/v1/post/{post_id}/",
            data=json.dumps(data),
            content_type="application/json",
        )

        assert response.status_code == 200
        response_data = response.get_json()
        assert (
            response_data["title"] == f"Updated Without Timestamp {unique_id}"
        )
