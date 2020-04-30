import setuptools

import comexdown


name = "comexdown"
description = "A little utility to download Brazil's foreign trade data"
with open("README.md", "r") as fh:
    long_description = fh.read()
url = "https://github.com/dkkomesu/comexdown"
classifiers = [
    "Development Status :: 3 - Alpha",
    "Environment :: Console",
    "Intended Audience :: Developers",
    "Intended Audience :: Information Technology",
    "Intended Audience :: Science/Research",
    "Programming Language :: Python :: 3",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
    "Topic :: Utilities",
]
entry_points = {
    "console_scripts": ["comexdown=comexdown.cli:main"],
}

setuptools.setup(
    name=name,
    version=comexdown.__version__,
    author=comexdown.__author__,
    author_email=comexdown.__author_email__,
    description=description,
    long_description=long_description,
    long_description_content_type="text/markdown",
    url=url,
    packages=setuptools.find_packages(),
    classifiers=classifiers,
    python_requires=">=3.7",
    entry_points=entry_points,
)
