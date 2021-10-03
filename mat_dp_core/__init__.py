import numpy as np
from numpy.typing import ArrayLike


def calculate_run_matrix(
        process_demands: ArrayLike,     # (process, resource) -> float
        demand_policy: ArrayLike,       # (process, process, resource) -> +ve float
        consumption_policy: ArrayLike   # (process, process, resource) -> +ve float
        ) -> ArrayLike:  # run_matrix: (process, process) -> +ve float
    """
    Given the resource demands of each process, and the demand and consumption
    policies to specify how the processes interrelate, calculate for each
    pair of processes the number of runs that process requires
    """
    pass


def calculate_run_scenario(
        process_demands: ArrayLike,     # (process, resource) -> float
        scenario: ArrayLike             # (process, process, resource) -> +ve float
        ) -> ArrayLike:  # run_scenario: process -> +ve float
    """
    Given the resource demands of each process, and the scenario to specify
    the lower bound of each resource edge, calculate the lower bound of
    the number of times that each process must run
    """
    pass


def calculate_run_vector(
        run_matrix: ArrayLike,          # (process, process) -> +ve float
        run_scenario: ArrayLike         # process -> +ve float
        ) -> ArrayLike:  # run_vector: process -> +ve float
    """
    Given the run matrix and run scenario, calculate the number of times
    that each process runs in the scenario
    """
    pass


def calculate_cost_matrix(
        process_demands: ArrayLike,     # (process, resource) -> float
        run_vector: ArrayLike           # process -> +ve float
        ) -> ArrayLike:  # cost_matrix: (process, process, resource) -> +ve float
    """
    Given the resource demands of each process, and the number of times
    that each process runs, calculate the number of resources that
    flow through each edge
    """
    pass


def measure_cost(
        cost_slice: ArrayLike,          # (process, process) -> +ve float
        measure: ArrayLike       # (process, process) -> bool
        ) -> float:  # +ve float
    """
    Given a slice of the cost matrix, which determines the number of resources
    that flows through each edge for a single resource, calculate the total
    number of resources that flow through measured edges
    """
    pass
