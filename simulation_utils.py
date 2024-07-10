# simulation_utils.py
import numpy as np

BLOAT_SLASH_DEF = 20
SALVE_MULTIPLIER = 1.20


def calc_total_damage(rng, count, max_damage, accuracy):
    hits = np.random.rand(count) < accuracy
    damage_values = np.random.randint(1, max_damage + 1, size=count)
    damage = np.sum(damage_values * hits)
    return damage
