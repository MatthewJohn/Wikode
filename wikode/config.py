

from enum import Enum


class Config(object):

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
    def get(config_name):
        return Config.DEFAULTS[config_name]

    @staticmethod
    def get_default(config_name):
        return Config.DEFAULTS[config_name]

