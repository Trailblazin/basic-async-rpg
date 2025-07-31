# Represents a player or AI participant in the game
class Player:
    # Default class stats for each class
    CLASS_STATS = {
        "Thief": {"hp": 80, "atk": 10, "speed": 15},
        "Warrior": {"hp": 120, "atk": 15, "speed": 8},
        "White Mage": {"hp": 70, "atk": 5, "speed": 10},
        "Black Mage": {"hp": 60, "atk": 20, "speed": 12},
    }

    def __init__(self, name, writer, is_ai=False):
        self.name = name                      # Player's name
        self.class_name = None               # Chosen class name
        self.currentHP = 0
        self.hp = 0                     # Stats derived from class
        self.atk = 0                     # Stats derived from class
        self.speed = 0                     # Stats derived from class
        self.ready = False                   # Readiness for battle
        self.writer = writer                 # Writer stream to communicate with client
        self.is_host = False                 # Host flag
        self.is_ai = is_ai                   # AI player flag
        self.type = "Player"

    def set_class(self, class_name):
        # Set player's class and corresponding stats
        self.class_name = class_name
        self.hp = self.CLASS_STATS[class_name]["hp"]
        self.atk = self.CLASS_STATS[class_name]["atk"]
        self.speed = self.CLASS_STATS[class_name]["speed"]

    def to_dict(self):
        # Return player data as a dictionary
        return {
            "name": self.name,
            "class": self.class_name,
            "ready": self.ready,
            "is_host": self.is_host,
            "is_ai": self.is_ai
        }