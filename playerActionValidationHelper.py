

#TODO: Extend function call to take previous string as input paramter to later print, (Optional) use config variable to disable print
def ConfirmSelection():
    """Function used to validate a previous player input.
        
    This is done by simply asking the user through print output to confirm that a previously inputted value is accurate.
    
    
    Parameters
    ----------
    None
        This function does not take in any arguments.

    Returns
    -------
    isValidSelection : bool
        Returns True on the user entering an affirmative input, otherwise returns false.
    """
    isValidSelection = False
    try:
        selConfirm= str(input("Confirm Selection?"))
        if selConfirm.lower() in ['yes','y','confirm']:
            isValidSelection = True
            return isValidSelection
        elif selConfirm.lower() in ['no','n','cancel','deny']:
            isValidSelection = False
            return isValidSelection
        else:
            print("Invalid input for confirmation")
            ConfirmSelection()
    except:
        print("Invalid value entry for confirmation")
        ConfirmSelection()

#TODO: (Low Priority) Make gameChars optional paramater for None but leave all function calls as normal
def TargetValidationHandler(gameChars):
    """Function used to determine and validate player target selection.
    
    This function will either output all possible to characters to target or ask the player choose which side of the field to target.
    The player will confirm that selection and the function will logically validate it before either returning the required value or asking the player to reselect their target.
    
    Parameters
    ----------
    gameChars : list
        The parameter for the list of objects representing the characters which are selectable in the game state.

    Returns
    -------
    object(RPGChar) or bool
        The return type is dependent on the value of gameChars. As long as gameChars is not none, it will return an object of type RPGChar to denote the character to target, otherwise, it'll return a bool denoting which side of the field to target.

    Notes
    -----
    If gameChars is passed as a 'None' value, the function will act differently, to determine which side of the field to target. 
    """
    isValidTarget = False

    while isValidTarget == False:
        try:
            #If selecting a single character to target
            if gameChars is not None:
                print("Chars to target:")
                for char in gameChars:
                    print(char.Name)
                targetChar = str(input("\n Who would you like to target?"))
                gameCharNames = [char.Name for char in gameChars]
                print("\n",gameCharNames,"\n")
                #TODO: Refactor to allow case-insensitivity 
                if str(targetChar) in gameCharNames:
                    confirmTarget = ConfirmSelection()
                    if confirmTarget == True:
                        for char in gameChars:
                            if targetChar == char.Name:
                                targetChar = char
                        isValidTarget = True
                    else:
                        TargetValidationHandler(gameChars)
                elif str(targetChar) not in gameCharNames:
                    print("That's not a valid target!")
                    print(targetChar,char.Name)
                    TargetValidationHandler(gameChars)
            #If selecting a party side to target
            else:
                targetParty = str(input("Are you targeting your allied party or the enemy party"))
                if targetParty.lower() in ['ally','allies', 'team','friendly','friends']:
                    confirmTarget = ConfirmSelection()
                    if confirmTarget == True:
                        return False
                    else:
                        print('Target party selection cancelled, retargeting...')
                        TargetValidationHandler(None)
                elif targetParty.lower() in ['enemy', 'enemies', 'foe', 'foes', 'non-allies', 'non-ally']:
                    confirmTarget = ConfirmSelection()
                    if confirmTarget == True:
                       return True
                    else:
                        print('Target party selection cancelled, retargeting...')
                        TargetValidationHandler(None)
        except Exception as e:
            print(e)
            print("Invalid Input for target!")
            TargetValidationHandler(gameChars)
    return targetChar
    
def ItemValidationHandler(char):
    """Function used to determine and validate item selection from player character's inventory.
    
    This function will allow the user to access their inventory to use an item.
    The player will confirm that selection and the function will logically validate it before either returning the dictionary containing the items data
    
    Parameters
    ----------
    char : object(RPGChar)
        The parameter is the character that is going to be accessing it's inventory.

    Returns
    -------
    dict
        The function returns a dictionairy containing the required item data of the chosen item.
    """
    print("Items Avaliable:")
    for item in char.itemDict:
        if int(char.itemDict.get(str(item),{}).get('quantity')) > 0:
            print(str(item),"Quantity:", char.itemDict.get(str(item),{}).get('quantity'));
    try:
        itemSelection = str(input("\n Please select an item:"))
        if char.itemDict.get(itemSelection) is None or int(char.itemDict.get(itemSelection,{}).get('quantity')) <= 0:
            print("This item is not in your inventory, please choose another item!")
            ItemValidationHandler(char)
        else:
            return char.itemDict.get(itemSelection)
    except:
        print("Invalid Item Selection, please make the selection again")
        ItemValidationHandler(char)


#TODO: Consider allowing confirmation for valid but not correct inputs for action category selection
#TODO: Condense Action and Special Action Validation Handler functions into one function via optional params
def ActionValidationHandler(actionList):
    """Function used to determine and validate action selection from player character's action list.
    
    This function will allow the user to select an action to use.
    The player will confirm that selection and the function will logically validate it before either returning the action to be used.
    
    Parameters
    ----------
    actionList : list
        The parameter is the list of values that denotes the actions avaliable to the character.

    Returns
    -------
    actionName : str
        Returns the name of the selected action.
    """
    isValidAction = False

    while isValidAction == False:
        try:
            actionName = str(input("Please select an action by inputting it's name, don't rush and stay focused.")).capitalize()
            #Safety measure, a player shouldn't pick an action not printed but to be safe
            actionAssertList = [action.lower() for action in actionList]
            if actionName.lower() in actionAssertList:
                isValidAction = True
            else:
                print("Invalid action selection!")
                ActionValidationHandler(actionList)
        except:
            print("Invalid input for action!")
            ActionValidationHandler(actionList)
    return actionName

#TODO: Refactor to use action validation handler on valid but non correct input by creating new action list with only MP Permittable actions
def SpecialActionValidationHandler(char):
    """Function used to determine and validate action selection from player character's specialActionList list.
    
    This will allow the user to select an action to use from the special actions list for a character.
    The player will confirm that selection and the function will logically validate it before either returning the action type to be used.
    
    Parameters
    ----------
    char : object(RPGChar)
        The parameter is the player char character to act so that it's object data can be accessed, including the action list.

    Returns
    -------
    actionName : str
        Returns the name of the selected action.
    """
    isValidAction = False
    actionList = char.specialActionList

    while isValidAction == False:
        try:
            for specialAction in char.specialActionList: 
                if char.specialActionDict[specialAction][0] < char.currentMP: 
                    print(specialAction+":",char.specialActionDict[specialAction][0])
            actionName = str(input("Please select an action by inputting it's name *AS IS*, don't rush and stay focused.")).title()
            #Safety measure, a player shouldn't pick an action not printed but to be safe
            if actionName in actionList and char.currentMP > char.specialActionDict[actionName][0]:
                confirmAction = ConfirmSelection()
                if confirmAction == True:
                    isValidAction = True 
                else:
                    SpecialActionValidationHandler(char)
            else:
                if actionName in actionList:
                    print(char.Name,"has not got enough MP to use this action!")
                    SpecialActionValidationHandler(char)
                else:
                    print("Invalid action selection!")
                    SpecialActionValidationHandler(char)
        except:
            print("Invalid input for action!")
            SpecialActionValidationHandler(char)
    return actionName