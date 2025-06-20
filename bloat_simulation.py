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
        all_bgs_hits = [tick for ticks in bgs_hits.values() for tick in ticks]
        all_bgs_hits = sorted(all_bgs_hits)
        bgs2_tick = all_bgs_hits[1]
        bgs3_tick = all_bgs_hits[2]
        bgs4_tick = all_bgs_hits[3]
        bonus_salve_hits = []

        # Initialize salve_hits as a dictionary
        salve_hits = {}

        # Iterate through each key-value pair in neck_hits
        for player, tick_list in neck_hits.items():
            first_hit_tick = tick_list[-1] - down_tick
            salve_hit_ticks = []
            for tick in range(first_hit_tick % 5, 32, 5):
                salve_hit_ticks.append(tick)

            # Store the computed list in salve_hits
            salve_hits[player] = salve_hit_ticks

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
            bonus_salve_hits.append(all_bgs_hits[2])

        if bloat_def > 15:
            bgs4 = roll_bgs(rng, bgs, (bloat_def + int(bgs4_tick * 0.2)), BLOAT_SLASH_DEF, 1)
            bloat_def -= bgs4
            total_dmg += bgs4 // 2
            claw_specs -= 1
            if low_num_trials:
                print(f"BGS 4: {bgs4}")
        # Change the 4th bgs to a salve hit if low def
        else:
            bonus_salve_hits.append(all_bgs_hits[3])

        if bloat_def < 0:
            bloat_def = 0
        if low_num_trials:
            print(f"Bloat def: {bloat_def}")

        # Bloat regens 1 defence every 5 ticks, roll each scythe based on the tick/defence
        necking_damage = 0
        for player, tick_list in neck_hits.items():  # Iterate over rows
            for tick in tick_list:  # Iterate over tick values in each row
                if tick < down_tick:
                    if low_num_trials:
                        print(f"Player: {player + 1} Tick: {tick}")
                    necking_damage += roll_scy(scythe, (bloat_def + int(tick * 0.2)), BLOAT_SLASH_DEF, 0, 1,
                                               low_num_trials)

        half_salve_damage = 0
        for player, tick_list in half_salve_hits.items():  # Iterate over rows
            for tick in tick_list:
                if tick < down_tick:
                    if low_num_trials:
                        print(f"Player: {player + 1} Tick: {tick}")
                    half_salve_damage += roll_scy(scythe, (bloat_def + int(tick * 0.2)), BLOAT_SLASH_DEF, 1, 1,
                                                  low_num_trials)
        for tick in bonus_salve_hits:
            if tick < down_tick:
                half_salve_damage += roll_scy(scythe, (bloat_def + int(tick * 0.2)), BLOAT_SLASH_DEF, 1, 1,
                                              low_num_trials)

        bloat_def += int(down_tick * 0.2)
        salve_damage = 0
        for player, tick_list in salve_hits.items():  # Iterate over rows
            for tick in tick_list:
                if low_num_trials:
                    print(f"Player: {player + 1} Tick: {tick}")
                salve_damage += roll_scy(scythe, (bloat_def + int(tick * 0.2)), BLOAT_SLASH_DEF, 1, 0,
                                         low_num_trials)

        claw_damage = np.sum(
            [roll_claw(claw, bloat_def, BLOAT_SLASH_DEF, low_num_trials) for _ in range(claw_specs)])

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
