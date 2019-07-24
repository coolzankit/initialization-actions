import os
import unittest

from parameterized import parameterized

from integration_tests.dataproc_test_case import DataprocTestCase


class KnoxTestCase(DataprocTestCase):
    COMPONENT = 'knox'
    INIT_ACTIONS = ['knox/knox.sh']
    TEST_SCRIPT_FILE_NAME = 'verify_knox.sh'

    def verify_instance(self, name, cert_type):
        self.upload_test_file(
            os.path.join(os.path.dirname(os.path.abspath(__file__)),
                         self.TEST_SCRIPT_FILE_NAME), name)
        print("Starting the tests")
        self.__run_test_script(name, cert_type)
        
        self.remove_test_script(self.TEST_SCRIPT_FILE_NAME, name)

    def __run_test_script(self, name, cert_type):
        self.assert_instance_command(
            name, "bash {} {}".format(self.TEST_SCRIPT_FILE_NAME, cert_type))

    def __get_gs_location(self):
        repo = self.INIT_ACTIONS_REPO.strip("/")
        prefix = "gs://"
        return repo[len(prefix):] if repo.startswith(prefix) else repo

    @parameterized.expand(
        [
            ("SINGLE", "1.3", ["m"]),
            ("SINGLE", "1.4", ["m"]),
            ("STANDARD", "1.4", ["m","w-0"]),
            ("HA", "1.4", ["m-2","w-0"])
        ],
        testcase_func_name=DataprocTestCase.generate_verbose_test_name)
    def test_knox_localhost_cert(self, configuration, dataproc_version, machine_suffixes):
        self.createCluster(configuration,
                           self.INIT_ACTIONS,
                           dataproc_version,
                           machine_type="n1-standard-2",
                           # we don't want to run the auto update during the tests since it overrides our changes in the tests. 
                           # So we assign cron date to 31/December. Hopefully no one runs a test on that day
                           metadata="knox-gw-config-gs={}/knox,certificate_hostname=localhost,config_update_interval=\"0 0 31 12 * \"".format(self.__get_gs_location()))
        for machine_suffix in machine_suffixes:
            self.verify_instance("{}-{}".format(self.getClusterName(),
                                                machine_suffix),"localhost")

    @parameterized.expand(
        [
            ("STANDARD", "1.4", ["w-0","m"]),
            ("HA", "1.4", ["m-1", "m-0"])
        ],
        testcase_func_name=DataprocTestCase.generate_verbose_test_name)
    def test_knox_hostname_cert(self, configuration, dataproc_version, machine_suffixes):
        self.createCluster(configuration,
                           self.INIT_ACTIONS,
                           dataproc_version,
                           machine_type="n1-standard-2",
                           # we don't want to run the auto update during the tests since it overrides our changes in the tests. 
                           # So we assign cron date to 31/December. Hopefully no one runs a test on that day
                           metadata="knox-gw-config-gs={}/knox,certificate_hostname=HOSTNAME,config_update_interval=\"0 0 31 12 * \"".format(self.__get_gs_location()))
        for machine_suffix in machine_suffixes:
            self.verify_instance("{}-{}".format(self.getClusterName(),
                                                machine_suffix),"hostname")


if __name__ == '__main__':
    unittest.main()
