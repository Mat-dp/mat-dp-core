from mat_dp_core import Resources, Processes, EqConstraint, RunRatioConstraint, GeConstraint, LeConstraint, Measure
r = Resources()

carbon_dioxide = r.create("CO2", "tons")

cable = r.create("High Voltage Cable", "metres")
turbine = r.create("Hydro-electric Turbine", "unit")
concrete = r.create("Concrete", "kilotons")
steel = r.create("Steel", "tons")
electricity = r.create("Power generation per day", "mwh")

p = Processes()

# Producers
electrical_cable_production = p.create("Cable production", (cable, 1), (carbon_dioxide, 0.2))
pylon_for_cable_production = p.create("Pylon production", (steel, -90), (carbon_dioxide, 0.5))
turbine_production = p.create("Turbine production", (steel, -0.8), (turbine, 1), (carbon_dioxide, 0.7))
concrete_production = p.create("Concrete production", (concrete, 1), (carbon_dioxide, 1200))
steel_production = p.create("Steel production", (steel, 1),(carbon_dioxide, 2))

# Dam construction (produces and consumes)
hydo_dam_construction = p.create("Dam construction", 
    (cable, -25000), 
    (turbine, -20), 
    (concrete, -5500), 
    (steel, -10000), 
    (electricity, 1700))

# Consumers
environment = p.create("CO2 uptake by environment", (carbon_dioxide, -1))
grid = p.create("Electricity uptake by grid", (electricity, -1))

# Constraints
one_dam = LeConstraint("The requirement to make only 1 dam", hydo_dam_construction, 1)
pylon_to_cable_ratio = RunRatioConstraint(electrical_cable_production, pylon_for_cable_production, 500, "Fixed run ratio of power cables to power pylons")

constraints = [one_dam, pylon_to_cable_ratio]

# Objective
objective = -grid

measure = Measure(r, p, constraints, objective)

# Printing
print("\n\nTotal pylons required:")
print(round(measure.run(process=pylon_for_cable_production)))

print("\n\nTotal steel used in cable production:")
print(round(measure.flow(process_from=electrical_cable_production, process_to=hydo_dam_construction, resource=cable)))

print("\n\nTotal CO2 absorbed by the environment:")
print(round(- measure.resource(process=environment, resource=carbon_dioxide)))

print("\n\nTons of CO2 produced by process:")
for x in measure.resource(resource=carbon_dioxide):
    print(x[0].name + ": " + str(round(x[1])))