from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from lib.util_sqlalchemy import ResourceMixin
from marrow_blog.extensions import db


class AdminUser(UserMixin, ResourceMixin, db.Model):
    __tablename__ = "admin_users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    mfa_secret = db.Column(db.String(32), nullable=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def is_mfa_enabled(self):
        return self.mfa_secret is not None

    def __repr__(self):
        return f"<AdminUser {self.username}>"
