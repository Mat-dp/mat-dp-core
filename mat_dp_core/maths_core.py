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
    _resources: List[Tuple[ResourceName, Unit]] = []

    def create(self, name: ResourceName, unit: Unit = "ea") -> Resource:
        resource_out = self[len(self._resources)]
        self._resources.append((name, unit,))
        return resource_out

    def __len__(self):
        return len(self._resources)
    
    def __getitem__(self, arg):
        return Resource(index = arg, parent = self)

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
    
    def __rmul__(self, other:float) -> "ProcessExpr":
        return self*other
    
    def __neg__(self):
        for element in self._processes:
            element.multiplier = -element.multiplier
        return self

    def __sub__(self, other):
        return self + -other
    
    def __repr__(self) -> str:
        return "<ProcessExpr {}>".format(' + '.join(map(format,self._processes)))
    
    def __format__(self, format_spec: str) -> str:
        return "{}".format(' + '.join(map(format,self._processes)))
    
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
    def __init__(
        self, 
        index: int,
        parent: "Processes"
    ):
        self._parent = parent
        self.index = index
        self.multiplier = 1
    
    @property
    def name(self) -> str:
        return self._parent._processes[self.index][0]
    
    @property
    def array(self) -> ArrayLike:
        return self._parent._processes[self.index][1]
    
    def __mul__(self, other: float) -> ProcessExpr:
        self.multiplier *= other
        return ProcessExpr([self])
    
    def __rmul__(self, other:float) -> ProcessExpr:
        return self*other

    def __add__(self, other: Union["Process", ProcessExpr]) -> ProcessExpr:
        return self*1 + other*1

    def __repr__(self) -> str:
        return f"<Process: {self.name}" + (">" if self.multiplier == 1 else " * {self.multiplier}>")

    def __format__(self, format_spec: str) -> str:
        return f"{self.name}{'' if self.multiplier == 1 else f' * {self.multiplier}'}"

    def __neg__(self):
        return self*-1

    def __sub__(self, other):
        return self + -other


class Processes:
    # Maps process names to resource demands
    _processes: List[Tuple[ProcessName, ArrayLike]] = []

    def create(self, name: ProcessName, *resources: Tuple[Resource, float]) \
            -> Process:
        res_max_index = max((resource.index for (resource, _) in resources)) + 1
        array = np.zeros(res_max_index)
        for (resource, v) in resources:
            i = resource.index
            array[i] = v
        process_inner = (name, array)
        process_out = self[len(self._processes)]
        self._processes.append(process_inner)
        return process_out



    def __len__(self):
        return len(self._processes)

    def __getitem__(self, arg):
        return Process(index = arg, parent = self)

    def __iter__(self):
        return map(self.__getitem__, range(len(self)))


def pack_constraint(
        constraint: Union[Process, ProcessExpr]
        ) -> ArrayLike:
    constraint *= 1 # Converts Process to ProcessExpr
    proc_max_index = max((process.index for process in constraint)) + 1
    array = np.zeros(proc_max_index)
    for process in constraint:
        array[process.index] = process.multiplier
    return array


class _Constraint:
    name: str
    array: ArrayLike
    bound: float

    def __init__(
            self,
            name: str,
            weighted_processes: Union[Process, ProcessExpr],
            bound: float):
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
    name: str,
    weighted_processes: Union[Process, ProcessExpr],
    bound: float
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
        le_constraints: Sequence[Tuple[LeConstraint, float]]):
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
    for process in processes:
        process.array.resize(len(resources), refcheck=False)    # TODO: find correct type for this
    # Pad arrays out to the correct size:
    # The processes weren't necessarily aware of the total number of
    # resources at the time they were created
    A_proc = np.transpose(np.array([process.array for process in processes]))
    b_proc = np.zeros(len(resources))

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
                raise Overconstrained([],[],[])
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
            print(res.con)
            
            raise Overconstrained(
                    [(processes[i], v) for i, v in enumerate(res.con[:len(processes)])
                        if v != 0],
                    [(eq_constraints[i], v) for i, v in enumerate(res.con[len(processes):])
                        if v != 0],
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

    for process in processes:
        process.array.resize(len(resources), refcheck=False)    # TODO: find correct type for this
    # Pad arrays out to the correct size:
    # The processes weren't necessarily aware of the total number of
    # resources at the time they were created
    A_proc = np.array([process.array for process in processes])
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