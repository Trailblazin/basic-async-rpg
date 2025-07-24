from playerActionValidationHelper import *

def AttackActionHelper(actor,actorParty,enemyParty):
    """Procedure used to handle the functionality for the character-universal 'Attack' action.
    
    This allows the user to select a valid target to attack and then use the basic attack damage calculaton to inflict damage on their desired target.
    The player will validate their target selection before damage calculation occurs.
    
    Parameters
    ----------
    actor : object(RPGChar)
        The parameter is the player char character to act so that it's object data can be accessed, including the action list.
    actorParty : list
        The collection of characters what are allied with the current actor in the game state.
    enemyParty : list
        The collection of characters what are opposed to the current actor in the game state.

    Returns
    -------
    None
        As a procedure modifying object data, it does not return any values.
    """
    targetChar = TargetValidationHandler(actorParty + enemyParty)
    actor.CharBasicAttack(targetChar)

def SpecialAttackActionHelper(actor,actorParty,enemyParty):
    """Procedure used to handle the functionality for the character specific sub-actions.
    
    This procedure allows for player target validation and selection of their desired special action.
    Once the desired action is found, the characters special action category is used to dynamically access the required module for special action data.
    The player will validate their target selection before passing the target char to the external module procedure.
    Furthermore, the procedure also manages the logic required to emulate multi-casting, both for innately multicasted and optionally multicasted actions.
    
    Parameters
    ----------
    actor : object(RPGChar)
        The parameter is the player char character to act so that it's object data can be accessed, including the action list.
    actorParty : list
        The collection of characters what are allied with the current actor in the game state.
    enemyParty : list
        The collection of characters what are opposed to the current actor in the game state.
    Returns
    -------
    None
        As a procedure modifying object data, it does not return any values.

    Notes
    -----
    specialActionModule dynamically imports the module by name, specialActionProcedure gets the procedure as an attribute from the module object by name.
    """
    playerSpecialAction = SpecialActionValidationHandler(actor)
    #String formating 
    specialActionToHandle = string.capwords(playerSpecialAction).replace(" ","")
    if specialActionToHandle == "SwordMagic": 
    #Dynamically typed variable, can either hold None or Str
        spellAvaliableForSwordMagic = battleConfig.storedSpell
        #Conditional to check that use of SwordMagic is valid 
        if spellAvaliableForSwordMagic is not None:
            targetChar = TargetValidationHandler(actorParty + enemyParty)
            specialActionProcedure(actor,targetChar,spellAvaliableForSwordMagic)
        else:
            #TODO: Add optional param for no stored spell available, unique print statement before target selection.
            print("Sword Magic unavaliable - using basic attack!")
            AttackActionHelper(actor,actorParty,enemyParty)
        
    specialActionCategory = actor.actionList[1].lower().replace(" ","")
    specialActionModule = __import__(specialActionCategory + 'handler')
    specialActionProcedure = getattr(specialActionModule,specialActionToHandle)

    #For all other special actions:
    #Iterative sequence for Innate Multi-Cast actions!
    if specialActionToHandle in specialActionModule.GetMultiCastActions(True):
        isEnemyMultiCast = TargetValidationHandler(None)
        if isEnemyMultiCast:
            for char in enemyParty:
                #TODO: Verify that char special actions call HP Damage, HP Damage should not be called directly
                specialActionProcedure(actor,char)
        else:
            for char in actorParty:
                specialActionProcedure(actor,char)
    #If action is not innate multi-cast but is multi-castable.
    elif specialActionToHandle in specialActionModule.GetMultiCastActions(False):
        try:
            multiCastConfirm = str(input("Would you like to group-cast this skill?"))
            if multiCastConfirm.lower() in ['y','yes','true','confirm']:
                #If EnemyMultiCast, player selects party not character to target
                isEnemyMultiCast = TargetValidationHandler(None)
                if isEnemyMultiCast:
                    for char in enemyParty:
                        specialActionProcedure(actor,char,True)
                else:
                    for char in actorParty:
                        specialActionProcedure(actor,char,True)
            elif multiCastConfirm.lower() in ['no','y','cancel','deny']:
                #If not multi-casting allow target selection to entire field
                targetChar = TargetValidationHandler(actorParty + enemyParty)
                specialActionProcedure(actor,targetChar)
            else:
                print("Invalid selection made, force-casting on single target...")
                targetChar = TargetValidationHandler(actorParty + enemyParty)
                specialActionProcedure(actor,targetChar)
        except:
            print("Invalid input made, force-casting on single target...")
            targetChar = TargetValidationHandler(actorParty + enemyParty)
            specialActionProcedure(actor,targetChar)
    #If action is not multi-castable
    else:
            targetChar = TargetValidationHandler(actorParty + enemyParty)
            specialActionProcedure(actor,targetChar)

def ItemActionHelper(actor,actorParty,enemyParty):
    """Procedure used to handle the functionality for the character-universal 'Item' action.
    
    This allows the user to selection an item in the actor's inventory before asserting and validate a target selection based on the item type.
    
    Parameters
    ----------
    actor : object(RPGChar)
        The parameter is the player char character to act so that it's object data can be accessed, including the action list.
    actorParty : list
        The collection of characters what are allied with the current actor in the game state.
    enemyParty : list
        The collection of characters what are opposed to the current actor in the game state.

    Returns
    -------
    None
        As a procedure calling object functions, it does not return any values.
    """
    itemChoice = ItemValidationHandler(actor)
    itemTarget = TargetValidationHandler(actorParty+enemyParty)
    actor.CharUseItem(itemTarget,itemChoice)