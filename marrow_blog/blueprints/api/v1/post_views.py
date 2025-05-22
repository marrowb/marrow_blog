from flask import jsonify, request
from flask_classful import route
from flask_login import current_user

from marrow_blog.extensions import db
from marrow_blog.extensions import marshmallow
from marrow_blog.blueprints.api.v1 import V1FlaskView
from marrow_blog.blueprints.posts.models import Post 
from marrow_blog.blueprints.posts.schemas import ( 
    post_schema,
    posts_schema,
    create_post_schema,
    update_post_schema
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
            return jsonify({'error': 'Invalid input'}), 400

        try: 
            data = create_post_schema.load(json_data)
        except marshmallow.ValidationError as err:
            return jsonify({'error': err.messages}), 422

        new_post = Post(
            title=data['title'],
            markdown_content=data.get('markdown_content'),
            published=data.get('published', False),
            author_id=current_user.id 
        )
        new_post.save()
        return jsonify(post_schema.dump(new_post)), 201

    def patch(self, id):
        """Update an existing post."""
        post = Post.query.get_or_404(id)

        if post.author_id != current_user.id:
            return jsonify({'error': 'Forbidden. You are not the author of this post.'}), 403

        json_data = request.get_json()
        if not json_data:
            return jsonify({'error': 'Invalid input'}), 400

        # Check for version conflict
        last_known_update = json_data.get('last_known_update')
        if last_known_update and post.updated_on.isoformat() != last_known_update:
            return jsonify({'error': 'Post has been modified since last load'}), 409

        try: 
            data = update_post_schema.load(json_data, partial=True)
        except marshmallow.ValidationError as err:
            return jsonify({'error': err.messages}), 422

        if 'title' in data:
            post.title = data['title']
        if 'markdown_content' in data:
            post.markdown_content = data['markdown_content']
        if 'published' in data:
            post.published = data['published']
        
        post.save()
        return jsonify(post_schema.dump(post)), 200

    def delete(self, id):
        """Delete a post."""
        post = Post.query.get_or_404(id)

        if post.author_id != current_user.id:
            return jsonify({'error': 'Forbidden. You are not the author of this post.'}), 403
            
        post.delete()
        return jsonify({}), 204
