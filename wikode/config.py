

from enum import Enum
import json
import os


class Config(object):
    """Interface to provide obtaining config values."""

    CONFIG_PATH = './config.json'
    CONFIG_CACHE = None

    class KEYS(Enum):  # pylint: disable=R0903
        """Enum of config key lookup values"""
        SCM_TYPE = 'SCM_TYPE'
        SCM_URL = 'SCM_URL'
        SCM_USERNAME = 'SCM_USERNAME'
        SCM_PASSWORD = 'SCM_PASSWORD'
        SCM_SYNC_ON_START = 'SCM_SYNC_ON_START'

        DATA_DIR = 'DATA_DIR'
        SQLITE_PATH = 'SQLITE_PATH'
        LISTEN_HOST = 'LISTEN_HOST'
        LISTEN_PORT = 'LISTEN_PORT'

    # Default config values
    DEFAULTS = {
        KEYS.SCM_TYPE: None,
        KEYS.SCM_URL: None,
        KEYS.SCM_USERNAME: None,
        KEYS.SCM_PASSWORD: None,
        KEYS.SCM_SYNC_ON_START: True,

        KEYS.DATA_DIR: './data',
        KEYS.SQLITE_PATH: './db.sqlite',
        KEYS.LISTEN_HOST: '127.0.0.1',
        KEYS.LISTEN_PORT: 5000
    }

    @staticmethod
    def load_config():
        """Load config overrides from file."""
        if os.path.isfile(Config.CONFIG_PATH):
            try:
                with open(Config.CONFIG_PATH, 'r') as config_fh:
                    return json.loads(config_fh.read())
            except Exception as exc:
                print('WARNING: Unable to load config: {0}'.format(str(exc)))
        else:
            print('INFO: config.json does not exist - using defaults')
        return {}

    @staticmethod
    def get_config():
        """Return config from file and cache."""
        if Config.CONFIG_CACHE is None:
            Config.CONFIG_CACHE = Config.load_config()
        return Config.CONFIG_CACHE

    @staticmethod
    def get(config_name):
        """Obtain value for config key, either from config file or default."""
        if config_name.value in Config.get_config():
            return Config.get_config()[config_name.value]
        return Config.DEFAULTS[config_name]

    @staticmethod
    def get_default(config_name):
        """Return default config value for given config key."""
        return Config.DEFAULTS[config_name]

    @property
    def scm_type(self):
        """Property to obtain SCM Type config."""
        return self.get(Config.KEYS.SCM_TYPE)

    @property
    def scm_url(self):
        """Property to obtain SCM URL config."""
        return self.get(Config.KEYS.SCM_URL)

    @property
    def scm_username(self):
        """Property to obtain SCM Type config."""
        return self.get(Config.KEYS.SCM_USERNAME)

    @property
    def scm_password(self):
        """Property to obtain SCM URL config."""
        return self.get(Config.KEYS.SCM_PASSWORD)


