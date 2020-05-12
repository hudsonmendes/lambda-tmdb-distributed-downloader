import pytest
import time
import datetime
from tdd import IMDb, FileS3


def test_cache_url():
    date_tag = int(time.mktime(datetime.date.today().timetuple()))
    assert IMDb().cache_url.endswith(f'{date_tag}.tsv.gz')


def test_get_movie_refs_stream():
    movie_ids = IMDb().get_movie_refs_stream(year=1892, initial='L')
    actual = next(movie_ids, None)
    assert actual


@pytest.mark.slow
def test_cache():
    imdb = IMDb()
    imdb.cache_url = 's3://hudsonmendes-datalake/test.tsv.gz'
    imdb.cache_file = FileS3(imdb.cache_url)
    try:
        imdb.cache_file.delete()
        next(imdb.get_movie_refs_stream(year=1892, initial='L'), None)
        assert imdb.cache_file.get_size() > 0
    finally:
        imdb.cache_file.delete()
