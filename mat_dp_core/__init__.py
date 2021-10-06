from typing import Dict, Generic, List, TypeVar

from mat_dp_core.maths_core import (
    calculate_actual_resource,
    calculate_run_matrix,
    calculate_run_scenario,
    calculate_run_vector,
    calculate_actual_resource_flow,
    get_flow_slice,
    measure_resource_usage,
    alt_measure_resource_usage
)
import numpy as np

class Resource:
    def __init__(self, resource_name: str, unit: str = 'ea'):
        self.resource_name = resource_name
        self.unit = unit
    def __repr__(self):
        return f'<Resource: {self.resource_name}>'

class Process:
    def __init__(
        self, 
        process_name: str, 
        process_demands: Dict[Resource, float]
    ):
        self.process_name = process_name
        self.process_demands = process_demands

    def __repr__(self):
        return f'<Process: {self.process_name}>'


class ProcessMaker:
    def __init__(
        self,
        resources: List[Resource]
    ):
        self.resources = resources
        self.resource_index = {resource.resource_name: resource for resource in resources}

    def __call__(
        self,
        process_name: str,
        **process_demands: float
    ):
        process_demands_by_rec_obj = {}
        for resource_name, value in process_demands.items():
            if resource_name in self.resource_index:
                resource = self.resource_index[resource_name]
            else:
                raise ValueError(f'Resource {resource_name} not found')
            process_demands_by_rec_obj[resource] = value
        
        return Process(
            process_name = process_name,
            process_demands = process_demands_by_rec_obj
        )
    def __repr__(self):
        return f'<ProcessMaker, contains resources: {self.resources}>'

class PolicyElement:
    def __init__(
        self,
        relevant_process: Process,
        relevant_resource: Resource,
        incident_processes: Dict[Process, float]
    ):
        total_incidence = 0
        for process, value in incident_processes.items():
            total_incidence += value
        if total_incidence !=1:
            raise ValueError(f'Total incidence not 1 but {total_incidence}')
        self.relevant_process = relevant_process
        self.relevant_resource = relevant_resource
        self.incident_processes = incident_processes
    
    def __repr__(self):
        return f'<PolicyElement for Process: {self.relevant_process}, Resource: {self.relevant_resource}>'
        


class PolicyElementMaker: # process demands???
    def __init__(
        self,
        resources: List[Resource],
        processes: List[Process]
    ):
        self.processes = processes
        self.process_index =  {process.process_name: process for process in processes}
        self.resources = resources
        self.resource_index = {resource.resource_name: resource for resource in resources}
    
    def __call__(
        self,
        relevant_process: str,
        relevant_resource: str,
        **incident_process_proportions: float
    ):
        if relevant_process in self.process_index:
            new_relevant_process = self.process_index[relevant_process]
        else:
            raise ValueError(f'Process {relevant_process} not found')
        if relevant_resource in self.resource_index:
            new_relevant_resource = self.resource_index[relevant_resource]
        else:
            raise ValueError(f'Resource {relevant_resource} not found')

        incident_process_props_by_proc_obj = {}
        for process_name, value in incident_process_proportions.items():
            if process_name in self.process_index:
                process = self.process_index[process_name]
            else:
                raise ValueError(f'Process {process_name} not found')
            incident_process_props_by_proc_obj[process] = value
        return PolicyElement(
            relevant_process = new_relevant_process,
            relevant_resource = new_relevant_resource, 
            incident_processes = incident_process_props_by_proc_obj
        )
    
    def __repr__(self):
        return f'<PolicyElementMaker, contains processes: {self.processes}>'

class Policy:
    def __init__(
        self,
        resources: List[Resource],
        processes: List[Process],
        policy_elements: List[PolicyElement]
    ):
        def generate_process_demands(resources: List[Resource], processes: List[Process]):
            process_demands = np.zeros((len(processes), len(resources)))
            resource_index = {resource: i for i, resource in enumerate(resources)}
            for i, process in enumerate(processes):
                for resource, value in process.process_demands.items():
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
                rel_proc = policy_element.relevant_process
                rel_res = policy_element.relevant_resource

                k = resource_index[rel_res]
                j = process_index[rel_proc]
                for incident_process, value in policy_element.incident_processes.items():
                    i = process_index[incident_process]
                    policy[i][j][k] = value
            return policy
        self.resources = resources
        self.processes = processes
        self.process_demands = generate_process_demands(resources, processes)
        self.policy = generate_policy(resources, processes, policy_elements)
        self.run_matrix = calculate_run_matrix(self.process_demands, self.policy)
        self.policy_elements = policy_elements

    def __repr__(self):
        return f'<Policy formed of : {self.policy_elements}>'

class ScenarioElement:
    def __init__(
        self,
        relevant_process: Process,
        resource_lower_bounds:  Dict[Resource, float],
    ):
        self.relevant_process = relevant_process
        self.resource_lower_bounds = resource_lower_bounds
    
    def __repr__(self):
        return f'<ScenarioElement for Process: {self.relevant_process}, ResourceLowerBounds: {self.resource_lower_bounds}>'

class ScenarioElementMaker:
    def __init__(
        self,
        resources: List[Resource],
        processes: List[Process]
    ):
        self.processes = processes
        self.process_index =  {process.process_name: process for process in processes}
        self.resources = resources
        self.resource_index = {resource.resource_name: resource for resource in resources}
    
    def __call__(
        self,
        relevant_process: str,
        **resource_lower_bounds: float
    ):

        if relevant_process in self.process_index:
            new_relevant_process = self.process_index[relevant_process]
        else:
            raise ValueError(f'Process {relevant_process} not found')

        resource_lower_bounds_by_proc_obj = {}
        for resource_name, value in resource_lower_bounds.items():
            if resource_name in self.resource_index:
                resource = self.resource_index[resource_name]
            else:
                raise ValueError(f'Resource {resource_name} not found')
            resource_lower_bounds_by_proc_obj[resource] = value
        return ScenarioElement(
            relevant_process = new_relevant_process, 
            resource_lower_bounds = resource_lower_bounds_by_proc_obj
        )

    def __repr__(self):
        return f'<ScenarioElementMaker, contains processes: {self.processes}>'



class Scenario:
    def __init__(
        self,
        policy,
        scenerio_elements
    ):
        def generate_scenario(
            resources:List[Resource],
            processes: List[Process],
            scenerio_elements: List[ScenarioElement]
        ):
            scenario = np.zeros(
                (len(processes), len(resources))
            )
            resource_index = {resource: i for i, resource in enumerate(resources)}
            process_index = {process: i for i, process in enumerate(processes)}
            for scenario_element in scenerio_elements:
                rel_proc = scenario_element.relevant_process
                i = process_index[rel_proc]

                for relevant_resource, value in scenario_element.resource_lower_bounds.items():
                    j = resource_index[relevant_resource]
                    scenario[i][j] = value
            return scenario
        self.processes = policy.processes
        self.resources = policy.resources
        self.process_demands = policy.process_demands
        self.run_matrix = policy.run_matrix
        #print(self.run_matrix)
        self.scenario = generate_scenario(self.resources, self.processes, scenerio_elements)
        #print(self.scenario)
        self.run_scenario = calculate_run_scenario(self.process_demands, self.scenario)
        #print(self.run_scenario)
        self.run_vector = calculate_run_vector(self.run_matrix, self.run_scenario)
        #print(self.run_vector)
        self.actual_resource = calculate_actual_resource(self.process_demands, self.run_vector)
        #print(self.actual_resource)
        self.actual_resource_flow = calculate_actual_resource_flow(self.actual_resource, demand_policy= policy.policy)
        #print(self.actual_resource_flow)

class MeasureElement:
    def __init__(
        self,
        resource: Resource,
        in_process: Process,
        out_process: Process
    ):
        self.resource = resource
        self.in_process = in_process
        self.out_process = out_process
    
    def __repr__(self):
        return f'<MeasureElement for \n InProcess: {self.in_process}, \n OutProcess: {self.out_process}, \n Resource: {self.resource}>'

class MeasureElementMaker:
    def __init__(
        self,
        resources,
        processes
    ) -> None:
        self.processes = processes
        self.process_index =  {process.process_name: process for process in processes}
        self.resources = resources
        self.resource_index = {resource.resource_name: resource for resource in resources}
    def __call__(
        self, 
        resource: str,
        in_process: str,
        out_process: str
    ) -> MeasureElement:
        if resource in self.resource_index:
            new_resource = self.resource_index[resource]
        else:
            raise ValueError(f'Process {resource} not found')
        if in_process in self.process_index:
            new_in_process = self.process_index[in_process]
        else:
            raise ValueError(f'Process {in_process} not found')
        if out_process in self.process_index:
            new_out_process = self.process_index[out_process]
        else:
            raise ValueError(f'Process {out_process} not found')
        
        return MeasureElement(
                new_resource,
                new_in_process,
                new_out_process
            )
        
        
class Measure:
    def __init__(
        self,
        scenario: Scenario,
    ):
        self.scenario = scenario
    def __call__(
        self,
        measure_elements: List[MeasureElement]
    ):
        def generate_measure(processes, resources, measure_elements):
            measure = np.zeros((len(processes), len(processes), len(resources)),dtype=bool)
            for measure_element in measure_elements:
                in_process = processes.index(measure_element.in_process)
                out_process = processes.index(measure_element.out_process)
                resource = resources.index(measure_element.resource)
                measure[in_process][out_process][resource] = True
            return measure
        
        #flow_slice = get_flow_slice(scenario.actual_resource_flow, 3)
        measure = generate_measure(self.scenario.processes, self.scenario.resources, measure_elements)
        resource_usage = alt_measure_resource_usage(self.scenario.actual_resource_flow, measure)
        new_resource_usage = {}
        for i, usage in enumerate(resource_usage):
            resource = self.scenario.resources[i]
            new_resource_usage[resource.resource_name] = usage
        return new_resource_usage

