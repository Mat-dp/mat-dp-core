from functools import reduce
from itertools import starmap
from typing import (
    List,
    MutableSequence,
    Optional,
    Sequence,
    Tuple,
    Union,
    overload,
)

import numpy as np
from numpy import ndarray
from scipy import linalg
from scipy.optimize import linprog
from sympy import Matrix

ResourceName = str
Unit = str


class Resource:
    index: int
    _parent: "Resources"

    def __init__(self, index: int, parent: "Resources"):
        self.index = index
        self._parent = parent

    @property
    def name(self) -> str:
        return self._parent._resources[self.index][0]

    @property
    def unit(self) -> str:
        return self._parent._resources[self.index][1]

    def __repr__(self):
        return f"<Resource: {self.name}>"


class Resources:
    _resources: MutableSequence[Tuple[ResourceName, Unit]]

    def __init__(self) -> None:
        self._resources = []

    def create(self, name: ResourceName, unit: Unit = "ea") -> Resource:
        """
        Create a resource
        """
        resource_out = self[len(self._resources)]
        self._resources.append(
            (
                name,
                unit,
            )
        )
        return resource_out

    def load(
        self, resources: Sequence[Tuple[ResourceName, Unit]]
    ) -> List[Resource]:
        """
        Load some additional resources in bulk
        """
        return list(starmap(self.create, resources))

    def dump(self) -> Sequence[Tuple[ResourceName, Unit]]:
        """
        Dump resources in bulk
        """
        return self._resources

    def __len__(self):
        return len(self._resources)

    def __getitem__(self, arg: Union[int, str]):
        if isinstance(arg, int):
            if arg > len(self._resources):
                raise IndexError("list index out of range")
            else:
                return Resource(index=arg, parent=self)
        else:
            results = [
                i for i, (name, _) in enumerate(self._resources) if name == arg
            ]
            if len(results) == 0:
                raise KeyError(f"'{arg}'")
            elif len(results) > 1:
                raise KeyError(f"Name {arg} non unique: please use index")
            else:
                return Resource(index=results[0], parent=self)

    def __iter__(self):
        return map(self.__getitem__, range(len(self)))


class ProcessExpr:
    _processes: List["Process"]

    def __init__(self, _processes: List["Process"]):
        self._processes = _processes

    def __add__(self, other: Union["ProcessExpr", "Process"]) -> "ProcessExpr":
        if isinstance(other, ProcessExpr):
            return ProcessExpr(self._processes + other._processes)
        else:
            return ProcessExpr(self._processes + [other])

    def __mul__(self, other: float) -> "ProcessExpr":
        if other == 1:
            return self
        for element in self._processes:
            element.multiplier = element.multiplier * other
        return self

    def __rmul__(self, other: float) -> "ProcessExpr":
        return self * other

    def __neg__(self):
        for element in self._processes:
            element.multiplier = -element.multiplier
        return self

    def __sub__(self, other):
        return self + -other

    def __repr__(self) -> str:
        return "<ProcessExpr {}>".format(
            " + ".join(map(format, self._processes))
        )

    def __format__(self, format_spec: str) -> str:
        return "{}".format(" + ".join(map(format, self._processes)))

    def __getitem__(self, arg):
        return self._processes[arg]

    def __len__(self):
        return len(self._processes)

    def __iter__(self):
        return map(self.__getitem__, range(len(self)))


ProcessName = str


class Process:
    _parent: "Processes"
    index: int
    multiplier: float

    def __init__(self, index: int, parent: "Processes"):
        self._parent = parent
        self.index = index
        self.multiplier = 1

    @property
    def name(self) -> str:
        return self._parent._processes[self.index][0]

    @property
    def array(self) -> ndarray:
        return self._parent._processes[self.index][1]

    def __mul__(self, other: float) -> ProcessExpr:
        self.multiplier *= other
        return ProcessExpr([self])

    def __rmul__(self, other: float) -> ProcessExpr:
        return self * other

    def __add__(self, other: Union["Process", ProcessExpr]) -> ProcessExpr:
        return self * 1 + other * 1

    def __repr__(self) -> str:
        return f"<Process: {self.name}" + (
            ">" if self.multiplier == 1 else " * {self.multiplier}>"
        )

    def __format__(self, format_spec: str) -> str:
        return f"{self.name}{'' if self.multiplier == 1 else f' * {self.multiplier}'}"

    def __neg__(self):
        return self * -1

    def __sub__(self, other):
        return self + -other


class Processes:
    # Maps process names to resource demands
    _processes: MutableSequence[Tuple[ProcessName, ndarray]]

    def __init__(self) -> None:
        self._processes = []

    def create(
        self, name: ProcessName, *resources: Tuple[Resource, float]
    ) -> Process:
        res_max_index = (
            max((resource.index for (resource, _) in resources)) + 1
        )
        array = np.zeros(res_max_index)
        for (resource, v) in resources:
            i = resource.index
            array[i] = v
        process_inner = (name, array)
        process_out = self[len(self._processes)]
        self._processes.append(process_inner)
        return process_out

    def load(
        self,
        processes: Sequence[
            Tuple[ProcessName, Sequence[Tuple[Resource, float]]]
        ],
    ) -> List[Process]:
        """
        Load some additional processes in bulk
        """
        return list(
            starmap(
                self.create,
                [
                    [process_name, *resources]
                    for process_name, resources in processes
                ],
            )
        )

    def dump(self) -> Sequence[Tuple[ProcessName, ndarray]]:
        """
        Dump processes in bulk
        """
        return self._processes

    def __len__(self):
        return len(self._processes)

    def __getitem__(self, arg: Union[int, str]):
        if isinstance(arg, int):
            if arg > len(self._processes):
                raise IndexError("list index out of range")
            else:
                return Process(index=arg, parent=self)
        else:
            results = [
                i for i, (name, _) in enumerate(self._processes) if name == arg
            ]
            if len(results) == 0:
                raise KeyError(f"'{arg}'")
            elif len(results) > 1:
                raise KeyError(f"Name {arg} non unique: please use index")
            else:
                return Process(index=results[0], parent=self)

    def __iter__(self):
        return map(self.__getitem__, range(len(self)))


def pack_constraint(constraint: Union[Process, ProcessExpr]) -> ndarray:
    constraint *= 1  # Converts Process to ProcessExpr
    proc_max_index = max((process.index for process in constraint)) + 1
    array = np.zeros(proc_max_index)
    for process in constraint:
        array[process.index] = process.multiplier
    return array


class _Constraint:
    name: str
    array: ndarray
    bound: float

    def __init__(
        self,
        name: str,
        weighted_processes: Union[Process, ProcessExpr],
        bound: float,
    ):
        # TODO: investigate whether it would be nice to add a constraint by np.array
        self.name = name
        self.array = pack_constraint(weighted_processes)
        self.bound = bound
        self.weighted_processes = weighted_processes


class EqConstraint(_Constraint):
    """
    Equality constraint
    """

    def __repr__(self) -> str:
        return f"<EqConstraint: {self.name}\nEquation:{self.weighted_processes} == {self.bound}>"

    def __format__(self, format_spec: str) -> str:
        return f"{self.weighted_processes} == {self.bound}"


class LeConstraint(_Constraint):
    """
    Less than or equal constraint
    """

    def __repr__(self) -> str:
        return f"<LeConstraint: {self.name}\nEquation:{self.weighted_processes} == {self.bound}>"

    def __format__(self, format_spec: str) -> str:
        return f"{self.weighted_processes} == {self.bound}"


def GeConstraint(
    name: str, weighted_processes: Union[Process, ProcessExpr], bound: float
):
    return LeConstraint(name, -weighted_processes, -bound)


class IterationLimitReached(Exception):
    def __init__(self, n_iters):
        self.n_iters = n_iters
        super().__init__(f"Iteration limit reached with {n_iters} iterations")


class Overconstrained(Exception):
    def __init__(
        self,
        rec_constraints: Sequence[
            Tuple[Resource, float, List[Process], List[Process]]
        ],
        eq_constraints: Sequence[Tuple[EqConstraint, float]],
        le_constraints: Sequence[Tuple[LeConstraint, float]],
    ):
        def constraints_to_rec_string(
            constraints: Sequence[
                Tuple[Resource, float, List[Process], List[Process]]
            ]
        ) -> str:
            rec_strings = []
            for (constraint, val, producers, consumers) in constraints:
                producer_names = ", ".join([p.name for p in producers])
                consumer_names = ", ".join([p.name for p in consumers])
                if val < 0:
                    format_str = f"Increase runs of {producer_names} or decrease runs of {consumer_names}"
                elif val > 0:
                    format_str = f"Increase runs of {consumer_names} or decrease runs of {producer_names}"
                else:
                    format_str = None
                if format_str is not None:
                    full_string = (
                        f"{constraint} => {val}: "
                        + format_str.format(constraint.name)
                    )
                    rec_strings.append(full_string)
            return "\n".join(rec_strings)

        self.rec_constraints = rec_constraints
        self.eq_constraints = eq_constraints
        self.le_constraints = le_constraints
        # TODO Fix residual val being non-zero
        message_list = ["Overconstrained problem:"]
        if len(rec_constraints) > 0:
            message_list += [
                "resources:",
                constraints_to_rec_string(rec_constraints),
            ]
        if len(eq_constraints) > 0:
            message_list += [
                "eq_constraints:",
                "\n".join([f"{c} => {val}" for (c, val) in eq_constraints]),
            ]
        if len(le_constraints) > 0:
            message_list += "le_constraints:", "\n".join(
                [f"{c} => {val}" for (c, val) in le_constraints]
            )

        super().__init__("\n".join(message_list))


class Underconstrained(Exception):
    pass


class UnboundedSolution(Exception):
    pass


class NumericalDifficulties(Exception):
    pass


class Measure:
    _resources: Resources
    _processes: Processes
    _run_vector: ndarray  # cols: processes
    _process_demands: Optional[
        ndarray
    ]  # cols: processes, rows: resources (resources, processes)

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
    ):
        self._resources = resources
        self._processes = processes
        self._run_vector = self._solve(
            resources=resources,
            processes=processes,
            constraints=constraints,
            objective=objective,
            maxiter=maxiter,
        )
        self._resource_matrix = None
        self._flow_matrix = None
        self._cumulative_resource_matrix = None
        self._process_demands = None

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
        if self._process_demands is None:
            self._process_demands = np.transpose(
                np.array([process.array for process in self._processes])
            )
        if self._resource_matrix is None:
            self._resource_matrix = (
                np.full(
                    (len(self._resources), len(self._processes)),
                    self._run_vector,
                )
                * self._process_demands
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
        if self._process_demands is None:
            self._process_demands = np.transpose(
                np.array([process.array for process in self._processes])
            )
        if self._resource_matrix is None:
            self._resource_matrix = (
                np.full(
                    (len(self._resources), len(self._processes)),
                    self._run_vector,
                )
                * self._process_demands
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
        assert self._process_demands is not None
        if self._cumulative_resource_matrix is None:
            objective: ProcessExpr = reduce(
                lambda x, y: x + y,
                [process * 1 for process in self._processes],
            )
            production_matrix = np.where(
                self._process_demands > 0, self._process_demands, 0
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

        # Add constraints for each process
        for process in processes:
            process.array.resize(len(resources), refcheck=False)
        # Pad arrays out to the correct size:
        # The processes weren't necessarily aware of the total number of
        # resources at the time they were created

        A_proc = np.transpose(
            np.array([process.array for process in processes])
        )
        b_proc = np.zeros(len(resources))

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

        A_eq = np.concatenate((A_proc, A_eq_con))
        b_eq = np.concatenate((b_proc, b_eq_con))

        if objective is None:
            objective = reduce(
                lambda x, y: x + y,
                [process * 1 for process in self._processes],
            )

        # Build objective vector
        coefficients = pack_constraint(objective)
        coefficients.resize(len(processes))
        # Solve
        # TODO: optimise with callback
        # TODO: optimise method

        options = {}
        if maxiter is not None:
            options["maxiter"] = maxiter

        res = linprog(
            c=coefficients,
            A_ub=A_le_con,
            b_ub=b_le_con,
            A_eq=A_eq,
            b_eq=b_eq,
            options=options,
        )

        if res.status == 0:  # Optimization terminated successfully
            return res.x
        elif res.status == 1:  # Iteration limit reached
            raise IterationLimitReached(res.nit)
        elif res.status == 2:  # Problem appears to be infeasible
            res_constraints = []

            for i, v in enumerate(res.con[: len(resources)]):
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
                    for i, v in enumerate(res.con[len(resources) :])
                    if v != 0
                ],
                [
                    (le_constraints[i], v)
                    for i, v in enumerate(res.slack)
                    if v < 0
                ],
            )
        elif res.status == 3:  # Problem appears to be unbounded
            raise UnboundedSolution
        elif res.status == 4:  # Numerical difficulties encountered
            raise NumericalDifficulties
        else:
            assert False
