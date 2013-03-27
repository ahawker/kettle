__author__ = 'Andrew Hawker <andrew.r.hawker@gmail.com>'

import kettle

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name=kettle.__name__,
    version=kettle.__version__,
    description='Kademlia Distributed Hash Table.',
    long_description=open('README.md').read(),
    author='Andrew Hawker',
    author_email='andrew.r.hawker@gmail.com',
    url='https://github.com/ahawker/kettle',
    license=open('LICENSE.md').read(),
    package_dir={'kettle': 'kettle'},
    packages=['kettle'],
    test_suite='tests',
    classifiers=(
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7'
        )
)