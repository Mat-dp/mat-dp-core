from mat_dp_core.maths_core import EqConstraint, Process, Resource, Resources, Processes
from typing import Union, List, Tuple, Optional


class RunEqConstraint(EqConstraint):
    def __init__(
        self,
        process: Process,
        processes: Processes,
        runs: float,
        name: Optional[str] = None,
    ):
        if isinstance(process, Process):
            process_index = process.index
        else:
            process_index = process
        if name is None:
            name = f"{processes[process_index].name}_fixed_at_{runs}_runs"
        weighted_processes = [(process_index, float(1))]
        super().__init__(name, process, runs)


# TODO ratios to support multiple in one go
# TODO require Process and not Processes
# get_constraints method that outputs list of constraints


class RunRatioConstraint(EqConstraint):
    def __init__(
        self,
        process1: Process,
        process2: Process,
        processes: Processes,
        p2_over_p1: float,
        name: Optional[str] = None,
    ):
        if isinstance(process1, Process):
            process1_index = process1.index
        else:
            process1_index = process1
        if isinstance(process2, Process):
            process2_index = process2.index
        else:
            process2_index = process2
        if name is None:
            name = f"fixed_ratio{processes[process1_index].name}_to_{processes[process2_index].name}_at_1:{p2_over_p1}"
        super().__init__(name, process1 + process2 * p2_over_p1, 0)


class ResourceConstraint(EqConstraint):
    def __init__(
        self,
        resource: Resource,
        process: Process,
        resources: Resources,
        processes: Processes,
        resource_bound: float,  # Positive float >0
        name: Optional[str] = None,
    ):
        # get from resource_bound to run bound
        # need to look at process
        if isinstance(resource, Resource):
            resource_index = resource.index
        else:
            resource_index = resource
        if isinstance(process, Process):
            process_index = process.index
        else:
            process_index = process
        # TODO Get resource from process
        demand = processes[process_index].array[resource_index]

        process_name = processes[process_index].name
        resource_name = resources[resource_index].name
        units = resources[resource_index].unit
        required_resource = abs(demand)

        # TODO Consider flows?
        if demand < 0:
            positive = False
        elif demand > 0:
            positive = True
        else:
            raise ValueError("Invalid demand")

        no_runs = required_resource / resource_bound

        if positive:
            phrase = "consumption"
        else:
            phrase = "production"

        if name is None:
            name = f"resource_{phrase}_{resource_name}_fixed_at_{resource_bound}{units}for_process{process_name}"
        super().__init__(name, process, no_runs)
