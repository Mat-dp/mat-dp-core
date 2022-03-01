from typing import Tuple

import pytest

from mat_dp_core import Processes, ResourceConstraint, Resources
from mat_dp_core.maths_core.processes import Processes


@pytest.mark.asyncio
class TestConstraintErrors:
    async def test_resource_constraint_invalid_demand(
        self, pizza_example: Tuple[Resources, Processes]
    ):
        resources, processes = pizza_example
        try:
            ResourceConstraint(
                resources["cardboard"], processes["energy_grid"], 16
            )
        except ValueError as e:
            assert (
                str(e)
                == "Invalid demand: cardboard demanded from energy_grid but process does not produce or consume this"
            )

    async def test_resource_constraint_invalid_demand_pre_res_definition(
        self, pizza_example: Tuple[Resources, Processes]
    ):
        resources, processes = pizza_example
        try:
            ResourceConstraint(
                resources["energy"], processes["cardboard_producer"], 16
            )
        except ValueError as e:
            assert (
                str(e)
                == "Invalid demand: energy demanded from cardboard_producer but process does not produce or consume this"
            )
