#TODO: AGAIN HERE, USE JUST CLASS NAMES BUD

CLASS_STATS = {
    "Thief": {"hp": 80, "atk": 10, "speed": 15},
    "Warrior": {"hp": 120, "atk": 15, "speed": 8},
    "White Mage": {"hp": 70, "atk": 5, "speed": 10},
    "Black Mage": {"hp": 60, "atk": 20, "speed": 12},
}

def get_unused_classes(players):
    # Return class options that haven't been taken yet
    
    return [cls for cls in CLASS_STATS if cls not in [p.class_name for p in players if p.class_name]]