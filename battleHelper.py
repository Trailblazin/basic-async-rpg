"""Module use to handle main combat functionality.

This module contains all of the helper functions used to emulate the turn-based combat mechanics for players.
near identical to the FF9 game. Aside from sequential turn-based battle instead of time-based ATB, this is a near perfect representation for CLI.
This module allows the player to select the globally avaliable player actions: Attack, Item, Shift and Flee as well as their class specific actions.
Through this module, all game logic is managed to prevent invalid action selections, erroneous skill and item functionality for multiple targets and more.
"""
import random
import OzmaProto
import rpgChar
import string
import battleConfig
from itertools import cycle, islice
from playerActionHelper import *

def BattleTurnHandler(actor,actorParty,enemyParty):
    """Procedure used to handle the functionality for the main Turn Based combat loop.
    
    This allows the player to select the actions to take on a particular turn in the game state and controls the Limit Break logic.
    By utilising the various Helper functions, this emulates the ATB system in a sequential time-series, allowing for control for each character in the player party.
    Non-Player/Enemy characters use a more simplified version of this function due to the lack of conditional requirements.

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
    if "KO" not in actor.statusList:
        print(actor.Name, "it's your turn! \n What will you choose to do?")
        #Selection for a turn without limit breaks
        print("Avaliable actions for", actor.Name,"are as follows:\n\n"+str(actor.actionList[0]).capitalize()+"\n"+str(actor.actionList[1]).title()+"\n"+str(actor.actionList[2]).capitalize()+"\n"+str(actor.actionList[3]).capitalize()+"\n"+str(actor.actionList[4]).capitalize()+"\n")
        playerAction = ActionValidationHandler(actor.actionList)
        if playerAction.capitalize() == "Attack":
            AttackActionHelper(actor,actorParty,enemyParty)
        #If player's chosen action is their class-specific action name
        elif playerAction.title() == actor.actionList[1].title():
            SpecialAttackActionHelper(actor,actorParty,enemyParty)

        elif playerAction.capitalize() == "Item":
            ItemActionHelper(actor,actorParty,enemyParty)
            
        elif playerAction.capitalize() == "Shift":
            actor.CharShiftSelf()
        elif playerAction.capitalize() == "Flee":
            print("Unable to flee!")
    else:
        print("\n",actor.Name, "is knocked out and cannot act!","\n")
