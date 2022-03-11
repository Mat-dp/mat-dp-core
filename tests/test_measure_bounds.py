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
    async def test_simple_dairy(self, farming_example_bounds):
        resources, processes = farming_example_bounds
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
        assert np.array_equal(
            np.round(solution.run_vector_lb, 3), np.array([10, 10, 10])
        )
        assert np.array_equal(
            np.round(solution.run_vector_ub, 3), np.array([50, 10, 10])
        )

    async def test_simple_dairy_new_objective(self, farming_example_bounds):
        resources, processes = farming_example_bounds
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
        assert np.array_equal(
            np.round(solution.run_vector_lb, 3), np.array([10, 10, 10])
        )
        assert np.array_equal(
            np.round(solution.run_vector_ub, 3), np.array([50, 10, 10])
        )

    @pytest.mark.filterwarnings("ignore: A_eq")
    async def test_simple_dairy_overconstrained_positive(
        self, farming_example_bounds
    ):
        resources, processes = farming_example_bounds
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
        self, farming_example_bounds
    ):
        resources, processes = farming_example_bounds
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

    async def test_simple_dairy_unbounded(self, farming_example_bounds):
        resources, processes = farming_example_bounds
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

    async def test_simple_dairy_large_objective(self, farming_example_bounds):
        resources, processes = farming_example_bounds
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
        self, farming_example_bounds
    ):
        resources, processes = farming_example_bounds
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
        processes.create("arable_farm", (hay, (+1, 0.5, 1.5)))
        processes.create(
            "dairy_farm",
            (cow, +1),
            (hay, (-20 * 10 ** -6, -25 * 10 ** 6, -15 * 10 ** 6)),
        )
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
            assert len(messages) == 10
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
            assert messages[4] == "hay: Order of mag range: 7.698970004336019"
            assert messages[5] == "    arable_farm: 0.5"
            assert messages[6] == "    dairy_farm: -25000000.0"
            assert messages[7] == "hay: Order of mag range: 7.0"
            assert messages[8] == "    arable_farm: -1.5"
            assert messages[9] == "    dairy_farm: 15000000"

    async def test_simple_dairy_inconsistent_order_of_mag_eq_con(self):
        resources = Resources()
        hay = resources.create("hay")
        cow = resources.create("cow")

        processes = Processes()
        processes.create("arable_farm", (hay, (+1, 0.5, 1.5)))
        processes.create(
            "dairy_farm",
            (cow, +1),
            (hay, (-20 * 10 ** -6, -25 * 10 ** 6, -15 * 10 ** 6)),
        )
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
        processes.create("arable_farm", (hay, (+1, 0.5, 1.5)))
        processes.create(
            "dairy_farm",
            (cow, +1),
            (hay, (-20 * 10 ** -6, -25 * 10 ** 6, -15 * 10 ** 6)),
        )
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
