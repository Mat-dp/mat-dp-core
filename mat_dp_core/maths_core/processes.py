from itertools import starmap
from typing import Any, List, MutableSequence, Optional, Sequence, Tuple, Union

import numpy as np
from numpy import ndarray

from .resources import Resource


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

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Process):
            return False
        else:
            return self.index == other.index and self._parent == other._parent


class Processes:
    # Maps process names to resource demands
    _processes: MutableSequence[Tuple[ProcessName, ndarray]]
    _process_produces: Optional[ndarray]  # (resources, processes)

    def __init__(self) -> None:
        self._processes = []
        self._process_produces = None

    def create(
        self, name: ProcessName, *resources: Tuple[Resource, float]
    ) -> Process:
        if len(resources) == 0:
            raise ValueError(f"No resources attached to {name}")
        res_max_index = (
            max([resource.index for (resource, _) in resources]) + 1
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

    @property
    def process_produces(self) -> ndarray:
        if self._process_produces is None:
            max_resource_size = max([len(process.array) for process in self])
            # Pad arrays out to the correct size:
            # The processes weren't necessarily aware of the total number of
            # resources at the time they were created
            for process in self:
                process.array.resize(max_resource_size, refcheck=False)
            self._process_produces = np.transpose(
                np.array([process.array for process in self])
            )
        return self._process_produces
