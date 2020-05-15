import pytest
import configparser
from tdd import TMDbReviews, FileS3


@pytest.fixture
def year():
    return 2000


@pytest.fixture
def initial():
    return 'A'


@pytest.fixture
def movie_id():
    return 19995


@pytest.fixture
def bucket_name():
    config = configparser.ConfigParser()
    config.read('config.ini')
    return config['DATALAKE']['BUCKET_NAME']


@pytest.fixture
def api_key():
    config = configparser.ConfigParser()
    config.read('config.ini')
    return config['TMDB']['API_KEY']


@pytest.fixture
def target(year, initial, movie_id, bucket_name, api_key):
    return TMDbReviews(
        year=year,
        initial=initial,
        movie_id=movie_id,
        bucket_name=bucket_name,
        api_key=api_key)


def test_get_documents(target):
    assert len(target.get_documents()) >= 2  # orginally 2


def test_save(target):
    urls = target.save()
    assert len(urls) >= 2
    assert all([FileS3(url).get_size() > 0 for url in urls])
