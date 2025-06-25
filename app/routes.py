from flask import Blueprint, render_template, request
from simulation.bloat_simulation import main_simulation
from simulation.simulation_input import SimulationInput

main = Blueprint('main', __name__)


@main.route('/', methods=['GET', 'POST'])
def index():
    result = None
    if request.method == 'POST':
        try:
            trials = int(request.form['trials'])
            # Replace this mock input with data from your form later
            sim_input = SimulationInput(
                trials=trials,
                bgs_hits={0: [2], 1: [9]},
                backup_bgs_hits={0: [7], 1: [15]},
                half_salve_hits={0: [16, 21],
                                 1: [16, 21],
                                 2: [6, 11]},
                neck_hits={0: [26, 31, 36, 41, 46],
                           1: [26, 31, 36, 41, 46],
                           2: [16, 21, 26, 31, 36, 41, 46]}
            )
            odds = main_simulation(sim_input)
            result = f"1D Chance: {odds:.2f}%"
        except Exception as e:
            result = f"Error: {str(e)}"
    return render_template("index.html", result=result)
