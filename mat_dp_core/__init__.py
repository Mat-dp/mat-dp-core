from dataclasses import dataclass
from typing import Dict, Generic, List, Optional, Tuple, TypeVar, Union

from mat_dp_core.maths_core import (
    calculate_actual_resource,
    calculate_run_matrix,
    calculate_run_vector,
    calculate_actual_resource_flow,
)
from numpy.typing import ArrayLike
import numpy as np
from dataclasses import dataclass

ResourceName = str
ProcessName = str
ScenarioName = str
PolicyName = str
Unit = str

class Resource:
    name: ResourceName
    unit: Unit
    def __init__(self, name: ResourceName, unit: Unit = 'ea'):
        self.name = name
        self.unit = unit

    def __repr__(self):
        return f'<Resource: {self.name}>'


class Process:
    name: ProcessName
    demands: Dict[Resource, float]
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
        incident_processes: Dict[Process, float]
    ):
        for incident_process in incident_processes.keys():
            if resource not in incident_process.demands.keys():
                raise ValueError(f'Resource {resource} not found in process demands for incident_process {incident_process} on process {process}')
        if resource not in process.demands.keys():
            raise ValueError(f'Resource {resource} not found in process demands for process {process}')
        if process in process.demands.keys():
            raise ValueError(f'Self demanding process {process}')
        total_incidence = sum(incident_processes.values())
        if total_incidence != 1:
            raise ValueError(f'Total incidence for process {process} not 1 but {total_incidence}')
        self.resource = resource
        self.process = process
        self.incident_processes = incident_processes
    
    def __repr__(self):
        return f'<PolicyElement for Process: {self.process}, Resource: {self.resource}>'

class Policy:
    name: PolicyName
    processes: List[Process]
    resources: List[Resource]
    process_demands: ArrayLike
    policy: ArrayLike
    run_matrix: ArrayLike
    elements: List[PolicyElement]
    def __init__(self, name: PolicyName, elements: List[PolicyElement]):
        
        def get_processes_from_policy_elements(policy_elements: List[PolicyElement]) -> List[Process]:
            processes = []
            for policy_element in policy_elements:
                #print(policy_element.incident_processes)
                if policy_element.process not in processes:
                    processes.append(policy_element.process)
                for process in policy_element.incident_processes.keys():
                    if process not in processes:
                        processes.append(process)

            return processes
        
        def get_resources_from_processes(processes: List[Process]) -> List[Resource]:
            resources = []
            for process in processes:
                for resource in process.demands.keys():
                    if resource not in resources:
                        resources.append(resource)
            return resources
        
        def generate_process_demands(resources: List[Resource], processes: List[Process]) -> ArrayLike:
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
        ) -> ArrayLike:
            policy = np.zeros(
                (len(processes), len(processes), len(resources))
            )
            resource_index = {resource: i for i, resource in enumerate(resources)}
            process_index = {process: i for i, process in enumerate(processes)}

            for policy_element in policy_elements:
                k = resource_index[policy_element.resource]
                j = process_index[policy_element.process]
                for incident_process, value in policy_element.incident_processes.items():
                    i = process_index[incident_process]
                    policy[i][j][k] = value
            return policy
        self.name = name
        self.processes = get_processes_from_policy_elements(elements)
        self.resources = get_resources_from_processes(self.processes)
        self.process_demands = generate_process_demands(self.resources, self.processes)
        self.policy = generate_policy(self.resources, self.processes, elements)
        self.run_matrix = calculate_run_matrix(self.process_demands, self.policy)
        self.elements = elements

    def __repr__(self):
        return f'<Policy {self.name}>'

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
        name: ScenarioName,
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
        
        def runs_to_run_scenario(runs: List[ScenarioRun], processes: List[Process]) -> ArrayLike:
            run_scenario = np.zeros((len(processes),))
            process_index = {process: i for i, process in enumerate(processes)}
            for run in runs:
                process = run.process
                run_scenario[process_index[process]] = max([run_scenario[process_index[process]], run.n_runs])
            return run_scenario
        
        runs = []
        for element in elements:
            runs += convert_element_to_runs(element)
        self.name = name
        self.policy = policy
        self.run_scenario = runs_to_run_scenario(runs, self.policy.processes)
        self.run_vector = calculate_run_vector(self.policy.run_matrix, self.run_scenario)
        self.actual_resource = calculate_actual_resource(self.policy.process_demands, self.run_vector)
        self.actual_resource_flow = calculate_actual_resource_flow(self.actual_resource, demand_policy= policy.policy)

    def measure_runs(self, measurement: RunMeasure) -> RunMeasurement:
        process_index = self.policy.processes.index(measurement.process)
        runs = self.run_vector[process_index]
        return RunMeasurement(n_runs=runs)

    def measure_flow(self, measurement: FlowMeasure) -> FlowMeasurement:
        resource_index = self.policy.resources.index(measurement.resource)
        if measurement.in_process is not None and measurement.out_process is not None:
            in_process_index = self.policy.processes.index(measurement.in_process)
            out_process_index = self.policy.processes.index(measurement.out_process)
            value = self.actual_resource_flow[in_process_index][out_process_index][resource_index]
        elif measurement.out_process is not None:
            out_process_index = self.policy.processes.index(measurement.out_process)
            value = sum(self.actual_resource_flow[:,out_process_index, resource_index])
        elif measurement.in_process is not None:
            in_process_index = self.policy.processes.index(measurement.in_process)
            value = sum(self.actual_resource_flow[in_process_index,:, resource_index])
        else:
            raise TypeError('Measurement not of type FlowMeasure')
        units = measurement.resource.unit
        return FlowMeasurement(value, units)
    def __repr__(self):
        return f'<Scenario {self.name}>'
