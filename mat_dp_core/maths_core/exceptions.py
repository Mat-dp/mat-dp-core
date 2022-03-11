from typing import Any, List, Optional, Sequence, Tuple, Union

import numpy as np

from .constraints import EqConstraint, LeConstraint
from .processes import Process, Processes, ProcessExpr
from .resources import Resource, Resources


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
                format_str = None
                if val < 0:
                    message_list = []
                    if len(producer_names) != 0:
                        message_list.append(
                            f"increase runs of {producer_names}"
                        )
                    if len(consumer_names) != 0:
                        message_list.append(
                            f"decrease runs of {consumer_names}"
                        )

                    assert len(message_list) > 0
                    format_str = " or ".join(message_list)
                elif val > 0:
                    message_list = []
                    if len(consumer_names) != 0:
                        message_list.append(
                            f"increase runs of {consumer_names}"
                        )
                    if len(producer_names) != 0:
                        message_list.append(
                            f"decrease runs of {producer_names}"
                        )

                    assert len(message_list) > 0
                    format_str = " or ".join(message_list)

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

    @classmethod
    def from_vector(
        cls,
        con_vector: np.ndarray,
        slack_vector: np.ndarray,
        solver_matrix: np.ndarray,
        processes: Processes,
        resources: Resources,
        eq_constraints: List[EqConstraint],
        le_constraints: List[LeConstraint],
    ):
        # TODO Get rid of dependency on solver_matrix
        res_constraints = []
        for i, v in enumerate(con_vector[: len(resources)]):
            if v != 0:
                prod_con = solver_matrix[int(i)]
                producers_i = np.nonzero(np.where(prod_con > 0, prod_con, 0))[
                    0
                ]
                consumers_i = np.nonzero(np.where(prod_con < 0, prod_con, 0))[
                    0
                ]
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

        return cls(
            res_constraints,
            [
                (eq_constraints[i], v)
                for i, v in enumerate(con_vector[len(resources) :])
                if v != 0
            ],
            [
                (le_constraints[i], v)
                for i, v in enumerate(slack_vector)
                if v < 0
            ],
        )


class UnboundedSolution(Exception):
    def __init__(self, process_sols: List[Tuple[Process, float]]) -> None:
        message_list = ["Solution unbounded - final solution was:"]
        for p, sol in process_sols:
            if sol > 10 ** 7 or sol < 10 ** -7:
                comment = " (probably unbounded)"
            else:
                comment = ""
            message_list.append(f"{p}: {sol}{comment}")

        super().__init__("\n".join(message_list))


class InconsistentOrderOfMagnitude(Exception):
    def __init__(
        self,
        objective: Optional[Tuple[ProcessExpr, float]],
        resources: List[Tuple[Resource, List[Tuple[Process, float]], float]],
        eq_constraints: List[
            Tuple[EqConstraint, List[Tuple[Process, float]], float]
        ],
        le_constraints: List[
            Tuple[LeConstraint, List[Tuple[Process, float]], float]
        ],
    ) -> None:
        message_list = [
            "\nAll resources and constraints must be of a \nconsistent order of magnitude. If you wish to allow this \nbehaviour use 'allow_inconsistent_order_of_mag'.\n"
        ]
        if objective is not None:
            message_list.append("Objective function inconsistencies")
            message_list.append(
                f"Objective func: {objective[0]}: Order of mag range: {objective[1]}"
            )
            message_list.append("\n")
        if len(resources) > 0:
            message_list.append("Resource inconsistencies")
            for resource, process_list, order_range in resources:
                message_list.append(
                    f"{resource}: Order of mag range: {order_range}"
                )
                for process, process_demand in process_list:
                    message_list.append(f"    {process}: {process_demand}")
                message_list.append("\n")
            message_list.append("\n")

        if len(eq_constraints) > 0:
            message_list.append("Eq Constraint inconsistencies")
            for eq_constraint, process_list, order_range in eq_constraints:
                message_list.append(
                    f"{eq_constraint}: Order of mag range - {order_range}"
                )
                for process, process_demand in process_list:
                    message_list.append(f"    {process}: {process_demand}")
                message_list.append("\n")

        if len(le_constraints) > 0:
            message_list.append("Le Constraint inconsistencies")

            for le_constraint, process_list, order_range in le_constraints:
                message_list.append(
                    f"{le_constraint}: Order of mag range - {order_range}"
                )
                for process, process_demand in process_list:
                    message_list.append(f"    {process}: {process_demand}")
                message_list.append("\n")
        super().__init__("\n".join(message_list))

    @classmethod
    def from_complex_objects(
        cls,
        order_limit: float,
        coeff_order_range: float,
        eq_order_range: np.ndarray,
        le_order_range: np.ndarray,
        resources: Resources,
        processes: Processes,
        objective: ProcessExpr,
        eq_constraints: List[EqConstraint],
        le_constraints: List[LeConstraint],
        eq_matrix: np.ndarray,
        le_matrix: np.ndarray,
        use_process_bounds: bool,
    ):
        def get_inconsistencies(
            order_limit: float,
            order_range: np.ndarray,
            group: Union[
                Resources,
                List[EqConstraint],
                List[LeConstraint],
                List[Resource],
            ],
            processes: Processes,
            matrix: np.ndarray,
            matrix_start_row: int = 0,
        ) -> List[Tuple[Any, List[Tuple[Process, float]], float]]:
            inconsistencies = []
            for i, v in enumerate(order_range):
                if v > order_limit:
                    related_processes = []
                    for j, process in enumerate(processes):
                        if matrix[i + matrix_start_row][j] != 0:
                            process_demand = (process, matrix[i][j])
                            related_processes.append(process_demand)

                    inconsistencies.append(
                        (
                            group[i],
                            related_processes,
                            v,
                        )
                    )
            return inconsistencies

        coeff_order_inconsistent = coeff_order_range > order_limit
        eq_order_inconsistent = (
            len(eq_order_range) > 0 and np.max(eq_order_range) > order_limit
        )
        le_order_inconsistent = (
            len(le_order_range) > 0 and np.max(le_order_range) > order_limit
        )
        if coeff_order_inconsistent:
            optional_objective = (objective, coeff_order_range)
        else:
            optional_objective = None

        if use_process_bounds:
            """
            Impossible for eq_order to be inconsistent in this case,
            and for le_order not to be inconsistent - it must have succeeded
            the first solve
            """
            assert not eq_order_inconsistent
            assert le_order_inconsistent
            resource_inconsistencies = get_inconsistencies(
                order_limit,
                le_order_range[: len(resources) * 2],
                list(resources) + list(resources),
                processes,
                le_matrix,
            )
            le_inconsistencies = get_inconsistencies(
                order_limit,
                le_order_range[len(resources) * 2 :],
                le_constraints,
                processes,
                le_matrix,
                matrix_start_row=len(resources) * 2,
            )
            eq_inconsistencies = []
        else:
            if eq_order_inconsistent:
                resource_inconsistencies = get_inconsistencies(
                    order_limit,
                    eq_order_range[: len(resources)],
                    resources,
                    processes,
                    eq_matrix,
                )
                eq_inconsistencies = get_inconsistencies(
                    order_limit,
                    eq_order_range[len(resources) :],
                    eq_constraints,
                    processes,
                    eq_matrix,
                    matrix_start_row=len(resources),
                )

            else:
                resource_inconsistencies = []
                eq_inconsistencies = []
            if le_order_inconsistent:
                le_inconsistencies = get_inconsistencies(
                    order_limit,
                    le_order_range,
                    le_constraints,
                    processes,
                    le_matrix,
                )

            else:
                le_inconsistencies = []

        return cls(
            optional_objective,
            resource_inconsistencies,
            eq_inconsistencies,
            le_inconsistencies,
        )
