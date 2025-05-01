from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class User:
    user_id: int
    name: Optional[str]
    screen_name: Optional[str]
    location: Optional[str]
    url: Optional[str]
    description: Optional[str]
    profile_image_url: Optional[str]
    profile_banner_url: Optional[str]
    followers_count: Optional[int]
    friends_count: Optional[int]
    listed_count: Optional[int]
    favourites_count: Optional[int]
    statuses_count: Optional[int]
    verified: Optional[bool]
    protected: Optional[bool]
    created_at: Optional[datetime]
