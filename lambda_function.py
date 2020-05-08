import os
import json
import imdb2tmdb


def lambda_handler(event, context):
    """
    Downloads 'movies' for a particular {year}, with names that
    start with a particular {initial} character

    Parameters
    ----------
    - event  : 'Records' have the messages received from SQS (full body)
    - context: lambda context wrapper

    QueryString Parameters
    ----------------------
    - year   : the year for which movies will be downloaded
    - initial: the first non-blank character of the name of the movie
    """

    files = []
    for record in event['Records']:

        body = json.loads(record['body'])

        year = int(body['year'])

        initial = body['initial']

        imdb_ids = imdb2tmdb.imdb.get_imdb_ids(year=year, initial=initial)

        tmdb_movies_generator = imdb2tmdb.tmdb.get_tmdb_movies(
            imdb_ids=imdb_ids,
            tmdb_api_key=os.environ['TMDB_API_KEY'])

        files.extend([
            imdb2tmdb.s3.save(year, initial, imdb_id, tmdb_id, tmdb_movie)
            for imdb_id, tmdb_id, tmdb_movie
            in tmdb_movies_generator])

    return {
        'statusCode': 200,
        'body': json.dumps(files)
    }
