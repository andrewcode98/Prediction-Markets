from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from engine.matching_engine import MatchingEngine
import asyncio

app = FastAPI()
engine = MatchingEngine()

class OrderRequest(BaseModel):
    user_id: int
    market_id: int
    side: str
    price: float
    quantity: int
    order_type: str

@app.post("/orders")
def sumbit_order(req: OrderRequest):
    if req.user_id not in engine.accounts:
        raise HTTPException(status_code=404, detail = "User not found")

    order_id = engine.submit_order(user_id = req.user_id, market_id = req.market_id, order_data = req.dict())
    return {"status":"accepted",
            "order_id": order_id}

# Test function to see if we can get details of order submitted
@app.get("/orders/{user_id}")
def get_user_orders(user_id:int):
    if user_id not in engine.accounts:
        raise HTTPException(status_code=404, detail="User not found")
    account = engine.accounts[user_id]
    orders_list = []
    for order_id, order in account.positions.items():
        orders_list.append({
            "order_id" : order_id,
            "price" : order.price,
            "quantity": order.quantity,
            "status": order.order_status,
            "time_submitted": str((order.time_submitted))


        }) 
    return {"positions":  orders_list}

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(engine.run())


engine.add_market(1)
engine.add_account(user_id = 1)
engine.add_account(user_id = 2)
engine.add_account(user_id = 3)
