import numpy as np
import pytest

from mat_dp_core import Measure


@pytest.mark.asyncio
class TestNull:
    async def test_run_vector(self, null_example_measure: Measure):
        run_vector = null_example_measure.run_vector
        assert np.array_equal(
            np.round(run_vector, decimals=3),
            np.array(
                [0, 0, 0],
                dtype=float,
            ),
        )

    async def test_resource_matrix(self, null_example_measure: Measure):
        resource_matrix = null_example_measure.resource_matrix
        assert np.array_equal(
            np.round(resource_matrix, decimals=3),
            np.array([[0.0, 0.0, 0.0], [0.0, 0.0, 0.0]], dtype=float),
        )

    async def test_flow_matrix(self, null_example_measure: Measure):
        flow_matrix = null_example_measure.flow_matrix
        assert np.array_equal(
            np.round(flow_matrix, decimals=3),
            np.array(
                [
                    [
                        [0, 0.0, 0.0],
                        [0.0, 0.0, 0.0],
                        [0.0, 0.0, 0.0],
                    ],
                    [
                        [0.0, 0.0, 0.0],
                        [0.0, 0.0, 0.0],
                        [0.0, 0.0, 0.0],
                    ],
                ],
                dtype=float,
            ),
        )

    async def test_cumulative_resource_matrix(
        self, null_example_measure: Measure
    ):
        cumulative_resource_matrix = (
            null_example_measure.cumulative_resource_matrix
        )
        assert np.array_equal(
            np.round(cumulative_resource_matrix, decimals=3),
            np.array([[0.0, 0.0, 0.0], [0.0, 0.0, 0.0]], dtype=float),
        )


@pytest.mark.asyncio
class TestFarming:
    async def test_run_vector(self, farming_example_measure: Measure):
        run_vector = farming_example_measure.run_vector
        assert np.array_equal(
            np.round(run_vector, decimals=3),
            np.array(
                [20.0, 10.0, 10.0],
                dtype=float,
            ),
        )

    async def test_resource_matrix(self, farming_example_measure: Measure):
        resource_matrix = farming_example_measure.resource_matrix
        assert np.array_equal(
            np.round(resource_matrix, decimals=3),
            np.array([[20, -20.0, 0.0], [0.0, 10.0, -10.0]], dtype=float),
        )

    async def test_flow_matrix(self, farming_example_measure: Measure):
        flow_matrix = farming_example_measure.flow_matrix
        assert np.array_equal(
            np.round(flow_matrix, decimals=3),
            np.array(
                [
                    [
                        [0, 20.0, 0.0],
                        [-20.0, 0.0, 0.0],
                        [0.0, 0.0, 0.0],
                    ],
                    [
                        [0, 0.0, 0.0],
                        [0.0, 0.0, 10.0],
                        [0.0, -10.0, 0.0],
                    ],
                ],
                dtype=float,
            ),
        )

    async def test_cumulative_resource_matrix(
        self, farming_example_measure: Measure
    ):
        cumulative_resource_matrix = (
            farming_example_measure.cumulative_resource_matrix
        )
        assert np.array_equal(
            np.round(cumulative_resource_matrix, decimals=3),
            np.array([[20, 20.0, 20.0], [10.0, 10.0, 10.0]], dtype=float),
        )


@pytest.mark.asyncio
class TestFarmingBounds:
    async def test_run_vector(self, farming_example_measure_bounds: Measure):
        run_vector = farming_example_measure_bounds.run_vector
        assert np.array_equal(
            np.round(run_vector, decimals=3),
            np.array(
                [20.0, 10.0, 10.0],
                dtype=float,
            ),
        )
        run_vector_lb = farming_example_measure_bounds.run_vector_lb
        assert np.array_equal(
            np.round(run_vector_lb, decimals=3),
            np.array(
                [10.0, 10.0, 10.0],
                dtype=float,
            ),
        )
        run_vector_ub = farming_example_measure_bounds.run_vector_ub
        assert np.array_equal(
            np.round(run_vector_ub, decimals=3),
            np.array(
                [50.0, 10.0, 10.0],
                dtype=float,
            ),
        )

    async def test_resource_matrix(
        self, farming_example_measure_bounds: Measure
    ):
        resource_matrix = farming_example_measure_bounds.resource_matrix
        assert np.array_equal(
            np.round(resource_matrix, decimals=3),
            np.array([[20, -20.0, 0.0], [0.0, 10.0, -10.0]], dtype=float),
        )
        resource_matrix_lb = farming_example_measure_bounds.resource_matrix_lb
        assert np.array_equal(
            np.round(resource_matrix_lb, decimals=3),
            np.array([[10, -20.0, 0.0], [0.0, 10.0, -10.0]], dtype=float),
        )
        resource_matrix_ub = farming_example_measure_bounds.resource_matrix_ub
        assert np.array_equal(
            np.round(resource_matrix_ub, decimals=3),
            np.array([[50, -20.0, 0.0], [0.0, 10.0, -10.0]], dtype=float),
        )

    async def test_flow_matrix(
        self, farming_example_measure_bounds_flow: Measure
    ):
        flow_matrix = farming_example_measure_bounds_flow.flow_matrix
        assert np.array_equal(
            np.round(flow_matrix, decimals=3),
            np.array(
                [
                    [
                        [0, 20.0, 0.0],
                        [-20.0, 0.0, 0.0],
                        [0.0, 0.0, 0.0],
                    ],
                    [
                        [0, 0.0, 0.0],
                        [0.0, 0.0, 10.0],
                        [0.0, -10.0, 0.0],
                    ],
                ],
                dtype=float,
            ),
        )
        flow_matrix_lb = farming_example_measure_bounds_flow.flow_matrix_lb
        assert np.array_equal(
            np.round(flow_matrix_lb, decimals=3),
            np.array(
                [
                    [
                        [0, 20.0, 0.0],
                        [-20.0, 0.0, 0.0],
                        [0.0, 0.0, 0.0],
                    ],
                    [
                        [0, 0.0, 0.0],
                        [0.0, 0.0, 3.333],
                        [0.0, -30.0, 0.0],
                    ],
                ],
                dtype=float,
            ),
        )
        flow_matrix_ub = farming_example_measure_bounds_flow.flow_matrix_ub
        assert np.array_equal(
            np.round(flow_matrix_ub, decimals=3),
            np.array(
                [
                    [
                        [0, 20.0, 0.0],
                        [-20.0, 0.0, 0.0],
                        [0.0, 0.0, 0.0],
                    ],
                    [
                        [0, 0.0, 0.0],
                        [0.0, 0.0, 30.0],
                        [0.0, -3.333, 0.0],
                    ],
                ],
                dtype=float,
            ),
        )

    async def test_cumulative_resource_matrix(
        self, farming_example_measure_bounds: Measure
    ):
        cumulative_resource_matrix = (
            farming_example_measure_bounds.cumulative_resource_matrix
        )
        assert np.array_equal(
            np.round(cumulative_resource_matrix, decimals=3),
            np.array([[20, 20.0, 20.0], [10.0, 10.0, 10.0]], dtype=float),
        )

        cumulative_resource_matrix_lb = (
            farming_example_measure_bounds.cumulative_resource_matrix_lb
        )

        assert np.array_equal(
            np.round(cumulative_resource_matrix_lb, decimals=3),
            np.array([[10, 20.0, 20.0], [5.0, 10.0, 10.0]], dtype=float),
        )

        cumulative_resource_matrix_ub = (
            farming_example_measure_bounds.cumulative_resource_matrix_ub
        )
        assert np.array_equal(
            np.round(cumulative_resource_matrix_ub, decimals=3),
            np.array([[50, 20.0, 20.0], [25.0, 10.0, 10.0]], dtype=float),
        )


@pytest.mark.asyncio
class TestFarmingBoundsNotBounded:
    async def test_run_vector(self, farming_example_measure: Measure):
        run_vector = farming_example_measure.run_vector
        assert np.array_equal(
            np.round(run_vector, decimals=3),
            np.array(
                [20.0, 10.0, 10.0],
                dtype=float,
            ),
        )
        run_vector_lb = farming_example_measure.run_vector_lb
        assert np.array_equal(
            np.round(run_vector_lb, decimals=3),
            np.array(
                [20.0, 10.0, 10.0],
                dtype=float,
            ),
        )
        run_vector_ub = farming_example_measure.run_vector_ub
        assert np.array_equal(
            np.round(run_vector_ub, decimals=3),
            np.array(
                [20.0, 10.0, 10.0],
                dtype=float,
            ),
        )

    async def test_resource_matrix(self, farming_example_measure: Measure):
        resource_matrix = farming_example_measure.resource_matrix
        assert np.array_equal(
            np.round(resource_matrix, decimals=3),
            np.array([[20, -20.0, 0.0], [0.0, 10.0, -10.0]], dtype=float),
        )
        resource_matrix_lb = farming_example_measure.resource_matrix_lb
        assert np.array_equal(
            np.round(resource_matrix_lb, decimals=3),
            np.array([[20, -20.0, 0.0], [0.0, 10.0, -10.0]], dtype=float),
        )
        resource_matrix_ub = farming_example_measure.resource_matrix_ub
        assert np.array_equal(
            np.round(resource_matrix_ub, decimals=3),
            np.array([[20, -20.0, 0.0], [0.0, 10.0, -10.0]], dtype=float),
        )

    async def test_flow_matrix(self, farming_example_measure: Measure):
        flow_matrix = farming_example_measure.flow_matrix
        assert np.array_equal(
            np.round(flow_matrix, decimals=3),
            np.array(
                [
                    [
                        [0, 20.0, 0.0],
                        [-20.0, 0.0, 0.0],
                        [0.0, 0.0, 0.0],
                    ],
                    [
                        [0, 0.0, 0.0],
                        [0.0, 0.0, 10.0],
                        [0.0, -10.0, 0.0],
                    ],
                ],
                dtype=float,
            ),
        )
        flow_matrix_lb = farming_example_measure.flow_matrix_lb
        assert np.array_equal(
            np.round(flow_matrix_lb, decimals=3),
            np.array(
                [
                    [
                        [0, 20.0, 0.0],
                        [-20.0, 0.0, 0.0],
                        [0.0, 0.0, 0.0],
                    ],
                    [
                        [0, 0.0, 0.0],
                        [0.0, 0.0, 10.0],
                        [0.0, -10.0, 0.0],
                    ],
                ],
                dtype=float,
            ),
        )
        flow_matrix_ub = farming_example_measure.flow_matrix_ub
        assert np.array_equal(
            np.round(flow_matrix_ub, decimals=3),
            np.array(
                [
                    [
                        [0, 20.0, 0.0],
                        [-20.0, 0.0, 0.0],
                        [0.0, 0.0, 0.0],
                    ],
                    [
                        [0, 0.0, 0.0],
                        [0.0, 0.0, 10.0],
                        [0.0, -10.0, 0.0],
                    ],
                ],
                dtype=float,
            ),
        )

    async def test_cumulative_resource_matrix(
        self, farming_example_measure: Measure
    ):
        cumulative_resource_matrix = (
            farming_example_measure.cumulative_resource_matrix
        )
        assert np.array_equal(
            np.round(cumulative_resource_matrix, decimals=3),
            np.array([[20, 20.0, 20.0], [10.0, 10.0, 10.0]], dtype=float),
        )

        cumulative_resource_matrix_lb = (
            farming_example_measure.cumulative_resource_matrix_lb
        )

        assert np.array_equal(
            np.round(cumulative_resource_matrix_lb, decimals=3),
            np.array([[20, 20.0, 20.0], [10.0, 10.0, 10.0]], dtype=float),
        )

        cumulative_resource_matrix_ub = (
            farming_example_measure.cumulative_resource_matrix_ub
        )
        assert np.array_equal(
            np.round(cumulative_resource_matrix_ub, decimals=3),
            np.array([[20, 20.0, 20.0], [10.0, 10.0, 10.0]], dtype=float),
        )


@pytest.mark.asyncio
class TestPizza:
    async def test_run_vector(self, pizza_example_measure: Measure):
        run_vector = pizza_example_measure.run_vector
        assert np.array_equal(
            np.round(run_vector, decimals=3),
            np.array(
                [6.0, 7.0, 2.0, 2.0, 4.0, 8.0],
                dtype=float,
            ),
        )

    async def test_resource_matrix(self, pizza_example_measure: Measure):
        resource_matrix = pizza_example_measure.resource_matrix

        assert np.array_equal(
            np.round(resource_matrix, decimals=3),
            np.array(
                [
                    [6.0, 0.0, -4.0, -2.0, 0.0, 0.0],
                    [0.0, 7.0, -1.0, -6.0, 0.0, 0.0],
                    [0.0, 0.0, 2.0, 2.0, -4.0, 0.0],
                    [0.0, 0.0, 0.0, 0.0, 16.0, -16.0],
                ],
                dtype=float,
            ),
        )

    async def test_flow_matrix(self, pizza_example_measure: Measure):
        flow_matrix = pizza_example_measure.flow_matrix
        assert np.array_equal(
            np.round(flow_matrix, decimals=3),
            np.array(
                [
                    [
                        [0.0, 0.0, 4.0, 2.0, 0.0, 0.0],
                        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                        [-4.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                        [-2.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                    ],
                    [
                        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                        [0.0, 0.0, 1.0, 6.0, 0.0, 0.0],
                        [0.0, -1.0, 0.0, 0.0, 0.0, 0.0],
                        [0.0, -6.0, 0.0, 0.0, 0.0, 0.0],
                        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                    ],
                    [
                        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                        [0.0, 0.0, 0.0, 0.0, 2.0, 0.0],
                        [0.0, 0.0, 0.0, 0.0, 2.0, 0.0],
                        [0.0, 0.0, -2.0, -2.0, 0.0, 0.0],
                        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                    ],
                    [
                        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                        [0.0, 0.0, 0.0, 0.0, 0.0, 16.0],
                        [0.0, 0.0, 0.0, 0.0, -16.0, 0.0],
                    ],
                ],
                dtype=float,
            ),
        )

    async def test_cumulative_resource_matrix(
        self, pizza_example_measure: Measure
    ):
        cumulative_resource_matrix = (
            pizza_example_measure.cumulative_resource_matrix
        )
        assert np.array_equal(
            np.round(cumulative_resource_matrix, decimals=3),
            np.array(
                [
                    [6.0, 6.0, 6.0, 6.0, 6.0, 6.0],
                    [7.0, 7.0, 7.0, 7.0, 7.0, 7.0],
                    [4.0, 4.0, 4.0, 4.0, 4.0, 4.0],
                    [16.0, 16.0, 16.0, 16.0, 16.0, 16.0],
                ],
                dtype=float,
            ),
        )


@pytest.mark.asyncio
class TestParallelFarming:
    async def test_run_vector(self, parallel_farming_example_measure: Measure):
        run_vector = parallel_farming_example_measure.run_vector
        assert np.array_equal(
            np.round(run_vector, decimals=3),
            np.array(
                [20.0, 10.0, 10.0, 10.0, 10.0, 10.0],
                dtype=float,
            ),
        )

    async def test_resource_matrix(
        self, parallel_farming_example_measure: Measure
    ):
        resource_matrix = parallel_farming_example_measure.resource_matrix
        assert np.array_equal(
            np.round(resource_matrix, decimals=3),
            np.array(
                [
                    [20.0, -20.0, 0.0, 0.0, 0.0, 0.0],
                    [0.0, 10.0, -10.0, 0.0, 0.0, 0.0],
                    [0.0, 0.0, 0.0, 10.0, -10.0, 0.0],
                    [0.0, 0.0, 0.0, 0.0, 30.0, -30.0],
                ],
                dtype=float,
            ),
        )

    async def test_flow_matrix(
        self, parallel_farming_example_measure: Measure
    ):
        flow_matrix = parallel_farming_example_measure.flow_matrix
        assert np.array_equal(
            np.round(flow_matrix, decimals=3),
            np.array(
                [
                    [
                        [0.0, 20.0, 0.0, 0.0, 0.0, 0.0],
                        [-20.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                    ],
                    [
                        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                        [0.0, 0.0, 10.0, 0.0, 0.0, 0.0],
                        [0.0, -10.0, 0.0, 0.0, 0.0, 0.0],
                        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                    ],
                    [
                        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                        [0.0, 0.0, 0.0, 0.0, 10.0, 0.0],
                        [0.0, 0.0, 0.0, -10.0, 0.0, 0.0],
                        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                    ],
                    [
                        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                        [0.0, 0.0, 0.0, 0.0, 0.0, 30.0],
                        [0.0, 0.0, 0.0, 0.0, -30.0, 0.0],
                    ],
                ],
                dtype=float,
            ),
        )

    async def test_cumulative_resource_matrix(
        self, parallel_farming_example_measure: Measure
    ):
        cumulative_resource_matrix = (
            parallel_farming_example_measure.cumulative_resource_matrix
        )
        assert np.array_equal(
            np.round(cumulative_resource_matrix, decimals=3),
            np.array(
                [
                    [20.0, 20.0, 20.0, 0.0, 0.0, 0.0],
                    [10.0, 10.0, 10.0, 0.0, 0.0, 0.0],
                    [0.0, 0.0, 0.0, 10.0, 10.0, 10.0],
                    [0.0, 0.0, 0.0, 30.0, 30.0, 30.0],
                ],
                dtype=float,
            ),
        )


@pytest.mark.asyncio
class TestReal:
    async def test_run_vector(self, real_example_measure: Measure):
        run_vector = real_example_measure.run_vector
        assert np.array_equal(
            np.round(run_vector, decimals=3),
            np.array(
                [40.0, 5.0, 12.5, 5.0, 15.0, 5.0, 5.0, 5.0],
                dtype=float,
            ),
        )

    async def test_resource_matrix(self, real_example_measure: Measure):
        resource_matrix = real_example_measure.resource_matrix
        assert np.array_equal(
            np.round(resource_matrix, decimals=3),
            np.array(
                [
                    [0.0, 0.0, 12.5, 0.0, 0.0, -10.0, -2.5, 0.0],
                    [0.0, 5.0, 0.0, 0.0, 0.0, 0.0, -5, 0.0],
                    [40.0, 0.0, 0.0, 0.0, 0.0, -15.0, 0.0, -25.0],
                    [0.0, 0.0, 0.0, 5.0, 0.0, 0.0, -5.0, 0.0],
                    [0.0, 0.0, 0.0, 0.0, -15.0, 5.0, 5.0, 5.0],
                ],
                dtype=float,
            ),
        )

    async def test_flow_matrix(self, real_example_measure: Measure):
        flow_matrix = real_example_measure.flow_matrix
        assert np.array_equal(
            np.round(flow_matrix, decimals=3),
            np.array(
                [
                    [
                        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                        [0.0, 0.0, 0.0, 0.0, 0.0, 10.0, 2.5, 0.0],
                        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                        [0.0, 0.0, -10.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                        [0.0, 0.0, -2.5, 0.0, 0.0, 0.0, 0.0, 0.0],
                        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                    ],
                    [
                        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 5.0, 0.0],
                        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                        [0.0, -5.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                    ],
                    [
                        [0.0, 0.0, 0.0, 0.0, 0.0, 15.0, 0.0, 25.0],
                        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                        [-15.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                        [-25.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                    ],
                    [
                        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 5.0, 0.0],
                        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                        [0.0, 0.0, 0.0, -5.0, 0.0, 0.0, 0.0, 0.0],
                        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                    ],
                    [
                        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                        [0.0, 0.0, 0.0, 0.0, 0.0, -5.0, -5.0, -5.0],
                        [0.0, 0.0, 0.0, 0.0, 5.0, 0.0, 0.0, 0.0],
                        [0.0, 0.0, 0.0, 0.0, 5.0, 0.0, 0.0, 0.0],
                        [0.0, 0.0, 0.0, 0.0, 5.0, 0.0, 0.0, 0.0],
                    ],
                ],
                dtype=float,
            ),
        )

    async def test_cumulative_resource_matrix(
        self, real_example_measure: Measure
    ):
        cumulative_resource_matrix = (
            real_example_measure.cumulative_resource_matrix
        )
        assert np.array_equal(
            np.round(cumulative_resource_matrix, decimals=3),
            np.array(
                [
                    [12.5, 12.5, 12.5, 12.5, 12.5, 12.5, 12.5, 12.5],
                    [5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0],
                    [40.0, 40.0, 40.0, 40.0, 40.0, 40.0, 40.0, 40.0],
                    [5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0],
                    [15.0, 15.0, 15.0, 15.0, 15.0, 15.0, 15.0, 15.0],
                ],
                dtype=float,
            ),
        )
