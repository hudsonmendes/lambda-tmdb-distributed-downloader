# IMDB to TMDB, Distributed SQS+Lambda+S3 Downloader

## Summary

**[IMDB](imdb.com)** is arguably the most prolific Cinema database
available on the internet. So common that we find many IMDB related
datasets online, e.g.: [Kaggle's IMDB 5000 Movie Dataset](https://www.kaggle.com/carolzhangdc/imdb-5000-movie-dataset).

### The Problem

**IMDB** provides [snapshots of their databases](https://datasets.imdbws.com/) on titles, casting, etc.
However, they do not provide user reviews. Furthermore, it is against their [Terms of Use](https://help.imdb.com/article/imdb/general-information/can-i-use-imdb-data-in-my-software/G5JTRESSHJBBHTGX?pf_rd_m=A2FGELUUNOQJNL&pf_rd_p=3aefe545-f8d3-4562-976a-e5eb47d1bb18&pf_rd_r=JGP2HXF3JTGQ8PZRRC3E&pf_rd_s=center-1&pf_rd_t=60601&pf_rd_i=interfaces&ref_=fea_mn_lk1#) to do any form of Scraping of their webpages.

### TMDB, an Alternative to IMDB

**[TMDB (The Movie Database)](https://www.themoviedb.org/?language=en-US)** on the other hand, does provide user reviews, [through their API](https://developers.themoviedb.org/3). It is even possible to [search a film by their `imdb_id`](https://developers.themoviedb.org/3/find/find-by-id).

However, if for any reason you must stick to the **IMDB** as your base dataset, and collect information for a good portion of IMDB's 6,782,091 entries, you are doomed.

10% of 6,782,091 would amount for **678,209** API requests, and even though you may not be rate limited, it will still take days.

### Solution

I've then created this script that can be used to download, with good level of paralellism, TMDB movies by their IMDB id.

Apart from the extra data that TMDB makes available (like full release date, for example), we attach the IMDB ID that was found (as `idIMDB`) to the TMDB movie JSON, and save it in S3.

## How to Run

1. Create a SQS queue named: `hudsonmendes-imdb2tmdb-movies-download-queue`, and ensure that the invisibility timeout of messages is set to 15 minutes

2. Create a Lambda function name: `hudsonmendes-imdb2tmdb-movies-download-lambda` and set it's timeout to 50 minutes

3. Ensure that the lambda function's role has permissions to (a) run with SQS and (b) write to s3

4. Enqueue what you want to collect using the following snipet:

```
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
```

## Important

1. This has been coded with the sole purpose of speeding up the process of building a IMDB to TMDB dataset

2. There is a number of coding issues, and this code lacks unit testing.

3. I got little time to maintain it, but contributions would be very welcome.

## Contributions

Whant o help make this better?

1. Send me a Pull Request

2. Ping me on twitter: http://twitter.com/hudsonmendes