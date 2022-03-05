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
            np.round(solution.run_vector, 3), np.array([20, 10, 10])
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
            np.round(solution.run_vector, 3), np.array([20, 10, 10])
        )

    @pytest.mark.filterwarnings("ignore: A_eq")
    async def test_simple_dairy_overconstrained_positive(
        self, farming_example
    ):
        resources, processes = farming_example
        constraints = [
            EqConstraint("burger_consumption", processes["dairy_farm"], 10),
            EqConstraint("burger_consumption", processes["arable_farm"], 199),
        ]
        objective = processes["arable_farm"]
        try:
            Measure(resources, processes, constraints, objective=objective)
            assert False
        except Overconstrained as e:
            string_list = str(e).split("\n")
            assert len(string_list) == 4
            assert string_list[0] == "Overconstrained problem:"
            assert string_list[1] == "resources:"
            assert (
                string_list[2]
                == "hay => 179.0: increase runs of dairy_farm or decrease runs of arable_farm"
            )
            assert (
                string_list[3]
                == "cow => 10.0: increase runs of mcdonalds or decrease runs of dairy_farm"
            )

    @pytest.mark.filterwarnings("ignore: A_eq")
    async def test_simple_dairy_overconstrained_negative(
        self, farming_example
    ):
        resources, processes = farming_example
        constraints = [
            EqConstraint("burger_consumption", processes["dairy_farm"], 10),
            EqConstraint("burger_consumption", processes["mcdonalds"], 199),
        ]
        objective = processes["arable_farm"]
        try:
            Measure(resources, processes, constraints, objective=objective)
            assert False
        except Overconstrained as e:
            string_list = str(e).split("\n")
            assert len(string_list) == 4
            assert string_list[0] == "Overconstrained problem:"
            assert string_list[1] == "resources:"
            assert (
                string_list[2]
                == "hay => -20.0: increase runs of arable_farm or decrease runs of dairy_farm"
            )
            assert (
                string_list[3]
                == "cow => -189.0: increase runs of dairy_farm or decrease runs of mcdonalds"
            )

    async def test_simple_dairy_overconstrained_eq_constraints(
        self, null_example
    ):
        resources, processes = null_example
        constraints = [
            EqConstraint("burger_consumption", processes["dairy_farm"], 10),
            EqConstraint("burger_consumption", processes["dairy_farm"], 199),
        ]
        objective = processes["arable_farm"]
        try:
            Measure(resources, processes, constraints, objective=objective)
            assert False
        except Overconstrained as e:
            string_list = str(e).split("\n")
            assert len(string_list) == 4
            assert string_list[0] == "Overconstrained problem:"
            assert string_list[1] == "eq_constraints:"
            assert string_list[2] == "dairy_farm == 10 => 10.0"
            assert string_list[3] == "dairy_farm == 199 => 199.0"

    async def test_simple_dairy_overconstrained_le_constraints(
        self, null_example
    ):
        resources, processes = null_example
        constraints = [
            GeConstraint("burger_consumption", processes["dairy_farm"], 10),
            LeConstraint("burger_consumption", processes["dairy_farm"], 5),
        ]
        objective = processes["arable_farm"]
        try:
            Measure(resources, processes, constraints, objective=objective)
            assert False
        except Overconstrained as e:
            string_list = str(e).split("\n")
            assert len(string_list) == 3
            assert string_list[0] == "Overconstrained problem:"
            assert string_list[1] == "le_constraints:"
            assert string_list[2] == "- dairy_farm <= -10 => -10.0"

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
            assert messages[0] == "Solution unbounded - final solution was:"
            for i in range(3):
                assert messages[i + 1][-20:] == "(probably unbounded)"

    async def test_simple_dairy_partially_unbounded(
        self, parallel_farming_example
    ):
        resources, processes = parallel_farming_example
        constraints = [
            EqConstraint("burger_consumption", processes["mcdonalds"], 10)
        ]
        objective = -processes["arable_farm"] - processes["sheep_farm"]
        try:
            Measure(resources, processes, constraints, objective=objective)
            assert False
        except UnboundedSolution as e:
            messages = str(e).split("\n")
        assert len(messages) == 7
        assert messages[0] == "Solution unbounded - final solution was:"
        assert messages[1] == "arable_farm: 11.170546563753362"
        assert messages[2] == "dairy_farm: 5.817627319466408"
        assert messages[3] == "mcdonalds: 10.0"
        assert (
            messages[4]
            == "field_growth: 29691916331.74252 (probably unbounded)"
        )
        assert (
            messages[5]
            == "sheep_farm: 29691916331.742508 (probably unbounded)"
        )
        assert (
            messages[6]
            == "dog_food_factory: 29691916331.742496 (probably unbounded)"
        )

    async def test_simple_dairy_large_objective(self, farming_example):
        resources, processes = farming_example
        constraint = EqConstraint(
            "burger_consumption", processes["mcdonalds"], 10
        )
        objective = (
            processes["arable_farm"] * (10 ** 50)
            + processes["dairy_farm"] * (10 ** 52)
            + processes["mcdonalds"] * (10 ** 49)
        )

        Measure(resources, processes, [constraint], objective=objective)

    async def test_simple_dairy_inconsistent_order_of_mag_coeff(
        self, farming_example
    ):
        resources, processes = farming_example
        constraint = EqConstraint(
            "burger_consumption", processes["mcdonalds"], 10
        )
        objective = (
            processes["arable_farm"] * (10 ** 20)
            + processes["dairy_farm"] * (10 ** 1)
            + processes["mcdonalds"] * (10 ** 2)
        )
        try:
            Measure(resources, processes, [constraint], objective=objective)
            assert False
        except InconsistentOrderOfMagnitude as e:
            messages = [i for i in str(e).split("\n") if i != ""]
            assert len(messages) == 5
            assert messages[0] == "All resources and constraints must be of a "
            assert (
                messages[1]
                == "consistent order of magnitude. If you wish to allow this "
            )
            assert (
                messages[2]
                == "behaviour use 'allow_inconsistent_order_of_mag'."
            )
            assert messages[3] == "Objective function inconsistencies"
            assert (
                messages[4]
                == "Objective func: 100000000000000000000*arable_farm + 10*dairy_farm + 100*mcdonalds: Order of mag range: 19.0"
            )

    async def test_simple_dairy_inconsistent_order_of_mag_resource(self):
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
            Measure(resources, processes, [constraint], objective=objective)
            assert False
        except InconsistentOrderOfMagnitude as e:
            messages = [i for i in str(e).split("\n") if i != ""]
            assert len(messages) == 7
            assert messages[0] == "All resources and constraints must be of a "
            assert (
                messages[1]
                == "consistent order of magnitude. If you wish to allow this "
            )
            assert (
                messages[2]
                == "behaviour use 'allow_inconsistent_order_of_mag'."
            )
            assert messages[3] == "Resource inconsistencies"
            assert messages[4] == "hay: Order of mag range: 7.301029995663981"
            assert messages[5] == "    arable_farm: 1.0"
            assert messages[6] == "    dairy_farm: -20000000.0"

    async def test_simple_dairy_inconsistent_order_of_mag_eq_con(self):
        resources = Resources()
        hay = resources.create("hay")
        cow = resources.create("cow")

        processes = Processes()
        processes.create("arable_farm", (hay, +1))
        processes.create("dairy_farm", (cow, +1), (hay, -20))
        processes.create("mcdonalds", (cow, -1))

        constraint = EqConstraint(
            "burger_consumption",
            processes["mcdonalds"]
            + 1000000000000000 * processes["arable_farm"],
            10,
        )
        objective = (
            processes["arable_farm"]
            + processes["dairy_farm"]
            + processes["mcdonalds"]
        )

        try:
            Measure(resources, processes, [constraint], objective=objective)
            assert False
        except InconsistentOrderOfMagnitude as e:
            messages = [i for i in str(e).split("\n") if i != ""]
            assert len(messages) == 7
            assert messages[0] == "All resources and constraints must be of a "
            assert (
                messages[1]
                == "consistent order of magnitude. If you wish to allow this "
            )
            assert (
                messages[2]
                == "behaviour use 'allow_inconsistent_order_of_mag'."
            )
            assert messages[3] == "Eq Constraint inconsistencies"
            assert (
                messages[4]
                == "mcdonalds + 1000000000000000*arable_farm == 10: Order of mag range - 15.0"
            )
            assert messages[5] == "    arable_farm: 1.0"
            assert messages[6] == "    mcdonalds: 0.0"

    async def test_simple_dairy_inconsistent_order_of_mag_le_con(self):
        resources = Resources()
        hay = resources.create("hay")
        cow = resources.create("cow")

        processes = Processes()
        processes.create("arable_farm", (hay, +1))
        processes.create("dairy_farm", (cow, +1), (hay, -20))
        processes.create("mcdonalds", (cow, -1))

        constraint = LeConstraint(
            "burger_consumption",
            processes["mcdonalds"]
            + 1000000000000000 * processes["arable_farm"],
            10,
        )
        objective = (
            processes["arable_farm"]
            + processes["dairy_farm"]
            + processes["mcdonalds"]
        )

        try:
            Measure(resources, processes, [constraint], objective=objective)
            assert False
        except InconsistentOrderOfMagnitude as e:
            messages = [i for i in str(e).split("\n") if i != ""]
            assert len(messages) == 7
            assert messages[0] == "All resources and constraints must be of a "
            assert (
                messages[1]
                == "consistent order of magnitude. If you wish to allow this "
            )
            assert (
                messages[2]
                == "behaviour use 'allow_inconsistent_order_of_mag'."
            )
            assert messages[3] == "Le Constraint inconsistencies"
            assert (
                messages[4]
                == "mcdonalds + 1000000000000000*arable_farm <= 10: Order of mag range - 15.0"
            )
            assert messages[5] == "    arable_farm: 1000000000000000.0"
            assert messages[6] == "    mcdonalds: 1.0"


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
