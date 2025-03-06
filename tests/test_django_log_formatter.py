import json
import logging
import os
from io import StringIO
from unittest import TestCase
from unittest.mock import patch

from django.conf import settings
from django.test import RequestFactory
from django.test import override_settings

from django_log_formatter_ecs import ECSFormatter
from django_log_formatter_ecs import ECSRequestFormatter

settings.configure(
    DEBUG=True,
    ALLOWED_HOSTS="*",
)


class User:
    def __init__(self, email, user_id, first_name, last_name, username):
        self.email = email
        self.id = user_id
        self.first_name = first_name
        self.last_name = last_name
        self.username = username

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"


class MockRecord:
    def __init__(self, name, request):
        self.name = name
        self.request = request

    def getMessage(self):
        return f"Message"


class ECSRequestFormatterTest(TestCase):
    def test_get_event_resolves_with_expected_fields(self):
        headers = {"SERVER_NAME": "test-server", "SERVER_PORT": 1234, "REMOTE_ADDR": "111.1.1.1"}
        request = RequestFactory().get(path="/", data={}, **headers)

        result = ECSRequestFormatter(MockRecord("testing-123", request)).get_event().get_log_dict()

        assert result["event"]["action"] == "testing-123"
        assert result["httprequest"]["method"] == "GET"
        assert result["client"]["domain"] == "test-server"
        assert result["client"]["port"] == 1234
        assert result["source"]["ip"] == "111.1.1.1"


class ECSFormatterTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

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

    def _create_request_log(self, add_user=False):
        request = self.factory.get("/")

        if add_user:
            user = User(
                email="test@test.com",
                user_id=1,
                first_name="John",
                last_name="Test",
                username="johntest",
            )
            setattr(request, "user", user)

        logger, log_buffer = self.create_logger("django.request")
        logger.error(
            msg="Request test",
            extra={
                "request": request,
            },
        )

        json_output = log_buffer.getvalue()

        return json.loads(json_output)

    def test_request_formatting(self):
        output = self._create_request_log()

        assert output["event"]["message"] == "Request test"

    def test_log_sensitive_user_data_default(self):
        output = self._create_request_log(add_user=True)

        assert "id" in output["user"]
        assert "email" not in output["user"]

    @override_settings(DLFE_LOG_SENSITIVE_USER_DATA=True)
    def test_log_sensitive_user_data_on(self):
        output = self._create_request_log(add_user=True)

        assert output["user"]["id"] == "1"
        assert output["user"]["email"] == "test@test.com"
        assert output["user"]["full_name"] == "John Test"
        assert output["user"]["name"] == "johntest"

    @override_settings(DLFE_APP_NAME="TestApp")
    def test_app_name_log_value(self):
        output = self._create_request_log()

        assert output["event"]["labels"]["application"] == "TestApp"

    def test_env_unset_log_value(self):
        output = self._create_request_log()

        assert output["event"]["labels"]["env"] == "Unknown"

    @patch.dict(os.environ, {"DJANGO_SETTINGS_MODULE": "settings.Test"})
    def test_env_log_value(self):
        output = self._create_request_log()

        assert output["event"]["labels"]["env"] == "settings.Test"
