from marshmallow import fields, validate
from marrow_blog.extensions import marshmallow
from marrow_blog.blueprints.posts.models import Post # Import Post model

class PostSchema(marshmallow.Schema):
    author_username = fields.Method("get_author_username", dump_only=True)

    class Meta:
        fields = (
            'id',
            'title',
            'markdown_content',
            'published',
            'created_on',
            'updated_on',
            'author_id',
            'author_username'
        )
        ordered = True 

    def get_author_username(self, obj):
        if obj.author:
            return obj.author.username
        return None

class CreateOrUpdatePostSchema(marshmallow.Schema):
    title = fields.Str(required=True, validate=validate.Length(min=1, max=255))
    markdown_content = fields.Str(allow_none=True, missing="")
    published = fields.Bool(missing=False)

post_schema = PostSchema()
posts_schema = PostSchema(many=True)
create_post_schema = CreateOrUpdatePostSchema()
update_post_schema = CreateOrUpdatePostSchema()
