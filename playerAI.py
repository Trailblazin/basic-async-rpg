class AIPlayer(Player):
    def __init__(self, original_name,class_name, ai_name):
        super().__init__(ai_name, None, is_ai=True)
        self.type = "AI"
        self.original_name = original_name
        self.set_class(class_name)