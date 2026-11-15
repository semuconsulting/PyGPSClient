"""
widget_frame.py

Abstract 'Widget' Frame Class for PyGPSClient Application.

All user-selectable widgets should inherit from this class.

Created 23 March 2023

:author: semuadmin (Steve Smith)
:copyright: 2020 semuadmin
:license: BSD 3-Clause
"""

import logging
from abc import ABC, abstractmethod
from tkinter import Frame, Tk, font

from pygpsclient.custom_classes import TAG_WAIT
from pygpsclient.globals import MAXWAIT
from pygpsclient.strings import DLGNODATA, DLGWAITDATA


class WidgetFrame(Frame, ABC):
    """
    Generic Widget frame class.
    """

    def __init__(self, app: Tk, parent: Frame, *args, **kwargs):
        """
        Constructor.

        :param Tk app: reference to main tkinter application
        :param Frame parent: reference to parent frame
        :param args: Optional args to pass to Frame parent class
        :param kwargs: Optional kwargs to pass to Frame parent class
        """

        self.__app = app
        self.logger = logging.getLogger(__name__)
        fontsize = kwargs.pop("fontsize", 12)
        self._data = kwargs.pop("data", "data")

        super().__init__(parent, *args, **kwargs)

        self.width = kwargs.get("width")
        self.height = kwargs.get("height")
        self._font = font.Font(size=fontsize)
        self._fonth = self._font.metrics("linespace")
        self._waiting = True
        self._redraw = True
        self._waits = 0
        self._body()
        self._do_layout()
        self.reset()
        self._attach_events()
        self.enable_messages()
        self.bind("<Configure>", self._on_resize)

    @abstractmethod
    def _body(self):
        """
        Set up frame and widgets.
        """

    @abstractmethod
    def _do_layout(self):
        """
        Arrange frame and widgets in grid.
        """

    def reset(self):
        """
        Reset settings to saved configuration.
        """

    def enable_messages(self, status: bool = True):
        """
        Enable any output messages required by widget.
        """

    def _attach_events(self):
        """
        Bind events to frame.
        """

    def _on_update_config(self, var, index, mode):  # pylint: disable=unused-argument
        """
        Update in-memory configuration if setting is changed.
        """

    def init_frame(self):
        """
        Initialize frame.
        """

    def _on_clear(self, event):  # pylint: disable=unused-argument
        """
        Clear frame.

        :param Event event: clear event
        """

        self.init_frame()

    def _on_resize(self, event):  # pylint: disable=unused-argument
        """
        Resize frame.

        :param Event event: resize event
        """

        self.width, self.height = self.get_size()
        self._redraw = True
        self._on_waiting()

    def _on_waiting(self):
        """
        Display 'waiting for data' alert.
        """

        txt = (
            DLGNODATA.format(data=self._data)
            if self._waits > MAXWAIT
            else DLGWAITDATA.format(data=self._data)
        )
        if self._waiting and hasattr(self, "_canvas"):
            self._canvas.create_alert(txt, tags=TAG_WAIT)

    def get_size(self) -> tuple:
        """
        Get current frame or canvas size.

        :return: window size (width, height)
        :rtype: tuple
        """

        self.update_idletasks()  # Make sure we know about resizing
        if hasattr(self, "_canvas"):
            return self._canvas.winfo_width(), self._canvas.winfo_height()
        return self.winfo_width(), self.winfo_height()
