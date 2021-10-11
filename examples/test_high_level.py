from mat_dp_core import (
    Resource,
    Process,
    Policy,
    PolicyElement,
    Scenario,
    ScenarioFlow,
    FlowMeasure
)
from mat_dp_core.utils import generate_index, generate_resource_index, generate_process_index

resources = [
    Resource('cardboard', unit = 'm2'),
    Resource('recycled_cardboard', unit = 'm2'),
    Resource('pizza_box'),
    Resource('energy', unit = 'kWh')
]

resource_index = generate_resource_index(resources)

processes = [
    Process(
        'generate_cardboard',
        {
            resource_index['cardboard']: -1.0,
            resource_index['recycled_cardboard']: -2.0
        }
    ),
    Process(
        'make_pizza_box_normal',
        {
            resource_index['cardboard']: 2.0,
            resource_index['recycled_cardboard']: 0.5,
            resource_index['pizza_box']: -1
        }
    ),
    Process(
        'make_pizza_box_recycled',
        {
            resource_index['recycled_cardboard']: 3,
            resource_index['cardboard']: 1,
            resource_index['pizza_box']: -1
        }
    ),
    Process(
        'burn_pizza_box',
        {
            resource_index['pizza_box']: 1,
            resource_index['energy']: -4
        }
    ),
    Process(
        'energy_sink',
        {
            resource_index['energy']: 2
        }
    )
]

processes_index = generate_process_index(processes)

policy_elements = [
    PolicyElement(
        resource_index['cardboard'],
        processes_index['make_pizza_box_normal'],
        {
            processes_index['generate_cardboard']: 1
        }
    ),
    PolicyElement(
        resource_index['cardboard'],
        processes_index['make_pizza_box_recycled'],
        {
            processes_index['generate_cardboard']: 1
        }
    ),
    PolicyElement(
        resource_index['recycled_cardboard'],
        processes_index['make_pizza_box_recycled'],
        {
            processes_index['generate_cardboard']: 1
        }
    ),
    PolicyElement(
        resource_index['recycled_cardboard'],
        processes_index['make_pizza_box_normal'],
        {
            processes_index['generate_cardboard']: 1
        }
    ),
    PolicyElement(
        resource_index['pizza_box'],
        processes_index['burn_pizza_box'],
        {
            processes_index['make_pizza_box_normal']: 0.5,
            processes_index['make_pizza_box_recycled']: 0.5
        }
    ),
    PolicyElement(
        resource_index['energy'],
        processes_index['energy_sink'],
        {
            processes_index['burn_pizza_box']: 1,

        }
    )
]

policy = Policy(policy_elements)



scenario_elements = [
    ScenarioFlow(
        resource_index['energy'],
        value = 8,
        out_process = processes_index['energy_sink']
    )
]

scenario = Scenario(policy, scenario_elements) # type: ignore

resource_usage = scenario.measure_flow(
    FlowMeasure(
        resource_index['energy'],
        in_process = processes_index['burn_pizza_box']
    )
)

print(resource_usage)
