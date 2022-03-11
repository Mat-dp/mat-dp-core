from functools import reduce
from typing import Any, Dict, List, Optional, Tuple, Union

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
    Overconstrained,
    UnboundedSolution,
)
from .processes import Processes, ProcessExpr
from .resources import Resources
from .tools import get_order_ranges, get_row_scales


def constraints_to_array(
    processes: Processes,
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


def sort_constraints(
    constraints: Union[
        List[Union[EqConstraint, LeConstraint]],
        List[EqConstraint],
        List[LeConstraint],
    ]
) -> Tuple[List[EqConstraint], List[LeConstraint]]:
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
    return eq_constraints, le_constraints


def get_associated_matrices_bounded(
    resources, processes, eq_constraints, le_constraints
) -> Tuple[ndarray, ndarray, ndarray, ndarray]:
    process_lower_bounds = processes.process_produces_lb
    process_upper_bounds = processes.process_produces_ub
    A_eq, b_eq = constraints_to_array(processes, list(eq_constraints))

    A_le_con, b_le_con = constraints_to_array(processes, list(le_constraints))
    A_le = np.concatenate(
        (process_lower_bounds, -process_upper_bounds, A_le_con)
    )
    b_le = np.concatenate((np.zeros(len(resources) * 2), b_le_con))
    return A_eq, b_eq, A_le, b_le


def get_associated_matrices(
    resources, processes, eq_constraints, le_constraints
) -> Tuple[ndarray, ndarray, ndarray, ndarray]:
    A_eq_con, b_eq_con = constraints_to_array(processes, list(eq_constraints))
    A_eq = np.concatenate((processes.process_produces, A_eq_con))
    b_eq = np.concatenate((np.zeros(len(resources)), b_eq_con))
    A_le, b_le = constraints_to_array(processes, list(le_constraints))
    return A_eq, b_eq, A_le, b_le


def solve(
    resources: Resources,
    processes: Processes,
    use_process_bounds: bool,
    constraints: Union[
        List[Union[EqConstraint, LeConstraint]],
        List[EqConstraint],
        List[LeConstraint],
    ] = [],
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

    eq_constraints, le_constraints = sort_constraints(constraints)

    if use_process_bounds:
        A_eq, b_eq, A_le, b_le = get_associated_matrices_bounded(
            resources, processes, eq_constraints, le_constraints
        )
    else:
        A_eq, b_eq, A_le, b_le = get_associated_matrices(
            resources, processes, eq_constraints, le_constraints
        )

    eq_equations = np.concatenate(
        (A_eq, np.resize(b_eq, (len(b_eq), 1))), axis=1
    )
    le_equations = np.concatenate(
        (A_le, np.resize(b_le, (len(b_le), 1))), axis=1
    )

    # Solve
    # TODO: optimise with callback
    # TODO: optimise method

    options: Dict[str, Any] = {}

    if maxiter is not None:
        options["maxiter"] = maxiter
    if use_process_bounds:
        options["sym_pos"] = False
        options["lstsq"] = True

    if not allow_inconsistent_order_of_mag:
        coeff_order_range: float = get_order_ranges(np.array([coefficients]))[
            0
        ]
        eq_order_range = get_order_ranges(eq_equations)
        le_order_range = get_order_ranges(le_equations)
        order_limit = 6
        coeff_order_inconsistent = coeff_order_range > order_limit
        eq_order_inconsistent = (
            len(eq_order_range) > 0 and np.max(eq_order_range) > order_limit
        )
        le_order_inconsistent = (
            len(le_order_range) > 0 and np.max(le_order_range) > order_limit
        )
        if (
            coeff_order_inconsistent
            or eq_order_inconsistent
            or le_order_inconsistent
        ):
            raise InconsistentOrderOfMagnitude.from_complex_objects(
                order_limit=order_limit,
                coeff_order_range=coeff_order_range,
                eq_order_range=eq_order_range,
                le_order_range=le_order_range,
                resources=resources,
                processes=processes,
                objective=new_objective,
                eq_constraints=eq_constraints,
                le_constraints=le_constraints,
                eq_matrix=A_eq,
                le_matrix=A_le,
                use_process_bounds=use_process_bounds,
            )

    coeff_scale = get_row_scales(np.array([coefficients]))[0]
    eq_scales = get_row_scales(eq_equations)
    le_scales = get_row_scales(le_equations)

    res = linprog(
        c=coefficients * coeff_scale,
        A_ub=np.einsum(
            "ij, i -> ij",
            np.array(A_le, dtype=float),
            np.array(le_scales, dtype=float),
        ),
        b_ub=np.einsum(
            "i, i -> i",
            np.array(b_le, dtype=float),
            np.array(le_scales, dtype=float),
        ),
        A_eq=np.einsum(
            "ij, i -> ij",
            np.array(A_eq, dtype=float),
            np.array(eq_scales, dtype=float),
        ),
        b_eq=np.einsum(
            "i, i -> i",
            np.array(b_eq, dtype=float),
            np.array(eq_scales, dtype=float),
        ),
        options=options,
    )
    assert res.status in [0, 1, 2, 3]
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

    else:  # Problem appears to be unbounded
        process_sols = [
            (process, res.x[process.index]) for process in processes
        ]
        raise UnboundedSolution(process_sols)
