import numpy as np
import pytest

from mat_dp_core import Processes, Resources


@pytest.mark.asyncio
class TestProcessExpr:
    async def test_simple_process_multiplier(self, farming_example):
        resources, processes = farming_example
        arable_farm = processes["arable_farm"]
        assert str(f"{arable_farm *2}") == "2*arable_farm"

    async def test_simple_process_r_multiplier(self, farming_example):
        resources, processes = farming_example
        arable_farm = processes["arable_farm"]
        assert str(f"{2*arable_farm}") == "2*arable_farm"

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
            == "2*arable_farm + dairy_farm"
        )

    async def test_simple_process_subtract(self, farming_example):
        resources, processes = farming_example
        arable_farm = processes["arable_farm"]
        dairy_farm = processes["dairy_farm"]
        assert str(f"{arable_farm - dairy_farm}") == "arable_farm - dairy_farm"

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
        assert str(repr(expr)) == "<ProcessExpr 9*arable_farm + 6*dairy_farm>"


@pytest.mark.asyncio
class TestProcesses:
    async def test_repr_process(self):
        resources = Resources()
        hay = resources.create("hay")
        processes = Processes()
        proc1 = processes.create("test1", (hay, 1))
        assert repr(proc1) == "<Process: test1>"

    async def test_repr_process_and_other_equality(self):
        resources = Resources()
        hay = resources.create("hay")
        processes = Processes()
        proc1 = processes.create("test1", (hay, 1))
        assert not (proc1 == 1)

    async def test_process_no_resources_attached(self):
        processes = Processes()
        try:
            processes.create("test1")
            assert False
        except ValueError as e:
            assert str(e) == "No resources attached to test1"

    async def test_two_processes_different_classes(self):
        resources = Resources()
        hay = resources.create("hay")
        processes1 = Processes()
        processes2 = Processes()

        proc1 = processes1.create("test1", (hay, 1))
        proc2 = processes2.create("test2", (hay, 1))
        try:
            proc1 + proc2
            assert False
        except ValueError as e:
            assert (
                str(e)
                == "Combining two exprs from different processes classes"
            )

    async def test_expr_and_process_different_classes(self):
        resources = Resources()
        hay = resources.create("hay")
        processes1 = Processes()
        processes2 = Processes()

        proc1 = processes1.create("test1", (hay, 1))
        proc2 = processes2.create("test2", (hay, 1))
        try:
            proc1 * 1 + proc2
            assert False
        except ValueError as e:
            assert (
                str(e)
                == "Combining process and expr from different processes classes"
            )

    async def test_load(self):
        resources = Resources()
        hay = resources.create("hay")
        processes = Processes()
        processes.load([("test", [(hay, 2)])])
        assert processes._processes == [("test", np.array([2.0]), None, None)]

    async def test_dump(self):
        resources = Resources()
        hay = resources.create("hay")
        processes = Processes()
        processes.create("test", (hay, 2))
        assert processes.dump() == [("test", np.array([2.0]), None, None)]

    async def test_getitem_out_of_range(self):
        resources = Resources()
        resources.create("hay")
        processes = Processes()
        try:
            processes[0]
            assert False
        except IndexError as e:
            assert str(e) == "list index out of range"

    async def test_unknown_key_process(self):
        resources = Resources()
        resources.create("hay")
        processes = Processes()
        try:
            processes["new"]
            assert False
        except KeyError as e:
            assert str(e) == "\"'new'\""

    async def test_non_unique_key_process(self):
        resources = Resources()
        hay = resources.create("hay")
        processes = Processes()
        processes.create("test", (hay, 2))
        processes.create("test", (hay, 2))
        try:
            processes["test"]
            assert False
        except KeyError as e:
            assert str(e) == "'Name test non unique: please use index'"

    async def test_process_in_processes(self):
        resources = Resources()
        hay = resources.create("hay")
        processes1 = Processes()
        processes2 = Processes()
        test = processes1.create("test", (hay, 2))

        assert test in processes1
        assert test not in processes2
        assert 1 not in processes1
