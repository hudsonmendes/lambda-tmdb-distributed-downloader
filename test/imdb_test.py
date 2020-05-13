import pytest
import time
import datetime
import configparser
from tdd import IMDb, FileS3


@pytest.fixture
def bucket_name():
    config = configparser.ConfigParser()
    config.read('config.ini')
    return config['DATALAKE']['BUCKET_NAME']


@pytest.fixture
def target(bucket_name):
    return IMDb(bucket_name=bucket_name)


def test_cache_url():
    date_tag = int(time.mktime(datetime.date.today().timetuple()))
    imdb = IMDb(bucket_name=bucket_name)
    assert imdb.cache_url.endswith(f'{date_tag}.tsv.gz')


@pytest.mark.slow
def test_get_movie_refs_stream(target):
    movie_ids = target.get_movie_refs_stream(year=1892, initial='L')
    actual = next(movie_ids, None)
    assert actual


@pytest.mark.slow
def test_cache(target, bucket_name):
    target.cache_url = f's3://{bucket_name}/test.tsv.gz'
    target.cache_file = FileS3(target.cache_url)
    try:
        target.cache_file.delete()
        next(target.get_movie_refs_stream(year=1892, initial='L'), None)
        assert target.cache_file.get_size() > 0
    finally:
        target.cache_file.delete()
