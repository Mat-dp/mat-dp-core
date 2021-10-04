from mat_dp_core import Resource, ProcessMaker, PolicyElementMaker, Policy

resources = [
    Resource('cardboard', unit = 'm2'),
    Resource('recycled_cardboard', unit = 'm2'),
    Resource('pizza_box'),
    Resource('energy', unit = 'kWh')
]
print(resources)
process_maker = ProcessMaker(resources)

processes = [
    process_maker(
        'generate_cardboard',
        cardboard = -1,
        recycled_cardboard = -2
    ),
    process_maker(
        'make_pizza_box_normal',
        cardboard = 2,
        pizza_box = -1
    ),
    process_maker(
        'make_pizza_box_recycled',
        recycled_cardboard = 3,
        pizza_box = -1
    ),
    process_maker(
        'burn_pizza_box',
        pizza_box = 1,
        energy = 2
    )
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
        'burn_pizza_box',
        'pizza_box',
        make_pizza_box_normal =  0.4,
        make_pizza_box_recycled =  0.6
    )
]
policy = Policy(resources, processes, policy_elements)

print(resources)
print(process_maker)
print(processes)
print(policy_element_maker)
print(policy_elements)