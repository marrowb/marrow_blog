import xml.etree.ElementTree as ET

from lib.tests import ViewTestMixin
from marrow_blog.blueprints.admin.models import AdminUser
from marrow_blog.blueprints.posts.models import Post


class TestRSSFeed(ViewTestMixin):
    """Test RSS feed functionality."""

    def test_rss_feed_returns_200(self):
        """Test RSS feed returns 200 status code."""
        response = self.client.get("/rss.xml")
        assert response.status_code == 200

    def test_rss_feed_content_type(self):
        """Test RSS feed returns correct content type."""
        response = self.client.get("/rss.xml")
        assert response.content_type == "application/rss+xml; charset=utf-8"

    def test_rss_feed_valid_xml(self):
        """Test RSS feed returns valid XML."""
        response = self.client.get("/rss.xml")

        # Should be able to parse as XML without errors
        root = ET.fromstring(response.data)
        assert root.tag == "rss"
        assert root.attrib["version"] == "2.0"

    def test_rss_feed_structure(self):
        """Test RSS feed has required elements."""
        response = self.client.get("/rss.xml")
        root = ET.fromstring(response.data)

        # Find channel element
        channel = root.find("channel")
        assert channel is not None

        # Check required channel elements
        title = channel.find("title")
        assert title is not None
        assert title.text == "Brandon Marrow's Blog"

        link = channel.find("link")
        assert link is not None

        description = channel.find("description")
        assert description is not None

    def test_rss_feed_only_published_posts(self):
        """Test RSS feed only includes published posts."""
        # Create test posts
        admin = AdminUser.query.filter_by(username="test_admin").first()

        published_post = Post(
            title="Published Post for RSS",
            slug="published-post-rss",
            markdown_content="Published content",
            excerpt="Published excerpt",
            published=True,
            author_id=admin.id,
        )
        published_post.save()

        draft_post = Post(
            title="Draft Post for RSS",
            slug="draft-post-rss",
            markdown_content="Draft content",
            excerpt="Draft excerpt",
            published=False,
            author_id=admin.id,
        )
        draft_post.save()

        response = self.client.get("/rss.xml")
        response_text = response.data.decode("utf-8")

        # Should contain published post
        assert "Published Post for RSS" in response_text
        assert "published-post-rss" in response_text

        # Should NOT contain draft post
        assert "Draft Post for RSS" not in response_text
        assert "draft-post-rss" not in response_text

    def test_rss_feed_with_tags(self):
        """Test RSS feed includes post tags as categories."""
        admin = AdminUser.query.filter_by(username="test_admin").first()

        tagged_post = Post(
            title="Tagged Post for RSS",
            slug="tagged-post-rss",
            markdown_content="Tagged content",
            excerpt="Tagged excerpt",
            tags="tech,blog,test",
            published=True,
            author_id=admin.id,
        )
        tagged_post.save()

        response = self.client.get("/rss.xml")
        root = ET.fromstring(response.data)

        # Find the item for our post
        channel = root.find("channel")
        items = channel.findall("item")

        # Look for our post item
        post_item = None
        for item in items:
            title = item.find("title")
            if title is not None and title.text == "Tagged Post for RSS":
                post_item = item
                break

        assert post_item is not None

        # Check categories (tags)
        categories = post_item.findall("category")
        category_texts = [cat.text for cat in categories]

        assert "tech" in category_texts
        assert "blog" in category_texts
        assert "test" in category_texts


class TestSitemap(ViewTestMixin):
    """Test sitemap functionality."""

    def test_sitemap_returns_200(self):
        """Test sitemap returns 200 status code."""
        response = self.client.get("/sitemap.xml")
        assert response.status_code == 200

    def test_sitemap_content_type(self):
        """Test sitemap returns correct content type."""
        response = self.client.get("/sitemap.xml")
        assert response.content_type == "application/xml; charset=utf-8"

    def test_sitemap_valid_xml(self):
        """Test sitemap returns valid XML."""
        response = self.client.get("/sitemap.xml")

        # Should be able to parse as XML without errors
        root = ET.fromstring(response.data)
        assert (
            root.tag == "{http://www.sitemaps.org/schemas/sitemap/0.9}urlset"
        )

    def test_sitemap_includes_homepage(self):
        """Test sitemap includes homepage URL."""
        response = self.client.get("/sitemap.xml")
        root = ET.fromstring(response.data)

        # Look for homepage URL
        urls = root.findall("{http://www.sitemaps.org/schemas/sitemap/0.9}url")
        homepage_found = False

        for url in urls:
            loc = url.find("{http://www.sitemaps.org/schemas/sitemap/0.9}loc")
            if loc is not None and loc.text.endswith("/"):
                homepage_found = True

                # Check homepage has proper attributes
                priority = url.find(
                    "{http://www.sitemaps.org/schemas/sitemap/0.9}priority"
                )
                assert priority is not None
                assert priority.text == "1.0"

                changefreq = url.find(
                    "{http://www.sitemaps.org/schemas/sitemap/0.9}changefreq"
                )
                assert changefreq is not None
                assert changefreq.text == "weekly"
                break

        assert homepage_found

    def test_sitemap_only_published_posts(self):
        """Test sitemap only includes published posts."""
        # Create test posts
        admin = AdminUser.query.filter_by(username="test_admin").first()

        published_post = Post(
            title="Published Post for Sitemap",
            slug="published-post-sitemap",
            markdown_content="Published content",
            published=True,
            author_id=admin.id,
        )
        published_post.save()

        draft_post = Post(
            title="Draft Post for Sitemap",
            slug="draft-post-sitemap",
            markdown_content="Draft content",
            published=False,
            author_id=admin.id,
        )
        draft_post.save()

        response = self.client.get("/sitemap.xml")
        response_text = response.data.decode("utf-8")

        # Should contain published post
        assert "published-post-sitemap" in response_text

        # Should NOT contain draft post
        assert "draft-post-sitemap" not in response_text

    def test_sitemap_post_structure(self):
        """Test sitemap posts have required elements."""
        # Create a published post
        admin = AdminUser.query.filter_by(username="test_admin").first()

        test_post = Post(
            title="Sitemap Structure Test",
            slug="sitemap-structure-test",
            markdown_content="Test content",
            published=True,
            author_id=admin.id,
        )
        test_post.save()

        response = self.client.get("/sitemap.xml")
        root = ET.fromstring(response.data)

        # Find our post URL
        urls = root.findall("{http://www.sitemaps.org/schemas/sitemap/0.9}url")
        post_url = None

        for url in urls:
            loc = url.find("{http://www.sitemaps.org/schemas/sitemap/0.9}loc")
            if loc is not None and "sitemap-structure-test" in loc.text:
                post_url = url
                break

        assert post_url is not None

        # Check required elements for post URLs
        loc = post_url.find("{http://www.sitemaps.org/schemas/sitemap/0.9}loc")
        assert loc is not None
        assert loc.text.endswith("/blog/sitemap-structure-test")

        lastmod = post_url.find(
            "{http://www.sitemaps.org/schemas/sitemap/0.9}lastmod"
        )
        assert lastmod is not None

        changefreq = post_url.find(
            "{http://www.sitemaps.org/schemas/sitemap/0.9}changefreq"
        )
        assert changefreq is not None
        assert changefreq.text == "monthly"

        priority = post_url.find(
            "{http://www.sitemaps.org/schemas/sitemap/0.9}priority"
        )
        assert priority is not None
        assert priority.text == "0.8"
