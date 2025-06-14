import os
from importlib.metadata import version

from flask import Blueprint, render_template
from marrow_blog.blueprints.posts.models import Post
from flask_flatpages.utils import pygmented_markdown

# from config.settings import DEBUG

page = Blueprint("page", __name__, template_folder="templates")


@page.get("/")
def home():
    return render_template(
        "page/home.html",
        flask_ver=version("flask"),
        python_ver=os.environ["PYTHON_VERSION"],
    )

@page.get("/blog/<int:post_id>")
def blog_post(post_id):
    post = Post.query.filter_by(id=post_id, published=True).first_or_404()
    html_content = pygmented_markdown(post.markdown_content)
    return render_template("page/post.html", post=post, content=html_content)
