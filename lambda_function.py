import os
import json
from tdd import Config, IMDb, TMDb


def lambda_handler(event, context):
    """
    Downloads 'movies' for a particular {year}, with names that
    start with a particular {initial} character

    Parameters
    ----------
    - event  : 'Records' have the messages received from SQS (full body)
    - context: lambda context wrapper

    Message Body
    ------------
    - year   : the year for which movies will be downloaded
    - initial: the first non-blank character of the name of the movie
    """

    config = Config()

    imdb = IMDb(
        bucket_name=config.get_datalake_bucket_name())

    tmdb = TMDb(
        bucket_name=config.get_datalake_bucket_name(),
        api_key=config.get_tmdb_api_key())

    for record in event['Records']:

        body = json.loads(record['body'])

        year = int(body['year'])

        initial = body['initial']

        imdb_movie_refs = imdb.get_movie_refs_stream(
            year=year,
            initial=initial)

        tmdb_movie_and_reviews_generator = tmdb.get_movies_related_to(
            imdb_movie_ref_stream=imdb_movie_refs)

        for tmdb_movie, tmdb_reviews in tmdb_movie_and_reviews_generator:
            tmdb_movie.save()
            for tmdb_review in tmdb_reviews:
                tmdb_review.save()

    return {
        'statusCode': 200,
        'body': json.dumps(body)
    }
