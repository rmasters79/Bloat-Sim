# gui.py
import tkinter as tk
from tkinter import ttk, messagebox
from bloat_simulation import main_simulation


class BloatSimGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Bloat Simulation")
        self.setup_widgets()

    def setup_widgets(self):
        # Create and place widgets
        ttk.Label(self.root, text="Number of Trials:").grid(column=0, row=0, padx=10, pady=5, sticky=tk.W)
        self.trials_entry = ttk.Entry(self.root)
        self.trials_entry.grid(column=1, row=0, padx=10, pady=5)

        self.run_button = ttk.Button(self.root, text="Run Simulation", command=self.run_simulation)
        self.run_button.grid(column=0, row=1, columnspan=2, padx=10, pady=5)

        self.result_label = ttk.Label(self.root, text="")
        self.result_label.grid(column=0, row=2, columnspan=2, padx=10, pady=5)

    def run_simulation(self):
        try:
            trials = int(self.trials_entry.get())
            if trials <= 0:
                raise ValueError("Number of trials must be positive.")

            probability = main_simulation(trials)
            self.result_label.config(text=f"1D Chance: {probability:.2f}%")

        except ValueError as e:
            messagebox.showerror("Input Error", str(e))
