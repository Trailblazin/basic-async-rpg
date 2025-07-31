class Boss:
    def __init__(self):
        self.name = "Chaos"
        self.hp = 300
        self.atk = 10
        self.speed = 10
        self.type = "Boss"

    def is_alive(self):
        return self.hp > 0

    def select_target(self, players):
        return random.choice([p for p in players if p.currentHP > 0])