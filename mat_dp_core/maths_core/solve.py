from functools import reduce
from typing import List, Optional, Sequence, Tuple, Union

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
from .processes import Processes, ProcessExpr
from .resources import Resources
from .tools import get_order_ranges, get_row_scales


def solve(
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
        """
        Converts a list of constraints to array format.

        returns the tuple of A matrix and b vector forming an equation
        """
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

    if objective is None:
        new_objective: ProcessExpr = reduce(
            lambda x, y: x + y,
            [process * 1 for process in processes],
        )
    else:
        new_objective: ProcessExpr = objective

    # Build objective vector
    coefficients = pack_constraint(new_objective)
    coefficients.resize(len(processes), refcheck=False)
    # TODO: Add Inconsistent order of mag check on coefficients

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
    A_eq = np.concatenate((processes.process_produces, A_eq_con))
    b_eq = np.concatenate((np.zeros(len(resources)), b_eq_con))

    A_le, b_le = constraints_to_array(list(le_constraints))

    eq_equations = np.concatenate(
        (A_eq, np.resize(b_eq, (len(b_eq), 1))), axis=1
    )
    le_equations = np.concatenate(
        (A_le, np.resize(b_le, (len(b_le), 1))), axis=1
    )

    # Solve
    # TODO: optimise with callback
    # TODO: optimise method

    options = {}
    if maxiter is not None:
        options["maxiter"] = maxiter

    if not allow_inconsistent_order_of_mag:
        eq_order_range = get_order_ranges(eq_equations)
        le_order_range = get_order_ranges(le_equations)
        order_limit = 6
        eq_order_inconsistent = (
            len(eq_order_range) > 0 and np.max(eq_order_range) > order_limit
        )
        le_order_inconsistent = (
            len(le_order_range) > 0 and np.max(le_order_range) > order_limit
        )
        if eq_order_inconsistent or le_order_inconsistent:
            raise InconsistentOrderOfMagnitude.from_complex_objects(
                order_limit=order_limit,
                eq_order_range=eq_order_range,
                le_order_range=le_order_range,
                resources=resources,
                processes=processes,
                eq_constraints=eq_constraints,
                le_constraints=le_constraints,
                eq_matrix=A_eq,
                le_matrix=A_le,
            )

    eq_scales = get_row_scales(eq_equations)
    le_scales = get_row_scales(le_equations)

    res = linprog(
        c=coefficients,
        A_ub=np.einsum("ij, i -> ij", A_le, le_scales),
        b_ub=np.einsum("i, i -> i", b_le, le_scales),
        A_eq=np.einsum("ij, i -> ij", A_eq, eq_scales),
        b_eq=np.einsum("i, i -> i", b_eq, eq_scales),
        options=options,
    )

    if res.status == 0:  # Optimization terminated successfully
        return res.x
    elif res.status == 1:  # Iteration limit reached
        raise IterationLimitReached(res.nit)
    elif res.status == 2:  # Problem appears to be infeasible
        rescaled_con = np.einsum(
            "i, i -> i", res.con, np.nan_to_num(np.reciprocal(eq_scales))
        )
        rescaled_slack = np.einsum(
            "i, i -> i", res.slack, np.nan_to_num(np.reciprocal(le_scales))
        )
        raise Overconstrained.from_vector(
            con_vector=rescaled_con,
            slack_vector=rescaled_slack,
            solver_matrix=A_eq,
            processes=processes,
            resources=resources,
            eq_constraints=eq_constraints,
            le_constraints=le_constraints,
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
