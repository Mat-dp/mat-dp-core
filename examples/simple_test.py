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
arable_farm = processes.create("arable farm", (hay, (1.0, 0.5, 1.5)))
dairy_farm = processes.create(
    "dairy farm", (cows, (1, 0.5, 2)), (hay, (-2, -2.5, -1.5))
)
mcdonalds = processes.create("mcdonalds", (cows, -1))

constraint = EqConstraint("burger consumption", mcdonalds, 10)

# Minimise total number of runs
# objective = arable_farm + dairy_farm + 2 * mcdonalds

solution = Measure(resources, processes, [constraint])

print(solution.run(bounds=True))
print(solution.cumulative_resource(bounds=True))
print(solution.flow(bounds=True))
print(solution.resource(bounds=True))
