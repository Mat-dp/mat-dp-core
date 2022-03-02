import pytest

from mat_dp_core import Resources


@pytest.mark.asyncio
class TestResource:
    async def test_repr(self, test_resource):
        assert str(repr(test_resource)) == "<Resource: test>"

    async def test_equality_random_object(self, test_resource):
        assert not (test_resource == 1)


@pytest.mark.asyncio
class TestResources:
    async def test_load_res(self):
        resources = Resources()
        resources.load([("test", "ea")])
        assert resources._resources == [("test", "ea")]

    async def test_dump_res(self):
        resources = Resources()
        resources.create("test", "ea")
        assert resources.dump() == [("test", "ea")]

    async def test_out_of_range_zero(self):
        resources = Resources()
        try:
            resources[0]
            assert False
        except IndexError as e:
            assert str(e) == "list index out of range"

    async def test_out_of_range_one(self):
        resources = Resources()
        try:
            resources[1]
            assert False
        except IndexError as e:
            assert str(e) == "list index out of range"

    async def test_get_wrong_item(self):
        resources = Resources()
        resources.create("test", "ea")
        try:
            resources["not_test"]
        except KeyError as e:
            assert str(e) == "\"'not_test'\""

    async def test_duplicate_item(self):
        resources = Resources()
        resources.create("test", "ea")
        resources.create("test", "ea")
        try:
            resources["test"]
        except KeyError as e:
            assert str(e) == "'Name test non unique: please use index'"
