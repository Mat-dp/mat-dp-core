from dataclasses import dataclass
from typing import Dict, Generic, List, Optional, Tuple, TypeVar, Union

from mat_dp_core.maths_core import (
    calculate_actual_resource,
    calculate_run_matrix,
    calculate_run_scenario,
    calculate_run_vector,
    calculate_actual_resource_flow,
    get_flow_slice,
    measure_resource_usage,
    alt_measure_resource_usage,
)
import numpy as np
from dataclasses import dataclass
ResourceName = str
ProcessName = str

# TODO: define __repr__ for each class

class Resource:
    def __init__(self, name: ResourceName, unit: str = 'ea'):
        self.name = name
        self.unit = unit

    def __repr__(self):
        return f'<Resource: {self.name}>'


class Process:
    def __init__(
        self, 
        name: ProcessName, 
        demands: Dict[Resource, float]
    ):
        self.name = name
        self.demands = demands

    def __repr__(self):
        return f'<Process: {self.name}>'


class PolicyElement:
    resource: Resource
    process: Process
    demands: Dict[Process, float]
    def __init__(
        self, 
        resource: Resource, 
        process: Process, 
        demands: Dict[Process, float]
    ):

        if resource not in demands.keys():
            raise ValueError(f'Resource {resource} not found in demands')
        if resource not in process.demands.keys():
            raise ValueError(f'Resource {resource} not found in process demands for process {process}')
        if process in process.demands.keys():
            raise ValueError(f'Self demanding process {process}')
        total_incidence = sum(demands.values())
        if total_incidence != 1:
            raise ValueError(f'Total incidence for process {process} not 1 but {total_incidence}')
        self.resource = resource
        self.process = process
        self.demands = demands
    
    def __repr__(self):
        return f'<PolicyElement for Process: {self.process}, Resource: {self.resource}>'

class Policy:
    def __init__(self, elements: List[PolicyElement]):
        def get_processes_from_policy_elements(policy_elements: List[PolicyElement]) -> List[Process]:
            processes = []
            for policy_element in policy_elements:
                if policy_element.process not in processes:
                    processes.append(policy_element.process)
                for process in policy_element.demands.keys():
                    if process not in processes:
                        processes.append(policy_element.process)
            return processes
        
        def get_resources_from_processes(processes: List[Process]) -> List[Resource]:
            resources = []
            for process in processes:
                for resource in process.demands.keys():
                    if resource not in resources:
                        resources.append(resource)
            return resources
        
        def generate_process_demands(resources: List[Resource], processes: List[Process]):
            process_demands = np.zeros((len(processes), len(resources)))
            resource_index = {resource: i for i, resource in enumerate(resources)}
            for i, process in enumerate(processes):
                for resource, value in process.demands.items():
                    j = resource_index[resource]
                    process_demands[i][j] = value
            return process_demands
        
        def generate_policy(
            resources: List[Resource], 
            processes: List[Process], 
            policy_elements: List[PolicyElement]
        ):
            policy = np.zeros(
                (len(processes), len(processes), len(resources))
            )
            resource_index = {resource: i for i, resource in enumerate(resources)}
            process_index = {process: i for i, process in enumerate(processes)}

            for policy_element in policy_elements:
                k = resource_index[policy_element.resource]
                j = process_index[policy_element.process]
                for incident_process, value in policy_element.demands.items():
                    i = process_index[incident_process]
                    policy[i][j][k] = value
            return policy

        self.processes = get_processes_from_policy_elements(elements)
        self.resources = get_resources_from_processes(self.processes)
        self.process_demands = generate_process_demands(self.resources, self.processes)        
        self.policy = generate_policy(self.resources, self.processes, elements)
        self.run_matrix = calculate_run_matrix(self.process_demands, self.policy)
        self.elements = elements

    def __repr__(self):
        return f'<Policy formed of : {self.elements}>'

class BaseFlow:
    def __init__(
        self,
        resource: Resource,
        in_process: Optional[Process] = None,
        out_process: Optional[Process] = None
    ):
        self.resource = resource
        self.in_process = in_process
        self.out_process = out_process

        if in_process is None and out_process is None:
            raise ValueError('Must supply at least one of in_process, out_process')

        if in_process is not None:
            if resource not in in_process.demands.keys():
                raise ValueError(f'{resource} is not produced or consumed by {in_process}')
            if in_process.demands[resource] >= 0:
                raise ValueError(f'{in_process} does not produce {resource}')

        if out_process is not None:
            if resource not in out_process.demands.keys():
                raise ValueError(f'{resource} is not produced or consumed by {out_process}')
            if out_process.demands[resource] <= 0:
                raise ValueError(f'{out_process} does not consume {resource}')


@dataclass
class ScenarioRun:
    process: Process
    n_runs: float
    def __repr__(self):
        return f'<ScenarioRun for process {self.process}>'

class ScenarioFlow(BaseFlow):
    def __init__(
        self,
        resource: Resource,
        value: float,
        in_process: Optional[Process] = None,
        out_process: Optional[Process] = None
    ):
        self.value = value
        super().__init__(resource, in_process, out_process)
    def __repr__(self):
        return f'<ScenarioFlow from process {self.in_process} to process {self.out_process}>'

# Measure item by item


@dataclass
class RunMeasure:
    process: Process

@dataclass
class RunMeasurement:
    n_runs: float

class FlowMeasure(BaseFlow):
    pass

@dataclass
class FlowMeasurement:
    resource: float
    units: str



class Scenario:
    def __init__(
        self,
        policy: Policy,
        elements: List[Union[ScenarioRun, ScenarioFlow]]
    ):
        def convert_element_to_runs(element: Union[ScenarioRun, ScenarioFlow]) -> List[ScenarioRun]:
            runs = []
            if isinstance(element, ScenarioRun):
                runs.append(element) 
            else:
                if element.in_process is not None:
                    demands = element.in_process.demands
                    min_runs = -element.value/demands[element.resource]
                    runs.append(
                        ScenarioRun(element.in_process, min_runs)
                    )
                if element.out_process is not None:
                    demands = element.out_process.demands
                    min_runs = element.value/demands[element.resource]
                    runs.append(
                        ScenarioRun(element.out_process, min_runs)
                    )
            return runs
        
        def runs_to_run_scenario(runs: List[ScenarioRun], processes: List[Process]) -> np.ArrayLike:
            run_scenario = np.zeros((len(processes),))
            process_index = {process: i for i, process in enumerate(processes)}
            for run in runs:
                process = run.process
                run_scenario[process_index[process]] = max([run_scenario[process_index[process]], run.n_runs])
            return run_scenario
        
        runs = []
        for element in elements:
            runs += convert_element_to_runs(element)

        self.processes = policy.processes
        self.run_scenario = runs_to_run_scenario(runs, self.processes)
        self.resources = policy.resources
        self.process_demands = policy.process_demands
        self.run_matrix = policy.run_matrix
        self.run_vector = calculate_run_vector(self.run_matrix, self.run_scenario)
        #print(self.run_vector)
        self.actual_resource = calculate_actual_resource(self.process_demands, self.run_vector)
        #print(self.actual_resource)
        self.actual_resource_flow = calculate_actual_resource_flow(self.actual_resource, demand_policy= policy.policy)
        #print(self.actual_resource_flow)


    def measure(self, measurements: List[Union[RunMeasure, FlowMeasure]]):
        for measurement in measurements:
            pass
        
        raise NotImplementedError('Nope')



# class MeasureElement:
#     def __init__(
#         self,
#         resource: Resource,
#         in_process: Process,
#         out_process: Process
#     ):
#         self.resource = resource
#         self.in_process = in_process
#         self.out_process = out_process
#     
#     def __repr__(self):
#         return f'<MeasureElement for \n InProcess: {self.in_process}, \n OutProcess: {self.out_process}, \n Resource: {self.resource}>'
# 
# class MeasureElementMaker:
#     def __init__(
#         self,
#         resources,
#         processes
#     ) -> None:
#         self.processes = processes
#         self.process_index =  {process.process_name: process for process in processes}
#         self.resources = resources
#         self.resource_index = {resource.resource_name: resource for resource in resources}
#     def __call__(
#         self, 
#         resource: str,
#         in_process: str,
#         out_process: str
#     ) -> MeasureElement:
#         if resource in self.resource_index:
#             new_resource = self.resource_index[resource]
#         else:
#             raise ValueError(f'Process {resource} not found')
#         if in_process in self.process_index:
#             new_in_process = self.process_index[in_process]
#         else:
#             raise ValueError(f'Process {in_process} not found')
#         if out_process in self.process_index:
#             new_out_process = self.process_index[out_process]
#         else:
#             raise ValueError(f'Process {out_process} not found')
#         
#         return MeasureElement(
#                 new_resource,
#                 new_in_process,
#                 new_out_process
#             )
#         
#         
# class Measure:
#     def __init__(
#         self,
#         scenario: Scenario,
#     ):
#         self.scenario = scenario
#     def __call__(
#         self,
#         measure_elements: List[MeasureElement]
#     ):
#         def generate_measure(processes, resources, measure_elements):
#             measure = np.zeros((len(processes), len(processes), len(resources)),dtype=bool)
#             for measure_element in measure_elements:
#                 in_process = processes.index(measure_element.in_process)
#                 out_process = processes.index(measure_element.out_process)
#                 resource = resources.index(measure_element.resource)
#                 measure[in_process][out_process][resource] = True
#             return measure
#         
#         #flow_slice = get_flow_slice(scenario.actual_resource_flow, 3)
#         measure = generate_measure(self.scenario.processes, self.scenario.resources, measure_elements)
#         resource_usage = alt_measure_resource_usage(self.scenario.actual_resource_flow, measure)
#         new_resource_usage = {}
#         for i, usage in enumerate(resource_usage):
#             resource = self.scenario.resources[i]
#             new_resource_usage[resource.resource_name] = usage
#         return new_resource_usage
# 
