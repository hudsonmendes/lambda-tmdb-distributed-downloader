from typing import Iterable
from .imdb_movie import IMDbMovie
from .tmdb_movie import TMDbMovie


class TMDb:
    """
    Facilitates persistence of movies and reviews into S3,
    using the path and file name standard chosen for the task.
    """

    def __init__(self, api_key, **kwargs):
        self.api_key = api_key

    def get_movies_related_to(self, imdb_movie_ref_stream: Iterable[IMDbMovie]):
        """
        Iterates through the stream, requesting the TMDb Movie
        and all its pages of reviews, and yields both the movie
        and the reviews, so that they can be persisted
        """
        for imdb_movie_ref in imdb_movie_ref_stream:
            tmdb_movie = self.get_movie_by(imdb_id=imdb_movie_ref)
            tmdb_movie_reviews = self.get_reviews_by(movie_id=tmdb_movie['id'])
            yield tmdb_movie, tmdb_movie_reviews

    def get_movie_by(self, imdb_id):
        return TMDbMovie(imdb_id, self.api_key)

    def get_reviews_by(self, movie_id):
        return None
