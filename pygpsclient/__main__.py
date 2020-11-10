"""
Entry point for PyGPSClient Application.

Created on 12 Sep 2020

@author: semuadmin
"""

from tkinter import Tk
from pygpsclient.app import App

if __name__ == "__main__":
    ROOT = Tk()
    APP = App(ROOT)
    ROOT.mainloop()
