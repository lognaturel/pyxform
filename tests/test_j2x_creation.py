"""Testing creation of Surveys using verbose methods."""

from unittest import TestCase

from pyxform import MultipleChoiceQuestion, Survey


class Json2XformVerboseSurveyCreationTests(TestCase):
    def test_survey_can_be_created_in_a_slightly_less_verbose_manner(self):
        choices = {
            "test": [
                {"name": "red", "label": "Red"},
                {"name": "blue", "label": "Blue"},
            ]
        }
        s = Survey(name="Roses_are_Red", choices=choices)
        q = MultipleChoiceQuestion(
            name="Favorite_Color",
            type="select one",
            list_name="test",
        )
        s.add_child(q)

        expected_dict = {
            "name": "Roses_are_Red",
            "type": "survey",
            "children": [
                {"name": "Favorite_Color", "type": "select one", "list_name": "test"}
            ],
            "choices": choices,
        }

        self.assertEqual(expected_dict, s.to_json_dict())
