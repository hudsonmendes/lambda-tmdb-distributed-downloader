import json
import boto3

if __name__ == "__main__":
    messages = [
        { 'year'   : 2000, 'initial': 'A' },
    ]
    sqs = boto3.resource('sqs')
    queue = sqs.get_queue_by_name(QueueName='hudsonmendes-imdb2tmdb-movies-download-queue')
    for message in messages:
        body = json.dumps(message)
        queue.send_message(MessageBody=body)