import pytest
import configparser
from ..pipeline import TMDbMovie, FileS3


@pytest.fixture
def year():
    return 2000


@pytest.fixture
def initial():
    return 'A'


@pytest.fixture
def imdb_id():
    return 'tt9686708'


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
def target(year, initial, imdb_id, bucket_name, api_key):
    return TMDbMovie(
        year=year,
        initial=initial,
        imdb_id=imdb_id,
        bucket_name=bucket_name,
        api_key=api_key)


def test_get_document(target):
    actual = target.get_document()
    assert actual['id'] == 579583


def test_imdb_id(target, imdb_id):
    actual = target.get_document()
    assert actual['id_imdb'] == imdb_id


def test_save(target):
    url = target.save()
    assert FileS3(url).get_size() > 0


def test_has_been_found_True(target):
    assert target.has_been_found()


def test_has_been_found_False(bucket_name, api_key):
    assert not TMDbMovie(
        year=year,
        initial=initial,
        imdb_id='tt0124798',
        bucket_name=bucket_name,
        api_key=api_key).has_been_found()
