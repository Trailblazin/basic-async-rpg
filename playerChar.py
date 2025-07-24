import char

class PlayerChar(char):    
    # TODO:Extend to define a special action list and use a JSON dict replicating Ozma's functionality
    # TODO:Needs a special action List and special action Dict (JSON)
    def CharActionListHandler(self):
        # TODO:Should utilise base job property to assign a list of possible actions permittable by a character
        if str(self.baseJob).lower() == "thief":
            self.actionList = ["Attack", "Thief Gimmicks", "Item", "Shift", "Flee"]
            self.specialActionList = [
                "Lucky Seven",
                "Soul Blade",
                "Shakedown",
                "Thousand Cuts Gambit",
                "Mana Siphon",
            ]
            self.specialActionDict = {
                "Lucky Seven": [7],
                "Soul Blade": [10],
                "Shakedown": [15],
                "Thousand Cuts Gambit": [10],
                "Mana Siphon": [35],
            }
        elif str(self.baseJob).lower() == "warrior":
            self.actionList = ["Attack", "Sword Arts", "Item", "Shift", "Flee"]
            self.specialActionList = [
                "Climhazard",
                "Shock",
                "Minus Strike",
                "Sword Magic",
            ]
            self.specialActionDict = {
                "Climhazard": [35],
                "Shock": [50],
                "Minus Strike": [15],
                "Sword Magic": [0],
            }
        elif str(self.baseJob).lower() == "white mage":
            self.actionList = ["Attack", "White Magicks", "Item", "Shift", "Flee"]
            self.specialActionList = [
                "Valor",
                "Virtue",
                "Esuna",
                "Life",
                "Holy",
                "Curaga",
                "Curaja",
            ]
            self.specialActionDict = {
                "Valor": [15],
                "Virtue": [13],
                "Esuna": [10],
                "Life": [10],
                "Holy": [35],
                "Curaga": [20],
                "Curaja": [45],
            }
        elif str(self.baseJob).lower() == "black mage":
            self.actionList = ["Attack", "Black Magicks", "Item", "Shift", "Flee"]
            self.specialActionList = [
                "Blizzard",
                "Blizzara",
                "Blizzara",
                "Fire",
                "Fira",
                "Firaga",
                "Thunder",
                "Thundara",
                "Thundaga",
                "Flare",
                "Comet",
                "Meteor",
                "Osmose",
            ]
            self.specialActionDict = {
                "Blizzard": [15],
                "Blizzara": [30],
                "Blizzara": [55],
                "Fire": [15],
                "Fira": [30],
                "Firaga": [55],
                "Thunder": [15],
                "Thundara": [30],
                "Thundaga": [55],
                "Flare": [50],
                "Comet": [30],
                "Meteor": [60],
                "Osmose": [2],
            }
        elif str(self.baseJob).lower() == "blue mage":
            self.actionList = ["Attack", "Hybrid Magicks", "Item", "Shift", "Flee"]
            self.specialActionList = [
                "Mighty Guard",
                "Thundara",
                "Blizzara",
                "Fira",
                "Cura",
                "Life",
            ]
            self.specialActionDict = {
                "Mighty Guard": [15],
                "Thundara": [30],
                "Blizzara": [30],
                "Fira": [30],
                "Cura": [15],
                "Life": [10],
            }
        elif str(self.baseJob).lower() == "dragoon":
            self.actionList = ["Attack", "Lancer Techs", "Item", "Shift", "Flee"]
            self.specialActionList = [
                "Jump",
                "Coalescence",
                "White Draw",
                "Cherry Blossom",
                "Drake Burst",
            ]
            self.specialActionDict = {
                "Jump": [15],
                "Coalescence": [10],
                "White Draw": [35],
                "Cherry Blossom": [45],
                "Drake Burst": [25],
            }

    def CharInventoryHandler(self):
        # Base Item Dictionary for all classes
        baseItemDict = {
            "Mega-Potion": {
                "name": "Mega-Potion",
                "power": "2500",
                "type": "healItem",
                "quantity": "3",
            },
            "Xtreme-Potion": {
                "name": "Xtreme-Portion",
                "power": "9999",
                "type": "healItem",
                "quantity": "3",
            },
            "Ether": {
                "name": "Ether",
                "power": "100",
                "type": "healMPItem",
                "quantity": "5",
            },
            "Reaper's Bane": {
                "name": "Reaper's Bane",
                "power": "15",
                "type": "reviveItem",
                "quantity": "5",
            },
        }
        self.itemDict = baseItemDict
        if str(self.baseJob).lower() in ["thief","warrior","dragoon"]:
            self.itemDict["Mega-Potion"]["quantity"] = "5"
            self.itemDict["Xtreme-Potion"]["quantity"] = "5"

        # Helper function to define job class for character

    def JobAllocator(self, job=""):
        job = str(job)
        if job.lower() == "thief":
            print("Allocated Class: Thief\n")
            self.baseJob = "Thief"
            self.currentHP = self.maxHP = 6500
            self.currentMP = self.maxMP = 320
            self.baseJobStatMatrix = [[50, 35, 45], [60, 55, 25], [85, 45, 40]]
            ##TODO: Should return a DmgStatMatrix incorperating custom level modifier
            self.baseDmgStatMatrix = self.DmgStatMatrix = [
                [int(stat * self.GetLevelStatModifier()) for stat in statSet]
                for statSet in self.baseJobStatMatrix
            ]
            self.ElementalMatrix = self.baseElementalMatrix
            return 0
        elif job.lower() == "warrior" or job.lower() == "fighter":
            print("Allocated Class: Warrior\n")
            self.baseJob = "Warrior"
            self.currentHP = self.maxHP = 8000
            self.currentMP = self.maxMP = 250
            self.baseJobStatMatrix = [[60, 50, 35], [30, 50, 10], [100, 40, 30]]
            self.baseDmgStatMatrix = self.DmgStatMatrix = [
                [int(stat * self.GetLevelStatModifier()) for stat in statSet]
                for statSet in self.baseJobStatMatrix
            ]
            self.ElementalMatrix = self.baseElementalMatrix
            return 1
        elif (
            job.lower() == "white mage"
            or job.lower() == "healer"
            or job.lower() == "support"
        ):
            print("Allocated Class: White Mage\n")
            self.baseJob = "White Mage"
            self.currentHP = self.maxHP = 4500
            self.currentMP = self.maxMP = 500
            self.baseJobStatMatrix = [[35, 25, 30], [70, 45, 20], [40, 35, 34]]
            self.baseDmgStatMatrix = self.DmgStatMatrix = [
                [int(stat * self.GetLevelStatModifier()) for stat in statSet]
                for statSet in self.baseJobStatMatrix
            ]
            self.baseElementalMatrix = [[1, 1, 1], [1, 1, 1], [0.75, 1, 1]]
            self.ElementalMatrix = self.baseElementalMatrix
            return 2
        elif (
            job.lower() == "black mage"
            or job.lower() == "wizard"
            or job.lower() == "caster"
            or job.lower() == "mage"
        ):
            print("Allocated Class: Black Mage\n")
            self.baseJob = "Black Mage"
            self.currentHP = self.maxHP = 4000
            self.currentMP = self.maxMP = 550
            self.baseJobStatMatrix = [[45, 30, 35], [80, 60, 15], [35, 40, 32]]
            self.baseDmgStatMatrix = self.DmgStatMatrix = [
                [int(stat * self.GetLevelStatModifier()) for stat in statSet]
                for statSet in self.baseJobStatMatrix
            ]
            self.baseElementalMatrix = [[1, 1, 1], [1, 1, 1], [1, 0.75, 1]]
            self.ElementalMatrix = self.baseElementalMatrix
            return 3
        elif job.lower() == "dragoon" or job.lower() == "lancer":
            print("Allocated Class: Dragoon\n")
            self.baseJob = "Dragoon"
            self.currentHP = self.maxHP = 7500
            self.currentMP = self.maxMP = 350
            self.baseJobStatMatrix = [[52, 45, 25],[60, 35, 35],[75, 40, 39]]
            self.baseDmgStatMatrix = self.DmgStatMatrix = [
                [int(stat * self.GetLevelStatModifier()) for stat in statSet]
                for statSet in self.baseDmgStatMatrix
            ]
            self.ElementalMatrix = self.baseElementalMatrix
            self.dragonCrest = 0
            return 4
        elif (
            job.lower() == "blue mage"
            or job.lower() == "battle mage"
            or job.lower() == "hybrid"
        ):
            print("Allocated Class: Blue Mage\n")
            self.baseJob = "Blue Mage"
            self.currentHP = self.maxHP = 5500
            self.currentMP = self.maxMP = 450
            self.baseJobStatMatrix = [[46, 35, 30], [65, 50, 19], [65, 35, 20]]
            self.baseDmgStatMatrix = self.DmgStatMatrix = [
                [int(stat * self.GetLevelStatModifier()) for stat in statSet]
                for statSet in self.baseJobStatMatrix
            ]
            self.ElementalMatrix = self.baseElementalMatrix
            return 5
        else:
            print("Base Job selection invalid, defaulting to Thief Class Allocation...")
            self.JobAllocator("Thief")
        self.CharActionListHandler()
        self.CharInventoryHandler()
