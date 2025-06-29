from datetime import datetime, timezone

from flask import Blueprint, current_app, render_template

from marrow_blog.blueprints.posts.models import Post

feeds = Blueprint("feeds", __name__, template_folder="templates")


@feeds.get("/rss.xml")
def rss():
    """RSS 2.0 feed for published blog posts."""
    posts = (
        Post.query.filter_by(published=True)
        .order_by(Post.created_on.desc())
        .limit(20)
        .all()
    )

    # Get server name for absolute URLs
    server_name = current_app.config.get("SERVER_NAME", "localhost:8000")
    if not server_name.startswith(("http://", "https://")):
        # Assume HTTPS in production, HTTP for localhost
        protocol = "https://" if "localhost" not in server_name else "http://"
        base_url = f"{protocol}{server_name}"
    else:
        base_url = server_name.rstrip("/")

    response = render_template(
        "feeds/rss.xml",
        posts=posts,
        base_url=base_url,
        build_date=datetime.now(timezone.utc),
    )

    # Set proper content type for RSS
    response = current_app.response_class(
        response, mimetype="application/rss+xml"
    )

    return response


@feeds.get("/sitemap.xml")
def sitemap():
    """XML sitemap for published blog posts."""
    posts = (
        Post.query.filter_by(published=True)
        .order_by(Post.updated_on.desc())
        .all()
    )

    # Get server name for absolute URLs
    server_name = current_app.config.get("SERVER_NAME", "localhost:8000")
    if not server_name.startswith(("http://", "https://")):
        # Assume HTTPS in production, HTTP for localhost
        protocol = "https://" if "localhost" not in server_name else "http://"
        base_url = f"{protocol}{server_name}"
    else:
        base_url = server_name.rstrip("/")

    response = render_template(
        "feeds/sitemap.xml", posts=posts, base_url=base_url
    )

    # Set proper content type for XML sitemap
    response = current_app.response_class(response, mimetype="application/xml")

    return response
