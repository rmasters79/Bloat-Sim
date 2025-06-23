from dataclasses import dataclass
from typing import Dict, List


@dataclass
class SimulationInput:
    trials: int
    bgs_hits: Dict[int, List[int]]
    backup_bgs_hits: Dict[int, List[int]]
    half_salve_hits: Dict[int, List[int]]
    neck_hits: Dict[int, List[int]]
