from mat_dp_core import ResourceConstraint, RunRatioConstraint
from mat_dp_core.maths_core import (
    EqConstraint,
    GeConstraint,
    LeConstraint,
    Measure,
    Processes,
    Resources,
)

resources = Resources()
aluminium = resources.create("aluminium", unit="g")
steel = resources.create("steel", unit="g")
concrete = resources.create("concrete", unit="g")
electronics = resources.create("electronics")
energy = resources.create("energy", unit="kWh")

processes = Processes()
concrete_producer = processes.create("concrete_producer", (concrete, +1))
steel_producer = processes.create("steel_producer", (steel, +1))
aluminium_producer = processes.create("aluminium_producer", (aluminium, +1))
electronics_producer = processes.create(
    "electronics_producer", (electronics, +1)
)
wind = processes.create("wind", (aluminium, -2), (concrete, -3), (energy, +1))
solar = processes.create(
    "solar", (steel, -1), (electronics, -1), (aluminium, -0.5), (energy, +1)
)
coal = processes.create("coal", (concrete, -5), (energy, +1))
energy_grid = processes.create("energy_grid", (energy, -1))

c1 = RunRatioConstraint(wind, solar, processes, 6 / 5)
c2 = RunRatioConstraint(solar, coal, processes, 3)
energy_con = ResourceConstraint(energy, energy_grid, resources, processes, 20)
constraints = [energy_con]
# Minimise run total
objective = (
    concrete_producer
    + steel_producer
    + aluminium_producer
    + electronics_producer
    + wind
    + solar
    + coal
    + energy_grid
)
# objective = concrete_producer + steel_producer + aluminium_producer + electronics_producer # TODO Fix this bug
objective = wind + solar + coal + energy_grid
solution = Measure(resources, processes, constraints, objective)
# print(solution._run_vector)
result = solution.resource(energy)
print(result)
