from setuptools import find_packages
from setuptools import setup

with open('README.rst') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='scrapy-logstats-cache',
    version='0.1.0',
    description='Logstats cache for Scrapy',
    long_description=readme,
    author='Frank Wang',
    url='https://github.com/leonardfrank/scrapy-logstats-cache',
    license=license,
    packages=find_packages(
        exclude=('tests', 'tests.*')
    ),
)
