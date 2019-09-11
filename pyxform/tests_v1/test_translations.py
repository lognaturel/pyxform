# -*- coding: utf-8 -*-
"""
Test translations syntax.
"""
from pyxform.tests_v1.pyxform_test_case import PyxformTestCase


class DoubleColonTranslations(PyxformTestCase):
    def test_langs(self):
        model_contains = (
            """<bind nodeset="/translations/n1"""
            + """" readonly="true()" type="string"/>"""
        )
        self.assertPyxformXform(
            name="translations",
            id_string="transl",
            md="""
            | survey |      |      |                |               |
            |        | type | name | label::english | label::french |
            |        | note | n1   | hello          | bonjour       |
            """,
            errored=False,
            itext__contains=[
                '<translation lang="french">',
                '<text id="/translations/n1:label">',
                "<value>bonjour</value>",
                "</text>",
                "</translation>",
                '<translation lang="english">',
                '<text id="/translations/n1:label">',
                "<value>hello</value>",
                "</text>",
                "</translation>",
            ],
            xml__contains=["""<label ref="jr:itext('/translations/n1:label')"/>"""],
            model__contains=[model_contains],
        )

    def test_translations_and_choice_filters(self):
        self.assertPyxformXform(
            name="translations_choice_filters",
            id_string="transl",
            md="""
            | survey  |                    |          |                     |                    |
            |         | type               | name     | label::English (en) | choice_filter      |
            |         | select_one country | country  | Country             |                    |
            |         | select_one city    | city     | City                | country=${country} |
            | choices |                    |          |                     |                    |
            |         | list_name          | name     | label               |                    |
            |         | country            | france   | France              |                    |
            |         | country            | canada   | Canada              |                    |
            |         | city               | grenoble | Grenoble            |                    |
            |         | city               | quebec   | Quebec              |                    |
            """,
            errored=False,
            debug= True
        )
