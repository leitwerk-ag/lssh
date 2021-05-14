from setuptools import setup, find_packages

setup(
    name='lssh',
    version='0.0.1',
    description='A command-line tool that simplifies searching for ssh targets to access them',
    packages=find_packages(where='.'),
    install_requires=['py-cui', 'xdg'],
    entry_points={
        'console_scripts': [
            'lssh=lssh.main:main',
        ],
    },
)
