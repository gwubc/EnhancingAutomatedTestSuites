@pytest.mark.parametrize(
        "stream, value",
        (
            (StringIO.StringIO, "Test"),
            (BytesIO, b"Test"),
            pytest.param(
                cStringIO, "Test", marks=pytest.mark.skipif("cStringIO is None")
            ),
        ),
    )
    def test_io_streams(self, stream, value):
        assert super_len(stream()) == 0
        assert super_len(stream(value)) == 4

def test_super_len_correctly_calculates_len_of_partially_read_file(self):
        s = StringIO.StringIO()
        s.write("foobarbogus")
        assert super_len(s) == 0

@pytest.mark.parametrize("error", [IOError, OSError])
    def test_super_len_handles_files_raising_weird_errors_in_tell(self, error):

        class BoomFile:

            def __len__(self):
                return 5

            def tell(self):
                raise error()

        assert super_len(BoomFile()) == 0

@pytest.mark.parametrize("error", [IOError, OSError])
    def test_super_len_tell_ioerror(self, error):

        class NoLenBoomFile:

            def tell(self):
                raise error()

            def seek(self, offset, whence):
                pass

        assert super_len(NoLenBoomFile()) == 0

def test_string(self):
        assert super_len("Test") == 4

@pytest.mark.parametrize("mode, warnings_num", (("r", 1), ("rb", 0)))
    def test_file(self, tmpdir, mode, warnings_num, recwarn):
        file_obj = tmpdir.join("test.txt")
        file_obj.write("Test")
        with file_obj.open(mode) as fd:
            assert super_len(fd) == 4
        assert len(recwarn) == warnings_num

def test_tarfile_member(self, tmpdir):
        file_obj = tmpdir.join("test.txt")
        file_obj.write("Test")
        tar_obj = str(tmpdir.join("test.tar"))
        with tarfile.open(tar_obj, "w") as tar:
            tar.add(str(file_obj), arcname="test.txt")
        with tarfile.open(tar_obj) as tar:
            member = tar.extractfile("test.txt")
            assert super_len(member) == 4

def test_super_len_with__len__(self):
        foo = [1, 2, 3, 4]
        len_foo = super_len(foo)
        assert len_foo == 4

def test_super_len_with_no__len__(self):

        class LenFile:

            def __init__(self):
                self.len = 5

        assert super_len(LenFile()) == 5

def test_super_len_with_tell(self):
        foo = StringIO.StringIO("12345")
        assert super_len(foo) == 5
        foo.read(2)
        assert super_len(foo) == 3

def test_super_len_with_fileno(self):
        with open(__file__, "rb") as f:
            length = super_len(f)
            file_data = f.read()
        assert length == len(file_data)

def test_super_len_with_no_matches(self):
        assert super_len(object()) == 0