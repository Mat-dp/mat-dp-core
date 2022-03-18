# *mat_dp_core.***measure**

Measure is the workhorse of MAT-DP core; resources, constraints, processes, and an objective function have set a stage and provided inputs, and Measure will solve the system according to these.

## **Objective Example Continued**

The most basic usage of measure should not be too difficult, see the complete code for the '3 power plants' example below:

```py
from mat_dp_core import Resources, Processes, GeConstraint, LeConstraint, Measure

r = Resources()
electricity = r.create("electricity", "kwh")
carbon_dioxide = r.create("CO2", "tonnes")

p = Processes()
coal_plant = p.create("Coal Power Plant", (carbon_dioxide, 1), (electricity, 100))
gas_plant = p.create("Gas Power Plant", (carbon_dioxide, 0.6), (electricity, 100))
organic_plant = p.create("Organic Mass Power Plant", (carbon_dioxide, 0.8), (electricity, 100))
environment = p.create("The Atmosphere", (carbon_dioxide, -1))
grid = p.create("The Energy Grid", (electricity, -100))

coal_capacity = LeConstraint("Coal Plant Capacity 2,000kwh", coal_plant, 20)
gas_capacity = LeConstraint("Gas Plant Capacity 1,500kwh", gas_plant, 15)
organic_capacity = LeConstraint("Organic Plant Capacity 1,000kwh", organic_plant, 10)
grid_needs = GeConstraint("Grid Requirement of 2,200kwh", grid, 22)

objective = environment

# constraints must be passed to measure in a list, so we put them in a list here.
constraints = [coal_capacity, gas_capacity, organic_capacity, grid_needs]

# To solve this system, only 4 parameters need to be passed:
measure = Measure(resources=r, processes=p, constraints=constraints, objective=objective)


# For display purposes:
print("\n\n\nTonnes of CO2 produced by process:\n")
for process in measure.resource(resource=carbon_dioxide):
    print(str(process[0].name).ljust(30) + ":  " + str(round(process[1], 1)))

print("\n\n")

print("kwh of electricity produced by process:\n")
for process in measure.resource(resource=electricity):
    print(str(process[0].name).ljust(30) + ":  " + str(round(process[1], 1)))

"""


>>> Tonnes of CO2 produced by process:

>>> Coal Power Plant              :  0.0
>>> Gas Power Plant               :  9.0
>>> Organic Mass Power Plant      :  5.6
>>> The Atmosphere                :  -14.6
>>> The Energy Grid               :  0.0



>>> kwh of electricity produced by process:

>>> Coal Power Plant              :  0.0
>>> Gas Power Plant               :  1500.0
>>> Organic Mass Power Plant      :  700.0
>>> The Atmosphere                :  0.0
>>> The Energy Grid               :  -2200.0
"""
```

## **Measure()**

The ```Measure``` class is responsible for solving a system.  
Just one ```Measure``` object is made to handle this.  

---

**Summary:**  
*Creates an instance of the ```Measure``` class, which will immediately attempt to solve the MAT-DP system.*

**Parameters:**

* `resources` Resources  
  *Resources object*

* `processes` Processes  
  *Processes object*

* `constraints` \[constraints\]  
  *A list of all constraints involved in the system.*

* `objective` the objective function  
  *The objective function being applied to this system.*

* `maxiter` int - OPTIONAL, default `None`  
  *Allows assignment of the maximum number of iterations for the solver to run*

* `allow_inconsistent_order_of_mag` bool - OPTIONAL, default `False`  
  *Permits inconsistent orders of magnitude (advanced).*

**Return Type:**  ```Measure```

**Location:** `measure.py - class Measure`

**Example Code:**

```py
measure = Measure(resources=r, processes=p, constraints=constraints, objective=objective)
```

---

## **Methods**

### `.run()`

**Summary:**  
*Returns the number of runs for a particular process or all the processes in the system. Optionally returns these with consideration for bounds.*

**Location:** `measure.py - class Measure`

---

#### **Option 1**  
**Parameters:**

* ```bounds``` bool  
  *Specifies whether bounds should be considered.*

**Return Type:**  ```[[_processes, run_vector, run_vector_lb, run_vector_ub], [...]]``` or ```[[_processes, run_vector]]```

---

#### **Option 2**  
**Parameters:**

* ```process``` process variable  
  *Specifies which specific process' run count should be returned.*

* ```bounds``` bool  
  *Specifies whether bounds should be considered.*

**Return Type:**  ```[runs, runs_lb, runs_ub]``` or ```[runs]```

---

#### **Example Code**
```py
measure = Measure(r, p, [constraints], objective)
# Option 1
print(measure.run(process=my_process, bounds=False))
# Option 2
print(measure.run(bounds=False))

# Below displayed values are from the three power plants example
"""
>>> [(<Process: Coal Power Plant>, 1.9815267861864423e-10), [...]]]
>>> 22.0078009099
"""
```

---

### `.resource()`

**Summary:**  
*Used to return information regarding resources in relation to the entire system or specific processes. Available with various options.*

**Location:** `measure.py - class Measure`

---

#### **Option 1**  

**Description:**  
*Returns measurements for all processes and resources.*

**Parameters:**

* ```bounds``` bool  
  *Whether or not to calculate bounds.*

**Return Type:**  ```list```

---

#### **Option 2**  

**Description:**  
*Returns input and output resource values for the process specified.*

**Parameters:**

* ```process``` process variable  
  *A process to be measured.*

* ```bounds``` bool  
  *Whether or not to calculate bounds.*

**Return Type:**  ```list```

---

#### **Option 3**  
**Parameters:**

* ```resource```  
  *The resource to be measured.*

* ```bounds```  
  *Whether or not to calculate bounds.*

**Return Type:**  ```list```

---

#### **Option 4**  
**Parameters:**

* ```process``` process variable  
  *The process to be measured.*

* ```resource``` resource variable  
  *The resource to be measured.*

* ```bounds``` bool - OPTIONAL, default False  
  *Whether or not to calculate bounds.*

**Return Type:**  ```list```

---

#### **Example Code**
```
# Comment code
```

### `.flow()`

**Summary:**  
*Used to return information regarding __flow__ of resources in relation to the entire system or to / from specific processes. Available with various options.*

**Location:** `measure.py - class Measure`

---
#### **Option 1**  
**Summary:**  
*Returns all flows between each process pair and each resource.*

**Parameters:**

* ```bounds``` bool - OPTIONAL, default False  
  *Whether or not to calculate bounds.*

**Return Type:**  ```list```

---

#### **Option 2**  
**Summary:**  
*Returns all flows between the process pair specified.*

**Parameters:**

* ```process_from``` process variable  
  *The process that the resource is flowing from.*

* ```process_to``` process variable  
  *The process that the resource is flowing into.*

* ```bounds``` bool - OPTIONAL, default False  
  *Whether or not to calculate bounds.*

**Return Type:**  ```list```

---

#### **Option 3**  
**Summary:**  
*Returns all flows for the resource specified.*

**Parameters:**

* ```resource``` resource variable  
  *The resource to measure flows for.*

* ```bounds``` bool - OPTIONAL, default False  
  *Whether or not to calculate bounds.*

**Return Type:**  ```list```

---

#### **Option 4**  
**Summary:**  
*Returns the sum of all outflows from this process for each resource.*

**Parameters:**

* ```process``` process variable  
  *The process that the resources are flowing from.*

* ```bounds``` bool - OPTIONAL, default False  
  *Whether or not to calculate bounds.*

**Return Type:**  ```list```

---

#### **Option 5**  
**Summary:**  
*Returns the sum of all outflows from this process for this resource.*

**Parameters:**

* ```process_from``` process variable  
  *The process material is flowing from.*

* ```resource``` resource variable  
  *The resource that is flowing.*

* ```bounds``` bool - OPTIONAL, default False  
  *Whether or not to calculate bounds.*


**Return Type:**  ```list```

---

#### **Option 6**  
**Summary:**  
*Returns the sum of all inflows into this process for each resource*

**Parameters:**

* ```process_to``` process variable  
  *The process that the resource is flowing into.*

* ```resource``` resource variable  
  *The resource to measure.*

* ```bounds``` bool - OPTIONAL, default False  
  *Whether or not to calculate bounds.*


**Return Type:**  ```list```

---

#### **Option 7**  
**Summary:**  
*Returns the sum of all inflows into this process for this resource.*

**Parameters:**

* ```process_from``` process variable  
  *The process that the resource is flowing from.*

* ```process_to``` process variable  
  *The process that the resource is flowing into.*

* ```resource``` resource variable  
  *The resource to measure.*

* ```bounds``` bool  
  *Whether or not to calculate bounds.*

**Return Type:**  ```list```

---

#### **Example Code**
```
# Comment code
```


### `.cumulative_resource()`

**Summary:**  
*Calculates resources leading up to all processes, or a given process. For example, all the steel contributing the manufacture of a boat. Available with various options.*

**Location:** `measure.py - class Measure`

---

#### **Option 1**  
**Summary:**  
*Returns the amount of each resource used for the entire chain of processes that led to each process.*

**Parameters:**

* ```bounds``` bool - OPTIONAL, default False  
  *Whether or not to calculate bounds.*

**Return Type:**  ```list```

---

#### **Option 2**  
**Summary:**  
*Returns the amount of each resource used for the entire chain of processes that led to __this__ process.*

**Parameters:**

* ```process``` process variable  
  *The process that the resource is flowing into.*

* ```bounds``` bool - OPTIONAL, default False  
  *Whether or not to calculate bounds.*

**Return Type:**  ```list```

---

#### **Option 3**  
**Summary:**  
*Returns the amount of resource used for the entire chain of processes that led to each process.*

**Parameters:**

* ```resource``` resource variable  
  *The resource to be measured.*

* ```bounds``` bool - OPTIONAL, default False  
  *Whether or not to calculate bounds.*

**Return Type:**  ```list```

---

#### **Option 4**  
**Summary:**  
*Returns the amount of resource used for the entire chain of processes that led to this process.*

**Parameters:**

* ```process``` process variable  
  *The process that the resource is flowing into.*

* ```resource``` resource variable  
  *The resource to be measured.*

* ```bounds``` bool - OPTIONAL, default False  
  *Whether or not to calculate bounds.*

**Return Type:**  ```list```

---

#### **Example Code**
```
# Comment code
```



