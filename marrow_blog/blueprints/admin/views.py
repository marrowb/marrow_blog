from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask import current_app
from flask_login import login_user, logout_user, login_required, current_user
import pyotp  # Uncomment if you implement pyotp for MFA
from werkzeug.utils import secure_filename

from .forms import LoginForm, UploadForm
from .models import AdminUser
from marrow_blog.blueprints.posts.models import Post
from marrow_blog.extensions import db
from lib.document_processor import PostManager

admin = Blueprint("admin", __name__, template_folder="templates")


@admin.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("admin.dashboard"))
    form = LoginForm()
    if form.validate_on_submit():
        user = AdminUser.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            if user.is_mfa_enabled:
                if not form.token.data:
                    flash("MFA token is required.", "warning")
                    return render_template("login.html", form=form, title="Admin Login")
                totp = pyotp.TOTP(user.mfa_secret)  # Uncomment for pyotp
                if not totp.verify(form.token.data):
                    flash("Invalid MFA token.", "error")
                    return render_template("login.html", form=form, title="Admin Login")
                # flash("MFA check placeholder: Successful (if token was provided and valid).", "info") # Placeholder

            login_user(user)
            flash("Logged in successfully.", "success")
            return redirect(url_for("admin.dashboard"))
        else:
            flash("Invalid username or password.", "error")
    return render_template("login.html", form=form, title="Admin Login")


@admin.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("admin.login"))


@admin.route("/dashboard")
@login_required
def dashboard():
    drafts = Post.query.filter_by(published=False).all()
    pubs = Post.query.filter_by(published=True).all()
    return render_template(
        "dashboard.html", title="Admin Dashboard", drafts=drafts, pubs=pubs
    )


@admin.route("/post")
@admin.route("/post/<int:post_id>")
@login_required
def post(post_id=None):
    """Post editor - loads existing post if ID provided, otherwise blank editor."""
    return render_template("post_editor.html", title="Post Editor")


@admin.route("/upload-doc", methods=["GET", "POST"])
@login_required
def upload_doc():
    form = UploadForm()
    
    if form.validate_on_submit() and form.doc_file.data:
        file_storage = form.doc_file.data
        if not file_storage.filename:
            flash("No file selected", "error")
            return render_template("upload_doc.html", title="Upload Document", form=form)
        
        # Read file content immediately
        content_bytes = file_storage.stream.read()
        
        # Process upload
        success, message, post = PostManager.create_from_upload(
            content_bytes, file_storage.filename, current_user.id
        )
        
        flash(message, "success" if success else "error")
        
        if success and post:
            return redirect(url_for('admin.post', post_id=post.id))
    
    return render_template("upload_doc.html", title="Upload Document", form=form)
