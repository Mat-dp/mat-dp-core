from collections.abc import Sequence
from dataclasses import dataclass
import numpy as np
from numpy.typing import ArrayLike
from scipy import linalg
from scipy.optimize import linprog
from sympy import Matrix
from typing import List, Optional, Tuple, Union


ResourceName = str
Unit = str

@dataclass
class _Resource:
    name: ResourceName
    index: int
    unit: Unit = "ea"
    def __repr__(self):
        return f"<Resource: {self.name}>"

class Resources:
    resources: List[_Resource] = []

    def create(self, name: ResourceName, unit: Unit = "ea") -> _Resource:
        resource = _Resource(name = name, index = len(self.resources), unit = unit)
        self.resources.append(resource)
        return resource

    def __len__(self):
        return len(self.resources)


class ProcessExpr:
    processes: List[Tuple[int, float]]

    def __init__(self, processes: List[Tuple[int, float]]):
        self.processes = processes

    def __add__(self, other: "ProcessExpr") -> "ProcessExpr":
        return ProcessExpr(self.processes + other.processes)


def pack_constraint(
        constraint: Union[ProcessExpr, List[Tuple[int, float]]]
        ) -> ArrayLike:
    if isinstance(constraint, ProcessExpr):
        processes = constraint.processes
    else:
        processes = constraint

    proc_max_index = max((i for (i, _) in processes)) + 1
    array = np.zeros(proc_max_index)
    for (i, v) in processes:
        array[i] = v
    return array


class _Constraint:
    name: str
    array: ArrayLike
    bound: float

    def __init__(
            self,
            name: str,
            constraint: Union[ProcessExpr, List[Tuple[int, float]]],
            bound: float):
        # TODO: investigate whether it would be nice to add a constraint by np.array
        self.name = name
        self.array = pack_constraint(constraint)
        self.bound = bound


class EqConstraint(_Constraint):
    """
    Equality constraint
    """


class LeConstraint(_Constraint):
    """
    Less than or equal constraint
    """


def GeConstraint(
        name: str,
        constraint: Union[ProcessExpr, List[Tuple[int, float]]],
        bound: float):
    if isinstance(constraint, ProcessExpr):
        processes = constraint.processes
    else:
        processes = constraint
    return LeConstraint(name, [(i, -v) for (i, v) in processes], -bound)


ProcessName = str

@dataclass
class _Process:
    name: ProcessName
    index: int
    array: ArrayLike

    def __mul__(self, other: float) -> ProcessExpr:
        return ProcessExpr([(self.index, other)])
    
    def __repr__(self) -> str:
        return f"<Process: {self.name}>"


class Processes:
    # Maps process names to resource constraints
    processes: List[_Process] = []

    def create(self, name: ProcessName, *resources: Tuple[_Resource, float]) \
            -> _Process:
        res_max_index = max((resource.index for (resource, _) in resources)) + 1
        array = np.zeros(res_max_index)
        for (resource, v) in resources:
            i = resource.index
            array[i] = v
        process = _Process(name = name, index = len(self.processes), array = array)
        self.processes.append(process)
        return process

    def __len__(self):
        return len(self.processes)


class IterationLimitReached(Exception):
    def __init__(self, n_iters):
        self.n_iters = n_iters
        super().__init__(f"Iteration limit reached with {n_iters} iterations")


class Overconstrained(Exception):
    def __init__(self, constraints: Sequence[Tuple[_Constraint, float]]):
        self.constraints = constraints
        super().__init__(
            "Overconstrained problem:\n" +
            "\n".join([f"{c} => {val}"for (c, val) in constraints])
            )


class Underconstrained(Exception):
    pass


class UnboundedSolution(Exception):
    pass


class NumericalDifficulties(Exception):
    pass


def solve(
        resources: Resources,
        processes: Processes,
        constraints: Sequence[Union[EqConstraint, LeConstraint]],
        objective: Optional[ProcessExpr] = None,
        maxiter: int = None):
    """
    Given a system of processes, resources, and constraints, and an optional
    objective, attempt to solve the system.

    If the system is under- or over-constrained, will report so

    Preconditions:
        *constraints* reference only processes in *processes*
        *processes* reference only resources in *resources*
    """

    # Add constraints for each process
    for process in processes.processes:
        process.array.resize(len(processes), refcheck=False)    # TODO: find correct type for this
    # Pad arrays out to the correct size:
    # The processes weren't necessarily aware of the total number of
    # resources at the time they were created
    A_proc = np.transpose(np.array([process.array for process in processes.processes]))
    b_proc = np.zeros(len(processes))

    # Add constraints for each specified constraint

    Al_eq = []
    bl_eq = []
    Al_le = []
    bl_le = []
    eq_constraints = []
    le_constraints = []
    for constraint in constraints:
        constraint.array.resize(len(processes))    # TODO: find correct type for this
        if isinstance(constraint, EqConstraint):
            eq_constraints.append(constraint)
            Al_eq.append(constraint.array)
            bl_eq.append(constraint.bound)
        elif isinstance(constraint, LeConstraint):
            le_constraints.append(constraint)
            Al_le.append(constraint.array)
            bl_le.append(constraint.bound)
        else:
            assert(False)
    A_eq = np.array(Al_eq)
    b_eq = np.array(bl_eq)
    A_le = np.array(Al_le)
    b_le = np.array(bl_le)

    if objective is None:
        try:
            # TODO: confirm that the inequalities were correctly satisfied
            return linalg.solve(A_proc + A_eq + A_le, b_proc, b_eq + b_le)
        except linalg.LinAlgError:
            # Determine whether the solution was under- or overconstrained
            # https://towardsdatascience.com/how-do-you-use-numpy-scipy-and-sympy-to-solve-systems-of-linear-equations-9afed2c388af
            augmented_A = Matrix(
                [A + [b] for A, b in zip(A_eq, b_eq)] +
                [A + [b] for A, b in zip(A_le, b_le)]
            )
            rref = augmented_A.rref()
            if len(rref[1]) < len(rref[0]):
                # Final row of RREF is zero if underconstrained
                # TODO: calculate how the system is ill-specified by inspecting
                # the matrix in RREF
                raise Underconstrained()
            else:
                raise Overconstrained([])
    else:
        # Build objective vector
        c = pack_constraint(objective)

        # Solve
        # TODO: optimise with callback
        # TODO: optimise method

        options = {}
        if maxiter is not None:
            options["maxiter"] = maxiter

        res = linprog(
                c,
                A_le if len(A_le) > 0 else None,
                b_le if len(b_le) > 0 else None,
                np.concatenate((A_proc, A_eq)),
                np.concatenate((b_proc, b_eq)),
                options=options)

        if res.status == 0:
            # Optimization terminated successfully
            return res.x
        elif res.status == 1:
            # Iteration limit reached
            raise IterationLimitReached(res.nit)
        elif res.status == 2:
            # Problem appears to be infeasible
            raise Overconstrained(
                    [(eq_constraints[i], v) for i, v in enumerate(res.con)
                        if v != 0] +
                    [(le_constraints[i], v) for i, v in enumerate(res.slack)
                        if v < 0])  # TODO: sort out typing warning
        elif res.status == 3:
            # Problem appears to be unbounded
            raise UnboundedSolution
        elif res.status == 4:
            # Numerical difficulties encountered
            raise NumericalDifficulties
        else:
            assert(False)

def generate_process_demands(
    resources: Resources,
    processes: Processes
) -> ArrayLike:

    for process in processes.processes:
        process.array.resize(len(resources), refcheck=False)    # TODO: find correct type for this
    # Pad arrays out to the correct size:
    # The processes weren't necessarily aware of the total number of
    # resources at the time they were created
    A_proc = np.array([process.array for process in processes.processes])
    return A_proc


def calculate_actual_resource(
    process_demands: ArrayLike,     # (process, resource) -> float
    run_vector: ArrayLike           # process -> +ve float
    ) -> ArrayLike:  # actual_resource: (process, resource) -> +ve float
    """
    Given the resource demands of each process, and the number of times
    that each process runs, calculate the number of resources that
    are required by each process.
    """
    actual_resource = np.zeros_like(process_demands)
    for i, runs in enumerate(run_vector):
        actual_resource[i] = process_demands[i]*runs
    return actual_resource

"""
Needs a rethink
def calculate_actual_resource_flow(
    actual_resource: ArrayLike,     # (process, resource) -> +ve float
    demand_policy: ArrayLike        # (process, process, resource) -> +ve float
    ) -> ArrayLike:  # actual_resource_flow: (process, process, resource) -> +ve float
    ""
    Given the number of resources that are required by each process, and the policy
    that defines how processes connect, calculate the number of resources that
    flow through each edge.
    ""
    actual_resource_flow = np.zeros_like(demand_policy)
    for i, in_process in enumerate(demand_policy):
        for j, out_process in enumerate(in_process):
            for k, proportion in enumerate(out_process):
                actual_resource_flow[i][j][k] = proportion*actual_resource[j][k]

    return actual_resource_flow
"""