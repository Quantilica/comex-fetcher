import setuptools
import ComexDown


with open("README.md", "r") as fh:
    long_description = fh.read()


setuptools.setup(
    name="ComexDown-DanKKom",
    version=ComexDown.__version__,
    author=ComexDown.__author__,
    author_email=ComexDown.__author_email__,
    description="A little utility to download Brazil's foreign trade data.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://bitbucket.org/DanKKom/comexdown/",
    packages=setuptools.find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "Intended Audience :: Science/Research",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Utilities",
    ],
    python_requires=">=3.7",
)
