
import os
import shutil
import subprocess
import tempfile
import glob

from wikode.config import Config


class Factory(object):

    @staticmethod
    def is_selected():
        return Config().scm_type != Config.get_default(Config.KEYS.SCM_TYPE)

    @staticmethod
    def get_scm():
        if Config().scm_type == 'SVN':
            return SVN()
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
            if scm.is_setup() and Config.get(Config.KEYS.SCM_SYNC_ON_START):
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
        """Has the initial setup already been done."""
        raise NotImplementedError

    def can_setup(self):
        """Can the inital setup be done."""
        raise NotImplementedError

    def run_command(self, cmds, exception_on_error=True, cwd=None, shell=False):
        if cwd is None:
            cwd = self.base_dir

        p = subprocess.Popen(
            cmds,
            cwd=cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=shell)

        rc = p.wait()

        stdout = p.stdout.read().decode(
            'utf8', errors='backslashreplace').replace('\r', '')
        stderr = p.stderr.read().decode(
            'utf8', errors='backslashreplace').replace('\r', '')

        if rc and exception_on_error:
            raise Exception('Systemc command error: {0}\n{1}\n{2}'.format(cmds, rc, stdout + stderr))

        return rc, stdout, stderr


class Fake(Base):

    def setup(self):
        pass

    def sync(self):
        pass

    def commit(self, wiki_obj):
        pass

    def is_setup(self):
        return True

    def can_setup(self):
        return True


class SVN(Base):

    def is_setup(self):
        return os.path.isdir(os.path.join(Config.get(Config.KEYS.DATA_DIR), '.svn'))

    def can_setup(self):
        rc, _, _ = self.run_command(['which', 'svn'], exception_on_error=False)
        return Config().scm_url and not rc

    def get_auth_args(self):
        if Config().scm_username and Config().scm_password:
            return ['--username', Config().scm_username,
                    '--password', Config().scm_password,
                    '--no-auth-cache']
        return []

    def setup(self):
        """Setup SVN repo in data directory."""
        # Clone to temporary location
        temp_dir = tempfile.mkdtemp()
        print('TEMP DI:' + temp_dir)

        cmds = [
            'svn', 'checkout',
            '--non-interactive',
            Config().scm_url, temp_dir
        ]

        cmds += self.get_auth_args()

        self.run_command(cmds, cwd=temp_dir)

        # Copy files from data directory into temporary SCM directory
        # Can't use glob in system command, since it's a bashism.
        # shutil is a pain and requires name of destination to be specified.
        for s_file in [n.name for n in os.scandir(Config.get(Config.KEYS.DATA_DIR))]:
            self.run_command(
                ['cp', '-r', s_file, temp_dir + '/'],
                cwd=os.path.join(Config.get(Config.KEYS.DATA_DIR))
            )
            self.run_command(
                ['svn', 'add', s_file],
                cwd=temp_dir
            )

        cmds = ['svn', 'commit', '--message', 'Add inital data files from Wikode']
        cmds += self.get_auth_args()
        self.run_command(cmds, cwd=temp_dir)

        # Replace data directory with temp directory
        shutil.rmtree(Config.get(Config.KEYS.DATA_DIR), ignore_errors=False, onerror=None)
        shutil.move(temp_dir, Config.get(Config.KEYS.DATA_DIR))

    def sync(self):
        cmds = ['svn', 'update']
        cmds += self.get_auth_args()
        self.run_command(cmds)

    def commit(self, wiki_obj):

        if wiki_obj.created:
            file_path = wiki_obj.RE_DATA_PREFIX.sub(
                '',
                wiki_obj.file_path
            )
            if file_path.startswith('/'):
                file_path = file_path[1:]
            print("file to add: {0}", file_path)

            cmds = ['svn', 'add', '--parents', file_path]
            self.run_command(cmds)

        cmds = ['svn', 'commit', '-m', 'Add/updated file {0}'.format(wiki_obj.url_struct)]
        cmds += self.get_auth_args()
        self.run_command(cmds)
