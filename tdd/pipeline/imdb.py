from typing import Iterable

import time
import csv
import gzip
import codecs
import datetime
import boto3
import unidecode
from urllib.request import urlopen

from .imdb_movie import IMDbMovie
from .file_http import FileHttp
from .file_s3 import FileS3


class IMDb:
    SOURCE_URL = 'https://datasets.imdbws.com/title.basics.tsv.gz'
    CACHE_URL = 's3://{bucket_name}/imdb/title.basics-{date_tag}.tsv.gz'

    """
    Operates the IMDB official dataset, caching it into S3, and
    providing us with the imdb_ids available in it.

    The chaching mechanism was devised to stop our downloader from
    hitting the official IMDB URL too manytimes, which could cause
    disruption to the service. We instead cache the file in S3 and
    reduce the roundtrip as well ourselves against being rate-limited
    or flagged as an attacker.
    """

    def __init__(
            self,
            max_attempts=60,
            bucket_name='hudsonmendes-datalake',
            **kwargs):
        self.max_attempts = max_attempts
        self.s3 = boto3.resource('s3')

        # source file is the official url from the IMDb
        self.source_file = FileHttp(IMDb.SOURCE_URL)

        # to be up-to-date, we renew the cache everyday
        ts = int(time.mktime(datetime.date.today().timetuple()))
        self.cache_url = IMDb.CACHE_URL.format(bucket_name=bucket_name, date_tag=ts)
        self.cache_file = FileS3(self.cache_url)

    def get_movie_refs_stream(self, year: int, initial: str) -> Iterable[IMDbMovie]:
        """
        Ensure that the IMDB file is cached in S3, and then stream its
        information about the movies represented by IMDbMovie.
        """
        self.attempt_first_cache()
        self.await_until_cached()
        with self.cache_file.stream() as f_in:
            yield from self.extract_movie_refs_from(f_in, year, initial)

    def attempt_first_cache(self):
        if self.cache_file.get_size() == 0:
            print('IMDB, file not cached, transfering it to datalake')
            self.cache_file.touch()
            self.cache_file.copy_from(self.source_file)
        else:
            print('IMDB, file already present in datalake')

    def await_until_cached(self):
        attempts = 0
        while self.cache_file.get_size() < self.source_file.get_size():
            print('IMDB, waiting transference of IMDB file to datalake')
            time.sleep(1)  # wait 1 second and check again
            attempts += 1
            if attempts > self.max_attempts:
                msg = f'[IMDB] the cache file never got ready, {self.max_attempts} attempts'
                raise ResourceWarning(msg)
        print('IMDB, file ready in datalake')

    def extract_movie_refs_from(self, stream, year, initial):
        print('IMDB -> TMDB, streaming ids now...')
        reviewed = 0
        with gzip.open(stream) as f_in:
            f_cur = codecs.iterdecode(f_in, 'utf-8')
            csv_reader = csv.reader(f_cur, delimiter='\t')
            header = next(csv_reader)
            for row in csv_reader:
                # check if it matches year and initial, and yield if it does
                imdb_movie = IMDbMovie(header, row)
                if initial == imdb_movie.initial and year == imdb_movie.year:
                    yield imdb_movie
                # log review progress
                reviewed += 1
                if reviewed % 100000 == 0:
                    print(f'[IMDb] rewiewed {reviewed}')
