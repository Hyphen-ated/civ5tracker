import json, atexit, sqlite3, os
from Tkinter import *
from sys import platform as _platform

class Tracker:
    def __init__(self):
        self.options = {}
        self.mod = "bnw"
        self.poll_delay = 5000
        self.root = Tk()
        
        if _platform == 'win32':
            self.dbpath = os.environ['USERPROFILE'] + "/Documents/My Games/Sid Meier's Civilization 5/ModUserData/exported streaming info-1.db"
        elif _platform == 'darwin':
            self.dbpath = os.environ['HOME'] + "/Documents/Aspyr/Sid Meier's Civilization 5/ModUserData/exported streaming info-1.db"
        else:
            # UNTESTED, LINUX
            self.dbpath = os.environ['HOME'] + "/.local/share/Aspyr/Sid Meier's Civilization 5/ModUserData/exported streaming info-1.db"

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


    def load_definitions(self, *args):
        self.log("Loading definitions")
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

    def save_options(self):
        self.options["mod-select"] = self.mod

        with open("options.json", "w") as json_file:
            json.dump(self.options, json_file, indent=3, sort_keys=True)

    def log(self, msg):
        if self.textlog:
            self.textlog.config(state=NORMAL)
            self.textlog.insert(END,msg + "\n")
            self.textlog.config(state=DISABLED)



    def run(self):
        self.root.wm_title("Civ 5 Tracker")
        self.root.resizable(False, False)

        self.load_options()
        atexit.register(self.save_options)



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

        self.load_definitions()

        self.poll_database()
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
        c.execute("SELECT Value FROM SimpleValues WHERE Name='buildings'")
        building_ids = c.fetchone()

        c.execute("SELECT Value FROM SimpleValues WHERE Name='policies'")
        policy_ids = c.fetchone()

        c.execute("SELECT Value FROM SimpleValues WHERE Name='religion'")
        belief_ids = c.fetchone()


        wonder_names = []
        if building_ids and building_ids[0]:
            for building_id in str(building_ids[0]).split(" "):
                ID = int(building_id)
                if self.wondersById[ID]:
                    name = self.buildingNames[ID]
                    if name:
                        wonder_names.append(name)
        with open(self.wonders_file, "w") as f:
            f.write(", ".join(wonder_names))

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
            f.write(", ".join(belief_names))

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



        policy_output = []
        for tree_root in policy_tree_sizes:
            if str(tree_root).isdigit():
                policy_output.append(self.policyNames[int(tree_root)] + " " + str(policy_tree_sizes[tree_root]))
            else:
                # its an ideology
                policy_output.append(tree_root + " " + str(policy_tree_sizes[tree_root]))
        with open(self.policies_file, "w") as f:
            f.write(", ".join(policy_output))








track = Tracker()
track.run()
