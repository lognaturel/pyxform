from tests.pyxform_test_case import PyxformTestCase
from tests.xpath_helpers.questions import xpq


class TestHiddenOutput(PyxformTestCase):
    def test_hidden(self):
        """Should find that the hidden type is recognised and output as a string."""
        md = """
        | survey |
        | | type   | name | label |
        | | hidden | q1   | Q1    |
        """
        self.assertPyxformXform(
            md=md,
            xml__xpath_match=[
                xpq.model_instance_item("q1"),
                xpq.model_instance_bind("q1", "string"),
            ],
        )
