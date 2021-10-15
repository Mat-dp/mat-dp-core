import csv
from typing import List, Optional, Sequence

from mat_dp_core import (
    FlowMeasure,
    Policy,
    Process,
    Resource,
    Scenario,
    ScenarioFlow,
)
from mat_dp_core.utils import generate_process_index, generate_resource_index


def load_processes(data: Sequence[Sequence[float]]):
    """
    Loads a Resources, Processes system from a 2D list
    """
    raise NotImplementedError


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
    step = (upper_bound - lower_bound) / bins
    scenarios = []
    for i in range(bins):
        current = lower_bound + i * step
        current_rounded = round(float(current) / step) * step
        scenario_name = str(current_rounded) + resource.unit + ":" + country

        scenario = Scenario(
            scenario_name,
            policy,
            [ScenarioFlow(resource, current_rounded, in_process, out_process)],
        )

        scenarios.append(scenario)
    return scenarios


# e.g. dfE_tech_by_country
def scenarios_to_csv_by_process(
    scenarios: List[Scenario],
    resource: str = "energy",
    policy_heading: str = "Year",
    scenario_heading_sections: List[str] = ["Scenario", "Country"],
    scenario_section_delimiter: str = ":",
    csv_file_loc: str = "../../E_matbytech_bycountry.csv",
):
    if not all(
        [
            i.policy.processes == scenarios[0].policy.processes
            for i in scenarios
        ]
    ):
        raise ValueError("Process sequence mismatch between scenarios")
    proc_headings = [process.name for process in scenarios[0].policy.processes]
    all_headings = (
        ["", policy_heading] + scenario_heading_sections + proc_headings
    )
    with open(csv_file_loc, mode="w") as new_file:
        file_writer = csv.writer(
            new_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_MINIMAL
        )
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
                        relevant_resource, in_process=process
                    )
                    out_flow = scenario.measure_flow(flow_measure).resource
                except ValueError:
                    out_flow = 0

                out_flows.append(out_flow)
            scenario_sections = scenario.name.split(scenario_section_delimiter)
            values = [i, scenario.policy.name] + scenario_sections + out_flows
            file_writer.writerow(values)


# e.g.E_matbytech_bycountry.csv
def scenarios_to_csv_by_tech_by_resource(
    scenarios: List[Scenario],
    resource: str = "energy",
    process_heading: str = "tech",
    policy_heading: str = "Year",
    scenario_heading_sections: List[str] = ["Scenario", "Country"],
    scenario_section_delimiter: str = ":",
    csv_file_loc: str = "../../E_matbytech_bycountry.csv",
    measure_in: bool = True,
):
    pass
