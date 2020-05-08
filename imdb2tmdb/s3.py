import os
import boto3
import json

S3_BUCKET = 'hudsonmendes-imdb2tmdb'
S3_FOLDER = 'tmdb-movies'
S3_CLIENT = boto3.client('s3')


def save(
        year,
        initial,
        imdb_id,
        tmdb_id,
        tmdb_movie):
    file_name = f'year-{year}/initial-{initial}/movie-tmdb-{tmdb_id}-imdb-{imdb_id}.json'
    file_key = os.path.join(S3_FOLDER, file_name)
    file_body = json.dumps(tmdb_movie).encode('utf-8')
    S3_CLIENT.put_object(Body=file_body, Bucket=S3_BUCKET, Key=file_key)
    return os.path.join(f's3://{S3_BUCKET}/{file_key}')
