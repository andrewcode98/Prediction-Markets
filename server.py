from matching_engine import MatchingEngine, OrderBook, Order
from datetime import datetime
import asyncio

mtch_engine = MatchingEngine()
mtch_engine.add_market(1)
mtch_engine.add_account(user_id = 1)
mtch_engine.add_account(user_id = 2)
mtch_engine.add_account(user_id = 3)
asyncio.run(mtch_engine.run())


# testing matching_engine mechanisms
# order1 = Order(id = 1, user_id=1, market_id=1, price = 100.00, side = "S", order_type="L", quantity=30, time_submitted=datetime.now())
# order2 = Order(id = 2, user_id=2, market_id=1, price = 100.00, side = "S", order_type="L", quantity=20, time_submitted=datetime.now())
# order3 = Order(id = 3, user_id=3, market_id=1, price = 100.00, side = "S", order_type="L", quantity=20, time_submitted=datetime.now())
# order5 = Order(id = 5, user_id=5, market_id=1, price = 101.00, side = "S", order_type="L", quantity=20, time_submitted=datetime.now())
# orders = [order1, order2, order3, order5]
# for order in orders:
#     mtch_engine.orderbooks[1].add_order(order)
# mtch_engine.orderbooks[1].view_orderbook()
# order4 = Order(id = 4, user_id=4, market_id=1, price = 100.00, side = "B", order_type="M", quantity=70, time_submitted=datetime.now())
# mtch_engine.orderbooks[1].match_market_order(order4)
# mtch_engine.orderbooks[1].view_orderbook()       

