import rpgChar
import OzmaProto
import behemothProto
#Function used to build playerParty
def constructParty(testParty= True):
    """Function used to build encounter party.
    
    This handles the creation of the player party by using the RPGChar class functions to initialise the party character data.
    Optional parameter allows for manual override of all data values but not Inventory values.
    

    Parameters
    ----------
    testParty : bool, optional
        This parmater controls the conditional data override for party character values.

    Returns
    -------
    partyList : list of object(RPGChar)  
    """    
    TestChar = rpgChar.RPGChar()
    TestChar2 =  rpgChar.RPGChar()
    #TestChar3 =  rpgChar.RPGChar()
    #TestChar4 =  rpgChar.RPGChar()
    partyList = [TestChar]#,TestChar2]#,TestChar3,TestChar4]
    #Iterates through party list
    for char in partyList:
        char.PlayerCharInit()
        char.CharInventoryHandler()
        print("Name:",char.Name)
        print("HP:"+str(char.currentHP),"MP:"+str(char.currentMP))
        #Please find order for stats in readME
        print("DMG STAT TABLE:",char.baseDmgStatMatrix)
        print("RES STAT TABLE:",char.baseElementalMatrix)
        print("\n\n")
    if testParty:
        #TODO: Modify for try and except
        customPartyStatMatrices  = input(str("Do you need to manually alter the party damage stats? \n Please enter Yes or No:\n "))
        if customPartyStatMatrices .lower() in ["y", "yes"]:
            for char in partyList:
                char.DefineCharDmgMatrix()
        customPartyElemStatMatrices  = input(str("Do you need to manually alter the party elemental stats?\n Please enter Yes or No:\n"))
        if customPartyElemStatMatrices .lower() in ["y", "yes"]:
            for char in partyList:
                char.DefineCharElementMatrix()
        customPartyVitals = input(str("Do you need to manually alter the char' vital stats?\n Please enter Yes or No:\n"))
        if customPartyVitals.lower() in ["y", "yes"]:
            for char in partyList:
                    char.DefineVitals()
    return partyList

def constructEncounterParty( autoSelect = False):
    """Function used to build encounter party.
    
    This handles the creation of the player party by using the RPGChar class functions to initialise the party character data.
    Optional parameter allows for manual override of all data values but not Inventory values.
    
    Parameters
    ----------
    autoSelect : bool, optional
        This procedure only needs access to data within the class instance.

    Returns
    -------
    partyList : list of object(RPGChar)  
    """    
    if autoSelect:
        bossChar = behemothProto.ProtoBehemoth("Behemoth",32000,32000,1000,1000)
        bossChar.BehemothAutoInit()
    else:
        bossChoice = input(str("Which enemy do you want to test? \n Choose between Ozma or Behemoth:"))
        if bossChoice.lower() is 'ozma':
            bossChar = OzmaProto.Ozma("Ozma", 55535, 55535, 9999, 9999, 0, 0, 0, 0)
            friendlyChoice = input(str("Is friendly monsters active? \n Please enter Yes or No:\n"))
            if friendlyChoice.lower() in ["y", "yes"]:
                OzmaProto.IsFriendlyMonsterModActive = True
            else:
                OzmaProto.IsFriendlyMonsterModActive = False
            bossChar.OzmaInit()
            customBossVitals = input(str("Do you need to manually alter the boss' vital stats?\n Please enter Yes or No:\n"))
            if customBossVitals.lower() in ["y", "yes"]:
                bossChar.DefineVitals()

        elif bossChoice.lower() is 'behemoth':
            bossChar = behemothProto.ProtoBehemoth("Behemoth",32000,32000,1000,1000)
            bossChar.BehemothAutoInit()
            customBossVitals = input(str("Do you need to manually alter the boss' vital stats?\n Please enter Yes or No:\n"))
            if customBossVitals.lower() in ["y", "yes"]:
                bossChar.DefineVitals()
        else:
            print("Invalid choice, auto selecting boss \n")
            constructEncounterParty(autoSelect=True)
    enemyList = [bossChar]
    return enemyList 