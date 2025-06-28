from marshmallow import fields, validate

from marrow_blog.extensions import marshmallow


class PostSchema(marshmallow.Schema):
    id = fields.Int(dump_only=True)
    title = fields.Str()
    slug = fields.Str()
    excerpt = fields.Str(allow_none=True)
    markdown_content = fields.Str()
    published = fields.Bool()
    tags = fields.Str(allow_none=True)
    tag_list = fields.Method("get_tag_list")
    created_on = fields.DateTime(dump_only=True)
    updated_on = fields.DateTime(dump_only=True)
    author_id = fields.Int(dump_only=True)
    author_username = fields.Method("get_author_username")

    class Meta:
        fields = (
            "id",
            "title",
            "slug",
            "excerpt",
            "markdown_content",
            "published",
            "tags",
            "tag_list",
            "created_on",
            "updated_on",
            "author_id",
            "author_username",
        )
        ordered = True

    def get_author_username(self, obj):
        if obj.author:
            return obj.author.username
        return None

    def get_tag_list(self, obj):
        return obj.tag_list


class CreatePostSchema(marshmallow.Schema):
    title = fields.Str(required=True, validate=validate.Length(min=1, max=255))
    slug = fields.Str(validate=validate.Length(max=255))
    excerpt = fields.Str(allow_none=True)
    markdown_content = fields.Str(allow_none=True, load_default="")
    published = fields.Bool(load_default=False, validate=validate.Equal(False))
    tags = fields.Str(allow_none=True)
    updated_on = fields.Str(required=False, allow_none=True)


class UpdatePostSchema(marshmallow.Schema):
    title = fields.Str(validate=validate.Length(min=1, max=255))
    slug = fields.Str(validate=validate.Length(max=255))
    excerpt = fields.Str(allow_none=True)
    markdown_content = fields.Str(allow_none=True)
    published = fields.Bool()
    tags = fields.Str(allow_none=True)
    updated_on = fields.Str(required=True, allow_none=False)


post_schema = PostSchema()
posts_schema = PostSchema(many=True)
create_post_schema = CreatePostSchema()
update_post_schema = UpdatePostSchema()
