from typing import Iterable, Dict
import json
from urllib.request import urlopen
from .file_s3 import FileS3


class TMDbReviews:
    URL_TMPL = 'https://api.themoviedb.org/3/movie/{movie_id}/reviews?api_key={api_key}&language=en-US&page={page}'
    S3_TMPL = 's3://{bucket_name}/tmdb/tmdb-reviews/tmdb-movie-{movie_id}-review-{review_id}.json'

    """
    Wraps the request to the TMDB review resource,
    working through the several pages and consolidating
    the documents.
    """

    def __init__(
            self,
            movie_id: int,
            bucket_name: str,
            api_key: str,
            max_pages: int = 1000,
            **kwargs):
        self.movie_id = movie_id
        self.bucket_name = bucket_name
        self.api_key = api_key
        self.max_pages = max_pages
        self.docs = None

    def get_documents(self) -> Iterable[Dict]:
        """
        Gets the JSON documents lazily, and caches it for future use.
        """
        self.ensure_cache()
        return self.docs

    def save(self) -> Iterable[str]:
        """
        Saves each document as a file in S3 and returns the S3 url.
        """
        self.ensure_cache()
        urls = []
        for doc in self.docs:
            url = TMDbReviews.S3_TMPL.format(
                bucket_name=self.bucket_name,
                movie_id=self.movie_id,
                review_id=doc['id'])
            FileS3(url).write(doc)
            urls.append(url)
        return urls

    def ensure_cache(self):
        """
        Ensures that we have the documents cached
        """
        if self.docs == None:
            cache = []
            for page in range(1, self.max_pages):
                url = TMDbReviews.URL_TMPL.format(
                    movie_id=self.movie_id,
                    api_key=self.api_key,
                    page=page)
                print(url)
                try:
                    with urlopen(url) as res:
                        res = json.load(res)
                        if 'results' in res and res['results']:
                            cache.extend(res['results'])
                        else:
                            break
                except:
                    break
            self.docs = cache
