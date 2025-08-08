# Python Program to make a scrollable frame
# using Tkinter

from tkinter import *
from datetime import datetime


class ScrollBarDemo(Toplevel):

    # constructor
    def __init__(self):

        def exit():

            lab.set(f"exiting {datetime.now()}...")
            l.update()

        # create root window
        super().__init__()
        self.title("Container")

        lab = StringVar()
        lab.set("this is a status label")

        # create widgets
        lf = Frame(self)
        l = Label(lf, textvariable=lab, anchor=W)
        b = Button(lf, text="EXIT", command=exit)
        h = Scrollbar(self, orient="horizontal")
        v = Scrollbar(self)
        c = Canvas(
            self, width=250, height=250, xscrollcommand=h.set, yscrollcommand=v.set
        )
        sf = Frame(c)

        # set layout
        c.grid(column=0, row=0, sticky=(N, S, E, W))
        h.grid(column=0, row=1, sticky=(E, W))
        v.grid(column=1, row=0, sticky=(N, S))
        lf.grid(column=0, row=2, sticky=(W, E))
        l.grid(column=0, row=0, sticky=(W, E))
        b.grid(column=1, row=0, sticky=E)

        # create scrollable frame
        c.create_window((0, 0), window=sf, anchor=NW)
        c.bind(
            "<Configure>",
            lambda e: c.config(scrollregion=c.bbox(ALL)),
        )
        h.config(command=c.xview)
        v.config(command=c.yview)

        # populate text widgets
        t1 = Text(sf, width=35, height=35, wrap=NONE)
        t2 = Text(sf, width=35, height=35, wrap=NONE)
        for i in range(50):
            t1.insert(END, f"this is some text {i}\n")
            t2.insert(END, f"this is some more text {i}\n")
        t1.grid(column=0, row=0, sticky=(N, S, W, E))
        t2.grid(column=1, row=0, sticky=(N, S, W, E))

        # set column and row weights
        # these goven the 'expansion' of the frames on resize
        self.grid_columnconfigure(0, weight=10)
        self.grid_rowconfigure(0, weight=10)
        lf.grid_columnconfigure(0, weight=10)
        colsp, rowsp = c.grid_size()
        for i in range(colsp):
            sf.grid_columnconfigure(i, weight=10)
        for i in range(rowsp):
            sf.grid_rowconfigure(i, weight=10)


# create an object to Scrollbar class
root = Tk()
root.title("Main App")
s = ScrollBarDemo()
root.mainloop()
