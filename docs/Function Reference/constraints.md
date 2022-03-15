# *mat_dp_core.***further_constraints**

## Conceptual Overview

Constraints specify the conditions under which a system operates.  
MAT-DP Core exposes several types of constraint to help researchers assess systems under a variety of conditions.

Some examples:  

* A given town will always consume water at 3,000 cubic metres/day: no more, no less.  
  *This can be expressed as an equal to (cycles == 3000) constraint.*

* A certain cardboard factory will never produce any less than 4 tonnes of waste paper/day.
  *This can be expressed as a greater than or equal to (cycles >= 4) constraint*

* An energy firm has agreed to reduce its coal use, but to no less than 10 tonnes/day.  
  *This can be expressed as a less than or equal to (cycles <= -10) constraint.*

Constraints make more sense in the context of an objective; try to imagine how constraints are useful in describing a system in the context of an operational objective.  
You may wish to maximise the operation of a certain process, and/or minimise the operation of another.


## **Constraints** Classes

There are three core Constraints, intended to be helpful in MAT-DP research contexts, these are: ```RunEqConstraint```, ```RunRatioConstraint```, and ```ResourceConstraint```.

## **Further Constraints** Classes

### **RunEqConstraint**

**Summary:**  
*Text*

**Parameters:**

* ```var```
  *Description*

**Return Type:**  ```type```

**Location:** ```further_constraints.py - class RunEqConstraint```

**Example Code:**
```
# Comment code
```

---

### **RunRatioConstraint**

**Summary:**  
*The Run Ratio Constraint class serves to fix the number of runs of a process in relation to another.  
For example, a Wheel Factory may run at a fixed ratio to its corresponding Car Factory (4:1).*

**Parameters:**

* ```process1```  
  *Description*

* ```process2```  
  *Description*

* ```p2_over_p1```  
  *Description*

* ```name```  
  *Description*

**Return Type:**  ```type```

**Location:** ```further_constraints.py - class RunRatioConstraint```

**Example Code:**
```
# Comment code
```

---

### **ResourceConstraint**

**Summary:**  
*Text*

**Parameters:**

* ```var```
  *Description*

**Return Type:**  ```type```

**Location:** ```further_constraints.py - class ResourceConstraint```

**Example Code:**
```
# Comment code
```

---
