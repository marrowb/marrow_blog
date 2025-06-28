from flask import jsonify, request
from flask_classful import route
from flask_login import current_user
from marshmallow.exceptions import ValidationError

from marrow_blog.blueprints.api.v1 import V1FlaskView
from marrow_blog.blueprints.posts.models import Post
from marrow_blog.blueprints.posts.schemas import (
    create_post_schema,
    post_schema,
    posts_schema,
    update_post_schema,
)


class PostView(V1FlaskView):
    # route_base defaults to '/post/' based on class name, under V1FlaskView's '/api/v1/' prefix

    def index(self):
        """Get a list of posts."""
        all_posts = Post.query.order_by(Post.created_on.desc()).all()
        return jsonify(posts_schema.dump(all_posts)), 200

    def get(self, id):
        """Get a single post by id."""
        post = Post.query.get_or_404(id)
        return jsonify(post_schema.dump(post)), 200

    def post(self):
        """Create a new post."""
        json_data = request.get_json()
        if not json_data:
            return jsonify({"error": "Invalid input"}), 400

        try:
            data = create_post_schema.load(json_data)
        except ValidationError as err:
            return jsonify({"error": err.messages}), 422

        # Generate slug if not provided
        slug = data.get("slug")
        if not slug:
            from lib.document_processor import DocumentProcessor

            slug = DocumentProcessor.generate_unique_slug(data["title"])

        new_post = Post(
            title=data["title"],
            slug=slug,
            excerpt=data.get("excerpt"),
            markdown_content=data.get("markdown_content"),
            published=data.get("published", False),
            tags=data.get("tags"),
            author_id=current_user.id,
        )
        new_post.save()
        return jsonify(post_schema.dump(new_post)), 201

    def patch(self, id):
        """Update an existing post."""
        post = Post.query.get_or_404(id)

        if post.author_id != current_user.id:
            return jsonify(
                {"error": "Forbidden. You are not the author of this post."}
            ), 403

        json_data = request.get_json()
        if not json_data:
            return jsonify({"error": "Invalid input"}), 400

        # Check for version conflict
        last_known_update = json_data.get("updated_on")
        if (
            last_known_update
            and post.updated_on.isoformat() != last_known_update
        ):
            return jsonify(
                {"error": "Post has been modified since last load"}
            ), 409

        try:
            data = update_post_schema.load(json_data, partial=True)
        except ValidationError as err:
            return jsonify({"error": err.messages}), 422

        # Check slug uniqueness if updating
        if "slug" in data:
            existing = Post.query.filter(
                Post.slug == data["slug"], Post.id != id
            ).first()
            if existing:
                return jsonify({"error": "Slug already exists"}), 409

        if "title" in data:
            post.title = data["title"]
        if "slug" in data:
            post.slug = data["slug"]
        if "excerpt" in data:
            post.excerpt = data["excerpt"]
        if "markdown_content" in data:
            post.markdown_content = data["markdown_content"]
        if "published" in data:
            post.published = data["published"]
        if "tags" in data:
            post.tags = data["tags"]

        post.save()
        return jsonify(post_schema.dump(post)), 200

    def delete(self, id):
        """Delete a post."""
        post = Post.query.get_or_404(id)

        if post.author_id != current_user.id:
            return jsonify(
                {"error": "Forbidden. You are not the author of this post."}
            ), 403

        post.delete()
        return jsonify({}), 204

    @route("/by-slug/<slug>")
    def get_by_slug(self, slug):
        """Get post by slug for SEO-friendly URLs."""
        post = Post.query.filter_by(slug=slug, published=True).first_or_404()
        return jsonify(post_schema.dump(post)), 200
