import random

class RNGPool:
    def __init__(self, pool_size=10, base_seed=None):
        self.pool_size = pool_size
        self.base_seed = base_seed or random.SystemRandom().randint(0, 2**32 - 1)
        self.rngs = [random.Random(self.base_seed + i) for i in range(pool_size)]
        # entity_id -> rng index 
        self.assignments = {}  # Chaos -> 0 for example


    def assign_rng(self, entity_id):
        if entity_id in self.assignments:
            return self.rngs[self.assignments[entity_id]]
        idx = len(self.assignments) % self.pool_size
        self.assignments[entity_id] = idx
        return self.rngs[idx]

    def get_rng(self, entity_id):
        return self.rngs[self.assignments[entity_id]]