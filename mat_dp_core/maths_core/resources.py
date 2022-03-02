from itertools import starmap
from typing import Any, List, MutableSequence, Sequence, Tuple, Union

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

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Resource):
            return False
        else:
            return self.index == other.index and self._parent == other._parent

    def __format__(self, format_spec: str) -> str:
        return f"{self.name}"


class Resources:
    _resources: MutableSequence[Tuple[ResourceName, Unit]]

    def __init__(self) -> None:
        self._resources = []

    def create(self, name: ResourceName, unit: Unit = "ea") -> Resource:
        """
        Create a resource
        """

        self._resources.append(
            (
                name,
                unit,
            )
        )
        return self[len(self._resources) - 1]

    def load(
        self, resources: Sequence[Tuple[ResourceName, Unit]]
    ) -> List[Resource]:
        """
        Load some additional resources in bulk
        """
        return list(starmap(self.create, resources))

    def dump(self) -> Sequence[Tuple[ResourceName, Unit]]:
        """
        Dump resources in bulk
        """
        return self._resources

    def __len__(self):
        return len(self._resources)

    def __getitem__(self, arg: Union[int, str]):
        if isinstance(arg, int):
            if arg < len(self._resources):
                return Resource(index=arg, parent=self)
            else:
                raise IndexError("list index out of range")

        else:
            results = [
                i for i, (name, _) in enumerate(self._resources) if name == arg
            ]
            if len(results) == 0:
                raise KeyError(f"'{arg}'")
            elif len(results) > 1:
                raise KeyError(f"Name {arg} non unique: please use index")
            else:
                return Resource(index=results[0], parent=self)

    def __iter__(self):
        return map(self.__getitem__, range(len(self)))
