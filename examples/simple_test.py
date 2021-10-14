from mat_dp_core.maths_core import (
    Resources,
    Processes,
    EqConstraint,
    LeConstraint,
    GeConstraint,
    Measure,
)

resources = Resources()
hay = resources.create("hay")
cows = resources.create("cows")

processes = Processes()
arable_farm = processes.create("arable farm", (hay, +1))
dairy_farm = processes.create("dairy farm", (cows, +1), (hay, -1))
mcdonalds = processes.create("mcdonalds", (cows, -1))

constraint = EqConstraint("burger consumption", mcdonalds, 10)

# Minimise total number of runs
objective = arable_farm + dairy_farm + 2 * mcdonalds

solution = Measure(resources, processes, [constraint], objective)
print(solution)
print(solution._run_vector)
