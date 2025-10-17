import copy
import time
from simulation import Simulation
from main import DEFAULT_CONFIG

def run_simulation_headless(config):
    """
    Runs the simulation without the GUI and returns the final time.
    """
    simulation = Simulation(config)
    while not simulation.is_finished():
        simulation.run_step()
    return simulation.time

if __name__ == "__main__":
    print("--- Running a single simulation with default parameters ---")

    start_time = time.time()

    # Run the simulation with the default configuration
    final_time = run_simulation_headless(DEFAULT_CONFIG)

    end_time = time.time()

    print(f"Simulation finished at time step: {final_time}")
    print(f"Real-world execution time: {end_time - start_time:.2f} seconds")

    # --- Example of a meta-optimization loop ---
    # This is a conceptual example. A real implementation would explore
    # a wider range of parameters.
    print("\n--- Example Meta-Optimization Loop ---")

    best_config = None
    best_time = float('inf')

    # Example: Test different epsilon values
    for epsilon in [0.1, 0.3, 0.5]:
        print(f"Testing with epsilon = {epsilon}...")

        # Create a copy of the default config to modify
        test_config = copy.deepcopy(DEFAULT_CONFIG)
        test_config["q_learning"]["epsilon"] = epsilon

        sim_time = run_simulation_headless(test_config)

        print(f"  -> Finished in {sim_time} steps.")

        if sim_time < best_time:
            best_time = sim_time
            best_config = test_config

    print("\n--- Meta-Optimization Finished ---")
    print(f"Best time: {best_time} steps")
    print(f"Best epsilon found: {best_config['q_learning']['epsilon']}")