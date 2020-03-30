from jenkins import Jenkins
from jenkins import NodeLaunchMethod
import os
import signal
import urllib
import subprocess
import shutil
import requests
import time
import logging

try:
    import httplib
    httplib.HTTPConnection.debuglevel = 1
except ImportError:
    import http.client
    http.client.HTTPConnection.debuglevel = 1


class Settings(object):
    """Jenkins settings for master and slave nodes."""

    _user_name = 'admin'
    _user_password = 'admin'
    _slave_secret = None
    _master_url = 'http://jenkins'
    _master_resource = '/jnlpJars/slave.jar'
    _slave_url = None
    _slave_name = None
    _slave_jar_file = '/var/lib/jenkins/slave.jar'
    _slave_executors = 1
    _slave_labels = 'docker'
    _slave_working_dir = None
    _clean_working_dir = True
    _start_agent_url = '%s/computer/%s/slave-agent.jnlp'

    def __init__(self, config: dict):
        if (
            'USER_NAME' in config and config['USER_NAME']
            and 'USER_PASSWORD' in config and config['USER_PASSWORD']
        ):
            self._user_name = config['USER_NAME']
            self._user_password = config['USER_PASSWORD']
        elif 'SLAVE_SECRET' in config and config['SLAVE_SECRET']:
            self._slave_secret = config['SLAVE_SECRET']
        else:
            raise Exception('''SLAVE_SECRET or USER_NAME and
            USER_PASSWORD are not defined in config.''')

        if 'MASTER_URL' in config and config['MASTER_URL']:
            self._master_url = config['MASTER_URL']
        else:
            raise Exception('MASTER_URL is not defined in config.')

        if 'SLAVE_URL' in config:
            self._slave_url = config['SLAVE_URL']
        else:
            raise Exception('SLAVE_URL is not defined in config.')

        if 'SLAVE_NAME' in config and config['SLAVE_NAME']:
            self._slave_name = config['SLAVE_NAME']
        elif 'HOSTNAME' in config and config['HOSTNAME']:
            self._slave_name = 'docker-slave-%s' % config['HOSTNAME']
        else:
            raise Exception('SLAVE_NAME or HOSTNAME is not defined in config.')

        if 'SLAVE_EXECUTORS' in config:
            self._slave_executors = int(config['SLAVE_EXECUTORS'])
        else:
            raise Exception('SLAVE_EXECUTORS is not defined in config.')

        if 'SLAVE_LABELS' in config and config['SLAVE_LABELS']:
            self._slave_labels = config['SLAVE_LABELS']
        else:
            raise Exception('SLAVE_LABELS is not defined in config.')

        if (
            'SLAVE_WORKING_DIR' in config
            and os.path.isdir(config['CLEAN_WORKING_DIR'])
        ):
            self._slave_working_dir = config['SLAVE_WORKING_DIR']
        else:
            self._slave_working_dir = os.getcwd()

        if 'CLEAN_WORKING_DIR' in config:
            self._clean_working_dir = config['CLEAN_WORKING_DIR']
        else:
            raise Exception('CLEAN_WORKING_DIR is not defined in config.')

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
        """Name of username who to start slave node."""
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
        """Working directory of slave node.
        This is not the same directory where the slave jar file is stored."""
        return self._slave_working_dir

    @slave_working_dir.setter
    def slave_working_dir(self, value: str) -> None:
        self._slave_working_dir = value

    @property
    def clean_working_dir(self) -> bool:
        """Cleans the working directory of previous build."""
        return self._clean_working_dir

    @clean_working_dir.setter
    def clean_working_dir(self, value: bool) -> None:
        self._clean_working_dir = value

    @property
    def start_agent_url(self) -> str:
        """Url used to start a slave node."""
        return self._start_agent_url % (self.master_url, self.slave_name)

    @property
    def jar_download_url(self) -> str:
        """Url used to download the slave jar file."""
        return self.master_url + self.master_resource

    @property
    def user_credentials(self) -> str:
        """Credentails of user if defined."""
        if (self._user_name and self._user_password):
            return '%s:%s' % (self._user_name, self._user_password)
        return None


class Slave(object):
    """Slave node for processing Jenkins requests."""

    _settings = None
    _process = None
    _logger = None

    def __init__(self, settings: Settings, logger: logging.Logger):
        self._settings = settings
        self._logger = logger

    def get_Jenkins(self) -> Jenkins:
        """Initialize Jenkins class with basic settings."""
        return Jenkins(
            self._settings.master_url,
            self._settings.user_name,
            self._settings.user_password
        )

    def clean_node(self, dir: str) -> None:
        """Clean node of previous builds."""
        for root, dirs, files in os.walk(dir):
            for f in files:
                os.unlink(os.path.join(root, f))
            for d in dirs:
                shutil.rmtree(os.path.join(root, d))

    def create_node(self, directory: str) -> None:
        """Create slave node."""
        self.get_Jenkins().node_create(
            self._settings.slave_name,
            directory,
            num_executors=self._settings.slave_executors,
            labels=self._settings.slave_labels,
            launcher=NodeLaunchMethod.JNLP
        )

    def delete_node(self, node_name) -> None:
        """Delete slave node."""
        self.get_Jenkins().node_delete(node_name)

    def download_jar_file(self, target) -> bool:
        """Download jar file from master node."""
        if os.path.isfile(target):
            os.remove(target)

        urllib.request.urlretrieve(self._settings.jar_download_url, target)

        return os.path.isfile(target)

    def run_process(self) -> subprocess.Popen:
        """Starts the process in the node."""
        params = [
            'java',
            '-jar',
            self._settings.slave_jar_file,
            '-jnlpUrl',
            self._settings.start_agent_url
        ]

        if self._settings.slave_url:
            params.extend(['-connectTo', self._settings.slave_url])

        self._logger.info('Subprocess params %s' % params)

        if self._settings.user_name and self._settings.user_password:
            params.extend([
                '-jnlpCredentials',
                self._settings.user_credentials
            ])

        if self._settings.slave_secret:
            params.extend(['-secret', self._settings.slave_secret])

        return subprocess.Popen(params, stdout=subprocess.PIPE)

    def is_master_ready(self, url: str) -> bool:
        """Checks to see if the master node is ready."""
        try:
            r = requests.head(url, verify=True, timeout=None)
            return r.status_code == 200
        except Exception as ex:
            self._logger.info(
                'An error %s has occured while checking master.' %
                str(ex)
            )
            return False

    def signal_handler(self, sig, frame) -> None:
        """Callback for process."""
        if self._process is not None:
            self._process.send_signal(signal.SIGINT)

    def setup_node(self):
        """Sets up slave node."""
        config = self._settings

        while not self.is_master_ready(config.jar_download_url):
            self._logger.info('Master not ready yet, sleeping for 10sec!')
            time.sleep(10)

        self._logger.info('Master %s is now ready.' % config.master_url)
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)

        if (self.download_jar_file(config.slave_jar_file)):
            self._logger.info(
                'Downloaded slave jar file from %s to %s.' %
                (config.jar_download_url, config.slave_jar_file)
            )
        else:
            self._logger.info(
                'Could not download slave jar file from %s to %s.' %
                (config.jar_download_url, config.slave_jar_file)
            )

        os.chdir(config.slave_working_dir)
        self._logger.info('Current cwd is %s.' % os.getcwd())

        if config.clean_working_dir:
            self.clean_node(config.slave_working_dir)
            self._logger.info('Cleaned up working directory.')

        self.create_node(config.slave_working_dir)
        self._logger.info(
            'Created temporary Jenkins slave %s.' %
            config.slave_name
        )
        self._process = self.run_process()
        self._logger.info(
            'Started Jenkins slave with name "%s" and labels [%s].' %
            (config.slave_name, config.slave_labels)
        )
        self._process.wait()
        self._logger.info('Jenkins slave stopped.')
        if config.slave_name:
            self.delete_node(config.slave_name)
            self._logger.info('Removed temporary Jenkins slave.')


if __name__ == '__main__':
    logging.basicConfig()
    logging.getLogger().setLevel(logging.DEBUG)
    logger = logging.getLogger('requests.packages.urllib3')
    logger.setLevel(logging.DEBUG)
    logger.propagate = True

    settings = Settings(os.environ)
    slave = Slave(settings, logger)
    slave.setup_node()
