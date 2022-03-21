# **Simple Example**

## **Context**

The below example should show the essence of MAT-DP Core for optimally allocating resources in low-carbon systems.

There exists two finite resources `land`, and `aluminium`.  
An energy firm has been contracted to manufacture and install Vertical Axis Wind-Turbines (VAWTs) and Horizontal Axis Wind-Turbines (HAWTs) using these resources.

The energy firm wishes to produce the maximum amount of energy using the resources available.


## **Setup**

Consider the below parameters:

* A single HAWT produces 10kw, requires 8 bales of aluminium, and takes up 40m^2 of land.
* A single VAWT produces 4kw, requires 4 bales of aluminium, and take up 20m^2 of land.
* There is  only 300m^2 of land.
* There is only 45 bales of aluminium.
* The objective is to maximise kw produced.

## **Resources**

First, create the resources of interest:

```py
from mat_dp_core import Resources, Processes, GeConstraint, LeConstraint, Measure
r = Resources()
aluminium = r.create("Aluminium", "bales")
land = r.create("land", "m^2")
energy = r.create("energy","kw")
```

## **Processes**

Now make processes to reflect the different parts of the system:

```py
p = Processes()
make_install_HAWT = p.create("Create + install a Horizontal-Axis Wind Turbine", (aluminium, -8), (land, -40), (energy, 10))
make_install_VAWT = p.create("Create + install a Vertical-Axis Wind Turbine", (aluminium, -2), (land, -20), (energy, 4))
aluminium_supply = p.create("Aluminium supply", (aluminium, 1))
land_supply = p.create("Land supply", (land, 1))
energy_grid = p.create("Energy grid", (energy, -1))
```

## **Constraints**

Then create the constraints:

```py
finite_aluminium = LeConstraint("Available aluminium", aluminium_supply, 45)
finite_land = LeConstraint("Available land", land_supply, 300)
constraints = [finite_aluminium, finite_land]
```

## **Objective**

Finally, declare an objective function:

```py
objective = -energy_grid

measure = Measure(r, p, constraints, objective)
```

## **Printing**

Here's some printing for good measure

```py
print(round(measure.run(process=make_install_HAWT), 1) + "Vertical-Axis Turbines")
print(round(measure.run(process=make_install_VAWT), 1) + "Horizontal-Axis Turbines")

print("kwh of energy produced by process:")
for process in measure.resource(resource=energy):
    print(str(process[0].name).ljust(50) + ":  " + str(round(process[1], 1)))
```

# **Summary**

If ran to completion, this code should result in 3.8 HAWTs and 7.5 VAWTs being made, resulting in 67.5kw of energy being made available to the grid.  
This is preferable to pure VAWT or pure HAWT. Such allocation would result in 60kw and 56.25kw respectively, missing out on 7.5kw (12.5% extra). MAT-DP-Core has allowed the optimal allocation of two limited resources to be found. MAT-DP-Core's Measure() functions would further provide a full trace of side-effects if those were to be included in the system (CO2, social cost, and so on).

