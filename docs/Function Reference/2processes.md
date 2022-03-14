# Processes

## Conceptual Overview

In the abstract, a process is any describable entity or recurrence that consumes and/or produces resources within a system.  
In a system typical of MAT-DP related research, a process is likely to be associated with a factory, business, or an entire industry.

Some simplified example are below:

- In a study of wind-turbine manufacture, a blade factory may be a process.  
  (inputs "metal", outputs "blades")
- A business that manufactures cars may be considered a process.  
  (inputs "engine block", outputs "vehicles")
- On a regional scale, the gas turbine industry of a country might be considered a process.  
  (inputs "gas", outputs "electricity" and "CO2")

Note: a process can have any number or combination of input and outputs resources.
<!-- TODO: Check this is true -->

## **Processes** Class

### Overview

The ```Processes``` class is responsible for the management of several processes.  
In all cases, just one ```Processes``` object is made to handle these processes. The way processes are managed by this object is very similar to instances of the ```Resources``` class.

---

### \_\_init\_\_()

**Summary:**  
*Creates an instance of the ```Processes``` class, which is mandatory in any MAT-DP solution.*

**Parameters:**

* ```n/a```

**Return Type:**  ```Processes```

**Location:** ```processes.py - class Processes```

**Example Code:**
```
from mat_dp_core import Processes

p = Processes()
```

---


