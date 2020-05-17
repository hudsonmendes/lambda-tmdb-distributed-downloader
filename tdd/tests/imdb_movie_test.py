from ..pipeline import IMDbMovie


def test_get_initial_from_alpha():
    assert IMDbMovie.get_initial_from('The Heroes of the Universe') == 'TH'


def test_get_initial_from_diacritics():
    assert IMDbMovie.get_initial_from('Àçoures') == 'AC'


def test_get_initial_from_less_than_1():
    assert IMDbMovie.get_initial_from('0') == '0_'


def test_get_initial_from_blank_and_text():
    assert IMDbMovie.get_initial_from(' 0 ') == '0_'
