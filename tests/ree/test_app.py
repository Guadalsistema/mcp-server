import unittest
from unittest.mock import patch

from ree import app


class AppTests(unittest.TestCase):
    @patch.object(app.server, "run")
    def test_main_disables_banner_for_stdio_startup(self, run):
        app.main()

        run.assert_called_once_with(show_banner=False)


if __name__ == "__main__":
    unittest.main()
