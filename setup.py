import codecs
from setuptools import setup

import laastfm


setup(
    name='laastfm',
    version=laastfm.__version__,
    description=laastfm.__doc__.strip(),
    long_description=codecs.open('README.rst', encoding='utf8').read(),
    author_email=laastfm.__email__,
    license=laastfm.__licence__,
    url='https://github.com/jkbr/laastfm',
    download_url='https://github.com/jkbr/laastfm',
    packages=['laastfm'],
    install_requires=[
        'requests>=1.0.4'
    ]
)
