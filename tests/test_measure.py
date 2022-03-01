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
    NumericalDifficulties,
    Overconstrained,
    UnboundedSolution,
)


@pytest.mark.asyncio
class TestSolvable:
    async def test_no_processes_or_resources(self):
        resources = Resources()
        processes = Processes()
        objective = None
        try:
            Measure(resources, processes, [], objective=objective)
            assert False
        except ValueError as e:
            assert str(e) == "No resources or processes created"

    async def test_no_processes(self):
        resources = Resources()
        processes = Processes()
        resources.create("hay")
        objective = None
        try:
            Measure(resources, processes, [], objective=objective)
            assert False
        except ValueError as e:
            assert str(e) == "No processes created"

    async def test_no_resources(self):
        resources = Resources()
        processes = Processes()
        hay = resources.create("hay")
        resources = Resources()
        processes.create("arable_farm", (hay, +1))
        objective = None
        try:
            Measure(resources, processes, [], objective=objective)
            assert False
        except ValueError as e:
            assert str(e) == "No resources created"

    async def test_simple_dairy(self, farming_example):
        resources, processes = farming_example
        constraint = EqConstraint(
            "burger_consumption", processes["mcdonalds"], 10
        )
        objective = (
            processes["arable_farm"]
            + processes["dairy_farm"]
            + processes["mcdonalds"]
        )
        solution = Measure(
            resources, processes, [constraint], objective=objective
        )
        assert np.array_equal(
            np.round(solution._run_vector, 3), np.array([20, 10, 10])
        )

    async def test_simple_dairy_new_objective(self, farming_example):
        resources, processes = farming_example
        constraint = EqConstraint(
            "burger_consumption", processes["mcdonalds"], 10
        )
        objective = processes["arable_farm"]
        solution = Measure(
            resources, processes, [constraint], objective=objective
        )
        assert np.array_equal(
            np.round(solution._run_vector, 3), np.array([20, 10, 10])
        )

    @pytest.mark.filterwarnings("ignore: A_eq")
    async def test_simple_dairy_overconstrained(self, farming_example):
        resources, processes = farming_example
        constraints = [
            EqConstraint("burger_consumption", processes["dairy_farm"], 10),
            EqConstraint("burger_consumption", processes["arable_farm"], 199),
        ]
        objective = processes["arable_farm"]
        try:
            Measure(resources, processes, constraints, objective=objective)
            assert False
        except Overconstrained:
            pass

    async def test_simple_dairy_unbounded(self, farming_example):
        resources, processes = farming_example
        constraints = []
        objective = -processes["arable_farm"]
        try:
            Measure(resources, processes, constraints, objective=objective)
            assert False
        except UnboundedSolution as e:
            messages = str(e).split("\n")
            assert len(messages) == 4
            for i in range(3):
                assert messages[i + 1][-20:] == "(probably unbounded)"

    async def test_simple_dairy_numerical_difficulties(self, farming_example):
        resources, processes = farming_example
        constraint = EqConstraint(
            "burger_consumption", processes["mcdonalds"], 10
        )
        objective = (
            processes["arable_farm"]
            * 10000000000000000000000000000000000000000
            + processes["dairy_farm"]
            + processes["mcdonalds"]
        )
        try:
            Measure(resources, processes, [constraint], objective=objective)
        except NumericalDifficulties:
            pass

    async def test_simple_dairy_numerical_difficulties_v2(self):
        resources = Resources()
        hay = resources.create("hay")
        cow = resources.create("cow")

        processes = Processes()
        processes.create("arable_farm", (hay, +1))
        processes.create("dairy_farm", (cow, +1), (hay, -20 * 10 ** 6))
        processes.create("mcdonalds", (cow, -1))

        constraint = EqConstraint(
            "burger_consumption", processes["mcdonalds"], 10
        )
        objective = (
            processes["arable_farm"]
            + processes["dairy_farm"]
            + processes["mcdonalds"]
        )

        try:
            res = Measure(
                resources, processes, [constraint], objective=objective
            )
            print(res._run_vector)
            assert False
        except InconsistentOrderOfMagnitude:
            pass


@pytest.mark.asyncio
class TestRun:
    async def test_farming_all(self, farming_example_measure):
        results = farming_example_measure.run()
        assert len(results) == 3
        assert len(results[0]) == 2
        assert (
            results[0][0] == farming_example_measure._processes["arable_farm"]
        )
        assert round(results[0][1], 3) == 20

    async def test_farming_specify_process(self, farming_example_measure):
        results = farming_example_measure.run(
            farming_example_measure._processes["arable_farm"]
        )
        assert round(results, 3) == 20


@pytest.mark.asyncio
class TestResource:
    async def test_farming_all(self, farming_example_measure):
        results = farming_example_measure.resource()
        assert len(results) == 6
        assert len(results[0]) == 3
        assert (
            results[0][0] == farming_example_measure._processes["arable_farm"]
        )
        assert results[0][1] == farming_example_measure._resources["hay"]
        assert round(results[0][2], 3) == 20

    async def test_farming_specify_process(self, farming_example_measure):
        results = farming_example_measure.resource(
            farming_example_measure._processes["arable_farm"]
        )
        assert len(results) == 2
        assert len(results[0]) == 2
        assert results[0][0] == farming_example_measure._resources["hay"]
        assert round(results[0][1], 3) == 20

    async def test_farming_specify_resource(self, farming_example_measure):
        results = farming_example_measure.resource(
            farming_example_measure._resources["hay"]
        )
        assert len(results) == 3
        assert len(results[0]) == 2
        assert (
            results[0][0] == farming_example_measure._processes["arable_farm"]
        )
        assert round(results[0][1], 3) == 20

    async def test_farming_specify_resource_and_process(
        self, farming_example_measure
    ):
        results = farming_example_measure.resource(
            farming_example_measure._resources["hay"],
            farming_example_measure._processes["arable_farm"],
        )
        assert round(results, 3) == 20


@pytest.mark.asyncio
class TestFlow:
    async def test_farming_all(self, farming_example_measure: Measure):
        results = farming_example_measure.flow()
        assert len(results) == 12
        assert len(results[0]) == 4
        assert (
            results[0][0] == farming_example_measure._processes["arable_farm"]
        )
        assert (
            results[0][1] == farming_example_measure._processes["dairy_farm"]
        )
        assert results[0][2] == farming_example_measure._resources["hay"]
        assert round(results[0][3], 3) == 20

    async def test_farming_specify_resource(
        self, farming_example_measure: Measure
    ):
        results = farming_example_measure.flow(
            farming_example_measure._resources["hay"]
        )
        assert len(results) == 6
        assert len(results[0]) == 3
        assert (
            results[0][0] == farming_example_measure._processes["arable_farm"]
        )
        assert (
            results[0][1] == farming_example_measure._processes["dairy_farm"]
        )
        assert round(results[0][2], 3) == 20

    async def test_farming_specify_process_pair(
        self, farming_example_measure: Measure
    ):
        results = farming_example_measure.flow(
            farming_example_measure._processes["arable_farm"],
            farming_example_measure._processes["dairy_farm"],
        )
        assert len(results) == 2
        assert len(results[0]) == 2
        assert results[0][0] == farming_example_measure._resources["hay"]
        assert round(results[0][1], 3) == 20
        assert len(results[1]) == 2
        assert results[1][0] == farming_example_measure._resources["cow"]
        assert round(results[1][1], 3) == 0

    async def test_farming_specify_process_pair_and_resource(
        self, farming_example_measure: Measure
    ):
        results = farming_example_measure.flow(
            farming_example_measure._processes["arable_farm"],
            farming_example_measure._processes["dairy_farm"],
            farming_example_measure._resources["hay"],
        )
        assert round(results, 3) == 20


@pytest.mark.asyncio
class TestFlowTo:
    async def test_farming_flow_to_process(
        self, farming_example_measure: Measure
    ):
        results = farming_example_measure.flow_to(
            farming_example_measure._processes["dairy_farm"]
        )
        assert len(results) == 2
        assert len(results[0]) == 2
        assert results[0][0] == farming_example_measure._resources["hay"]
        assert round(results[0][1], 3) == 20

    async def test_farming_flow_to_process_and_resource(
        self, farming_example_measure: Measure
    ):
        results = farming_example_measure.flow_to(
            farming_example_measure._processes["dairy_farm"],
            farming_example_measure._resources["hay"],
        )
        assert round(results, 3) == 20


@pytest.mark.asyncio
class TestFlowFrom:
    async def test_farming_flow_from_process(
        self, farming_example_measure: Measure
    ):
        results = farming_example_measure.flow_from(
            farming_example_measure._processes["arable_farm"]
        )
        assert len(results) == 2
        assert len(results[0]) == 2
        assert results[0][0] == farming_example_measure._resources["hay"]
        assert round(results[0][1], 3) == 20

    async def test_farming_flow_to_process_and_resource(
        self, farming_example_measure: Measure
    ):
        results = farming_example_measure.flow_from(
            farming_example_measure._processes["arable_farm"],
            farming_example_measure._resources["hay"],
        )
        assert round(results, 3) == 20


@pytest.mark.asyncio
class TestCumulativeResource:
    async def test_farming_all(self, farming_example_measure):
        results = farming_example_measure.cumulative_resource()
        assert len(results) == 6
        assert len(results[0]) == 3
        assert (
            results[0][0] == farming_example_measure._processes["arable_farm"]
        )
        assert results[0][1] == farming_example_measure._resources["hay"]
        assert round(results[0][2], 3) == 20

    async def test_farming_specify_process(self, farming_example_measure):
        results = farming_example_measure.cumulative_resource(
            farming_example_measure._processes["arable_farm"]
        )
        assert len(results) == 2
        assert len(results[0]) == 2
        assert results[0][0] == farming_example_measure._resources["hay"]
        assert round(results[0][1], 3) == 20

    async def test_farming_specify_resource(self, farming_example_measure):
        results = farming_example_measure.cumulative_resource(
            farming_example_measure._resources["hay"]
        )
        assert len(results) == 3
        assert len(results[0]) == 2
        assert (
            results[0][0] == farming_example_measure._processes["arable_farm"]
        )
        assert round(results[0][1], 3) == 20

    async def test_farming_specify_resource_and_process(
        self, farming_example_measure
    ):
        results = farming_example_measure.cumulative_resource(
            farming_example_measure._resources["hay"],
            farming_example_measure._processes["arable_farm"],
        )
        assert round(results, 3) == 20
