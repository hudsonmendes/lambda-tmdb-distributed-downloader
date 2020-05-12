import os
import json
import tdd


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

    files = []
    for record in event['Records']:

        body = json.loads(record['body'])

        year = int(body['year'])

        initial = body['initial']

        tmdb_api_key = os.environ['TMDB_API_KEY']

        imdb_ids = tdd.imdb.movies.get_ids(
            year=year,
            initial=initial)

        tmdb_movies = tdd.tmdb.movies.get_by(
            imdb_ids=imdb_ids,
            api_key=tmdb_api_key)

        for tmdb_movie in tmdb_movies:
            
            tdd.tmdb.movies.export(tmdb_movie)
            
            tmdb_reviews = tdd.tmdb.reviews.get_by(
                tmdb_id=tmdb_movie['id'],
                api_key=tmdb_api_key)

            for tmdb_review in tmdb_reviews:
                tdd.tmdb.reviews.export(tmdb_review)

    return {
        'statusCode': 200,
        'body': json.dumps(files)
    }
