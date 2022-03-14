# Resources

## Overview

For the purposes of MAT-DP, a ```Resource``` is any quantifiable direct input (consumption) or output (production) of a ```Process```. In a project for typical MAT-DP related research, each ```Resource``` is likely to be a material.

For example, in some hypothetical models:

- "hay" may be a ```Resource``` outputted by arable farms.
- "CO2" may be a ```Resource``` outputted by several processes.
- "water" may be a ```Resource``` inputted by garden centres.

Once again: *any* quantifiable direct input or output of an industrial process can be regarded as a resource for use in MAT-DP core.


## Resource Obj

The ```Resource``` object 
<!-- Necessary? -->

## Resources Obj

The ```Resources``` object serves to manage instances of different ```Resource```. It exposes methods to create, access, load (import), and dump (export) ```Resource``` objects.

### \_\_init\_\_()

Summary:  
Creates an instance of the ```Resources``` object, which is mandatory in any typical MAT-DP solution.

Parameters: ```n/a```

Return Type: ```Resources```

Location: ```resources.py - class Resources```

Example Code:  
```r = Resources() # creates a Resources object, assigns it to variable 'r'```

### create()

Summary:  
Creates an instance of a ```Resource``` object, and stores it within the calling ```Resources``` object. This is the conventional way to create a new ```Resource``` for a model.

Parameters: ```name``` string, ```unit``` string (*optional, default: ```"ea"```*)

Return Type: ```Resource``` (*Specifically, returns the  ```Resource``` you just created. Assignment of this returned object is advised and necessary for use.*)

Location: ```resources.py - class Resources```

Example Code:  
```
r = Resources()
hy = r.create("hay") # Creates a Resource object named "hay" and binds it with parent Resources object 'r'
wh = r.create("wheat", "bale") # As above, but it makes a Resource object named "wheat" AND sets its unit type to "bale"
```

### load()

Summary:  
Loads ```Resource``` object data from a conventional List of Tuples in format ```[(ResourceName, Unit), [...], (ResourceName, Unit)]```. This method is especially useful for loading in data created by the ```dump()``` method, and appropriately formatted large sets of resource data.

Parameters: ```resources``` List[Tuple[ResourceName, Unit]] / [(ResourceName, Unit), [...]]

Return Type: ```List[Resource]```

Location: ```resources.py - class Resources```

Example Code:
```
r = Resource()
myInputList = [("hay", "ea"), ("wheat", "kegs"), ("barley", "barrels")] # List of tuples containing the data we wish to load
hayWheatBarley = r.load(myInputList)
```


### method()

Summary:  
text

Parameters: ```var```

Return Type:

Location: ```fil.py - class ClassName```

Example Code:
```
# Comment
```