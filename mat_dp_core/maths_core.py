from collections.abc import Sequence
from dataclasses import dataclass
from inspect import stack
import numpy as np
from numpy.typing import ArrayLike
from scipy import linalg
from scipy.optimize import linprog
from sympy import Matrix
from sys import exc_info
from typing import Dict, List, Optional, Tuple, overload, Union


ResourceName = str
Unit = str
Resource = int


class Resources:
    resources: List[Tuple[ResourceName, Unit]] = []

    def create(self, name: ResourceName, unit: Unit = "ea") -> Resource:
        self.resources.append((name, unit))
        return len(self.resources) - 1

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


class _Process:
    def __init__(self, process_index: int):
        self.process_index = process_index

    def __mul__(self, other: float) -> ProcessExpr:
        return ProcessExpr([(self.process_index, other)])


class Processes:
    # Maps process names to resource constraints
    processes: List[Tuple[ProcessName, ArrayLike]] = []

    def create(self, name: ProcessName, *resources: Tuple[Resource, float]) \
            -> _Process:
        res_max_index = max((i for (i, _) in resources)) + 1
        array = np.zeros(res_max_index)
        for (i, v) in resources:
            array[i] = v
        self.processes.append((name, array))
        return _Process(len(self.processes) - 1)

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

    for (_, a) in processes.processes:
        a.resize(len(processes), refcheck=False)    # TODO: find correct type for this
    # Pad arrays out to the correct size:
    # The processes weren't necessarily aware of the total number of
    # resources at the time they were created
    A_proc = np.transpose(np.array([a for (_, a) in processes.processes]))
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
