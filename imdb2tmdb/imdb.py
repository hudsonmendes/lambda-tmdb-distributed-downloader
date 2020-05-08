import os
import io
import csv
import codecs
import unidecode
import string
import gzip
from urllib.request import urlopen

IMDB_MOVIES_URL = 'https://datasets.imdbws.com/title.basics.tsv.gz'


def get_imdb_ids(year,  initial):
    imdb_ids = []
    year = str(year)
    with urlopen(IMDB_MOVIES_URL) as f_gz:
        with gzip.open(f_gz) as f_in:
            csv_reader = csv.reader(codecs.iterdecode(f_in, 'utf-8'), delimiter='\t')
            header = next(csv_reader)
            ix_id = header.index('tconst')
            ix_title = header.index('primaryTitle')
            ix_year = header.index('startYear')
            for row in csv_reader:
                if initial == get_initial_from(row[ix_title]) and year == row[ix_year]:
                    imdb_ids.append(row[ix_id])
    return imdb_ids

def get_initial_from(x):
    initial = str(x)
    initial = unidecode.unidecode(initial)
    initial = initial.translate(str.maketrans('', '', string.punctuation))
    if initial:
        initial = initial[0].strip().upper()
    return initial