import os
import json
from pipeline import IMDb, TMDb
from infra import Config


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

        print(f'Lambda, processsing partition ({year}, {initial})')

        imdb_movies_stream = imdb.get_movie_refs_stream(
            year=year,
            initial=initial)

        tmdb_movie_and_reviews_generator = tmdb.get_movies_related_to(
            imdb_movies_stream=imdb_movies_stream)

        processed_count = 0
        for tmdb_movie, tmdb_reviews in tmdb_movie_and_reviews_generator:
            tmdb_movie.save()
            tmdb_reviews.save()
            processed_count += 1

        print(f'Lambda, completed processing {processed_count}')

    return {
        'statusCode': 200,
        'body': json.dumps(body)
    }
