import numpy as np
import pytest

from mat_dp_core import (
    EqConstraint,
    GeConstraint,
    LeConstraint,
    Measure,
    Processes,
    Resources,
)
from mat_dp_core.maths_core.exceptions import (
    InconsistentOrderOfMagnitude,
    Overconstrained,
    UnboundedSolution,
)


@pytest.mark.asyncio
class TestRun:
    async def test_farming_all(
        self, farming_example_measure_bounds, bounds_bool
    ):
        results = farming_example_measure_bounds.run(bounds=bounds_bool)

        assert len(results) == 3
        if bounds_bool:
            assert len(results[0]) == 4
            assert round(results[0][1], 3) == 20
            assert round(results[0][2], 3) == 10
            assert round(results[0][3], 3) == 50
        else:
            assert len(results[0]) == 2
            assert round(results[0][1], 3) == 20
        assert (
            results[0][0]
            == farming_example_measure_bounds._processes["arable_farm"]
        )

    async def test_farming_specify_process(
        self, farming_example_measure_bounds, bounds_bool
    ):
        results = farming_example_measure_bounds.run(
            process=farming_example_measure_bounds._processes["arable_farm"],
            bounds=bounds_bool,
        )
        if bounds_bool:
            assert round(results[0], 3) == 20
            assert round(results[1], 3) == 10
            assert round(results[2], 3) == 50
        else:
            assert round(results, 3) == 20


@pytest.mark.asyncio
class TestResource:
    async def test_farming_all(
        self, farming_example_measure_bounds, bounds_bool
    ):
        results = farming_example_measure_bounds.resource(bounds=bounds_bool)
        assert len(results) == 6
        if bounds_bool:
            assert len(results[0]) == 5
            assert round(results[0][2], 3) == 20
            assert round(results[0][3], 3) == 10
            assert round(results[0][4], 3) == 50
        else:
            assert len(results[0]) == 3
            assert round(results[0][2], 3) == 20
        assert (
            results[0][0]
            == farming_example_measure_bounds._processes["arable_farm"]
        )
        assert (
            results[0][1] == farming_example_measure_bounds._resources["hay"]
        )

    async def test_farming_specify_process(
        self, farming_example_measure_bounds, bounds_bool
    ):
        results = farming_example_measure_bounds.resource(
            process=farming_example_measure_bounds._processes["arable_farm"],
            bounds=bounds_bool,
        )
        assert len(results) == 2
        if bounds_bool:
            assert len(results[0]) == 4
            assert round(results[0][1], 3) == 20
            assert round(results[0][2], 3) == 10
            assert round(results[0][3], 3) == 50
        else:
            assert len(results[0]) == 2
            assert round(results[0][1], 3) == 20
        assert (
            results[0][0] == farming_example_measure_bounds._resources["hay"]
        )

    async def test_farming_specify_resource(
        self, farming_example_measure_bounds, bounds_bool
    ):
        results = farming_example_measure_bounds.resource(
            resource=farming_example_measure_bounds._resources["hay"],
            bounds=bounds_bool,
        )
        assert len(results) == 3
        if bounds_bool:
            assert len(results[0]) == 4
            assert round(results[0][1], 3) == 20
            assert round(results[0][2], 3) == 10
            assert round(results[0][3], 3) == 50
        else:
            assert len(results[0]) == 2
            assert round(results[0][1], 3) == 20
        assert (
            results[0][0]
            == farming_example_measure_bounds._processes["arable_farm"]
        )

    async def test_farming_specify_resource_and_process(
        self, farming_example_measure_bounds, bounds_bool
    ):
        results = farming_example_measure_bounds.resource(
            resource=farming_example_measure_bounds._resources["hay"],
            process=farming_example_measure_bounds._processes["arable_farm"],
            bounds=bounds_bool,
        )
        if bounds_bool:
            assert round(results[0], 3) == 20
            assert round(results[1], 3) == 10
            assert round(results[2], 3) == 50
        else:
            assert round(results, 3) == 20


@pytest.mark.asyncio
class TestFlow:
    async def test_farming_all(
        self, farming_example_measure_bounds_flow: Measure, bounds_bool
    ):
        results = farming_example_measure_bounds_flow.flow(bounds=bounds_bool)
        assert len(results) == 12
        if bounds_bool:
            assert len(results[7]) == 6
            assert round(results[7][3], 3) == 10
            assert round(results[7][4], 3) == 3.333
            assert round(results[7][5], 3) == 30
        else:
            assert len(results[7]) == 4
            assert round(results[7][3], 3) == 10
        assert (
            results[7][0]
            == farming_example_measure_bounds_flow._processes["dairy_farm"]
        )
        assert (
            results[7][1]
            == farming_example_measure_bounds_flow._processes["mcdonalds"]
        )
        assert (
            results[7][2]
            == farming_example_measure_bounds_flow._resources["cow"]
        )

    async def test_farming_specify_resource(
        self, farming_example_measure_bounds_flow: Measure, bounds_bool
    ):
        results = farming_example_measure_bounds_flow.flow(
            resource=farming_example_measure_bounds_flow._resources["cow"],
            bounds=bounds_bool,
        )
        assert len(results) == 6
        if bounds_bool:
            assert len(results[3]) == 5
            assert round(results[3][2], 3) == 10
            assert round(results[3][3], 3) == 3.333
            assert round(results[3][4], 3) == 30
        else:
            assert len(results[3]) == 3
            assert round(results[3][2], 3) == 10
        assert (
            results[3][0]
            == farming_example_measure_bounds_flow._processes["dairy_farm"]
        )
        assert (
            results[3][1]
            == farming_example_measure_bounds_flow._processes["mcdonalds"]
        )

    async def test_farming_specify_process_pair(
        self, farming_example_measure_bounds_flow: Measure, bounds_bool
    ):
        results = farming_example_measure_bounds_flow.flow(
            process_from=farming_example_measure_bounds_flow._processes[
                "dairy_farm"
            ],
            process_to=farming_example_measure_bounds_flow._processes[
                "mcdonalds"
            ],
            bounds=bounds_bool,
        )
        assert len(results) == 2
        if bounds_bool:
            assert len(results[0]) == 4
            assert round(results[0][1], 3) == 0
            assert round(results[0][2], 3) == 0
            assert round(results[0][3], 3) == 0
            assert len(results[1]) == 4
            assert round(results[1][1], 3) == 10
            assert round(results[1][2], 3) == 3.333
            assert round(results[1][3], 3) == 30
        else:
            assert len(results[0]) == 2
            assert round(results[0][1], 3) == 0
            assert len(results[1]) == 2
            assert round(results[1][1], 3) == 10
        assert (
            results[0][0]
            == farming_example_measure_bounds_flow._resources["hay"]
        )
        assert (
            results[1][0]
            == farming_example_measure_bounds_flow._resources["cow"]
        )

    async def test_farming_specify_process_pair_and_resource(
        self, farming_example_measure_bounds_flow: Measure, bounds_bool
    ):
        results = farming_example_measure_bounds_flow.flow(
            process_from=farming_example_measure_bounds_flow._processes[
                "dairy_farm"
            ],
            process_to=farming_example_measure_bounds_flow._processes[
                "mcdonalds"
            ],
            resource=farming_example_measure_bounds_flow._resources["cow"],
            bounds=bounds_bool,
        )
        if bounds_bool:
            assert isinstance(results, tuple)
            assert len(results) == 3
            assert round(results[0], 3) == 10
            assert round(results[1], 3) == 3.333
            assert round(results[2], 3) == 30
        else:
            assert isinstance(results, float)
            assert round(results, 3) == 10

    async def test_farming_flow_to_process(
        self, farming_example_measure_bounds_flow: Measure, bounds_bool
    ):
        results = farming_example_measure_bounds_flow.flow(
            process_to=farming_example_measure_bounds_flow._processes[
                "mcdonalds"
            ],
            bounds=bounds_bool,
        )
        assert len(results) == 2
        if bounds_bool:
            assert len(results[1]) == 4
            assert round(results[1][1], 3) == 10
            assert round(results[1][2], 3) == 3.333
            assert round(results[1][3], 3) == 30
        else:
            assert len(results[1]) == 2
            assert round(results[1][1], 3) == 10
        assert (
            results[1][0]
            == farming_example_measure_bounds_flow._resources["cow"]
        )

    async def test_farming_flow_to_process_and_resource(
        self, farming_example_measure_bounds_flow: Measure, bounds_bool
    ):
        results = farming_example_measure_bounds_flow.flow(
            process_to=farming_example_measure_bounds_flow._processes[
                "mcdonalds"
            ],
            resource=farming_example_measure_bounds_flow._resources["cow"],
            bounds=bounds_bool,
        )
        if bounds_bool:
            assert isinstance(results, tuple)
            assert len(results) == 3
            assert round(results[0], 3) == 10
            assert round(results[1], 3) == 3.333
            assert round(results[2], 3) == 30
        else:
            assert isinstance(results, float)
            assert round(results, 3) == 10

    async def test_farming_flow_from_process(
        self, farming_example_measure_bounds_flow: Measure, bounds_bool
    ):
        results = farming_example_measure_bounds_flow.flow(
            process_from=farming_example_measure_bounds_flow._processes[
                "dairy_farm"
            ],
            bounds=bounds_bool,
        )
        assert len(results) == 2
        if bounds_bool:
            assert len(results[1]) == 4
            assert round(results[1][1], 3) == 10
            assert round(results[1][2], 3) == 3.333
            assert round(results[1][3], 3) == 30
        else:
            assert len(results[1]) == 2
            assert round(results[1][1], 3) == 10
        assert (
            results[1][0]
            == farming_example_measure_bounds_flow._resources["cow"]
        )

    async def test_farming_flow_from_process_and_resource(
        self, farming_example_measure_bounds_flow: Measure, bounds_bool
    ):
        results = farming_example_measure_bounds_flow.flow(
            process_from=farming_example_measure_bounds_flow._processes[
                "dairy_farm"
            ],
            resource=farming_example_measure_bounds_flow._resources["cow"],
            bounds=bounds_bool,
        )
        if bounds_bool:
            assert isinstance(results, tuple)
            assert len(results) == 3
            assert round(results[0], 3) == 10
            assert round(results[1], 3) == 3.333
            assert round(results[2], 3) == 30
        else:
            assert isinstance(results, float)
            assert round(results, 3) == 10


@pytest.mark.asyncio
class TestCumulativeResource:
    async def test_farming_all(
        self, farming_example_measure_bounds, bounds_bool
    ):
        results = farming_example_measure_bounds.cumulative_resource(
            bounds=bounds_bool
        )
        assert len(results) == 6
        if bounds_bool:
            assert len(results[0]) == 5
            assert round(results[0][2], 3) == 20
            assert round(results[0][3], 3) == 10
            assert round(results[0][4], 3) == 50
        else:
            assert len(results[0]) == 3
            assert round(results[0][2], 3) == 20

        assert (
            results[0][0]
            == farming_example_measure_bounds._processes["arable_farm"]
        )
        assert (
            results[0][1] == farming_example_measure_bounds._resources["hay"]
        )

    async def test_farming_specify_process(
        self, farming_example_measure_bounds, bounds_bool
    ):
        results = farming_example_measure_bounds.cumulative_resource(
            process=farming_example_measure_bounds._processes["arable_farm"],
            bounds=bounds_bool,
        )
        assert len(results) == 2
        if bounds_bool:
            assert len(results[0]) == 4
            assert round(results[0][1], 3) == 20
            assert round(results[0][2], 3) == 10
            assert round(results[0][3], 3) == 50
        else:
            assert len(results[0]) == 2
            assert round(results[0][1], 3) == 20

        assert (
            results[0][0] == farming_example_measure_bounds._resources["hay"]
        )

    async def test_farming_specify_resource(
        self, farming_example_measure_bounds, bounds_bool
    ):
        results = farming_example_measure_bounds.cumulative_resource(
            resource=farming_example_measure_bounds._resources["hay"],
            bounds=bounds_bool,
        )
        assert len(results) == 3
        if bounds_bool:
            assert len(results[0]) == 4
            assert round(results[0][1], 3) == 20
            assert round(results[0][2], 3) == 10
            assert round(results[0][3], 3) == 50
        else:
            assert len(results[0]) == 2
            assert round(results[0][1], 3) == 20
        assert (
            results[0][0]
            == farming_example_measure_bounds._processes["arable_farm"]
        )

    async def test_farming_specify_resource_and_process(
        self, farming_example_measure_bounds, bounds_bool
    ):
        results = farming_example_measure_bounds.cumulative_resource(
            resource=farming_example_measure_bounds._resources["hay"],
            process=farming_example_measure_bounds._processes["arable_farm"],
            bounds=bounds_bool,
        )

        if bounds_bool:
            assert round(results[0], 3) == 20
            assert round(results[1], 3) == 10
            assert round(results[2], 3) == 50
        else:
            assert round(results, 3) == 20
