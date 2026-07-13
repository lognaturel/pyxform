"""Some tests for the new (v0.9) spec is properly implemented."""

import os
from pathlib import Path
from unittest import TestCase

import pyxform
from pyxform.errors import ErrorCode, PyXFormError
from pyxform.utils import has_external_choices
from pyxform.validators.odk_validate import ODKValidateError, check_xform
from pyxform.xls2json import SurveyReader
from pyxform.xls2json_backends import DefinitionData, get_xlsform, xlsx_to_dict
from pyxform.xls2xform import convert

from tests import test_output
from tests.fixtures import bug_example_forms, example_forms


class TestXFormConversion(TestCase):
    maxDiff = None

    def test_conversion_raises(self):
        """Should find that conversion results in an error being raised by pyxform."""
        cases = (
            ("group_name_test.xls", "[row : 3] Question or group with no name."),
            ("duplicate_columns.xlsx", "Duplicate column header: label"),
        )
        for i, (case, err_msg) in enumerate(cases):
            with self.subTest(msg=f"{i}: {case}"):
                with self.assertRaises(PyXFormError) as err:
                    convert(xlsform=Path(bug_example_forms.PATH) / case, warnings=[])
                self.assertIn(err_msg, err.exception.args[0])


class ValidateWrapper(TestCase):
    maxDiff = None

    @staticmethod
    def test_conversion():
        filename = "ODKValidateWarnings.xlsx"
        path_to_excel_file = os.path.join(bug_example_forms.PATH, filename)
        # Get the xform output path:
        root_filename, _ = os.path.splitext(filename)
        output_path = os.path.join(test_output.PATH, root_filename + ".xml")
        # Do the conversion:
        warnings = []
        json_survey = pyxform.xls2json.parse_file_to_json(
            path_to_excel_file, default_name="ODKValidateWarnings", warnings=warnings
        )
        survey = pyxform.create_survey_element_from_dict(json_survey)
        survey.print_xform_to_file(output_path, warnings=warnings)


class EmptyStringOnRelevantColumnTest(TestCase):
    def test_conversion(self):
        filename = "ict_survey_fails.xls"
        workbook_dict = get_xlsform(
            xlsform=os.path.join(bug_example_forms.PATH, filename)
        )
        with self.assertRaises(KeyError):
            # bind:relevant should not be part of workbook_dict
            workbook_dict.survey[0]["bind: relevant"].strip()


class BadChoicesSheetHeaders(TestCase):
    def test_conversion(self):
        filename = "spaces_in_choices_header.xls"
        path_to_excel_file = os.path.join(bug_example_forms.PATH, filename)
        warnings = []
        pyxform.xls2json.parse_file_to_json(
            path_to_excel_file,
            default_name="spaces_in_choices_header",
            warnings=warnings,
        )
        # The "column with no header" warning is probably not reachable since XLS/X
        # pre-processing ignores any columns without a header.
        observed = [
            w
            for w in warnings
            if w == ErrorCode.HEADER_004.value.format(column="header with spaces")
        ]
        self.assertEqual(1, len(observed), warnings)

    def test_values_with_spaces_are_cleaned(self):
        """
        Test that values with leading and trailing whitespaces are processed.

        This test checks that the submission_url provided is cleaned
        of leading and trailing whitespaces.
        """
        filename = "spaces_in_choices_header.xls"
        path_to_excel_file = os.path.join(bug_example_forms.PATH, filename)
        survey_reader = SurveyReader(
            path_to_excel_file, default_name="spaces_in_choices_header"
        )
        result = survey_reader.to_json_dict()

        self.assertEqual(
            result["submission_url"], "https://odk.ona.io/random_person/submission"
        )


class TestChoiceNameAsType(TestCase):
    def test_choice_name_as_type(self):
        filename = "choice_name_as_type.xls"
        path_to_excel_file = os.path.join(example_forms.PATH, filename)
        xls_reader = SurveyReader(path_to_excel_file, default_name="choice_name_as_type")
        survey_dict = xls_reader.to_json_dict()
        self.assertTrue(has_external_choices(survey_dict))


class TestXLDateAmbigous(TestCase):
    """Test non standard sheet with exception is processed successfully."""

    def test_xl_date_ambigous(self):
        """Test non standard sheet with exception is processed successfully."""
        filename = "xl_date_ambiguous.xlsx"
        path_to_excel_file = os.path.join(bug_example_forms.PATH, filename)
        xls_reader = SurveyReader(path_to_excel_file, default_name="xl_date_ambiguous")
        survey_dict = xls_reader.to_json_dict()
        self.assertTrue(len(survey_dict) > 0)


class TestXLDateAmbigousNoException(TestCase):
    """Test date values that exceed the workbook datemode value.
    (This would cause an exception with xlrd, but openpyxl handles it).
    """

    def test_xl_date_ambigous_no_exception(self):
        """Test standard sheet is processed successfully."""
        filename = "xl_date_ambiguous_v1.xlsx"
        path_to_excel_file = os.path.join(bug_example_forms.PATH, filename)
        survey_dict = xlsx_to_dict(path_to_excel_file)
        self.assertEqual(survey_dict["survey"][4]["default"], "1900-01-01 00:00:00")


class TestSpreadSheetFilesWithMacrosAreAllowed(TestCase):
    """Test that spreadsheets with .xlsm extension are allowed."""

    def test_xlsm_files_are_allowed(self):
        filename = "excel_with_macros.xlsm"
        result = get_xlsform(xlsform=os.path.join(bug_example_forms.PATH, filename))
        self.assertIsInstance(result, DefinitionData)


class TestBadCalculation(TestCase):
    """Bad calculation should not kill the application."""

    def test_bad_calculate_javarosa_error(self):
        filename = "bad_calc.xml"
        test_xml = os.path.join(test_output.PATH, filename)
        self.assertRaises(ODKValidateError, check_xform, test_xml)
