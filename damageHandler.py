
# Function used to determine if a basic attack is a critical hit
def ReturnCriticalModifier(spiritStat, randomizer = None, isCrit = False):
    if randomizer is None:
        randomizer = random.Random()
    critHighBar = randomizer.getrandbits(32)
    critModifier = randomizer.randrange(0, critHighBar) % (spiritStat/4)
    critCheck = randomizer.randrange(0, 99)
    if isCrit:
        print('CRITICAL HIT!!!')
        return 2
    if critModifier > critCheck:
        print('CRITICAL HIT!!!')
        return 2
    else:
        return 1


'''
#TODO:Extend script to call module to generate dictionary of spells from csv/JSON
#Should hold a key denoting the spell and the list of values denoting the Magic Power and MP Cost
#Should also hold value for white and black magic
#Dict key = Spell Name
#Dict value = spell power, spell cost, isWhiteMagic, isInnateMultiTarget
'''

'''
#Remember each reflect is a new spell attack calculation.
#Function calculated magic damage for a single magic user, does not handle multi casting nor reflecting; just the required damage calculations
#When creating Magic Selection Pass the magic as a string to this function
'''


def specialAttackCalc(actor,target,spellData):
    r = random.Random()
    actorLevel = actor.level

    specialAttackType = spellData["type"]
    specialAttackPower = int(spellData["power"]) if specialAttackType.lower() != "physical" else 0
    specialAttackModifier = 1 if spellData.get("modifier") is None else float(spellData["modifier"])
    specialAttackFinalModifier = 1 if spellData.get("finalDmgMod") is None else spellData["finalDmgMod"]
    
    if specialAttackType.lower() == "hpclamp":
        finalAtkDmg = actor.maxHP - actor.currentHP
        return finalAtkDmg

    if specialAttackType.lower() == "valueClamp":
        finalAtkDmg = specialAttackPower
        return finalAtkDmg

    if specialAttackType == "physical":
        actorStrength = GetDmgStatByName("Strength",actor)
        actorAttackPower = GetDmgStatByName("Attack Power",actor)
        if spellData.get("targetMagicDef") is not True:
            targetDef = GetDmgStatByName("Defense",target)
        else:
            targetDef = GetDmgStatByName("Magic Defense",target)

        attackBonusModifier = (((actorLevel + actorStrength) / 8) + 1)

        actionBasal = actorAttackPower * specialAttackModifier - targetDef
        if "Mini" not in actor.statusList:
            actionBonus = actorStrength + (r.randrange(0, r.getrandbits(32)) % attackBonusModifier) if "Mini" not in actor.statusList else 1
        else:
            actionBonus = 1
        finalAtkDmg = actionBasal * actionBonus * specialAttackFinalModifier

    elif specialAttackType == "magical":
        actorMagic = GetDmgStatByName("Magic",actor)
        magicBonusModifier = (((actorLevel + actorMagic) / 8) + 1)
        if spellData.get("addType").lower() == "random":
            actionBasal = specialAttackPower
            actionBonus = r.randint(1,(actor.level+actorMagic))
            finalAtkDmg = actionBasal * actionBonus
 
        actionBonus = actorMagic + (r.randrange(0, r.getrandbits(32)) % magicBonusModifier)
        
        specialAttackElement = spellData["element"]

        if specialAttackElement.lower() == "curative":
            actionBasal = specialAttackPower * specialAttackModifier
            finalAtkDmg = actionBasal * actionBonus * specialAttackFinalModifier * GetElementByName(specialAttackElement.capitalize(),target)

        else: 
            targetDef = GetDmgStatByName("Magic Defense", target)
            actionBasal = specialAttackPower * specialAttackModifier - targetDef
            
            finalAtkDmg = actionBasal * actionBonus * specialAttackFinalModifier * GetElementByName(specialAttackElement.capitalize(),target) 
            if spellData.get("addType").lower() == "osmose":
                finalAtkDmg /= 4

    elif specialAttackType.lower() == "swordmagic":
        specialAttackElement = spellData["element"]
        actorStrength = GetDmgStatByName("Strength",actor)
        actorAttackPower = GetDmgStatByName("Attack Power",actor)
        targetDef = GetDmgStatByName("Defense",target)


        actionBasal = actorAttackPower + specialAttackPower * specialAttackModifier - targetDef
        actionBonus = actorStrength + (r.randrange(0, r.getrandbits(32)) % attackBonusModifier)
        finalAtkDmg = actionBasal * actionBonus * GetElementByName(specialAttackElement.capitalize(),target)

    return int(finalAtkDmg)