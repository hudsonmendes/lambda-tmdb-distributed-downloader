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

## Components & Resources

This solution is composed by the following components:

1. AWS SQS Queue that will receive all the requests to trigger the TMDB data download

2. AWS Lambda Function that will consume the messages from SQS and perform the download

3. AWS S3 Bucket, required for dumping the downloaded data

3. **Fleet Launcher Jupyter Notebook**, that will prepare the messages ans send to SQS

## Small "CLI" (Command Line INterface)

The current code also has a small command line that helps us with what is needed in order to develop and run this program:

1. **`python tdd development`:** creates the local `config.ini` that is reponsible for keeping your TMDB api key and your data lake bucket name

2. **`python tdd deploy`:** installs the AWS infrastructure automatically interactively for you

3. **`python tdd download:`** launches the downloader locally, downloads a single item, ideal for debugging

3. **`python tdd simulate:`** send the message to SQS to download one single partition, ideal to test the system in AWS.

## How to Run

### Setup Development Environment

1. Clone the repository locally, and

2. Setup your development environment: you will be prompted for information such as your `TMDB_API_KEY` and your `S3_BUCKET_NAME` (for your datalake)

```
cd ~/[workspace_path]
git clone git@github.com:hudsonmendes/lambda-tmdb-distributed-downloader.git
cd lambda-tmdb-distributed-downloader
python tdd development
```

### Deploy the lambda to your AWS account

**Important:** this step requires you to have your `aws configure` run previously.

1. Run the deployment code,

2. Tell where you want the system to be deployed (parameters), and

3. Check to see if the resources were properly created

```
# you must be connected to your amazon account
# aws configure

# here we will deploy the components to lambda
python tdd deploy
```

## Contributions

Whant o help make this better?

1. Send me a Pull Request

2. Ping me on twitter: http://twitter.com/hudsonmendes