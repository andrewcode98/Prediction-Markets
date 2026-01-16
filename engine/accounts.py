from engine.orderbook import Order
from typing import Dict

class Account():
    def __init__(self, username:str, password:str, positions:Dict, balance:float = 0):
        self.username = username
        self.password = password
        self.balance = balance
        # Mapping order_id -> order
        self.positions = positions

    def add_position(self, order_id:int, order:Order):
        self.positions[order_id] = order