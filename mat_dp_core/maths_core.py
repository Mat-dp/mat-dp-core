import numpy as np
from numpy.typing import ArrayLike
from numpy.linalg import solve

from numpy import identity

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
                elif amount_demanded_by_sub ==0:
                    run_ratio = 0
                else:
                    run_ratio = resource_produced_one_run/amount_demanded_by_sub
                resource_runs.append(run_ratio)
            run_matrix[i][j] = max(resource_runs)
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
            t_run_matrix = np.transpose(run_matrix)
            downstream_slice = run_matrix[i]
            upstream_slice = t_run_matrix[i]
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



def calculate_run_scenario(
    process_demands: ArrayLike,     # (process, resource) -> float
    scenario: ArrayLike             # (process, resource) -> +ve float
) -> ArrayLike:  # run_scenario: process -> +ve float
    """
    Given the resource demands of each process, and the scenario to specify
    the lower bound of each resource edge, calculate the lower bound of
    the number of times that each process must run
    """
    run_scenario = np.zeros(scenario.shape[0:1])
    for i, resource_bounds in enumerate(scenario):
        resource_runs = []
        for j, lower_bound in enumerate(resource_bounds):
            amount_demanded = process_demands[i][j]
            if amount_demanded==0 or lower_bound==0:
                expected_runs = 0
            else:
                expected_runs = lower_bound/amount_demanded
            resource_runs.append(expected_runs)
        run_scenario[i] = max(resource_runs)
    return run_scenario


def calculate_run_vector(
    run_matrix: ArrayLike,          # (process, process) -> +ve float
    run_scenario: ArrayLike         # process -> +ve float
) -> ArrayLike:  # run_vector: process -> +ve float
    """
    Given the run matrix and run scenario, calculate the number of times
    that each process runs in the scenario
    """

    def evaluate_new_lower_bounds(old_lower_bounds):
        new_lower_bounds = []
        for i, current_lower_bound in enumerate(old_lower_bounds):
            upstream_slice = np.transpose(run_matrix)[i]
            lower_bounds = [current_lower_bound]

            for j, upstream_ratio in enumerate(upstream_slice):
                lower_bound_at_dest = old_lower_bounds[j]
                prediction = lower_bound_at_dest*upstream_ratio
                lower_bounds.append(prediction)
            
            agreed_lower_bound = max(lower_bounds)
            new_lower_bounds.append(agreed_lower_bound)
            
        return new_lower_bounds
    
    return evaluate_new_lower_bounds(run_scenario)



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
        resource_demands = process_demands[i]
        actual_resource_element = resource_demands*runs
        actual_resource[i] = actual_resource_element
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
                if proportion!=0:
                    resource_out = actual_resource[j][k]
                    resource_flow = proportion*resource_out
                    actual_resource_flow[i][j][k] = resource_flow

    return actual_resource_flow


def get_flow_slice(
    actual_resource_flow: ArrayLike,    # (process, process, resource) -> +ve float
    resource_index: int
) -> ArrayLike:     # flow slice (process, process) -> +ve float
    """
    Get a slice of the actual resource flow given a resource index.
    """
    flow_slice = np.zeros(actual_resource_flow.shape[0:2])

    for i, in_process in enumerate(actual_resource_flow):
        for j, out_process in enumerate(in_process):
            try:
                resource_value = out_process[resource_index]
            except IndexError:
                raise ValueError('Resource index out of range')
            flow_slice[i][j] = resource_value
    return flow_slice


def measure_resource_usage(
    flow_slice: ArrayLike,          # (process, process) -> +ve float
    measure: ArrayLike              # (process, process) -> bool
) -> float:  # +ve float
    """
    Given a flow slice, calculate the total
    number of resources that flow through measured edges.
    """
    total_resource_usage = 0
    for i, in_process in enumerate(measure):
        for j, count_bool in enumerate(in_process):
            if count_bool:
                total_resource_usage += flow_slice[i][j]

    return total_resource_usage

def alt_measure_resource_usage(
    actual_resource_flow: ArrayLike,    # (process, process, resource) -> +ve float
    measure: ArrayLike              # (process, process, resource) -> bool
) -> ArrayLike: # resource_usage (resource) -> +ve float
    """
    Given the resource flow and which edges to measure, calculate the total resource
    consumed for each edge.
    """
    resource_usage = np.zeros(measure.shape[2:3])
    for i, in_process in enumerate(measure):
        for j, out_process in enumerate(in_process):
            for k, count_bool in enumerate(out_process):
                if count_bool:
                    resource_value = actual_resource_flow[i][j][k]
                    resource_usage[k] +=  resource_value
    return resource_usage


