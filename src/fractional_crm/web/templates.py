"""Shared Jinja2 template environment for the server-rendered web UI."""
from pathlib import Path

from fastapi.templating import Jinja2Templates

_TEMPLATES_DIR = Path(__file__).parent / "templates"

# Single shared environment; routers import `templates` and call TemplateResponse.
templates = Jinja2Templates(directory=str(_TEMPLATES_DIR))
