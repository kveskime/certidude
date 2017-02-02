from click.testing import CliRunner
from certidude.cli import entry_point as cli
from datetime import datetime, timedelta
from certidude.api import certidude_app
from falcon import testing
from certidude import authority


runner = CliRunner()

class TestCliSetup_TestAPI(testing.TestCase):
    def setUp(self):
        super(TestCliSetup_TestAPI, self).setUp()
        self.app = certidude_app()


class TestMyApp(TestCliSetup_TestAPI):
    def test_cli_setup_authority(self):
        result = runner.invoke(cli, ['setup', 'authority'])
        self.assertIsNot(result.exception)
        self.assertEqual(authority.certificate.serial_number, '0000000000000000000000000000000000000001')
        self.assertGreater(datetime.now(), authority.certificate.signed)
        self.assertGreater(authority.certificate.expires, datetime.now() + timedelta(days=7000))
