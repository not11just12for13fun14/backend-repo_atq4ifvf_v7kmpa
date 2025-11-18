import os
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from database import db, create_document, get_documents
from schemas import CoachProfile, CoachingPackage, Testimonial, BookingRequest

app = FastAPI(title="AnorakFPS API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------- Utilities ----------

def ensure_seed_data():
    """Seed minimal data for first run so the frontend has content."""
    if db is None:
        return

    # Profile
    if "coachprofile" not in db.list_collection_names() or db["coachprofile"].count_documents({}) == 0:
        profile = CoachProfile(
            name="Anorak",
            headline="Apex Legends Pro Coach • Ex-Pro & Former Predator",
            bio=(
                "I’m a former pro and multi-time Predator who has run 3,000+ 1:1 coaching sessions. "
                "I help you climb fast with fundamentals that stick: rotations, comms, fights, and winning habits."
            ),
            years_experience=6,
            sessions_coached=3000,
            highest_rank="Apex Predator",
            specialties=["IGL & Rotations", "Team Comms", "Fighting Fundamentals", "End-Game Clutch"],
            socials={
                "twitter": "https://twitter.com/AnorakFPS",
                "youtube": "https://youtube.com/@AnorakFPS",
                "twitch": "https://twitch.tv/AnorakFPS",
                "website": "https://anorakfps.com",
            },
            avatar_url="/anorak-avatar.png",
            hero_image_url="/anorak-hero.jpg",
        )
        create_document("coachprofile", profile)

    # Packages
    if "coachingpackage" not in db.list_collection_names() or db["coachingpackage"].count_documents({}) == 0:
        pkgs = [
            {
                "title": "VOD Review + Action Plan",
                "description": "45-min VOD breakdown with a ranked-ready improvement plan.",
                "duration_minutes": 45,
                "price_usd": 39,
                "features": [
                    "Personalized improvement goals",
                    "Macro + micro mistakes highlighted",
                    "Drills you can apply instantly",
                ],
                "popular": False,
            },
            {
                "title": "Live 1:1 Coaching Session",
                "description": "90-min live session (share screen or co-queue) with structured skill reps.",
                "duration_minutes": 90,
                "price_usd": 89,
                "features": [
                    "Warm-up & aim routine",
                    "Fight reviews between games",
                    "Rotations & end-game decision making",
                ],
                "popular": True,
            },
            {
                "title": "Climb Pack (3 Sessions)",
                "description": "Three 90-min sessions focused on rapid rank growth.",
                "duration_minutes": 270,
                "price_usd": 239,
                "features": [
                    "Structured progression plan",
                    "VODs + post-session notes",
                    "Priority scheduling",
                ],
                "popular": False,
            },
        ]
        for p in pkgs:
            create_document("coachingpackage", p)

    # Testimonials
    if "testimonial" not in db.list_collection_names() or db["testimonial"].count_documents({}) == 0:
        reviews = [
            {
                "name": "Kade",
                "quote": "Went from Gold to Diamond in 2 weeks. Rotations finally make sense.",
                "rating": 5,
                "platform": "Discord",
                "game_rank_before": "Gold",
                "game_rank_after": "Diamond",
            },
            {
                "name": "Mila",
                "quote": "The fight reviews were insane. I win more 3v3s now.",
                "rating": 5,
                "platform": "Discord",
            },
            {
                "name": "Yuki",
                "quote": "Clarity on my role as IGL was a game changer for our trio.",
                "rating": 5,
                "platform": "Twitter",
            },
        ]
        for r in reviews:
            create_document("testimonial", r)


@app.on_event("startup")
async def startup_event():
    try:
        ensure_seed_data()
    except Exception:
        # If DB not available, silently continue so the API still runs
        pass


# ---------- Models for responses ----------

class ProfileResponse(BaseModel):
    profile: CoachProfile

class PackagesResponse(BaseModel):
    packages: List[CoachingPackage]

class TestimonialsResponse(BaseModel):
    testimonials: List[Testimonial]

class BookingResponse(BaseModel):
    success: bool
    message: str


# ---------- Routes ----------

@app.get("/")
def read_root():
    return {"message": "AnorakFPS API running"}


@app.get("/api/profile", response_model=ProfileResponse)
def get_profile():
    try:
        items = get_documents("coachprofile", limit=1)
        if not items:
            raise HTTPException(status_code=404, detail="Profile not found")
        # Remove Mongo _id for Pydantic validation safety
        item = items[0]
        item.pop("_id", None)
        return {"profile": item}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/packages", response_model=PackagesResponse)
def get_packages():
    try:
        items = get_documents("coachingpackage")
        for it in items:
            it.pop("_id", None)
        return {"packages": items}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/testimonials", response_model=TestimonialsResponse)
def get_testimonials():
    try:
        items = get_documents("testimonial")
        for it in items:
            it.pop("_id", None)
        return {"testimonials": items}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/bookings", response_model=BookingResponse)
def create_booking(request: BookingRequest):
    try:
        create_document("bookingrequest", request)
        return {"success": True, "message": "Booking request received. I’ll reach out via email/Discord."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Expose schemas for the database viewer
@app.get("/schema")
def get_schema():
    return {
        "models": [
            "CoachProfile",
            "CoachingPackage",
            "Testimonial",
            "BookingRequest",
        ]
    }


@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": [],
    }
    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = db.name
            response["connection_status"] = "Connected"
            try:
                response["collections"] = db.list_collection_names()
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️ Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️ Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"
    return response


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
