from fastapi import APIRouter

from app.database import get_db
from app.services import scorecards

router = APIRouter(prefix="/api/public", tags=["public"])
# NOTE: no auth dependencies here — these endpoints are intentionally open.


@router.get("/scorecards")
async def public_scorecards():
    """Headline platform metrics for the landing page."""
    db = get_db()
    ngos = [{**n.to_dict(), "id": n.id} for n in db.collection("ngos").stream()]
    stories = [s.to_dict() for s in db.collection("impact_stories").stream()]
    needs = [n.to_dict() for n in db.collection("needs").stream()]
    return scorecards.platform_scorecards(ngos, stories, needs)


@router.get("/gallery")
async def public_gallery(limit: int = 24):
    """Verified impact stories (before/after) for the public Impact Gallery."""
    db = get_db()
    stories = [{**s.to_dict(), "id": s.id} for s in db.collection("impact_stories").stream()]
    visible = [s for s in stories if s.get("verified", True)]
    visible.sort(key=lambda s: s.get("created_at", ""), reverse=True)
    return {"stories": visible[:limit]}


@router.get("/directory")
async def public_directory(sector: str | None = None, search: str | None = None):
    """Vetted NGO directory with trust metrics, ranked most-trustworthy first."""
    db = get_db()
    ngos = [{**n.to_dict(), "id": n.id} for n in db.collection("ngos").stream()]
    return {"ngos": scorecards.rank_directory(ngos, sector, search)}