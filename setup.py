import os
from setuptools import setup

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "simplecms",
    version = "0.0.01",
    author = "jan-karel visser",
    author_email = "jankarelvisser@gmail.com",
    description = ("A simple CMS."),
    license = "LGPL",
    keywords = "basic CMS system",
    url = "https://github.com/jan-karel/simplecms/",
    packages=['simplecms', 'static','application'],
    long_description=read('README.md'),
    classifiers=[
        "Topic :: Utilities",
   
    ],
)