from tkinter import Tk

import threading
import queue
from dashboard_frame import *
from parse2 import *
from pcfg_grammar import *
from sentence import *
from tkinter.ttk import Progressbar
from time import sleep

class App:
    def __init__(self, master):

        self.root = master
        self.root.protocol("WM_DELETE_WINDOW", self.ask_quit)
        self.set_app_title(master, "Parsing Tool")

        self.main_frame = ATIDashboard(master, expand=True, relief="sunken")
        self.input_frame = ATIDashboard(self.main_frame.frame, expand=True)
        self.input_label = ATILabel(self.input_frame.frame, text='Input Goes Here')
        self.output_frame = ATIDashboard(self.main_frame.frame, expand=True)
        self.output_label = ATILabel(self.output_frame.frame, text='Output Appears Here')
        self.menu_frame = ATIDashboard(self.main_frame.frame, relief="sunken")

        self.log = ATILog(self.input_frame.frame, scrollbar=True)
        self.output_log = ATILog(self.output_frame.frame, scrollbar=True)
        self.output_log.log.config(state="disabled")

        parse_button = ATIButton(self.menu_frame.frame, text="Parse", btn_response=self.parse)

        self.progressbar = Progressbar(mode="determinate", orient="horizontal", length=200)

        self.gr = PCFG_Grammar('./wallstreet.gr')

    def set_app_title(self, master, title):
        top_level = master.winfo_toplevel()
        top_level.title(title)

    def parse(self):

        self.output_log.log.config(state="normal")
        self.output_log.clear()
        self.output_log.log.config(state="disabled")

        sen = Sentence(self.log.retrieve_text())

        self.result_slot = {'result':''}
        self.thread = threading.Thread(target=parse_sen, args=(self.gr, sen, self.result_slot))
        self.thread.daemon = True
        self.progressbar.pack()
        self.log.log.config(state="disabled")
        self.root.config(cursor="wait")
        self.root.update()

        self.thread.start()
        self.progressbar.start()
        self.root.after(50, self.check_completed)

    def check_completed(self):
        if self.thread.is_alive():
            self.root.after(50, self.check_completed)
        else:
            # if thread has finished stop and reset everything
            self.progressbar.stop()
            self.progressbar.pack_forget()
            self.log.log.config(state="normal")

            self.output_log.log.config(state="normal")
            self.output_log.add_text(self.result_slot['result'])
            self.output_log.log.config(state="disabled")

            self.root.config(cursor="")
            self.root.update()

    def ask_quit(self):
        self.root.destroy()
        self.root.quit()

root = Tk()
root.minsize(width=500, height=100)
root.attributes('-fullscreen', True)
app = App(root)

root.mainloop()
