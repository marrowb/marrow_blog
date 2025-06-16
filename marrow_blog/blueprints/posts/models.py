from marrow_blog.extensions import db
from lib.util_sqlalchemy import ResourceMixin
from marrow_blog.blueprints.admin.models import AdminUser # This line is needed

class Post(ResourceMixin, db.Model):
    __tablename__ = "posts"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False, unique=True)
    slug = db.Column(db.String(255), nullable=False, unique=True, index=True)
    excerpt = db.Column(db.Text, nullable=True)
    markdown_content = db.Column(db.Text, nullable=True)
    published = db.Column(db.Boolean, default=False, nullable=False, index=True)
    tags = db.Column(db.String(500), nullable=True, index=True)

    # Assuming AdminUser is defined in marrow_blog.blueprints.admin.models
    author_id = db.Column(db.Integer, db.ForeignKey('admin_users.id'), nullable=False)
    author = db.relationship('AdminUser', backref=db.backref('posts', lazy='dynamic'))

    # created_on and updated_on are inherited from ResourceMixin

    @property
    def tag_list(self):
        """Return tags as a list"""
        return [tag.strip() for tag in (self.tags or '').split(',') if tag.strip()]
    
    @tag_list.setter 
    def tag_list(self, value):
        """Set tags from a list"""
        self.tags = ', '.join(value) if value else None

    def __repr__(self):
        return f"<Post '{self.title}'>"
