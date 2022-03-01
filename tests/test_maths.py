import numpy as np
import pytest

from mat_dp_core import Measure


@pytest.mark.asyncio
class TestCalculation:
    async def test_farming_all(self, farming_example_measure: Measure):
        resource_matrix = farming_example_measure.resource_matrix
        flow_matrix = farming_example_measure.flow_matrix
        cumulative_resource_matrix = (
            farming_example_measure.cumulative_resource_matrix
        )
        assert np.all(
            np.round(resource_matrix, decimals=3)
            == np.array([[20, -20.0, 0.0], [0.0, 10.0, -10.0]], dtype=float)
        )
        assert np.all(
            np.round(flow_matrix, decimals=3)
            == np.array(
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
            )
        )
        assert np.all(
            np.round(cumulative_resource_matrix, decimals=3)
            == np.array([[20, 20.0, 20.0], [10.0, 10.0, 10.0]], dtype=float)
        )
