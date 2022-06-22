from mat_dp_core import Resources, Processes, GeConstraint, LeConstraint, Measure


r = Resources()
aluminium = r.create("Aluminium", "bales")
land = r.create("land", "m^2")
energy = r.create("energy","kw")

p = Processes()
make_install_HAWT = p.create("Create + install a Horizontal-Axis Wind Turbine", (aluminium, -8), (land, -40), (energy, 10))
make_install_VAWT = p.create("Create + install a Vertical-Axis Wind Turbine", (aluminium, -2), (land, -20), (energy, 4))
aluminium_supply = p.create("Aluminium supply", (aluminium, 1))
land_supply = p.create("Land supply", (land, 1))
energy_grid = p.create("Energy grid", (energy, -1))

# Constraints

finite_aluminium = LeConstraint("Available aluminium", aluminium_supply, 45)
finite_land = LeConstraint("Available land", land_supply, 300)
constraints = [finite_aluminium, finite_land]

# Objective and Measure

objective = -energy_grid

measure = Measure(r, p, constraints, objective)

# Printing

print(round(measure.run(process=make_install_HAWT), 1) + "Vertical-Axis Turbines")
print(round(measure.run(process=make_install_VAWT), 1) + "Horizontal-Axis Turbines")

print("kwh of energy produced by process:")
for process in measure.resource(resource=energy):
    print(str(process[0].name).ljust(50) + ":  " + str(round(process[1], 1)))