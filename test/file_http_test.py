from tdd import FileHttp, IMDb


def test_get_size_for_https():
    http_file = FileHttp(IMDb.SOURCE_URL)
    assert http_file.get_size() > 0
