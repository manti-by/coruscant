import logging.config
from unittest import mock

from coruscant.settings import LOGGING


logging.config.dictConfig(LOGGING)
logger = logging.getLogger(__name__)


class TestLogs:
    @mock.patch("logging.handlers.HTTPHandler.emit")
    def test_loging_handlers(self, mock_emit):
        logger.info("This is INFO message")
        assert mock_emit.call_count == 1
