import logging
import os
import yaml
from datetime import date
from ..models import Author, Post, Series
import markdown

logger = logging.getLogger(__name__)

CONTENT_DIR = os.path.join(os.path.dirname(__file__), '../../../content')
POSTS_DIR = os.path.join(CONTENT_DIR, 'posts')
SERIES_DIR = os.path.join(CONTENT_DIR, 'series')

def parse_frontmatter(md_path):
    with open(md_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    if lines[0].strip() == '---':
        end = next(i for i, line in enumerate(lines[1:], 1) if line.strip() == '---')
        frontmatter = ''.join(lines[1:end])
        body = ''.join(lines[end+1:])
        data = yaml.safe_load(frontmatter)
        return data, body
    return {}, ''.join(lines)

class BlogService:
    def __init__(self):
        self._posts: list[Post] | None = None
        self._series: list[Series] | None = None
        self._md = markdown.Markdown(extensions=[
            'codehilite',
            'fenced_code', 
            'tables',
            'toc'
        ], extension_configs={
            'codehilite': {
                'css_class': 'highlight',
                'use_pygments': True,
                'noclasses': False
            }
        })

    def get_post(self, slug: str) -> Post | None:
        for post in self.posts:
            if post.slug == slug:
                return post
        return None
    
    def get_series(self, slug: str, include_drafts: bool = False) -> Series | None:
        for series in self.series:
            if series.slug == slug:
                if not include_drafts:
                    posts = [post for post in series.posts if not post.draft]
                    series.posts = posts
                return series
        return None
    
    @property
    def posts(self) -> list[Post]:
        if self._posts is not None:
            return self._posts

        posts_list = []
        for fname in os.listdir(POSTS_DIR):
            if not fname.endswith('.md'):
                continue
            path = os.path.join(POSTS_DIR, fname)
            meta, _ = parse_frontmatter(path)
            if not meta:
                continue
            posts_list.append(Post(
                slug=meta.get('slug', fname[:-3]),
                file=fname,
                title=meta.get('title', ''),
                authors=[Author(name=a) for a in meta.get('authors', [])],
                created=date.fromisoformat(meta.get('created', '')),
                updated=date.fromisoformat(meta.get('updated', meta.get('created', ''))),
                description=meta.get('description', ''),
                tags=meta.get('tags', []),
                draft=meta.get('draft', False),
                featured=meta.get('featured', False),
                cover_image=meta.get('cover_image', ''),
                attachments=meta.get('attachments', [])
            ))

        self._posts = posts_list[:]
        return posts_list
    
    @property
    def series(self) -> list[Series]:
        if self._series is not None:
            return self._series

        series_list = []
        for fname in os.listdir(SERIES_DIR):
            if not fname.endswith('.yaml'):
                continue
            path = os.path.join(SERIES_DIR, fname)
            with open(path, 'r', encoding='utf-8') as f:
                meta = yaml.safe_load(f)
            if not meta:
                continue

            posts_data = meta.get('posts', [])
            if isinstance(posts_data[0], dict):
                posts_data.sort(key=lambda p: p.get('order', 0))
                post_slugs = [p['slug'] for p in posts_data]
            else:
                post_slugs = posts_data

            posts = [p for p in self.posts if p.slug in post_slugs]
            posts.sort(key=lambda p: post_slugs.index(p.slug))

            series_list.append(Series(
                slug=meta.get('slug', fname[:-5]),
                title=meta.get('title', ''),
                description=meta.get('description', ''),
                authors=[Author(name=a) for a in meta.get('authors', [])],
                created=date.fromisoformat(meta.get('created', '')),
                status=meta.get('status', ''),
                cover_image=meta.get('cover_image', ''),
                posts=posts
            ))

        self._series = series_list[:]
        return series_list
    
    def get_series_of_post(self, post_slug: str) -> list[Series]:
        return [s for s in self.series if any(p.slug == post_slug for p in s.posts)]
    
    def get_series_navigation(self, series_slug: str, post_slug: str) -> dict | None:
        series = self.get_series(series_slug)
        if not series:
            return None
        
        current_index = None
        for i, post in enumerate(series.posts):
            if post.slug == post_slug:
                current_index = i
                break

        if current_index is None:
            return None
        
        prev_post = series.posts[current_index - 1] if current_index > 0 else None
        next_post = series.posts[current_index + 1] if current_index < len(series.posts) - 1 else None

        return {
            'prev': prev_post,
            'next': next_post,
            'current_index': current_index + 1,
            'total': len(series.posts)
        }

    def get_latest_posts(self, limit: int = 5, include_drafts: bool = False) -> list[Post]:
        posts = self.posts
        if not include_drafts:
            posts = [p for p in posts if not p.draft]
        return sorted(posts, key=lambda p: p.created, reverse=True)[:limit]

    def get_featured_posts(self, limit: int = 5, include_drafts: bool = False) -> list[Post]:
        posts = self.posts
        if not include_drafts:
            posts = [p for p in posts if not p.draft]
        return [p for p in posts if p.featured][:limit]
    
    def render_post_body(self, post: Post) -> str:
        post_path = os.path.join(POSTS_DIR, post.file)
        _, body = parse_frontmatter(post_path)
        return self._md.convert(body)
