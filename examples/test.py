from mat_dp_core.maths_core import (
    EqConstraint,
    GeConstraint,
    LeConstraint,
    Measure,
    Processes,
    Resources,
)

resources = Resources()
cardboard = resources.create("cardboard", unit="m2")
recycled_cardboard = resources.create("recycled_cardboard", unit="m2")
pizza_box = resources.create("pizza_box")
energy = resources.create("energy", unit="kWh")

processes = Processes()
cardboard_producer = processes.create("cardboard producer", (cardboard, +1))
recycled_cardboard_producer = processes.create(
    "recycled cardboard producer", (recycled_cardboard, +1)
)
pizza_box_producer = processes.create(
    "pizza box producer",
    (recycled_cardboard, -0.5),
    (cardboard, -2),
    (pizza_box, 1),
)
recycled_pizza_box_producer = processes.create(
    "recycled pizza box producer",
    (recycled_cardboard, -3),
    (cardboard, -1),
    (pizza_box, 1),
)
power_plant = processes.create("power plant", (pizza_box, -1), (energy, 4))
energy_grid = processes.create("energy grid", (energy, -2))

constraints = [
    EqConstraint(
        "recycled pizza box ratio",
        pizza_box_producer - recycled_pizza_box_producer,
        0,
    ),
    EqConstraint("required energy", energy_grid, 8),
]

# Minimise total number of runs
objective = (
    cardboard_producer
    + recycled_cardboard_producer
    + pizza_box_producer
    + recycled_pizza_box_producer
    + power_plant
    + energy_grid
)

measurement = Measure(resources, processes, constraints, objective)

print(measurement._run_vector)
print(measurement.resource(pizza_box))
