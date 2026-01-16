from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from api.deps import get_engine
from engine.matching_engine import MatchingEngine

router = APIRouter(prefix="/orders", tags=["orders"])

class OrderRequest(BaseModel):
    user_id: int
    market_id: int
    side: str
    price: float
    quantity: int
    order_type: str

@router.post("")
async def sumbit_order(req: OrderRequest, engine: MatchingEngine = Depends(get_engine)):
    if req.user_id not in engine.accounts:
        raise HTTPException(status_code=404, detail = "User not found")

    order_id = await engine.submit_order(user_id = req.user_id, market_id = req.market_id, order_data = req.dict())
    return {"status":"accepted",
            "order_id": order_id}

@router.get("/{user_id}")
def get_user_orders(user_id:int, engine: MatchingEngine = Depends(get_engine)):
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

