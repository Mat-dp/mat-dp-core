# *mat_dp_core.***constraints**

There are three more expressive Constraints: ```GeConstraint```, ```LeConstraint```, and ```EqConstraint```.  
Each of these can be used to express the conditions of a system in the form of a *constraint expression*.

### **Constraint Expressions**

**Overview:**

A constraint expression permits more advanced constraints to be defined according to one or more weighted variables.

If a constraint needs to be expressed in terms of another process, then constraint expressions can be particularly useful.  
*Hint: Constraint expressions are written just the same as objective functions.*

**Example Code:**

```py
from mat_dp_core import Resources, Processes, GeConstraint

r = Resources()
water = r.create(name="fresh water", unit="litres")

p = Processes() 
pump = p.create("water pump", (water, 100))
valve = p.create("water valve", (water, 40))

# Constraint created:
constraint = GeConstraint("weighted pump and valve GeConstraint", 5 * pump + 3 * valve, 5)

# Expression is:
# 5 * pump + 3 * valve
```

### `GeConstraint()` 

**Summary:**  
*The Ge ('greater than or equal to') Constraint class can be used to assert a given process runs __at least__ ```n``` times.*

**Parameters:**

* ```name```  
  *A string name for this constraint*

* ```weighted_processes``` process variable, or a process expression  
  *The process variable to be constrained, or a valid process expression.*

* ```bound```  
  *A float value representing the number of cycles this process must be greater than or equal to.*

**Return Type:**  ```GeConstraint```

**Location:** ```constraints.py - class GeConstraint```

**Example Code:**
```py
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


### `LeConstraint()` 

**Summary:**  
*The Le ('less than or equal to') Constraint class can be used to assert a given process runs __at most__ ```n``` times.*

**Parameters:**

* ```name```  
  *A string name for this constraint*

* ```weighted_processes``` process variable, or a process expression  
  *The process variable to be constrained, or a valid process expression.*

* ```bound```  
  *A float value representing the number of cycles this process must be less than or equal to.*

**Return Type:**  ```LeConstraint```

**Location:** ```constraints.py - class LeConstraint```

**Example Code:**
```py
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



### `EqConstraint()`

**Summary:**  
*The Eq ('equal to') Constraint class can be used to assert a given process runs __exactly__ ```n``` times.*

**Parameters:**

* ```name```  
  *A string name for this constraint*

* ```weighted_processes``` process variable, or a process expression  
  *The process variable to be constrained, or a valid process expression.*

* ```bound```  
  *A float value representing the number of cycles this process must run.*

**Return Type:**  ```EqConstraint```

**Location:** ```constraints.py - class EqConstraint```

**Example Code:**
```py
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

