#!/usr/bin/python

from setuptools import setup, find_packages

setup(
    name = 'dtcwtfusion',
    version = '0.1',
    author = 'Rich Wareham',
    author_email = 'rjw57@cantab.net',
    description = 'Registration of images via DT-CWT',
    long_description = open('README.rst').read(),
    url = 'https://github.com/rjw57/dtcwt-fusion',
    license = 'MIT',
    packages = find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
    entry_points = { 'console_scripts': [
        'dtcwt_fuse = dtcwtfusion.tool:main',
    ] },
    install_requires = [
        'docopt', 'numpy', 'Pillow', 'dtcwt',
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

