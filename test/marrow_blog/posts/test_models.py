import pytest
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timezone

from marrow_blog.blueprints.posts.models import Post
from marrow_blog.blueprints.admin.models import AdminUser
from marrow_blog.extensions import db
from lib.tests import ViewTestMixin


class TestPostModel(ViewTestMixin):
    """Test basic Post model functionality."""

    def test_post_creation_with_required_fields(self, clean_session):
        """Test creating a post with all required fields."""
        admin = AdminUser.query.filter_by(username="test_admin").first()
        
        post = Post(
            title="New Test Post",
            slug="new-test-post",
            author_id=admin.id
        )
        post.save()  # Save to get default values from database
        
        assert post.title == "New Test Post"
        assert post.slug == "new-test-post"
        assert post.author_id == admin.id
        assert post.published is False  # Default value from database
        assert post.excerpt is None
        assert post.markdown_content is None
        assert post.tags is None

    def test_post_save_method(self, clean_session):
        """Test Post save method commits to database."""
        admin = AdminUser.query.filter_by(username="test_admin").first()
        
        post = Post(
            title="Saved Post",
            slug="saved-post",
            author_id=admin.id
        )
        
        # Before save, should not be in database
        assert Post.query.filter_by(slug="saved-post").first() is None
        
        result = post.save()
        
        # After save, should be in database
        saved_post = Post.query.filter_by(slug="saved-post").first()
        assert saved_post is not None
        assert saved_post.title == "Saved Post"
        assert result == post  # save() returns self

    def test_post_delete_method(self, clean_session):
        """Test Post delete method removes from database."""
        admin = AdminUser.query.filter_by(username="test_admin").first()
        
        post = Post(
            title="To Delete",
            slug="to-delete",
            author_id=admin.id
        )
        post.save()
        
        # Verify it exists
        assert Post.query.filter_by(slug="to-delete").first() is not None
        
        post.delete()
        
        # Verify it's deleted
        assert Post.query.filter_by(slug="to-delete").first() is None

    def test_post_repr(self, clean_session):
        """Test Post __repr__ method."""
        post = Post(title="Test Repr", slug="test-repr", author_id=1)
        
        repr_str = repr(post)
        assert "Test Repr" in repr_str
        assert "Post" in repr_str

    def test_post_creation_with_all_fields(self, clean_session):
        """Test creating a post with all fields populated."""
        admin = AdminUser.query.filter_by(username="test_admin").first()
        
        post = Post(
            title="Complete Post",
            slug="complete-post",
            excerpt="This is a complete post",
            markdown_content="# Complete Post\n\nContent here",
            published=True,
            tags="test,complete",
            author_id=admin.id
        )
        post.save()
        
        assert post.title == "Complete Post"
        assert post.slug == "complete-post"
        assert post.excerpt == "This is a complete post"
        assert post.markdown_content == "# Complete Post\n\nContent here"
        assert post.published is True
        assert post.tags == "test,complete"
        assert post.author_id == admin.id


class TestPostTagSystem(ViewTestMixin):
    """Test Post tag system functionality."""

    def test_tag_list_getter_with_tags(self, clean_session):
        """Test tag_list property returns list from comma-separated string."""
        post = Post(title="Tagged", slug="tagged", author_id=1)
        post.tags = "test,blog,python"
        
        tag_list = post.tag_list
        assert tag_list == ["test", "blog", "python"]

    def test_tag_list_getter_with_spaced_tags(self, clean_session):
        """Test tag_list property handles whitespace in tags."""
        post = Post(title="Spaced Tags", slug="spaced-tags", author_id=1)
        post.tags = "test, blog , python"
        
        tag_list = post.tag_list
        assert tag_list == ["test", "blog", "python"]

    def test_tag_list_getter_empty_tags(self, clean_session):
        """Test tag_list property with empty/None tags."""
        post = Post(title="No Tags", slug="no-tags", author_id=1)
        
        # Test None tags
        post.tags = None
        assert post.tag_list == []
        
        # Test empty string tags
        post.tags = ""
        assert post.tag_list == []
        
        # Test whitespace only
        post.tags = "   "
        assert post.tag_list == []

    def test_tag_list_getter_with_empty_segments(self, clean_session):
        """Test tag_list property filters out empty segments."""
        post = Post(title="Messy Tags", slug="messy-tags", author_id=1)
        post.tags = "test,,blog, ,python,"
        
        tag_list = post.tag_list
        assert tag_list == ["test", "blog", "python"]

    def test_tag_list_setter_from_list(self, clean_session):
        """Test tag_list property setter converts list to string."""
        post = Post(title="Set Tags", slug="set-tags", author_id=1)
        
        post.tag_list = ["python", "flask", "testing"]
        assert post.tags == "python, flask, testing"

    def test_tag_list_setter_empty_list(self, clean_session):
        """Test tag_list property setter with empty list."""
        post = Post(title="Empty Tags", slug="empty-tags", author_id=1)
        
        post.tag_list = []
        assert post.tags is None

    def test_tag_list_setter_none_value(self, clean_session):
        """Test tag_list property setter with None."""
        post = Post(title="None Tags", slug="none-tags", author_id=1)
        
        post.tag_list = None
        assert post.tags is None

    def test_tag_list_roundtrip(self, clean_session):
        """Test setting and getting tag_list maintains consistency."""
        post = Post(title="Roundtrip", slug="roundtrip", author_id=1)
        
        original_tags = ["python", "flask", "testing"]
        post.tag_list = original_tags
        retrieved_tags = post.tag_list
        
        assert retrieved_tags == original_tags

    def test_existing_tagged_post_from_fixtures(self, session):
        """Test tag_list property on existing post from fixtures."""
        tagged_post = Post.query.filter_by(slug="tagged-post").first()
        
        assert tagged_post is not None
        assert tagged_post.tags == "test,blog"
        assert tagged_post.tag_list == ["test", "blog"]


class TestPostRelationships(ViewTestMixin):
    """Test Post model relationships."""

    def test_post_author_relationship(self, session):
        """Test Post.author relationship returns AdminUser."""
        post = Post.query.filter_by(slug="test-post-1").first()
        admin = AdminUser.query.filter_by(username="test_admin").first()
        
        assert post.author is not None
        assert post.author.id == admin.id
        assert post.author.username == "test_admin"
        assert isinstance(post.author, AdminUser)

    def test_admin_posts_backref(self, session):
        """Test AdminUser.posts backref returns post collection."""
        admin = AdminUser.query.filter_by(username="test_admin").first()
        
        posts = admin.posts.all()
        assert len(posts) >= 3  # Our fixture posts
        
        # Check that all posts belong to this admin
        for post in posts:
            assert post.author_id == admin.id

    def test_admin_posts_backref_filtering(self, session):
        """Test filtering posts through admin backref."""
        admin = AdminUser.query.filter_by(username="test_admin").first()
        
        published_posts = admin.posts.filter_by(published=True).all()
        draft_posts = admin.posts.filter_by(published=False).all()
        
        assert len(published_posts) >= 2  # test-post-1 and tagged-post
        assert len(draft_posts) >= 1     # draft-post

    def test_post_author_foreign_key(self, clean_session):
        """Test author_id foreign key constraint."""
        # Valid foreign key should work
        admin = AdminUser.query.filter_by(username="test_admin").first()
        post = Post(
            title="FK Test",
            slug="fk-test",
            author_id=admin.id
        )
        post.save()
        
        assert post.author_id == admin.id
        assert post.author.username == "test_admin"


class TestPostConstraints(ViewTestMixin):
    """Test Post database constraints."""

    def test_title_uniqueness_constraint(self, clean_session):
        """Test title must be unique across posts."""
        admin = AdminUser.query.filter_by(username="test_admin").first()
        
        # Create first post
        post1 = Post(
            title="Unique Title",
            slug="unique-slug-1",
            author_id=admin.id
        )
        post1.save()
        
        # Try to create second post with same title
        post2 = Post(
            title="Unique Title",  # Same title
            slug="unique-slug-2",   # Different slug
            author_id=admin.id
        )
        
        with pytest.raises(IntegrityError):
            post2.save()

    def test_slug_uniqueness_constraint(self, clean_session):
        """Test slug must be unique across posts."""
        admin = AdminUser.query.filter_by(username="test_admin").first()
        
        # Create first post
        post1 = Post(
            title="First Title",
            slug="unique-slug",
            author_id=admin.id
        )
        post1.save()
        
        # Try to create second post with same slug
        post2 = Post(
            title="Second Title",  # Different title
            slug="unique-slug",    # Same slug
            author_id=admin.id
        )
        
        with pytest.raises(IntegrityError):
            post2.save()

    def test_title_required_constraint(self, clean_session):
        """Test title is required (not null)."""
        admin = AdminUser.query.filter_by(username="test_admin").first()
        
        post = Post(
            slug="no-title",
            author_id=admin.id
            # No title provided
        )
        
        with pytest.raises(IntegrityError):
            post.save()

    def test_slug_required_constraint(self, clean_session):
        """Test slug is required (not null)."""
        admin = AdminUser.query.filter_by(username="test_admin").first()
        
        post = Post(
            title="No Slug Post",
            author_id=admin.id
            # No slug provided
        )
        
        with pytest.raises(IntegrityError):
            post.save()

    def test_author_id_required_constraint(self, clean_session):
        """Test author_id is required (not null)."""
        post = Post(
            title="No Author",
            slug="no-author"
            # No author_id provided
        )
        
        with pytest.raises(IntegrityError):
            post.save()

    def test_long_field_values_accepted(self, clean_session):
        """Test posts can handle reasonable field lengths."""
        admin = AdminUser.query.filter_by(username="test_admin").first()
        
        # Test with reasonable but long values
        long_title = "A" * 200  # Within 255 limit
        long_slug = "a" * 200   # Within 255 limit
        long_tags = "tag1," * 50  # Within 500 limit when repeated
        
        post = Post(
            title=long_title,
            slug=long_slug,
            tags=long_tags,
            author_id=admin.id
        )
        
        # Should save successfully
        post.save()
        
        saved_post = Post.query.filter_by(slug=long_slug).first()
        assert saved_post is not None
        assert len(saved_post.title) == 200
        assert len(saved_post.slug) == 200

    def test_published_default_value(self, clean_session):
        """Test published defaults to False."""
        admin = AdminUser.query.filter_by(username="test_admin").first()
        
        post = Post(
            title="Default Published",
            slug="default-published",
            author_id=admin.id
        )
        post.save()
        
        # Refresh from database to get default value
        saved_post = Post.query.filter_by(slug="default-published").first()
        assert saved_post.published is False


class TestResourceMixinIntegration(ViewTestMixin):
    """Test ResourceMixin inherited functionality."""

    def test_timestamps_auto_population(self, clean_session):
        """Test created_on and updated_on are automatically set."""
        admin = AdminUser.query.filter_by(username="test_admin").first()
        
        post = Post(
            title="Timestamp Test",
            slug="timestamp-test",
            author_id=admin.id
        )
        
        # Before save, timestamps should be None
        assert post.created_on is None
        assert post.updated_on is None
        
        post.save()
        
        # After save, timestamps should be set
        assert post.created_on is not None
        assert post.updated_on is not None
        assert isinstance(post.created_on, datetime)
        assert isinstance(post.updated_on, datetime)

    def test_updated_on_changes_on_update(self, clean_session):
        """Test updated_on changes when post is modified."""
        admin = AdminUser.query.filter_by(username="test_admin").first()
        
        post = Post(
            title="Update Test",
            slug="update-test",
            author_id=admin.id
        )
        post.save()
        
        original_updated = post.updated_on
        
        # Modify and save again
        post.title = "Updated Title"
        post.save()
        
        assert post.updated_on > original_updated

    def test_resource_mixin_str_method(self, clean_session):
        """Test inherited __str__ method from ResourceMixin."""
        admin = AdminUser.query.filter_by(username="test_admin").first()
        
        post = Post(
            title="Str Test",
            slug="str-test",
            author_id=admin.id
        )
        post.save()
        
        str_repr = str(post)
        
        # Should contain class name and field values
        assert "Post" in str_repr
        assert "Str Test" in str_repr
        assert "str-test" in str_repr

    def test_timestamps_are_datetime_objects(self, clean_session):
        """Test timestamps are proper datetime objects."""
        admin = AdminUser.query.filter_by(username="test_admin").first()
        
        post = Post(
            title="DateTime Test",
            slug="datetime-test",
            author_id=admin.id
        )
        post.save()
        
        # Timestamps should be datetime objects
        assert isinstance(post.created_on, datetime)
        assert isinstance(post.updated_on, datetime)
        
        # Should be recent (within last minute)
        now = datetime.now()
        time_diff = (now - post.created_on.replace(tzinfo=None)).total_seconds()
        assert time_diff < 60  # Should be very recent