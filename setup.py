import os

from setuptools import setup, find_packages

ROOT = os.path.abspath(os.path.dirname(__file__))
README_FILE = os.path.join(ROOT, 'README.md')
REQS_FILE = os.path.join(ROOT, 'requirements.txt')

with open(README_FILE, 'r') as rm:
    readme = rm.read()

with open(REQS_FILE, 'r') as reqf:
    reqs = reqf.readlines()

setup(
    name="release_watch",
    version="0.0.1",
    author="blockjoe",
    description="A discord bot to watch for github releases",
    license="MIT",
    long_description=readme,
    packages=find_packages(),
    url="https://github.com/pokt-foundation/release_watch",
    install_requires=reqs,
    setup_requires=['wheel'],
    entry_points={
        'console_scripts': ['release_watch=release_bot.bot:main']
    },
    python_requires='>=3.8'
)


