"""Test multiple XLSForm can be generated successfully."""

import os
from pathlib import Path
from unittest import TestCase

from pyxform.builder import create_survey_from_path

from tests import utils


class DumpAndLoadTests(TestCase):
    def setUp(self):
        self.excel_files = [
            "group.xlsx",
            "loop.xlsx",
            "text_and_integer.xlsx",
            "yes_or_no_question.xlsx",
        ]
        self.surveys = {}
        self.this_directory = os.path.dirname(__file__)
        for filename in self.excel_files:
            path = utils.path_to_text_fixture(filename)
            self.surveys[filename] = create_survey_from_path(path)

    def test_load_from_dump(self):
        for survey in self.surveys.values():
            survey.json_dump()
            path = survey.name + ".json"
            survey_from_dump = create_survey_from_path(path)
            self.assertEqual(survey.to_json_dict(), survey_from_dump.to_json_dict())

    def tearDown(self):
        for survey in self.surveys.values():
            path = Path(survey.name + ".json")
            path.unlink(missing_ok=True)
