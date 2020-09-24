
import os

from wikode.config import Config


class Factory(object):

    @staticmethod
    def is_initialised():
        return Config.get(Config.KEYS.SCM_TYPE) != Config.get_default(Config.KEYS.SCM_TYPE)

    @staticmethod
    def get_scm():
        return Fake()

    @staticmethod
    def initialise():
        if Factory.is_initialised():
            print("SCM SET")
        else:
            print("SCM NOT SELECTED")

        # Initialise data dir if it doens't exist
        data_dir = Config.get(Config.KEYS.DATA_DIR)
        if not os.path.isdir(data_dir):
            os.mkdir(data_dir)


class Base(object):

    def setup(self):
        raise NotImplementedError()

    def sync(self):
        raise NotImplementedError()

    def commit(self, wiki_obj):
        raise NotImplementedError()


class Fake(Base):

    def setup(self):
        pass

    def sync(self):
        pass

    def commit(self, wiki_obj):
        pass
