from typing import Optional

from mat_dp_core.maths_core import EqConstraint, Process, Resource


class RunEqConstraint(EqConstraint):
    def __init__(
        self,
        process: Process,
        runs: float,
        name: Optional[str] = None,
    ):
        if name is None:
            name = f"{process.name}_fixed_at_{runs}_runs"
        super().__init__(name, process, runs)


# TODO ratios to support multiple in one go
# get_constraints method that outputs list of constraints


class RunRatioConstraint(EqConstraint):
    def __init__(
        self,
        process1: Process,
        process2: Process,
        p2_over_p1: float,
        name: Optional[str] = None,
    ):
        if name is None:
            name = f"fixed_ratio{process1.name}_to_{process2.name}_at_1:{p2_over_p1}"
        super().__init__(name, process1 - process2 * p2_over_p1, 0)


class ResourceConstraint(EqConstraint):
    def __init__(
        self,
        resource: Resource,
        process: Process,
        resource_bound: float,  # Positive float >0
        name: Optional[str] = None,
    ):
        # get from resource_bound to run bound
        # need to look at process
        try:
            demand = process.array[resource.index]
        except IndexError:
            raise ValueError(
                f"Invalid demand: {resource} demanded from {process} but process does not produce or consume this"
            )

        if demand < 0:
            positive = False
        elif demand > 0:
            positive = True
        else:
            raise ValueError(
                f"Invalid demand: {resource} demanded from {process} but process does not produce or consume this"
            )

        no_runs = resource_bound / abs(demand)

        if positive:
            phrase = "consumption"
        else:
            phrase = "production"

        if name is None:
            name = f"resource_{phrase}_{resource.name}_fixed_at_{resource_bound}{resource.unit}_for_process_{process.name}"
        super().__init__(name, process, no_runs)
