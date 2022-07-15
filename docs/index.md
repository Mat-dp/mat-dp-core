# Material Demand Projections Core


![](res/mat%20dp%20core%20banner.png)

Welcome to the Mat-dp core. This repository sits at the centre of a wider model called Mat-dp (Material Demand Projections) which is part of a project to deliver user-friendly and open-access software solutions to environment and energy research.  
While this software *could* be used for many applications, Mat-dp core and its documentation have been designed to research *'environmental impacts and material use in the building of low-carbon systems'*.

## **What gap does Mat-dp fill?**

Materials are essential for creating the systems used in everyday life, yet, manufacturing materials emits important quantities of greenhouse gases (GHG). Emissions from material production have been estimated to increase from 5 gigatons (Gt) of CO2-equivalent to 11 Gt between 1995 and 2015. In turn, global emissions due to material production rose from 15 per cent to 23 per cent in the same period [2], while materials are estimated to contribute to over half of GHG emissions from industry[1].
Thus, identifying and implementing options for reducing material emissions are required.

Mat-dp offers an easy-to-use structure to study material demands, where the types of processes and resources can be extended as much as the user needs. To the best of our knowledge, this is the first time that such an extensible open-source python model to study materials has been developed. Previous models in the literature and other open-source models have focused on either only a subset of systems (e.g., materials for buildings) or a comprehensive, yet prescribed, set of systems which include some technologies and materials (e.g., ODYM-RECC model [3]). The reusable nature of Mat-dp makes it ideal for allowing users to focus on the process(es) they want to investigate, rather than setting up code or a mathematical model from scratch. The benefits of such reusability to advancing research in this scientific discipline cannot be understated.

Mat-dp is capable of adapting the temporal and regional specifications of users by creating the processes according to prescribed names and using indices for the desired categories, once the Mat-dp library has been added to a working example. Mat-dp also allows for different material mixes, technology changes or improvements over time, and recycled material content in a given process to be included in the model. These capabilities allow for models to be built that are tailored for a specific case-study, which might benefit decision making.

## **What is Mat-dp-core?**

Mat-dp contains a linear programming library called Mat-dp core which includes the core classes of each element and their mathematical operations for obtaining results. Mat-dp-core has an easy-to-use structure and code base with the mathematical model to let users evaluate and optimise the environmental effects of a given set of resources that are fed into one or more processes.

Mat-dp core is available [on PyPi](https://pypi.org/project/mat-dp-core/) and on [this Github repository](https://github.com/Mat-dp/mat-dp-core). Mat-dp core helps technically proficient users to explore scenarios and systems relating to their research in Python.

## **Getting Started**

### **Install and Test Run**

You can install mat-dp-core using:

`pip install mat-dp-core`

There is an examples folder you can access either navigating to it or using the following command:

`cd examples`

You can then run examples, such as the pizza box example called test.py

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

### **Contributing to mat-dp-core**

Developers of mat-dp-core need to make changes using poetry with the following instructions:

Please install poetry, a dependency manager for Python. You can find poetry at [this Poetry GitHub page.](https://github.com/python-poetry/poetry)

Then, install mat-dp-core from PyPi using:

`poetry add mat-dp-core`

To install all the project dependencies, navigate to the downloaded library at `path-to-folder/mat-dp-core` in PowerShell or Command Line, then use:

`poetry install`

To set up poetry.  

Then, navigate to the `path-to-folder/mat-dp-core/examples` folder:

`cd examples`

Now try running the premade pizza box example with:

`poetry run python3 test.py`

If successful, you should see a large number of results regarding 'energy, 'pizza_box', and 'cardboard'. This means mat-dp-core is working as intended!

### **References**

[1] Allwood, J. M., Cullen, J. M., & Milford, R. L. (2010). Options for achieving a 50. Environmental Science & Technology, 44, 1888–1894. https://doi.org/10.1021/es902909k79

[2] Hertwich, E., Lifset, R., Pauliuk, S., Heeren, N., Ali, S., Tu, Q., Ardente, F., Berrill, P.,
Fishman, T., Kanaoka, K., Makov, T., Masanet, E., Wolfram, P., Acheampong, E.,
Beardsley, E., Calva, T., Ciacci, L., Clifford, M., Eckelman, M., ... Zhu, B. (2020). 
Resource efficiency and climate change. In International Resource Panel (IRP). 
https://doi.org/10.5281/zenodo.354268084

[3] Pauliuk, S. (2020). Documentation of part IVof the RECC model framework: Open dynamic
material systems model for the resource efficiency-climate change nexus (ODYM-RECC), v2.2. University of Freiburg
