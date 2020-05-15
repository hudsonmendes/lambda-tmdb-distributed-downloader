from typing import Iterable, Tuple, List
from .imdb_movie import IMDbMovie
from .tmdb_movie import TMDbMovie
from .tmdb_reviews import TMDbReviews


class TMDb:
    """
    Facilitates persistence of movies and reviews into S3,
    using the path and file name standard chosen for the task.
    """

    def __init__(
            self,
            bucket_name: str,
            api_key: str,
            **kwargs):
        self.bucket_name = bucket_name
        self.api_key = api_key

    def get_movies_related_to(
            self,
            imdb_movies_stream: Iterable[IMDbMovie]) -> Iterable[Tuple[TMDbMovie, TMDbReviews]]:
        """
        Iterates through the stream, requesting the TMDb Movie
        and all its pages of reviews, and yields both the movie
        and the reviews, so that they can be persisted
        """
        processed = 0
        for imdb_movie in imdb_movies_stream:
            
            tmdb_movie = self.get_movie_by(imdb_movie=imdb_movie)
            if tmdb_movie.has_been_found():
                
                tmdb_movie_reviews = self.get_reviews_by(imdb_movie=imdb_movie, tmdb_movie=tmdb_movie)
                yield tmdb_movie, tmdb_movie_reviews

            processed += 1
            if processed % 100 == 0:
                print(f'[TMDb] processed {processed}')

    def get_movie_by(self, imdb_movie):
        return TMDbMovie(
            year=imdb_movie.year,
            initial=imdb_movie.initial,
            imdb_id=imdb_movie.get_id(),
            bucket_name=self.bucket_name,
            api_key=self.api_key)

    def get_reviews_by(self, imdb_movie, tmdb_movie):
        return TMDbReviews(
            year=imdb_movie.year,
            initial=imdb_movie.initial,
            movie_id=tmdb_movie.get_id(),
            bucket_name=self.bucket_name,
            api_key=self.api_key)
