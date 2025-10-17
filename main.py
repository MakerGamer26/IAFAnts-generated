import tkinter as tk
from tkinter import ttk
from simulation import Simulation
from models import CellType, Explorer, Fighter, Collector

# --- Default Configuration ---
DEFAULT_CONFIG = {
    "grid_width": 20,
    "grid_height": 20,
    "map": [
        "NNW................F",
        ".NW................F",
        ".W........DD......F.",
        "....................",
        "....................",
        "....................",
        "....................",
        "....................",
        "....................",
        "....................",
        "....................",
        "....................",
        "....................",
        "....................",
        "....................",
        "....................",
        "....................",
        "F...................",
        "F...................",
        "F...................",
    ],
    "food_quantities": {
        (19, 0): 20000, (19, 1): 20000, (19, 2): 20000,
        (0, 17): 1000, (0, 18): 1000, (0, 19): 1000,
    },
    "max_time": 100000,
    "nest": {
        "ants": {
            "Explorer": 2,
            "Fighter": 1,
            "Collector": 3,
        }
    },
    "q_learning": {
        "learning_rate": 0.1,
        "discount_factor": 0.9,
        "epsilon": 0.1,
    },
    "pheromones": {
        "dissipation_rate": 0.01,
        "food_reward": 1000,
        "nest_reward": 1000,
        "deadly_reward": -500,
        "move_reward": -1,
    }
}

class App(tk.Tk):
    """Main application class for the AI-Fants simulation."""
    def __init__(self, config):
        super().__init__()
        self.title("AI-Fants Simulation")
        self.config = config
        self.cell_size = 25
        self.is_running = False

        self.simulation = Simulation(self.config)

        # --- UI Elements ---
        self.canvas = tk.Canvas(
            self,
            width=self.config["grid_width"] * self.cell_size,
            height=self.config["grid_height"] * self.cell_size,
            bg="white"
        )
        self.canvas.pack(pady=10, padx=10)

        controls_frame = tk.Frame(self)
        controls_frame.pack(pady=5)

        self.start_button = tk.Button(controls_frame, text="Start", command=self.start_simulation)
        self.start_button.pack(side=tk.LEFT, padx=5)

        self.pause_button = tk.Button(controls_frame, text="Pause", command=self.pause_simulation, state=tk.DISABLED)
        self.pause_button.pack(side=tk.LEFT, padx=5)

        self.reset_button = tk.Button(controls_frame, text="Reset", command=self.reset_simulation)
        self.reset_button.pack(side=tk.LEFT, padx=5)

        # --- Time Slider ---
        slider_frame = tk.Frame(self)
        slider_frame.pack(fill=tk.X, padx=10, pady=5)
        self.time_label = tk.Label(slider_frame, text="Time: 0")
        self.time_label.pack(side=tk.LEFT)
        self.time_slider = ttk.Scale(slider_frame, from_=0, to=0, orient=tk.HORIZONTAL, command=self.on_slider_move)
        self.time_slider.pack(fill=tk.X, expand=True, padx=5)

        # --- Pheromone View ---
        view_frame = tk.Frame(self)
        view_frame.pack(pady=5)
        self.pheromone_view_var = tk.StringVar(value="none")
        tk.Label(view_frame, text="Pheromone View:").pack(side=tk.LEFT)
        tk.Radiobutton(view_frame, text="None", variable=self.pheromone_view_var, value="none", command=self.draw_world).pack(side=tk.LEFT)
        tk.Radiobutton(view_frame, text="Food", variable=self.pheromone_view_var, value="food", command=self.draw_world).pack(side=tk.LEFT)
        tk.Radiobutton(view_frame, text="Nest", variable=self.pheromone_view_var, value="nest", command=self.draw_world).pack(side=tk.LEFT)

        # --- Initial Draw ---
        self.draw_world()

    def on_slider_move(self, value):
        """Callback for when the time slider is moved."""
        if self.simulation.history:
            time_step = int(float(value))
            self.draw_world(time_step)
            self.time_label.config(text=f"Time: {time_step}")

    def start_simulation(self):
        """Starts or resumes the simulation."""
        self.is_running = True
        self.start_button.config(state=tk.DISABLED)
        self.pause_button.config(state=tk.NORMAL)
        self.update_loop()

    def pause_simulation(self):
        """Pauses the simulation."""
        self.is_running = False
        self.start_button.config(state=tk.NORMAL)
        self.pause_button.config(state=tk.DISABLED)

    def reset_simulation(self):
        """Resets the simulation to its initial state."""
        self.is_running = False
        self.simulation = Simulation(self.config)
        self.start_button.config(state=tk.NORMAL)
        self.pause_button.config(state=tk.DISABLED)
        self.draw_world()

    def update_loop(self):
        """Main loop to update and redraw the simulation."""
        if not self.is_running:
            return

        self.simulation.run_step()
        self.time_slider.config(to=self.simulation.time)
        self.time_slider.set(self.simulation.time)
        self.time_label.config(text=f"Time: {self.simulation.time}")
        self.draw_world()

        if self.simulation.is_finished():
            self.pause_simulation()
            print(f"Simulation finished at time {self.simulation.time}.")
        else:
            self.after(50, self.update_loop) # Update every 50ms

    def draw_world(self, time_step=None):
        """Draws the entire simulation state on the canvas."""
        self.canvas.delete("all")

        state = None
        if time_step is not None and time_step < len(self.simulation.history):
            state = self.simulation.history[time_step]

        self._draw_pheromones(time_step)
        self._draw_grid()
        self._draw_ants(state)

    def _draw_pheromones(self, time_step=None):
        """Draws the pheromone trails on the canvas."""
        view = self.pheromone_view_var.get()
        if view == "none":
            return

        # Note: For simplicity, this visualizes the *current* pheromone state,
        # not the historical state, as storing pheromone history is memory-intensive.
        q_table = self.simulation.pheromone_grid.food_q_table if view == "food" else self.simulation.pheromone_grid.nest_q_table

        max_pheromone = 0.001 # Avoid division by zero
        for y in range(self.simulation.grid.height):
            for x in range(self.simulation.grid.width):
                max_pheromone = max(max_pheromone, max(q_table[y][x]))

        for y in range(self.simulation.grid.height):
            for x in range(self.simulation.grid.width):
                q_values = q_table[y][x]
                if sum(q_values) > 0:
                    intensity = int((max(q_values) / max_pheromone) * 255)
                    color = f'#ff{255-intensity:02x}{255-intensity:02x}' # Heatmap (red)
                    if view == "nest":
                        color = f'#{255-intensity:02x}{255-intensity:02x}ff' # Heatmap (blue)

                    x1, y1 = x * self.cell_size, y * self.cell_size
                    x2, y2 = x1 + self.cell_size, y1 + self.cell_size
                    self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="")

    def _draw_grid(self):
        """Draws the grid cells (walls, food, nest, etc.)."""
        colors = {
            CellType.WALL: "black",
            CellType.FOOD: "green",
            CellType.NEST: "blue",
            CellType.DEADLY: "red",
        }
        for y in range(self.simulation.grid.height):
            for x in range(self.simulation.grid.width):
                cell_type = self.simulation.grid.grid[y][x]
                if cell_type != CellType.EMPTY:
                    x1 = x * self.cell_size
                    y1 = y * self.cell_size
                    x2 = x1 + self.cell_size
                    y2 = y1 + self.cell_size
                    self.canvas.create_rectangle(x1, y1, x2, y2, fill=colors[cell_type], outline="")

    def _draw_ants(self, state=None):
        """Draws the ants on the canvas."""
        ant_colors = {
            "Explorer": "orange",
            "Fighter": "purple",
            "Collector": "brown",
        }

        ants_to_draw = self.simulation.ants if state is None else state["ants"]

        for ant_data in ants_to_draw:
            x = ant_data['x'] if isinstance(ant_data, dict) else ant_data.x
            y = ant_data['y'] if isinstance(ant_data, dict) else ant_data.y
            ant_type_name = ant_data['type'] if isinstance(ant_data, dict) else type(ant_data).__name__

            x1 = x * self.cell_size + self.cell_size / 4
            y1 = y * self.cell_size + self.cell_size / 4
            x2 = x1 + self.cell_size / 2
            y2 = y1 + self.cell_size / 2
            self.canvas.create_oval(x1, y1, x2, y2, fill=ant_colors[ant_type_name], outline="black")

if __name__ == "__main__":
    app = App(DEFAULT_CONFIG)
    app.mainloop()