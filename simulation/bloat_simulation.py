import numpy as np
import logging
from .player_stats import PlayerStats
from .combat import roll_scy, roll_bgs, roll_claw, calc_hit_chance, calc_max_hit
from .simulation_utils import calc_total_damage, get_down_tick
from .simulation_input import SimulationInput

# Initial branch commit
BLOAT_SLASH_DEF = 20
SALVE_MULTIPLIER = 1.20

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG, filename="../simulation.log", filemode="w",
                    format="%(levelname)s - %(message)s")
# Suppress Pillow's internal debug logs
logging.getLogger("PIL").setLevel(logging.WARNING)


def main_simulation(sim_input: SimulationInput) -> float:
    trials = sim_input.trials
    bgs_hits = sim_input.bgs_hits
    backup_bgs_hits = sim_input.backup_bgs_hits
    half_salve_hits = sim_input.half_salve_hits
    neck_hits = sim_input.neck_hits

    all_bgs_hits = []
    for player, tick_list in bgs_hits.items():
        for tick in tick_list:
            all_bgs_hits.append(tick)
    all_bgs_hits = sorted(all_bgs_hits)
    all_backup_bgs_hits = []
    for player, tick_list in backup_bgs_hits.items():
        for tick in tick_list:
            all_backup_bgs_hits.append(tick)
    all_backup_bgs_hits = sorted(all_backup_bgs_hits)
    first_bgs_tick = all_bgs_hits[0]

    rng = np.random.default_rng()
    successful_trials = 0

    str_level = atk_level = 99
    bloat_hp = 1500
    def_threshold = 15
    scythe = PlayerStats(str_level, atk_level, 132, 147)
    bgs = PlayerStats(str_level, atk_level, 189, 154)
    claw = PlayerStats(str_level, atk_level, 113, 79)

    for _ in range(trials):
        claw_specs = 6
        total_dmg = 0
        bloat_def = 100
        min_bgs = (bloat_def - def_threshold) // 2
        down_tick = get_down_tick()
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

        bgs_damage = 0
        for tick in all_bgs_hits:
            def_gained = int((tick - first_bgs_tick) * 0.2)
            current_bloat_def = bloat_def + def_gained
            bgs_roll = roll_bgs(rng, bgs, current_bloat_def, BLOAT_SLASH_DEF, 1)
            damage = bgs_roll // 2
            logger.debug(f"[BGS] Tick: {tick} Damage: {damage}")
            bloat_def = max(bloat_def - bgs_roll, 0)
            bgs_damage += damage
            claw_specs -= 1
        for tick in all_backup_bgs_hits:
            if bgs_damage < min_bgs:
                def_gained = int((tick - first_bgs_tick) * 0.2)
                current_bloat_def = bloat_def + def_gained
                bgs_roll = roll_bgs(rng, bgs, current_bloat_def, BLOAT_SLASH_DEF, 1)
                damage = bgs_roll // 2
                logger.debug(f"[BGS] Tick: {tick} Damage: {damage}")
                bloat_def = max(bloat_def - bgs_roll, 0)
                bgs_damage += damage
                claw_specs -= 1
            else:
                bonus_salve_hits.append(tick)
        logger.debug(f"Bloat def: {bloat_def}")

        half_salve_damage = 0
        for tick in bonus_salve_hits:
            if tick < down_tick:
                damage = roll_scy(scythe, (bloat_def + int(tick * 0.2)), BLOAT_SLASH_DEF, 1, 1)
                logger.debug(f"[Bonus 1/2 Salve] Tick: {tick} Damage: {damage}")
                half_salve_damage += damage

        # Bloat regens 1 defence every 5 ticks, roll each scythe based on the tick/defence
        necking_damage = 0
        for player, tick_list in neck_hits.items():  # Iterate over rows
            for tick in tick_list:  # Iterate over tick values in each row
                if tick < down_tick:
                    damage = roll_scy(scythe, (bloat_def + int(tick * 0.2)), BLOAT_SLASH_DEF, 0, 1)
                    logger.debug(f"[PNeck] Player: {player + 1} Tick: {tick} Damage: {damage}")
                    necking_damage += damage

        for player, tick_list in half_salve_hits.items():  # Iterate over rows
            for tick in tick_list:
                if tick < down_tick:
                    damage = roll_scy(scythe, (bloat_def + int(tick * 0.2)), BLOAT_SLASH_DEF, 1, 1)
                    logger.debug(f"[1/2 Damage Salve] Player: {player + 1} Tick: {tick} Damage: {damage}")
                    half_salve_damage += damage

        bloat_def += int(down_tick * 0.2)
        salve_damage = 0
        for player, tick_list in salve_hits.items():  # Iterate over rows
            for tick in tick_list:
                damage = roll_scy(scythe, (bloat_def + int(tick * 0.2)), BLOAT_SLASH_DEF, 1, 0)
                logger.debug(f"[Full Damage Salve] Player: {player + 1} Tick: {tick} Damage: {damage}")
                salve_damage += damage

        claw_damage = 0
        for _ in range(claw_specs):
            damage = roll_claw(claw, bloat_def, BLOAT_SLASH_DEF)
            logger.debug(f"[Claw Spec] Damage: {damage}")
            claw_damage += damage

        total_dmg += bgs_damage + necking_damage + half_salve_damage + salve_damage + claw_damage

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
