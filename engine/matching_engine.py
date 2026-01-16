from collections import deque
from typing import List, Dict
from datetime import datetime,timezone
from engine.orderbook import Order, OrderBook
from engine.account import Account
from asyncio import Queue
import asyncio
import random





        


# One matching engine for multiple orderbooks
class MatchingEngine():
    def __init__(self):
        self.queues : Dict[int, Queue] = {}
        self.orderbooks : Dict[int, OrderBook] = {}
        # user_id -> Account class
        self.accounts : Dict[int, Account] = {} 
        self.market_num: int = 0

    # Method to add new market -> initializing its queue of orders and orderbook state
    def add_market(self, market_id:int):
        self.queues[market_id] = Queue()
        self.orderbooks[market_id] = OrderBook()
        self.market_num += 1

    # Method to add new accounts
    def add_account(self, user_id):
        self.accounts[user_id] = Account(username="andreas", password = "gaf", positions = {})

    # Method to sumbit orders to queue
    def submit_order(self, user_id, market_id, order_data:Dict):
        account = self.accounts[user_id]
        order_id = int(str(market_id) + str(user_id) + str(random.randint(1,10000)))
        order = Order(id = order_id, user_id = user_id,
                       market_id=market_id, price = order_data["price"],
                       side = order_data["side"], order_type = order_data["order_type"],
                       quantity = order_data["quantity"], time_submitted=datetime.now(timezone.utc), order_status = 0)
        
        self.queues[market_id].put(order)
        
        account.add_position(order_id, order)
        return order_id


    # Test function to sumbit orders and populate order books
    async def submit_orders(self, market_id):
        order_id = 1
        while True:
            order1 = Order(id = order_id, user_id = 1, market_id=market_id, price = 100.00,
                            side = "B",  order_type = "L", quantity=100, time_submitted=datetime.now(timezone.utc), order_status=0)
            order_id += 1
            order2 = Order(id = order_id, user_id = 2, market_id=market_id, price = 105.00, side = "S",
                             order_type = "L", quantity=100, time_submitted=datetime.now(timezone.utc), order_status=0)
            order_id += 1
            order3 = Order(id = order_id, user_id = 3, market_id=market_id, price = None, side = "S",
                             order_type = "M", quantity=50, time_submitted=datetime.now(timezone.utc), order_status=0)
            order_id += 1
            order4 = Order(id = order_id - 2, user_id = 2, market_id=market_id, price = 105.00, side = "S",
                             order_type = "C", quantity=None, time_submitted=datetime.now(timezone.utc), order_status=0)
            order_id += 1
            await self.queues[market_id].put(order1)
            await self.queues[market_id].put(order2)
            await self.queues[market_id].put(order3)
            await self.queues[market_id].put(order4)
            self.accounts[order1.user_id].add_position(order1.id, order1)
            self.accounts[order2.user_id].add_position(order2.id, order2)
            self.accounts[order3.user_id].add_position(order3.id, order3)
            self.accounts[order4.user_id].add_position(order4.id, order4)
            print(f"Submitted order {order1.id} to market {market_id}")
            print(f"Submitted order {order2.id} to market {market_id}")
            print(f"Submitted order {order3.id} to market {market_id}")
            print(f"Submitted order {order4.id} to market {market_id}")
            await asyncio.sleep(5)
            

    async def process_queue(self, market_id):
        q = self.queues[market_id]
        ob = self.orderbooks[market_id]
        while True:
            print(f"Awaiting Order for market[{market_id}]")
            order = await q.get()
            order_id = order.id
            user_id = order.user_id
            best_bid = ob.bids.peekitem(-1)[0] if ob.bids else None
            best_ask = ob.asks.peekitem(0)[0] if ob.asks else None
            # If its a market order match it
            if order.order_type == "M":
                ob.match_market_order(order)
                self.accounts[user_id].positions[order_id].order_status = 1
                print(f"Market order id {order.id} executed!")
                continue
            # If its a cancel order match the order id and cancel it
            if order.order_type == "C":
               if ob.cancel_order(order):
                   print(f"Order id {order.id} cancelled succesfuly")
                   self.accounts[user_id].positions[order_id].order_status = 3
                   continue
               else:
                   print(f"Order id {order.id} has not been cancelled succesfuly")
                   continue
                
            # Limit sell order placed
            if order.side == "S":
                if best_bid is None or order.price > best_bid:
                    ob.add_order(order)
                    print(f"Market[{market_id}] LIMIT SELL order id {order.id} added @ {order.price}")
                else:
                    ob.match_market_order(order)
                    print(f"Market order id {order.id} executed!")
            # Limit buy order placed
            elif order.side == "B":
                if best_ask is None or order.price < best_ask:
                    ob.add_order(order)
                    print(f"Market[{market_id}] LIMIT BUY order id {order.id} added @ {order.price}")
                else:
                    ob.match_market_order(order)
                    print(f"Market order id {order.id} executed!")

    # Test function to view orderbook changes
    async def view_async_orderbook(self, market_id):
        ob = self.orderbooks[market_id]   
        while True:
            ob.view_orderbook()
            await asyncio.sleep(5)     

    # Test function to view positions of specific user
    async def view_user_positions(self, user_id):
        account = self.accounts[user_id]
        while True:
            for order_id, order in account.positions.items():
                print(f"Order_id[{order_id}]: Price:{order.price}$ Qty:{order.quantity} Status:{order.order_status} time:{order.time_submitted}")
            await asyncio.sleep(5)        

    async def run(self):
        tasks = []
        for market_id in self.queues:
            tasks.append(self.process_queue(market_id))
            tasks.append(self.submit_orders(market_id))
           
        
        await asyncio.gather(*tasks)




