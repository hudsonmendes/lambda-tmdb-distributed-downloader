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

    def get_id(self) -> str:
        return self.id

    def get_title(self) -> str:
        return self.title

    def get_year(self) -> int:
        return self.year

    def get_initial(self) -> str:
        return self.initial

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
            initial = initial.strip().upper()
            if len(initial) < 2:
                missing_len = 2 - len(initial)
                initial += ''.join(['_'] * missing_len)
            initial = initial[0:2]
        return initial
