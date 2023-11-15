# Django ECS log formatter

The library formats Django logs in ECS format.

https://www.elastic.co/guide/en/ecs/current/index.html

Mapping to the format is incomplete and best effort has been made to create logical field mappings between Django and ECS.

If you need to amend the mapping you can implement a custom formatter (see below).

## Installation

``` shell
pip install django-log-formatter-ecs
```

## Usage

Using in a Django logging configuration:

``` python
from django_log_formatter_ecs import ECSFormatter

LOGGING = {
    ...
    "formatters": {
        "ecs_formatter": {
            "()": ECSFormatter,
        },
    },
    'handlers': {
        'ecs': {
            'formatter': 'ecs_formatter',
            ...
        },
    },
    "loggers": {
        "django": {
            "handlers": ["ecs"],
            ...
        },
    },
}
```

## Dependencies

This package uses kubi_ecs_logger https://github.com/kumina/kubi_ecs_logger for base ECS formatting

This package uses Django IPware https://github.com/un33k/django-ipware for IP address capture.

This package is compatible with django-user_agents https://pypi.org/project/django-user-agents/ which, when used, will enhance logged user agent information.

## Settings

`DLFE_APP_NAME` - used to define the application name that should be logged.

`DLFE_LOG_SENSITIVE_USER_DATA` - the formatter checks this setting to see if user information should be logged. If this is not set to true, only the user's id is logged.

`DLFE_ZIPKIN_HEADERS` - used for defining custom zipkin headers, the defaults is :code:`("X-B3-TraceId" "X-B3-SpanId")`

The Django configuration file logged is determined by running:

``` python
os.getenv('DJANGO_SETTINGS_MODULE')
```

## Formatter classes

``` python
    ECS_FORMATTERS = {
        "root": ECSSystemFormatter,
        "django.request": ECSRequestFormatter,
        "django.db.backends": ECSSystemFormatter,
    }
```

The default class for other loggers is:

``` python
    ECSSystemFormatter
```

## Creating a custom formatter

If you wish to create your own ECS formatter, you can inherit from ECSSystemFormatter and call _get_event_base to get the base level logging data for use in augmentation:

``` python
    class ECSSystemFormatter(ECSFormatterBase):
        def get_event(self):
            logger_event = self._get_event_base()

            # Customise logger event

            return logger_event
```

## Contributing to the `django-log-formatter-ecs` package

### Getting started

1. Clone the repository:

   ```
   git clone https://github.com/uktrade/django-log-formatter-ecs.git && cd django-log-formatter-ecs
   ```

2. Install the required dependencies:

   ```
   pip install poetry && poetry install && poetry run pre-commit install
   ```

### Testing

#### Automated testing

Run `poetry run pytest` in the root directory to run all tests.

Or, run `poetry run tox` in the root directory to run all tests for multiple Python versions. See the [`tox` configuration file](tox.ini).
