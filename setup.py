from __future__ import with_statement
from __future__ import absolute_import
from setuptools import setup, find_packages
from codecs import open
from os import path
from io import open

here = path.abspath(path.dirname(__file__))

with open(path.join(here, u'README.rst'), encoding=u'utf-8') as f:
    long_description = f.read()

setup(
  name = u'udsoncan',
  packages = find_packages(exclude=[u'test']),
#  package_data={
#      u'': [u'*.conf'],
#  },
  version = u'1.13.1',
  description = u'Implementation of the Unified Diagnostic Service (UDS) protocol (ISO-14229) used in the automotive industry.',
  long_description=long_description,
  author = u'Pier-Yves Lessard',
  author_email = u'py.lessard@gmail.com',
  license=u'MIT',
  url = u'https://github.com/pylessard/python-udsoncan',
  download_url = u'https://github.com/pylessard/python-udsoncan/archive/v1.13.1.tar.gz',
  keywords = [u'uds', u'14229', u'iso-14229', u'diagnostic', u'automotive'], 
  python_requires=u'>=2.7',
  classifiers = [
        u"Programming Language :: Python",
        u"Development Status :: 4 - Beta",
        u"Operating System :: POSIX :: Linux",
        u"Intended Audience :: Developers",
        u"License :: OSI Approved :: MIT License",
        u"Topic :: Scientific/Engineering :: Interface Engine/Protocol Translator",
        ],
)
