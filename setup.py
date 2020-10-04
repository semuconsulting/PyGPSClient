#!/usr/bin/env python
'''
Setup script for PyGPSClient Application

python setup.py sdist bdist_wheel

Created on 12 Sep 2020

@author: semuadmin
'''

from setuptools import setup, find_packages

from version import VERSION

setup(
    name="PyGPSClient",
    version=VERSION,
    packages=find_packages(),
    scripts=["__main__.py"],

    install_requires=["pyubx2>=0.1.3", "pynmea2>=1.15.0", "requests>=2.24.0",
                      "Pillow>=7.2.0", "pyserial>=3.4"],

    package_data={
        "pygpsclient": ["resources/*.gif", "resources/*.png",
                     "resources/*.ico", "resources/*.icns",
                     "images/*.png"],
    },

    author="semuadmin",
    author_email="semuadmin@semuconsulting.com",
    description="PyGPSClient GPS Client",
    long_description="NMEA & UBX GPS Client application written in Python3 and tkinter",
    keywords="PyGPSClient GPS NMEA UBX",
    platforms="Windows, MacOS, Linux",
    license="BSD 3-Clause 'Modified' License",
    url="https://github.com/semuconsulting/PyGPSClient",
    project_urls={
        "Bug Tracker": "https://github.com/semuconsulting/PyGPSClient",
        "Documentation": "https://github.com/semuconsulting/PyGPSClient",
        "Source Code": "https://github.com/semuconsulting/PyGPSClient",
    },
    classifiers=[
        "License :: OSI Approved :: BSD License",
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: MacOS X',
        'Environment :: X11 Applications',
        'Environment :: Win32 (MS Windows)',
        'Environment :: Console',
        'Intended Audience :: End Users/Desktop',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 3.8',
        'Topic :: Desktop Environment',
        'Topic :: Terminals :: Serial',
    ]

)
