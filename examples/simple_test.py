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
# process runs for following runs: is float value
# le less than or equal to
# eq equal to
# ge greater than or equal to

# Minimise total number of runs
objective = arable_farm + dairy_farm + 2 * mcdonalds

solution = Measure(resources, processes, [constraint], objective)

print(solution.run(bounds=True)) # tells you how many runs for each process
print(solution.cumulative_resource(bounds=True)) # sankey output
print(solution.flow(bounds=True)) # connections with ratios of resources
print(solution.resource(bounds=True)) # resource at finish
# bounds false and default returns equilibrium value and not 'error bounds'
