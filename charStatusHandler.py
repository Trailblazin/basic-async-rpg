import random

def AttackMissedCall(actor,attackName,targetChar):
    if attackName is None:
        print(str(actor),"attacked:",str(targetChar),"but missed!")
    else:
        print(str(actor),"used:",str(attackName),"on",str(targetChar),"but it missed!")

def DebuffApply(debuffList,targetChar):
    for debuff in debuffList:
        if "KO" in targetChar.statusList:
            print(targetChar.Name,"cannot be debuffed whilst KO'ed!")
        if debuff not in targetChar.statusList:
            if debuff not in targetChar.statusImmuneList:
                targetChar.statusList.append(debuff)
            else:
                print(str(targetChar.Name), "is Immune to:",str(debuff)+"!")
        else:
            print(str(targetChar.Name), "is already afflicted with the debuff:",str(debuff)+"!")

#isDebuffPurge will be used for effects replicating esuna
def DebuffCleanse(cureTarget,debuffToCure=None, isDebuffPurge = False):
    if isDebuffPurge:
        #Used in FF12 format for later implementations of spells and conditionals
        esunaPurgeList = ["Petrify","Confuse","Sleep","Reverse","Disable","Immobilize","Silence","Blind","Poison","Sap"]
        for status in esunaPurgeList:
            if status in cureTarget.statusList:
                cureTarget.statusList.remove(status)
    else:
        if debuffToCure is not None:
            try:
                cureTarget.statusList.remove(debuffToCure)
            except ValueError:
                print("No debuff present on target!")

def PlayerOverhealCheck(targetChar):
    if targetChar.currentHP > targetChar.maxHP:
        targetChar.currentHP = targetChar.maxHP
def PlayerOverchargeCheck(targetChar):
        if targetChar.currentMP > targetChar.maxMP:
            targetChar.currentMP = targetChar.maxMP

#Used as call check to see if a player reaches <=0 HP
#Any attack that inflicts a deathblow should call this function after setting HP to 0
#Will be called by stat handler functions
def PlayerDeathblowCallCheck(targetChar, instant = False):
    #Should only do anything if HP <= 0
    if targetChar.currentHP <= 0:
        targetChar.currentHP = 0
        targetChar.statusList = []
        targetChar.statusList.append("KO")
        #Could add to local class function for player Char
        targetChar.DmgStatMatrix = targetChar.baseDmgStatMatrix
        if instant:
            print(targetChar.Name, "was killed, instantly!")
        else:
            print(targetChar.Name, "has been knocked out")
#All player chars will share this function usage
def PlayerManaOutageCheck(targetChar):
    if targetChar.currentMP <= 0:
        targetChar.currentMP = 0