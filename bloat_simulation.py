import numpy as np
from player_stats import PlayerStats
from combat import roll_scy, roll_bgs, roll_claw, calc_hit_chance, calc_max_hit
from simulation_utils import calc_total_damage, get_down_tick

BLOAT_SLASH_DEF = 20
SALVE_MULTIPLIER = 1.20


def main_simulation(trials, bgs_hits, half_salve_hits, neck_hits):
    rng = np.random.default_rng()
    successful_trials = 0
    low_num_trials = trials <= 100

    str_level = atk_level = 99
    bloat_hp = 1500
    scythe = PlayerStats(str_level, atk_level, 132, 147)
    bgs = PlayerStats(str_level, atk_level, 189, 154)
    claw = PlayerStats(str_level, atk_level, 113, 79)

    for _ in range(trials):
        claw_specs = 4
        total_dmg = 0
        bloat_def = 100
        down_tick = get_down_tick()
        bgs2_tick = bgs_hits[1]
        bgs3_tick = bgs_hits[2]
        bgs4_tick = bgs_hits[3]
        bonus_salve_hits = []

        bgs1 = roll_bgs(rng, bgs, bloat_def, BLOAT_SLASH_DEF, 1)
        bloat_def -= bgs1
        total_dmg += bgs1 // 2
        # Account for def regen
        bgs2 = roll_bgs(rng, bgs, (bloat_def + int(bgs2_tick * 0.2)), BLOAT_SLASH_DEF, 1)
        bloat_def -= bgs2
        total_dmg += bgs2 // 2
        if low_num_trials:
            print(f"BGS 1: {bgs1}\nBGS 2: {bgs2}")

        if bloat_def > 15:
            bgs3 = roll_bgs(rng, bgs, (bloat_def + int(bgs3_tick * 0.2)), BLOAT_SLASH_DEF, 1)
            bloat_def -= bgs3
            total_dmg += bgs3 // 2
            claw_specs -= 1
            if low_num_trials:
                print(f"BGS 3: {bgs3}")
        # Change the 3rd bgs to a salve hit if low def
        else:
            bonus_salve_hits.append(bgs_hits[2])
            print(f"Added {bgs_hits[2]} to bonus_salve_hits")

        if bloat_def > 15:
            bgs4 = roll_bgs(rng, bgs, (bloat_def + int(bgs4_tick * 0.2)), BLOAT_SLASH_DEF, 1)
            bloat_def -= bgs4
            total_dmg += bgs4 // 2
            claw_specs -= 1
            if low_num_trials:
                print(f"BGS 4: {bgs4}")
        # Change the 4th bgs to a salve hit if low def
        else:
            bonus_salve_hits.append(bgs_hits[3])
            print(f"Added {bgs_hits[3]} to bonus_salve_hits")

        if bloat_def < 0:
            bloat_def = 0
        if low_num_trials:
            print(f"Bloat def: {bloat_def}")

        # Bloat regens 1 defence every 5 ticks, roll each scythe based on the tick/defence
        necking_damage = 0
        for tick in neck_hits:
            if tick < down_tick:
                necking_damage += roll_scy(scythe, (bloat_def + int(tick * 0.2)), BLOAT_SLASH_DEF, 0, 1, low_num_trials)

        half_salve_damage = 0
        for tick in half_salve_hits:
            if tick < down_tick:
                half_salve_damage += roll_scy(scythe, (bloat_def + int(tick * 0.2)), BLOAT_SLASH_DEF, 1, 1,
                                              low_num_trials)
        for tick in bonus_salve_hits:
            if tick < down_tick:
                half_salve_damage += roll_scy(scythe, (bloat_def + int(tick * 0.2)), BLOAT_SLASH_DEF, 1, 1,
                                              low_num_trials)

        # Find tick for the first 3 scythe swings, based on the last 3 neck hits
        salve_hits = []
        salve_hits.append(neck_hits[-1] - down_tick)
        salve_hits.append(neck_hits[-2] - down_tick)
        salve_hits.append(neck_hits[-3] - down_tick)

        # Add other hits to the array
        for tick in range(salve_hits[0] % 5, 32, 5):
            salve_hits.append(tick)
        for tick in range(salve_hits[1] % 5, 32, 5):
            salve_hits.append(tick)
        for tick in range(salve_hits[2] % 5, 32, 5):
            salve_hits.append(tick)
        # Delete the first 3 (duplicates)
        del salve_hits[:3]

        bloat_def += int(down_tick * 0.2)
        salve_damage = 0
        for tick in salve_hits:
            salve_damage += roll_scy(scythe, (bloat_def + int(tick * 0.2)), BLOAT_SLASH_DEF, 1, 0,
                                     low_num_trials)

        claw_damage = np.sum(
            [roll_claw(rng, claw, bloat_def, BLOAT_SLASH_DEF, low_num_trials) for _ in range(claw_specs)])

        total_dmg += necking_damage + half_salve_damage + salve_damage + claw_damage

        if total_dmg >= bloat_hp:
            successful_trials += 1
        if low_num_trials:
            print(f"Down tick: {down_tick}")
            print(f"BGS ticks: {bgs_hits}")
            print(f"Necking scythes: {neck_hits}")
            print(f"Half damage salve hits: {half_salve_hits} + {bonus_salve_hits}")
            print(f"Salve scythes post down: {salve_hits}")
            print(f"Claw damage: {claw_damage}")
            print(f"Total damage: {total_dmg}\n{'-' * 52}")

    probability = successful_trials / trials * 100

    print(f"1D Chance: {probability:.2f}%")

    return probability
