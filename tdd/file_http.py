from urllib.parse import urlparse
from urllib.request import urlopen


class FileHttp:
    """
    Wrapper for file provided via HTTP, with access
    to file size and streaming of the file content.
    """

    def __init__(self, url: str, **kwargs):
        self.url = url
        assert self.url.startswith('http')

    def get_size(self):
        with urlopen(self.url) as res:
            return int(res.headers.get('Content-Length', 0))

    def stream(self):
        return urlopen(self.url)
