import json, atexit
from Tkinter import *

class Tracker:
    options = {}
    var = None
    poll_delay = 5000
    root = Tk()

    def load_options(self):
        with open("options.json", "r") as json_file:
            self.options = json.load(json_file)
        self.poll_delay = self.options["poll_delay"]

    def save_options(self):
        self.options["mod-select"] = self.var.get()

        with open("options.json", "w") as json_file:
            json.dump(self.options, json_file, indent=3, sort_keys=True)


    def run(self):
        self.root.wm_title("Civ 5 Tracker")
        self.root.geometry('300x100')
        self.root.resizable(False, False)

        atexit.register(self.save_options)
        self.load_options()


        self.var = StringVar(name="mod-select", value=self.options.get("mod-select"))
        # "mod-select":"bnw"
        Radiobutton( self.root, text="Vanilla Brave New World", variable=self.var, value="bnw").pack(anchor=CENTER)
        Radiobutton( self.root, text="No Quitters Mod", variable=self.var, value="nqmod").pack(anchor=CENTER)

        self.poll_database()
        mainloop()


    def poll_database(self):
        print("yeah")
        self.root.after(self.poll_delay, self.poll_database)



track = Tracker()
track.run()