import os
import json
import getpass
import lambda_function

if __name__ == "__main__":
    tmdb_api_key = None
    if 'TMDB_API_KEY' in os.environ and os.environ['TMDB_API_KEY']:
        tmdb_api_key = os.environ['TMDB_API_KEY']
    else:
        tmdb_api_key = getpass.getpass('TMDB API Key: ')
        os.environ['TMDB_API_KEY'] = tmdb_api_key

    event = {
        'Records': [
            { 'body': json.dumps({ 'year': 2000, 'initial': 'A' }) },
            { 'body': json.dumps({ 'year': 2000, 'initial': 'B' }) },
            { 'body': json.dumps({ 'year': 2000, 'initial': 'C' }) }
        ]
    }
    lambda_function.lambda_handler(
        event=event,
        context=None)