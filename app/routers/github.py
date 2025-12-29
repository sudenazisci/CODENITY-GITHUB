from fastapi import APIRouter
from app.services.github_analyzer import analyze_github

router = APIRouter(
    prefix="/github",
    tags=["GitHub Analysis"]
)

@router.get("/analyze/{username}")
def analyze(username: str, userId: str | None = None):
    return analyze_github(username, userId)
