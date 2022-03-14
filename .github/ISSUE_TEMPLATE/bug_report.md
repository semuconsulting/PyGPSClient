---
name: PyGPSClient bug report

about: Create a report to help us improve

title: ''

labels: ''

assignees: semuadmin

---

**Describe the bug**

A clear and concise description of what the bug is.

Please specify the pygpsclient version (`>>> pygpsclient.version`) and, where possible, include:
- A screenshot of the error.
- The error message and full traceback.
- A binary / hexadecimal dump of the UBX data stream (e.g. from PuTTY, screen or u-center).

**To Reproduce**

Steps to reproduce the behaviour:
1. Any relevant device configuration (if other than factory defaults).
2. Any causal UBX command input(s).

**Expected Behaviour**

A clear and concise description of what you expected to happen.

**Desktop (please complete the following information):**

- The operating system you're using [e.g. Windows 10, MacOS Big Sur, Ubuntu Bionic]
- The version of Python you're using (e.g. Python 3.8.3)
- The type of serial connection [e.g. USB, UART1, I2C]

**GNSS/GPS Device (please complete the following information as best you can):**

- Device Model/Generation: [e.g. u-blox NEO-9M]
- Firmware Version: [e.g. SPG 4.03]
- Protocol: [e.g. 32.00]
 
This information is typically output by the device at startup via a series of NMEA TXT messages. It can also be found by polling the device with a UBX MON-VER message. If you're using the PyGPSClient GUI, a screenshot of the UBXConfig window should suffice.

**Additional context**

Add any other context about the problem here.
