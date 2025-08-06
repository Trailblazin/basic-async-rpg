#TODO: Improve this, create factory class that holds RNG objects
# Also, research more data secure practices for these features.

class Boss:
    def __init__(self, rng_pool):
        self.name = "Chaos"
        self.hp = 300
        self.currentHP = self.hp
        self.atk = 10
        self.speed = 10
        self.type = "Boss"
        self.rng = rng_pool.assign_rng(self.name)

    def is_alive(self):
        return self.currentHP > 0

    def select_target(self, players):
        return self.rng.choice([p for p in players if p.currentHP > 0])