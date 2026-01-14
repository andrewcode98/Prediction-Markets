from collections import deque
from typing import List
import heapq
from typing import Dict
from datetime import datetime,timezone
from sortedcontainers import SortedDict
from asyncio import Queue
import asyncio

class Order():
    def __init__(self, id:int, market_id:int, price:float, side:str, order_type:str, quantity:int, time_submitted:datetime):
        # side -> Buy/Sell as B/S
        # type -> Limit/Market as L/M
        self.id = id
        self.market_id = market_id
        self.price = price
        self.side = side
        self.order_type = order_type
        self.quantity = quantity
        self.time_submitted = time_submitted
        
class OrderBook():
    def __init__(self):
        # sorted dictionary stores price -> deque of Orders. 
        # Bid price levels, iterate them in descending highest -> lowest when matching
        # Ask price levels, iterate them in ascending lowest -> highest when matching
        self.bids : SortedDict[float, deque] = SortedDict() 
        self.asks : SortedDict[float, deque] = SortedDict() 

    def add_order(self, order:Order):
       
        book = self.bids if order.side == "B" else self.asks
        if order.price not in book:
            book[order.price] = deque()
        book[order.price].append(order)
        


# One matching engine for multiple orderbooks
class MatchingEngine():
    def __init__(self):
        self.queues : Dict[int, Queue] = {}
        self.orderbooks : Dict[int, OrderBook] = {}
        self.market_num: int = 0

    # Method to add new market -> initializing its queue of orders and orderbook state
    def add_market(self, market_id:int):
        self.queues[market_id] = Queue()
        self.orderbooks[market_id] = OrderBook()
        self.market_num += 1

    # Test function to sumbit orders every 2 sec
    async def submit_orders(self, market_id):
        order_id = 1
        while True:
            order = Order(id = order_id, market_id=market_id, price = 100.00, side = "B",  order_type = "L", quantity=100, time_submitted=datetime.now(timezone.utc))
            await self.queues[market_id].put(order)
            print(f"Submitted order {order.id} to market {market_id}")
            await asyncio.sleep(5)
            order_id += 1

    async def process_queue(self, market_id):
        q = self.queues[market_id]
        while True:
            print(f"Awaiting Order for market[{market_id}]")
            order = await q.get()
            if order.order_type == "L":
                self.orderbooks[market_id].add_order(order)
                print(f"Market:[{market_id}], Order {order.id} has been added to orderbook at {order.time_submitted}!")

    async def run(self):
        tasks = []
        for market_id in self.queues:
            tasks.append(self.process_queue(market_id))
            tasks.append(self.submit_orders(market_id))
        
        await asyncio.gather(*tasks)


mtch_engine = MatchingEngine()
mtch_engine.add_market(1)
mtch_engine.add_market(2)
asyncio.run(mtch_engine.run())

