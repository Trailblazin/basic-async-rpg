def get_unused_classes(self):
    # Return class options that haven't been taken yet
    return [cls for cls in CLASS_STATS if cls not in [p.class_name for p in self.players if p.class_name]]