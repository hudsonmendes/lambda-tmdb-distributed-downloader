import os
import json
import click


@click.group()
def cli():
    """
    Command line group, allowing us to run `python tdd` commands
    in the root folder of this repository.
    """
    pass


@cli.command()
@click.option('--datalake_bucket_name', prompt='DataLake, Bucket Name', help='The S3 BucketName to which you will dump your files', default='hudsonmendes-datalake')
@click.option('--tmdb_api_key', prompt='TMDB, API Key', help='Find it in https://www.themoviedb.org/settings/api', default=lambda: os.environ.get('TMDB_API_KEY', None))
def development(datalake_bucket_name: str, tmdb_api_key: str):
    """
    Setup the development environment locally, with the required configuration.
    `python tdd development --datalake_bucket_name [bucket_name] --tmdb_api_key [api_key]`
    """
    from config import Config
    Config().update(
        datalake_bucket_name=datalake_bucket_name,
        tmdb_api_key=tmdb_api_key)


@cli.command()
@click.option('--year', prompt='IMDB, Year', default=2000, help='Year of movies that will be downloaded')
@click.option('--initial', prompt='IMDB, Initial', default='A', help='First letter of the films that will be downloaded')
@click.option('--queue_name', prompt='AWS SQS, Queue', default='hudsonmendes-tmdb-downloader-queue', help='The name of the queue to which we will send the message')
def simulate(year: int, initial: str, queue_name: str):
    """
    Simulates the system by sending a one-off message to the SQS queue,
    so that the Lambda Function can pick it up and we can evaluate that
    the whole system is functioning.
    """
    import boto3
    messages = [{'year': year, 'initial': initial}]
    sqs = boto3.resource('sqs')
    queue = sqs.get_queue_by_name(QueueName=queue_name)
    for message in messages:
        body = json.dumps(message)
        queue.send_message(MessageBody=body)


@cli.command()
@click.option('--year', prompt='IMDB, Year', default=2000, help='Year of movies that will be downloaded')
@click.option('--initial', prompt='IMDB, Initial', default='A', help='First letter of the films that will be downloaded')
def download(year: int, initial: str):
    """
    Invokes the lambda_function manually for a one-off download.
    Can be used for debug purposes
    """
    import lambda_function
    event = {'Records': [{'body': json.dumps({'year': year, 'initial': initial})}]}
    lambda_function.lambda_handler(event=event, context=None)


@cli.command()
@click.option('--lambda_name', prompt='AWS Lambda, Function Name', default='hudsonmendes-tmdb-downloader-lambda', help='The name of the function to which we will deploy')
@click.option('--queue_name', prompt='AWS SQS, Queue', default='hudsonmendes-tmdb-downloader-queue', help='The name of the queue to which we will send the message')
@click.option('--datalake_bucket_name', prompt='DataLake, Bucket Name', help='The S3 BucketName to which you will dump your files', default='hudsonmendes-datalake')
def deploy(lambda_name, queue_name, datalake_bucket_name):
    """
    Deploy the system into lambda, creating everything that is necessary to run.
    """
    from deploy import Deploy
    Deploy(
        lambda_name=lambda_name,
        queue_name=queue_name,
        datalake_bucket_name=datalake_bucket_name).deploy()


if __name__ == "__main__":
    cli()
