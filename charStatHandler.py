from charStatusHandler import PlayerDeathblowCallCheck, PlayerOverhealCheck, PlayerOverchargeCheck,PlayerManaOutageCheck


def HPDamage(target, value, isHarm=True, isHeal=False, actionName = None):
    #Boolean check to make sure that an action can only harm or heal
    isHarm  = not(isHeal)
    if isHarm:
        if value > 0:
            target.currentHP -= value * target.rowDmgReductionModifier
            if actionName is not None:
                print(target.Name,"takes", value * target.rowDmgReductionModifier,"damage from",actionName+"!")
            PlayerDeathblowCallCheck(target)
        else:
            print(target.Name, "is absorbing", actionName+"!")
            HPDamage(target,-value,actionName,isHeal = True,)
    elif isHeal:
        target.currentHP += value
        if actionName is not None:
            print(target.Name,"regains", value ,"HP from",actionName+"!")
        PlayerOverhealCheck(target)


# Is charging will be used for MP healing and elixer items
def MPDamage(target, value, isCasting=True, isCharging=False, actionName = None):
    if type(value) is list:
        value = value[0]
    if isCasting:
        if value > 0:
            target.currentMP -= value
            if actionName is not None:
                print(target.Name, "has had their MP absorbed via",actionName+"!")
            PlayerManaOutageCheck(target)
    elif isCharging:
        target.currentMP += value
        if actionName is not None:
            print(target.Name,"regains", value, "MP!")
        PlayerOverchargeCheck(target)


# Will reset a given stat to it's base stat
def ResetToBaseStat(statName, target):
    if statName == "Strength":
        target.DmgStatMatrix[0][0] = target.baseDmgStatMatrix[0][0]
    if statName == "Defense":
        target.DmgStatMatrix[0][1] = target.baseDmgStatMatrix[0][1]
    if statName == "Evade":
        target.DmgStatMatrix[0][2] = target.baseDmgStatMatrix[0][2]
    if statName == "Magic":
        target.DmgStatMatrix[1][0] = target.baseDmgStatMatrix[1][0]
    if statName == "Magic Defense":
        target.DmgStatMatrix[1][1] = target.baseDmgStatMatrix[1][1]
    if statName == "Magic Evade":
        target.DmgStatMatrix[1][2] = target.baseDmgStatMatrix[1][2]
    if statName == "Attack Power":
        target.DmgStatMatrix[2][0] = target.baseDmgStatMatrix[2][0]
    if statName == "Spirit":
        target.DmgStatMatrix[2][1] = target.baseDmgStatMatrix[2][1]
    if statName == "Speed":
        target.DmgStatMatrix[2][2] = target.baseDmgStatMatrix[2][2]


def AlterStat(statName, target, modifier):
    if statName == "Strength":
        target.DmgStatMatrix[0][0] = target.baseDmgStatMatrix[0][0] * modifier
    if statName == "Defense":
        target.DmgStatMatrix[0][1] = target.baseDmgStatMatrix[0][1] * modifier
    if statName == "Evade":
        target.DmgStatMatrix[0][2] = target.baseDmgStatMatrix[0][2] * modifier
    if statName == "Magic":
        target.DmgStatMatrix[1][0] = target.baseDmgStatMatrix[1][0] * modifier
    if statName == "Magic Defense":
        target.DmgStatMatrix[1][1] = target.baseDmgStatMatrix[1][1] * modifier
    if statName == "Magic Evade":
        target.DmgStatMatrix[1][2] = target.baseDmgStatMatrix[1][2] * modifier
    if statName == "Attack Power":
        target.DmgStatMatrix[2][0] = target.baseDmgStatMatrix[2][0] * modifier
    if statName == "Spirit":
        target.DmgStatMatrix[2][1] = target.baseDmgStatMatrix[2][1] * modifier
    if statName == "Speed":
        target.DmgStatMatrix[2][2] = target.baseDmgStatMatrix[2][2] * modifier

def GetDmgStatByName(statName,target):
    if statName == "Strength":
        return target.DmgStatMatrix[0][0] 
    if statName == "Defense":
        return target.DmgStatMatrix[0][1] 
    if statName == "Evade":
        return target.DmgStatMatrix[0][2] 
    if statName == "Magic":
        return target.DmgStatMatrix[1][0]
    if statName == "Magic Defense":
        return target.DmgStatMatrix[1][1]
    if statName == "Magic Evade":
        return target.DmgStatMatrix[1][2]
    if statName == "Attack Power":
        return target.DmgStatMatrix[2][0] 
    if statName == "Spirit":
        return target.DmgStatMatrix[2][1] 
    if statName == "Speed":
        return target.DmgStatMatrix[2][2]

def ResetToBaseElement(statName, target):
    if statName == "Strength":
        target.ElementalMatrix[0][0] = target.baseElementalMatrix[0][0]
    if statName == "Defense":
        target.ElementalMatrix[0][1] = target.baseElementalMatrix[0][1]
    if statName == "Evade":
        target.ElementalMatrix[0][2] = target.baseElementalMatrix[0][2]
    if statName == "Magic":
        target.ElementalMatrix[1][0] = target.baseElementalMatrix[1][0]
    if statName == "Magic Defense":
        target.ElementalMatrix[1][1] = target.baseElementalMatrix[1][1]
    if statName == "Magic Evade":
        target.ElementalMatrix[1][2] = target.baseElementalMatrix[1][2]
    if statName == "Attack Power":
        target.ElementalMatrix[2][0] = target.baseElementalMatrix[2][0]
    if statName == "Spirit":
        target.ElementalMatrix[2][1] = target.baseElementalMatrix[2][1]
    if statName == "Speed":
        target.ElementalMatrix[2][2] = target.baseElementalMatrix[2][2]

def AlterElement(statName, target, modifier):
    if statName == "Fire":
        target.ElementalMatrix[0][0] = target.baseElementalMatrix[0][0] * modifier
    if statName == "Ice":
        target.ElementalMatrix[0][1] = target.baseElementalMatrix[0][1] * modifier
    if statName == "Thunder":
        target.ElementalMatrix[0][2] = target.baseElementalMatrix[0][2] * modifier
    if statName == "Water":
        target.ElementalMatrix[1][0] = target.baseElementalMatrix[1][0] * modifier
    if statName == "Wind":
        target.ElementalMatrix[1][1] = target.baseElementalMatrix[1][1] * modifier
    if statName == "Earth":
        target.ElementalMatrix[1][2] = target.baseElementalMatrix[1][2] * modifier
    if statName == "Holy":
        target.ElementalMatrix[2][0] = target.baseElementalMatrix[2][0] * modifier
    if statName == "Shadow":
        target.ElementalMatrix[2][1] = target.baseElementalMatrix[2][1] * modifier
    if statName == "Curative":
        target.ElementalMatrix[2][2] = target.baseElementalMatrix[2][2] * modifier

def GetElementByName(statName,target):
    if statName == "Fire":
        target.ElementalMatrix[0][0] 
    if statName == "Ice":
        target.ElementalMatrix[0][1] 
    if statName == "Thunder":
        target.ElementalMatrix[0][2] 
    if statName == "Water":
        target.ElementalMatrix[1][0]
    if statName == "Wind":
        target.ElementalMatrix[1][1]
    if statName == "Earth":
        target.ElementalMatrix[1][2]
    if statName == "Holy":
        target.ElementalMatrix[2][0] 
    if statName == "Shadow":
        target.ElementalMatrix[2][1] 
    if statName == "Curative":
        target.ElementalMatrix[2][2] 



def BuffDebuff_StatHander(target):
    if "Haste" in target.statusList:
        print(str(target.Name), "has been hasted!")
        AlterStat("Speed", target, 2.0)
    if "Mini" in target.statusList:
        print(str(target.Name), "has been minimized")
    if "Slow" in target.statusList:
        print(str(target.Name), "has been slowed")
        AlterStat("Speed", target, 0.5)