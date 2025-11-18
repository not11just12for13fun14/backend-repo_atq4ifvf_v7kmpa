"""
Database Schemas for AnorakFPS (Apex Legends Coaching)

Each Pydantic model represents a collection in MongoDB. The collection name is the
lowercase of the class name.

Use these models for validation and to power the database helper functions.
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List


class CoachProfile(BaseModel):
    """
    Collection: "coachprofile"
    Stores public profile information for the coach used on the website.
    """
    name: str = Field(..., description="Coach display name")
    headline: str = Field(..., description="Short hero tagline")
    bio: str = Field(..., description="Longer about section text")
    years_experience: int = Field(0, ge=0)
    sessions_coached: int = Field(0, ge=0)
    highest_rank: str = Field(..., description="e.g., Apex Predator, Pro League")
    specialties: List[str] = Field(default_factory=list, description="Focus areas")
    socials: dict = Field(default_factory=dict, description="Map of social links")
    avatar_url: Optional[str] = Field(None, description="Profile image URL")
    hero_image_url: Optional[str] = None


class CoachingPackage(BaseModel):
    """
    Collection: "coachingpackage"
    Represents a coaching offer shown on the pricing section.
    """
    title: str
    description: str
    duration_minutes: int = Field(..., ge=15)
    price_usd: float = Field(..., ge=0)
    features: List[str] = Field(default_factory=list)
    popular: bool = False


class Testimonial(BaseModel):
    """
    Collection: "testimonial"
    Student feedback shown on the website.
    """
    name: str
    quote: str
    rating: int = Field(5, ge=1, le=5)
    platform: Optional[str] = Field(None, description="Where the review came from")
    game_rank_before: Optional[str] = None
    game_rank_after: Optional[str] = None


class BookingRequest(BaseModel):
    """
    Collection: "bookingrequest"
    Captures inbound booking requests from the website.
    """
    name: str
    email: EmailStr
    discord: Optional[str] = None
    platform: Optional[str] = Field(None, description="PC, PS, Xbox")
    timezone: Optional[str] = None
    package_title: Optional[str] = None
    goals: Optional[str] = Field(None, description="What the player wants to improve")
    preferred_times: Optional[str] = None


# Note for the database viewer:
# The Flames database viewer reads these models from GET /schema.
# Each class here will map to its own MongoDB collection automatically.
