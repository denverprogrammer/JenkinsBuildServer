import unittest
import os

from scripts.settings import JenkinsSettings


class TestJenkinsSettings(unittest.TestCase):

    def config_defaults(self):
        return {
            'USER_NAME': 'admin',
            'USER_PASSWORD': 'drowssap',
            'SLAVE_SECRET': None,
            'MASTER_URL': 'http://jenkins:8080',
            'MASTER_RESOURCE': '/jnlpJars/slave.jar',
            'SLAVE_URL': None,
            'SLAVE_NAME': None,
            'SLAVE_JAR_FILE': '/var/lib/jenkins/slave.jar',
            'SLAVE_EXECUTORS': 1,
            'SLAVE_LABELS': 'docker',
            'SLAVE_WORKING_DIR': None,
            'CLEAN_WORKING_DIR': True,
            'HOSTNAME': 'test_host'
        }

    def test_user_name(self):
        settings = JenkinsSettings(self.config_defaults())
        self.assertEqual(settings.user_name, 'admin')
        settings.user_name = 'test user'
        self.assertEqual(settings.user_name, 'test user')

    def test_user_password(self):
        settings = JenkinsSettings(self.config_defaults())
        self.assertEqual(settings.user_password, 'drowssap')
        settings.user_password = 'testing'
        self.assertEqual(settings.user_password, 'testing')

    def test_slave_secret(self):
        settings = JenkinsSettings(self.config_defaults())
        self.assertEqual(settings.slave_secret, None)
        settings.slave_secret = 'this is a secret'
        self.assertEqual(settings.slave_secret, 'this is a secret')

    def test_master_url(self):
        settings = JenkinsSettings(self.config_defaults())
        self.assertEqual(settings.master_url, 'http://jenkins:8080')
        settings.master_url = 'http://master.com'
        self.assertEqual(settings.master_url, 'http://master.com')

    def test_master_resource(self):
        settings = JenkinsSettings(self.config_defaults())
        self.assertEqual(settings.master_resource, '/jnlpJars/slave.jar')
        settings.master_resource = '/var/lib/test'
        self.assertEqual(settings.master_resource, '/var/lib/test')

    def test_slave_url(self):
        settings = JenkinsSettings(self.config_defaults())
        self.assertEqual(settings.slave_url, None)
        settings.slave_url = 'http://slave'
        self.assertEqual(settings.slave_url, 'http://slave')

    def test_slave_name(self):
        # Test HOSTNAME default
        defaults = self.config_defaults()
        settings = JenkinsSettings(defaults)
        self.assertEqual(settings.slave_name, 'docker-slave-test_host')
        # Test SLAVE_NAME default
        defaults['SLAVE_NAME'] = 'test_agent'
        settings = JenkinsSettings(defaults)
        self.assertEqual(settings.slave_name, 'test_agent')
        # Test SLAVE_NAME setter
        settings.slave_name = 'test_agent again'
        self.assertEqual(settings.slave_name, 'test_agent again')

    def test_slave_jar_file(self):
        settings = JenkinsSettings(self.config_defaults())
        self.assertEqual(settings.slave_jar_file, '/var/lib/jenkins/slave.jar')
        settings.slave_jar_file = '/var/lib/jenkins/test.jar'
        self.assertEqual(settings.slave_jar_file, '/var/lib/jenkins/test.jar')

    def test_slave_executors(self):
        settings = JenkinsSettings(self.config_defaults())
        self.assertEqual(settings.slave_executors, 1)
        settings.slave_executors = 5
        self.assertEqual(settings.slave_executors, 5)

    def test_slave_labels(self):
        settings = JenkinsSettings(self.config_defaults())
        self.assertEqual(settings.slave_labels, 'docker')
        settings.slave_labels = 'testing'
        self.assertEqual(settings.slave_labels, 'testing')

    def test_slave_working_dir(self):
        settings = JenkinsSettings(self.config_defaults())
        self.assertEqual(settings.slave_working_dir, os.getcwd())
        settings.slave_working_dir = '/var/lib'
        self.assertEqual(settings.slave_working_dir, '/var/lib')

    def test_clean_working_dir(self):
        settings = JenkinsSettings(self.config_defaults())
        self.assertEqual(settings.clean_working_dir, True)
        settings.clean_working_dir = False
        self.assertEqual(settings.clean_working_dir, False)

    def test_credentials(self):
        settings = JenkinsSettings(self.config_defaults())
        self.assertEqual(settings.user_credentials, 'admin:drowssap')
        settings.user_name = None
        settings.user_password = None
        settings.slave_secret = 'this is a secret'
        self.assertEqual(settings.user_credentials, None)
        self.assertEqual(settings.user_password, None)
        self.assertEqual(settings.slave_secret, 'this is a secret')


if __name__ == '__main__':
    unittest.main()
