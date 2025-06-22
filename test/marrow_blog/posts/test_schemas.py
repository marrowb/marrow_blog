import pytest
from marshmallow import ValidationError
from datetime import datetime

from marrow_blog.blueprints.posts.schemas import (
    PostSchema, 
    CreatePostSchema, 
    UpdatePostSchema,
    post_schema,
    posts_schema,
    create_post_schema,
    update_post_schema
)
from marrow_blog.blueprints.posts.models import Post
from marrow_blog.blueprints.admin.models import AdminUser
from lib.tests import ViewTestMixin


class TestPostSchema(ViewTestMixin):
    
    def test_post_schema_serialization(self, session):
        """Test PostSchema correctly serializes a Post model."""
        admin = AdminUser.query.filter_by(username="test_admin").first()
        post = Post.query.filter_by(slug="test-post-1").first()
        
        result = post_schema.dump(post)
        
        assert result['id'] == post.id
        assert result['title'] == 'Test Post 1'
        assert result['slug'] == 'test-post-1'
        assert result['excerpt'] == 'Test excerpt'
        assert result['markdown_content'] == '# Test Content\n\nThis is a test post.'
        assert result['published'] is True
        assert result['tags'] is None
        assert result['tag_list'] == []
        assert 'created_on' in result
        assert 'updated_on' in result
        assert result['author_id'] == admin.id
        assert result['author_username'] == 'test_admin'

    def test_post_schema_with_tags(self, session):
        """Test PostSchema correctly handles tag serialization."""
        post = Post.query.filter_by(slug="tagged-post").first()
        
        result = post_schema.dump(post)
        
        assert result['tags'] == 'test,blog'
        assert result['tag_list'] == ['test', 'blog']

    def test_post_schema_many_serialization(self, session):
        """Test PostSchema serializes multiple posts."""
        posts = Post.query.filter_by(published=True).all()
        
        result = posts_schema.dump(posts)
        
        assert len(result) >= 2  # At least test-post-1 and tagged-post from fixtures
        assert all('id' in post for post in result)
        assert all('title' in post for post in result)

    def test_post_schema_dump_only_fields(self, session):
        """Test that dump_only fields are not included in load."""
        # Test that we can load data without dump_only fields
        data = {
            'title': 'Test Title',
            'slug': 'test-slug',
            'markdown_content': 'Test content',
            'published': True
        }
        
        result = post_schema.load(data)
        
        assert result['title'] == 'Test Title'
        assert result['slug'] == 'test-slug'
        assert result['markdown_content'] == 'Test content'
        assert result['published'] is True
        
        # Ensure dump_only fields don't appear in load result
        assert 'id' not in result
        assert 'created_on' not in result  
        assert 'updated_on' not in result
        assert 'author_id' not in result


class TestCreatePostSchema(ViewTestMixin):

    def test_create_post_schema_valid_data(self, session):
        """Test CreatePostSchema with valid data."""
        data = {
            'title': 'New Test Post',
            'slug': 'new-test-post',
            'excerpt': 'A new test post',
            'markdown_content': '# New Post\n\nContent here',
            'tags': 'new,test'
        }
        
        result = create_post_schema.load(data)
        
        assert result['title'] == 'New Test Post'
        assert result['slug'] == 'new-test-post'
        assert result['excerpt'] == 'A new test post'
        assert result['markdown_content'] == '# New Post\n\nContent here'
        assert result['published'] is False  # Default value
        assert result['tags'] == 'new,test'

    def test_create_post_schema_minimal_data(self, session):
        """Test CreatePostSchema with minimal required data."""
        data = {
            'title': 'Minimal Post'
        }
        
        result = create_post_schema.load(data)
        
        assert result['title'] == 'Minimal Post'
        assert result['markdown_content'] == ""  # Default value
        assert result['published'] is False  # Default value

    def test_create_post_schema_title_required(self, session):
        """Test CreatePostSchema requires title."""
        data = {
            'slug': 'no-title-post'
        }
        
        with pytest.raises(ValidationError) as exc_info:
            create_post_schema.load(data)
        
        assert 'title' in exc_info.value.messages
        assert 'required' in str(exc_info.value.messages['title'])

    def test_create_post_schema_title_length_validation(self, session):
        """Test CreatePostSchema validates title length."""
        # Test empty title
        data = {'title': ''}
        with pytest.raises(ValidationError) as exc_info:
            create_post_schema.load(data)
        assert 'title' in exc_info.value.messages

        # Test title too long
        data = {'title': 'x' * 256}
        with pytest.raises(ValidationError) as exc_info:
            create_post_schema.load(data)
        assert 'title' in exc_info.value.messages

    def test_create_post_schema_slug_length_validation(self, session):
        """Test CreatePostSchema validates slug length."""
        data = {
            'title': 'Valid Title',
            'slug': 'x' * 256
        }
        
        with pytest.raises(ValidationError) as exc_info:
            create_post_schema.load(data)
        
        assert 'slug' in exc_info.value.messages

    def test_create_post_schema_published_validation(self, session):
        """Test CreatePostSchema enforces published=False."""
        data = {
            'title': 'Published Post',
            'published': True
        }
        
        with pytest.raises(ValidationError) as exc_info:
            create_post_schema.load(data)
        
        assert 'published' in exc_info.value.messages

    def test_create_post_schema_allows_none_fields(self, session):
        """Test CreatePostSchema allows None for optional fields."""
        data = {
            'title': 'Test Post',
            'excerpt': None,
            'tags': None
        }
        
        result = create_post_schema.load(data)
        
        assert result['excerpt'] is None
        assert result['tags'] is None


class TestUpdatePostSchema(ViewTestMixin):

    def test_update_post_schema_valid_data(self, session):
        """Test UpdatePostSchema with valid data."""
        data = {
            'title': 'Updated Title',
            'slug': 'updated-slug',
            'excerpt': 'Updated excerpt',
            'markdown_content': '# Updated Content',
            'published': True,
            'tags': 'updated,tags',
            'updated_on': '2024-01-01T12:00:00'
        }
        
        result = update_post_schema.load(data)
        
        assert result['title'] == 'Updated Title'
        assert result['slug'] == 'updated-slug'
        assert result['excerpt'] == 'Updated excerpt'
        assert result['markdown_content'] == '# Updated Content'
        assert result['published'] is True
        assert result['tags'] == 'updated,tags'
        assert result['updated_on'] == '2024-01-01T12:00:00'

    def test_update_post_schema_partial_data(self, session):
        """Test UpdatePostSchema with partial data."""
        data = {
            'title': 'Only Title Updated',
            'updated_on': '2024-01-01T12:00:00'
        }
        
        result = update_post_schema.load(data)
        
        assert result['title'] == 'Only Title Updated'
        assert result['updated_on'] == '2024-01-01T12:00:00'
        assert 'slug' not in result
        assert 'excerpt' not in result

    def test_update_post_schema_updated_on_required(self, session):
        """Test UpdatePostSchema requires updated_on."""
        data = {
            'title': 'Updated Title'
        }
        
        with pytest.raises(ValidationError) as exc_info:
            update_post_schema.load(data)
        
        assert 'updated_on' in exc_info.value.messages
        assert 'required' in str(exc_info.value.messages['updated_on'])

    def test_update_post_schema_updated_on_not_none(self, session):
        """Test UpdatePostSchema does not allow None for updated_on."""
        data = {
            'title': 'Updated Title',
            'updated_on': None
        }
        
        with pytest.raises(ValidationError) as exc_info:
            update_post_schema.load(data)
        
        assert 'updated_on' in exc_info.value.messages

    def test_update_post_schema_title_length_validation(self, session):
        """Test UpdatePostSchema validates title length."""
        # Test empty title
        data = {
            'title': '',
            'updated_on': '2024-01-01T12:00:00'
        }
        with pytest.raises(ValidationError) as exc_info:
            update_post_schema.load(data)
        assert 'title' in exc_info.value.messages

        # Test title too long
        data = {
            'title': 'x' * 256,
            'updated_on': '2024-01-01T12:00:00'
        }
        with pytest.raises(ValidationError) as exc_info:
            update_post_schema.load(data)
        assert 'title' in exc_info.value.messages

    def test_update_post_schema_slug_length_validation(self, session):
        """Test UpdatePostSchema validates slug length."""
        data = {
            'slug': 'x' * 256,
            'updated_on': '2024-01-01T12:00:00'
        }
        
        with pytest.raises(ValidationError) as exc_info:
            update_post_schema.load(data)
        
        assert 'slug' in exc_info.value.messages

    def test_update_post_schema_allows_none_fields(self, session):
        """Test UpdatePostSchema allows None for optional fields."""
        data = {
            'excerpt': None,
            'markdown_content': None,
            'tags': None,
            'updated_on': '2024-01-01T12:00:00'
        }
        
        result = update_post_schema.load(data)
        
        assert result['excerpt'] is None
        assert result['markdown_content'] is None
        assert result['tags'] is None


class TestSchemaInstances(ViewTestMixin):
    
    def test_schema_instances_exist(self, session):
        """Test that schema instances are properly created."""
        assert post_schema is not None
        assert create_post_schema is not None
        assert update_post_schema is not None
        
        # Test they are the right types
        assert isinstance(post_schema, PostSchema)
        assert isinstance(create_post_schema, CreatePostSchema)
        assert isinstance(update_post_schema, UpdatePostSchema)

    def test_post_schema_many_instance(self, session):
        """Test that posts_schema (many=True) works correctly."""
        from marrow_blog.blueprints.posts.schemas import posts_schema
        
        posts = Post.query.limit(2).all()
        result = posts_schema.dump(posts)
        
        assert isinstance(result, list)
        assert len(result) <= 2