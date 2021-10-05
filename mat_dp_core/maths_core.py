import numpy as np
from numpy.typing import ArrayLike


def calculate_run_matrix(
    process_demands: ArrayLike,     # (process, resource) -> float
    demand_policy: ArrayLike,       # (process, process, resource) -> +ve float
) -> ArrayLike:  # run_matrix: (process, process) -> +ve float
    """
    Given the resource demands of each process, and the demand
    policy to specify how the processes interrelate, calculate for each
    pair of processes the number of runs that process requires
    """
    run_cube_matrix = np.zeros_like(demand_policy)

    for i, process_policy in enumerate(demand_policy):
        resource_products = -process_demands[i]
        new_pol = np.transpose(process_policy)
        for j, resource_produced_one_run in enumerate(resource_products):
            dest_procs = new_pol[j]
            for k, value in enumerate(dest_procs):
                amount_demanded_by_sub = process_demands[k][j]*value
                if amount_demanded_by_sub==0 and resource_produced_one_run==0:
                    expected_runs = 0
                elif resource_produced_one_run ==0:
                    raise ValueError('Material demanded when none is produced!')
                else:
                    expected_runs = amount_demanded_by_sub/resource_produced_one_run
                run_cube_matrix[i][k][j] = expected_runs
    
    run_matrix = np.zeros(run_cube_matrix.shape[0:2])
    
    for i, process_in_layer in enumerate(run_cube_matrix):
        for j, process_out_layer in enumerate(process_in_layer):
            run_matrix[i][j] = max(process_out_layer)
    return run_matrix


                


    


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


def calculate_actual_resource(
    process_demands: ArrayLike,     # (process, resource) -> float
    run_vector: ArrayLike           # process -> +ve float
    ) -> ArrayLike:  # actual_resource: (process, resource) -> +ve float
    """
    Given the resource demands of each process, and the number of times
    that each process runs, calculate the number of resources that
    are required by each process.
    """
    pass

def calculate_actual_resource_flow(
    actual_resource: ArrayLike,     # (process, resource) -> +ve float
    demand_policy: ArrayLike        # (process, process, resource) -> +ve float
    ) -> ArrayLike:  # actual_resource_flow: (process, process, resource) -> +ve float
    """
    Given the resource demands of each process, and the number of times
    that each process runs, calculate the number of resources that
    are required by each process.
    """
    pass


def get_flow_slice(
    actual_resource_flow: ArrayLike,    # (process, process, resource) -> +ve float
    resource_index: int
) -> ArrayLike:     # flow slice (process, process) -> +ve float
    """
    Get a slice of the actual resource flow given a resource index.
    """
    pass

def measure_resource_usage(
    flow_slice: ArrayLike,          # (process, process) -> +ve float
    measure: ArrayLike              # (process, process) -> bool
) -> float:  # +ve float
    """
    Given a flow slice, calculate the total
    number of resources that flow through measured edges.
    """
    pass
