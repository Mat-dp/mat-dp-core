# Constraints

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

### Overview

There are three core Constraints classes: ```GeConstraint```, ```LeConstraint```, and ```EqConstraint```.  
Each of these can be used to express the conditions of a system. Constraints can be hard to devise, but should be straightforward to implement.

There are three 'further' Constraints classes, intended to be helpful in MAT-DP research contexts, these are: ```RunEqConstraint```, ```RunRatioConstraint```, and ```ResourceConstraint```.

### **GeConstraint** \_\_init\_\_()

**Summary:**  
*The Ge ('greater than or equal to') Constraint class can be used to assert a given process runs __at least__ ```n``` times.*

**Parameters:**

* ```name```  
  *A string name for this constraint*

* ```process```  
  *The process variable to be constrained*

* ```bound```  
  *A float value representing the number of cycles this process must be greater than or equal to.*

**Return Type:**  ```GeConstraint```

**Location:** ```constraints.py - class GeConstraint```

**Example Code:**
```
from mat_dp_core import Resources, Processes, GeConstraint

r = Resources()
water = r.create(name="fresh water", unit="litres")

p = Processes() 
pump = p.create("water pump", (water, 100))

# Constraint created:
constraint = GeConstraint("minimum pump cycles", pump, 5)

# For display purposes:
print(constraint)
"""
>>> <GeConstraint: minimum pump cycles | Equation:- water pump <= -5>
"""
```

---


### **LeConstraint** \_\_init\_\_()

**Summary:**  
*The Le ('less than or equal to') Constraint class can be used to assert a given process runs __at most__ ```n``` times.*

**Parameters:**

* ```name```  
  *A string name for this constraint*

* ```process```  
  *The process variable to be constrained*

* ```bound```  
  *A float value representing the number of cycles this process must be less than or equal to.*

**Return Type:**  ```LeConstraint```

**Location:** ```constraints.py - class LeConstraint```

**Example Code:**
```
from mat_dp_core import Resources, Processes, LeConstraint

r = Resources()
engine = r.create(name="engine", unit="ea")

p = Processes() 
factory = p.create("engine factory", (engine, 1))

# Factory can produce no more than 50 engines
constraint = LeConstraint("maximum", factory, 50)

# For display purposes:
print(constraint)
"""
>>> <LeConstraint: maximum | Equation:engine factory <= 50>
"""
```

---


### **EqConstraint** \_\_init\_\_()

**Summary:**  
*The Eq ('equal to') Constraint class can be used to assert a given process runs __exactly__ ```n``` times.*

**Parameters:**

* ```name```  
  *A string name for this constraint*

* ```process```  
  *The process variable to be constrained*

* ```bound```  
  *A float value representing the number of cycles this process must run.*

**Return Type:**  ```EqConstraint```

**Location:** ```constraints.py - class EqConstraint```

**Example Code:**
```
from mat_dp_core import Resources, Processes, EqConstraint

r = Resources()
sandwich = r.create(name="sandwich", unit="ea")

p = Processes() 
cornerShop = p.create("corner shop", (sandwich, -1))

# corner shop always consumes 20 sandwiches
constraint = EqConstraint("uses exactly 20 sandwiches", cornerShop, 20)

# For display purposes:
print(constraint)
"""
>>> <EqConstraint: uses exactly 20 sandwiches | Equation:corner shop == 20>
"""
```

---

## **Further Constraints** Classes

### **RunEqConstraint** \_\_init\_\_()

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

### **RunRatioConstraint** \_\_init\_\_()

**Summary:**  
*Text*

**Parameters:**

* ```var```
  *Description*

**Return Type:**  ```type```

**Location:** ```further_constraints.py - class RunRatioConstraint```

**Example Code:**
```
# Comment code
```

---

### **ResourceConstraint** \_\_init\_\_()

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
