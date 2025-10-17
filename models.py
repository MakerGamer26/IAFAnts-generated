import enum

class CellType(enum.Enum):
    """Enumeration for the different types of cells on the grid."""
    EMPTY = 0
    WALL = 1
    FOOD = 2
    NEST = 3
    DEADLY = 4

class AntMode(enum.Enum):
    """Enumeration for the two modes of an ant."""
    SEARCHING_FOOD = "recherche de nourriture"
    RETURNING_TO_NEST = "recherche du nid"

class Ant:
    """Base class for all ants."""
    def __init__(self, x, y, learning_rate, discount_factor, epsilon):
        self.x = x
        self.y = y
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.epsilon = epsilon
        self.current_load = 0
        self.mode = AntMode.SEARCHING_FOOD

        # To be defined in subclasses
        self.max_load = 0
        self.speed = 0  # Time units (S) per cell (M)
        self.vision_range = 0
        self.time_to_next_move = 0

    def switch_mode(self):
        """Switches the ant's mode."""
        if self.current_load > 0:
            self.mode = AntMode.RETURNING_TO_NEST
        else:
            self.mode = AntMode.SEARCHING_FOOD

class Explorer(Ant):
    """Explorer ant subclass."""
    def __init__(self, x, y, learning_rate, discount_factor, epsilon):
        super().__init__(x, y, learning_rate, discount_factor, epsilon)
        self.max_load = 10
        self.speed = 5  # 1 case per 5S
        self.vision_range = 1
        self.time_to_next_move = self.speed

class Fighter(Ant):
    """Fighter ant subclass."""
    def __init__(self, x, y, learning_rate, discount_factor, epsilon):
        super().__init__(x, y, learning_rate, discount_factor, epsilon)
        self.max_load = 10
        self.speed = 5  # 1 case per 5S
        self.vision_range = 1
        self.time_to_next_move = self.speed

class Collector(Ant):
    """Collector ant subclass."""
    def __init__(self, x, y, learning_rate, discount_factor, epsilon):
        super().__init__(x, y, learning_rate, discount_factor, epsilon)
        self.max_load = 100
        self.speed = 10  # 1 case per 10S
        self.vision_range = 0
        self.time_to_next_move = self.speed

class FoodSource:
    """Represents a source of food on the grid."""
    def __init__(self, x, y, quantity):
        self.x = x
        self.y = y
        self.initial_quantity = quantity
        self.quantity = quantity

class Nest:
    """Represents the ant's nest."""
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.food_collected = 0
        self.available_ants = {
            Explorer: 0,
            Fighter: 0,
            Collector: 0,
        }

class Grid:
    """Represents the 2D world grid."""
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.grid = [[CellType.EMPTY for _ in range(width)] for _ in range(height)]
        self.food_sources = []
        self.nest_position = None

    def set_cell(self, x, y, cell_type, quantity=0):
        """Sets the type of a cell and adds food or nest if applicable."""
        if 0 <= x < self.width and 0 <= y < self.height:
            self.grid[y][x] = cell_type
            if cell_type == CellType.FOOD:
                self.food_sources.append(FoodSource(x, y, quantity))
            elif cell_type == CellType.NEST:
                self.nest_position = (x, y)

class PheromoneGrid:
    """Represents the Q-tables for the simulation."""
    def __init__(self, width, height):
        self.width = width
        self.height = height
        # Q-table for finding food
        self.food_q_table = [[[0.0, 0.0, 0.0, 0.0] for _ in range(width)] for _ in range(height)] # N, E, S, W
        # Q-table for returning to the nest
        self.nest_q_table = [[[0.0, 0.0, 0.0, 0.0] for _ in range(width)] for _ in range(height)] # N, E, S, W