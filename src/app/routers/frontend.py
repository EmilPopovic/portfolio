import logging
from fastapi import APIRouter, Depends, Request
from fastapi.responses import FileResponse, HTMLResponse
from ..dependencies import TemplateService, get_template_service, BlogService, get_blog_service

logger = logging.getLogger(__name__)
router = APIRouter(tags=['frontend'])

@router.get('/', response_class=HTMLResponse)
async def serve_frontend(
    request: Request,
    template_service: TemplateService = Depends(get_template_service),
    blog_service: BlogService = Depends(get_blog_service)
):
    logger.info('Serving frontend index.html')
    latest_posts = blog_service.get_latest_posts(limit=3, include_drafts=False)
    context = {
        'request': request,
        'latest_posts': latest_posts
    }
    print(latest_posts)
    print(request)
    return template_service.render_index(context, request)

@router.get('/favicon.ico', include_in_schema=False, response_class=HTMLResponse)
async def serve_favicon():
    logger.info('Serving favicon')
    return FileResponse('static/favicon.ico')
