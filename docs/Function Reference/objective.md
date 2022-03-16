# **Objective**

In any MAT-DP system, there must be an objective to be achieved.  
One may wish to maximise the runs of a certain process, and/or minimise the runs of another.

An objective function in MAT-DP Core is expressed very similarly to a [constraint expression](advancedconstraints.md): an objective helps to find an 'optimal' valid means of operation, while a constraint defines what is valid in the first place.

Below is an example objective function:

`objective = 5 * coal_power_plant + 2 * gas_power_plant + 4 * oil_power_plant`


