# MATerial Demand Projections Core

Welcome to the MAT-DP Core. This repository sits at the centre of a wider project to deliver user-friendly and open-access software solutions to environment and energy research.  
While this software *could* be used for many applications, MAT-DP Core and its documentation has been designed with the research of *'environmental impact and material usage in the building of low-carbon systems'* in mind.

## **What is MAT-DP Core?**

MAT-DP Core is a linear programming library tailored to the needs of research around material demand for low-carbon systems.  
MAT-DP Core helps technically proficient users to explore scenarios and systems relating to their research in Python.

## **Getting Started**

### **Install and Test Run**

Please install poetry, a dependency manager for Python. You can find poetry at [this Poetry GitHub page.](https://github.com/python-poetry/poetry)

You will need to download MAT-DP Core from the [MAT-DP Core Github repository here](https://github.com/dreamingspires/mat-dp-core).

To install all the project dependencies, navigate to the downloaded library at `path-to-folder/mat-dp-core` in PowerShell or Command Line, then use:

`poetry install`

To set up poetry.  
Then, navigate to the `path-to-folder/mat-dp-core/examples` folder:

`cd examples`

Now try running the premade pizza box example with:

`poetry run python3 test.py`

If successful, you should see a large number of results regarding 'energy, 'pizza_box', and 'cardboard'. This means MAT-DP Core is working as intended!

### **Definitions**

The following terms will be used frequently:

Resource - A resource to be produced or consumed, such as steel or aluminium.

Process - A process which produces and/or consumes resources.

Constraint - A condition the system is placed under.

* Run Ratio Constraint - A constraint that fixes the ratio of runs between two processes - e.g. wind and solar will run at a ratio of 1:2.

* Resource Constraint - A constraint on the amount of resource produced, e.g. we must produce at least 10 energy.

* Run Eq Constraint - A constraint that specifies the number of runs a process must make.

Objective - The objective function is the property of the system which will be minimised. This could be something like the number of runs of the system, or the total cost.

Measurement - a measurement taken of the solved system, determining the 

### **Usage**

#### **Example problem**

Below describes a practical example of using MAT-dp. Imagine...

* Pizza boxes are made from cardboard and recycled cardboard. *(process/resource)*
* There are different processes for making them, which have different ratios of `cardboard:recycled_cardboard` . *(process)*
* We wish to priorites the process that uses the most recycled cardboard, but not so as to eliminate the less efficient version. *(ratio constraint)*
* We then, rather inefficiently, burn them to produce energy. *(process)*
* We must produce at least 8 kWh of energy to survive the frosty winters. *(resource constraint)*
* We wish to only generate the minimum amount of cardboard and pizza boxes. *(objective)*
* How many pizza boxes must we burn to survive? *(measurement)*

#### **Step 1: Define resources**

Firstly we must define all the resources we wish to use, with their name and units.

```py
from mat_dp_core import Resources

resources = Resources()
cardboard = resources.create("cardboard", unit="m2")
recycled_cardboard = resources.create("recycled_cardboard", unit="m2")
pizza_box = resources.create("pizza_box")
energy = resources.create("energy", unit="kWh")
```

#### **Step 2: Define processes**

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



#### **Step 3: Define constraints**

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

#### **Step 4: Define an objective function**

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

#### **Step 5: Make a measurement**

We must now measure the number of pizza boxes to burn.

```py
from mat_dp_core import Measure

measurement = Measure(resources, processes, constraints, objective)
print(measurement.resource(pizza_box))
```
