# MaDe Core
## *(Ma)terial (De)mand software for analysing emissions reduction potential*


Welcome to the MaDe core. This repo represents the core of the MaDe project, which aims to deliver user-friendly and open-access software to study the environmental implications of materials used for building low-carbon systems. 

# Concepts

## Definitions

The following terms will be used frequently:

Resource - A resource to be produced or consumed, such as steel or aluminium.

Process - A process which produces and/or consumes resources.

Policy - A graph that describes how processes are linked.

Scenario - A specified lower bound on the resource flow or number of process runs.


# Usage - High Level

## Introduction

The below describes a practical example of using MaDe. Imagine...

* Pizza boxes are made from cardboard and recycled cardboard. *(process/resource)*
* There are different processes for making them, which have different ratios of `cardboard:recycled_cardboard` . *(process)*
* We wish to priorites the process that uses the most recycled cardboard, but not so as to eliminate the less efficient version. *(policy)*
* We then, rather inefficiently, burn them to produce energy. *(process)*
* We must produce at least 8 kWh of energy to survive the frosty winters. *(scenario)*
* How many pizza boxes must we burn to survive? *(measurement)*
## Step 1: Define resources

Firstly you must define all the resources you wish to use, with their name and units.

```py
from mat_dp_core import Resource

resources = [
    Resource('cardboard', unit = 'm2'),
    Resource('recycled_cardboard', unit = 'm2'),
    Resource('pizza_box'),
    Resource('energy', unit = 'kWh')
]
```

## Step 1a: Put resources in accessible format

You'll want to access these resources a lot, so you may find it helpful to have them structured by name rather than in a list. We have provided a helper function for this:

```py
from mat_dp_core.utils import generate_resource_index
resource_index = generate_resource_index(resources)
```


## Step 2: Define processes

You must must take these resources and use them to define your processes. These are defined by a name and the resources that they produce and consume.

```py
from mat_dp_core import Process
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
```

## Step 2a: Put processes in accessible format

Similarly to resources, you may want to use a helper function to put the processes in a more useable format:

```py
from mat_dp_core.utils import generate_process_index
process_index = generate_process_index(processes)
```

## Step 3: Define policy_elements

Now we need to define the policy graph, the linkages between the section of the graph. Each element of the policy graph is defined by:

* The resource it is relevent to
* The process node it is relevant to
* The incident processes upon that the proportion of the total is demanded from each incident process


```py
from mat_dp_core import Policy, PolicyElement

policy = Policy(
    [
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
                processes_index['make_pizza_box_normal']: 0.4,
                processes_index['make_pizza_box_recycled']: 0.6
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
)
```

## Step 4: Generate a scenario

Once you've estiblished how all the processes are linked, we must now add our scenario. The below specifies we get at least 8 kWh of energy out:

```py
from mat_dp_core import Scenario

scenario_elements = [
    ScenarioFlow(
        resource_index['energy'],
        value = 8,
        out_process = processes_index['energy_sink']
    )
]
scenario = Scenario(policy, scenario_elements)
```

## Step 5: Make a measurement

We must now measure the number of pizza boxes to burn.

We can specify an out_process, in_process or both here. Note that it will sum over the in_processes if one is not specified, and sum over the out_processes if one is not specified.

We can also specify a number of runs in our scenario.

```py
from mat_dp_core import FlowMeasure, RunMeasure
resource_usage = scenario.measure_flow(
    FlowMeasure(
        resource_index['pizza_box'],
        out_process = processes_index['burn_pizza_box']
    )
)
```
