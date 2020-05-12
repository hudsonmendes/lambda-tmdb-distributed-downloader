import pytest
from tdd import FileHttp, FileS3, IMDb


@pytest.fixture
def http_file():
    return FileHttp('https://www.iana.org/assignments/service-names-port-numbers/service-names-port-numbers.txt')


def test_get_size_for_s3_non_existing():
    s3_file = FileS3('s3://hudsonmendes-datalake/non-existing.txt')
    assert s3_file.get_size() == 0


def test_get_size_for_s3_existing():
    s3_file = FileS3('s3://hudsonmendes-datalake/dummy.txt')
    assert s3_file.get_size() > 0


def test_copy_from_http(http_file):
    s3_file = FileS3('s3://hudsonmendes-datalake/test.txt')
    try:
        s3_file.delete()
        s3_file.copy_from(http_file)
        assert s3_file.get_size() == http_file.get_size()
    finally:
        s3_file.delete()


def test_touch(http_file):
    s3_file = FileS3('s3://hudsonmendes-datalake/test.txt')
    try:
        s3_file.delete()
        s3_file.touch()
        assert s3_file.get_size() == len('touchè') + 1
    finally:
        s3_file.delete()


def test_stream():
    s3_file = FileS3('s3://hudsonmendes-datalake/dummy.txt')
    with s3_file.stream() as stream:
        assert next(stream) == b'<nothing>'
