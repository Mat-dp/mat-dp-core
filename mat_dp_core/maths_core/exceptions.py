from typing import List, Sequence, Tuple

import numpy as np

from .constraints import EqConstraint, LeConstraint
from .processes import Process, Processes
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
                producers_i = np.nonzero(np.where(prod_con > 0, prod_con, 0))
                consumers_i = np.nonzero(np.where(prod_con < 0, prod_con, 0))
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
                comment = "(probably unbounded)"
            else:
                comment = ""
            message_list.append(f"{p}: {sol} {comment}")

        super().__init__("\n".join(message_list))


class NumericalDifficulties(Exception):
    pass


class InconsistentOrderOfMagnitude(Exception):
    def __init__(
        self,
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
        if len(resources) > 0:
            message_list.append("Resource inconsistencies")
            for resource, process_list, order_range in resources:
                message_list.append(
                    f"{resource}: Order of mag range: {order_range}"
                )
                for process, process_demand in process_list:
                    message_list.append(f"{process}: {process_demand}")
                message_list.append("\n")
            message_list.append("\n")

        if len(eq_constraints) > 0:
            message_list.append("Eq Constraint inconsistencies")
            for eq_constraint, process_list, order_range in resources:
                message_list.append(
                    f"{eq_constraint}: Order of mag range - {order_range}"
                )
                for process, process_demand in process_list:
                    message_list.append(f"{process}: {process_demand}")
                message_list.append("\n")

        if len(le_constraints) > 0:
            message_list.append("Le Constraint inconsistencies")
            for le_constraint, process_list, order_range in resources:
                message_list.append(
                    f"{le_constraint}: Order of mag range - {order_range}"
                )
                for process, process_demand in process_list:
                    message_list.append(f"{process}: {process_demand}")
                message_list.append("\n")
        super().__init__("\n".join(message_list))
