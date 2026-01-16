from datetime import datetime
from sortedcontainers import SortedDict
from collections import deque

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