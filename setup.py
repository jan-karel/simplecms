import os
from setuptools import setup

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
doc = '''

Nothing yet to report

'''

setup(
    name = "simplecms",
    version = "0.0.06",
    author = "jan-karel visser",
    author_email = "jankarelvisser@gmail.com",
    description = ("A basic MVC framework."),
    license = "LGPL",
    platforms ="ALL",
    keywords = "basic CMS system",
    url = "https://github.com/jan-karel/simplecms/",
    packages=['simplecms'],
    long_description=doc,
    classifiers=[
        "Topic :: Utilities",
    'Programming Language :: Python :: 2',
    'Programming Language :: Python :: 2.6',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.2',
    'Programming Language :: Python :: 3.3',
    'Programming Language :: Python :: 3.4',        
   
    ],
)