from typing import Tuple

import pytest

from mat_dp_core import EqConstraint, Measure, Processes, Resources


@pytest.fixture
def farming_example() -> Tuple[Resources, Processes]:
    resources = Resources()
    hay = resources.create("hay")
    cow = resources.create("cow")

    processes = Processes()
    processes.create("arable_farm", (hay, +1))
    processes.create("dairy_farm", (cow, +1), (hay, -2))
    processes.create("mcdonalds", (cow, -1))
    return resources, processes


@pytest.fixture
def unscaled_farming_example() -> Tuple[Resources, Processes]:
    resources = Resources()
    hay = resources.create("hay")
    cow = resources.create("cow")

    processes = Processes()
    processes.create("arable_farm", (hay, +100000000000))
    processes.create("dairy_farm", (cow, +1000000000), (hay, -200000000000))
    processes.create("mcdonalds", (cow, -1000000000))
    return resources, processes


@pytest.fixture
def farming_example_measure(farming_example) -> Measure:
    resources, processes = farming_example
    constraints = [
        EqConstraint("burger_consumption", processes["dairy_farm"], 10)
    ]
    objective = -processes["arable_farm"]
    return Measure(resources, processes, constraints, objective=objective)
