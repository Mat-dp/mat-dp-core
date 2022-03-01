from typing import Tuple

import pytest

from mat_dp_core import EqConstraint, Processes, ResourceConstraint, Resources
from mat_dp_core.maths_core.exceptions import IterationLimitReached
from mat_dp_core.maths_core.solve import solve


@pytest.mark.asyncio
class TestSolveErrors:
    async def test_iter_limit_reached(
        self, farming_example: Tuple[Resources, Processes]
    ):
        resources, processes = farming_example
        constraints = [
            EqConstraint("burger_consumption", processes["dairy_farm"], 10)
        ]
        try:
            solve(resources, processes, constraints, maxiter=1)
        except IterationLimitReached as e:
            assert str(e) == "Iteration limit reached with 1 iterations"
