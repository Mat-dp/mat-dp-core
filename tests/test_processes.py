import pytest

from mat_dp_core import Processes, Resources


@pytest.mark.asyncio
class TestProcessExpr:
    async def test_simple_process_multiplier(self, farming_example):
        resources, processes = farming_example
        arable_farm = processes["arable_farm"]
        assert str(f"{arable_farm *2}") == "arable_farm * 2"

    async def test_simple_process_r_multiplier(self, farming_example):
        resources, processes = farming_example
        arable_farm = processes["arable_farm"]
        assert str(f"{2*arable_farm}") == "arable_farm * 2"

    async def test_simple_process_add(self, farming_example):
        resources, processes = farming_example
        arable_farm = processes["arable_farm"]
        dairy_farm = processes["dairy_farm"]
        assert str(f"{arable_farm + dairy_farm}") == "arable_farm + dairy_farm"

    async def test_duplicate_process_add(self, farming_example):
        resources, processes = farming_example
        arable_farm = processes["arable_farm"]
        dairy_farm = processes["dairy_farm"]
        assert (
            str(f"{arable_farm + dairy_farm + arable_farm}")
            == "arable_farm * 2 + dairy_farm"
        )

    async def test_simple_process_subtract(self, farming_example):
        resources, processes = farming_example
        arable_farm = processes["arable_farm"]
        dairy_farm = processes["dairy_farm"]
        assert (
            str(f"{arable_farm - dairy_farm}")
            == "arable_farm + dairy_farm * -1"
        )

    async def test_duplicate_process_subtract(self, farming_example):
        resources, processes = farming_example
        arable_farm = processes["arable_farm"]
        dairy_farm = processes["dairy_farm"]
        assert str(f"{arable_farm + dairy_farm - arable_farm}") == "dairy_farm"

    async def test_repr(self, farming_example):
        resources, processes = farming_example
        arable_farm = processes["arable_farm"]
        dairy_farm = processes["dairy_farm"]
        expr = (arable_farm * 4 + dairy_farm * 2 - arable_farm) * 3
        assert (
            str(repr(expr)) == "<ProcessExpr arable_farm * 9 + dairy_farm * 6>"
        )
