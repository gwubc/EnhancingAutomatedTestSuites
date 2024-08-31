@pytest.mark.parametrize(
    "value, expected",
    (
        ("application/xml", ("application/xml", {})),
        (
            "application/json ; charset=utf-8",
            ("application/json", {"charset": "utf-8"}),
        ),
        (
            "application/json ; Charset=utf-8",
            ("application/json", {"charset": "utf-8"}),
        ),
        ("text/plain", ("text/plain", {})),
        (
            "multipart/form-data; boundary = something ; boundary2='something_else' ; no_equals ",
            (
                "multipart/form-data",
                {
                    "boundary": "something",
                    "boundary2": "something_else",
                    "no_equals": True,
                },
            ),
        ),
        (
            'multipart/form-data; boundary = something ; boundary2="something_else" ; no_equals ',
            (
                "multipart/form-data",
                {
                    "boundary": "something",
                    "boundary2": "something_else",
                    "no_equals": True,
                },
            ),
        ),
        (
            "multipart/form-data; boundary = something ; 'boundary2=something_else' ; no_equals ",
            (
                "multipart/form-data",
                {
                    "boundary": "something",
                    "boundary2": "something_else",
                    "no_equals": True,
                },
            ),
        ),
        (
            'multipart/form-data; boundary = something ; "boundary2=something_else" ; no_equals ',
            (
                "multipart/form-data",
                {
                    "boundary": "something",
                    "boundary2": "something_else",
                    "no_equals": True,
                },
            ),
        ),
        ("application/json ; ; ", ("application/json", {})),
    ),
)
def test__parse_content_type_header(value, expected):
    assert _parse_content_type_header(value) == expected