import os
from fastapi.templating import Jinja2Templates
from .services.blog_service import BlogService
from .services.template_service import TemplateService
from .services.email_service import EmailService

_blog_service: BlogService | None = None
_templates: Jinja2Templates | None = None
_email_service: EmailService | None = None

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

def get_email_service() -> EmailService:
    global _email_service
    if _email_service is None:
        to = os.getenv('TO', '')
        smtp_username = os.getenv('SMTP_USERNAME', '')
        smtp_password = os.getenv('SMTP_PASSWORD', '')
        smtp_host = os.getenv('SMTP_HOST', '')
        smtp_port = int(os.getenv('SMTP_PORT', ''))
        _email_service = EmailService(
            to,
            smtp_username,
            smtp_password,
            smtp_host,
            smtp_port
        )
    return _email_service
