"""Test sms syntax."""

from tests.pyxform_test_case import PyxformTestCase


class SMSTest(PyxformTestCase):
    def test_prefix_only(self):
        self.assertPyxformXform(
            name="data",
            md="""
            | survey   |           |          |       |           |
            |          | type      |   name   | label | hint      |
            |          | string    |   name   | Name  | your name |
            | settings |           |          |       |           |
            |          | prefix    |          |       |           |
            |          | sms_test  |          |       |           |
            """,
            xml__contains=['odk:prefix="sms_test"'],
        )

    def test_delimiter_only(self):
        self.assertPyxformXform(
            name="data",
            md="""
            | survey   |           |          |       |           |
            |          | type      |   name   | label | hint      |
            |          | string    |   name   | Name  | your name |
            | settings |           |          |       |           |
            |          | delimiter |          |       |           |
            |          | ~         |          |       |           |
            """,
            xml__contains=['odk:delimiter="~"'],
        )

    def test_prefix_and_delimiter(self):
        self.assertPyxformXform(
            name="data",
            md="""
            | survey   |           |          |       |           |
            |          | type      |   name   | label | hint      |
            |          | string    |   name   | Name  | your name |
            | settings |           |          |       |           |
            |          | delimiter | prefix   |       |           |
            |          | *         | sms_test2|       |           |
            """,
            xml__contains=['odk:delimiter="*"', 'odk:prefix="sms_test2"'],
        )

    def test_sms_tag(self):
        self.assertPyxformXform(
            name="data",
            md="""
            | survey   |           |          |             |       |           |         |
            |          | type      |   name   | compact_tag | label | hint      | default |
            |          | string    |   name   | n           | Name  | your name |         |
            |          | int       |   age    | +a          | Age   | your age  | 7       |
            |          | string    | fruit    |             | Fruit | fav fruit |         |
            """,
            xml__contains=[
                '<name odk:tag="n"/>',
                '<age odk:tag="+a">7</age>',
                "<fruit/>",
            ],
        )

    def test_sms_info(self):
        md = """
        | settings |
        | | form_title | form_id  | sms_keyword | sms_separator | sms_allow_media | sms_date_format | sms_datetime_format |
        | | SMS        | sms_info | inf         | +             | 1               | %Y-%m-%d        | %Y-%m-%d-%H:%M      |

        | survey |
        | | type                     | name         | sms_field | label                         |
        | | begin_group              | section1     | a         |                               |
        | | integer                  | age          | q1        | How old are you?              |
        | | select_one yes_no        | has_children | q2        | Do you have any children?     |
        | | end_group                |              |           |                               |
        | | begin_group              | medias       | c         |                               |
        | | image                    | picture      |           | May I take your picture?      |
        | | geopoint                 | gps          |           | Record your GPS coordinates.  |
        | | end_group                |              |           |                               |
        | | begin_group              | browsers     | b         |                               |
        | | select_multiple browsers | web_browsers | q5        | What web browsers do you use? |
        | | end_group                |              |           |                               |

        | choices |
        | | list_name | name    | sms_option | label             |
        | | yes_no    | n       | n          | no                |
        | | yes_no    | y       | y          | yes               |
        | | browsers  | firefox | ff         | Mozilla Firefox   |
        | | browsers  | chrome  | gc         | Google Chrome     |
        """

        def get_cases(value) -> tuple[tuple[str, int], ...]:
            """No element text and no attribute values match the input 'value'."""
            return (
                (f"""/h:html//*[text()='{value}']""", 0),
                (f"""/h:html//*[@*='{value}']""", 0),
            )

        sms_values = (
            "inf",
            "+",
            "1",
            "%Y-%m-%d",
            "%Y-%m-%d-%H:%M",
            "a",
            "q1",
            "q2",
            "b",
            "c",
        )

        self.assertPyxformXform(
            md=md,
            xml__xpath_count=[
                # The sms_* settings and sms_field values do not affect the xform output.
                case
                for val in sms_values
                for case in get_cases(val)
            ],
            xml__xpath_match=[
                # Model instance for choices contains sms_option values. Currently occurs
                # due to passing through all choices data, not specific to sms_option.
                """/h:html/h:head/x:model/x:instance[@id='yes_no']/x:root/x:item[./x:name='n' and ./x:sms_option='n']""",
                """/h:html/h:head/x:model/x:instance[@id='yes_no']/x:root/x:item[./x:name='y' and ./x:sms_option='y']""",
                """/h:html/h:head/x:model/x:instance[@id='browsers']/x:root/x:item[./x:name='firefox' and ./x:sms_option='ff']""",
                """/h:html/h:head/x:model/x:instance[@id='browsers']/x:root/x:item[./x:name='chrome' and ./x:sms_option='gc']""",
            ],
        )
