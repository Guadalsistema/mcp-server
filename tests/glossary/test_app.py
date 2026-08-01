import os
import unittest
from unittest.mock import patch

from glossary import app


class GlossaryAppTests(unittest.TestCase):
    @patch.object(app.server, "run")
    def test_asios_api_key_flag_configures_esios_environment(self, run):
        with patch.dict(os.environ, {}, clear=True):
            app.main(["--asios-api-key", "cli-key"])
            self.assertEqual(os.environ["ESIOS_API_KEY"], "cli-key")

        run.assert_called_once_with(show_banner=False)


if __name__ == "__main__":
    unittest.main()
