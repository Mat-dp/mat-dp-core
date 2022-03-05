from typing import Optional, Sequence, Tuple, Union, overload

import numpy as np
from numpy import ndarray

from .maths_core import Process, Processes, Resource, Resources
from .maths_core.solvers import BoundedSolver


def extract_from_resource_process_array(
    resource_process_array: ndarray,
    resources: Resources,
    processes: Processes,
    input_args: Tuple[Optional[Union[Process, Resource]], Optional[Resource]],
) -> Union[
    Sequence[Tuple[Process, Resource, float]],
    Sequence[Tuple[Resource, float]],
    Sequence[Tuple[Process, float]],
    float,
]:
    """
    resource_process_array - a 2D input array of the form (resource, process)
    resources - The associated resources object
    processes - The associated processes object
    input_args - The input args specifying the relevant resource and/or process, if any
    """
    arg1, arg2 = input_args
    if arg1 is None and arg2 is None:
        output = []
        for p in processes:
            for r in resources:
                output.append(
                    (
                        p,
                        r,
                        resource_process_array[r.index][p.index],
                    )
                )
        return output
    elif isinstance(arg1, Process) and arg2 is None:
        return list(
            zip(
                resources,
                resource_process_array[:, arg1.index],
            )
        )
    elif isinstance(arg1, Resource) and arg2 is None:
        return list(
            zip(
                processes,
                resource_process_array[arg1.index],
            )
        )
    else:
        assert arg1 is not None and arg2 is not None
        return resource_process_array[arg2.index][arg1.index]


def calculate_incident_flow(
    flow_matrix, resource_index, process_index, flow_from: bool
) -> float:
    if flow_from:
        column = flow_matrix[resource_index, process_index, :]
    else:
        column = flow_matrix[resource_index, :, process_index]
    return np.sum(column, where=column > 0)


class Measure(BoundedSolver):
    @overload
    def run(self) -> Sequence[Tuple[Process, float]]:
        ...

    @overload
    def run(self, process: Process) -> float:
        ...

    def run(
        self, process: Optional[Process] = None
    ) -> Union[Sequence[Tuple[Process, float]], float]:
        if process is None:
            return list(zip(self._processes, self.run_vector))
        else:
            return self.run_vector[process.index]

    @overload
    def resource(self) -> Sequence[Tuple[Process, Resource, float]]:
        """
        Returns measurements for all processes and resources.
        """
        ...

    @overload
    def resource(self, arg1: Process) -> Sequence[Tuple[Resource, float]]:
        """
        arg1: A process to be measured

        Returns the input and output resource values for the process specified.
        """
        ...

    @overload
    def resource(self, arg1: Resource) -> Sequence[Tuple[Process, float]]:
        """
        arg1: A resource to be measured

        Returns how much each process consumes or produces of the resource provided.
        """
        ...

    @overload
    def resource(self, arg1: Process, arg2: Resource) -> float:
        """
        arg1: A process to be measured
        arg2: A resource to be measured

        Returns how much this process produces or consumes of this resource.
        """
        ...

    def resource(
        self,
        arg1: Optional[Union[Process, Resource]] = None,
        arg2: Optional[Resource] = None,
    ) -> Union[
        Sequence[Tuple[Process, Resource, float]],
        Sequence[Tuple[Resource, float]],
        Sequence[Tuple[Process, float]],
        float,
    ]:
        return extract_from_resource_process_array(
            self.resource_matrix,
            self._resources,
            self._processes,
            (arg1, arg2),
        )

    @overload
    def flow(self) -> Sequence[Tuple[Process, Process, Resource, float]]:
        """
        Returns all flows between each process pair and each resource.
        """
        ...

    @overload
    def flow(
        self, arg1: Process, arg2: Process
    ) -> Sequence[Tuple[Resource, float]]:
        """
        arg1: The process to measure the flow from
        arg2: The process to measure the flow to

        Returns all flows between the process pair specified.
        """
        ...

    @overload
    def flow(self, arg1: Resource) -> Sequence[Tuple[Process, Process, float]]:
        """
        arg1: The resource to measure flows for

        Returns all flows for the resource specified
        """
        ...

    @overload
    def flow(self, arg1: Process, arg2: Process, arg3: Resource) -> float:
        """
        arg1: The process to measure the flow from
        arg2: The process to measure the flow to
        arg3: The resource to measure

        Returns the value of resource flow for the given process pair and resource
        """
        ...

    def flow(
        self,
        arg1: Optional[Union[Process, Resource]] = None,
        arg2: Optional[Process] = None,
        arg3: Optional[Resource] = None,
    ) -> Union[
        Sequence[Tuple[Process, Process, Resource, float]],
        Sequence[Tuple[Resource, float]],
        Sequence[Tuple[Process, Process, float]],
        float,
    ]:
        if arg1 is None and arg2 is None and arg3 is None:
            output = []
            for p1 in self._processes:
                for p2 in self._processes:
                    for r in self._resources:
                        if p1.index != p2.index:
                            output.append(
                                (
                                    p1,
                                    p2,
                                    r,
                                    self.flow_matrix[r.index][p1.index][
                                        p2.index
                                    ],
                                )
                            )
            return output
        elif isinstance(arg1, Resource) and arg2 is None and arg3 is None:
            output = []
            for p1 in self._processes:
                for p2 in self._processes:
                    if p1.index != p2.index:
                        output.append(
                            (
                                p1,
                                p2,
                                self.flow_matrix[arg1.index][p1.index][
                                    p2.index
                                ],
                            )
                        )
            return output
        elif isinstance(arg1, Process) and arg2 is not None and arg3 is None:
            output = []
            for r in self._resources:
                output.append(
                    (
                        r,
                        self.flow_matrix[r.index][arg1.index][arg2.index],
                    )
                )
            return output
        else:
            assert arg1 is not None and arg2 is not None and arg3 is not None
            assert isinstance(arg1, Process)
            return self.flow_matrix[arg3.index][arg1.index][arg2.index]

    @overload
    def flow_from(self, process: Process) -> Sequence[Tuple[Resource, float]]:
        """
        process: The process material is flowing from

        Returns the sum of all outflows from this process for each resource
        """
        ...

    @overload
    def flow_from(self, process: Process, resource: Resource) -> float:
        """
        process: The process material is flowing from
        resource: The resource that is flowing

        Returns the sum of all outflows from this process for this resource
        """
        ...

    def flow_from(
        self, process: Process, resource: Optional[Resource] = None
    ) -> Union[Sequence[Tuple[Resource, float]], float]:
        if resource is None:
            return [
                (
                    r,
                    calculate_incident_flow(
                        self.flow_matrix,
                        r.index,
                        process.index,
                        flow_from=True,
                    ),
                )
                for r in self._resources
            ]
        else:
            return calculate_incident_flow(
                self.flow_matrix,
                resource.index,
                process.index,
                flow_from=True,
            )

    @overload
    def flow_to(self, process: Process) -> Sequence[Tuple[Resource, float]]:
        """
        process: The process material is flowing into

        Returns the sum of all inflows into this process for each resource
        """
        ...

    @overload
    def flow_to(self, process: Process, resource: Resource) -> float:
        """
        process: The process material is flowing into
        resource: The resource that is flowing

        Returns the sum of all inflows into this process for this resource
        """
        ...

    def flow_to(
        self, process: Process, resource: Optional[Resource] = None
    ) -> Union[Sequence[Tuple[Resource, float]], float]:
        if resource is None:
            return [
                (
                    r,
                    calculate_incident_flow(
                        self.flow_matrix,
                        r.index,
                        process.index,
                        flow_from=False,
                    ),
                )
                for r in self._resources
            ]
        else:
            return calculate_incident_flow(
                self.flow_matrix,
                resource.index,
                process.index,
                flow_from=False,
            )

    @overload
    def cumulative_resource(self) -> Sequence[Tuple[Process, Resource, float]]:
        """
        Returns the amount of each resource used for the entire chain of processes that led to each process.
        """
        ...

    @overload
    def cumulative_resource(
        self, arg1: Process
    ) -> Sequence[Tuple[Resource, float]]:
        """
        arg1: The process using resource

        Returns the amount of each resource used for the entire chain of processes that led to this process.
        """
        ...

    @overload
    def cumulative_resource(
        self, arg1: Resource
    ) -> Sequence[Tuple[Process, float]]:
        """
        arg1: The resource we are measuring

        Returns the amount of resource used for the entire chain of processes that led to each process.
        """
        ...

    @overload
    def cumulative_resource(self, arg1: Process, arg2: Resource) -> float:
        """
        arg1: The process using resource
        arg2: The resource we are measuring

        Returns the amount of resource used for the entire chain of processes that led to this process.
        """
        ...

    def cumulative_resource(
        self,
        arg1: Optional[Union[Process, Resource]] = None,
        arg2: Optional[Resource] = None,
    ) -> Union[
        Sequence[Tuple[Process, Resource, float]],
        Sequence[Tuple[Resource, float]],
        Sequence[Tuple[Process, float]],
        float,
    ]:
        return extract_from_resource_process_array(
            self.cumulative_resource_matrix,
            self._resources,
            self._processes,
            (arg1, arg2),
        )
