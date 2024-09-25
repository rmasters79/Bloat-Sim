# combat.py
import numpy as np
from player_stats import PlayerStats

BLOAT_SLASH_DEF = 20
SALVE_MULTIPLIER = 1.20


def calc_max_hit(player):
    mel_boost = 19
    str_prayer_boost = 1.23
    effective_strength = (player.str_level + mel_boost) * str_prayer_boost + 3 + 8
    max_hit = ((effective_strength * (player.str_bonus + 64)) + 320) // 640
    return int(max_hit)


def calc_attack_roll(player, salve):
    mel_boost = 19
    atk_prayer_boost = 1.20
    effective_attack = int((player.atk_level + mel_boost) * atk_prayer_boost + 8)
    attack_roll = int(effective_attack * (player.acc_bonus + 64))
    if salve:
        attack_roll *= 1.2
    return int(attack_roll)


def calc_defence_roll(def_level, def_bonus):
    return (def_level + 9) * (def_bonus + 64)


def calc_hit_chance(player, def_level, def_bonus, salve):
    defence_roll = calc_defence_roll(def_level, def_bonus)
    attack_roll = calc_attack_roll(player, salve)
    if attack_roll > defence_roll:
        hit_chance = 1 - ((defence_roll + 2) / (2 * (attack_roll + 1)))
    else:
        hit_chance = attack_roll / (2 * (defence_roll + 1))
    return hit_chance


def roll_scy(scy, def_level, def_bonus, salve, bloat_walking, print_hits=False):
    accuracy = calc_hit_chance(scy, def_level, def_bonus, salve)
    if salve:
        max1 = int(calc_max_hit(scy) * SALVE_MULTIPLIER)
    else:
        max1 = calc_max_hit(scy)
    if bloat_walking:
        max1 = max1 // 2
    max2 = max1 // 2
    max3 = max2 // 2

    # Roll each hit
    if np.random.rand() > accuracy:
        hit1 = 0
    else:
        hit1 = np.random.randint(0, max1)
    if np.random.rand() > accuracy:
        hit2 = 0
    else:
        hit2 = np.random.randint(0, max2)
    if np.random.rand() > accuracy:
        hit3 = 0
    else:
        hit3 = np.random.randint(0, max3)

    total = hit1 + hit2 + hit3
    if print_hits:
        print(f"Scy: {hit1}-{hit2}-{hit3} ({total})")
    return total


def roll_bgs(rng, bgs, def_level, def_bonus, salve):
    accuracy = calc_hit_chance(bgs, def_level, def_bonus, salve)
    if np.random.rand() > accuracy * 2:
        return 0
    else:
        bgs_max = int(calc_max_hit(bgs) * SALVE_MULTIPLIER * 1.21)
        return np.random.randint(0, bgs_max)


def roll_claw(rng, claw, def_level, def_bonus, print_specs=False):
    max_hit = int(calc_max_hit(claw) * SALVE_MULTIPLIER)
    accuracy = calc_hit_chance(claw, def_level, def_bonus, 1)
    hits = []

    for _ in range(4):
        if np.random.rand() < accuracy:
            if len(hits) == 0:
                min_hit = max_hit // 2
                temp_max_hit = max_hit - 1
                hits.append(np.random.randint(min_hit, max_hit))
            elif len(hits) == 1:
                hits.append(hits[0] // 2)
            elif len(hits) == 2:
                hits.append(hits[1] // 2)
            else:
                hits.append(hits[2] + 1)
        else:
            hits.append(0)

    if sum(hits[:2]) == 0:
        min_hit = int(0.25 * max_hit)
        temp_max_hit = int(0.75 * max_hit)
        hits[2] = np.random.randint(min_hit, temp_max_hit)
        hits[3] = hits[2] + 1
    elif hits[0] == 0:
        min_hit = int(0.375 * max_hit)
        temp_max_hit = int(0.875 * max_hit)
        hits[1] = np.random.randint(min_hit, temp_max_hit)
        hits[2] = hits[1] // 2
        hits[3] = hits[2] + 1

    damage = sum(hits)
    if print_specs:
        print(f"Claw Spec: {'-'.join(map(str, hits))} ({damage})")
    return damage
