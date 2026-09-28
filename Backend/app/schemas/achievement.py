from __future__ import annotations
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class AchievementCreateRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=200, description="Achievement title (e.g. 'Advanced Python Certification')")
    description: str = Field(..., min_length=5, max_length=2000, description="Detailed explanation of what was achieved")
    criteria: str = Field(..., min_length=5, max_length=5000, description="Verifiable assessment criteria or requirements met")
    skills: List[str] = Field(default_factory=list, description="Competency and skill tags (e.g. ['Machine Learning', 'Python'])")
    category: Optional[str] = Field("certification", description="Category: 'certification', 'course', 'internship', 'badge'")
    level: Optional[str] = Field(None, description="Level: 'beginner', 'intermediate', 'advanced', 'expert'")
    image: Optional[str] = Field(None, description="Badge or certificate emblem artwork URL")
    url: Optional[str] = Field(None, description="Link to official syllabus, course, or assessment page")
    credits: Optional[float] = Field(None, description="Academic or CEU credits awarded, if any")


class AchievementUpdateRequest(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=200)
    description: Optional[str] = Field(None, min_length=5, max_length=2000)
    criteria: Optional[str] = Field(None, min_length=5, max_length=5000)
    skills: Optional[List[str]] = None
    category: Optional[str] = None
    level: Optional[str] = None
    image: Optional[str] = None
    url: Optional[str] = None
    credits: Optional[float] = None


class AchievementResponse(BaseModel):
    id: str
    achievement_id: str
    organization_id: str
    name: str
    description: str
    criteria: str
    skills: List[str] = Field(default_factory=list)
    category: str = "certification"
    level: Optional[str] = None
    image: Optional[str] = None
    url: Optional[str] = None
    credits: Optional[float] = None
    created_at: datetime
    updated_at: datetime


class AchievementListResponse(BaseModel):
    items: List[AchievementResponse]
    total: int
