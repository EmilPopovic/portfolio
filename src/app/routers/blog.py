import logging
from fastapi import APIRouter, Depends, HTTPException, Request, Query
from fastapi.responses import HTMLResponse
from ..dependencies import BlogService, get_blog_service, TemplateService, get_template_service

logger = logging.getLogger(__name__)
router = APIRouter(tags=['blog'])

@router.get('/blog', response_class=HTMLResponse)
async def blog(
    request: Request,
    search: str = Query(None, description='Search term'),
    tag: str = Query(None, description='Filter by tag'),
    blog_service: BlogService = Depends(get_blog_service),
    template_service: TemplateService = Depends(get_template_service)
):
    all_posts = blog_service.get_latest_posts(limit=100, include_drafts=False)
    featured_posts = blog_service.get_featured_posts(limit=6, include_drafts=False)
    all_series = blog_service.series

    filtered_posts = all_posts

    if search:
        search_lower = search.lower()
        filtered_posts = [
            post for post in filtered_posts
            if search_lower in post.title.lower() or
               search_lower in post.description.lower() or
               any(search_lower in tag.lower() for tag in post.tags)
        ]

    if tag:
        filtered_posts = [
            post for post in filtered_posts
            if tag in post.tags
        ]

    all_tags = set()
    for post in all_posts:
        all_tags.update(post.tags)
    all_tags = sorted(list(all_tags))

    return template_service.render(
        'blog.html',
        {
            'featured_posts': featured_posts,
            'series': all_series,
            'posts': filtered_posts,
            'all_tags': all_tags,
            'current_search': search,
            'current_tag': tag,
            'title': 'Emil\'s Blog'
        },
        request
    )

@router.get('/blog/p/{post_slug}', response_class=HTMLResponse)
async def post(
    request: Request,
    post_slug: str,
    blog_service: BlogService = Depends(get_blog_service),
    template_service: TemplateService = Depends(get_template_service)
):
    post = blog_service.get_post(post_slug)
    if not post:
        raise HTTPException(status_code=404, detail='Post not found')
    
    html_body = blog_service.render_post_body(post)
    series_list = blog_service.get_series_of_post(post_slug)

    return template_service.render_post(
        {
            'post': post,
            'body': html_body,
            'series_list': series_list,
            'current_series': None,
            'navigation': None,
            'title': post.title
        },
        request
    )

@router.get('/blog/s/{series_slug}', response_class=HTMLResponse)
async def series(
    request: Request,
    series_slug: str,
    blog_service: BlogService = Depends(get_blog_service),
    template_service: TemplateService = Depends(get_template_service)
):
    series = blog_service.get_series(series_slug)
    if not series:
        raise HTTPException(status_code=404, detail='Series not found')
    
    return template_service.render(
        'series.html',
        {
            'series': series,
            'posts': series.posts,
            'title': series.title
        },
        request
    )

@router.get('/blog/s/{series_slug}/p/{post_slug}', response_class=HTMLResponse)
async def post_in_series(
    request: Request,
    series_slug: str,
    post_slug: str,
    blog_service: BlogService = Depends(get_blog_service),
    template_service: TemplateService = Depends(get_template_service)
):
    post = blog_service.get_post(post_slug)
    if not post:
        raise HTTPException(status_code=404, detail='Post not found.')
    
    series = blog_service.get_series(series_slug)
    if not series:
        raise HTTPException(status_code=404, detail='Series not found.')
    
    # Check if post is in this series
    if not any(p.slug == post_slug for p in series.posts):
        raise HTTPException(status_code=404, detail='Post not found in this series')
    
    html_body = blog_service.render_post_body(post)
    series_list = blog_service.get_series_of_post(post_slug)
    navigation = blog_service.get_series_navigation(series_slug, post_slug)

    return template_service.render_post(
        {
            'post': post,
            'body': html_body,
            'series_list': series_list,
            'current_series': series,
            'navigation': navigation,
            'title': post.title
        },
        request
    )
