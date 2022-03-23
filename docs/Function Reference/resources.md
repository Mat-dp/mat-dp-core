# *mat_dp_core.***Resources**

For the purposes of MAT-DP, a resource can be any quantifiable direct input (consumption) or output (production) of a process. In a system being used for typical MAT-DP related research, each resource is likely to be a material.

For example, in some hypothetical systems:

- "hay" may be a resource outputted by arable farms.
- "CO2" may be a resource outputted by several processes.
- "water" may be a resource inputted by garden centres.

Once again: *any* quantifiable direct input or output of an industrial process can be regarded as a resource for the purposes of a MAT-DP core system.

## **Resources()**

The ```Resources``` object serves to manage different resources, such as "steel", or "hay".  
It contains methods to create, access, and otherwise handle resource data.

---

**Summary:**  
*Create an instance of the ```Resources``` object, which is mandatory in any typical MAT-DP solution.*

**Return Type:** ```Resources```

**Location:** ```resources.py - class Resources```

**Example Code:**  
```py
from mat_dp_core import Resources
r = Resources() # creates a Resources object, assigns it to variable 'r'
```

---
## **Methods**

### `.create()`

**Summary:**  
*Creates a resource, storing it with the calling ```Resources``` object. This is the conventional way to create a new resource for a system.*

**Parameters:**

* ```name``` string,
* ```unit``` string (*optional - default:* ```"ea"```)

**Return Type:** resource (*Specifically, returns the  resource you just created. Assignment of this returned object is advised and necessary for use.*)

**Location:** ```resources.py - class Resources```

**Example Code:**  
```py
from mat_dp_core import Resources

r = Resources()
# Keyword:
hy = r.create(name="hay") # optional unit argument defaults to "ea"
wh = r.create(name="wheat", unit="bale")
```

---

### `.load()`

**Summary:**  
*Loads resource data from a conventional List of Tuples in format ```[(ResourceName, Unit), [...], (ResourceName, Unit)]```. This method is especially useful for loading in data created by the ```dump()``` method, and appropriately formatted large sets of resource data.*

**Parameters:**

* ```resources``` List[Tuple[ResourceName, Unit]] / [(ResourceName, Unit), [...]]  
  *A list of tuples in the displayed format, ResourceName and Unit are strings.*

**Return Type:** ```List[Resource]```

**Location:** ```resources.py - class Resources```

**Example Code:**
```py
r = Resource()
myInputList = [("hay", "ea"), ("wheat", "kegs"), ("barley", "barrels")] # List of tuples containing the data we wish to load
hayWheatBarley = r.load(myInputList)
```

---

### `.dump()`

**Summary:**  
*Returns a tuple list representation of all resources existing in this ```Resources``` object's context.*

**Parameters:**

* ```n/a```

**Return Type:**  ```List[Tuple[ResourceName (string), Unit (string)]]```

**Location:** ```resources.py - class Resources```

**Example Code:**
```py
from mat_dp_core import Resources

r = Resources()
hy = r.create(name="hay", unit="bales")
st = r.create(name="steel", unit="kilograms")
fe = r.create(name="feathers", unit="kilograms")

myTupleList = r.dump()
print(myTupleList)

>>> [('hay', 'bales'), ('steel', 'kilograms'), ('feathers', 'kilograms')]
```

---

## **Length**

**Summary:**  
*The number of resources currently managed by a ```Resources``` instance.*

**Return Type:**  ```int```

**Location:** ```resources.py - class Resources```

**Example Code:**
```py
from mat_dp_core import Resources

r = Resources()
cl = r.create(name="coal")
wt = r.create(name="water")

numberOfResources = len(r)

print(numberOfResources)

>>> 2
```

<!--
---

### .\_\_getitem\_\_()

**Summary:**  
*Returns a resource corresponding to two search parameters. Not intended for end-users*

**Parameters:**

* ```index```
  *integer describing the position of the *

* ```name```
  *Description*

**Return Type:**  ```type```

**Location:** ```fil.py - class ClassName```

**Example Code:**
```
# Comment code
```

---
-->

<!--
### .method()

**Summary:**  
*Text*

**Parameters:**

* ```var```  
  *Description*

**Return Type:**  ```type```

**Location:** ```fil.py - class ClassName```

**Example Code:**
```
# Comment code
```

---


-->
<!-- Non-essential, covering more vital content first
## **Resource** Class (*Advanced*)

The ```Resource``` object is not intended for end-users.  
Nevertheless, advanced users may find some of its properties or methods useful. It is important not to instantiate the ```Resource``` object without using the ```Resources.create()``` method, otherwise the resource will be ignored. -->
