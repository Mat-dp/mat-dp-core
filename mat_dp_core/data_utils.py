from mat_dp_core import Scenario, FlowMeasure, Policy, Resource, Process, ScenarioFlow
from mat_dp_core.utils import generate_resource_index, generate_process_index
from typing import List, Optional

import csv

def generate_scenarios(
    policy: Policy,
    country: str,
    resource: Resource,
    lower_bound: float,
    upper_bound: float,
    bins: int,
    in_process: Optional[Process] = None,
    out_process: Optional[Process] = None,
) -> List[Scenario]:
    step = (upper_bound - lower_bound)/bins
    scenarios = []
    for i in range(bins):
        current = lower_bound + i*step
        current_rounded = round(float(current) / step) * step
        scenario_name = str(current_rounded) + resource.unit + ':' + country

        scenario = Scenario(
            scenario_name,
            policy,
            [ScenarioFlow(resource, current_rounded, in_process, out_process)]
        )
        
        scenarios.append(scenario)
    return scenarios



def scenarios_to_csv(
    scenarios: List[Scenario],
    resource: str = 'energy',
    policy_heading: str = 'Year',
    scenario_heading_sections: List[str] = ['Scenario', 'Country'],
    scenario_section_delimiter: str = ':',
    csv_file_loc: str = '../../E_matbytech_bycountry.csv'
):
    if not all([i.policy.processes == scenarios[0].policy.processes for i in scenarios]):
        raise ValueError('Process sequence mismatch between scenarios')
    proc_headings = [process.name for process in scenarios[0].policy.processes]
    all_headings = ['',policy_heading] + scenario_heading_sections + proc_headings
    with open(csv_file_loc, mode='w') as new_file:
        file_writer = csv.writer(new_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        file_writer.writerow(all_headings)
        for i, scenario in enumerate(scenarios):
            resources = scenario.policy.resources
            processes = scenario.policy.processes
            resource_index = generate_resource_index(resources)
            relevant_resource = resource_index[resource]
            out_flows = []
            for process in processes:
                try:
                    flow_measure = FlowMeasure(
                        relevant_resource,
                        in_process = process
                    )
                    out_flow = scenario.measure_flow(flow_measure).resource
                except ValueError:
                    out_flow = 0
                
                out_flows.append(out_flow)
            scenario_sections = scenario.name.split(scenario_section_delimiter)
            values = [i, scenario.policy.name] + scenario_sections + out_flows
            file_writer.writerow(values)

    