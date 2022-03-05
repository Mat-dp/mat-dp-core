from mat_dp_core import (
    EqConstraint,
    GeConstraint,
    LeConstraint,
    Measure,
    Processes,
    Resources,
)

resources = Resources()
hay = resources.create("hay")
cows = resources.create("cows")

processes = Processes()
arable_farm = processes.create("arable farm", (hay, +1))
dairy_farm = processes.create("dairy farm", (cows, +1), (hay, -2))
mcdonalds = processes.create("mcdonalds", (cows, -1))

constraint = EqConstraint("burger consumption", mcdonalds, 10)

# Minimise total number of runs
objective = arable_farm + dairy_farm + 2 * mcdonalds

solution = Measure(resources, processes, [constraint])
print(solution.flow_from(arable_farm))
print(solution)
print(solution.run_vector)
print(solution.cumulative_resource())
