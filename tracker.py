import json, atexit, sqlite3, os, subprocess
from Tkinter import *
from sys import platform as _platform

class Tracker:
    def __init__(self):
        self.options = {}
        self.mod = "bnw"
        self.poll_delay = 5000
        self.root = Tk()


        if _platform == 'win32':
            self.dbdir = os.environ['USERPROFILE'] + "/Documents/My Games/Sid Meier's Civilization 5/ModUserData/"
        elif _platform == 'darwin':
            self.dbdir = os.environ['HOME'] + "/Documents/Aspyr/Sid Meier's Civilization 5/ModUserData/"
        else:
            # UNTESTED, LINUX
            self.dbdir = os.environ['HOME'] + "/.local/share/Aspyr/Sid Meier's Civilization 5/ModUserData/"
        self.dbpath = ""
        self.set_dbpath()

        output_dir = 'output files'
        
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        self.wonders_file = output_dir + '/wonders.txt'
        self.policies_file = output_dir + '/pol.txt'
        self.religion_file = output_dir + '/rel.txt'
        
        self.last_turn = -1
        self.policyNames = [None] * 111
        self.policyTrees = [None] * 111
        self.policyRootIds = []
        self.buildingNames = [None] * 162
        self.wondersById = [False] * 162
        self.beliefNames = [None] * 69
        self.textlog = None
        self.server_subprocess = None

        # gets created in load_options
        self.each_thing_new_line = None

    def set_dbpath(self):
        self.dbpath = self.dbdir + "exported streaming info-1.db"

    def load_definitions(self):
        with open("definitions-" + self.mod + ".json", "r") as json_file:
            definitions = json.load(json_file)
            for key,value in definitions["policy-trees"].iteritems():
                effectiveKey = ""
                # todo maybe we want to add a thing that shows what levels their ideology upgrades have?
                # for now we just strip off the 1,2,3 at the end
                if key.startswith("freedom"):
                    effectiveKey = "Freedom"
                elif key.startswith("order"):
                    effectiveKey = "Order"
                elif key.startswith("autocracy"):
                    effectiveKey = "Autocracy"
                else:
                    effectiveKey = str(key)
                for policyId in value:
                    self.policyTrees[policyId] = effectiveKey
            for ID in definitions["policy-root-ids"]:
                self.policyRootIds.append(int(ID))

        self.log("Connecting to database to load localized names")
        conn = sqlite3.connect(self.dbpath)
        c = conn.cursor()

        c.execute("SELECT Value FROM SimpleValues WHERE Name='buildingNames'")
        resp = c.fetchone()[0]
        for line in resp.split("\n"):
            pair = line.split(":", 1)
            self.buildingNames[int(pair[0])] = pair[1]

        c.execute("SELECT Value FROM SimpleValues WHERE Name='policyNames'")
        resp = c.fetchone()[0]
        for line in resp.split("\n"):
            pair = line.split(":", 1)
            self.policyNames[int(pair[0])] = pair[1]

        c.execute("SELECT Value FROM SimpleValues WHERE Name='beliefNames'")
        resp = c.fetchone()[0]
        for line in resp.split("\n"):
            pair = line.split(":", 1)
            self.beliefNames[int(pair[0])] = pair[1]

        c.execute("SELECT Value FROM SimpleValues WHERE Name='wonderNames'")
        resp = c.fetchone()[0]
        for line in resp.split("\n"):
            pair = line.split(":", 1)
            self.wondersById[int(pair[0])] = True
        self.log("Done loading initial info from database")



    def load_options(self):
        with open("options.json", "r") as json_file:
            self.options = json.load(json_file)
        self.poll_delay = self.options["poll_delay"]
        dbdir_override = self.options['dbdir-override']
        if dbdir_override and len(dbdir_override) > 0:
            self.dbdir = dbdir_override
            self.set_dbpath()

        self.each_thing_new_line = IntVar(name="each_thing_new_line", value=self.options.get("each_thing_new_line"))

    def save_options(self):
        self.options["mod-select"] = self.mod
        with open("options.json", "w") as json_file:
            json.dump(self.options, json_file, indent=3, sort_keys=True)

    def atexit(self):
        self.save_options()
        if self.server_subprocess:
            self.server_subprocess.kill()
    def log(self, msg):
        if self.textlog:
            self.textlog.config(state=NORMAL)
            self.textlog.insert(END,msg + "\n")
            self.textlog.config(state=DISABLED)

    def ui_option_change_listener(self, *args):
        self.options["each_thing_new_line"] = self.each_thing_new_line.get()
        self.save_options()
        self.update_from_database()

    def run(self):
        self.root.wm_title("Civ 5 Tracker")
        self.root.resizable(False, False)

        self.load_options()
        atexit.register(self.atexit)

        scroll = Scrollbar(self.root)
        self.textlog = Text(self.root, height=8, width=80, state=DISABLED)
        scroll.pack(side=RIGHT, fill=Y)
        self.textlog.pack(side=TOP, fill=Y)
        scroll.config(command=self.textlog.yview)
        self.textlog.config(yscrollcommand=scroll.set)

        #self.mod_select_var = StringVar(name="mod-select", value=self.options.get("mod-select"))
        #Radiobutton( self.root, text="Vanilla Brave New World", variable=self.mod_select_var, value="bnw").pack(anchor=CENTER)
        #Radiobutton( self.root, text="No Quitters Mod", variable=self.mod_select_var, value="nqmod").pack(anchor=CENTER)
        #self.mod_select_var.trace("w", self.reload_mod())

        Radiobutton( self.root, text="Use commas to separate things", variable=self.each_thing_new_line, value=0).pack(anchor=CENTER)
        Radiobutton( self.root, text="Use new lines to separate things", variable=self.each_thing_new_line, value=1).pack(anchor=CENTER)
        self.each_thing_new_line.trace("w", self.ui_option_change_listener)

        if os.path.isfile("server/civ5_tracker_webserver.exe"):
            self.log("Starting integrated server from .exe")
            with open("serverlog.txt", "w") as serverlog:

                self.server_subprocess = subprocess.Popen('"../server/civ5_tracker_webserver.exe"',shell=True,cwd=os.path.join(os.getcwd(), "output files"),stdout=serverlog, stderr=serverlog)
        elif os.path.isfile("civ5_tracker_webserver.py"):
            self.log("Starting integrated server from .py")
            self.server_subprocess = subprocess.Popen("python ../civ5_tracker_webserver.py",shell=True,cwd=os.path.join(os.getcwd(), "output files"))
        else:
            self.log("No integrated server found! (CLR browser won't work)")

        self.log("Loading definitions")
        if os.path.isdir(self.dbdir):
            try:
                self.load_definitions()
                self.poll_database()
            except sqlite3.OperationalError:
                self.log("ERROR: couldn't find the 'export info' database. You have to start a game of civ5 at least once with the Export Info Mod running, then restart this program.")
        else:
            self.log("ERROR: couldn't find civ5 user files at '" + self.dbdir + "'. Try editing options.json and putting the correct location of that directory into the 'dbdir-override' setting")
        mainloop()

    def poll_database(self):
        self.root.after(self.poll_delay, self.poll_database)

        conn = sqlite3.connect(self.dbpath)
        c = conn.cursor()

        c.execute("SELECT Value FROM SimpleValues WHERE Name='turn'")
        turn = c.fetchone()[0]
        # if the turn didnt change, then we dont need to do any more until the next poll
        if turn == self.last_turn:
            return
        self.log("turn " + str(turn))
        self.last_turn = turn
        self.update_from_database(c)

    def update_from_database(self, c=None):
        if c is None:
            conn = sqlite3.connect(self.dbpath)
            c = conn.cursor()

        c.execute("SELECT Value FROM SimpleValues WHERE Name='buildings'")
        building_ids = c.fetchone()

        c.execute("SELECT Value FROM SimpleValues WHERE Name='policies'")
        policy_ids = c.fetchone()

        c.execute("SELECT Value FROM SimpleValues WHERE Name='religion'")
        belief_ids = c.fetchone()


        if self.each_thing_new_line.get() == 1:
            separator = "\n"
        else:
            separator = ", "

        wonder_names = []
        if building_ids and building_ids[0]:
            for building_id in str(building_ids[0]).split(" "):
                ID = int(building_id)
                if self.wondersById[ID]:
                    name = self.buildingNames[ID]
                    if name:
                        wonder_names.append(name)
        if len(wonder_names) == 0:
            wonder_names.append("none")
        with open(self.wonders_file, "w") as f:
            wonder_output = separator.join(wonder_names) + "  "
            f.write(wonder_output)

        belief_names = []
        # sometimes there are two copies of a belief in there, so only show each once
        beliefs_seen_already = {}
        if belief_ids and belief_ids[0]:
            for belief_id in str(belief_ids[0]).split(" "):
                ID = int(belief_id)
                if ID >= 0 and ID not in beliefs_seen_already:
                    name = self.beliefNames[ID]
                    if name:
                        belief_names.append(name)
                        beliefs_seen_already[ID] = True
        if len(belief_names) == 0:
            belief_names.append("none")
        with open(self.religion_file, "w") as f:
            belief_output = separator.join(belief_names) + "  "
            f.write(belief_output)

        # count how many policies are in each branch, so we get stuff like "Honor 0, Liberty 3"
        # its confusing because of the way the root is itself a policy but it doesnt have itself as a parent
        # and ideologies having no policy for their root makes it annoying to do a different way
        policy_tree_sizes = {}
        if policy_ids and policy_ids[0]:
            for policy_id in str(policy_ids[0]).split(" "):
                ID = int(policy_id)
                tree_root = self.policyTrees[ID]
                if tree_root or ID in self.policyRootIds:

                    if tree_root in policy_tree_sizes:
                        policy_tree_sizes[tree_root] += 1
                    else:
                        if tree_root:
                            policy_tree_sizes[tree_root] = 1
                        else:
                            policy_tree_sizes[str(ID)] = 0



        policy_entries = []
        for tree_root in policy_tree_sizes:
            if str(tree_root).isdigit():
                policy_entries.append(self.policyNames[int(tree_root)] + " " + str(policy_tree_sizes[tree_root]))
            else:
                # its an ideology
                policy_entries.append(tree_root + " " + str(policy_tree_sizes[tree_root]))
        if len(policy_entries) == 0:
            policy_entries.append("none")
        with open(self.policies_file, "w") as f:
            policy_output = separator.join(policy_entries) + "  "
            f.write(policy_output)

        with open("output files/template.html", "r") as template:
            data = template.read()
            data = data.replace("%pol%", policy_output).replace("%rel%", belief_output).replace("%wonders%", wonder_output)
            with open("output files/sidebar.html", "w") as sidebarhtml:
                sidebarhtml.write(data)


track = Tracker()
track.run()
