import json
from urllib.request import urlopen

class TMDbMovie:
    URL_TMPL = 'https://api.themoviedb.org/3/find/{imdb_id}?api_key={api_key}&language=en-US&external_source=imdb_id'

    """
    Wraps the request to the TMDBMovie resource.
    """

    def __init__(self, imdb_id, api_key, **kwargs):
        self.imdb_id = imdb_id
        self.url = TMDbMovie.URL_TMPL.format(imdb_id=imdb_id, api_key=api_key)
        self.cache = None

    def get_document(self):
        """
        Gets the JSON document lazily, and caches it for future use.
        """
        if not self.cache:
            with urlopen(self.url) as res:
                doc = json.load(res)
                if 'movie_results' in doc:
                    doc = next(iter(doc['movie_results']), None)
                    if doc:
                        doc['id_imdb'] = self.imdb_id
                        self.cache = doc
        return self.cache

    def get_id(self):
        """
        Reads the movie_id from the cached document
        """
        return self.cache['id']