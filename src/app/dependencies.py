from fastapi.templating import Jinja2Templates
from .services.blog_service import BlogService
from .services.template_service import TemplateService

_blog_service: BlogService | None = None
_templates: Jinja2Templates | None = None

def get_blog_service() -> BlogService:
    global _blog_service
    if _blog_service is None:
        _blog_service = BlogService()
    return _blog_service

def get_templates() -> Jinja2Templates:
    global _templates
    if _templates is None:
        _templates = Jinja2Templates(directory='templates')
    return _templates

def get_template_service() -> TemplateService:
    return TemplateService(get_templates())
