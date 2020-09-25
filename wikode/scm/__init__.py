
import os
import subprocess

from wikode.config import Config


class Factory(object):

    @staticmethod
    def is_selected():
        return Config.get(Config.KEYS.SCM_TYPE) != Config.get_default(Config.KEYS.SCM_TYPE)

    @staticmethod
    def get_scm():
        return Fake()

    @staticmethod
    def initialise():
        if Factory.is_selected():
            print("SCM SELECTED")
        else:
            print("SCM NOT SELECTED")

        # Initialise data dir if it doens't exist
        data_dir = Config.get(Config.KEYS.DATA_DIR)
        if not os.path.isdir(data_dir):
            os.mkdir(data_dir)

        if Factory.is_selected():
            scm = Factory.get_scm()
            if scm.is_setup():
                scm.sync()
            else:
                print('SCM is selected but not setup')


class Base(object):

    @property
    def base_dir(self):
        return Config.get(Config.KEYS.DATA_DIR)
    
    def setup(self):
        raise NotImplementedError()

    def sync(self):
        raise NotImplementedError()

    def commit(self, wiki_obj):
        raise NotImplementedError()

    def is_setup(self):
        raise NotImplementedError

    def run_command(self, cmds):
        subprocess.Popen(cmds, cwd=self.base_dir)
        return 


class Fake(Base):

    def setup(self):
        pass

    def sync(self):
        pass

    def commit(self, wiki_obj):
        pass

    def is_setup(self):
        return True


class SVN(Base):

    def is_setup(self):
        return os.path.isdir(os.path.join(Config.get(Config.KEYS.DATA_DIR), '.svn'))

    def setup(self):
        pass

    def sync(self):
        subprocess.Popen('svn ')

    def commit(self, wiki_obj):
        pass

    def is_setup(self):
        return True
