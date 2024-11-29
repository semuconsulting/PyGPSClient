"""
confirm_box.py

Confirm action dialog class.
Provides better consistency across different OS platforms
than using messagebox.askyesno()

Created on 17 Apr 2021

:author: semuadmin
:copyright: 2020 SEMU Consulting
:license: BSD 3-Clause

"""

from tkinter import Button, Label, Toplevel, W


class ConfirmBox(Toplevel):
    """
    Confirm action dialog class.
    Provides better consistency across different OS platforms
    than using messagebox.askyesno()

    Returns True if OK, False if Cancel
    """

    def __init__(self, parent, title, prompt):
        """
        Constructor

        :param parent: parent dialog
        :param string title: title
        :param string prompt: prompt to be displayed
        """

        self.__master = parent
        Toplevel.__init__(self, parent)
        self.title(title)  # pylint: disable=E1102
        self.resizable(False, False)
        Label(self, text=prompt, anchor=W).grid(
            row=0, column=0, columnspan=2, padx=3, pady=5
        )
        Button(self, command=self._on_ok, text="OK", width=8).grid(
            row=1, column=0, padx=3, pady=3
        )
        Button(self, command=self._on_cancel, text="Cancel", width=8).grid(
            row=1, column=1, padx=3, pady=3
        )
        self.lift()  # Put on top of
        self.grab_set()  # Make modal
        self._rc = False

        self._centre()

    def _on_ok(self, event=None):  # pylint: disable=unused-argument
        """
        OK button handler
        """

        self._rc = True
        self.destroy()

    def _on_cancel(self, event=None):  # pylint: disable=unused-argument
        """
        Cancel button handler
        """

        self._rc = False
        self.destroy()

    def _centre(self):
        """
        Centre dialog in parent
        """

        # self.update_idletasks()
        dw = self.winfo_width()
        dh = self.winfo_height()
        mx = self.__master.winfo_x()
        my = self.__master.winfo_y()
        mw = self.__master.winfo_width()
        mh = self.__master.winfo_height()
        self.geometry(f"+{int(mx + (mw/2 - dw/2))}+{int(my + (mh/2 - dh/2))}")

    def show(self):
        """
        Show dialog

        :return: True (OK) or False (Cancel)
        :rtype: bool
        """

        self.wm_deiconify()
        self.wait_window()
        return self._rc
