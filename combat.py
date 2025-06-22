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


def roll_scy(scy, def_level, def_bonus, salve, bloat_walking):
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
    return total


def roll_bgs(rng, bgs, def_level, def_bonus, salve):
    accuracy = calc_hit_chance(bgs, def_level, def_bonus, salve)
    if np.random.rand() > accuracy * 2:
        return 0
    else:
        bgs_max = int(calc_max_hit(bgs) * SALVE_MULTIPLIER * 1.21)
        return np.random.randint(0, bgs_max)


def roll_claw(claw, def_level, def_bonus):
    max_hit = int(calc_max_hit(claw))
    accuracy = calc_hit_chance(claw, def_level, def_bonus, True)
    claw1 = claw2 = claw3 = claw4 = 0

    # First hit attempt
    if np.random.rand() < accuracy:
        # If the first attack hits, then its max hit will be 1 point less than the max hit of an ordinary attack. The
        # minimum hit will be half of the ordinary max hit
        min_hit = max_hit // 2
        claw1 = np.random.randint(min_hit, max_hit)  # Roll between min_hit and max_hit - 1
        claw2 = claw1 // 2
        claw3 = claw2 // 2
        claw4 = claw3 + 1

    # Second hit attempt
    elif np.random.rand() < accuracy:
        # If the first hit is 0 and the second one hits, then the second hit will deal between about 3/8 and 7/8 of
        # the ordinary maximum hit
        min_hit = int(0.375 * max_hit)
        temp_max_hit = int(0.875 * max_hit)
        claw2 = np.random.randint(min_hit, temp_max_hit + 1)
        claw3 = claw2 // 2
        claw4 = claw3 + 1

    # Third hit attempt
    elif np.random.rand() < accuracy:
        # If the first two attacks hit 0–0, the third attack will deal between about 1/4 and 3/4 of the ordinary max hit
        min_hit = int(0.25 * max_hit)
        temp_max_hit = int(0.75 * max_hit)
        claw3 = np.random.randint(min_hit, temp_max_hit + 1)  # Third hit roll
        claw4 = claw3 + 1

    # Fourth hit attempt
    elif np.random.rand() < accuracy:
        # If the claws' first 3 hits are zeros, the last hit (if successful) will deal between 0.25x and 1.25x
        # ordinary damage
        min_hit = int(0.25 * max_hit)
        temp_max_hit = int(1.25 * max_hit)
        claw4 = np.random.randint(min_hit, temp_max_hit + 1)  # Fourth hit roll

    # If all four attacks miss, there is a 50% chance of rolling 0-0-1-1 instead of 0-0-0-0
    elif np.random.rand() < 0.5:
        claw3, claw4 = 1, 1

    damage = claw1 + claw2 + claw3 + claw4
    return damage
