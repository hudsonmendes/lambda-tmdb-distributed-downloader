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

    def get_tmdb_api_key(self):
        """
        Returns the [TMDB]API_KEY available in the config.ini file.
        """
        return self.config['TMDB'].get('API_KEY')
    
    def set_tmdb_api_key(self, tmdb_api_key: str):
        """
        Updates the config and writes the config to `config_path`
        """
        self.config['TMDB'].update({'API_KEY': tmdb_api_key})
        self.config.write(open(self.config_path, 'w+'))