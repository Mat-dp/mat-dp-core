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
    _resources: MutableSequence[Tuple[ResourceName, Unit]] = []

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

    def load(self, resources: Sequence[Tuple[ResourceName, Unit]]):
        """
        Load some additional resources in bulk
        """
        starmap(self.create, resources)

    def dump(self) -> Sequence[Tuple[ResourceName, Unit]]:
        """
        Dump resources in bulk
        """
        return self._resources

    def __len__(self):
        return len(self._resources)

    def __getitem__(self, arg):
        return Resource(index=arg, parent=self)

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
    _processes: MutableSequence[Tuple[ProcessName, ndarray]] = []

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
    ):
        """
        Load some additional processes in bulk
        """
        starmap(
            self.create,
            [
                [process_name, *resources]
                for process_name, resources in processes
            ],
        )

    def dump(self) -> Sequence[Tuple[ProcessName, ndarray]]:
        """
        Dump processes in bulk
        """
        return self._processes

    def __len__(self):
        return len(self._processes)

    def __getitem__(self, arg):
        return Process(index=arg, parent=self)

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
        proc_constraints: Sequence[Tuple[Process, float]],
        eq_constraints: Sequence[Tuple[EqConstraint, float]],
        le_constraints: Sequence[Tuple[LeConstraint, float]],
    ):
        self.proc_constraints = proc_constraints
        self.eq_constraints = eq_constraints
        self.le_constraints = le_constraints
        # TODO Fix residual val being non-zero
        super().__init__(
            "Overconstrained problem:\nprocesses:\n"
            + "\n".join([f"{c} => {val}" for (c, val) in proc_constraints])
            + "\neq_constraints:\n"
            + "\n".join([f"{c} => {val}" for (c, val) in eq_constraints])
            + "\nle_constraints:\n"
            + "\n".join([f"{c} => {val}" for (c, val) in le_constraints])
        )


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
        maxiter: int = None,
    ):
        self._resources = resources
        self._processes = processes
        self._run_vector = self._solve(
            resources, processes, constraints, objective, maxiter
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
        self._prepare_flow()  # TODO: Implement
        assert self._flow_matrix is not None
        if self._cumulative_resource_matrix is None:
            raise NotImplementedError

        if arg1 is None and arg2 is None:
            raise NotImplementedError
        elif isinstance(arg1, Process) and arg2 is None:
            raise NotImplementedError
        elif isinstance(arg1, Resource) and arg2 is None:
            raise NotImplementedError
        elif arg1 is not None and arg2 is not None:
            raise NotImplementedError
        else:
            assert False

    def _solve(
        self,
        resources: Resources,
        processes: Processes,
        constraints: Sequence[Union[EqConstraint, LeConstraint]],
        objective: Optional[ProcessExpr],
        maxiter: Optional[int],
    ):
        """
        Given a system of processes, resources, and constraints, and an optional
        objective, attempt to solve the system.

        If the system is under- or over-constrained, will report so.

        Preconditions:
            *constraints* reference only processes in *processes*
            *processes* reference only resources in *resources*
        """
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

        # Add constraints for each specified constraint

        A_eq_con_list = []
        b_eq_con_list = []
        A_le_con_list = []
        b_le_con_list = []
        eq_constraints = []
        le_constraints = []
        for constraint in constraints:
            constraint.array.resize(len(processes))
            if isinstance(constraint, EqConstraint):
                eq_constraints.append(constraint)
                A_eq_con_list.append(constraint.array)
                b_eq_con_list.append(constraint.bound)
            elif isinstance(constraint, LeConstraint):
                le_constraints.append(constraint)
                A_le_con_list.append(constraint.array)
                b_le_con_list.append(constraint.bound)
            else:
                assert False
        A_eq_con = np.array(A_eq_con_list)
        b_eq_con = np.array(b_eq_con_list)
        A_le_con = np.array(A_le_con_list)
        b_le_con = np.array(b_le_con_list)

        if objective is None:
            try:
                # TODO: confirm that the inequalities were correctly satisfied
                return linalg.solve(
                    a=A_proc + A_eq_con + A_le_con,
                    b=b_proc + b_eq_con + b_le_con,
                )
            except linalg.LinAlgError:
                # Determine whether the solution was under- or overconstrained
                # https://towardsdatascience.com/how-do-you-use-numpy-scipy-and-sympy-to-solve-systems-of-linear-equations-9afed2c388af
                augmented_A = Matrix(
                    [A + [b] for A, b in zip(A_eq_con, b_eq_con)]
                    + [A + [b] for A, b in zip(A_le_con, b_le_con)]
                )
                rref = augmented_A.rref()
                if len(rref[1]) < len(rref[0]):
                    # Final row of RREF is zero if underconstrained
                    # TODO: calculate how the system is ill-specified by inspecting
                    # the matrix in RREF
                    raise Underconstrained()
                else:
                    raise Overconstrained([], [], [])
        else:
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
                A_ub=A_le_con if len(A_le_con) > 0 else None,
                b_ub=b_le_con if len(b_le_con) > 0 else None,
                A_eq=np.concatenate((A_proc, A_eq_con)),
                b_eq=np.concatenate((b_proc, b_eq_con)),
                options=options,
            )

            if res.status == 0:
                # Optimization terminated successfully
                return res.x
            elif res.status == 1:
                # Iteration limit reached
                raise IterationLimitReached(res.nit)
            elif res.status == 2:
                # Problem appears to be infeasible
                print(res.con)

                raise Overconstrained(
                    [
                        (processes[i], v)
                        for i, v in enumerate(res.con[: len(processes)])
                        if v != 0
                    ],
                    [
                        (eq_constraints[i], v)
                        for i, v in enumerate(res.con[len(processes) :])
                        if v != 0
                    ],
                    [
                        (le_constraints[i], v)
                        for i, v in enumerate(res.slack)
                        if v < 0
                    ],
                )  # TODO: sort out typing warning
            elif res.status == 3:
                # Problem appears to be unbounded
                raise UnboundedSolution
            elif res.status == 4:
                # Numerical difficulties encountered
                raise NumericalDifficulties
            else:
                assert False
