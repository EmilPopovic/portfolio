import os
import logging
from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import FileResponse, HTMLResponse
from markdown import markdown
from ..dependencies import (
    TemplateService,
    get_template_service,
    BlogService,
    get_blog_service,
    EmailService,
    get_email_service,
)

logger = logging.getLogger(__name__)
router = APIRouter(tags=['frontend'])

CONTENT_DIR = os.path.join(os.path.dirname(__file__), '../../../content')

@router.get('/', response_class=HTMLResponse)
async def serve_frontend(
    request: Request,
    template_service: TemplateService = Depends(get_template_service),
    blog_service: BlogService = Depends(get_blog_service)
):
    hero_md_path = os.path.join(CONTENT_DIR, 'home', 'hero.md')
    with open(hero_md_path, 'r', encoding='utf-8') as f:
        hero_md_content = f.read()

    hero_html = markdown(hero_md_content, extensions=['fenced_code', 'codehilite', 'tables'])

    latest_posts = blog_service.get_latest_posts(limit=3, include_drafts=False)
    project_summaries = blog_service.get_series('project-summaries')
    context = {
        'request': request,
        'title': 'Emil\'s Site',
        'hero': hero_html,
        'latest_posts': latest_posts,
        'project_summaries': project_summaries
    }
    return template_service.render_index(context, request)

@router.get('/favicon.ico', include_in_schema=False, response_class=HTMLResponse)
async def serve_favicon():
    return FileResponse('static/favicon.ico')

@router.get('/about', response_class=HTMLResponse)
async def serve_about(
    request: Request,
    template_service: TemplateService = Depends(get_template_service),
):
    about_md_path = os.path.join(CONTENT_DIR, 'home', 'about.md')
    with open(about_md_path, 'r', encoding='utf-8') as f:
        about_md_content = f.read()

    about_html = markdown(about_md_content, extensions=['fenced_code', 'codehilite', 'tables'])

    context = {
        'request': request,
        'title': 'About Emil',
        'about': about_html,
    }
    return template_service.render('about.html', context, request)

@router.get('/contact', response_class=HTMLResponse)
async def serve_contact(
    request: Request,
    template_service: TemplateService = Depends(get_template_service),
):
    contact_md_path = os.path.join(CONTENT_DIR, 'home', 'contact.md')
    with open(contact_md_path, 'r', encoding='utf-8') as f:
        contact_md_content = f.read()

    contact_html = markdown(contact_md_content, extensions=['fenced_code', 'codehilite', 'tables'])

    context = {
        'request': request,
        'title': 'Contact Emil',
        'contact': contact_html,
        'show_form': os.getenv('SMTP_USERNAME', '')
    }
    return template_service.render('contact.html', context, request)

@router.post('/contact', response_class=HTMLResponse)
async def process_contact_form(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    topic: str = Form('General question'),
    message: str = Form(...),
    email_service: EmailService = Depends(get_email_service),
    template_service: TemplateService = Depends(get_template_service),
):
    errors = []
    if not name.strip():
        errors.append('Name is required')
    if not message.strip():
        errors.append('Message is required')
    if len(message) > 5000:
        errors.append('Message too long')

    contact_md_path = os.path.join(CONTENT_DIR, 'home', 'contact.md')
    with open(contact_md_path, 'r', encoding='utf-8') as f:
        contact_md_content = f.read()

    contact_html = markdown(contact_md_content, extensions=['fenced_code', 'codehilite', 'tables'])

    if errors:
        context = {
            'request': request,
            'title': 'Contact Emil',
            'contact': contact_html,
            'show_form': True,
            'error_message': ' • '.join(errors),
            'form_data': {'name': name, 'email': email, 'topic': topic, 'message': message}
        }
        return template_service.render('contact.html', context, request)
    
    try:
        email_content = f"""
New contact form submission from emilpopovic.me

Name: {name.strip()}
Email: {email.strip()}
Topic: {topic}

Message:
{message.strip()}

---
Sent from your personal website contact form
        """.strip()

        email_service.send_email(content=email_content)

        context = {
            'request': request,
            'title': 'Contact Emil',
            'contact': contact_html,
            'show_form': True,
            'success_message': "Thanks for reaching out! I'll get back to you within 24-72 hours."
        }
        return template_service.render('contact.html', context, request)
    
    except Exception as e:
        print(f'Failed to send contact form email: {e}')
        context = {
            'request': request,
            'title': 'Contact Emil',
            'contact': contact_html,
            'show_form': True,
            'error_message': "That didn't work. Please contact me in a different way. /(._. )\\",
            'form_data': {'name': name, 'email': email, 'topic': topic, 'message': message}
        }
        return template_service.render('contact.html', context, request)
