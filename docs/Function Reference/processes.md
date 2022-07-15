# *mat_dp_core.***Processes**

In the abstract, a process is any describable entity or recurrence that consumes and/or produces [resources](resources.md) within a system.  
In a system typical of Mat-dp related research, a process is likely to be associated with a factory, business, or an entire industry.

Some simplified examples are below:

- In a study of wind-turbine manufacture, a blade factory may be a process.  
  (inputs "metal", outputs "blades")
- A business that manufactures cars may be considered a process.  
  (inputs "engine block", outputs "vehicles")
- On a regional scale, the gas turbine industry of a country might be considered a process.  
  (inputs "natural gas", outputs "electricity" and "CO2")

Note: a process can have any number or combination of input and output resources.

## **Processes()**

The ```Processes``` class is responsible for the management of several processes.  
In all cases, just one ```Processes``` object is made to handle these. The way processes are created and managed by this object is very similar to instances of the ```Resources``` class.

---

**Summary:**  
*Creates an instance of the ```Processes``` class, which is mandatory in any MAT-DP solution.*

**Return Type:**  ```Processes```

**Location:** ```processes.py - class Processes```

**Example Code:**
```py
from mat_dp_core import Processes

p = Processes() # variable 'p' is now an instance a 'Processes' object
```

---

## **Methods**

### `.create()`

**Summary:**  
*Creates a process, i.e. a resource producer and/or consumer for a system.*

**Parameters:**

* ```name```  
  *A string name representation of the process, e.g. "paper factory"*

* ```resources```  
  *One or many data tuples representing the resource(s) involved in this process.  
  Each tuple describes the consumption and/or production ratios of a resource in the process.  
  Any number of different resources can be produced or consumed by a process.  
  (resourceVariable, rate) / (water, 5)  
  (resourceVariable, (rate, low-bound rate, up-bound rate)) / (water, (5, 4, 6))  
  See the Example Code section for more details.*


**Return Type:**  ```Process```

**Location:** ```processes.py - class Processes```

**Example Code:**
```py
from mat_dp_core import Resources, Processes

# A process cannot exist without its resource, so we create those first.
r = Resources()
water = r.create(name="fresh water", unit="litres")
coal = r.create(name="minable coal", unit="kilos")
steam = r.create(name="steam", unit="kilos")

# Creating the Processes object, which manages our processes.
p = Processes() 

# A simple producer process. Creates 100 litres of water per 'cycle'.
pump = p.create("water pump", (water, 100))

# A producer process with: (target, lower, and upper) bounds.
# When solved, MAT-DP core will simulate the mine creating:
# 10 (target), 9 (lower) or 11 (upper) minable coal per 'cycle'.
mine = p.create("coal mine", (coal, (10, 9, 11)))

# A consumer and producer process (produces steam, consumes water and coal).
# NB: Resource consumption is effectively 'negative production': (water, *-1*).
# Note that a process can consume or produce any number of different resources
boiler = p.create("steam boiler",
    (steam, (0.85, 0.8, 0.9)),
    (water, -1),
    (coal, -0.01))


# For display purposes:
for process in p:
    print(process)
"""
>>> <Process: water pump>
>>> <Process: coal mine>
>>> <Process: steam boiler>
"""
```

---

### `.load()`

**Summary:**  
*Loads and creates processes from using a conventional List of Tuples in the format:  
```[(processName (resourceVariable, rate)), (processName (resourceVariable, (rate, low-bound rate, up-bound rate))) [...]]```*

**Parameters:**

* ```processes```  
  ```py
  List[Tuple[processName Tuple[resourceVariable, rate]]] /
  List[Tuple[processName Tuple[resourceVariable, Tuple[rate, low-bound rate, up-bound rate]]]]
  ```  
  *A list of tuples in the displayed format.*  
  processName - string  
  resourceVariable - process created by a ```Processes``` object  
  rate, and up/low bound rate - integer or float values


**Return Type:**  ```List[process]```

**Location:** ```processes.py - class Processes```

**Example Code:**
```py
from mat_dp_core import Resources, Processes

r = Resources()
hay = r.create("hay")
p = Processes()
p.load([("smallFarm", [(hay, 2)]),
("bigFarm", [(hay, 20)]),
("hugeFarm", [(hay, 200)])])

# For display purposes:
for process in p:
    print(process)

"""
>>> <Process: smallFarm>
>>> <Process: bigFarm>
>>> <Process: hugeFarm>
"""
```

---

### `.dump()`

**Summary:**  
*Returns a tuple list representation of all processes existing in this ```Processes``` object's context.*

**Parameters:**

* ```n/a```

**Return Type:** ```[Tuple[processName, np.array([2.0]), np.array([2.0]), np.array([2.0]))]```

**Location:** ```processes.py - class Processes```

**Example Code:**
```py
from mat_dp_core import Resources, Processes

r = Resources()
hay = r.create("hay")
p = Processes()
p.load([("smallFarm", [(hay, 2)]),
("bigFarm", [(hay, 20)]),
("hugeFarm", [(hay, (200, 180, 220))])])

dumpVariable = p.dump()

# For display purposes:
for entry in dumpVariable:
    print(entry)
"""
>>> ('smallFarm', array([2.]), array([2.]), array([2], dtype=object))
>>> ('bigFarm', array([20.]), array([20.]), array([20], dtype=object))
>>> ('hugeFarm', array([200.]), array([180.]), array([220], dtype=object))
"""
```

---

## Length

**Summary:**  
*Returns the number of processes currently managed by the calling ```Processes``` object.*

**Parameters:**

* ```n/a```

**Return Type:**  ```int```

**Location:** ```processes.py - class Processes```

**Example Code:**
```py
from mat_dp_core import Resources, Processes

r = Resources()
water = r.create(name="fresh water", unit="litres")
coal = r.create(name="minable coal", unit="kilos")
steam = r.create(name="steam", unit="kilos")

p = Processes() 
pump = p.create("water pump", (water, 100))
mine = p.create("coal mine", (coal, (10, 9, 11)))
boiler = p.create("steam boiler",
    (steam, (0.85, 0.8, 0.9)),
    (water, -1),
    (coal, -0.01))

# Use of __len__ on the Processes object 'p':
print(len(p))
"""
>>> 3
"""
```

---


