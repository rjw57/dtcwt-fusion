#!/usr/bin/python

from setuptools import setup, find_packages

setup(
    name = 'dtcwtregister',
    version = '0.1',
    author = 'Rich Wareham',
    author_email = 'rjw57@cantab.net',
    description = 'Registration of images via DT-CWT',
    long_description = open('README.rst').read(),
    license = 'MIT',
    packages = find_packages(),
    entry_points = { 'console_scripts': [
        'dtcwt_register = dtcwtregister.tool:main',
    ] },
    install_requires = [
        'docopt', 'numpy', 'matplotlib', 'dtcwt',
    ],
    classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: Utilities',
    ],
)

# vim:sw=4:sts=4:et

