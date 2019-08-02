from asynctest import TestCase

from asgard.models.base import BaseModel, ModelFactory


class BaseModelTest(TestCase):
    async def test_choose_instance_based_on_type_field(self):
        class BaseAgent(BaseModel):
            pass

        Agent = ModelFactory(BaseAgent)

        class ModelOne(BaseAgent):
            type: str = "ONE"
            other_field: str

        class ModelTwo(BaseAgent):
            type: str = "TWO"

        instance = Agent(**{"type": "ONE", "other_field": "value"})
        self.assertIsInstance(instance, ModelOne)
        self.assertDictEqual(
            {"type": "ONE", "other_field": "value"}, instance.dict()
        )

    async def test_check_transformation_method_to_alchemy(self):
        class MyModel(BaseModel):
            type = "type"

        with self.assertRaises(NotImplementedError):
            model = MyModel()
            await model.to_alchemy_obj()

    async def test_check_transformation_method_from_alchemy(self):
        class MyModel(BaseModel):
            type = "type"

        with self.assertRaises(NotImplementedError):
            model = MyModel()
            await model.from_alchemy_object(None)
