from mat_dp_core.maths_core import Resources, Processes, EqConstraint, LeConstraint, GeConstraint, solve, generate_process_demands, calculate_actual_resource
from mat_dp_core.measures import MeasureManager
resources = Resources()
hay = resources.create("hay")
cows = resources.create("cows")

processes = Processes()
arable_farm = processes.create("arable farm", (hay, +1))
dairy_farm = processes.create("dairy farm", (cows, +1), (hay, -1))
mcdonalds = processes.create("mcdonalds", (cows, -1))

constraint = EqConstraint("burger consumption", mcdonalds, 10)

# Minimise total number of runs
objective = arable_farm + dairy_farm + 2*mcdonalds

solution = solve(resources, processes, [constraint], objective)
print(solution)

#process_demands = generate_process_demands(resources, processes)
#actual_resource = calculate_actual_resource(process_demands, solution)
measure_man = MeasureManager(resources, processes, solution)

mcdonalds_cows = measure_man.make_actual_resource_measure(mcdonalds, cows)

print(mcdonalds_cows)

