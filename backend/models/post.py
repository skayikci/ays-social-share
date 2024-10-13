from dataclasses import dataclass
from datetime import datetime

@dataclass
class Post:
    content: str
    platform: str
    status: str = 'pending'
    timestamp: datetime = datetime.utcnow()
