from setuptools import setup, find_packages


INSTALL_REQUIRES = [
    "marisa-trie>=0.7.5",
    "ujson",
    "tqdm",
    "cached_property",
    "sqlalchemy",
    "download",
    "PyYAML",
    "us",
    "boltons",
    "attrs",
    "scipy"
]

CLASSIFIERS = [
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python",
    "Programming Language :: Python :: 3.5",
    "Programming Language :: Python :: 3.6",
    "Programming Language :: Python :: 3.7",
]


setup(
    name="litecoder",
    version="0.3.0",
    description="US city + state geocoding.",
    url="https://github.com/social-machines/litecoder",
    download_url="https://github.com/social-machines/litecoder/archive/v0.3.0.tar.gz",
    license="MIT",
    author="Lab for Social Machines, MIT Media Lab",
    author_email="wesc@media.mit.edu",
    packages=find_packages(),
    classifiers=CLASSIFIERS,
    install_requires=INSTALL_REQUIRES,
)
