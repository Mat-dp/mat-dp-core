from mat_dp_core.maths_core import EqConstraint, _Process, _Resource, Resources, Processes
from typing import Union, List, Tuple, Optional

class RunEqConstraint(EqConstraint):
    def __init__(
        self, 
        process: Union[_Process, int],
        processes: Processes,
        runs: float,
        name: Optional[str] = None, 
    ):
        if isinstance(process, _Process):
            process_index = process.index
        else:
            process_index = process
        if name is None:
            name = f"{processes[process_index][0]}_fixed_at_{runs}_runs"
        weighted_processes = [(process_index, float(1))]
        super().__init__(name, weighted_processes, runs)


class RunRatioConstraint(EqConstraint):
    def __init__(
        self, 
        process1: Union[_Process, int], 
        process2: Union[_Process, int],
        processes: Processes,
        p2_over_p1: float,
        name: Optional[str] = None, 
    ):
        if isinstance(process1, _Process):
            process1_index = process1.index
        else:
            process1_index = process1
        if isinstance(process2, _Process):
            process2_index = process2.index
        else:
            process2_index = process2
        if name is None:
            name = f"fixed_ratio{processes[process1_index][0]}_to_{processes[process2_index][0]}_at_1:{p2_over_p1}"
        weighted_processes = [(process1_index, 1),(process2_index, p2_over_p1)]
        super().__init__(name, weighted_processes, 0)

class ResourceConstraint(EqConstraint):
    def __init__(
        self,
        resource: Union[_Resource, int],
        process: Union[_Process, int],
        resources: Resources,
        processes: Processes,
        resource_bound: float, # Positive float >0
        name: Optional[str] = None, 
    ):
        # get from resource_bound to run bound
        # need to look at process
        if isinstance(resource, _Resource):
            resource_index = resource.index
        else:
            resource_index = resource
        if isinstance(process, _Process):
            process_index = process.index
        else:
            process_index = process
        demand = processes[process_index][1][resource_index]
        process_name = processes[process_index][0]
        resource_name = resources[resource_index][0]
        units = resources[resource_index][1]
        required_resource = abs(demand)
        if demand < 0:
            positive = False
        elif demand > 0:
            positive = True
        else:
            raise ValueError('Invalid demand')
        
        no_runs = required_resource/resource_bound
    
        if positive:
            phrase = 'consumption'
        else:
            phrase = 'production'
        

        weighted_processes = [(process_index, float(1))]
        
        if name is None:
            name = f"resource_{phrase}_{resource_name}_fixed_at_{resource_bound}{units}for_process{process_name}"
        
        super().__init__(name, weighted_processes, no_runs)


