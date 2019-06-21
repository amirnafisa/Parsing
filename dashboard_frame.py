from tkinter import Frame, Button, OptionMenu, StringVar, Scrollbar, Text, Label, filedialog
from style import *

class ATIDashboard:
    def __init__ (self, master, expand=False, relief="flat"):
        self.frame = Frame(master, relief=relief, borderwidth=4, style=style_frame())
        self.frame.pack(side='top',fill='both', expand=expand)

class ATILabel:
    def __init__ (self, master, text=''):
        self.lbl = Label(master, text=text)
        self.lbl.pack(side='top')

class ATIButton:
    def __init__ (self, master, text, btn_response):
        self.button = Button(master, text=text, command=btn_response, style=style_button())
        self.button.pack(side="left")

class ATIScroll:
    def __init__ (self, master):
        self.scrollbar = Scrollbar(master)
        self.scrollbar.pack(side='right', fill='y')

class ATILog:
    def __init__(self, master, state='disabled', scrollbar=False):
        # make a text box to put the serial output
        self.log = Text(master, width=50, height=2, background='linen', highlightbackground='antique white')

        if scrollbar:
            scrollbar = ATIScroll(master)

            # attach text box to scrollbar
            self.log.config(yscrollcommand=scrollbar.scrollbar.set)
            scrollbar.scrollbar.config(command=self.log.yview)

        self.log.pack(fill='both', expand=1)

    def retrieve_text(self):
        return self.log.get("1.0","end")

    def clear(self):
        self.log.delete('1.0','end')
        self.log.update()

    def add_text(self, text):
        self.log.insert("end", text)
