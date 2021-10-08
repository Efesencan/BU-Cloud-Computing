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
    url              = 'https://github.com/yannip1234/pl-ageatscan#readme',
    packages         = ['ageatscan'],
    install_requires = ['chrisapp', 'tqdm', 'pandas'],
    license          = 'MIT',
    zip_safe         = False,
    python_requires  = '>=3.6',
    entry_points     = {
        'console_scripts': [
            'ageatscan = ageatscan.__main__:main'
            ]
        }
)
