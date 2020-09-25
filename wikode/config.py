

from enum import Enum
import json
import os


class Config(object):

    CONFIG_PATH = './config.json'
    CONFIG_CACHE = None

    class KEYS(Enum):
        SCM_TYPE = 'SCM_TYPE'
        DATA_DIR = 'DATA_DIR'
        SQLITE_PATH = 'SQLITE_PATH'

    DEFAULTS = {
        KEYS.SCM_TYPE: None,
        KEYS.DATA_DIR: './data',
        KEYS.SQLITE_PATH: './db.sqlite'
    }

    @staticmethod
    def load_config():
        if os.path.isfile(Config.CONFIG_PATH):
            try:
                with open(Config.CONFIG_PATH, 'r') as fh:
                    return json.loads(fh.read())
            except Exception as exc:
                print('WARNING: Unable to load config: {0}'.format(str(exc)))
        else:
            print('INFO: config.json does not exist - using defaults')
        return {}

    @staticmethod
    def get_config():
        if Config.CONFIG_CACHE is None:
            Config.CONFIG_CACHE = Config.load_config()
        return Config.CONFIG_CACHE

    @staticmethod
    def get(config_name):
        if config_name.value in Config.get_config():
            return Config.get_config()[config_name.value]
        return Config.DEFAULTS[config_name]

    @staticmethod
    def get_default(config_name):
        return Config.DEFAULTS[config_name]
