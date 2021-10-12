from mat_dp_core import Resource, Process, ResourceName, ProcessName
from typing import Union, List, Dict


def generate_resource_index(
    list_to_convert: List[Resource]
) -> Dict[ResourceName, Resource]:
    return {i.name: i for i in list_to_convert}

def generate_process_index(
    list_to_convert: List[Process]
) -> Dict[ProcessName, Process]:
    return {i.name: i for i in list_to_convert}


def generate_index(
    list_to_convert: Union[List[Resource],List[Process]]
) -> Union[Dict[ResourceName, Resource],Dict[ProcessName, Process]]:
    all_resources = all([isinstance(i, Resource) for i in list_to_convert])
    all_processes = all([isinstance(i, Process) for i in list_to_convert])
    if all_resources == all_processes:
        raise ValueError('Invalid list')

    output = {}
    for i in list_to_convert:
        name = i.name
        output[name] = i
    return output
