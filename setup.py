from distutils.core import setup

import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="django_log_formatter_ecs",
    version="0.0.5",
    packages=setuptools.find_packages(),
    author="Department for Business and Trade Platform Team",
    author_email="sre-team@digital.trade.gov.uk",
    url="https://github.com/uktrade/django-log-formatter-ecs",
    description="ECS log formatter for Django",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    install_requires=[
        "django-ipware~=3.0",
        "kubi-ecs-logger~=0.1.0",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
)
