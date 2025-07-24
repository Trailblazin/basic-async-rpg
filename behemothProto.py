import random

BehemothIsDefeated = False

class Behemoth(char):
    def BehemothAutoInit(self):
        self.attackList = ["Strike", "Heave","Meteor"]
        self.baseDmgStatMatrix = self.DmgStatMatrix = [[25,10,7],[25,10,9],[55,45,44]]
        self.baseElementalMatrix = self.ElementalMatrix = [[1,1.5,1],[1,1,1],[1,1,-1]]
    #Probably not needed
    def BehemothTestInit(self):
        self.attackList = ["Strike", "Heave","Meteor"]
        self.DmgStatMatrix = self.baseDmgStatMatrix
        self.ElementalMatrix = self.baseElementalMatrix
    def ATB(self,partyList):
        attackChoice = random.choice(self.attackList)
        target = random.choice(partyList)
        if attackChoice == "Strike":
            strikeDmg = ff9DmgCalc.basicAttack(self,target,isEnemyActor=True) * 0.5
            ff9StatHandler.HPDamage(target,strikeDmg,actionName=attackChoice)
            self.lastAction = "Strike"
            self.meteorTick +=1
        elif attackChoice == "Heave":
                heaveDmg = ff9DmgCalc.basicAttack(self,target,isEnemyActor=True) * 0.65
                ff9StatHandler.HPDamage(target,heaveDmg,actionName=attackChoice)
                self.lastAction = "Heave"
                self.meteorTick +=1
        else:
            meteorData = {"type":"magical", "addType":"random", "power":"40"}
            if self.meteorTick >3 and self.currentMP > 40:
                if self.lastAction == "Strike":
                    meteorInt = random.randint(1,random.getrandbits(16))
                    if meteorInt % 7 == 0:
                        meteorDmg = ff9DmgCalc.specialAttackCalc(self,target,meteorData)
                        ff9StatHandler.HPDamage(target,meteorDmg,actionName="Meteor")
                elif self.lastAction == "Heave":
                    meteorInt = random.randint(1,random.getrandbits(16))
                    if meteorInt % 11 == 0:
                        meteorDmg = ff9DmgCalc.specialAttackCalc(self,target,meteorData)
                        ff9StatHandler.HPDamage(target,meteorDmg,actionName="Meteor")
                else:
                    ATB(self,partyList)