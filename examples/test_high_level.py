from mat_dp_core import Resource, ProcessMaker, PolicyElementMaker, Policy, Scenario, ScenarioElementMaker, Measure, MeasureElementMaker

resources = [
    Resource('cardboard', unit = 'm2'),
    Resource('recycled_cardboard', unit = 'm2'),
    Resource('pizza_box'),
    Resource('energy', unit = 'kWh')
]

process_maker = ProcessMaker(resources)
# Recipe class?
# List of emissions by country

processes = [
    process_maker(
        'generate_cardboard',
        cardboard = -1,
        recycled_cardboard = -2
    ),
    process_maker(
        'make_pizza_box_normal',
        cardboard = 2,
        recycled_cardboard = 0.5,
        pizza_box = -1
    ),
    process_maker(
        'make_pizza_box_recycled',
        recycled_cardboard = 3,
        cardboard = 1,
        pizza_box = -1
    ),
    process_maker(
        'burn_pizza_box',
        pizza_box = 1,
        energy = -4, # produced and consumed
    ),
    process_maker(
        'energy_sink',
        energy = 2
    ),
]

policy_element_maker = PolicyElementMaker(resources, processes)


policy_elements = [
    policy_element_maker(
        'make_pizza_box_normal',
        'cardboard',
        generate_cardboard =  1

    ),
    policy_element_maker(
        'make_pizza_box_recycled',
        'cardboard',
        generate_cardboard = 1
    ),
    policy_element_maker(
        'make_pizza_box_recycled',
        'recycled_cardboard',
        generate_cardboard = 1
    ),
    policy_element_maker(
        'make_pizza_box_normal',
        'recycled_cardboard',
        generate_cardboard =  1

    ),
    policy_element_maker(
        'burn_pizza_box',
        'pizza_box',
        make_pizza_box_normal =  0.4,
        make_pizza_box_recycled =  0.6
    ),
    policy_element_maker(
        'energy_sink',
        'energy',
        burn_pizza_box = 1
    )
]
policy = Policy(resources, processes, policy_elements)

scenario_element_maker = ScenarioElementMaker(resources, processes)

scenario_elements = [
    scenario_element_maker(
        'energy_sink',
        energy = 10
    ),
    #scenario_element_maker(
    #    'burn_pizza_box',
    #    energy = -3
    #),
]

scenario = Scenario(policy, scenario_elements)
measure_element_maker = MeasureElementMaker(resources, processes)

measure_elements = [
    measure_element_maker(
        'energy',
        'burn_pizza_box',
        'energy_sink'
    )
]

measure = Measure(scenario)
resource_usage = measure(measure_elements)
print(resource_usage)

