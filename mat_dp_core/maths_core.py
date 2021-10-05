import numpy as np
from numpy.typing import ArrayLike
from numpy.linalg import solve, lstsq, qr

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
    print(process_demands)
    run_matrix = np.zeros(demand_policy.shape[0:2])
    for i, process_slice in enumerate(demand_policy):
        for j, resource_links in enumerate(process_slice):
            resource_runs = []
            for k, value in enumerate(resource_links):
                resource_produced_one_run = -process_demands[i][k]
                amount_demanded_by_sub = process_demands[j][k]*value
                if amount_demanded_by_sub==0 and resource_produced_one_run==0:
                    expected_runs = 0
                elif resource_produced_one_run ==0:
                    raise ValueError('Material demanded when none is produced!')
                else:
                    expected_runs = amount_demanded_by_sub/resource_produced_one_run
                resource_runs.append(expected_runs)
            run_matrix[i][j] = max(resource_runs)
    #print(run_matrix)
    return run_matrix



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
    # Subtract identity matrix
    # Make into reduced row echelon form
    #Use solver


    # TODO Figure out if this start and end method is generic - test by adding other constraints
    start=None
    end = None
    for i, line in enumerate(run_matrix):
        if all([i==0 for i in line]):
            end = i
    for i, line in enumerate(np.transpose(run_matrix)):
        if all([i==0 for i in line]):
            start = i
    
    i = identity(5)
    new_run = np.transpose(run_matrix - i)
    test = np.delete(new_run,start, 0)
    new_test = np.delete(test,end,1)
    new_scenario_2 = np.delete(run_scenario,start,0)
    out = solve(new_test, new_scenario_2)
    print(out)
    return out
    """
    #print(np.array(out[3]))
    new_run_mat = np.array(
        [
            [2, -1, 0, 0],
            [1.5, 0, -1, 0],
            [0, 0.4,0.6,-1],
            [0, 0, 0, 0.5]
        ]
    )
    new_run_scenario = np.array([0,0,0,5])
    print(new_run_mat)
    print(new_run_scenario)
    out = solve(new_run_mat, new_run_scenario)
    print(out)
    """
    """
    for i, lower_bound in enumerate(run_scenario):
        def get_total_runs_for_process(process_index, lower_bound, run_matrix):
            if lower_bound !=0:
                if lower_bound >0:
                    proc_slice = np.transpose(run_matrix)[process_index]
                else:
                    proc_slice = run_matrix[process_index]
                
                for j, runs_to_satisfy in enumerate(proc_slice):
                    if runs_to_satisfy != 0:
                        dest_lower_bound = lower_bound/runs_to_satisfy
                        total_runs = get_total_runs_for_process(j, dest_lower_bound, run_matrix)
                        print(total_runs)
                
            else:
                #
                #    #j_lower = run_scenario[j]
            
                print(lower_bound)
                print(proc_slice)
        total_runs = get_total_runs_for_process(i, lower_bound, run_matrix)
    """




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
