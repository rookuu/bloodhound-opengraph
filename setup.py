"""
Setup configuration for the BloodHound OpenGraph Helper Library.
"""

from setuptools import setup, find_packages
import os

# Read the contents of your README file
this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

# Read the version from the package
def get_version():
    """Get version from package __init__.py"""
    init_file = os.path.join(this_directory, "opengraph", "__init__.py")
    with open(init_file, encoding="utf-8") as f:
        for line in f:
            if line.startswith("__version__"):
                return line.split("=")[1].strip().strip('"').strip("'")
    return "0.0.0"

setup(
    name="bloodhound-opengraph",
    version=get_version(),
    author="Luke Roberts",
    author_email="rookuu@github.com",
    description="A Python library for creating BloodHound OpenGraph JSON data",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/rookuu/bloodhound-opengraph",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        # No external dependencies - uses only Python standard library
    ],
    project_urls={
        "Documentation": "https://github.com/rookuu/bloodhound-opengraph/blob/main/README.md",
        "Source": "https://github.com/rookuu/bloodhound-opengraph",
        "Tracker": "https://github.com/rookuu/bloodhound-opengraph/issues",
    },
)
