import os
import configparser

class Config:
    """
    Manages the secrets required to run the app in
    development, test or production mode
    """

    def __init__(
            self,
            config_path:str = 'config.ini',
            **kwargs):
        self.config = configparser.ConfigParser()
        self.config_path = config_path
        self.config.read(config_path)

    def get_datalake_bucket_name(self):
        """
        Returns the [DATALAKE] BUCKET_NAME available prioritarily
        in the os.environ context; otherwise it returns from the
        `config.ini` file.
        """
        if 'DATALAKE_BUCKET_NAME' in os.environ:
            return os.environ['DATALAKE_BUCKET_NAME']
        else:
            return self.config['DATALAKE'].get('BUCKET_NAME')

    def get_tmdb_api_key(self):
        """
        Returns the [TMDB] API_KEY available prioritarily in the
        os.environ context; otherwise it returns from the
        `config.ini` file.
        """
        if 'TMDB_API_KEY' in os.environ:
            return os.environ['TMDB_API_KEY']
        else:
            return self.config['TMDB'].get('API_KEY')
    
    def update(
            self,
            datalake_bucket_name: str,
            tmdb_api_key: str):
        """
        Updates the config and writes the config to `config_path`
        """
        if 'DATALAKE' not in self.config:
            self.config.add_section('DATALAKE')
        if 'TMDB' not in self.config:
            self.config.add_section('TMDB')
        self.config.set('DATALAKE', 'BUCKET_NAME', datalake_bucket_name)
        self.config.set('TMDB', 'API_KEY', tmdb_api_key)
        self.config.write(open(self.config_path, 'w+'))