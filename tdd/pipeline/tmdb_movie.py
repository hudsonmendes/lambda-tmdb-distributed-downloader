import json
from urllib.request import urlopen
from .file_s3 import FileS3

class TMDbMovie:
    URL_TMPL = 'https://api.themoviedb.org/3/find/{imdb_id}?api_key={api_key}&language=en-US&external_source=imdb_id'
    S3_TMPL  = 's3://{bucket_name}/tmdb/movies/year-{year}/initial-{initial}/tmdb-movie-{tmdb_id}.json'

    """
    Wraps the request to the TMDBMovie resource.
    """

    def __init__(
            self,
            year: int,
            initial: str,
            imdb_id: str,
            api_key: str,
            bucket_name: str,
            **kwargs):
        self.year = year
        self.initial = initial
        self.imdb_id = imdb_id
        self.bucket_name = bucket_name
        self.url = TMDbMovie.URL_TMPL.format(imdb_id=imdb_id, api_key=api_key)
        self.doc = None

    def get_document(self):
        """
        Gets the JSON document lazily, and caches it for future use.
        """
        self.ensure_cache()
        return self.doc

    def has_been_found(self):
        """ 
        Some movies from IMDb may not be found in TMDb.
        When that is the case, we ignore it
        """ 
        self.ensure_cache()
        return self.doc != None

    def get_id(self):
        """
        Reads the movie_id from the cached document
        """
        self.ensure_cache()
        return self.doc['id']

    def save(self):
        """
        Saves the `doc` as a file in S3 and returns the S3 url.
        """
        self.ensure_cache()
        s3_url = TMDbMovie.S3_TMPL.format(
            bucket_name=self.bucket_name,
            year=self.year,
            initial=self.initial,
            tmdb_id=self.get_id())
        s3_file = FileS3(s3_url)
        s3_file.write(self.doc)
        return s3_file.url

    def ensure_cache(self):
        """
        Ensure that we have the document cached
        """
        if self.doc == None:
            with urlopen(self.url) as res:
                res = json.load(res)
                if 'movie_results' in res and res['movie_results']:
                    self.doc = next(iter(res['movie_results']), None)
                    self.doc['id_imdb'] = self.imdb_id
