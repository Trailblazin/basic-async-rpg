#TODO: Improve this, create factory class that holds RNG objects
# Also, research more data secure practices for these features.

import random

class Boss:
    def __init__(self):
        self.name = "Chaos"
        self.hp = 300
        self.currentHP = self.hp
        self.atk = 10
        self.speed = 10
        self.type = "Boss"

    def is_alive(self):
        return self.currentHP > 0

    def select_target(self, players):
        return random.choice([p for p in players if p.currentHP > 0])