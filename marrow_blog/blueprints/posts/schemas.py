from marshmallow import fields, validate
from marrow_blog.extensions import marshmallow
from marrow_blog.blueprints.posts.models import Post

class PostSchema(marshmallow.Schema):
    id = fields.Int(dump_only=True)
    title = fields.Str()
    markdown_content = fields.Str()
    published = fields.Bool()
    created_on = fields.DateTime(dump_only=True)
    updated_on = fields.DateTime(dump_only=True)
    author_id = fields.Int(dump_only=True)
    author_username = fields.Method("get_author_username")
    
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
    markdown_content = fields.Str(allow_none=True, load_default="")
    published = fields.Bool(load_default=False)

post_schema = PostSchema()
posts_schema = PostSchema(many=True)
create_post_schema = CreateOrUpdatePostSchema()
update_post_schema = CreateOrUpdatePostSchema()
