import json
import logging
import os
import platform
from urllib.parse import urlparse

from django.conf import settings

from kubi_ecs_logger import Logger
from kubi_ecs_logger.models import BaseSchema, Severity

# Event categories - https://www.elastic.co/guide/en/ecs/current/ecs-allowed-values-event-category.html  # noqa E501
CATEGORY_DATABASE = "database"
CATEGORY_PROCESS = "process"
CATEGORY_WEB = "web"


class ECSlogger(Logger):
    def __init__(self, *args, **kwargs):
        super(ECSlogger, self).__init__(*args, **kwargs)

    def get_log_dict(self):
        return BaseSchema().dump(self._base).data


class ECSFormatterBase:
    def __init__(self, record):
        self.record = record

    def _get_event_base(self, extra_labels={}):
        labels = {
            'application': getattr(settings, "DLFE_APP_NAME", None),
            'env': self._get_environment(),
        }

        logger = ECSlogger().event(
            category=self._get_event_category(),
            action=self.record.name,
            message=self.record.getMessage(),
            labels={
                **labels,
                **extra_labels,
            },
        ).host(
            architecture=platform.machine(),
        )

        return logger

    def _get_event_category(self):
        if self.record.name in ("django.request", "django.server"):
            return CATEGORY_WEB
        if self.record.name.startswith("django.db.backends"):
            return CATEGORY_DATABASE

        return CATEGORY_PROCESS

    def _get_environment(self):
        return os.getenv('DJANGO_SETTINGS_MODULE') or "Unknown"


class ECSSystemFormatter(ECSFormatterBase):
    def get_event(self):
        logger_event = self._get_event_base()

        return logger_event


class ECSDBFormatter(ECSFormatterBase):
    # created for augmentation based on django.db.backends
    def get_event(self):
        logger_event = self._get_event_base()

        return logger_event


class ECSRequestFormatter(ECSFormatterBase):
    def get_event(self):
        zipkin_headers = getattr(
            settings,
            'DLFE_ZIPKIN_HEADERS',
            ("X-B3-TraceId", "X-B3-SpanId"),
        )

        extra_labels = {}

        for zipkin_header in zipkin_headers:
            if getattr(
                self.record.request.headers, zipkin_header, None,
            ):
                extra_labels[zipkin_header] = self.record.request.headers[zipkin_header]  # noqa E501

        logger_event = self._get_event_base(
            extra_labels=extra_labels,
        )

        parsed_url = urlparse(
            self.record.request.build_absolute_uri()
        )

        ip = self._get_ip_address(self.record.request)

        request_bytes = len(self.record.request.body)

        logger_event.url(
            path=parsed_url.path,
            domain=parsed_url.hostname,
        ).source(
            ip=self._get_ip_address(self.record.request)
        ).http_response(
            status_code=getattr(self.record, 'status_code', None)
        ).client(
            address=ip,
            bytes=request_bytes,
            domain=parsed_url.hostname,
            ip=ip,
            port=parsed_url.port,
        ).http_request(
            body_bytes=request_bytes,
            body_content=self.record.request.body,
            method=self.record.request.method,
        )

        user_agent_string = getattr(
            self.record.request.headers, 'user_agent', None,
        )

        if not user_agent_string and 'HTTP_USER_AGENT' in self.record.request.META:  # noqa E501
            user_agent_string = self.record.request.META['HTTP_USER_AGENT']

        # Check for use of django-user_agents
        if getattr(self.record.request, 'user_agent', None):
            logger_event.user_agent(
                device={
                    "name": self.record.request.user_agent.device.family,
                },
                name=self.record.request.user_agent.browser.family,
                original=user_agent_string,
                version=self.record.request.user_agent.browser.version_string,
            )
        elif user_agent_string:
            logger_event.user_agent(
                original=user_agent_string,
            )

        if getattr(self.record.request, 'user', None):
            if getattr(settings, 'DLFE_LOG_SENSITIVE_USER_DATA', False):
                # Defensively check for full name due to possibility of custom user app
                try:
                    full_name = self.record.request.user.get_full_name()
                except AttributeError:
                    full_name = None

                # Check user attrs to account for custom user apps
                logger_event.user(
                    email=getattr(self.record.request.user, 'email', None),
                    full_name=full_name,
                    name=getattr(self.record.request.user, 'username', None),
                    id=getattr(self.record.request.user, 'id', None),
                )
            else:
                logger_event.user(
                    id=getattr(self.record.request.user, 'id', None),
                )

        return logger_event

    def _get_ip_address(self, request):
        # Import here as ipware uses settings
        from ipware import get_client_ip
        client_ip, is_routable = get_client_ip(request)
        return client_ip or "Unknown"


ECS_FORMATTERS = {
    "root": ECSSystemFormatter,
    "django.request": ECSRequestFormatter,
    "django.db.backends": ECSSystemFormatter,
}


class ECSFormatter(logging.Formatter):
    def format(self, record):
        if record.name in ECS_FORMATTERS:
            ecs_formatter = ECS_FORMATTERS[record.name]
        else:
            ecs_formatter = ECSSystemFormatter

        formatter = ecs_formatter(record=record)
        logger_event = formatter.get_event()

        logger_event.log(
            level=self._get_severity(record.levelname),
        )

        log_dict = logger_event.get_log_dict()

        return json.dumps(log_dict)

    def _get_severity(self, level):
        if level == "DEBUG":
            return Severity.DEBUG
        elif level == "INFO":
            return Severity.INFO
        elif level == "WARNING":
            return Severity.WARNING
        elif level == "ERROR":
            return Severity.ERROR
        elif level == "CRITICAL":
            return Severity.CRITICAL
