from setuptools import setup
setup(
    name = 'chrisclient',
    version = '0.1.0',
    packages = ['chrisclient'],
    entry_points = {
        'console_scripts': [
            'chrisclient = chrisclient.__main__:main'
        ]
    })