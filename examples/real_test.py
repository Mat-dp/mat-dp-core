from mat_dp_core import (
    EqConstraint,
    GeConstraint,
    LeConstraint,
    Measure,
    Processes,
    ResourceConstraint,
    Resources,
    RunRatioConstraint,
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
energy_producer = processes.create("energy_grid", (energy, -1))

wind = processes.create("wind", (aluminium, -2), (concrete, -3), (energy, +1))
solar = processes.create(
    "solar", (steel, -1), (electronics, -1), (aluminium, -0.5), (energy, +1)
)
coal = processes.create("coal", (concrete, -5), (energy, +1), (electronics, 0))


wind_con = ResourceConstraint(energy, wind, 5)
coal_con = ResourceConstraint(energy, coal, 5)
solar_con = ResourceConstraint(energy, solar, 5)
constraints = [wind_con, coal_con, solar_con]
print(constraints)
# Minimise run total

objective = (
    concrete_producer
    + steel_producer
    + aluminium_producer
    + electronics_producer
    + wind
    + solar
    + coal
    + energy_producer
)

solution = Measure(resources, processes, constraints, objective)
print(solution.run_vector)

result = solution.resource(energy)
print(result)
