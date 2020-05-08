import os
import json
from urllib.request import urlopen


def get_tmdb_movies(
        imdb_ids,
        tmdb_api_key):
    """
    Generates a tuple (imdb_id, tmdb_id, tmdb_movie) with each TMDB movie found
    via API by the external IMDB id. The tuple structure is:

    - `imdb_id`   : the IMDB id used in the search
    - `tmdb_id`   : the TMDB id found in the API
    - `tmdb_movie`: the TMDB movie, as a dictionary, representing the JSON returned

    Parameters
    ----------
    - imdb_ids      {list[str]} the list of IMDB movie ids that we will request from the TMDB Api
    - tmdb_api_key  {str}       the TMDB Api Key
    - output_folder {str}       the folder to which we output the downloads; if the file already exists, we skip it
    """
    processed = 0
    total = len(imdb_ids)
    print(f'[imdb 2 tmdb] starting: {total} in total')
    for imdb_id in imdb_ids:

        tmdb_movie = get_tmdb_movie(
            imdb_id=imdb_id,
            tmdb_api_key=tmdb_api_key)

        if tmdb_movie:
            tmdb_id = tmdb_movie['id']
            yield imdb_id, tmdb_id, tmdb_movie

        processed += 1
        if processed % 100 == 0:
            print(f'[imdb 2 tmdb] processed {processed}/{total} movies')
    print(f'[imdb 2 tmdb] completed: {processed}/{total} movies')

def get_tmdb_movie(
        imdb_id,
        tmdb_api_key):
    """
    Fetches a TMDB movie from the TMDB API by imdb_id, using the api_key.
    We append the `idIMDB` to the original json, so that later we can perform some level of batch mapping.

    Parameters
    ----------
    - imdb_id      {str} the IMDB id used in the search
    - tmdb_api_key {str} the TMDB Api Key used in the search
    """
    source_url = f'https://api.themoviedb.org/3/find/{imdb_id}?api_key={tmdb_api_key}&language=en-US&external_source=imdb_id'
    with urlopen(source_url) as res:

        tmdb_movies = json.loads(res.read())
        tmdb_movie = next(iter(tmdb_movies['movie_results']), None)
        if tmdb_movie:
            tmdb_movie['idIMDB'] = imdb_id

        return tmdb_movie
