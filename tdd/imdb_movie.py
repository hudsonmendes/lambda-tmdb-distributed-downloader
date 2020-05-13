from typing import List
import unidecode
import string

class IMDbMovie:
    HEADER_ID = 'tconst'
    HEADER_TITLE = 'primaryTitle'
    HEADER_YEAR = 'startYear'

    """
    Wraps the Movie File, simplfying advanced parsing of the information
    """

    def __init__(
            self,
            header: List[str],
            row: List[str],
            **kwargs):
        ix_id = header.index(IMDbMovie.HEADER_ID)
        ix_title = header.index(IMDbMovie.HEADER_TITLE)
        ix_year = header.index(IMDbMovie.HEADER_YEAR)
        self.id = row[ix_id]
        self.title = row[ix_title]
        self.year = IMDbMovie.get_year_from(row[ix_year])
        self.initial = IMDbMovie.get_initial_from(self.title)

    @staticmethod
    def get_year_from(x):
        try:
            return int(x)
        except:
            return None

    @staticmethod
    def get_initial_from(x):
        initial = str(x)
        initial = unidecode.unidecode(initial)
        initial = initial.translate(str.maketrans('', '', string.punctuation))
        if initial:
            initial = initial[0].strip().upper()
        return initial
