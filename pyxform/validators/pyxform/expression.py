"""Targeted validation for expressions in XLSForm workbook cells."""

from collections.abc import Sequence
from itertools import islice
from typing import Any

from pyxform import aliases, constants
from pyxform.errors import ErrorCode, PyXFormError
from pyxform.parsing.expression import ends_with_dangling_operator
from pyxform.utils import default_is_dynamic

ExpressionPath = tuple[str, ...]

_SURVEY_EXPRESSION_PATHS = {
    (constants.BIND, "relevant"),
    (constants.BIND, "constraint"),
    (constants.BIND, "calculate"),
    (constants.BIND, "required"),
    (constants.BIND, "readonly"),
    (constants.CHOICE_FILTER,),
    (constants.CONTROL, "jr:count"),
    ("default",),
}
_SETTINGS_EXPRESSION_PATHS = {("instance_name",)}
_ENTITIES_EXPRESSION_PATHS = {
    (constants.EntityColumns.ENTITY_ID.value,),
    (constants.EntityColumns.CREATE_IF.value,),
    (constants.EntityColumns.UPDATE_IF.value,),
    (constants.EntityColumns.LABEL.value,),
}
_EXPRESSION_PATHS_BY_SHEET = {
    constants.SURVEY: _SURVEY_EXPRESSION_PATHS,
    constants.SETTINGS: _SETTINGS_EXPRESSION_PATHS,
    constants.ENTITIES: _ENTITIES_EXPRESSION_PATHS,
}


def _get_source_headers(
    sheet_data: Sequence[dict[str, Any]],
    sheet_header: Sequence[dict[str, Any]] | None,
) -> tuple[str, ...]:
    """Get original headers in the same order used by header normalization."""
    if sheet_header:
        return tuple(sheet_header[0])

    headers: dict[str, None] = {}
    for row in islice(sheet_data, 0, 100):
        for header in row:
            headers[header] = None
    return tuple(headers)


def _get_value(row: dict[str, Any], path: ExpressionPath) -> Any:
    """Get a possibly nested value from a normalized workbook row."""
    value: Any = row
    for token in path:
        if not isinstance(value, dict):
            return None
        value = value.get(token)
    return value


def validate_dangling_operators(
    sheet_name: str,
    source_sheet_data: Sequence[dict[str, Any]],
    source_sheet_header: Sequence[dict[str, Any]] | None,
    normalized_sheet_data: Sequence[dict[str, Any]],
    normalized_headers: tuple[ExpressionPath, ...],
) -> None:
    """Reject recognized expressions ending with an operator needing an operand."""
    expression_paths = _EXPRESSION_PATHS_BY_SHEET[sheet_name]
    source_headers = _get_source_headers(
        sheet_data=source_sheet_data, sheet_header=source_sheet_header
    )
    expression_columns = tuple(
        (path, source_header)
        for path, source_header in zip(normalized_headers, source_headers, strict=False)
        if path in expression_paths
    )

    for row_number, row in enumerate(normalized_sheet_data, start=2):
        if sheet_name == constants.SURVEY and aliases.yes_no.get(row.get("disabled")):
            continue

        for path, source_header in expression_columns:
            value = _get_value(row=row, path=path)
            if not isinstance(value, str) or not value:
                continue
            if path == ("default",) and not default_is_dynamic(
                element_default=value, element_type=row.get(constants.TYPE)
            ):
                continue
            if ends_with_dangling_operator(text=value):
                raise PyXFormError(
                    code=ErrorCode.EXPRESSION_001,
                    context={
                        "row": row_number,
                        "sheet": sheet_name,
                        "column": source_header,
                    },
                )
