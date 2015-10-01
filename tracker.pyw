import json, atexit, sqlite3, os
from Tkinter import *

class Tracker:
    options = {}
    mod_select_var = None
    poll_delay = 5000
    root = Tk()
    dbpath = os.environ['USERPROFILE'] + "/Documents/My Games/Sid Meier's Civilization 5/ModUserData/exported streaming info-1.db"
    last_turn = -1
    policies = [None] * 111
    wonders = [None] * 111
    beliefs = [None] * 111



    def load_options(self):
        with open("options.json", "r") as json_file:
            self.options = json.load(json_file)
        self.poll_delay = self.options["poll_delay"]

    def save_options(self):
        self.options["mod-select"] = self.mod_select_var.get()

        with open("options.json", "w") as json_file:
            json.dump(self.options, json_file, indent=3, sort_keys=True)

    def load_definitions(self, *args):
        mod = self.mod_select_var.get()
        with open("definitions-" + mod + ".json", "r") as json_file:
            definitions = json.load(json_file)
            #todo: populate policies, wonders, beliefs


    def run(self):
        self.root.wm_title("Civ 5 Tracker")
        self.root.geometry('300x100')
        self.root.resizable(False, False)

        atexit.register(self.save_options)
        self.load_options()


        self.mod_select_var = StringVar(name="mod-select", value=self.options.get("mod-select"))
        # "mod-select":"bnw"
        Radiobutton( self.root, text="Vanilla Brave New World", variable=self.mod_select_var, value="bnw").pack(anchor=CENTER)
        Radiobutton( self.root, text="No Quitters Mod", variable=self.mod_select_var, value="nqmod").pack(anchor=CENTER)
        self.mod_select_var.trace("w", self.load_definitions)
        self.load_definitions()

        self.poll_database()
        mainloop()


    def poll_database(self):
        self.root.after(self.poll_delay, self.poll_database)

        conn = sqlite3.connect(self.dbpath)
        c = conn.cursor()

        c.execute("SELECT Value FROM SimpleValues WHERE Name='turn'")
        turn = c.fetchone()
        # if the turn didnt change, then we dont need to do any more until the next poll
        if turn == self.last_turn:
            return

        self.last_turn = turn
        c.execute("SELECT Value FROM SimpleValues WHERE Name='buildings'")
        building_ids = c.fetchone()

        c.execute("SELECT Value FROM SimpleValues WHERE Name='policies'")
        policy_ids = c.fetchone()

        c.execute("SELECT Value FROM SimpleValues WHERE Name='religion'")
        belief_ids = c.fetchone()

        #todo: format the info




track = Tracker()
track.run()