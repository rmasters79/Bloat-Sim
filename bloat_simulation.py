import numpy as np
import logging
from player_stats import PlayerStats
from combat import roll_scy, roll_bgs, roll_claw, calc_hit_chance, calc_max_hit
from simulation_utils import calc_total_damage, get_down_tick
from simulation_input import SimulationInput


BLOAT_SLASH_DEF = 20
SALVE_MULTIPLIER = 1.20

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.WARNING, filename="simulation.log", filemode="w",
                    format="%(levelname)s - %(message)s")
# Suppress Pillow's internal debug logs
logging.getLogger("PIL").setLevel(logging.WARNING)


def main_simulation(sim_input: SimulationInput) -> float:
    trials = sim_input.trials
    bgs_hits = sim_input.bgs_hits
    half_salve_hits = sim_input.half_salve_hits
    neck_hits = sim_input.neck_hits

    rng = np.random.default_rng()
    successful_trials = 0

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
        logger.debug(f"BGS 1:  {bgs1}")
        bloat_def -= bgs1
        total_dmg += bgs1 // 2
        # Account for def regen
        bgs2 = roll_bgs(rng, bgs, (bloat_def + int(bgs2_tick * 0.2)), BLOAT_SLASH_DEF, 1)
        logger.debug(f"BGS 2:  {bgs2}")
        bloat_def -= bgs2
        total_dmg += bgs2 // 2

        if bloat_def > 15:
            bgs3 = roll_bgs(rng, bgs, (bloat_def + int(bgs3_tick * 0.2)), BLOAT_SLASH_DEF, 1)
            logger.debug(f"BGS 3:  {bgs3}")
            bloat_def -= bgs3
            total_dmg += bgs3 // 2
            claw_specs -= 1
        # Change the 3rd bgs to a salve hit if low def
        else:
            bonus_salve_hits.append(all_bgs_hits[2])

        if bloat_def > 15:
            bgs4 = roll_bgs(rng, bgs, (bloat_def + int(bgs4_tick * 0.2)), BLOAT_SLASH_DEF, 1)
            logger.debug(f"BGS 4:  {bgs4}")
            bloat_def -= bgs4
            total_dmg += bgs4 // 2
            claw_specs -= 1
        # Change the 4th bgs to a salve hit if low def
        else:
            bonus_salve_hits.append(all_bgs_hits[3])

        if bloat_def < 0:
            bloat_def = 0
        logger.debug(f"Bloat def: {bloat_def}")

        # Bloat regens 1 defence every 5 ticks, roll each scythe based on the tick/defence
        necking_damage = 0
        for player, tick_list in neck_hits.items():  # Iterate over rows
            for tick in tick_list:  # Iterate over tick values in each row
                if tick < down_tick:
                    damage = roll_scy(scythe, (bloat_def + int(tick * 0.2)), BLOAT_SLASH_DEF, 0, 1)
                    logger.debug(f"Player: {player + 1} Tick: {tick} Damage: {damage} (PNeck)")
                    necking_damage += damage

        half_salve_damage = 0
        for player, tick_list in half_salve_hits.items():  # Iterate over rows
            for tick in tick_list:
                if tick < down_tick:
                    damage = roll_scy(scythe, (bloat_def + int(tick * 0.2)), BLOAT_SLASH_DEF, 1, 1)
                    logger.debug(f"Player: {player + 1} Tick: {tick} Damage: {damage} (1/2 Salve)")
                    half_salve_damage += damage
        for tick in bonus_salve_hits:
            if tick < down_tick:
                damage = roll_scy(scythe, (bloat_def + int(tick * 0.2)), BLOAT_SLASH_DEF, 1, 1)
                logger.debug(f"Tick: {tick} Damage: {damage} (Bonus 1/2 Salve)")
                half_salve_damage += damage

        bloat_def += int(down_tick * 0.2)
        salve_damage = 0
        for player, tick_list in salve_hits.items():  # Iterate over rows
            for tick in tick_list:
                damage = roll_scy(scythe, (bloat_def + int(tick * 0.2)), BLOAT_SLASH_DEF, 1, 0)
                logger.debug(f"Player: {player + 1} Tick: {tick} Damage: {damage} (Salve)")
                salve_damage += damage

        claw_damage = 0
        for _ in range(claw_specs):
            damage = roll_claw(claw, bloat_def, BLOAT_SLASH_DEF)
            logger.debug(f"Claw Spec Damage: {damage}")
            claw_damage += damage

        total_dmg += necking_damage + half_salve_damage + salve_damage + claw_damage

        if total_dmg >= bloat_hp:
            successful_trials += 1

        logger.info(f"Down tick: {down_tick}")
        logger.info(f"BGS ticks: {bgs_hits}")
        logger.info(f"Necking scythes: {neck_hits}")
        logger.info(f"Half damage salve hits: {half_salve_hits} + {bonus_salve_hits}")
        logger.info(f"Salve scythes post down: {salve_hits}")
        logger.info(f"Claw damage: {claw_damage}")
        logger.info(f"Total damage: {total_dmg}\n{'-' * 52}")

    probability = successful_trials / trials * 100
    logger.info(f"1D Chance: {probability:.2f}%")

    return probability
