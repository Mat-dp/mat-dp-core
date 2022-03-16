# **Objective**

In any MAT-DP system, there must be an objective to be achieved.  
One may wish to maximise the runs of a certain process, and/or minimise the runs of another.

An objective function in MAT-DP Core is expressed very similarly to a [constraint expression](advancedconstraints.md): an objective helps to find an 'optimal' valid means of operation, while a constraint defines what is valid in the first place.

---

An objective function will always aim to minimise its result.  

Below is an example of a minimising objective function:

```
objective = 5 * coal_power_plant + gas_power_plant + 4 * oil_power_plant
```

Lets take one section of the function: `5 * coal_power_plant`  
The process variable `coal_power_plant` by itself contributes +1 to the value of the objective function each time it 'runs'.  
`5 * ` is a multiplier to the runs of process variable `coal_power_plant` - this is typically called a 'weighting'.  
As a consequence of the `5 * ` weighting, during Measurement the solution will favour **reducing** runs of the `coal_power_plant` five times more than runs of the `gas_power_plant`.

---

An objective makes the most sense in the context of an optimisation problem.

Below is an optimisation problem concerning how to provide a power grid with sufficient kwh of electricity. The constraints involve not exceeding the capacity of each plant, while meeting the demand of the grid.

There exists the following processes:

* A coal power plant, producing 100kwh for every 1 tonnes of CO2.
* A gas power plant, producing 100kwh for every 0.6 tonnes of CO2.
* An organic waste power plant, producing 100kwh for every 0.8 tonnes of CO2.

The following constraints:

* The coal power plant cannot produce more than 2,000kwh/day.
* The gas power plant cannot produce more than 1,500kwh/day.
* The organic waste power plant cannot produce more than 1,000kwh/day.
* The combined output of all three power plants must meet the needs of the grid: 2,200kwh/day.

The optimisation objective of:

* Minimise the amount of CO2 produced by the system.

Let's break the above problem into code:

```

```
