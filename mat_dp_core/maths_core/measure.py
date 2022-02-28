import warnings
from functools import reduce
from typing import List, Optional, Sequence, Tuple, Union, overload

import numpy as np
from numpy import ndarray
from scipy.optimize import linprog

from .constraints import (
    EqConstraint,
    LeConstraint,
    _Constraint,
    pack_constraint,
)
from .exceptions import (
    InconsistentOrderOfMagnitude,
    IterationLimitReached,
    NumericalDifficulties,
    Overconstrained,
    UnboundedSolution,
)
from .processes import Process, Processes, ProcessExpr
from .resources import Resource, Resources


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
        self._run_vector = self._solve(
            resources=resources,
            processes=processes,
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
            self._resource_matrix = (
                np.full(
                    (len(self._resources), len(self._processes)),
                    self._run_vector,
                )
                * self._process_produces
            )
        if arg1 is None and arg2 is None:
            output = []
            for p in self._processes:
                for r in self._resources:
                    output.append(
                        (
                            p,
                            r,
                            self._resource_matrix[r.index][p.index],
                        )
                    )
            return output
        elif isinstance(arg1, Process) and arg2 is None:
            return list(
                zip(
                    self._resources,
                    self._resource_matrix[:, arg1.index],
                )
            )
        elif isinstance(arg1, Resource) and arg2 is None:
            return list(
                zip(self._processes, self._resource_matrix[arg1.index])
            )
        elif arg1 is not None and arg2 is not None:
            return self._resource_matrix[arg2.index][arg1.index]
        else:
            assert False

    def _prepare_flow(self):
        if self._resource_matrix is None:
            self._resource_matrix = (
                np.full(
                    (len(self._resources), len(self._processes)),
                    self._run_vector,
                )
                * self._process_produces
            )
        if self._flow_matrix is None:
            total_res_produced_vector = np.sum(
                self._resource_matrix, where=self._resource_matrix > 0, axis=1
            )
            produced = np.where(
                self._resource_matrix > 0, self._resource_matrix, 0
            )
            consumed = np.where(
                self._resource_matrix < 0, self._resource_matrix, 0
            )
            reciprocal_total_res = np.reciprocal(
                total_res_produced_vector,
                where=total_res_produced_vector != 0,
                dtype=float,
            )
            unreflected_flow_matrix = np.einsum(
                "i, ij, ik -> ijk", reciprocal_total_res, consumed, produced
            )

            self._flow_matrix = np.subtract(
                unreflected_flow_matrix,
                np.transpose(unreflected_flow_matrix, axes=(0, 2, 1)),
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
        self._prepare_flow()
        assert self._flow_matrix is not None
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

        self._prepare_flow()
        assert self._flow_matrix is not None

        if resource is None:
            return [
                (
                    r,
                    sum(
                        [
                            flow
                            for flow in self._flow_matrix[
                                r.index, process.index, :
                            ]
                            if flow > 0
                        ]
                    ),
                )
                for r in self._resources
            ]
        else:
            return sum(
                [
                    flow
                    for flow in self._flow_matrix[
                        resource.index, process.index, :
                    ]
                    if flow > 0
                ]
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

        self._prepare_flow()
        assert self._flow_matrix is not None

        if resource is None:
            return [
                (
                    r,
                    sum(
                        [
                            flow
                            for flow in self._flow_matrix[
                                r.index, :, process.index
                            ]
                            if flow > 0
                        ]
                    ),
                )
                for r in self._resources
            ]
        else:
            return sum(
                [
                    flow
                    for flow in self._flow_matrix[
                        resource.index, :, process.index
                    ]
                    if flow > 0
                ]
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

        self._prepare_flow()
        assert self._flow_matrix is not None
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
                    self._solve(
                        self._resources,
                        self._processes,
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

        if arg1 is None and arg2 is None:
            output = []
            for p in self._processes:
                for r in self._resources:
                    output.append(
                        (
                            p,
                            r,
                            self._cumulative_resource_matrix[r.index][p.index],
                        )
                    )
            return output
        elif isinstance(arg1, Process) and arg2 is None:
            return list(
                zip(
                    self._resources,
                    self._cumulative_resource_matrix[:, arg1.index],
                )
            )
        elif isinstance(arg1, Resource) and arg2 is None:
            return list(
                zip(
                    self._processes,
                    self._cumulative_resource_matrix[arg1.index],
                )
            )
        elif arg1 is not None and arg2 is not None:
            return self._cumulative_resource_matrix[arg2.index][arg1.index]
        else:
            assert False

    def _solve(
        self,
        resources: Resources,
        processes: Processes,
        constraints: Sequence[Union[EqConstraint, LeConstraint]] = [],
        objective: Optional[ProcessExpr] = None,
        maxiter: Optional[int] = None,
        allow_inconsistent_order_of_mag: bool = False,
    ):
        """
        Given a system of processes, resources, and constraints, and an optional
        objective, attempt to solve the system.

        If the system is under- or over-constrained, will report so.

        Preconditions:
            *constraints* reference only processes in *processes*
            *processes* reference only resources in *resources*
        """

        def constraints_to_array(
            constraints: List[_Constraint],
        ) -> Tuple[ndarray, ndarray]:
            A_constraint_array = np.zeros((len(constraints), len(processes)))
            b_constraint_array = np.zeros((len(constraints)))

            for i, constraint in enumerate(constraints):
                constraint.array.resize(len(processes), refcheck=False)
                A_constraint_array[i] = constraint.array
                b_constraint_array[i] = constraint.bound

            return A_constraint_array, b_constraint_array

        if len(resources) == 0 and len(processes) == 0:
            raise ValueError("No resources or processes created")
        elif len(resources) == 0:
            raise ValueError("No resources created")
        elif len(processes) == 0:
            raise ValueError("No processes created")

        eq_constraints = [
            constraint
            for constraint in constraints
            if isinstance(constraint, EqConstraint)
        ]
        le_constraints = [
            constraint
            for constraint in constraints
            if isinstance(constraint, LeConstraint)
        ]

        A_eq_con, b_eq_con = constraints_to_array(list(eq_constraints))
        A_le_con, b_le_con = constraints_to_array(list(le_constraints))

        A_eq = np.concatenate((self._process_produces, A_eq_con))
        b_eq = np.concatenate((np.zeros(len(resources)), b_eq_con))

        if objective is None:
            objective = reduce(
                lambda x, y: x + y,
                [process * 1 for process in self._processes],
            )

        # Build objective vector
        coefficients = pack_constraint(objective)
        coefficients.resize(len(processes), refcheck=False)
        # Solve
        # TODO: optimise with callback
        # TODO: optimise method

        options = {}
        if maxiter is not None:
            options["maxiter"] = maxiter

        def get_row_scales(equations: ndarray):
            with warnings.catch_warnings():
                warnings.filterwarnings(
                    "ignore", "divide by zero encountered in log10"
                )

                A_maxima = np.max(np.absolute(equations), axis=1)
                scales = np.nan_to_num(
                    np.power(10, np.floor(np.log10(np.absolute(A_maxima))))
                )
            return np.nan_to_num(np.reciprocal(scales))

        def get_order_ranges(equations: ndarray) -> ndarray:
            with warnings.catch_warnings():
                warnings.filterwarnings(
                    "ignore", "divide by zero encountered in log10"
                )
                mags = np.log10(np.absolute(equations))
            order_ranges = []
            for res in mags:
                new_res_list = []
                for i in res:
                    if i != -np.inf:
                        new_res_list.append(i)
                if len(new_res_list) > 0:
                    order_range = np.ptp(new_res_list)
                else:
                    order_range = 0
                order_ranges.append(order_range)
            return np.array(order_ranges)

        eq_equations = np.concatenate(
            (A_eq, np.resize(b_eq, (len(b_eq), 1))), axis=1
        )
        le_equations = np.concatenate(
            (A_le_con, np.resize(b_le_con, (len(b_le_con), 1))), axis=1
        )

        if not allow_inconsistent_order_of_mag:
            eq_order_range = get_order_ranges(eq_equations)
            le_order_range = get_order_ranges(le_equations)
            order_limit = 6
            eq_order_inconsistent = (
                len(eq_order_range) > 0
                and np.max(eq_order_range) > order_limit
            )
            le_order_inconsistent = (
                len(le_order_range) > 0
                and np.max(le_order_range) > order_limit
            )
            if eq_order_inconsistent or le_order_inconsistent:
                if eq_order_inconsistent:
                    resource_inconsistencies = [
                        (
                            resources[i],
                            [
                                (process, A_eq[i][j])
                                for j, process in enumerate(self._processes)
                                if A_eq[i][j] != 0
                            ],
                            v,
                        )
                        for i, v in enumerate(eq_order_range[: len(resources)])
                        if v > order_limit
                    ]
                    eq_inconsistencies = [
                        (
                            eq_constraints[i],
                            [
                                (process, A_eq[i + len(self._processes)][j])
                                for j, process in enumerate(self._processes)
                                if A_eq[i + len(self._processes)][j] != 0
                            ],
                            v,
                        )
                        for i, v in enumerate(eq_order_range[len(resources) :])
                        if v > order_limit
                    ]
                else:
                    resource_inconsistencies = []
                    eq_inconsistencies = []
                if le_order_inconsistent:
                    le_inconsistencies = [
                        (
                            le_constraints[i],
                            [
                                (process, A_le_con[i][j])
                                for j, process in enumerate(self._processes)
                                if A_le_con[i][j] != 0
                            ],
                            v,
                        )
                        for i, v in enumerate(le_order_range)
                        if v > order_limit
                    ]
                else:
                    le_inconsistencies = []

                raise InconsistentOrderOfMagnitude(
                    resource_inconsistencies,
                    eq_inconsistencies,
                    le_inconsistencies,
                )

        eq_scales = get_row_scales(eq_equations)
        le_scales = get_row_scales(le_equations)
        red_A_eq = np.einsum("ij, i -> ij", A_eq, eq_scales)
        red_b_eq = np.einsum("i, i -> i", b_eq, eq_scales)
        red_A_ub = np.einsum("ij, i -> ij", A_le_con, le_scales)
        red_b_ub = np.einsum("i, i -> i", b_le_con, le_scales)

        res = linprog(
            c=coefficients,
            A_ub=red_A_ub,
            b_ub=red_b_ub,
            A_eq=red_A_eq,
            b_eq=red_b_eq,
            options=options,
        )

        if res.status == 0:  # Optimization terminated successfully
            return res.x
        elif res.status == 1:  # Iteration limit reached
            raise IterationLimitReached(res.nit)
        elif res.status == 2:  # Problem appears to be infeasible
            res_constraints = []
            rescaled_con = np.einsum(
                "i, i -> i", res.con, np.nan_to_num(np.reciprocal(eq_scales))
            )
            rescaled_slack = np.einsum(
                "i, i -> i", res.slack, np.nan_to_num(np.reciprocal(le_scales))
            )
            for i, v in enumerate(rescaled_con[: len(resources)]):
                if v != 0:
                    prod_con = A_eq[int(i)]
                    producers_i = np.nonzero(
                        np.where(prod_con > 0, prod_con, 0)
                    )
                    consumers_i = np.nonzero(
                        np.where(prod_con < 0, prod_con, 0)
                    )
                    producers = (
                        [processes[int(v)] for v in producers_i]
                        if len(producers_i) > 0
                        else []
                    )
                    consumers = (
                        [processes[int(v)] for v in consumers_i]
                        if len(consumers_i) > 0
                        else []
                    )
                    res_constraints.append(
                        (resources[int(i)], -v, producers, consumers)
                    )

            raise Overconstrained(
                res_constraints,
                [
                    (eq_constraints[i], v)
                    for i, v in enumerate(rescaled_con[len(resources) :])
                    if v != 0
                ],
                [
                    (le_constraints[i], v)
                    for i, v in enumerate(rescaled_slack)
                    if v < 0
                ],
            )
        elif res.status == 3:  # Problem appears to be unbounded
            process_sols = [
                (process, res.x[process.index]) for process in processes
            ]
            raise UnboundedSolution(process_sols)
        elif res.status == 4:  # Numerical difficulties encountered
            raise NumericalDifficulties
        else:
            assert False
