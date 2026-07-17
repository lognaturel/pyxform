"""Test builder module functionality."""

import os
from pathlib import Path
from unittest import TestCase

from pyxform import InputQuestion, Survey
from pyxform.builder import SurveyElementBuilder, create_survey_from_xls
from pyxform.errors import ErrorCode, PyXFormError
from pyxform.utils import print_pyobj_to_json

from tests import utils

FIXTURE_FILETYPE = "xls"


class BuilderTests(TestCase):
    maxDiff = None

    def setUp(self):
        self.this_directory = os.path.dirname(__file__)
        survey_out = Survey(name="age", sms_keyword="age", type="survey")
        question = InputQuestion(name="age", type="integer", label="How old are you?")
        survey_out.add_child(question)
        self.survey_out_dict = survey_out.to_json_dict()
        print_pyobj_to_json(
            self.survey_out_dict, utils.path_to_text_fixture("how_old_are_you.json")
        )

    @staticmethod
    def test_create_from_file_object():
        path = utils.path_to_text_fixture("yes_or_no_question.xls")
        with open(path, "rb") as f:
            create_survey_from_xls(f)

    def tearDown(self):
        fixture_path = utils.path_to_text_fixture("how_old_are_you.json")
        Path(fixture_path).unlink(missing_ok=True)

    def test_create_table_from_dict(self):
        d = {
            "type": "loop",
            "name": "my_loop",
            "label": {"English": "My Loop"},
            "columns": [
                {"name": "col1", "label": {"English": "column 1"}},
                {"name": "col2", "label": {"English": "column 2"}},
            ],
            "children": [
                {
                    "type": "integer",
                    "name": "count",
                    "label": {"English": "How many are there in this group?"},
                }
            ],
        }
        builder = SurveyElementBuilder()
        g = builder.create_survey_element_from_dict(d)

        expected_dict = {
            "name": "my_loop",
            "label": {"English": "My Loop"},
            "type": "group",
            "children": [
                {
                    "name": "col1",
                    "label": {"English": "column 1"},
                    "type": "group",
                    "children": [
                        {
                            "name": "count",
                            "label": {"English": "How many are there in this group?"},
                            "type": "integer",
                        }
                    ],
                },
                {
                    "name": "col2",
                    "label": {"English": "column 2"},
                    "type": "group",
                    "children": [
                        {
                            "name": "count",
                            "label": {"English": "How many are there in this group?"},
                            "type": "integer",
                        }
                    ],
                },
            ],
        }
        self.assertEqual(expected_dict, g.to_json_dict())

    def test_loop(self):
        survey = utils.create_survey_from_fixture("loop", filetype=FIXTURE_FILETYPE)
        expected_dict = {
            "name": "loop",
            "id_string": "loop",
            "sms_keyword": "loop",
            "title": "loop",
            "type": "survey",
            "default_language": "default",
            "choices": {
                "toilet_type": [
                    {
                        "label": {"english": "Pit latrine with slab"},
                        "name": "pit_latrine_with_slab",
                    },
                    {
                        "label": {"english": "Pit latrine without slab/open pit"},
                        "name": "open_pit_latrine",
                    },
                    {"label": {"english": "Bucket system"}, "name": "bucket_system"},
                    {"label": {"english": "Other"}, "name": "other"},
                ]
            },
            "children": [
                {
                    "name": "available_toilet_types",
                    "list_name": "toilet_type",
                    "itemset": "toilet_type",
                    "label": {"english": "What type of toilets are on the premises?"},
                    "type": "select all that apply",
                    "children": [
                        {
                            "name": "pit_latrine_with_slab",
                            "label": {"english": "Pit latrine with slab"},
                        },
                        {
                            "name": "open_pit_latrine",
                            "label": {"english": "Pit latrine without slab/open pit"},
                        },
                        {
                            "name": "bucket_system",
                            "label": {"english": "Bucket system"},
                        },
                        # Removing this because select alls shouldn't need
                        # an explicit none option
                        # {
                        #    u'name': u'none',
                        #    u'label': u'None',
                        #    },
                        {"name": "other", "label": {"english": "Other"}},
                    ],
                },
                {
                    "name": "available_toilet_types_other",
                    "bind": {"relevant": "selected(../available_toilet_types, 'other')"},
                    "label": "Specify other.",
                    "type": "text",
                },
                {
                    "name": "loop_toilet_types",
                    "type": "group",
                    "children": [
                        {
                            "name": "pit_latrine_with_slab",
                            "label": {"english": "Pit latrine with slab"},
                            "type": "group",
                            "children": [
                                {
                                    "name": "number",
                                    "label": {
                                        "english": "How many Pit latrine with slab are"
                                        " on the premises?"
                                    },
                                    "type": "integer",
                                }
                            ],
                        },
                        {
                            "name": "open_pit_latrine",
                            "label": {"english": "Pit latrine without slab/open pit"},
                            "type": "group",
                            "children": [
                                {
                                    "name": "number",
                                    "label": {
                                        "english": "How many Pit latrine without "
                                        "slab/open pit are on the premises?"
                                    },
                                    "type": "integer",
                                }
                            ],
                        },
                        {
                            "name": "bucket_system",
                            "label": {"english": "Bucket system"},
                            "type": "group",
                            "children": [
                                {
                                    "name": "number",
                                    "label": {
                                        "english": "How many Bucket system are on the"
                                        " premises?"
                                    },
                                    "type": "integer",
                                }
                            ],
                        },
                        {
                            "children": [
                                {
                                    "label": {
                                        "english": "How many Other are on the premises?"
                                    },
                                    "name": "number",
                                    "type": "integer",
                                }
                            ],
                            "label": {"english": "Other"},
                            "name": "other",
                            "type": "group",
                        },
                    ],
                },
                {
                    "children": [
                        {
                            "bind": {"jr:preload": "uid", "readonly": "true()"},
                            "name": "instanceID",
                            "type": "calculate",
                        }
                    ],
                    "control": {"bodyless": True},
                    "name": "meta",
                    "type": "group",
                },
            ],
        }
        self.assertEqual(expected_dict, survey.to_json_dict())

    def test_trigger_data_wrong_type__error(self):
        """Should raise an error if a trigger is truthy and something other than tuple."""
        # Should only happen if the builder is used incorrectly, rather than any user
        # XLSForm being able to trigger this.
        d = {
            "type": "survey",
            "name": "test_name",
            "id_string": "data",
            "title": "data",
            "sms_keyword": "data",
            "default_language": "default",
            "children": [
                {"label": "Q1", "name": "q1", "type": "integer"},
                {"label": "Q2", "name": "q2", "trigger": "${q1}", "type": "text"},
                {
                    "children": [
                        {
                            "bind": {"jr:preload": "uid", "readonly": "true()"},
                            "name": "instanceID",
                            "type": "calculate",
                        }
                    ],
                    "control": {"bodyless": True},
                    "name": "meta",
                    "type": "group",
                },
            ],
        }
        with self.assertRaises(PyXFormError) as e:
            SurveyElementBuilder().create_survey_element_from_dict(d)
        self.assertEqual(ErrorCode.INTERNAL_001, e.exception.code)
        self.assertEqual({"type": "<class 'str'>", "value": "${q1}"}, e.exception.context)
