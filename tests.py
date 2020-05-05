import json
import logging
from io import BytesIO, StringIO
from unittest import TestCase

from django.conf import settings
from django.core.handlers.wsgi import WSGIRequest

settings.configure(
    DEBUG=True,
    ALLOWED_HOSTS="*",
)

from django_log_formatter_ecs import ECSFormatter


class ECSFormatterTest(TestCase):
    def create_logger(self, logger_name):
        log_buffer = StringIO()
        ecs_handler = logging.StreamHandler(log_buffer)
        ecs_handler.setFormatter(ECSFormatter())

        logger = logging.getLogger(logger_name)
        logger.addHandler(ecs_handler)
        logger.setLevel(logging.DEBUG)
        logging.propagate = False

        return logger, log_buffer

    def test_record_base_formatting(self):
        logger, log_buffer = self.create_logger("django")
        logger.debug("Test")
        json_output = log_buffer.getvalue()
        output = json.loads(json_output)

        assert output["event"]["message"] == "Test"

    def test_request_formatting(self):
        logger, log_buffer = self.create_logger("django.request")
        logger.error(
            msg="Request test",
            extra={
                "request": WSGIRequest({
                    "SERVER_NAME": "test.com",
                    "SERVER_PORT": "443",
                    "PATH_INFO": "test",
                    "REQUEST_METHOD": "test",
                    "CONTENT_TYPE": "text/html; charset=utf8",
                    "wsgi.input": BytesIO(b''),
                }),
            }
        )

        json_output = log_buffer.getvalue()
        output = json.loads(json_output)

        assert output["event"]["message"] == "Request test"
