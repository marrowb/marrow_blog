from flask import Blueprint, render_template
from flask_flatpages.utils import pygmented_markdown

from marrow_blog.blueprints.posts.models import Post

# from config.settings import DEBUG

page = Blueprint("page", __name__, template_folder="templates")


@page.get("/")
def home():
    _posts = Post.get_recent_posts()
    return render_template("page/home.html", _posts=_posts)


@page.get("/blog/<slug>")
def blog_post(slug):
    post = Post.query.filter_by(slug=slug, published=True).first_or_404()
    html_content = pygmented_markdown(post.markdown_content)
    return render_template("page/post.html", post=post, content=html_content)
