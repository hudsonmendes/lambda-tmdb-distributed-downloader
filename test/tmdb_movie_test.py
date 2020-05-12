import pytest
import os
import configparser
from tdd import TMDbMovie


@pytest.fixture
def imdb_id():
    return 'tt9686708'


@pytest.fixture
def api_key():
    config = configparser.ConfigParser()
    config.read('../secrets.ini')
    return config['TMDB']['API_KEY']


def test_get_document(imdb_id, api_key):
    actual = TMDbMovie(imdb_id, api_key).get_document()
    print(actual)
    assert actual['id'] == 579583
