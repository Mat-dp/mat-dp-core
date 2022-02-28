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
from mat_dp_core.maths_core import Overconstrained


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
        assert np.all(
            np.round(solution._run_vector, 3) == np.array([20, 10, 10])
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
        assert np.all(
            np.round(solution._run_vector, 3) == np.array([20, 10, 10])
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

    async def test_simple_dairy_underconstrained(self, farming_example):
        resources, processes = farming_example
        constraints = []
        objective = processes["arable_farm"]
        solution = Measure(
            resources, processes, constraints, objective=objective
        )
