from typing import Tuple

import pytest

from mat_dp_core import (
    EqConstraint,
    Measure,
    Processes,
    ResourceConstraint,
    Resources,
    RunEqConstraint,
    RunRatioConstraint,
)
from mat_dp_core.maths_core.resources import Resource


@pytest.fixture
def test_resource() -> Resource:
    resources = Resources()
    return resources.create("test")


@pytest.fixture
def null_example() -> Tuple[Resources, Processes]:
    resources = Resources()
    hay = resources.create("hay")
    cow = resources.create("cow")

    processes = Processes()
    processes.create("arable_farm", (hay, 0))
    processes.create("dairy_farm", (hay, 0), (cow, 0))
    processes.create("mcdonalds", (cow, 0))
    return resources, processes


@pytest.fixture
def null_example_measure(null_example) -> Measure:
    resources, processes = null_example
    return Measure(resources, processes, [], objective=None)


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
    objective = (
        2 * (processes["arable_farm"] * 2 + 3 * processes["dairy_farm"]) * 2
    )
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


@pytest.fixture(
    params=[0, 1, 2, 3, 4],
    ids=[
        "raw_constraints",
        "raw_constraints_with_multipliers",
        "higher_level_constraint_eq",
        "higher_level_constraint_resource_grid",
        "higher_level_constraint_resource_plant",
    ],
)
def pizza_example_measure(request, pizza_example) -> Measure:
    resources, processes = pizza_example
    if request.param == 0:
        constraints = [
            EqConstraint(
                "pizza_box_ratio",
                processes["pizza_box_producer"]
                - processes["recycled_pizza_box_producer"],
                0,
            ),
            EqConstraint("required_energy", processes["energy_grid"], 8),
        ]
    if request.param == 1:
        constraints = [
            EqConstraint(
                "pizza_box_ratio",
                (
                    processes["pizza_box_producer"] * 2
                    - processes["recycled_pizza_box_producer"] * 2
                )
                - (
                    processes["pizza_box_producer"]
                    - processes["recycled_pizza_box_producer"]
                ),
                0,
            ),
            EqConstraint("required_energy", processes["energy_grid"], 8),
        ]
    elif request.param == 2:
        constraints = [
            RunRatioConstraint(
                processes["pizza_box_producer"],
                processes["recycled_pizza_box_producer"],
                1,
            ),
            RunEqConstraint(processes["energy_grid"], 8),
        ]
    elif request.param == 3:
        constraints = [
            RunRatioConstraint(
                processes["pizza_box_producer"],
                processes["recycled_pizza_box_producer"],
                1,
            ),
            ResourceConstraint(
                resources["energy"], processes["energy_grid"], 16
            ),
        ]
    else:
        constraints = [
            RunRatioConstraint(
                processes["pizza_box_producer"],
                processes["recycled_pizza_box_producer"],
                1,
            ),
            ResourceConstraint(
                resources["energy"], processes["power_plant"], 16
            ),
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


@pytest.fixture
def real_example_measure() -> Measure:
    resources = Resources()
    aluminium = resources.create("aluminium", unit="g")
    steel = resources.create("steel", unit="g")
    concrete = resources.create("concrete", unit="g")
    electronics = resources.create("electronics")
    energy = resources.create("energy", unit="kWh")

    processes = Processes()
    processes.create("concrete_producer", (concrete, +1))
    processes.create("steel_producer", (steel, +1))
    processes.create("aluminium_producer", (aluminium, +1))

    processes.create("electronics_producer", (electronics, +1))
    processes.create("energy_grid", (energy, -1))

    wind = processes.create(
        "wind", (aluminium, -2), (concrete, -3), (energy, +1)
    )
    solar = processes.create(
        "solar",
        (steel, -1),
        (electronics, -1),
        (aluminium, -0.5),
        (energy, +1),
    )
    coal = processes.create(
        "coal", (concrete, -5), (energy, +1), (electronics, 0)
    )

    wind_con = ResourceConstraint(energy, wind, 5)
    coal_con = ResourceConstraint(energy, coal, 5)
    solar_con = ResourceConstraint(energy, solar, 5)
    constraints = [wind_con, coal_con, solar_con]

    return Measure(resources, processes, constraints, objective=None)
