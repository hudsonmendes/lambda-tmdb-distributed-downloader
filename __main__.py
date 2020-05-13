import os
import json
import click


@click.group()
def cli():
    pass


@cli.command()
@click.option(
    '--datalake_bucket_name',
    prompt='DataLake, Bucket Name',
    help='The S3 BucketName to which you will dump your files',
    default='hudsonmendes-datalake')
@click.option(
    '--tmdb_api_key',
    prompt='TMDB, API Key',
    help='Find it in https://www.themoviedb.org/settings/api',
    default=lambda: os.environ.get('TMDB_API_KEY', None))
def setup(
        datalake_bucket_name: str,
        tmdb_api_key: str):
    from tdd import Config
    Config().update(
        datalake_bucket_name=datalake_bucket_name,
        tmdb_api_key=tmdb_api_key)


@cli.command()
@click.option('--year', prompt='IMDB, Year', default=2000, help='Year of movies that will be downloaded')
@click.option('--initial', prompt='IMDB, Initial', default='A', help='First letter of the films that will be downloaded')
@click.option('--queue', prompt='AWS SQS, Queue', default='hudsonmendes-tmdb-downloader-queue', help='The name of the queue to which we will send the message')
def simulate(year: int, initial: str, queue: str):
    import boto3
    messages = [{'year': year, 'initial': initial}]
    sqs = boto3.resource('sqs')
    queue = sqs.get_queue_by_name(QueueName=queue)
    for message in messages:
        body = json.dumps(message)
        queue.send_message(MessageBody=body)


@cli.command()
@click.option('--year', prompt='IMDB, Year', default=2000, help='Year of movies that will be downloaded')
@click.option('--initial', prompt='IMDB, Initial', default='A', help='First letter of the films that will be downloaded')
def download(year: int, initial: str):
    import lambda_function
    event = {'Records': [{'body': json.dumps({'year': year, 'initial': initial})}]}
    lambda_function.lambda_handler(event=event, context=None)


@cli.command()
@click.option('--lambda-name', prompt='AWS Lambda, Function Name', default='hudsonmendes-tmdb-downloader-lambda', help='The name of the function to which we will deploy')
def deploy(lambda_name):
    from tdd import Deploy
    Deploy(lambda_name).deploy()


if __name__ == "__main__":
    cli()
