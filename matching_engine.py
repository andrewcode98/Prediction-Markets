from collections import deque
from typing import List, Dict
from datetime import datetime,timezone
from sortedcontainers import SortedDict
from asyncio import Queue
import asyncio

class Order():
    def __init__(self, id:int, user_id:int, market_id:int, price:float, side:str,
                  order_type:str, quantity:int, time_submitted:datetime, order_status:int):
        # side -> Buy/Sell as B/S
        # type -> Limit/Market/Cancel as L/M/C
        # status -> 0,1,2,3 -> 0: Sumbitted, 1: Filled, 2: Partially_Filled, 3: Cancelled
        self.id = id
        self.market_id = market_id
        self.price = price
        self.side = side
        self.order_type = order_type
        self.quantity = quantity
        self.time_submitted = time_submitted
        self.user_id = user_id
        self.order_status = order_status
    
    def fill_order(self, qty):
        self.quantity -= qty

class Account():
    def __init__(self, username:str, password:str, positions:Dict, balance:float = 0):
        self.username = username
        self.password = password
        self.balance = balance
        # Mapping order_id -> order
        self.positions = positions

    def add_position(self, order_id:int, order:Order):
        self.positions[order_id] = order

    




class OrderBook():
    def __init__(self):
        # sorted dictionary stores price -> deque of Orders. 
        # Bid price levels, iterate them in descending highest -> lowest when matching
        # Ask price levels, iterate them in ascending lowest -> highest when matching
        self.bids : SortedDict[float, deque] = SortedDict() 
        self.asks : SortedDict[float, deque] = SortedDict() 
    
    def view_orderbook(self):
        print("Asks")
        for key,value in reversed(self.asks.items()):
            print(f"Price: {key}, Qtys: {[order.quantity for order in value]}")
        print("Bids")
        for key,value in (self.bids.items()):
            print(f"Price: {key}, Qtys: {[order.quantity for order in value]}")

    def add_order(self, order:Order):
       
        book = self.bids if order.side == "B" else self.asks
        if order.price not in book:
            book[order.price] = deque()
        book[order.price].append(order)
    
    def change_order_status(self,incoming_order, resting_order):
        orders = [incoming_order, resting_order]
        for order in orders:
            if order.quantity == 0:
                order.order_status = 1
            else:
                order.order_status = 2


    # return whether a trade happened
    def processTrade(self, incoming_order:Order, resting_order:Order, queue:deque) -> bool:
        min_qty = min(incoming_order.quantity, resting_order.quantity)
        trade_price = resting_order.price
        incoming_order.fill_order(min_qty)
        resting_order.fill_order(min_qty)
        self.change_order_status(incoming_order, resting_order)

        if resting_order.quantity == 0:
            queue.popleft()
        
        return min_qty > 0

    def match_market_buy_order(self, order:Order):
        book = self.asks
        while (order.quantity > 0 and book):
            # Start with best ask
            best_price, queue = book.peekitem(0)
            while queue and order.quantity > 0:
                resting = queue[0]
                if resting.user_id == order.user_id:
                    queue.rotate(-1)
                    continue
                self.processTrade(order, resting, queue)
            if not queue:
                del book[best_price]

                    

    def match_market_sell_order(self, order:Order):
        book = self.bids
        while (order.quantity > 0 and book):
            # Start with best bid
            best_price, queue = book.peekitem(-1)
            while queue and order.quantity > 0:
                resting = queue[0]
                if resting.user_id == order.user_id:
                    queue.rotate(-1)
                    continue
                self.processTrade(order, resting, queue)
            if not queue:
                del book[best_price]

    def match_market_order(self, order:Order):
        if order.side == "B":
            self.match_market_buy_order(order)
        else:
            self.match_market_sell_order(order)

    def cancel_order(self, order:Order):
        ob = self.bids if order.side == "B" else self.asks
        if ob and order.price in ob:
           queue = ob[order.price]
           for i in range(len(queue)):
               queue_order = queue[i]
               # Condition to find the order
               if order.id == queue_order.id and order.user_id == queue_order.user_id:
                   del queue[i]
                   return True
        return False
        


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




