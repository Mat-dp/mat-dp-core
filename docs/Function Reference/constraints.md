# *mat_dp_core.***further_constraints**

Constraints specify the conditions under which a system operates.  
MAT-DP Core exposes several types of constraint to help researchers assess systems under a variety of conditions.

Some examples:  

* A given town will always consume water at 3,000 cubic metres/day: no more, no less.  
  *This can be expressed as an equal to (cycles == 3000) constraint.*

* A certain cardboard factory will never produce any less than 4 tonnes of waste paper/day.
  *This can be expressed as a greater than or equal to (cycles >= 4) constraint*

* An energy firm has agreed to reduce its coal use, but to no less than 10 tonnes/day.  
  *This can be expressed as a less than or equal to (cycles <= -10) constraint.*

Constraints make more sense in the context of the [Objective](objective.md); try to imagine how constraints are useful in describing a system in the context of your operational Objective.  


## **The Three Constraints**

There are three core Constraints, intended to be helpful in MAT-DP research contexts, these are: ```RunEqConstraint```, ```RunRatioConstraint```, and ```ResourceConstraint```.

### **RunEqConstraint()**

**Summary:**  
*Run Equal (to) Constraint states that a given process must run exactly `n` times.*

**Parameters:**

* ```process``` process variable  
  *The process variable of choice.*

* ```runs``` float  
  *A float value stating the number of runs this process should be constrained to do.*

* ```name``` string  
  *A string representation of the constraint.*

**Return Type:**  ```RunEqConstraint```

**Location:** ```further_constraints.py - class RunEqConstraint```

**Example Code:**
```py
from mat_dp_core import Resources, Processes, RunEqConstraint

r = Resources()
sandwich = r.create(name="sandwich", unit="ea")

p = Processes() 
cornerShop = p.create("corner shop", (sandwich, -1))

# corner shop always consumes 20 sandwiches
constraint = RunEqConstraint(cornerShop, 20, "Corner Shop Sandwich 20pcs constraint")

# For display purposes:
print(constraint)
"""
>>> <RunEqConstraint: Corner Shop Sandwich 20pcs constraint | Equation:corner shop == 20>
"""
```

---

### **RunRatioConstraint()**

**Summary:**  
*The Run Ratio Constraint class serves to fix the number of runs of a process in relation to another.  
For example, a Wheel Factory may run at a fixed ratio to its corresponding Car Factory (4:1).*

**Parameters:**

* ```process1``` process variable  
  *The process to fix against another.*

* ```process2```  process variable  
  *The other process*

* ```p2_over_p1``` float  
  *A float value representing the fixed cycles of process1 vs process2*

* ```name``` string  
  *A string representation of the constraint.*

**Return Type:**  ```RunRatioConstraint```

**Location:** ```further_constraints.py - class RunRatioConstraint```

**Example Code:**
```py
from mat_dp_core import Resources, Processes, RunRatioConstraint

r = Resources()
flour = r.create(name="flour", unit="kilos")
bread = r.create(name="bread", unit="loaves")

p = Processes() 
flourMachine = p.create("flour maker", (flour, -0.7))
breadMachine = p.create("bread maker", (bread, 1))

constraint = RunRatioConstraint(flourMachine, breadMachine, 4, "fixed run ratio of bread to flour at 4:1")

# For display purposes:
print(constraint)
"""
>>> <RunRatioConstraint: fixed ratio of flour to bread at 4:1 | Equation:flour maker - 4*bread maker == 0>
"""
```

---

### **ResourceConstraint()**

**Summary:**  
*Sets the number runs of a process in relation to its production or consumption of a resource.  
See the example code for more details.*

**Parameters:**

* ```resource``` resource variable  
  *The resource variable to be constrained in its production or consumption.*

* ```process``` process variable  
  *The process variable to be constrained.*

* ```resource_bound``` float  
  *The float value give to the production or consumption a resource involved in this process.*

* ```name``` string  
  *A string representation of the constraint.*

**Return Type:**  ```ResourceConstraint```

**Location:** ```further_constraints.py - class ResourceConstraint```

**Example Code:**
```py
from mat_dp_core import Resources, Processes, ResourceConstraint

r = Resources()
flour = r.create(name="flour", unit="kilos")

p = Processes() 
flourMachine = p.create("flour maker", (flour, -0.7))

constraint = ResourceConstraint(resource=flour, process=flourMachine, resource_bound=4, name="Fixed output of flour at 4 units")

# For display purposes:
print(constraint)
"""
>>> <ResourceConstraint: Fixed output of flour at 4 units | Equation:flour maker == 5.714285714285714>
"""
```

---
