import pytest
import configparser
from tdd import TMDbMovie, FileS3


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
def target(imdb_id, bucket_name, api_key):
    return TMDbMovie(
        api_key=api_key,
        bucket_name=bucket_name,
        imdb_id=imdb_id)

def test_get_document(target):
    actual = target.get_document()
    assert actual['id'] == 579583


def test_imdb_id(target, imdb_id):
    actual = target.get_document()
    assert actual['id_imdb'] == imdb_id


def test_save(target):
    url = target.save()
    assert FileS3(url).get_size() > 0
