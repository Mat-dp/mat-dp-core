from mat_dp_core.maths_core import (
    Resources,
    Processes,
    calculate_actual_resource,
    generate_process_demands,
)
from numpy.typing import ArrayLike
from typing import Union

ResourceMeasurement = Union[float, ArrayLike]

# Definitions
"""
The inits of all measures must provide all the necessary structures to measure
The calls perform the measurement itself
"""

class Measure:
    def __init__(self):
        raise NotImplementedError('__init__ not implemented')
    def __call__(self):
        raise NotImplementedError('__call__ not implemented')

# Define subtypes

class BaseResourceMeasure(Measure):
    def __init__(
        self,
        resources: Resources,
        processes: Processes,
        run_vector: ArrayLike,
        process_demands: ArrayLike = None,
        actual_resource: ArrayLike = None,
    ) -> None:
        if process_demands is None:
            process_demands = generate_process_demands(resources, processes)
        if actual_resource is None:
            actual_resource = calculate_actual_resource(process_demands, run_vector)
        self.process_demands = process_demands
        self.actual_resource = actual_resource

class ActualResourceMeasure(BaseResourceMeasure):
    def __call__(
        self,
        process_index = None,
        resource_index = None
    ) -> ResourceMeasurement:
        if process_index is None and resource_index is None:
            return self.actual_resource
        elif process_index is None:
            return self.actual_resource[:, resource_index]
        elif resource_index is None:
            return self.actual_resource[process_index]
        else:
            return self.actual_resource[process_index][resource_index]


class CumulativeResourceMeasure(BaseResourceMeasure):
    def __init__(
        self,
        resources: Resources,
        processes: Processes,
        run_vector: ArrayLike,
        process_demands: ArrayLike = None,
        actual_resource: ArrayLike = None,
    ) -> None:
        super().__init__(
            resources,
            processes,
            run_vector,
            process_demands,
            actual_resource
        )
        # TODO Initialise cumulative matrix

    def __call__(
        self,
        process_index = None,
        resource_index = None
    ) -> ResourceMeasurement:
        raise NotImplementedError('CumulativeResourceMeasure not implemented')


class FlowMeasure(Measure):
    def __init__(
        self,
        resources: Resources,
        processes: Processes,
        run_vector: ArrayLike,
        process_demands: ArrayLike = None,
        actual_resource: ArrayLike = None,
    ) -> None:
        pass
        # TODO Initialise flow matrix
    def __call__(
        self,
        in_process_index = None,
        out_process_index = None,
        resource_index = None
    ) -> ResourceMeasurement:
        raise NotImplementedError('FlowMeasure not implemented')

# Define manager

class MeasureManager:
    def __init__(
        self,
        resources,
        processes,
        run_vector: ArrayLike,
    ) -> None:
        process_demands = generate_process_demands(resources, processes)
        actual_resource = calculate_actual_resource(process_demands, run_vector)
        self.actual_res_measure = ActualResourceMeasure(
            resources,
            processes,
            run_vector,
            process_demands,
            actual_resource
        )
        self.cumulative_res_measure = CumulativeResourceMeasure(
            resources,
            processes,
            run_vector,
            process_demands,
            actual_resource
        )
        self.flow_measure = FlowMeasure(
            resources,
            processes,
            run_vector,
            process_demands,
            actual_resource
        )


    def make_actual_resource_measure(
        self,
        process_index = None,
        resource_index = None
    ):
        return self.actual_res_measure(process_index, resource_index)

    def make_cumulative_resource_measure(
        self,
        process_index = None,
        resource_index = None
    ):
        return self.cumulative_res_measure(process_index, resource_index)
    
    def make_flow_measure(
        self,
        in_process_index = None,
        out_process_index = None,
        resource_index = None
    ):
        return self.flow_measure(in_process_index, out_process_index, resource_index)