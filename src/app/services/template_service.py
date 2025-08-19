from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi import Request
import os

class TemplateService:
    def __init__(self, templates: Jinja2Templates):
        self.templates = templates
        self._setup_template_functions()

    def _setup_template_functions(self):
        """Add custom functions to Jinja2 templates"""
        self.templates.env.globals.update(load_svg=self._load_svg)

    def _load_svg(self, filename):
        """Load SVG file content and return as string with currentColor support"""
        svg_path = os.path.join(os.path.dirname(__file__), f'../../../static/icons/{filename}.svg')
        try:
            with open(svg_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Remove existing width/height attributes to allow CSS control
            import re
            content = re.sub(r'\s*width="[^"]*"', '', content)
            content = re.sub(r'\s*height="[^"]*"', '', content)
            
            # Automatically convert common fill colors to currentColor
            replacements = [
                ('fill="#000"', 'fill="currentColor"'),
                ('fill="#000000"', 'fill="currentColor"'),
                ('fill="black"', 'fill="currentColor"'),
                ('fill="#333"', 'fill="currentColor"'),
                ('fill="#333333"', 'fill="currentColor"'),
            ]
            
            for old, new in replacements:
                content = content.replace(old, new)
                
            return content
            
        except FileNotFoundError:
            return f'<!-- SVG not found: {filename} -->'
        except Exception as e:
            return f'<!-- Error loading {filename}: {e} -->'

    def render(self, template_name, context, request: Request | None = None) -> HTMLResponse:
        ctx = dict(context)
        if request is not None:
            ctx.setdefault('request', request)
        return self.templates.TemplateResponse(template_name, ctx)

    def render_index(self, context, request: Request | None = None) -> HTMLResponse:
        return self.render('index.html', context, request)

    def render_post(self, context, request: Request | None = None) -> HTMLResponse:
        return self.render('post.html', context, request)
