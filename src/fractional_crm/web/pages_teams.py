"""Teams UI: team list, member roster, and the add-member form."""
from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from fractional_crm.team import ROLES, TeamMember, Team
from fractional_crm.sqlite_team_repository import SqliteTeamRepository
from fractional_crm.web.deps import get_team_repo
from fractional_crm.web.errors import not_found
from fractional_crm.web.templates import templates

router = APIRouter(prefix="/teams")

def _find_team(repo, team_id):
    """Return the team dict with this id, or raise a 404."""
    for team in repo.list_teams():
        if team["id"] == team_id:
            return team
    raise not_found(f"no team with id {team_id}")

def _list_response(request, repo, *, error=None, form=None, status_code=200):
    """Render the teams list page, optionally with a form error and prior input."""
    return templates.TemplateResponse(request, "teams/list.html", {
        "teams": repo.list_teams(), "error": error, "form": form or {},
    }, status_code=status_code)

def _detail_response(request, team, members, *, error=None, form=None, status_code=200):
    """Render a team's detail page, optionally with a form error and prior input."""
    return templates.TemplateResponse(request, "teams/detail.html", {
        "team": team, "members": members, "roles": ROLES,
        "error": error, "form": form or {},
    }, status_code=status_code)

def _roster_response(request, members, *, status_code=200):
    """Render just the team member roster fragment (used for HTMX swaps)."""
    return templates.TemplateResponse(request, "teams/_roster.html",
                                      {"members": members}, status_code=status_code)

@router.get("", response_class=HTMLResponse)
def teams_list(request: Request,
               repo: SqliteTeamRepository = Depends(get_team_repo)) -> HTMLResponse:
    """Render the team list page."""
    return _list_response(request, repo)

@router.post("", response_class=Response)
def create_team(request: Request, name: str = Form(...),
                repo: SqliteTeamRepository = Depends(get_team_repo)) -> Response:
    """Create a new team."""
    try:
        team = Team(name)               # validates and strips; raises ValueError when blank
        repo.create_team(team.name)
    except ValueError as e:
        return _list_response(request, repo, error=str(e), form={"name": name})
    return RedirectResponse("/teams", status_code=303)

@router.get("/{team_id}", response_class=HTMLResponse)
def team_detail(request: Request, team_id: int,
                repo: SqliteTeamRepository = Depends(get_team_repo)) -> HTMLResponse:
    """Render the detail page for a specific team."""
    team = _find_team(repo, team_id)
    members = repo.list_members(team_id)
    return _detail_response(request, team, members)

@router.post("/{team_id}/members", response_class=Response)
def add_member(request: Request, team_id: int,
               name: str = Form(...), email: str = Form(...), role: str = Form(...),
               repo: SqliteTeamRepository = Depends(get_team_repo)) -> Response:
    """Add a new member to a team."""
    team = _find_team(repo, team_id)
    try:
        member = TeamMember(name=name, email=email, role=role)
        repo.add_member(team_id, member)
    except ValueError as e:
        members = repo.list_members(team_id)
        return _detail_response(request, team, members, error=str(e),
                               form={"name": name, "email": email, "role": role})
    except KeyError as e:
        raise not_found(str(e))
    members = repo.list_members(team_id)
    if request.headers.get("HX-Request"):
        return _roster_response(request, members)   # HTMX swaps just the roster
    return RedirectResponse(f"/teams/{team_id}", status_code=303)
