from storage.users import users_by_username, users_by_id, User
from auth.security import hash_password, verify_password

_next_user_id = 1

def register_user(username:str, password:str) -> User:
    global _next_user_id

    if username in users_by_username:
        raise ValueError("Username already exists")
    
    user = User(id = _next_user_id,
                username = username,
                password_hash = hash_password(password))
    
    users_by_username[username] = user
    users_by_id[_next_user_id] = user
    _next_user_id += 1

    return user

def authenticate_user(username: str, password:str) -> User | None:
    user = users_by_username.get(username)
    if not user:
        return None
    if not verify_password(password, user.password_hash):
        return None

    return user