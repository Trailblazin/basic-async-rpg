from itertools import cycle
import battleHelper
import battleInit

def battleSetup():
    playerParty = battleInit.constructParty()
    enemyParty = battleInit.constructEncounterParty(True)
    return playerParty,enemyParty
   
#For generic enemies, not Ozma...
def battle(playerParty,encounterParty):
    print("TEST BATTLE BEGINS!!!\n\n\n")
    ozmaPresent = False
    ozmaChar = None
    for char in encounterParty:
        if char.type == "Eidolon":
            ozmaPresent = True
            ozmaChar = char
            ozmaChar.OzmaInit(playerParty)
    nTurns = 0
    gameInitiative = encounterParty + playerParty
    gameInitiative.sort(key = lambda x: x.DmgStatMatrix[2][2],reverse=True)

    while True:
        nTurns +=1
        print("TURN:",nTurns+"\n")
        print("Player Party Info:")
        
        for char in playerParty:
            print(char.Name,char.currentHP)
        print("Enemy Party Info:")
        for char in encounterParty:
            print(char.Name)

        #TODO: Extend this for use with AI Functionality
        for char in gameInitiative:
            if char.type == "Player":
                battleHelper.BattleTurnHandler(char,playerParty,encounterParty)
            if ozmaPresent and char is not ozmaChar:
                ozmaChar.OzmaATB_Bypass(playerParty)
            elif char.type == "Eidolon":
                char.OzmaPhasePrep(playerParty)
            else:
                char.ATB(playerParty)
            '''
            WIN STATE CHECKS
            '''
            if all(char.currentHP <= 0 for char in playerParty):
                isWin = False
                BattleEnd(isWin,nTurns)
            elif all(char.currentHP <= 0 for char in encounterParty): 
                isWin = True
                BattleEnd(isWin,nTurns)
            else:
                pass


def BattleEnd(winState,nTurns):
    if winState == False:
        print("\nYou lost! Better luck next time!")
    else:
        print("\nYou won in", nTurns,"turns!")
        print("Play: Final Fantasy Win Jingle!!! \n You did good XD!")


def Main():
    setupParties = battleSetup()
    battle(setupParties[0],setupParties[1])

if __name__ == "__main__":
    Main()