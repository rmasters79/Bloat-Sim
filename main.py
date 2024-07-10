# main.py
import tkinter as tk
from gui import BloatSimGUI

if __name__ == "__main__":
    root = tk.Tk()
    app = BloatSimGUI(root)
    root.mainloop()
