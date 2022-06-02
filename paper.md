---
title: 'Mat-dp: An open-source Python model for analysing material demand projections and their environmental implications, 
which result from building low-carbon systems.'
tags:
  - materials
  - Python
  - low carbon
  - material efficiency
  - material demand 
  - environmental implications
  - embodied emissions
authors:
 - name: Karla Cervantes Barron
   orcid: 0000-0002-4081-3175
   affiliation: 1
 - name: Jonathan M Cullen
   orcid: 0000-0001-9367-1791
   affiliation: 1
affiliations:
 - name: University of Cambridge
   index: 1
date: 30th April 2022
bibliography: paper.bib
---

# Summary

MAT-dp is a python model which aims to calculate the amounts and types of materials needed for building any system
or resource transformation including those found along any supply chain- but is particularly applied to studying
the materials needed for building low-carbon systems- and estimate the environmental implications associated to such materials.


Mat-dp has an easy-to-use structure and code base with the mathematical model to let users evaluate and optimise the environmental 
effects of a given set of resources that are fed into one or more processes. This code base is called mat-dp-core, since it contains 
the core classes of each elements and their mathematical operations for obtaining results.


In Mat-dp, the system and its required materials are defined as a series of resources that are fed 
into different processes, which in turn have a defined set of outputs. 
The outputs can be the result of the process, e.g., energy, materials or greenhouse gas emissions. 
The system can then be optimised by using three types of constraints built into Mat-dp, depending on the desired 
output of the process, e.g., a required electricity capacity of an offshore wind installation. 
The three types of constraints that can be defined are: a given ratio of process runs (Run Ratio Constraint), 
a given number of resources produced (Resource Constraint), and a given number of process runs (Run Eq Constraint)
that the system has to comply with.
The model results obtained can then be exported and further explored.

# Statement of need

Materials are essential for creating the systems used in everyday life, yet, manufacturing materials emits important quantities of
greenhouse gases (GHG). Emissions from material production have been estimated to increase
from 5 gigatons (Gt) of CO2-equivalent to 11 Gt between 1995 and 2015. 
In turn, global emissions due to material production rose from 15 per cent to 23 per cent in the same period [@Hertwich2020], while
materials are estimated to contribute to over half of GHG emissions from industry [@Allwood2010].  
Thus, identifying and implementing options for reducing material emissions is required.


Mat-dp offers an easy-to-use structure to study material demands, where the types of processes and resources can
be extended as much as the user needs. To the best of our knowledge, this is the first time that such an extensible
open-source python model to study materials has been developed. Previous models in the literature and as open-source models have
focused on either only a subset of systems (e.g., materials for buildings) or a comprehensive, yet prescribed, set of systems which include  
some technologies and materials (e.g., ODYM-RECC model [@Pauliuk2020]). The reusable nature of Mat-dp makes it ideal for allowing
users to focus on the process(es) they want to investigate, rather than setting up code or a mathematical model
from scratch. The benefits of such reusability to advancing research in this scientific discipline cannot be understated.


Mat-dp is capable of adapting the temporal and regional specifications of users by creating the processes
according to prescribed names and using indices for the desired categories once the Mat-dp library has been imported
to a working example. Mat-dp also allows for different material mixes, technology changes or improvements over time, 
and recycled material content in a given process to be included in the model. These capabilities allow for models to be built
that are tailored for a specific case-study, which might benefit decision making.


# Target Audience

The model facilitates the framing of resource flows and the optimisation of their flows 
in and out of systems which can then be easily visualised. This allows for users to explore 
alternative ways to build systems by either reducing or changing their inputs, maximising 
their outputs or by minimising their emissions or waste.


MAT-dp has been used to study the environmental implications of electricity systems, where each 
power plant is considered a process in the model. However, these processes can be anything along 
any supply chain or resource transformation, as long as the user knows the resources that are 
fed into the processes. 


# Acknowledgements

We acknowledge the contribution from Maaike E Hakker in the inception of 
this project, and the contribution from Edd Salkield, Mark Todd, and Elliott Hughes 
who have helped refactor the model into its current extensible form.


This material has been produced under the Climate Compatible Growth programme, which 
is funded by UK aid from the UK government. However the views expressed herein do not 
necessarily reflect the UK government's official policies.

# References
