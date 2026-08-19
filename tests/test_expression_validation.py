"""Tests for targeted validation of dangling XPath operators."""

from unittest import TestCase, mock

from pyxform.errors import ErrorCode, PyXFormError
from pyxform.xls2xform import convert


class TestDanglingOperatorValidation(TestCase):
    @staticmethod
    def _survey_with_expression(column: str, expression: str) -> dict:
        expression_row = {
            "type": "text",
            "name": "q2",
            "label": "Q2",
            column: expression,
        }
        if column == "repeat_count":
            expression_row.update(type="begin_repeat", name="r1", label="R1")
        elif column == "choice_filter":
            expression_row.update(type="select_one choices")
        return {
            "survey": [
                {"type": "text", "name": "q1", "label": "Q1"},
                expression_row,
            ]
        }

    def assert_expression_error(
        self, xlsform: dict, *, sheet: str, row: int, column: str
    ) -> PyXFormError:
        with self.assertRaises(PyXFormError) as caught:
            convert(xlsform=xlsform, validate=False)
        self.assertEqual(ErrorCode.EXPRESSION_001, caught.exception.code)
        self.assertEqual(
            ErrorCode.EXPRESSION_001.value.format(sheet=sheet, row=row, column=column),
            str(caught.exception),
        )
        return caught.exception

    def test_survey_expression_columns(self):
        """Should validate every recognized survey expression source and its aliases."""
        for column in (
            "relevance",
            "constraint",
            "calculation",
            "required",
            "read_only",
            "choice_filter",
            "repeat_count",
            "default",
        ):
            with self.subTest(column=column):
                self.assert_expression_error(
                    self._survey_with_expression(column=column, expression="${q1} ="),
                    sheet="survey",
                    row=3,
                    column=column,
                )

    def test_supported_dangling_operators(self):
        """Should reject every operator that unambiguously needs a right operand."""
        for operator in (
            "=",
            "!=",
            "<",
            ">",
            "<=",
            ">=",
            "+",
            "-",
            "div",
            "mod",
            "and",
            "or",
            "|",
        ):
            with self.subTest(operator=operator):
                self.assert_expression_error(
                    self._survey_with_expression(
                        column="relevant", expression=f"${{q1}} {operator}"
                    ),
                    sheet="survey",
                    row=3,
                    column="relevant",
                )

    def test_word_operators_at_token_boundaries(self):
        """Should reject word operators without spaces and after wildcard operands."""
        for expression in ("${q1}and", "true()and", "/data/* and"):
            with self.subTest(expression=expression):
                self.assert_expression_error(
                    self._survey_with_expression(
                        column="relevant", expression=expression
                    ),
                    sheet="survey",
                    row=3,
                    column="relevant",
                )

    def test_example_reports_original_survey_location(self):
        """Should report the workbook row and original column before conversion."""
        xlsform = {
            "survey": [
                {"type": "begin_group", "name": "intro_module", "label": "Intro"},
                {
                    "type": "begin_group",
                    "name": "intro_submodule",
                    "label": "Intro",
                },
                {
                    "type": "select_one yes_no",
                    "name": "RESPConsent",
                    "label": "May we begin?",
                },
                {
                    "type": "integer",
                    "name": "test_fail_moda",
                    "label": "Test",
                    "relevant": "${RESPConsent} =",
                },
            ]
        }
        self.assert_expression_error(xlsform, sheet="survey", row=5, column="relevant")

    def test_settings_instance_name_with_normalized_header(self):
        """Should report the original settings header after normalization."""
        xlsform = {
            "settings": [{"Instance Name": "${q1} !="}],
            "survey": [{"type": "text", "name": "q1", "label": "Q1"}],
        }
        self.assert_expression_error(
            xlsform, sheet="settings", row=2, column="Instance Name"
        )

    def test_entities_expression_columns(self):
        """Should validate every recognized entities expression source."""
        for column in ("entity_id", "create_if", "update_if", "label"):
            with self.subTest(column=column):
                xlsform = {
                    "entities": [{"list_name": "people", column: "${q1} <="}],
                    "survey": [{"type": "text", "name": "q1", "label": "Q1"}],
                }
                self.assert_expression_error(
                    xlsform, sheet="entities", row=2, column=column
                )

    def test_valid_and_non_expression_values_are_accepted(self):
        """Should accept valid paths, disabled rows, and static defaults."""
        xlsform = {
            "survey": [
                {"type": "text", "name": "q1", "label": "Q1"},
                {
                    "type": "text",
                    "name": "valid_comparison",
                    "label": "Valid",
                    "relevant": "${q1} = '='",
                },
                {
                    "type": "text",
                    "name": "wildcard_path",
                    "label": "Wildcard",
                    "relevant": "/data/*",
                },
                {
                    "type": "text",
                    "name": "operator_node_names",
                    "label": "Operator node names",
                    "relevant": "/data/and | /data/or | /data/div | /data/mod",
                },
                {
                    "type": "text",
                    "name": "disabled_expression",
                    "label": "Disabled",
                    "relevant": "${q1} >",
                    "disabled": "yes",
                },
                {
                    "type": "text",
                    "name": "static_default",
                    "label": "Static",
                    "default": "literal text =",
                },
            ]
        }
        result = convert(xlsform=xlsform, validate=False)
        self.assertIn("<static_default>literal text =</static_default>", result.xform)

    @mock.patch("pyxform.survey.odk_validate.check_xform")
    def test_odk_validate_is_not_invoked(self, odk_validate_mock):
        """Should reject the source expression before invoking ODK Validate."""
        xlsform = self._survey_with_expression(column="relevant", expression="${q1} >=")
        with self.assertRaises(PyXFormError):
            convert(xlsform=xlsform, validate=True)
        odk_validate_mock.assert_not_called()
