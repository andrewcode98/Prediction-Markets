from fastapi import FastAPI
from api.routes import orders, auth
from api.deps import engine
import asyncio
from auth.service import register_user

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(engine.run())

# Include routers
app.include_router(orders.router)
app.include_router(auth.router)

engine.add_market(1)

users_info = [("alice", "pass1"),
              ("bob", "pass2"),
              ("carol", "pass3")]

for username, password in users_info:
    user = register_user(username, password)
    print(f"Registered user {user.username} with ID {user.id}")
    engine.add_account(user_id=user.id)
    print(f"Created engine account for user ID {user.id}")