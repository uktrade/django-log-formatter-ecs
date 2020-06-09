========================
Django ECS log formatter
========================

The library formats Django logs in ECS format.

https://www.elastic.co/guide/en/ecs/current/index.html

Mapping to the format is incomplete and best effort has been made to create logical field mappings between Django and ECS.

If you need to amend the mapping you can implement a custom formatter (see below).

Installation
------------

.. code-block:: python

    pip install django-log-formatter-ecs

Usage
-----

Using in a Django logging configuration:

.. code-block:: python

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

Dependencies
------------

This package uses for kubi_ecs_logger https://github.com/kumina/kubi_ecs_logger for base ECS formatting.

This package uses Django IPware https://github.com/un33k/django-ipware for IP address capture.

This package is compatible with django-user_agents https://pypi.org/project/django-user-agents/ which, when used, will enhance logged user agent information.

Environment variables
-------------
To set the application name within ECS define the DLFE_APP_NAME environment variable.

The formatter checks the setting DLFE_LOG_SENSITIVE_USER_DATA to see if user information should be logged. If this is not set to true, only the user's id is logged.

Creating a custom formatter
---------------------------

If you wish to create your own ECS formatter, you can inherit from ECSSystemFormatter and call _get_event_base to get the base level logging data for use in augmentation:

.. code-block:: python

    class ECSSystemFormatter(ECSFormatterBase):
        def get_event(self):
            logger_event = self._get_event_base()

            # Customise logger event

            return logger_event

Tests
-----

.. code-block:: console

    $ pip install -r requirements.txt
    $ tox
