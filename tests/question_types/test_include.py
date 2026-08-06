from pathlib import Path

from pyxform.builder import create_survey_from_path
from pyxform.errors import PyXFormError
from pyxform.xls2xform import convert

from tests.pyxform_test_case import PyxformTestCase
from tests.utils import get_temp_dir
from tests.xpath_helpers.questions import xpq


class TestIncludeParsing(PyxformTestCase):
    def test_include_file_missing__error(self):
        """Should raise an error if the include 'name' does not match an adjacent file."""
        md = """
        | survey |
        | | type        | name     | label    |
        | | begin_group | g1       | G1       |
        | | include     | included | Included |
        | | end_group   | g1       |          |
        """
        with get_temp_dir() as tmp, self.assertRaises(PyXFormError) as err:
            self.assertFalse((Path(tmp) / "included.md").is_file())
            (Path(tmp) / "test_name.md").write_text(md)
            create_survey_from_path(
                path=str(Path(tmp) / "test_name.md"),
                include_directory=True,
            )

        self.assertEqual("This section has not been included.", str(err.exception))

    def test_include_via_pyxformtestcase__error(self):
        """Should raise an error if 'include' is used via PyxformTestCase."""
        # Loading of additional files is only available via `create_survey_from_path`.
        md = """
        | survey |
        | | type        | name     | label    |
        | | begin_group | g1       | G1       |
        | | include     | included | Included |
        | | end_group   | g1       |          |
        """
        self.assertPyxformXform(
            md=md, errored=True, error__contains=["This section has not been included."]
        )

    def test_include_via_convert__error(self):
        """Should raise an error if 'include' is used via `convert`."""
        # Loading of additional files is only available via `create_survey_from_path`.
        md = """
        | survey |
        | | type        | name     | label    |
        | | begin_group | g1       | G1       |
        | | include     | included | Included |
        | | end_group   | g1       |          |
        """
        included = """
        | survey |
        | | type | name | label |
        | | text | q1   | Q1    |
        """
        with get_temp_dir() as tmp, self.assertRaises(PyXFormError) as err:
            (Path(tmp) / "included.md").write_text(included)
            (Path(tmp) / "test_name.md").write_text(md)
            convert(xlsform=Path(tmp) / "test_name.md")

        self.assertEqual("This section has not been included.", str(err.exception))


class TestIncludeOutput(PyxformTestCase):
    def test_include(self):
        """Should find that the 'include' type loads adjacent named files into the form."""
        # The included file has the "meta" item so it has to be wrapped in a group.
        md = """
        | survey |
        | | type        | name     | label    |
        | | begin_group | g1       | G1       |
        | | include     | included | Included |
        | | end_group   | g1       |          |
        """
        included = """
        | survey |
        | | type | name | label |
        | | text | q1   | Q1    |
        """
        with get_temp_dir() as tmp:
            # The include item "name" value is used to match the file name.
            (Path(tmp) / "included.md").write_text(included)
            # Uses "test_name" to match the default XPath helper instance name.
            (Path(tmp) / "test_name.md").write_text(md)
            # The feature is only implemented and reachable via this function.
            survey = create_survey_from_path(
                path=str(Path(tmp) / "test_name.md"),
                include_directory=True,
            )

        self.assertPyxformXform(
            survey=survey,
            xml__xpath_match=[
                xpq.model_instance_item("g1/x:q1"),
                xpq.model_instance_bind("g1/q1", "string"),
                # The question item directive "included" is in the output.
                """/h:html/h:head/x:model/x:instance[not(.//x:included)]""",
            ],
        )
