#!/usr/bin/env python
# -*- coding: utf-8 -*-
import io
import os
import sys
from shutil import rmtree

from setuptools import find_packages, setup, Command

# Package meta-data.
NAME = 'hapycolor'
DESCRIPTION = 'Generates beautiful color palettes from images.'
URL = 'https://github.com/rvdz/hapycolor'
EMAIL = 'robin.vincent@grenoble-inp.org, romain.pierson@grenoble-inp.org, yanncolina@gmail.com'
AUTHOR = 'Robin Vincent-Deleuze, Romain Pierson, Yann Colina'

# Packages required for this module to be executed
REQUIRED = [
    'Pillow==5.1.0',
    'networkx==2.1',
    'scipy==1.0.1',
    'colormath==3.0.0',
    'numpy==1.14.3',
    'imgur-downloader==0.1.7',
]

HERE = os.path.abspath(os.path.dirname(__file__))

# Import the README and use it as the long-description.
with io.open(os.path.join(HERE, 'README.md'), encoding='utf-8') as f:
    LONG_DESCRIPTION = '\n' + f.read()

# Load the package's __version__.py module as a dictionary.
ABOUT = {}
with open(os.path.join(HERE, NAME, '__version__.py')) as f:
    exec(f.read(), ABOUT)


class UploadCommand(Command):
    """Support setup.py upload."""

    description = 'Build and publish the package.'
    user_options = []

    @staticmethod
    def status(string):
        """Prints things in bold."""
        print('\033[1m{0}\033[0m'.format(string))

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        try:
            self.status('Removing previous builds…')
            rmtree(os.path.join(HERE, 'dist'))
        except OSError:
            pass

        self.status('Building Source and Wheel (universal) distribution…')
        os.system('{0} setup.py sdist bdist_wheel --universal'.format(sys.executable))

        self.status('Uploading the package to PyPi via Twine…')
        os.system('twine upload dist/*')

        sys.exit()


# Where the magic happens:
setup(
    name=NAME,
    version=ABOUT['__version__'],
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    author=AUTHOR,
    author_email=EMAIL,
    url=URL,
    packages=find_packages(exclude=('tests', 'docs', 'docs_sources')),
    # If your package is a single module, use this instead of 'packages':
    # py_modules=['mypackage'],

    entry_points={
        'console_scripts': ['hapycolor=hapycolor.__main__:main']
    },
    python_requires=">=3.5",
    install_requires=REQUIRED,
    include_package_data=True,
    license='MIT License',
    classifiers=[
        # Trove classifiers
        # Full list: https://pypi.python.org/pypi?%3Aaction=list_classifiers
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    # $ setup.py publish support.
    cmdclass={
        'upload': UploadCommand,
    },
)
