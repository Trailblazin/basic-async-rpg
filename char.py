"""
Class used to contstruct or handle player characters
"""
from battleConfig import battleParamList
from ff9DmgCalc import basicAttack, specialAttackCalc
from itemhandler import itemDamageCalc, variantItemHandler
import crisisActionHandler
import ff9StatHandler
import ff9StatusHandler


class RPGChar:
    """This is our class reperesenting our boss enemy in our game.

    Contains all of the statistical data for our AI to be used for our RL state observations,
    as well as the actions to be used on each 'phase' of battle and, damage calculation tables for both offensive and defensive calculations
    and all functions replicating the binary-switch dependant finite state machine shown in Final Fantasy IX.
    These will be used to create an erratic AI which acts unpredictably and will operate until its or the other 'party members' have HP values less than or equal to zero.

    Attributes
    ----------
    Name : str
        String holding the name 'Ozma'
    currentHP : int
        Integer holding the current HP value of Ozma.
    maxHP : int
        Integer holding the maximum HP value of Ozma.
    currentMP : int
        Integer holding the current MP value of Ozma.
    maxMP : int
        Integer holding the max MP value of Ozma.
    baseStrength : int 
        Integer holding the base Strength value of Ozma.
    currentStrength : int
        Integer holding the current Strength value of Ozma.
    baseDefense : int
        Integer holding the base defense value of Ozma.
    currentDefense : int
        Integer holding the current defense value of Ozma.
    level : int
        Integer denoting Ozma's numerical level
    currentPhase : int
        Integer representing Ozma's current phase in battle. (Default is 1, because once the game loop runs, Ozma switches state before state selection. Can only hold values: 1 or 0. )
    phase1AtkDict : dict
        Dictionary object holding the names and damage calculation data for Ozma's usable attacks in phase 1. (Default is None for safety, this is immediately overwritten on initialization.)
    phase2AtkDict : dict
        Dictionary object holding the names and damage calculation data for Ozma's usable attacks in phase 2. (Default is None for safety, this is immediately overwritten on initialization.)  
    baseDmgStatMatrix : list
        List object contianing the list matrix of integer values used for damage calculation, concerning attacks. (Default is None for safety, this is immediately overwritten on initialization.)
    baseElementalMatrix : list
        List object contianing the list matrix of float values used for damage calculation, concerning resistances. (Default is None for safety, this is immediately overwritten on initialization.)
    
    """
    def __init__(
        self,
        Name="",
        level=0,
        currentHP=0,
        maxHP=0,
        currentMP=0,
        maxMP=0,
        baseDmgStatMatrix=None,
        baseJob=None,
    ):
        self.Name = Name
        self.level = level
        self.currentHP = currentHP
        self.maxHP = maxHP
        self.currentMP = currentMP
        self.maxMP = maxMP
        self.type = "Player"
        # We can dynamically initialise these values by creating a mini inventory system later
        # For now, we'll use helper functions to pass values to these parameters
        self.baseDmgStatMatrix = (
            [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
            if baseDmgStatMatrix is None
            else baseDmgStatMatrix
        )
        self.baseJobStatMatrix = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
        self.DmgStatMatrix = [[]]
        self.baseElementalMatrix = [[1, 1, 1], [1, 1, 1], [1, 1, 1]]
        self.ElementalMatrix = [[]]
        self.baseJob = "Thief" if baseJob is None else baseJob
        self.statusList = []
        self.statusImmuneList = []
        # For testing purposes, I'll construct these manually using the baseJob parameter
        self.actionList = []
        # Used to denote which row the character is in
        self.rowState = 0
        self.rowDmgReductionModifier = 1
        self.specialActionList = None
        # First value is MP Cost, second value is innate multicast
        self.specialActionDict = {}
        # Represents the ff8 limit level, varies by each class; warrior/thief will go up fastest
        # Should be none unless a black mage is casting
        self.itemDict = {}
        self.inventory = {}

    def DefineCharName(self, nameString):
        self.Name = nameString

    def DefineCharLevel(self, levelValue):
        self.level = levelValue

    # Function used to pass character HP and MP values directly
    def DefineVitals(self, hp=None, mp=None):
        self.currentHP = self.maxHP = hp
        self.currentMP = self.maxHP = mp

    # Function to create a player character dmg matrix in real time
    def DefineCharDmgMatrix(self):
        for i in range(3):
            for j in range(3):
                print("Old stat:", self.DmgStatMatrix[i][j])
                # TODO:Print respective value to modify using a 2D array
                # TODO:Extend to catch EOF error using try catch
                statNameList = [
                    ["Strength", "Defense", "Evade"],
                    ["Magic", "Magic Defense", "Magic Evade"],
                    ["Attack Power", "Spirit", "Speed"],
                ]
                stat = int(
                    input(
                        "Please enter a stat value for stat: "
                        + str(statNameList[i][j])
                        + ": "
                    )
                )
                self.baseDmgStatMatrix[i][j] = stat

    # TODO: Amend this for elements in FF9/FF12
    # Function used to create an elemental resistance matrix for a player character
    def DefineCharElementMatrix(self):
        for i in range(3):
            for j in range(3):
                print("Old stat:", self.ElementalMatrix[i][j])
                # TODO:Print respective value to modify using a 2D array
                # TODO:Extend to catch EOF error using try catch
                statNameList = [
                    ["Fire", "Ice", "Thunder"],
                    ["Water", "Wind", "Earth"],
                    ["Holy", "Shadow", "Curative"],
                ]
                stat = int(
                    input(
                        "Please enter a stat value for stat: "
                        + str(statNameList[i][j])
                        + ": "
                    )
                )
                self.baseElementalMatrix[i][j] = stat
        return 0

    # Function to check if a particular status affliction is on a party member
    def CharStatusContains(self, status, statusList=None, isAll=False):
        if statusList != None:
            # If we have a list of multiple status' we'll check if any are in the list
            if isAll == False:
                return any(status in statusList for status in self.statusList)
            # Returns True if all status' in the list appear the characters statusList
            else:
                return statusList.issubset(self.statusList)
        # Otherwise, return if the single status is present in the list
        else:
            return status in self.statusList


    def GetLevelStatModifier(self):
        return (100 + self.level) / 175



    # Function used to make a character defend instead of act
    # TODO: Test that rowDmgReductionModifier works
    def CharShiftSelf(self):
        if self.rowState == 0:
            self.rowState = -self.rowState + 1
            self.rowDmgReductionModifier = 1.5
            print(self.Name, "has shifted to the rear line!")
        else:
            self.rowState = -self.rowState + 1
            self.rowDmgReductionModifier = 1
            print(self.Name, "has shifted to the front line!")

    def CharBasicAttack(self, targetToHit, forPrint=True):
        print(self.Name,"attacks",targetToHit.Name)
        finalDamage = basicAttack(self, targetToHit)
        ff9StatHandler.HPDamage(targetToHit, finalDamage,actionName="Attack")
        if forPrint:
            return finalDamage

    # Function used to allow item interaction
    # ItemData is tuple containing item name and item data
    # Item Data is list containing int for item power value and str for item type
    # TODO: Assert that when a mote is selected, the whole party is targeted
    def CharUseItem(self, target, itemData):
        itemName = itemData["name"]
        itemPower = int(itemData["power"])
        itemType = itemData["type"]

        if "healItem" == itemType:
            ff9StatHandler.HPDamage(target, itemPower, isHeal=True)
            if target is self:
                print(self.Name, "used", itemName, "to heal themselves!")
            else:
                print(self.Name, "used", itemName, "to heal", target.Name + "!")
        elif "healMPItem" == itemType:
            ff9StatHandler.MPDamage(target, itemPower, isCharging=True)
            if target is self:
                print(self.Name, "used", itemName, "to restore their Mana!")
            else:
                print(
                    self.Name, "used", itemName, "to restores", target.Name + "'s Mana!"
                )
        elif "reviveItem" == itemType:
            if "KO" in target.statusList:
                ff9StatusHandler.DebuffCleanse(target, debuffToCure="KO")
                ff9StatHandler.HPDamage(
                    target, (itemPower / 100 * target.maxHP), isHeal=True
                )
                print(self.Name, "used", itemName, "to revive", target.Name + "!")
            # Revive items instant kill undead ememies
            elif target.type == "Undead":
                target.currentHP = 0
                ff9StatusHandler.PlayerDeathblowCallCheck(target, True)
            else:
                print(itemName, "has no discernable effect!")

        self.itemDict[itemName]["quantity"] = str(
            int(self.itemDict[itemName]["quantity"]) - 1
        )
        if int(self.itemDict[itemName]["quantity"]) <= 0:
            # itemDict.pop(itemName)
            del self.itemDict[itemName]
