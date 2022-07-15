# Mat-dp core
## *Material Demand Projections Model*

Welcome to the Mat-dp core. This repo represents the core of the MAT-dp project, which aims to deliver user-friendly and open-access software to study the environmental implications of materials used for building low-carbon systems. 

# Installation and launch

You can find [mat-dp-core in PyPi](https://pypi.org/project/mat-dp-core/). You can then install it using:

`pip install mat-dp-core`

There is an examples folder you can access either navigating to it or using the following command:

`cd examples`

You can then run examples, such as the pizza box example called test.py

# Concepts

## Definitions

The following terms will be used frequently:

Resource - A resource to be produced or consumed, such as steel or aluminium.

Process - A process which produces and/or consumes resources.

Constraint - A condition the system is placed under.

* Run Ratio Constraint - A constraint that fixes the ratio of runs between two processes - e.g. wind and solar will run at a ratio of 1:2.

* Resource Constraint - A constraint on the amount of resource produced, e.g. we must produce at least 10 energy.

* Run Eq Constraint - A constraint that specifies the number of runs a process must make.

Objective - The objective function is the property of the system which will be minimised. This could be something like the number of runs of the system, or the total cost.

Measurement - a measurement taken of the solved system, determining the 

# Usage - High Level

## Introduction

The below describes a practical example of using MAT-dp. Imagine...

* Pizza boxes are made from cardboard and recycled cardboard. *(process/resource)*
* There are different processes for making them, which have different ratios of `cardboard:recycled_cardboard` . *(process)*
* We wish to priorites the process that uses the most recycled cardboard, but not so as to eliminate the less efficient version. *(ratio constraint)*
* We then, rather inefficiently, burn them to produce energy. *(process)*
* We must produce at least 8 kWh of energy to survive the frosty winters. *(resource constraint)*
* We wish to only generate the minimum amount of cardboard and pizza boxes. *(objective)*
* How many pizza boxes must we burn to survive? *(measurement)*
## Step 1: Define resources

Firstly we must define all the resources we wish to use, with their name and units.

```py
from mat_dp_core import Resources

resources = Resources()
cardboard = resources.create("cardboard", unit="m2")
recycled_cardboard = resources.create("recycled_cardboard", unit="m2")
pizza_box = resources.create("pizza_box")
energy = resources.create("energy", unit="kWh")
```

## Step 2: Define processes

We must now take these resources and use them to define our processes. These are defined by a name and the resources that they produce and consume.

```py
from mat_dp_core import Processes
processes = Processes()
cardboard_producer = processes.create("cardboard producer", (cardboard, +1))
recycled_cardboard_producer = processes.create(
    "recycled cardboard producer", (recycled_cardboard, +1)
)
pizza_box_producer = processes.create(
    "pizza box producer",
    (recycled_cardboard, -0.5),
    (cardboard, -2),
    (pizza_box, 1),
)
recycled_pizza_box_producer = processes.create(
    "recycled pizza box producer",
    (recycled_cardboard, -3),
    (cardboard, -1),
    (pizza_box, 1),
)
power_plant = processes.create("power plant", (pizza_box, -1), (energy, 4))
energy_grid = processes.create("energy grid", (energy, -2))
```



## Step 3: Define constraints

Now we need to define the constraints of the problem. We want to specify we take equal amounts of pizza boxes from each producer *(Run ratio constraint)*, and that we only require 8 kWh of energy *(Resource constraint)*:

```py
from mat_dp_core import EqConstraint
constraints = [
    EqConstraint(
        "recycled pizza box ratio",
        pizza_box_producer - recycled_pizza_box_producer,
        0,
    ),
    EqConstraint("required energy", energy_grid, 8),
]
```

## Step 4: Define an objective function

Once we've established all of our constraints, we must define an objective function. The below example specifies we minimise the total number of runs:

```py
# Minimise total number of runs
objective = (
    cardboard_producer
    + recycled_cardboard_producer
    + pizza_box_producer
    + recycled_pizza_box_producer
    + power_plant
    + energy_grid
)
```

## Step 5: Make a measurement

We must now measure the number of pizza boxes to burn.

```py
from mat_dp_core import Measure

measurement = Measure(resources, processes, constraints, objective)
print(measurement.resource(pizza_box))
```


# Visualising the documentation


To view the documentation in html format, go to [this website](https://client.dreamingspires.dev/mat_dp_core/) 
or run the documentation through mkdocs using the following command at the root of the repository:

`poetry run mkdocs serve`

# Contributing to Mat-dp


Contributions are welcome! 

If you see something that needs to be improved, open an issue in the [respective section of the repository](https://github.com/Mat-dp/mat-dp-core/issues).
If you have questions, need assistance or need better instructions for contributing, please 
[get in touch via e-mail](mailto:refficiency-enquiries@eng.cam.ac.uk) mentioning "Mat-dp" in the subject.


Developers of mat-dp-core need to make changes using poetry with the following instructions:


Please install poetry- please see [here](https://github.com/python-poetry/poetry)

Then, install mat-dp-core with:

`poetry add mat-dp-core`

To install all the project dependencies

`poetry install`

Then go the examples folder

`cd examples`

Then run the pizza box example to test everything works.

`poetry run python3 test.py`

For any questions on how to use the software, please refer to the [documentation](https://github.com/Mat-dp/mat-dp-core/tree/master/docs). 
It contains useful definitions and examples of using the software. Please contact us by e-mail for any other support requried.

