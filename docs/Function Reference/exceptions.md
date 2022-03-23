# **Exceptions**

## **Inconsistent Orders of Magnitude**

**The system is unsolvable with the existing degrees of magnitude.**  
This exception is typically raised when the order of magnitude for resources between processes and constraints varies by a large degree, e.g. the mixing of metric grams and metric tons.

## **Over Constrained**

**The system is unsolvable under the current constraints.**  
A common cause of this exception is the absence of a process to either produce or consume a given resource. This is because a tacit constraint of MAT-DP systems is that all resources must sum to 0: everything produced must eventually be consumed.  
In the worked 'Three Factories' example from Measure and Objective, the `environment`  process serves to consume the `CO2` resource.

## **Unbounded Solution**

**The system can reach an infinite objective score under the current constraints.**  
This error will occur if one or more processes is counted toward the objective function, and they do not have a direct or indirect constraint limiting the number of runs they may fulfil.

## **Iteration limit reached**

**Please report this to Dreaming Spires if encountered!**
