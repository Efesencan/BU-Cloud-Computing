from os import path
from setuptools import setup

with open(path.join(path.dirname(path.abspath(__file__)), 'README.md')) as f:
    readme = f.read()

setup(
    name             = 'AgeAtScan',
    version          = '1.0.0',
    description      = 'Get the age between scan date and birthdate from a CSV',
    long_description = readme,
    author           = 'Yanni Pang',
    author_email     = 'yanni@bu.edu',
    url              = 'https://github.com/FNNDSC/pl-re-sub#readme',
    packages         = ['AgeAtScan'],
    install_requires = ['chrisapp', 'tqdm', 'pandas'],
    license          = 'MIT',
    zip_safe         = False,
    python_requires  = '>=3.6',
    entry_points     = {
        'console_scripts': [
            'AgeAtScan = AgeAtScan.__main__:main'
            ]
        }
)