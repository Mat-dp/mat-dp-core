from typing import Union

import numpy as np
from numpy import ndarray

from .processes import Process, ProcessExpr


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
        return f"<{self.__class__.__name__}: {self.name} | Equation:{self.weighted_processes} == {self.bound}>"

    def __format__(self, format_spec: str) -> str:
        return f"{self.weighted_processes} == {self.bound}"


class LeConstraint(_Constraint):
    """
    Less than or equal to constraint
    """

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}: {self.name} | Equation:{self.weighted_processes} <= {self.bound}>"

    def __format__(self, format_spec: str) -> str:
        return f"{self.weighted_processes} <= {self.bound}"


class GeConstraint(LeConstraint):
    """
    Greater than or equal to constraint
    """

    def __init__(
        self,
        name: str,
        weighted_processes: Union[Process, ProcessExpr],
        bound: float,
    ):
        super().__init__(name, -weighted_processes, -bound)
