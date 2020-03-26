from jenkins import Jenkins, JenkinsError, NodeLaunchMethod
import os
import signal
import sys
import urllib
import subprocess
import shutil
import requests
import time
import os

class Settings(object):
    """Jenkins settings for master and slave nodes."""

    _user_name         = 'admin'
    _user_password     = 'admin'
    _slave_secret      = None
    _master_url        = 'http://jenkins'
    _master_resource   = '/jnlpJars/slave.jar'
    _slave_url         = None
    _slave_name        = None
    _slave_jar_file    = '/var/lib/jenkins/slave.jar'
    _slave_executors   = 1
    _slave_labels      = 'docker'
    _slave_working_dir = None
    _clean_working_dir = True

    def __init__(self, config: dict):
        if 'USER_NAME' in config and config['USER_NAME'] and 'USER_PASSWORD' in config and config['USER_PASSWORD']:
            self._user_name = config['USER_NAME']
            self._user_password = config['USER_PASSWORD']
        elif 'SLAVE_SECRET' in config and config['SLAVE_SECRET']:
            self._slave_secret = config['SLAVE_SECRET']
        else:
            raise Exception('SLAVE_SECRET or USER_NAME and USER_PASSWORD must be defined in environment settings.')

        if 'MASTER_URL' in config and config['MASTER_URL']:
            self._master_url = config['MASTER_URL']
        else:
            raise Exception('MASTER_URL must be defined in environment settings.')

        if 'SLAVE_URL' in config:
            self._slave_url = config['SLAVE_URL']
        else:
            raise Exception('SLAVE_URL must be defined in environment settings.')
        
        if 'SLAVE_NAME' in config and config['SLAVE_NAME']:
            self._slave_name = config['SLAVE_NAME']
        elif 'HOSTNAME' in config and config['HOSTNAME']:
            self._slave_name = 'docker-slave-%s' % config['HOSTNAME']
        else:
            raise Exception('SLAVE_NAME or HOSTNAME must be defined in environment settings.')

        if 'SLAVE_EXECUTORS' in config:
            self._slave_executors = int(config['SLAVE_EXECUTORS'])
        else:
            raise Exception('SLAVE_EXECUTORS must be defined in environment settings.')

        if 'SLAVE_LABELS' in config and config['SLAVE_LABELS']:
            self._slave_labels = config['SLAVE_LABELS']
        else:
            raise Exception('SLAVE_LABELS must be defined in environment settings.')

        if 'SLAVE_WORKING_DIR' in config and os.path.isdir(config['CLEAN_WORKING_DIR']):
            self._slave_working_dir = config['SLAVE_WORKING_DIR']
        else:
            self._slave_working_dir = os.getcwd()

        if 'CLEAN_WORKING_DIR' in config:
            self._clean_working_dir = config['CLEAN_WORKING_DIR']
        else:
            raise Exception('CLEAN_WORKING_DIR must be defined in environment settings.')

    @property
    def master_url(self) -> str:
        """Server url of master node."""
        return self._master_url

    @master_url.setter
    def master_url(self, value: str) -> None:
        self._master_url = value

    @property
    def master_resource(self) -> str:
        """Resource where slave jar file located."""
        return self._master_resource

    @master_resource.setter
    def master_resource(self, value: str) -> None:
        self._master_resource = value

    @property
    def slave_url(self) -> str:
        """Url of slave node."""
        return self._slave_url

    @slave_url.setter
    def slave_url(self, value: str) -> None:
        self._slave_url = value

    @property
    def user_name(self) -> str:
        """Name of user used to start slave node."""
        return self._user_name

    @user_name.setter
    def user_name(self, value: str) -> None:
        self._user_name = value

    @property
    def user_password(self) -> str:
        """Password of user."""
        return self._user_password

    @user_password.setter
    def user_password(self, value: str) -> None:
        self._user_password = value

    @property
    def slave_jar_file(self) -> str:
        """Location on slave filesystem where the jar file will be saved."""
        return self._slave_jar_file

    @slave_jar_file.setter
    def slave_jar_file(self, value: str) -> None:
        self._slave_jar_file = value

    @property
    def slave_name(self) -> str:
        """Name of slave node."""
        return self._slave_name

    @slave_name.setter
    def slave_name(self, value: str) -> None:
        self._slave_name = value

    @property
    def slave_secret(self) -> str:
        """Secret key for communicating between master and slave."""
        return self._slave_secret

    @slave_secret.setter
    def slave_secret(self, value: str) -> None:
        self._slave_secret = value

    @property
    def slave_executors(self) -> int:
        """Number of slave nodes."""
        return self._slave_executors

    @slave_executors.setter
    def slave_executors(self, value: int) -> None:
        self._slave_executors = value

    @property
    def slave_labels(self) -> str:
        """Descriptor of slave node."""
        return self._slave_labels

    @slave_labels.setter
    def slave_labels(self, value: str) -> None:
        self._slave_labels = value

    @property
    def slave_working_dir(self) -> str:
        return self._slave_working_dir

    @slave_working_dir.setter
    def slave_working_dir(self, value: str) -> None:
        self._slave_working_dir = value

    @property
    def clean_working_dir(self) -> bool:
        return self._clean_working_dir

    @clean_working_dir.setter
    def clean_working_dir(self, value: bool) -> None:
        self._clean_working_dir = value

    @property
    def start_agent_url(self) -> str:
        return '%s/computer/%s/slave-agent.jnlp' % (self.master_url, self.slave_name)

    @property
    def jar_download_url(self) -> str:
        return self.master_url + self.master_resource

class Slave(object):
    """Slave node for processing Jenkins requests."""

    _settings = None
    _process = None

    def __init__(self, settings: Settings):
        self._settings = settings

    def get_Jenkins(self) -> Jenkins:
        return Jenkins(
            self._settings.master_url,
            self._settings.user_name,
            self._settings.user_password
        )

    def clean(self, dir: str) -> None:
        for root, dirs, files in os.walk(dir):
            for f in files:
                os.unlink(os.path.join(root, f))
            for d in dirs:
                shutil.rmtree(os.path.join(root, d))

    def create(self, directory: str) -> None:
        self.get_Jenkins().node_create(
            self._settings.slave_name,
            directory,
            num_executors = self._settings.slave_executors,
            labels = self._settings.slave_labels,
            launcher = NodeLaunchMethod.JNLP
        )

    def delete(self, node_name) -> None:
        self.get_Jenkins().node_delete(node_name)

    def download(self, target) -> bool:
        if os.path.isfile(target):
            os.remove(target)

        urllib.request.urlretrieve(
            self._settings.jar_download_url,
            target
        )

        return os.path.isfile(target)

    def run(self) -> subprocess.Popen:
        params = [
            'java',
            '-jar',
            self._settings.slave_jar_file,
            '-jnlpUrl',
            self._settings.start_agent_url
        ]

        if self._settings.slave_url:
            params.extend([ '-connectTo', self._settings.slave_url ])

        if self._settings.user_name and self._settings.user_password:
            params.extend([
                '-jnlpCredentials',
                '%s:%s' % (
                    self._settings.user_name,
                    self._settings.user_password
                )
            ])
        
        if self._settings.slave_secret:
            params.extend([ '-secret', self._settings.slave_secret ])

        print('Subprocess params %s' % params)

        return subprocess.Popen(params, stdout=subprocess.PIPE)

    def master_ready(self, url: str) -> bool:
        try:
            print(url)
            r = requests.head(url, verify=False, timeout=None)
            return r.status_code == requests.codes.ok
        except Exception as ex:
            print('An error %s has occured while checking master.' % str(ex))
            return False

    def signal_handler(self, sig, frame) -> None:
        if self._process != None:
            self._process.send_signal(signal.SIGINT)

    def initialize(self):
        print(self._settings.jar_download_url)

        while not self.master_ready(self._settings.jar_download_url):
            print('Master not ready yet, sleeping for 10sec!')
            time.sleep(10)

        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)

        if (self.download(self._settings.slave_jar_file)):
            print(
                'Downloaded slave jar file from %s to %s.' %
                (self._settings.jar_download_url, self._settings.slave_jar_file)
            )
        else:
            print(
                'Could not download slave jar file from %s to %s.' %
                (self._settings.jar_download_url, self._settings.slave_jar_file)
            )

        os.chdir(self._settings.slave_working_dir)
        print('Current cwd is %s.' % os.getcwd())

        if self._settings.clean_working_dir:
            self.clean(self._settings.slave_working_dir)
            print('Cleaned up working directory.')

        self.create(self._settings.slave_working_dir)
        print('Created temporary Jenkins slave.')
            
        self._process = self.run()
        print(
            'Started Jenkins slave with name "%s" and labels [%s].' % 
            (self._settings.slave_name, self._settings.slave_labels)
        )

        self._process.wait()

        print('Jenkins slave stopped.')
        if self._settings.slave_name:
            self.delete(self._settings.slave_name)
            print('Removed temporary Jenkins slave.')

if __name__ == '__main__':
    settings = Settings(os.environ)
    slave = Slave(settings)
    slave.initialize()
