import random
from models import Grid, PheromoneGrid, Ant, Explorer, Fighter, Collector, CellType, AntMode

class Simulation:
    """Manages the entire ant simulation."""

    def __init__(self, config):
        """Initializes the simulation with a given configuration."""
        self.config = config
        self.time = 0
        self.history = []

        # Setup the world
        self.grid = Grid(config["grid_width"], config["grid_height"])
        self.pheromone_grid = PheromoneGrid(config["grid_width"], config["grid_height"])
        self._setup_world_from_map(config["map"], config.get("food_quantities", {}))

        # Setup Q-learning
        self.q_learning = QLearning(self.grid, self.pheromone_grid)

        # Create ants
        self.ants = self._create_ants()
        self.nest = self.grid.nest_position # Assuming nest position is stored after setup

    def _setup_world_from_map(self, map_layout, food_quantities):
        """Configures the grid based on a map layout."""
        for y, row in enumerate(map_layout):
            for x, char in enumerate(row):
                if char == 'W':
                    self.grid.set_cell(x, y, CellType.WALL)
                elif char == 'N':
                    self.grid.set_cell(x, y, CellType.NEST)
                elif char == 'F':
                    quantity = food_quantities.get((x, y), 1000)
                    self.grid.set_cell(x, y, CellType.FOOD, quantity=quantity)
                elif char == 'D':
                    self.grid.set_cell(x, y, CellType.DEADLY)

    def _create_ants(self):
        """Creates the initial set of ants."""
        ants = []
        nest_x, nest_y = self.grid.nest_position
        q_params = self.config["q_learning"]

        ant_counts = self.config["nest"]["ants"]
        ant_classes = {"Explorer": Explorer, "Fighter": Fighter, "Collector": Collector}

        for name, count in ant_counts.items():
            for _ in range(count):
                ant = ant_classes[name](
                    nest_x, nest_y,
                    q_params["learning_rate"],
                    q_params["discount_factor"],
                    q_params["epsilon"]
                )
                ants.append(ant)
        return ants

    def run_step(self):
        """Runs a single time step of the simulation."""
        if self.is_finished():
            return

        # Process each ant
        ants_to_remove = []
        for ant in self.ants:
            ant.time_to_next_move -= 1
            if ant.time_to_next_move <= 0:
                self._process_ant_action(ant)
                ant.time_to_next_move = ant.speed # Reset timer
                if self.grid.grid[ant.y][ant.x] == CellType.DEADLY:
                    ants_to_remove.append(ant)

        # Remove dead ants
        for ant in ants_to_remove:
            self.ants.remove(ant)

        # Dissipate pheromones
        self._dissipate_pheromones()

        self.time += 1
        self._record_history()

    def _process_ant_action(self, ant):
        """Handles the logic for a single ant's action."""
        old_pos = (ant.x, ant.y)
        action_index = self.q_learning.choose_action(ant)
        action = self.q_learning.actions[action_index]

        new_x, new_y = ant.x + action[0], ant.y + action[1]
        new_pos = (new_x, new_y)

        reward = self._get_reward(new_pos, ant)
        self.q_learning.update_q_value(ant, old_pos, action_index, reward, new_pos)

        # Move ant
        ant.x, ant.y = new_x, new_y

        # Interact with the environment
        self._handle_environment_interaction(ant)

    def _get_reward(self, pos, ant):
        """Calculates the reward for moving to a new position."""
        x, y = pos
        cell = self.grid.grid[y][x]
        rewards = self.config["pheromones"]

        if cell == CellType.DEADLY:
            return rewards["deadly_reward"]
        if ant.mode == AntMode.SEARCHING_FOOD and cell == CellType.FOOD:
            return rewards["food_reward"]
        if ant.mode == AntMode.RETURNING_TO_NEST and cell == CellType.NEST:
            return rewards["nest_reward"]

        return rewards["move_reward"]

    def _handle_environment_interaction(self, ant):
        """Handles the ant's interaction with its current cell."""
        cell_type = self.grid.grid[ant.y][ant.x]

        if cell_type == CellType.FOOD and ant.mode == AntMode.SEARCHING_FOOD:
            # Pick up food
            food_source = next((fs for fs in self.grid.food_sources if fs.x == ant.x and fs.y == ant.y), None)
            if food_source and food_source.quantity > 0:
                pickup_amount = min(ant.max_load - ant.current_load, food_source.quantity)
                ant.current_load += pickup_amount
                food_source.quantity -= pickup_amount
                ant.switch_mode()

        elif cell_type == CellType.NEST and ant.mode == AntMode.RETURNING_TO_NEST:
            # Drop off food
            # For now, let's assume the Nest class will be developed further
            # self.nest.food_collected += ant.current_load
            ant.current_load = 0
            ant.switch_mode()


    def _dissipate_pheromones(self):
        """Reduces the intensity of all pheromones over time."""
        rate = self.config["pheromones"]["dissipation_rate"]
        for y in range(self.grid.height):
            for x in range(self.grid.width):
                for i in range(4):
                    self.pheromone_grid.food_q_table[y][x][i] *= (1 - rate)
                    self.pheromone_grid.nest_q_table[y][x][i] *= (1 - rate)

    def _record_history(self):
        """Saves the current state of the simulation for rewinding."""
        state = {
            "time": self.time,
            "ants": [{"x": a.x, "y": a.y, "type": type(a).__name__, "load": a.current_load} for a in self.ants],
            # To save space, we might not save pheromones every step or save them differently
            # "food_pheromones": [row[:] for row in self.pheromone_grid.food_q_table],
            # "nest_pheromones": [row[:] for row in self.pheromone_grid.nest_q_table],
        }
        self.history.append(state)

    def is_finished(self):
        """Checks if the simulation has ended."""
        total_food = sum(fs.initial_quantity for fs in self.grid.food_sources)
        # food_collected_at_nest = self.nest.food_collected
        # For now, check if sources are empty, as nest logic is simple
        food_remaining = sum(fs.quantity for fs in self.grid.food_sources)

        return self.time >= self.config["max_time"] or food_remaining <= 0


class QLearning:
    """Handles the Q-learning logic for an ant."""

    def __init__(self, grid, pheromone_grid):
        self.grid = grid
        self.pheromone_grid = pheromone_grid
        self.actions = [(0, -1), (1, 0), (0, 1), (-1, 0)]  # N, E, S, W

    def get_q_table(self, ant_mode):
        """Returns the appropriate Q-table based on the ant's mode."""
        if ant_mode == AntMode.SEARCHING_FOOD:
            return self.pheromone_grid.food_q_table
        else:
            return self.pheromone_grid.nest_q_table

    def choose_action(self, ant):
        """Chooses an action for the ant using an epsilon-greedy strategy."""
        if random.random() < ant.epsilon:
            # Explore: choose a random valid action
            possible_actions = self._get_valid_actions(ant.x, ant.y)
            return random.choice(possible_actions) if possible_actions else (0, 0)
        else:
            # Exploit: choose the best action from the Q-table
            return self._get_best_action(ant.x, ant.y, ant.mode)

    def _get_valid_actions(self, x, y):
        """Gets a list of valid actions from a given position."""
        valid_actions = []
        for i, (dx, dy) in enumerate(self.actions):
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.grid.width and 0 <= ny < self.grid.height and \
               self.grid.grid[ny][nx] != CellType.WALL:
                valid_actions.append(i)
        return valid_actions

    def _get_best_action(self, x, y, ant_mode):
        """Finds the best action from the Q-table for a given state."""
        q_table = self.get_q_table(ant_mode)
        q_values = q_table[y][x]
        valid_actions = self._get_valid_actions(x,y)

        if not valid_actions:
            return 0 # Default action index if no valid moves

        max_q = -float('inf')
        best_action_index = valid_actions[0]

        # Find the action with the highest Q-value among valid actions
        for action_index in valid_actions:
            if q_values[action_index] > max_q:
                max_q = q_values[action_index]
                best_action_index = action_index

        return best_action_index


    def update_q_value(self, ant, old_pos, action_index, reward, new_pos):
        """Updates the Q-value for a given state-action pair."""
        q_table = self.get_q_table(ant.mode)
        old_x, old_y = old_pos
        new_x, new_y = new_pos

        # Old Q-value
        old_q_value = q_table[old_y][old_x][action_index]

        # Maximum Q-value for the new state
        future_q_values = q_table[new_y][new_x]
        max_future_q = max(future_q_values)

        # Q-learning formula
        new_q_value = old_q_value + ant.learning_rate * \
            (reward + ant.discount_factor * max_future_q - old_q_value)

        q_table[old_y][old_x][action_index] = new_q_value