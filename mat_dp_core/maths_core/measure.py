from functools import reduce
from typing import List, Optional, Sequence, Tuple, Union, overload

import numpy as np
from numpy import ndarray

from .constraints import EqConstraint, LeConstraint
from .processes import Process, Processes, ProcessExpr
from .resources import Resource, Resources
from .solve import solve


def calculate_incident_flow(
    flow_matrix, resource_index, process_index, flow_from: bool
) -> float:
    if flow_from:
        column = flow_matrix[resource_index, process_index, :]
    else:
        column = flow_matrix[resource_index, :, process_index]
    return np.sum(column, where=column > 0)


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
    elif arg1 is not None and arg2 is not None:
        return resource_process_array[arg2.index][arg1.index]
    else:
        assert False


def construct_resource_matrix(
    process_produces: ndarray, run_vector: ndarray
) -> ndarray:
    """
    process_produces - A (resource, process) array describing the resources consumed
    and produced by each process
    run_vector - A (process) vector displaying the runs of each process

    returns the resource_matrix (resource, process), the resource produced or consumed by each process
    """
    return (
        np.full(
            process_produces.shape,
            run_vector,
        )
        * process_produces
    )


def construct_flow_matrix(resource_matrix: ndarray) -> ndarray:
    """
    resource_matrix - A (resource, process) array describing the resource
    produced or consumed by each process

    returns the flow_matrix (resource, process1, process2), the flow in a particular resource
    from process1 to process2
    """
    total_res_produced_vector = np.sum(
        resource_matrix, where=resource_matrix > 0, axis=1
    )
    produced = np.where(resource_matrix > 0, resource_matrix, 0)
    consumed = np.where(resource_matrix < 0, resource_matrix, 0)
    reciprocal_total_res = np.reciprocal(
        total_res_produced_vector,
        where=total_res_produced_vector != 0,
        dtype=float,
    )
    unreflected_flow_matrix = np.einsum(
        "i, ij, ik -> ijk", reciprocal_total_res, consumed, produced
    )
    return np.subtract(
        unreflected_flow_matrix,
        np.transpose(unreflected_flow_matrix, axes=(0, 2, 1)),
    )


class Measure:
    _resources: Resources
    _processes: Processes
    _run_vector: ndarray  # processes
    _process_produces: ndarray  # (resources, processes)
    _resource_matrix: Optional[ndarray]  # (resource, process)
    _flow_matrix: Optional[ndarray]  # (resource, process, process)
    _cumulative_resource_matrix: Optional[ndarray]  # (resource, process)

    def __init__(
        self,
        resources: Resources,
        processes: Processes,
        constraints: Sequence[Union[EqConstraint, LeConstraint]],
        objective: Optional[ProcessExpr] = None,
        maxiter: Optional[int] = None,
        allow_inconsistent_order_of_mag: bool = False,
    ):
        for process in processes:
            process.array.resize(len(resources), refcheck=False)
        # Pad arrays out to the correct size:
        # The processes weren't necessarily aware of the total number of
        # resources at the time they were created
        self._resources = resources
        self._processes = processes
        self._process_produces = np.transpose(
            np.array([process.array for process in processes])
        )
        self._allow_inconsistent_order_of_mag = allow_inconsistent_order_of_mag
        self._run_vector = solve(
            resources=resources,
            processes=processes,
            process_produces=self._process_produces,
            constraints=constraints,
            objective=objective,
            maxiter=maxiter,
            allow_inconsistent_order_of_mag=self._allow_inconsistent_order_of_mag,
        )
        self._resource_matrix = None
        self._flow_matrix = None
        self._cumulative_resource_matrix = None

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
            return list(zip(self._processes, self._run_vector))
        else:
            return self._run_vector[process.index]

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
        if self._resource_matrix is None:
            self._resource_matrix = construct_resource_matrix(
                self._process_produces, self._run_vector
            )
        return extract_from_resource_process_array(
            self._resource_matrix,
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
        if self._resource_matrix is None:
            self._resource_matrix = construct_resource_matrix(
                self._process_produces, self._run_vector
            )
        if self._flow_matrix is None:
            self._flow_matrix = construct_flow_matrix(self._resource_matrix)

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
                                    self._flow_matrix[r.index][p1.index][
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
                                self._flow_matrix[arg1.index][p1.index][
                                    p2.index
                                ],
                            )
                        )
            return output
        elif isinstance(arg1, Process) and arg2 is not None and arg3 is None:
            output = []
            if arg1.index == arg2.index:
                raise ValueError(f"Same process {arg1.name} supplied")
            for r in self._resources:
                output.append(
                    (
                        r,
                        self._flow_matrix[r.index][arg1.index][arg2.index],
                    )
                )
            return output
        elif arg1 is not None and arg2 is not None and arg3 is not None:
            assert isinstance(arg1, Process)
            if arg1.index == arg2.index:
                raise ValueError(f"Same process {arg1.name} supplied")
            return self._flow_matrix[arg3.index][arg1.index][arg2.index]
        else:
            assert False

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

        if self._resource_matrix is None:
            self._resource_matrix = construct_resource_matrix(
                self._process_produces, self._run_vector
            )
        if self._flow_matrix is None:
            self._flow_matrix = construct_flow_matrix(self._resource_matrix)

        if resource is None:
            return [
                (
                    r,
                    calculate_incident_flow(
                        self._flow_matrix,
                        r.index,
                        process.index,
                        flow_from=True,
                    ),
                )
                for r in self._resources
            ]
        else:
            return calculate_incident_flow(
                self._flow_matrix,
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

        if self._resource_matrix is None:
            self._resource_matrix = construct_resource_matrix(
                self._process_produces, self._run_vector
            )
        if self._flow_matrix is None:
            self._flow_matrix = construct_flow_matrix(self._resource_matrix)

        if resource is None:
            return [
                (
                    r,
                    calculate_incident_flow(
                        self._flow_matrix,
                        r.index,
                        process.index,
                        flow_from=False,
                    ),
                )
                for r in self._resources
            ]
        else:
            return calculate_incident_flow(
                self._flow_matrix,
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
        def make_eq_constraints(
            production_matrix: ndarray,
            processes: Processes,
            run_vector: ndarray,
        ) -> List[EqConstraint]:
            def make_eq_constraint(
                process1: Process, process2: Process, p2_over_p1: float
            ) -> EqConstraint:
                """
                Given two processes and the ratio between them make an eq_constraint.
                """
                return EqConstraint(
                    f"{process1.name}_{process2.name}_1:{p2_over_p1}ratio",
                    process1 - p2_over_p1 * process2,
                    0,
                )

            def identify_process_index_pairs(
                production_matrix,
            ) -> List[Tuple[int, int]]:
                """
                Identify pairs of process indices that both produce the same resource
                """
                final_pairs = []
                for resource in production_matrix:
                    non_zero_elems = np.nonzero(resource)[0]
                    if len(non_zero_elems) > 1:
                        pairs = [
                            (non_zero_elems[0], i) for i in non_zero_elems[1:]
                        ]
                        final_pairs += pairs
                return final_pairs

            process_pairs = identify_process_index_pairs(production_matrix)

            eq_constraints = []
            for process1_index, process2_index in process_pairs:
                process1 = processes[int(process1_index)]
                process2 = processes[int(process2_index)]
                process1_runs = run_vector[process1_index]
                process2_runs = run_vector[process2_index]
                p2_over_p1 = process2_runs / process1_runs
                eq_constraints.append(
                    make_eq_constraint(process1, process2, p2_over_p1)
                )
            return eq_constraints

        if self._cumulative_resource_matrix is None:
            objective: ProcessExpr = reduce(
                lambda x, y: x + y,
                [process * 1 for process in self._processes],
            )
            production_matrix = np.where(
                self._process_produces > 0, self._process_produces, 0
            )
            eq_cons = make_eq_constraints(
                production_matrix, self._processes, self._run_vector
            )
            process_process_matrix = np.array(
                [
                    solve(
                        self._resources,
                        self._processes,
                        self._process_produces,
                        constraints=[
                            EqConstraint(
                                f"{process.name}_no_runs",
                                process,
                                self._run_vector[process.index],
                            )
                        ]
                        + eq_cons,
                        objective=objective,
                        maxiter=None,
                        allow_inconsistent_order_of_mag=self._allow_inconsistent_order_of_mag,
                    )
                    for process in self._processes
                ],
                dtype=float,
            )

            self._cumulative_resource_matrix = np.einsum(
                "ij, kj -> ki", process_process_matrix, production_matrix
            )
        return extract_from_resource_process_array(
            self._cumulative_resource_matrix,
            self._resources,
            self._processes,
            (arg1, arg2),
        )
