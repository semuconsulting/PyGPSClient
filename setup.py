#!/usr/bin/env python
'''
Setup script for PyGPSClient Application

python setup.py sdist bdist_wheel

Created on 12 Sep 2020

@author: semuadmin
'''

from setuptools import setup, find_packages
from pygpsclient import version as VERSION

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="PyGPSClient",
    version=VERSION,
    packages=find_packages(exclude=['tests', 'references', 'images']),
    install_requires=["pyubx2>=1.0.3", "pynmea2>=1.15.0", "requests>=2.24.0",
                      "Pillow>=7.2.0", "pyserial>=3.4"],
    package_data={
        "pygpsclient": ["resources/*.gif", "resources/*.png",
                     "resources/*.ico", "resources/*.icns"],
    },
    include_package_data=True,
    author="semuadmin",
    author_email="semuadmin@semuconsulting.com",
    description="PyGPSClient GNSS/GPS Graphical Client",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/semuconsulting/PyGPSClient",
    license="BSD 3-Clause 'Modified' License",
    keywords="PyGPSClient GNSS GPS GLONASS NMEA UBX GIS",
    platforms="Windows, MacOS, Linux",
    project_urls={
        "Bug Tracker": "https://github.com/semuconsulting/PyGPSClient",
        "Documentation": "https://github.com/semuconsulting/PyGPSClient",
        "Source Code": "https://github.com/semuconsulting/PyGPSClient",
    },
    classifiers=[
        "License :: OSI Approved :: BSD License",
        'Development Status :: 4 - Beta',
        'Environment :: MacOS X',
        'Environment :: X11 Applications',
        'Environment :: Win32 (MS Windows)',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Science/Research',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Topic :: Desktop Environment',
        'Topic :: Terminals :: Serial',
        'Topic :: Scientific/Engineering :: GIS'
    ]

)
