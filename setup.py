from distutils.core import setup

import setuptools


with open("README.rst", "r") as fh:
    long_description = fh.read()

setup(
    name="django_log_formatter_ecs",
    version="0.0.3",
    packages=setuptools.find_packages(),
    author="Ross Miller",
    author_email="ross.miller@digita.trade.gov.uk",
    url="https://github.com/uktrade/django-log-formatter-ecs",
    description="ECS log formatter for Django",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    install_requires=[
        "django-ipware>=2.1.0",
        "kubi-ecs-logger>=0.0.6",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
