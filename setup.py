from distutils.core import setup

import setuptools


with open("README.rst", "r") as fh:
    long_description = fh.read()

setup(
    name="ECS-log-formatter",
    version="0.0.1",
    packages=setuptools.find_packages(),
    author="Ross Miller",
    author_email="ross.miller@digita.trade.gov.uk",
    url="https://github.com/uktrade/django-log-formatter-ecs",
    description="ECS log formatter for Django",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    install_requires=[
        "django-ipware",
        "kubi-ecs-logger",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
