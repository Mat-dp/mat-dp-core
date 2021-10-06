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
    """
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
    print(new_test)
    print(new_scenario_2)
    print(out)
    print(run_matrix)
    """
    run_vectors = []
    for i, lower_bound in enumerate(run_scenario):
        def get_submatrix_of_run_matrix(process_index: int, run_matrix: ArrayLike):
            axis_labels = [None]*5

            def get_current_line(axis_labels: ArrayLike, process_index: int):
                proc_slice = np.transpose(run_matrix)[process_index]
                current_line = [None]*5
                connecting_processes = []
                has_none_zero = False
                for i, run_num in enumerate(proc_slice):
                    if run_num !=0:
                        if i not in axis_labels:
                            first_free_slot = axis_labels.index(None)
                            axis_labels[first_free_slot] = i
                        line_index = axis_labels.index(i)
                        current_line[line_index] = run_num
                        connecting_processes.append(i)
                        has_none_zero = True
                    elif i == process_index:
                        if i in axis_labels:
                            line_index = axis_labels.index(i)
                            current_line[line_index] = -1
                if not has_none_zero:
                    current_line = [None]*5
                return current_line, axis_labels, connecting_processes
            def get_current_lines(axis_labels, process_index):
                current_lines = []
                current_line, axis_labels, connecting_processes = get_current_line(axis_labels, process_index)
                current_lines += [current_line]
                for connected_index in connecting_processes:
                    current_lines_new, axis_labels = get_current_lines(axis_labels, connected_index)
                    current_lines += current_lines_new
                return current_lines, axis_labels

            current_lines, axis_labels = get_current_lines(axis_labels, process_index)
            current_array = np.array(current_lines)
            new_array = []
            for line in current_array:
                if not all([i==None for i in line]):
                    new_array.append(line)
            flipped_array = np.transpose(np.array(new_array))
            new_new_array = []
            for line in flipped_array:
                if not all([i==None for i in line]):
                    new_new_array.append(line)
            
            clean_array = np.array(new_new_array)
            for i, item in enumerate(clean_array):
                for j, sub_item in enumerate(item):
                    if sub_item == None:
                        clean_array[i][j] = 0
            clean_array = np.transpose(np.array(clean_array, dtype = np.dtype('float64')))
            x,y = clean_array.shape

            new_axis_labels = axis_labels[0:x]
            return clean_array, new_axis_labels
            """
            # TODO Line descending tree also
            for i, run_num in enumerate(alt_proc_slice):
                if run_num !=0:
                    if i not in axis_labels:
                        axis_labels.append(i)
                    current_line.append(run_num)
            """

        
        if lower_bound !=0:
            submatrix, process_indices = get_submatrix_of_run_matrix(i, run_matrix)
            comparison = np.array([float(0)]*len(process_indices))
            comparison[0] = float(lower_bound)
            results = solve(submatrix, comparison)
            if len(results) != len(process_indices):
                'result process index mismatch'
            run_vector = np.zeros((len(run_scenario)))
            for j, p_index in enumerate(process_indices):
                result = results[j]
                run_vector[p_index] = result
            run_vector[i] = lower_bound
            run_vectors.append(run_vector)


    if len(run_vectors) == 1:
        run_vector = run_vectors[0]
    else:
        raise ValueError('More than one run vector found')
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
        resource_demands = process_demands[i]
        actual_resource_element = resource_demands*runs
        actual_resource[i] = actual_resource_element
    return actual_resource


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
