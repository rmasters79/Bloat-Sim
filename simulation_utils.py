# simulation_utils.py
import numpy as np

BLOAT_SLASH_DEF = 20
SALVE_MULTIPLIER = 1.20


def calc_total_damage(rng, count, max_damage, accuracy):
    hits = np.random.rand(count) < accuracy
    damage_values = np.random.randint(1, max_damage + 1, size=count)
    damage = np.sum(damage_values * hits)
    return damage


def get_down_tick():
    down_tick = 38
    bloat_walking = True

    # Minimum down tick = 39, maximum = 47
    # 1/4 chance on each tick to go down (not including turns)
    while bloat_walking:
        down_tick += 1
        if np.random.uniform(0, 1) < 0.25 or down_tick == 47:
            bloat_walking = False

    return down_tick
