# Represents a player or AI participant in the game
class Player:
    def __init__(self, name, writer, is_ai=False):
        self.name = name                      # Player's name
        self.class_name = None               # Chosen class name
        self.stats = {}                      # Stats derived from class
        self.ready = False                   # Readiness for battle
        self.writer = writer                 # Writer stream to communicate with client
        self.is_host = False                 # Host flag
        self.is_ai = is_ai                   # AI player flag

    def set_class(self, class_name):
        # Set player's class and corresponding stats
        if class_name in CLASS_STATS:
            self.class_name = class_name
            self.stats = CLASS_STATS[class_name]

    def to_dict(self):
        # Return player data as a dictionary
        return {
            "name": self.name,
            "class": self.class_name,
            "ready": self.ready,
            "is_host": self.is_host,
            "is_ai": self.is_ai
        }