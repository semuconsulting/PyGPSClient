"""
Entry point for PyGPSClient Application.

Created on 12 Sep 2020

:author: semuadmin
:copyright: SEMU Consulting © 2020
:license: BSD 3-Clause
"""

from tkinter import Tk
from pygpsclient.app import App

if __name__ == "__main__":
    ROOT = Tk()
    APP = App(ROOT)
    ROOT.mainloop()
