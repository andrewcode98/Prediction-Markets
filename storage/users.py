from typing import Dict
from dataclasses import dataclass

@dataclass
class User:
    id : int
    username: str
    password_hash: str

users_by_username : Dict[str, User] = {}
users_by_id : Dict[int, User] = {}