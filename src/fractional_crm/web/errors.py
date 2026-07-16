"""HTTP error helpers mapping domain exceptions to responses."""
from fastapi import HTTPException


def not_found(detail: str) -> HTTPException:
    """Return a 404 HTTPException with the given detail."""
    return HTTPException(status_code=404, detail=detail)


def invalid(detail: str) -> HTTPException:
    """Return a 422 HTTPException with the given detail."""
    return HTTPException(status_code=422, detail=detail)


def conflict(detail: str) -> HTTPException:
    """Return a 409 HTTPException with the given detail."""
    return HTTPException(status_code=409, detail=detail)
