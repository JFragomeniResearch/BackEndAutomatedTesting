from setuptools import setup, find_packages

setup(
    name="beat",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        'pytest',
        'requests',
        'sqlalchemy',
        'pytest-html',
    ],
) 