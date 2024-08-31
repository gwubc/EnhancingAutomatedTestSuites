@pytest.mark.parametrize(
        "encoding",
        (
            "utf-32",
            "utf-8-sig",
            "utf-16",
            "utf-8",
            "utf-16-be",
            "utf-16-le",
            "utf-32-be",
            "utf-32-le",
        ),
    )
    def test_encoded(self, encoding):
        data = "{}".encode(encoding)
        assert guess_json_utf(data) == encoding

def test_bad_utf_like_encoding(self):
        assert guess_json_utf(b"\x00\x00\x00\x00") is None

@pytest.mark.parametrize(
        ("encoding", "expected"),
        (
            ("utf-16-be", "utf-16"),
            ("utf-16-le", "utf-16"),
            ("utf-32-be", "utf-32"),
            ("utf-32-le", "utf-32"),
        ),
    )
    def test_guess_by_bom(self, encoding, expected):
        data = "\ufeff{}".encode(encoding)
        assert guess_json_utf(data) == expected