import os
import signal
import urllib
import subprocess
import shutil
import requests
import time
import logging
from jenkins import Jenkins
from jenkins import NodeLaunchMethod
from settings import JenkinsSettings


class Slave(object):
    """Slave node for processing Jenkins requests."""

    _settings = None
    _process = None
    _logger = None

    def __init__(self, settings: JenkinsSettings, logger: logging.Logger):
        """Initialzies the slave node."""
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

    settings = JenkinsSettings(os.environ)
    slave = Slave(settings, logger)
    slave.setup_node()
