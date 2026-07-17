from collections.abc import Iterable
from unittest import expectedFailure

from pyxform.aliases import select, select_multiple, select_one

from tests.pyxform_test_case import PyxformTestCase
from tests.xpath_helpers.choices import xpc
from tests.xpath_helpers.questions import xpq


class TestSelectOrOtherOutput(PyxformTestCase):
    @staticmethod
    def get_cases(
        commands: Iterable[str], control: str, list_name: str = "c1"
    ) -> tuple[tuple[str, str], ...]:
        return tuple(
            (f"{s} {list_name} {o}", control)
            for s in commands
            for o in ("or specify other", "or_other", "or other")
        )

    def test_aliases__select_one__ok(self):
        """Should find that all supported aliases result in the same output."""
        md = """
        | survey |
        | | type   | name | label |
        | | {}     | q1   | Q1    |

        | choices |
        | | list_name | name | label |
        | | c1        | n1   | N1    |
        """
        for case in self.get_cases(select_one, "select1"):
            with self.subTest(msg=case):
                self.assertPyxformXform(
                    md=md.format(case[0]),
                    xml__xpath_match=[
                        xpc.model_instance_choices_label(
                            "c1", (("n1", "N1"), ("other", "Other"))
                        ),
                        xpq.model_instance_item("q1"),
                        xpq.model_instance_bind("q1", "string"),
                        xpq.body_control("q1", case[1]),
                        xpq.model_instance_item("q1_other"),
                        xpq.model_instance_bind("q1_other", "string"),
                        xpq.body_control("q1_other", "input"),
                    ],
                )

    def test_aliases__select_multiple__ok(self):
        """Should find that all supported aliases result in the same output."""
        md = """
        | survey |
        | | type   | name | label |
        | | {}     | q1   | Q1    |

        | choices |
        | | list_name | name | label |
        | | c1        | n1   | N1    |
        """
        for case in self.get_cases(select_multiple, "select"):
            with self.subTest(msg=case):
                self.assertPyxformXform(
                    md=md.format(case[0]),
                    xml__xpath_match=[
                        xpc.model_instance_choices_label(
                            "c1", (("n1", "N1"), ("other", "Other"))
                        ),
                        xpq.model_instance_item("q1"),
                        xpq.model_instance_bind("q1", "string"),
                        xpq.body_control("q1", case[1]),
                        xpq.model_instance_item("q1_other"),
                        xpq.model_instance_bind("q1_other", "string"),
                        xpq.body_control("q1_other", "input"),
                    ],
                )

    def test_aliases__select_from_file__error(self):
        """Should raise an error for unsupported select types used with or_other."""
        md = """
        | survey |
        | | type   | name | label |
        | | {}     | q1   | Q1    |

        | choices |
        | | list_name | name | label |
        | | c1        | n1   | N1    |
        """
        for case in self.get_cases(select_multiple, "select", "c1.csv"):
            with self.subTest(msg=case):
                self.assertPyxformXform(
                    md=md.format(case[0]),
                    errored=True,
                    error__contains=[
                        "[row : 2] Please specify choices for this 'or other' question."
                    ],
                )

    # Does not raise an error, just outputs a form with `q1` but no `q1_other`.
    @expectedFailure
    def test_aliases__rank__error(self):
        """Should raise an error for unsupported select types used with or_other."""
        md = """
        | survey |
        | | type    | name | label |
        | | rank c1 | q1   | Q1    |

        | choices |
        | | list_name | name | label |
        | | c1        | n1   | N1    |
        """
        for case in self.get_cases(("rank",), "odk:rank"):
            with self.subTest(msg=case):
                self.assertPyxformXform(
                    md=md.format(case[0]),
                    errored=True,
                )

    # Does not raise an error, just outputs a form with `q1` but no `q1_other`.
    @expectedFailure
    def test_aliases__select_one_external__error(self):
        """Should raise an error for unsupported select types used with or_other."""
        md = """
        | survey |
        | | type                   | name | label | choice_filter |
        | | select_one_external c1 | q1   | Q1    | false()       |

        | external_choices |
        | | list_name | name | label |
        | | c1        | n1   | N1    |
        """
        self.assertIn("select_one_external", select)
        self.assertPyxformXform(
            md=md,
            errored=True,
        )
