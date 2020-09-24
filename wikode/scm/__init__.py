
import os

from wikode.config import Config


class SCM(object):

    @staticmethod
    def is_initialised():
        return Config.get(Config.KEYS.SCM_TYPE) != Config.get_default(Config.KEYS.SCM_TYPE)

    @staticmethod
    def Initialise():
        if SCM.is_initialised():
            print("SCM SET")
        else:
            print("SCM NOT SELECTED")

        # Initialise data dir if it doens't exist
        data_dir = Config.get(Config.KEYS.DATA_DIR)
        if not os.path.isdir(data_dir):
            os.mkdir(data_dir)
