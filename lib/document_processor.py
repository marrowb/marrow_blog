import frontmatter
import re
from typing import Dict, Tuple, List, Optional
from slugify import slugify

class DocumentProcessor:
    """Business logic for processing markdown documents and posts."""
    
    @staticmethod
    def generate_unique_slug(title: str, exclude_id: Optional[int] = None) -> str:
        """Generate unique slug, checking database for conflicts."""
        from marrow_blog.blueprints.posts.models import Post
        
        base_slug = slugify(title)
        slug = base_slug
        counter = 1
        
        while True:
            query = Post.query.filter_by(slug=slug)
            if exclude_id:
                query = query.filter(Post.id != exclude_id)
            
            if not query.first():
                return slug
            
            slug = f"{base_slug}-{counter}"
            counter += 1
    
    @staticmethod
    def extract_excerpt(content: str, max_length: int = 200) -> str:
        """Extract meaningful excerpt from markdown content."""
        if not content:
            return ""
        
        # Remove frontmatter if present
        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 3:
                content = parts[2]
        
        lines = content.strip().split('\n')
        for line in lines:
            line = line.strip()
            # Skip headers, empty lines, and markdown syntax
            if line and not line.startswith('#') and not line.startswith('```'):
                # Remove basic markdown formatting
                clean_line = re.sub(r'[*_`\[\]()]', '', line)
                if len(clean_line) > 10:  # Must have substantial content
                    return (clean_line[:max_length] + '...') if len(clean_line) > max_length else clean_line
        
        return ""
    
    @staticmethod
    def process_frontmatter(markdown_content: str) -> Tuple[Dict, str]:
        """Parse YAML frontmatter and return metadata dict + clean content."""
        try:
            post_data = frontmatter.loads(markdown_content)
            return post_data.metadata, post_data.content
        except Exception:
            # If frontmatter parsing fails, return empty metadata
            return {}, markdown_content
    
    @staticmethod
    def validate_post_data(data: Dict) -> List[str]:
        """Validate post data and return list of errors."""
        errors = []
        
        if not data.get('title', '').strip():
            errors.append("Title is required")
        
        if len(data.get('title', '')) > 255:
            errors.append("Title must be 255 characters or less")
        
        if data.get('slug') and len(data['slug']) > 255:
            errors.append("Slug must be 255 characters or less")
        
        if data.get('tags') and len(data['tags']) > 500:
            errors.append("Tags must be 500 characters or less")
        
        return errors

class PostManager:
    """Business logic for post operations."""
    
    @staticmethod
    def create_from_upload(content_bytes: bytes, filename: str, author_id: int) -> Tuple[bool, str, Optional[object]]:
        """Create post from uploaded markdown file. Returns (success, message, post_object)."""
        from marrow_blog.blueprints.posts.models import Post
        from marrow_blog.extensions import db
        
        try:
            markdown_content = content_bytes.decode('utf-8')
            metadata, clean_content = DocumentProcessor.process_frontmatter(markdown_content)
            
            # Extract data with fallbacks
            title = metadata.get('title', PostManager._title_from_filename(filename))
            slug = metadata.get('slug') or DocumentProcessor.generate_unique_slug(title)
            excerpt = metadata.get('excerpt') or DocumentProcessor.extract_excerpt(clean_content)
            published = metadata.get('published', False)
            tags = PostManager._normalize_tags(metadata.get('tags', []))
            
            # Validate data
            post_data = {
                'title': title,
                'slug': slug,
                'excerpt': excerpt,
                'published': published,
                'tags': tags
            }
            
            errors = DocumentProcessor.validate_post_data(post_data)
            if errors:
                return False, '; '.join(errors), None
            
            # Check for existing post
            existing = Post.query.filter(
                (Post.title == title) | (Post.slug == slug)
            ).first()
            
            if existing:
                return False, f"Post with title '{title}' or slug '{slug}' already exists", None
            
            # Create post
            new_post = Post(
                title=title,
                slug=slug,
                excerpt=excerpt,
                markdown_content=clean_content,
                published=published,
                tags=tags,
                author_id=author_id
            )
            
            db.session.add(new_post)
            db.session.commit()
            
            status = "published" if published else "draft"
            return True, f"Successfully imported '{title}' as {status} post", new_post
            
        except UnicodeDecodeError:
            return False, "Unable to decode file. Please ensure it's a UTF-8 text file.", None
        except Exception as e:
            return False, f"Error processing file: {str(e)}", None
    
    @staticmethod
    def _normalize_tags(tags) -> str:
        """Normalize tags from various formats to comma-separated string."""
        if isinstance(tags, list):
            return ', '.join(str(tag).strip() for tag in tags if str(tag).strip())
        elif isinstance(tags, str):
            return tags
        else:
            return ""
    
    @staticmethod 
    def _title_from_filename(filename: str) -> str:
        """Generate title from filename."""
        name = filename.replace('.md', '').replace('_', ' ').replace('-', ' ')
        return ' '.join(word.capitalize() for word in name.split())