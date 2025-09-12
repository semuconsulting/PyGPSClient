
# PyGPSClient Installation

[Basics](#basics) |
[Prerequisites](#prereqs) |
[Install with pip](#pip) |
[Install with pipx](#pipx) |
[Install with script](#script) |
[Troubleshooting](#troubleshooting) |
[License](#license) |
[Author Information](#author)

## <a name="basics">Some Basics on Python Installation</a>

*Experienced Python users can [skip](#prereqs) this section.*

### <a name="venv">global vs venv</a>

There are, in essence, two options available when installing Python applications like PyGPSClient using the standard [`pip`](https://pypi.org/project/pip/) installation manager:
1. Install into the global system environment¹.
2. Install into a dedicated virtual environment ('venv').

Though by no means mandatory, it is [generally considered best practice](https://peps.python.org/pep-0405/) to use a separate virtual environment for each application, as this allows you to:

1. Install application-specific packages without messing up your global Python installation.
1. Use different versions of the same package across applications.
1. Keep your application dependencies clean and organized.

Some platforms (e.g. Ubuntu Linux) **enforce** the use of virtual environments via a so-called 'Externally Managed Environment' constraint². Attempting to install a package into the global environment will result in an `error: externally-managed-environment` error.

¹ In practice, 'global' generally means the user's home environment. Installing into the platform's global system environment typically results in a `Defaulting to user installation because normal site-packages is not writeable` warning.

² Though not recommended, this constraint can generally be removed by simply deleting or renaming the file `/usr/lib/python3.x/EXTERNALLY-MANAGED`.

### <a name="format">sdist vs wheel</a>

There are two file formats in common use for distributing Python packages:

1. sdist (source distribution ) - conceptually, an archive of the source code in raw form. Concretely, an sdist is a TAR compressed archive (`.tar.gz`) containing the source code plus an additional special file called PKG-INFO, which holds the project metadata. Packages with 'extension modules', written in languages like C, C++ and Rust, need to be compiled into platform-dependent machine code *at time of installation*. This may in turn require certain external 'build dependencies' (*files required for successful code compilation*) to be pre-installed on the installation platform.
1. wheel (aka binary distribution or bdist) - conceptually, a wheel contains exactly the files that need to be copied when installing the package. There is a big difference between sdists and wheels for packages with 'extension modules'. With these packages, wheels do not contain source code (like C source files) but compiled, executable code (like `.so` files on Linux or `.dll` on Windows). Concretely, wheels are ZIP compressed files (`.whl`) containing Python source code and any non-Python compiled executables.

By default, pip will look for wheel first, and only resort to using sdist where no wheel is available for the installation platform.

For pure Python packages like PyGPSClient and its subsidiary [GNSS utilities](https://github.com/semuconsulting), the differences between sdist and wheel distributions are to some extent academic. The distinction is, however, relevant for some of PyGPSClient's optional dependencies (e.g. `cryptography` and `rasterio`) - see [troubleshooting](#troubleshooting) for further details.

### <a name="binaries">site_packages and binaries directories</a>

pip installs application source code and distribution information into a `../site_packages` directory.

If the installation also entails one or more binary executables, these will be installed into a `../bin` directory (or `..\Scripts` on Windows). In the case of PyGPSClient, for example, pip installs a binary executable `../bin/pygpsclient` (or `..\Scripts\pygpsclient.exe` on Windows), which allows the application to be executed from the command line or standard application shortcut³.

The exact location of the site_packages and binary directories will depend on the platform and installation specifics. A virtual environment ('venv') will contain its own dedicated site_packages and binary directories e.g. `../venv/bin` and `../venv/lib/python3.13/site_packages`. 

**NB To facilitate operation, it is highly recommended that these directories are included in your system's PATH environment variable**.

³ The `pygpsclient` executable does not actually contain compiled Python source code - it is simply an executable form of the standard `python -m pygpsclient` command.

## <a name="prereqs">Prerequisites</a>

### All platforms

In the following, `python3` & `pip` refer to the Python 3 executables. You may need to substitute `python` for `python3`, depending on your particular environment (*on Windows it's generally `python`*). 

- Python >= 3.9
- Tk (tkinter) >= 8.6, < 9.0⁴ (*tkinter is a commonly used library for developing Graphical User Interfaces (GUI) in Python*)
- Screen resolution >= 640 x 400; Ideally 1920 x 1080, though at lower screen resolutions (<= 1024 width), top level dialogs will be resizable and scrollable.

**NB** It is highly recommended to use the latest official [Python.org](https://www.python.org/downloads/) installation package for your platform, rather than any pre-installed version.

**NB** It is highly recommended that the Python 3 [binaries](#binaries) (`../bin` or `..\Scripts`) directory is included in your PATH (*most standard Python 3 installation packages will do this automatically if you select the 'Add to PATH' option during installation*).

### Windows 10 or later

Normally installs without any additional steps.

### MacOS 13 or later

⁴ The version of Python supplied with some older Apple MacOS platforms includes a [deprecated version of tkinter](https://www.python.org/download/mac/tcltk/) (8.5). Use an official [Python.org](https://www.python.org/downloads/macos) installation package instead. 

**NB:** Python does ***NOT*** require Homebrew or MacPorts to be installed on MacOS. The Python organisation provides serviceable [64-bit universal installation packages](https://www.python.org/downloads/macos/) for all current and legacy versions of Python, including release candidates. 

However, if you wish to install Python using [Homebrew](https://brew.sh/) to take advantage of certain non-default configurations (*e.g. support for sqlite3 extensions*), use the `python-tk` formula rather than `python`, e.g. 

```shell
brew install python-tk@3.13 libspatialite
```

Note also that the Homebrew formulae for python-tk>=3.12 include the latest tkinter 9.0 (rather than 8.6). There are known compatibility issues between tkinter 9.0 and other Python packages (*e.g. ImageTk*) on some platform configurations, which may result in PyGPSClient being unable to load. If you encounter these issues, consider using `brew install python-tk@3.11` or an official [Python.org](https://www.python.org/downloads/macos) installation package instead.

### Linux (including Raspberry Pi OS)

Some Linux distributions may not include the necessary pip, tkinter or Pillow imaging libraries by default. They may need to be installed separately, e.g.:

```shell
sudo apt install python3-pip python3-tk python3-pil python3-pil.imagetk libjpeg-dev zlib1g-dev tk-dev
```

## <a name="userpriv">User Privileges</a>

To access the serial port on most Linux platforms, you will need to be a member of the 
`tty` and/or `dialout` groups. Other than this, no special privileges are required.

```shell
usermod -a -G tty myuser
```

## <a name="pip">Install using pip</a>

The recommended way to install the latest version of `PyGPSClient` is with [pip](http://pypi.python.org/pypi/pip/):

```shell
python3 -m pip install --upgrade pygpsclient
```

It is generally considered best practice to install into a [virtual environment](#global-vs-venv):

```shell
python3 -m venv pygpsclient
source pygpsclient/bin/activate # (or .\pygpsclient\Scripts\activate on Windows)
python3 -m pip install --upgrade pygpsclient
pygpsclient
```

To deactivate the virtual environment:

```shell
deactivate
```

To reactivate and run from the virtual environment:
```shell
source pygpsclient/bin/activate # (or .\pygpsclient\Scripts\activate on Windows)
pygpsclient
```

To upgrade PyGPSClient to the latest version from the virtual environment:
```shell
source pygpsclient/bin/activate # (or .\pygpsclient\Scripts\activate on Windows)
python3 -m pip install --upgrade pygpsclient
```

The pip installation process places an executable file in the Python binaries folder (`../bin/pygpsclient` on Linux & MacOS, `..\Scripts\pygpsclient.exe` on Windows). The PyGPSClient application may be started by double-clicking on this executable file from your file manager or, if the binaries folder is in your PATH⁵, by opening a terminal and typing (all lowercase):
```shell
pygpsclient
````

`pygpsclient` accepts optional command line arguments for a variety of configurable parameters. These will override any saved configuration file settings. Type the following for help:
```shell
pygpsclient -h
```

⁵ **NB:** If the Python 3 binaries folder is *not* in your PATH, you will need to add the fully-qualified path to the `pygpsclient` executable in the command above.

<a name="binaries">**Tip:**</a> The location of the relevant binaries folder(s) can usually be found by executing the following commands:

```shell
python3 -c "import os,sysconfig;print(sysconfig.get_path('scripts'))"
python3 -c "import os,sysconfig;print(sysconfig.get_path('scripts',f'{os.name}_user'))"
```

**NB** The pip installation process does not automatically create a desktop application launcher, but this can be done manually - see [APPLAUNCH](https://github.com/semuconsulting/PyGPSClient/blob/master/APPLAUNCH.md).

### Optional dependencies

The following Python packages are optional:

1. rasterio - required for automated extents detection in the PyGPSClient [Import Custom Map](https://github.com/semuconsulting/PyGPSClient/blob/master/images/importcustommap.png?raw=true) facility.
1. cryptography - required to decrypt SPARTN messages in the PyGPSClient [console](https://github.com/semuconsulting/PyGPSClient/blob/master/images/spartn_consolelog.png?raw=true).

```shell
python3 -m pip install rasterio
python3 -m pip install cryptography
```

... or, on some Linux distributions:

```shell
sudo apt install python3-rasterio
```

(see [troubleshooting](#troubleshooting) below for potential issues on some Linux / ARM platforms)

## <a name="pipx">Install using pipx</a>

[pipx](https://pipx.pypa.io/latest/installation/) is essentially a wrapper around the standard `pip` command which provides simplified syntax for virtual environment installation:

```shell
python3 -m pip install pipx # if not already installed
pipx ensurepath # ensures venv binaries folder is in PATH
pipx install pygpsclient
```

pipx will typically create a virtual environment in the user's home folder e.g. `/home/user/.local/share/pipx/venvs/pygpsclient` or `C:\Users\user\pipx\venvs\pygpsclient>`.

## <a name="script">Install using installation script</a>

The following scripts require sudo/admin privileges and will prompt for the sudo password.

### Debian Linux
An example [installation shell script](https://github.com/semuconsulting/PyGPSClient/blob/master/examples/pygpsclient_debian_install.sh) is available for use on most vanilla 64-bit Debian-based environments with Python>=3.9, including Raspberry Pi and Ubuntu. To run this installation script, download it to your Raspberry Pi or other Debian-based workstation and - from the download folder - type:

```shell
chmod +x pygpsclient_debian_install.sh
./pygpsclient_debian_install.sh
```

### MacOS
A similar [installation shell script](https://github.com/semuconsulting/PyGPSClient/blob/master/examples/pygpsclient_macos_install.sh) is available for MacOS 13 or later running a ZSH shell (*Homebrew or MacPorts are **NOT** required*). This will also install the latest official version of Python 3 with tkinter 8.6. Download the script to your Mac and - from the download folder - type:

```shell
./pygpsclient_macos_install.sh
```

### Windows

TBC. Anyone conversant with PowerShell is welcome to contribute an equivalent installation script for Windows 11.

---

## <a name="troubleshooting">Troubleshooting</a>

1. The optional `rasterio` package is only available as an [sdist](#sdist-vs-wheel) on some Linux / ARM platforms (including Raspberry Pi OS), and the consequent [GDAL](https://gdal.org/en/stable/) build and configuration requirements may be problematic e.g. `WARNING:root:Failed to get options via gdal-config`. Refer to [rasterio installation](https://rasterio.readthedocs.io/en/stable/installation.html) and [GDAL installation](https://gdal.org/en/stable/) for assistance but - *be warned* - the process is **not** for the faint-hearted.
  
   In practice, `rasterio` is only required for automatic extents detection in PyGPSClient's Import Custom Map facility. As a workaround, extents can be entered manually, or you can try importing maps on a different platform and then copy-and-paste the relevant `usermaps_l` extents configuration to the target platform.

1. The optional `cryptography` package is only available as an [sdist](#sdist-vs-wheel) on some 32-bit Linux / ARM platforms (including Raspberry Pi OS), and the consequent OpenSSL build requirements may be problematic e.g. `Building wheel for cryptography (PEP 517): finished with status 'error'`. Refer to [cryptography installation](https://github.com/semuconsulting/pyspartn/blob/main/cryptography_installation/README.md) for assistance. To install PyGPSClient *without* cryptography, first install the `pyspartn` package with the `--no-deps` option i.e. `python3 -m pip install pyspartn --no-deps`, and *then* install PyGPSClient.

---
## <a name="license">License</a>

![License](https://img.shields.io/github/license/semuconsulting/PyGPSClient.svg)

BSD 3-Clause License

Copyright &copy; 2020, SEMU Consulting
All rights reserved.

Application icons from [iconmonstr](https://iconmonstr.com/license/) &copy;.

---
## <a name="author">Author Information</a>

semuadmin@semuconsulting.com