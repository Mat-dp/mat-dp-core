from typing import List, Optional, Tuple, Union, overload

import numpy as np
from numpy import ndarray

from .maths_core import Process, Processes, Resource, Resources
from .maths_core.solvers import BoundedSolver


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
    def run(
        self, *, bounds: bool = False
    ) -> Union[
        List[Tuple[Process, float]],
        List[Tuple[Process, float, float, float]],
    ]:
        """
        bounds: Whether or not to calculate bounds

        Returns the runs of each process
        """
        ...

    @overload
    def run(
        self, *, process: Process, bounds: bool = False
    ) -> Union[float, Tuple[float, float, float]]:
        """
        process: The process under inspection
        bounds: Whether or not to calculate bounds

        Returns the runs of this process
        """
        ...

    def run(
        self, *, process: Optional[Process] = None, bounds: bool = False
    ) -> Union[
        List[Tuple[Process, float]],
        List[Tuple[Process, float, float, float]],
        float,
        Tuple[float, float, float],
    ]:
        if process is None:
            if bounds:
                return list(
                    zip(
                        self._processes,
                        self.run_vector,
                        self.run_vector_lb,
                        self.run_vector_ub,
                    )
                )
            else:
                return list(zip(self._processes, self.run_vector))
        else:
            if bounds:
                return (
                    self.run_vector[process.index],
                    self.run_vector_lb[process.index],
                    self.run_vector_ub[process.index],
                )
            else:
                return self.run_vector[process.index]

    @overload
    def resource(
        self, *, bounds: bool = False
    ) -> Union[
        List[Tuple[Process, Resource, float]],
        List[Tuple[Process, Resource, float, float, float]],
    ]:

        """
        bounds: Whether or not to calculate bounds

        Returns measurements for all processes and resources.
        """
        ...

    @overload
    def resource(
        self, *, process: Process, bounds: bool = False
    ) -> Union[
        List[Tuple[Resource, float]],
        List[Tuple[Resource, float, float, float]],
    ]:
        """
        process: A process to be measured
        bounds: Whether or not to calculate bounds

        Returns the input and output resource values for the process specified.
        """
        ...

    @overload
    def resource(
        self, *, resource: Resource, bounds: bool = False
    ) -> Union[
        List[Tuple[Process, float]], List[Tuple[Process, float, float, float]]
    ]:
        """
        resource: A resource to be measured
        bounds: Whether or not to calculate bounds

        Returns how much each process consumes or produces of the resource provided.
        """
        ...

    @overload
    def resource(
        self, *, process: Process, resource: Resource, bounds: bool = False
    ) -> Union[float, Tuple[float, float, float]]:
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
        List[Tuple[Process, Resource, float]],
        List[Tuple[Resource, float]],
        List[Tuple[Process, float]],
        float,
        List[Tuple[Process, Resource, float, float, float]],
        List[Tuple[Resource, float, float, float]],
        List[Tuple[Process, float, float, float]],
        Tuple[float, float, float],
    ]:
        if process is None and resource is None:
            output = []
            for p in self._processes:
                for r in self._resources:
                    if bounds:
                        output.append(
                            (
                                p,
                                r,
                                self.resource_matrix[r.index][p.index],
                                self.resource_matrix_lb[r.index][p.index],
                                self.resource_matrix_ub[r.index][p.index],
                            )
                        )
                    else:
                        output.append(
                            (
                                p,
                                r,
                                self.resource_matrix[r.index][p.index],
                            )
                        )
            return output
        elif process is not None and resource is None:
            if bounds:
                return list(
                    zip(
                        self._resources,
                        self.resource_matrix[:, process.index],
                        self.resource_matrix_lb[:, process.index],
                        self.resource_matrix_ub[:, process.index],
                    )
                )
            else:
                return list(
                    zip(
                        self._resources, self.resource_matrix[:, process.index]
                    )
                )
        elif resource is not None and process is None:
            if bounds:
                return list(
                    zip(
                        self._processes,
                        self.resource_matrix[resource.index],
                        self.resource_matrix_lb[resource.index],
                        self.resource_matrix_ub[resource.index],
                    )
                )
            else:
                return list(
                    zip(
                        self._processes,
                        self.resource_matrix[resource.index],
                    )
                )
        else:
            assert resource is not None and process is not None
            if bounds:
                return (
                    self.resource_matrix[resource.index][process.index],
                    self.resource_matrix_lb[resource.index][process.index],
                    self.resource_matrix_ub[resource.index][process.index],
                )
            else:
                return self.resource_matrix[resource.index][process.index]

    @overload
    def flow(
        self, *, bounds: bool = False
    ) -> Union[
        List[Tuple[Process, Process, Resource, float]],
        List[Tuple[Process, Process, Resource, float, float, float]],
    ]:
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
    ) -> Union[
        List[Tuple[Resource, float]],
        List[Tuple[Resource, float, float, float]],
    ]:
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
    ) -> Union[
        List[Tuple[Process, Process, float]],
        List[Tuple[Process, Process, float, float, float]],
    ]:
        """
        resource: The resource to measure flows for
        bounds: Whether or not to calculate bounds

        Returns all flows for the resource specified
        """
        ...

    @overload
    def flow(
        self, *, process_from: Process, bounds: bool = False
    ) -> Union[
        List[Tuple[Resource, float]],
        List[Tuple[Resource, float, float, float]],
    ]:
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
    ) -> Union[float, Tuple[float, float, float]]:
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
    ) -> Union[
        List[Tuple[Resource, float]],
        List[Tuple[Resource, float, float, float]],
    ]:
        """
        process: The process material is flowing into
        bounds: Whether or not to calculate bounds

        Returns the sum of all inflows into this process for each resource
        """
        ...

    @overload
    def flow(
        self, *, process_to: Process, resource: Resource, bounds: bool = False
    ) -> Union[float, Tuple[float, float, float]]:
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
    ) -> Union[float, Tuple[float, float, float]]:
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
        List[Tuple[Process, Process, Resource, float]],
        List[Tuple[Resource, float]],
        List[Tuple[Process, Process, float]],
        float,
        List[Tuple[Process, Process, Resource, float, float, float]],
        List[Tuple[Resource, float, float, float]],
        List[Tuple[Process, Process, float, float, float]],
        Tuple[float, float, float],
    ]:
        if process_from is None and process_to is None and resource is None:
            output = []
            for p1 in self._processes:
                for p2 in self._processes:
                    for r in self._resources:
                        if p1.index != p2.index:
                            if bounds:
                                output.append(
                                    (
                                        p1,
                                        p2,
                                        r,
                                        self.flow_matrix[r.index][p1.index][
                                            p2.index
                                        ],
                                        self.flow_matrix_lb[r.index][p1.index][
                                            p2.index
                                        ],
                                        self.flow_matrix_ub[r.index][p1.index][
                                            p2.index
                                        ],
                                    )
                                )
                            else:
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
            process_from is not None
            and process_to is None
            and resource is None
        ):
            if bounds:
                return [
                    (
                        r,
                        calculate_incident_flow(
                            self.flow_matrix,
                            r.index,
                            process_from.index,
                            flow_from=True,
                        ),
                        calculate_incident_flow(
                            self.flow_matrix_lb,
                            r.index,
                            process_from.index,
                            flow_from=True,
                        ),
                        calculate_incident_flow(
                            self.flow_matrix_ub,
                            r.index,
                            process_from.index,
                            flow_from=True,
                        ),
                    )
                    for r in self._resources
                ]
            else:
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
            process_from is None
            and process_to is not None
            and resource is None
        ):
            if bounds:
                return [
                    (
                        r,
                        calculate_incident_flow(
                            self.flow_matrix,
                            r.index,
                            process_to.index,
                            flow_from=False,
                        ),
                        calculate_incident_flow(
                            self.flow_matrix_lb,
                            r.index,
                            process_to.index,
                            flow_from=False,
                        ),
                        calculate_incident_flow(
                            self.flow_matrix_ub,
                            r.index,
                            process_to.index,
                            flow_from=False,
                        ),
                    )
                    for r in self._resources
                ]
            else:
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
            process_from is None
            and process_to is None
            and resource is not None
        ):
            output = []
            for p1 in self._processes:
                for p2 in self._processes:
                    if p1.index != p2.index:
                        if bounds:
                            output.append(
                                (
                                    p1,
                                    p2,
                                    self.flow_matrix[resource.index][p1.index][
                                        p2.index
                                    ],
                                    self.flow_matrix_lb[resource.index][
                                        p1.index
                                    ][p2.index],
                                    self.flow_matrix_ub[resource.index][
                                        p1.index
                                    ][p2.index],
                                )
                            )
                        else:
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
                if bounds:
                    output.append(
                        (
                            r,
                            self.flow_matrix[r.index][process_from.index][
                                process_to.index
                            ],
                            self.flow_matrix_lb[r.index][process_from.index][
                                process_to.index
                            ],
                            self.flow_matrix_ub[r.index][process_from.index][
                                process_to.index
                            ],
                        )
                    )
                else:
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
            and resource is not None
        ):
            if bounds:
                return (
                    calculate_incident_flow(
                        self.flow_matrix,
                        resource.index,
                        process_from.index,
                        flow_from=True,
                    ),
                    calculate_incident_flow(
                        self.flow_matrix_lb,
                        resource.index,
                        process_from.index,
                        flow_from=True,
                    ),
                    calculate_incident_flow(
                        self.flow_matrix_ub,
                        resource.index,
                        process_from.index,
                        flow_from=True,
                    ),
                )
            else:
                return calculate_incident_flow(
                    self.flow_matrix,
                    resource.index,
                    process_from.index,
                    flow_from=True,
                )

        elif (
            process_from is None
            and process_to is not None
            and resource is not None
        ):
            if bounds:
                return (
                    calculate_incident_flow(
                        self.flow_matrix,
                        resource.index,
                        process_to.index,
                        flow_from=False,
                    ),
                    calculate_incident_flow(
                        self.flow_matrix_lb,
                        resource.index,
                        process_to.index,
                        flow_from=False,
                    ),
                    calculate_incident_flow(
                        self.flow_matrix_ub,
                        resource.index,
                        process_to.index,
                        flow_from=False,
                    ),
                )
            else:
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
            if bounds:
                return (
                    self.flow_matrix[resource.index][process_from.index][
                        process_to.index
                    ],
                    self.flow_matrix_lb[resource.index][process_from.index][
                        process_to.index
                    ],
                    self.flow_matrix_ub[resource.index][process_from.index][
                        process_to.index
                    ],
                )
            else:
                return self.flow_matrix[resource.index][process_from.index][
                    process_to.index
                ]

    @overload
    def cumulative_resource(
        self, *, bounds: bool = False
    ) -> Union[
        List[Tuple[Process, Resource, float]],
        List[Tuple[Process, Resource, float, float, float]],
    ]:
        """
        bounds: Whether or not to calculate bounds

        Returns the amount of each resource used for the entire chain of processes that led to each process.
        """
        ...

    @overload
    def cumulative_resource(
        self, *, process: Process, bounds: bool = False
    ) -> Union[
        List[Tuple[Resource, float]],
        List[Tuple[Resource, float, float, float]],
    ]:
        """
        process: The process using resource
        bounds: Whether or not to calculate bounds

        Returns the amount of each resource used for the entire chain of processes that led to this process.
        """
        ...

    @overload
    def cumulative_resource(
        self, *, resource: Resource, bounds: bool = False
    ) -> Union[
        List[Tuple[Process, float]], List[Tuple[Process, float, float, float]]
    ]:
        """
        resource: The resource we are measuring
        bounds: Whether or not to calculate bounds

        Returns the amount of resource used for the entire chain of processes that led to each process.
        """
        ...

    @overload
    def cumulative_resource(
        self, *, process: Process, resource: Resource, bounds: bool = False
    ) -> Union[float, Tuple[float, float, float]]:
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
        List[Tuple[Process, Resource, float]],
        List[Tuple[Resource, float]],
        List[Tuple[Process, float]],
        float,
        List[Tuple[Process, Resource, float, float, float]],
        List[Tuple[Resource, float, float, float]],
        List[Tuple[Process, float, float, float]],
        Tuple[float, float, float],
    ]:
        if process is None and resource is None:
            output = []
            for p in self._processes:
                for r in self._resources:
                    if bounds:
                        output.append(
                            (
                                p,
                                r,
                                self.cumulative_resource_matrix[r.index][
                                    p.index
                                ],
                                self.cumulative_resource_matrix_lb[r.index][
                                    p.index
                                ],
                                self.cumulative_resource_matrix_ub[r.index][
                                    p.index
                                ],
                            )
                        )
                    else:
                        output.append(
                            (
                                p,
                                r,
                                self.cumulative_resource_matrix[r.index][
                                    p.index
                                ],
                            )
                        )
            return output
        elif process is not None and resource is None:
            if bounds:
                return list(
                    zip(
                        self._resources,
                        self.cumulative_resource_matrix[:, process.index],
                        self.cumulative_resource_matrix_lb[:, process.index],
                        self.cumulative_resource_matrix_ub[:, process.index],
                    )
                )
            else:
                return list(
                    zip(
                        self._resources,
                        self.cumulative_resource_matrix[:, process.index],
                    )
                )
        elif resource is not None and process is None:
            if bounds:
                return list(
                    zip(
                        self._processes,
                        self.cumulative_resource_matrix[resource.index],
                        self.cumulative_resource_matrix_lb[resource.index],
                        self.cumulative_resource_matrix_ub[resource.index],
                    )
                )
            else:
                return list(
                    zip(
                        self._processes,
                        self.cumulative_resource_matrix[resource.index],
                    )
                )
        else:
            assert resource is not None and process is not None
            if bounds:
                return (
                    self.cumulative_resource_matrix[resource.index][
                        process.index
                    ],
                    self.cumulative_resource_matrix_lb[resource.index][
                        process.index
                    ],
                    self.cumulative_resource_matrix_ub[resource.index][
                        process.index
                    ],
                )
            else:
                return self.cumulative_resource_matrix[resource.index][
                    process.index
                ]
