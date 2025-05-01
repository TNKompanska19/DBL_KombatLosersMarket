from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Tweet:
    tweet_id: int
    created_at: Optional[datetime]
    text: Optional[str]
    source: Optional[str]
    truncated: Optional[bool]
    is_quote_status: Optional[bool]
    quote_count: Optional[int]
    reply_count: Optional[int]
    retweet_count: Optional[int]
    favorite_count: Optional[int]
    lang: Optional[str]
    tweet_url: Optional[str]
    user_id: Optional[int]
    in_reply_to_status_id: Optional[int]
    in_reply_to_user_id: Optional[int]
