from typing import Dict, List

class Resource:
    def __init__(self, resource_name, unit = 'ea'):
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
        


class PolicyElementMaker:
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
        pass

    def __repr__(self):
        return f'<PolicyElementMaker, contains processes: {self.processes}>'



class Policy:
    def __init__(
        self,
        resources: List[Resource],
        processes: List[Process],
        policy_elements: List[PolicyElement]
    ):
        pass
