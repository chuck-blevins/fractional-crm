from fastapi import APIRouter, Depends
from pydantic import BaseModel
from fractional_crm.team import TeamMember
from fractional_crm.sqlite_team_repository import SqliteTeamRepository
from fractional_crm.web.deps import get_team_repo
from fractional_crm.web.errors import conflict, invalid, not_found

router = APIRouter(prefix="/api/teams", tags=["teams"])

class TeamIn(BaseModel): name: str
class TeamOut(BaseModel): id: int; name: str
class MemberIn(BaseModel): name: str; email: str; role: str
class MemberOut(MemberIn): pass

def _member_out(m: TeamMember) -> MemberOut:
    return MemberOut(name=m.name, email=m.email, role=m.role)

@router.post("", status_code=201)
def create_team(payload: TeamIn, repo: SqliteTeamRepository = Depends(get_team_repo)) -> TeamOut:
    tid = repo.create_team(payload.name)
    return TeamOut(id=tid, name=payload.name)

@router.get("")
def list_teams(repo: SqliteTeamRepository = Depends(get_team_repo)) -> list[TeamOut]:
    return [TeamOut(id=t["id"], name=t["name"]) for t in repo.list_teams()]

@router.post("/{team_id}/members", status_code=201)
def add_member(team_id: int, payload: MemberIn, repo: SqliteTeamRepository = Depends(get_team_repo)) -> MemberOut:
    try:
        m = TeamMember(name=payload.name, email=payload.email, role=payload.role)
    except ValueError as e:
        raise invalid(str(e))
    try:
        repo.add_member(team_id, m)
    except KeyError as e:
        raise not_found(str(e))
    except ValueError as e:
        raise conflict(str(e))
    return _member_out(m)

@router.get("/{team_id}/members")
def list_members(team_id: int, role: str | None = None, repo: SqliteTeamRepository = Depends(get_team_repo)) -> list[MemberOut]:
    return [_member_out(m) for m in repo.list_members(team_id, role)]
