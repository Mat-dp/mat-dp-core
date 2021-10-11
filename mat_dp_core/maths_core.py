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
    
    run_matrix = np.zeros(demand_policy.shape[0:2])
    for i, process_slice in enumerate(demand_policy):
        for j, resource_links in enumerate(process_slice):
            resource_runs = []
            for k, value in enumerate(resource_links):
                resource_produced_one_run = -process_demands[i][k]
                amount_demanded_by_sub = process_demands[j][k]*value
                if amount_demanded_by_sub==0 and resource_produced_one_run==0:
                    run_ratio = 0
                elif resource_produced_one_run ==0:
                    raise ValueError('Material demanded when none is produced!')
                else:
                    run_ratio = amount_demanded_by_sub/resource_produced_one_run
                resource_runs.append(run_ratio)
            #print(resource_runs)
            run_matrix[j][i] = max(resource_runs)

    #return run_matrix
    # Reflect run matrix
    for i, in_process in enumerate(run_matrix):
        for j, ratio in enumerate(in_process):
            if (ratio !=0 )and (i!=j):
                run_matrix[j][i] = 1/ratio
    
    # Iterate to fill distant values
    new_run_matrix = np.copy(run_matrix)
    def iterate_on_run_matrix(run_matrix):
        new_run_matrix = np.copy(run_matrix)
        for i in range(run_matrix.shape[0]):
            downstream_slice = run_matrix[i]
            for j, run_ratio in enumerate(downstream_slice):
                if run_ratio !=0:
                    new_slice = run_matrix[j]
                    for k, k_run_ratio in enumerate(new_slice):
                        if k_run_ratio!=0:
                            if new_run_matrix[i][k] ==0 and (k!=i):
                                new_run_matrix[i][k] = run_ratio*k_run_ratio

        return new_run_matrix
    
    while True:
        brand_new_run_matrix = iterate_on_run_matrix(new_run_matrix)
        if np.array_equal(brand_new_run_matrix, new_run_matrix):
            break
        new_run_matrix = brand_new_run_matrix
    
    return new_run_matrix

def calculate_run_vector(
    run_matrix: ArrayLike,          # (process, process) -> +ve float
    run_scenario: ArrayLike         # process -> +ve float
) -> ArrayLike:  # run_vector: process -> +ve float
    """
    Given the run matrix and run scenario, calculate the number of times
    that each process runs in the scenario
    """

    def iterate_on_run_vector(run_vector):
        new_run_vector = []
        for i, current_lower_bound in enumerate(run_vector):
            upstream_slice = np.transpose(run_matrix)[i]
            lower_bounds = [current_lower_bound]
            for j, upstream_ratio in enumerate(upstream_slice):
                lower_bounds.append(run_vector[j]*upstream_ratio)

            new_run_vector.append(max(lower_bounds))
        
        return new_run_vector
    run_vector = iterate_on_run_vector(run_scenario)
    return run_vector



def calculate_actual_resource(
    process_demands: ArrayLike,     # (process, resource) -> float
    run_vector: ArrayLike           # process -> +ve float
    ) -> ArrayLike:  # actual_resource: (process, resource) -> +ve float
    """
    Given the resource demands of each process, and the number of times
    that each process runs, calculate the number of resources that
    are required by each process.
    """
    actual_resource = np.zeros_like(process_demands)
    for i, runs in enumerate(run_vector):
        actual_resource[i] = process_demands[i]*runs
    return actual_resource


def calculate_actual_resource_flow(
    actual_resource: ArrayLike,     # (process, resource) -> +ve float
    demand_policy: ArrayLike        # (process, process, resource) -> +ve float
    ) -> ArrayLike:  # actual_resource_flow: (process, process, resource) -> +ve float
    """
    Given the number of resources that are required by each process, and the policy
    that defines how processes connect, calculate the number of resources that
    flow through each edge.
    """
    actual_resource_flow = np.zeros_like(demand_policy)
    for i, in_process in enumerate(demand_policy):
        for j, out_process in enumerate(in_process):
            for k, proportion in enumerate(out_process):
                actual_resource_flow[i][j][k] = proportion*actual_resource[j][k]

    return actual_resource_flow
