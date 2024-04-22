from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="yourapp-backend",
    version="0.1.0",
    author="Anicet Nougaret, Osama Atwi",
    author_email="",
    description="Yourapp's backend",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourapp",
    packages=find_packages(),
    install_requires=[
        # repeat deps here
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)
