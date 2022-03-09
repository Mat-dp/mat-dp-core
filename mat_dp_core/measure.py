from typing import Optional, Sequence, Tuple, Union, overload

import numpy as np
from numpy import ndarray

from .maths_core import Process, Processes, Resource, Resources
from .maths_core.solvers import BoundedSolver


def extract_from_resource_process_array(
    resource_process_array: ndarray,
    resources: Resources,
    processes: Processes,
    process: Optional[Process],
    resource: Optional[Resource],
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
    if process is None and resource is None:
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
    elif process is not None and resource is None:
        return list(
            zip(
                resources,
                resource_process_array[:, process.index],
            )
        )
    elif resource is not None and process is None:
        return list(
            zip(
                processes,
                resource_process_array[resource.index],
            )
        )
    else:
        assert resource is not None and process is not None
        return resource_process_array[resource.index][process.index]


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
    def run(self, *, bounds: bool = False) -> Sequence[Tuple[Process, float]]:
        """
        bounds: Whether or not to calculate bounds

        Returns the runs of each process
        """
        ...

    @overload
    def run(self, *, process: Process, bounds: bool = False) -> float:
        """
        process: The process under inspection
        bounds: Whether or not to calculate bounds

        Returns the runs of this process
        """
        ...

    def run(
        self, *, process: Optional[Process] = None, bounds: bool = False
    ) -> Union[Sequence[Tuple[Process, float]], float]:
        if process is None:
            return list(zip(self._processes, self.run_vector))
        else:
            return self.run_vector[process.index]

    @overload
    def resource(
        self, *, bounds: bool = False
    ) -> Sequence[Tuple[Process, Resource, float]]:
        """
        bounds: Whether or not to calculate bounds

        Returns measurements for all processes and resources.
        """
        ...

    @overload
    def resource(
        self, *, process: Process, bounds: bool = False
    ) -> Sequence[Tuple[Resource, float]]:
        """
        process: A process to be measured
        bounds: Whether or not to calculate bounds

        Returns the input and output resource values for the process specified.
        """
        ...

    @overload
    def resource(
        self, *, resource: Resource, bounds: bool = False
    ) -> Sequence[Tuple[Process, float]]:
        """
        resource: A resource to be measured
        bounds: Whether or not to calculate bounds

        Returns how much each process consumes or produces of the resource provided.
        """
        ...

    @overload
    def resource(
        self, *, process: Process, resource: Resource, bounds: bool = False
    ) -> float:
        """
        process: A process to be measured
        resource: A resource to be measured
        bounds: Whether or not to calculate bounds

        Returns how much this process produces or consumes of this resource.
        """
        ...

    def resource(
        self,
        *,
        process: Optional[Process] = None,
        resource: Optional[Resource] = None,
        bounds: bool = False
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
            process,
            resource,
        )

    @overload
    def flow(
        self, *, bounds: bool = False
    ) -> Sequence[Tuple[Process, Process, Resource, float]]:
        """
        Returns all flows between each process pair and each resource.
        """
        ...

    @overload
    def flow(
        self,
        *,
        process_from: Process,
        process_to: Process,
        bounds: bool = False
    ) -> Sequence[Tuple[Resource, float]]:
        """
        process_from: The process to measure the flow from
        process_to: The process to measure the flow to
        bounds: Whether or not to calculate bounds

        Returns all flows between the process pair specified.
        """
        ...

    @overload
    def flow(
        self, *, resource: Resource, bounds: bool = False
    ) -> Sequence[Tuple[Process, Process, float]]:
        """
        resource: The resource to measure flows for
        bounds: Whether or not to calculate bounds

        Returns all flows for the resource specified
        """
        ...

    @overload
    def flow(
        self, *, process_from: Process, bounds: bool = False
    ) -> Sequence[Tuple[Resource, float]]:
        """
        process: The process material is flowing from
        bounds: Whether or not to calculate bounds

        Returns the sum of all outflows from this process for each resource
        """
        ...

    @overload
    def flow(
        self,
        *,
        process_from: Process,
        resource: Resource,
        bounds: bool = False
    ) -> float:
        """
        process_from: The process material is flowing from
        resource: The resource that is flowing
        bounds: Whether or not to calculate bounds

        Returns the sum of all outflows from this process for this resource
        """
        ...

    @overload
    def flow(
        self, *, process_to: Process, bounds: bool = False
    ) -> Sequence[Tuple[Resource, float]]:
        """
        process: The process material is flowing into
        bounds: Whether or not to calculate bounds

        Returns the sum of all inflows into this process for each resource
        """
        ...

    @overload
    def flow(
        self, *, process_to: Process, resource: Resource, bounds: bool = False
    ) -> float:
        """
        process_to: The process material is flowing into
        resource: The resource that is flowing
        bounds: Whether or not to calculate bounds

        Returns the sum of all inflows into this process for this resource
        """
        ...

    @overload
    def flow(
        self,
        *,
        process_from: Process,
        process_to: Process,
        resource: Resource,
        bounds: bool = False
    ) -> float:
        """
        process_from: The process to measure the flow from
        process_to: The process to measure the flow to
        resource: The resource to measure
        bounds: Whether or not to calculate bounds

        Returns the value of resource flow for the given process pair and resource
        """
        ...

    def flow(
        self,
        *,
        process_from: Optional[Process] = None,
        process_to: Optional[Process] = None,
        resource: Optional[Resource] = None,
        bounds: bool = False
    ) -> Union[
        Sequence[Tuple[Process, Process, Resource, float]],
        Sequence[Tuple[Resource, float]],
        Sequence[Tuple[Process, Process, float]],
        float,
    ]:
        if process_from is None and process_to is None and resource is None:
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
        elif (
            resource is not None
            and process_from is None
            and process_to is None
        ):
            output = []
            for p1 in self._processes:
                for p2 in self._processes:
                    if p1.index != p2.index:
                        output.append(
                            (
                                p1,
                                p2,
                                self.flow_matrix[resource.index][p1.index][
                                    p2.index
                                ],
                            )
                        )
            return output
        elif (
            process_from is not None
            and process_to is not None
            and resource is None
        ):
            output = []
            for r in self._resources:
                output.append(
                    (
                        r,
                        self.flow_matrix[r.index][process_from.index][
                            process_to.index
                        ],
                    )
                )
            return output
        elif (
            process_from is not None
            and process_to is None
            and resource is None
        ):
            return [
                (
                    r,
                    calculate_incident_flow(
                        self.flow_matrix,
                        r.index,
                        process_from.index,
                        flow_from=True,
                    ),
                )
                for r in self._resources
            ]
        elif (
            process_from is not None
            and process_to is None
            and resource is not None
        ):
            return calculate_incident_flow(
                self.flow_matrix,
                resource.index,
                process_from.index,
                flow_from=True,
            )
        elif (
            resource is None
            and process_to is not None
            and process_from is None
        ):
            return [
                (
                    r,
                    calculate_incident_flow(
                        self.flow_matrix,
                        r.index,
                        process_to.index,
                        flow_from=False,
                    ),
                )
                for r in self._resources
            ]
        elif (
            resource is not None
            and process_to is not None
            and process_from is None
        ):
            return calculate_incident_flow(
                self.flow_matrix,
                resource.index,
                process_to.index,
                flow_from=False,
            )
        else:
            assert (
                process_from is not None
                and process_to is not None
                and resource is not None
            )
            return self.flow_matrix[resource.index][process_from.index][
                process_to.index
            ]

    @overload
    def cumulative_resource(
        self, *, bounds: bool = False
    ) -> Sequence[Tuple[Process, Resource, float]]:
        """
        bounds: Whether or not to calculate bounds

        Returns the amount of each resource used for the entire chain of processes that led to each process.
        """
        ...

    @overload
    def cumulative_resource(
        self, *, process: Process, bounds: bool = False
    ) -> Sequence[Tuple[Resource, float]]:
        """
        process: The process using resource
        bounds: Whether or not to calculate bounds

        Returns the amount of each resource used for the entire chain of processes that led to this process.
        """
        ...

    @overload
    def cumulative_resource(
        self, *, resource: Resource, bounds: bool = False
    ) -> Sequence[Tuple[Process, float]]:
        """
        resource: The resource we are measuring
        bounds: Whether or not to calculate bounds

        Returns the amount of resource used for the entire chain of processes that led to each process.
        """
        ...

    @overload
    def cumulative_resource(
        self, *, process: Process, resource: Resource, bounds: bool = False
    ) -> float:
        """
        process: The process using resource
        resource: The resource we are measuring
        bounds: Whether or not to calculate bounds

        Returns the amount of resource used for the entire chain of processes that led to this process.
        """
        ...

    def cumulative_resource(
        self,
        *,
        process: Optional[Process] = None,
        resource: Optional[Resource] = None,
        bounds: bool = False
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
            process=process,
            resource=resource,
        )
