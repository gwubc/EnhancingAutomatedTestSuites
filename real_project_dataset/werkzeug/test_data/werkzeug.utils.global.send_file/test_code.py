@pytest.mark.parametrize("path", [html_path, str(html_path)])
def test_path(path):
    rv = send_file(path, environ)
    assert rv.mimetype == "text/html"
    assert rv.direct_passthrough
    rv.direct_passthrough = False
    assert rv.data == html_path.read_bytes()
    rv.close()

def test_x_sendfile():
    rv = send_file(html_path, environ, use_x_sendfile=True)
    assert rv.headers["x-sendfile"] == str(html_path)
    assert rv.data == b""
    rv.close()

def test_last_modified():
    last_modified = datetime.datetime(1999, 1, 1, tzinfo=datetime.timezone.utc)
    rv = send_file(txt_path, environ, last_modified=last_modified)
    assert rv.last_modified == last_modified
    rv.close()

@pytest.mark.parametrize(
    "file_factory", [lambda: txt_path.open("rb"), lambda: io.BytesIO(b"test")]
)
def test_object(file_factory):
    rv = send_file(file_factory(), environ, mimetype="text/plain", use_x_sendfile=True)
    rv.direct_passthrough = False
    assert rv.data
    assert rv.mimetype == "text/plain"
    assert "x-sendfile" not in rv.headers
    rv.close()

def test_object_without_mimetype():
    with pytest.raises(TypeError, match="detect the MIME type"):
        send_file(io.BytesIO(b"test"), environ)

def test_object_mimetype_from_name():
    rv = send_file(io.BytesIO(b"test"), environ, download_name="test.txt")
    assert rv.mimetype == "text/plain"
    rv.close()

@pytest.mark.parametrize(
    "file_factory", [lambda: txt_path.open(), lambda: io.StringIO("test")]
)
def test_text_mode_fails(file_factory):
    with file_factory() as f, pytest.raises(ValueError, match="binary mode"):
        send_file(f, environ, mimetype="text/plain")

@pytest.mark.parametrize(
    ("as_attachment", "value"), [(False, "inline"), (True, "attachment")]
)
def test_disposition_name(as_attachment, value):
    rv = send_file(txt_path, environ, as_attachment=as_attachment)
    assert rv.headers["Content-Disposition"] == f"{value}; filename=test.txt"
    rv.close()

def test_object_attachment_requires_name():
    with pytest.raises(TypeError, match="attachment"):
        send_file(
            io.BytesIO(b"test"), environ, mimetype="text/plain", as_attachment=True
        )
    rv = send_file(
        io.BytesIO(b"test"), environ, as_attachment=True, download_name="test.txt"
    )
    assert rv.headers["Content-Disposition"] == "attachment; filename=test.txt"
    rv.close()

@pytest.mark.parametrize(
    ("name", "ascii", "utf8"),
    (
        ("index.html", "index.html", None),
        (
            "Ñandú／pingüino.txt",
            '"Nandu/pinguino.txt"',
            "%C3%91and%C3%BA%EF%BC%8Fping%C3%BCino.txt",
        ),
        ("Vögel.txt", "Vogel.txt", "V%C3%B6gel.txt"),
        ("те:/ст", '":/"', "%D1%82%D0%B5%3A%2F%D1%81%D1%82"),
        ("(тест.txt", '"(.txt"', "%28%D1%82%D0%B5%D1%81%D1%82.txt"),
        ("(test.txt", '"(test.txt"', None),
    ),
)
def test_non_ascii_name(name, ascii, utf8):
    rv = send_file(html_path, environ, as_attachment=True, download_name=name)
    rv.close()
    content_disposition = rv.headers["Content-Disposition"]
    assert f"filename={ascii}" in content_disposition
    if utf8:
        assert f"filename*=UTF-8''{utf8}" in content_disposition
    else:
        assert "filename*=UTF-8''" not in content_disposition

def test_no_cache_conditional_default():
    rv = send_file(
        txt_path,
        EnvironBuilder(
            headers={"If-Modified-Since": http_date(datetime.datetime(2020, 7, 12))}
        ).get_environ(),
        last_modified=datetime.datetime(2020, 7, 11),
    )
    rv.close()
    assert "no-cache" in rv.headers["Cache-Control"]
    assert not rv.cache_control.public
    assert not rv.cache_control.max_age
    assert not rv.expires
    assert rv.status_code == 304

@pytest.mark.parametrize(("value", "public"), [(0, False), (60, True)])
def test_max_age(value, public):
    rv = send_file(txt_path, environ, max_age=value)
    rv.close()
    assert ("no-cache" in rv.headers["Cache-Control"]) != public
    assert rv.cache_control.public == public
    assert rv.cache_control.max_age == value
    assert rv.expires
    assert rv.status_code == 200

def test_etag():
    rv = send_file(txt_path, environ)
    rv.close()
    assert rv.headers["ETag"].count("-") == 2
    rv = send_file(txt_path, environ, etag=False)
    rv.close()
    assert "ETag" not in rv.headers
    rv = send_file(txt_path, environ, etag="unique")
    rv.close()
    assert rv.headers["ETag"] == '"unique"'

@pytest.mark.parametrize("as_attachment", (True, False))
def test_content_encoding(as_attachment):
    rv = send_file(
        txt_path, environ, download_name="logo.svgz", as_attachment=as_attachment
    )
    rv.close()
    assert rv.mimetype == "image/svg+xml"
    assert rv.content_encoding == ("gzip" if not as_attachment else None)

def test_root_path(tmp_path):
    d = tmp_path / "d"
    d.mkdir()
    (d / "test.txt").write_bytes(b"test")
    rv = send_file("d/test.txt", environ, _root_path=tmp_path)
    rv.direct_passthrough = False
    assert rv.data == b"test"
    rv.close()
    rv = send_from_directory("d", "test.txt", environ, _root_path=tmp_path)
    rv.direct_passthrough = False
    assert rv.data == b"test"
    rv.close()

def test_max_age_callable():
    rv = send_file(txt_path, environ, max_age=lambda p: 10)
    rv.close()
    assert rv.cache_control.max_age == 10