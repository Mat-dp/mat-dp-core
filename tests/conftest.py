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
    objective = processes["arable_farm"]
    return Measure(resources, processes, constraints, objective=objective)


@pytest.fixture
def pizza_example() -> Tuple[Resources, Processes]:
    resources = Resources()
    cardboard = resources.create("cardboard", unit="m2")
    recycled_cardboard = resources.create("recycled_cardboard", unit="m2")
    pizza_box = resources.create("pizza_box")
    energy = resources.create("energy", unit="kWh")

    processes = Processes()
    processes.create("cardboard_producer", (cardboard, +1))
    processes.create("recycled_cardboard_producer", (recycled_cardboard, +1))
    processes.create(
        "pizza_box_producer",
        (recycled_cardboard, -0.5),
        (cardboard, -2),
        (pizza_box, 1),
    )
    processes.create(
        "recycled_pizza_box_producer",
        (recycled_cardboard, -3),
        (cardboard, -1),
        (pizza_box, 1),
    )
    processes.create("power_plant", (pizza_box, -1), (energy, 4))
    processes.create("energy_grid", (energy, -2))

    return resources, processes


@pytest.fixture
def pizza_example_measure(pizza_example) -> Measure:
    resources, processes = pizza_example
    constraints = [
        EqConstraint(
            "recycled pizza box ratio",
            processes["pizza_box_producer"]
            - processes["recycled_pizza_box_producer"],
            0,
        ),
        EqConstraint("required_energy", processes["energy_grid"], 8),
    ]
    return Measure(resources, processes, constraints, objective=None)


@pytest.fixture
def parallel_farming_example() -> Tuple[Resources, Processes]:
    resources = Resources()
    hay = resources.create("hay")
    cow = resources.create("cow")
    grass = resources.create("grass")
    sheep = resources.create("sheep")
    processes = Processes()
    processes.create("arable_farm", (hay, +1))
    processes.create("dairy_farm", (cow, +1), (hay, -2))
    processes.create("mcdonalds", (cow, -1))
    processes.create("field_growth", (grass, +1))
    processes.create("sheep_farm", (grass, -1), (sheep, +3))
    processes.create("dog_food_factory", (sheep, -3))
    return resources, processes


@pytest.fixture
def parallel_farming_example_measure(parallel_farming_example) -> Measure:
    resources, processes = parallel_farming_example
    constraints = [
        EqConstraint("burger_consumption", processes["mcdonalds"], 10),
        EqConstraint("dog_food_harvest", processes["dog_food_factory"], 10),
    ]
    objective = processes["arable_farm"]
    return Measure(resources, processes, constraints, objective=objective)
