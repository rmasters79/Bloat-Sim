import numpy as np
from player_stats import PlayerStats
from combat import roll_bgs, roll_claw, calc_hit_chance, calc_max_hit
from simulation_utils import calc_total_damage

BLOAT_SLASH_DEF = 20
SALVE_MULTIPLIER = 1.20


def main_simulation(trials):
    rng = np.random.default_rng()
    successful_trials = 0
    low_num_trials = trials <= 100

    str_level = atk_level = 99
    bloat_hp = 1500
    scythe = PlayerStats(str_level, atk_level, 132, 147)
    bgs = PlayerStats(str_level, atk_level, 189, 154)
    claw = PlayerStats(str_level, atk_level, 113, 79)

    neck_max1 = calc_max_hit(scythe) // 2
    neck_max2 = neck_max1 // 2
    neck_max3 = neck_max2 // 2
    neck_max = neck_max1 + neck_max2 + neck_max3
    salve_max1 = int(calc_max_hit(scythe) * SALVE_MULTIPLIER)
    salve_max2 = salve_max1 // 2
    salve_max3 = salve_max2 // 2
    salve_max = salve_max1 + salve_max2 + salve_max3
    half_salve_max1 = int((calc_max_hit(scythe) * SALVE_MULTIPLIER) // 2)
    half_salve_max2 = half_salve_max1 // 2
    half_salve_max3 = half_salve_max2 // 2
    half_salve_max = half_salve_max1 + half_salve_max2 + half_salve_max3
    bgs_max = int(calc_max_hit(bgs) * SALVE_MULTIPLIER)
    bgs_max = int(bgs_max * 1.21)
    half_bgs_max = bgs_max // 2

    for _ in range(trials):
        necking_hits = 16
        half_salve_hits = 2
        salve_hits = 20
        claw_specs = 4
        total_dmg = 0
        bloat_def = 100

        bgs1 = roll_bgs(rng, bgs, bloat_def, BLOAT_SLASH_DEF, 1)
        bloat_def -= bgs1
        total_dmg += bgs1 // 2
        bgs2 = roll_bgs(rng, bgs, bloat_def, BLOAT_SLASH_DEF, 1)
        bloat_def -= bgs2
        total_dmg += bgs2 // 2
        if low_num_trials:
            print(f"BGS 1: {bgs1}\nBGS 2: {bgs2}")

        if bloat_def > 15:
            bgs3 = roll_bgs(rng, bgs, bloat_def, BLOAT_SLASH_DEF, 1)
            bloat_def -= bgs3
            total_dmg += bgs3 // 2
            necking_hits -= 1
            claw_specs -= 1
            if low_num_trials:
                print(f"BGS 3: {bgs3}")

        if bloat_def > 15:
            bgs4 = roll_bgs(rng, bgs, bloat_def, BLOAT_SLASH_DEF, 1)
            bloat_def -= bgs4
            total_dmg += bgs4 // 2
            necking_hits -= 1
            claw_specs -= 1
            if low_num_trials:
                print(f"BGS 4: {bgs4}")

        if bloat_def < 0:
            bloat_def = 0
        if low_num_trials:
            print(f"Bloat def: {bloat_def}")

        salve_hits -= claw_specs
        claw_damage = np.sum(
            [roll_claw(rng, claw, bloat_def, BLOAT_SLASH_DEF, low_num_trials) for _ in range(claw_specs)])

        accuracy = calc_hit_chance(scythe, bloat_def, BLOAT_SLASH_DEF, 1)

        necking_damage = calc_total_damage(rng, necking_hits, neck_max, accuracy)
        half_salve_damage = calc_total_damage(rng, half_salve_hits, half_salve_max, accuracy)
        salve_damage = calc_total_damage(rng, salve_hits, salve_max, accuracy)

        total_dmg += necking_damage + half_salve_damage + salve_damage + claw_damage

        if total_dmg >= bloat_hp:
            successful_trials += 1
        if low_num_trials:
            print(f"Necking scythes: {necking_hits}")
            print(f"Salve flicks: {half_salve_hits}")
            print(f"Salve scythes post down: {salve_hits}")
            print(f"Claw damage: {claw_damage}")
            print(f"Total damage: {total_dmg}\n{'-' * 52}")

    probability = successful_trials / trials * 100

    print(f"{'-' * 20} 13-12-5 Trio {'-' * 20}")
    print(f"Bgs max (pre-down): {half_bgs_max}")
    print(f"Bgs max (post-down): {bgs_max}")
    print(f"Neck max (pre-down): {neck_max}")
    print(f"Pre-down salve max: {half_salve_max}\nSalve max: {salve_max}")
    print(f"1D Chance: {probability:.2f}%")

    return probability
