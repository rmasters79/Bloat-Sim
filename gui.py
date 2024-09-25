import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
from bloat_simulation import main_simulation


class ImageGrid:
    def __init__(self, root):
        self.root = root
        self.root.title("Dynamic Image Grid")

        # Frame for row input
        self.input_frame = tk.Frame(self.root)
        self.input_frame.pack(pady=10)

        # Label and entry for number of rows
        self.row_label = tk.Label(self.input_frame, text="Enter number of players:")
        self.row_label.pack(side=tk.LEFT)

        self.row_entry = tk.Entry(self.input_frame, width=5)
        self.row_entry.pack(side=tk.LEFT)

        # Button to create grid
        self.create_button = tk.Button(self.input_frame, text="Create Grid", command=self.create_grid)
        self.create_button.pack(side=tk.LEFT, padx=5)

        # Frame for the grid and result
        self.grid_frame = tk.Frame(self.root)
        self.result_frame = tk.Frame(self.root)

        # Label and entry for number of trials
        self.trials_label = tk.Label(self.result_frame, text="Enter number of trials:")
        self.trials_label.pack(side=tk.TOP)

        self.trials_entry = tk.Entry(self.result_frame, width=10)
        self.trials_entry.pack(side=tk.TOP)

        # Button and label for displaying the results
        self.result_button = tk.Button(self.result_frame, text="Run Simulation",
                                       command=self.run_simulation)
        self.result_label = tk.Label(self.result_frame, text="")

        # Load images with different names
        self.images = {
            "Empty tick": self.load_and_resize_image("icons/Empty tick.png"),
            "Salve hit": self.load_and_resize_image("icons/Salve amulet (e).png"),
            "Neck hit": self.load_and_resize_image("icons/Phoenix necklace.png"),
            "BGS hit": self.load_and_resize_image("icons/Bandos godsword.png"),
        }

        # Prepare arrays for each image
        self.image_arrays = {key: [] for key in self.images}

        # Dictionary to track which image is selected for each button (by row and column)
        self.selected_images = {}

    def load_and_resize_image(self, file_path, size=(20, 20)):
        image = Image.open(file_path)
        image = image.resize(size, Image.Resampling.LANCZOS)
        return ImageTk.PhotoImage(image)

    def create_grid(self):
        # Clear any existing grid
        for widget in self.grid_frame.winfo_children():
            widget.destroy()

        self.grid_frame.pack_forget()
        self.result_frame.pack_forget()

        # Get the number of rows from the entry
        try:
            self.num_rows = int(self.row_entry.get())
            if self.num_rows < 1:
                raise ValueError
        except ValueError:
            self.result_label.config(text="Please enter a valid number of players.")
            return

        # Initialize buttons and arrays
        self.buttons = [[None for _ in range(52)] for _ in range(self.num_rows)]
        self.selected_squares = []

        # Create column labels
        for col in range(52):
            col_label = tk.Label(self.grid_frame, text=str(col + 1))
            col_label.grid(row=0, column=col + 1, padx=2)

        # Create grid with dynamic number of rows
        for row in range(self.num_rows):
            player_label = tk.Label(self.grid_frame, text=f"Player {row + 1}:")
            player_label.grid(row=row + 1, column=0, padx=5, pady=2)

            for col in range(52):
                button = tk.Button(self.grid_frame, image=self.images["Empty tick"],
                                   command=lambda r=row, c=col: self.toggle_image(r, c),
                                   padx=0, pady=0)
                button.grid(row=row + 1, column=col + 1, padx=1, pady=1)
                self.buttons[row][col] = button

        self.grid_frame.pack(padx=10, pady=10)
        self.result_frame.pack(pady=10)
        self.result_button.pack(side=tk.TOP)
        self.result_label.pack(side=tk.TOP)

    def toggle_image(self, row, col):
        button = self.buttons[row][col]
        current_image = button.cget("image")

        # Determine the next image
        image_keys = list(self.images.keys())
        if not current_image or current_image == str(self.images[image_keys[-1]]):
            new_image_key = image_keys[0]
        else:
            current_index = image_keys.index(next(key for key in image_keys if str(self.images[key]) == current_image))
            new_image_key = image_keys[(current_index + 1) % len(image_keys)]

        # Update the button with the new image
        new_image = self.images[new_image_key]
        button.config(image=new_image)
        button.image = new_image  # Keep a reference to avoid garbage collection

        # Track the selected image for this cell (row, col)
        self.selected_images[(row, col)] = new_image_key  # Track the newly selected image for this row/col

    def run_simulation(self):
        # Clear arrays for each image before rebuilding
        self.image_arrays = {key: [] for key in self.images}

        # Iterate through selected images and populate arrays
        for (row, col), image_key in self.selected_images.items():
            self.image_arrays[image_key].append(col + 1)  # Add column number (1-indexed)

        # Display results
        result_text = "\n".join([f"{label}: {columns}" for label, columns in self.image_arrays.items()])
        self.result_label.config(text=result_text)

        bgs_hit_ticks = sorted(self.image_arrays['BGS hit'])
        salve_hit_ticks = sorted(self.image_arrays['Salve hit'])
        neck_hit_ticks = sorted(self.image_arrays['Neck hit'])

        try:
            trials = int(self.trials_entry.get())
            if trials <= 0:
                raise ValueError("Number of trials must be positive.")

            probability = main_simulation(trials, bgs_hit_ticks, salve_hit_ticks, neck_hit_ticks)
            self.result_label.config(text=f"1D Chance: {probability:.2f}%")

        except ValueError as e:
            messagebox.showerror("Input Error", str(e))


if __name__ == "__main__":
    root = tk.Tk()
    app = ImageGrid(root)
    root.mainloop()

