'''
Created on Jan 21, 2014

@author: presto
'''

import random
import re
from PIL import Image
from math import floor, ceil, sqrt, sin, cos, fabs
import string
import ImageFont, ImageDraw

from General import WGMap


class MULEWGMap(WGMap):
  def doSetup(self):
    print "setting plot types"
    self.initPlotTypes()
    print "getting territory IDs"
    self.getTerritoryIDs()    
    #print "adding Mule Box territories"
    #self.addMuleBoxTerritories()
    
    print "adding mule territories"
    self.addMuleTerritories()
    
    #self.addMuleAttacksWithinPlots()
    print "adding mule attacks"
    self.addMuleAttacksBetweenPlots()
    print "adding mercenary fortifies"
    self.addFortifiesForMercenaries()
    print "adding mule factories"
    self.addMuleFactories()
    
  def initPlotTypes(self):
    self.plotType = [["p","p","p","p","m","r","m","p","p","p","p"],
                     ["p","M","p","p","p","r","p","M","p","p","p"],
                     ["m","p","p","M","p","r","p","m","p","m","p"],
                     ["p","p","p","p","m","r","p","p","m","m","p"],
                     ["p","M","m","p","p","r","p","M","p","p","p"]]

    self.plotType = [["p","p","p","p","m","r","m","p","x","p","p"],
                     ["x","M","x","x","p","r","x","M","p","p","p"],
                     ["m","p","x","M","x","r","p","x","x","m","x"],
                     ["p","x","p","p","m","r","x","p","m","m","p"],
                     ["p","M","m","x","p","r","p","M","p","x","p"]]
    
    #return e,f,s
  def getBonusesFromRC(self,row,col):
    pt = self.plotType[row][col]
    if pt == "p":
      return (4,2,1)
    if pt == "r":
      return (2,4,0)
    if pt == 'm':
      return (2,1,2)
    if pt == 'M':
      return (1,0,3)
    
    return None;
      
  
  def getTerritoryIDs(self):
    self.tidMercenary = dict()
    self.tidMule1 = dict()
    self.tidMule2 = dict()
    self.tidMule3 = dict()
    self.tidReady1 = dict()
    self.tidReady2 = dict()
    self.tidReady3 = dict()
    self.tidBuild1 = dict()
    self.tidBuild2 = dict()
    self.tidBuild3 = dict()
    self.tidIng1 = dict()
    self.tidIng2 = dict()
    self.tidIng3 = dict()
    self.tidSmithore = dict()
    self.tidBattery = dict()
    self.tidPID = dict()
    #self.tidBoxes = AutoVivification() #[["" for i in range(6)] for j in range(8)]
    
    for playerID in ["P1","P2","P3","P4","P5","P6"]:
      self.tidPID[playerID] = self.getTerritoryIDFromName(playerID)
      self.tidMercenary[playerID] = self.getTerritoryIDFromName(playerID+"-Mercenary")
      self.tidMule1[playerID] = self.getTerritoryIDFromName(playerID+"-Mule1")
      self.tidMule2[playerID] = self.getTerritoryIDFromName(playerID+"-Mule2")
      self.tidMule3[playerID] = self.getTerritoryIDFromName(playerID+"-Mule3")
      self.tidReady1[playerID] = self.getTerritoryIDFromName(playerID+"-Ready1")
      self.tidReady2[playerID] = self.getTerritoryIDFromName(playerID+"-Ready2")
      self.tidReady3[playerID] = self.getTerritoryIDFromName(playerID+"-Ready3")
      self.tidBuild1[playerID] = self.getTerritoryIDFromName(playerID+"-Build1")
      self.tidBuild2[playerID] = self.getTerritoryIDFromName(playerID+"-Build2")
      self.tidBuild3[playerID] = self.getTerritoryIDFromName(playerID+"-Build3")
      self.tidIng1[playerID] = self.getTerritoryIDFromName(playerID+"-Ing1")
      self.tidIng2[playerID] = self.getTerritoryIDFromName(playerID+"-Ing2")
      self.tidIng3[playerID] = self.getTerritoryIDFromName(playerID+"-Ing3")
      self.tidSmithore[playerID] = self.getTerritoryIDFromName(playerID+"-Smithore")
      self.tidBattery[playerID] = self.getTerritoryIDFromName(playerID+"-Battery")
      
      
      
    
  def addMuleAttacksWithinPlots(self):
    
    for row in range(5):
      for col in range(11):
        if self.plotType[row][col] != 'x':
          eMule = self.getTerritoryIDFromName(str(row)+","+str(col)+"-Energy");
          fMule = self.getTerritoryIDFromName(str(row)+","+str(col)+"-Food");
          sMule = self.getTerritoryIDFromName(str(row)+","+str(col)+"-Smithore");
          
          self.addBorder(eMule,fMule)
          self.addBorder(sMule,fMule)
          self.addBorder(eMule,sMule)
    
  
  def addMuleAttacksBetweenPlots(self):

    # also mule neighbor bonuses

    for row in range(5):
      for col in range(10):
        # territory to the right
        c1 = col+1
        if self.plotType[row][col] == 'x':
          continue
        if self.plotType[row][c1] == 'x':
          continue

        eMule1 = self.getTerritoryIDFromName(str(row)+","+str(col)+"-Energy");
        fMule1 = self.getTerritoryIDFromName(str(row)+","+str(col)+"-Food");
        sMule1 = self.getTerritoryIDFromName(str(row)+","+str(col)+"-Smithore");

        eMule2 = self.getTerritoryIDFromName(str(row)+","+str(c1)+"-Energy");
        fMule2 = self.getTerritoryIDFromName(str(row)+","+str(c1)+"-Food");
        sMule2 = self.getTerritoryIDFromName(str(row)+","+str(c1)+"-Smithore");
        
        self.addBorder(eMule1,eMule2,borderType="Artillery")
        self.addBorder(eMule1,fMule2,borderType="Artillery")
        self.addBorder(eMule1,sMule2,borderType="Artillery")

        self.addBorder(fMule1,eMule2,borderType="Artillery")
        self.addBorder(fMule1,fMule2,borderType="Artillery")
        self.addBorder(fMule1,sMule2,borderType="Artillery")

        self.addBorder(sMule1,eMule2,borderType="Artillery")
        self.addBorder(sMule1,fMule2,borderType="Artillery")
        self.addBorder(sMule1,sMule2,borderType="Artillery")
        
        for playerID in ["P1","P2","P3","P4","P5","P6"]: 
          factoryID = self.tidBattery[playerID]
          tName = playerID + "-" + str(row) + "," + str(col) + "+"+str(row) + "," + str(c1) +"-EnergyNieghborsBonus"
          members = set([eMule1, eMule2, self.tidPID[playerID]])
          self.addContinent(tName,members,bonus="1",factory=factoryID,factoryType="AutoCapture")

          factoryID = self.tidSmithore[playerID]
          tName = playerID + "-" + str(row) + "," + str(col) + "+"+str(row) + "," + str(c1) +"-SmithoreNieghborsBonus"
          members = set([sMule1, sMule2, self.tidPID[playerID]])
          self.addContinent(tName,members,bonus="1",factory=factoryID,factoryType="AutoCapture")

          factoryID = self.tidMercenary[playerID]
          tName = playerID + "-" + str(row) + "," + str(col) + "+"+str(row) + "," + str(c1) +"-FoodNieghborsBonus"
          members = set([fMule1, fMule2, self.tidPID[playerID]])
          self.addContinent(tName,members,bonus="1",factory=factoryID,factoryType="AutoCapture")


    for row in range(4):
      for col in range(11):
        # territory below
        r1 = row+1
        
        if self.plotType[row][col] == 'x':
          continue
        if self.plotType[r1][col] == 'x':
          continue

        eMule1 = self.getTerritoryIDFromName(str(row)+","+str(col)+"-Energy");
        fMule1 = self.getTerritoryIDFromName(str(row)+","+str(col)+"-Food");
        sMule1 = self.getTerritoryIDFromName(str(row)+","+str(col)+"-Smithore");
        eMule2 = self.getTerritoryIDFromName(str(r1)+","+str(col)+"-Energy");
        fMule2 = self.getTerritoryIDFromName(str(r1)+","+str(col)+"-Food");
        sMule2 = self.getTerritoryIDFromName(str(r1)+","+str(col)+"-Smithore");
        
        self.addBorder(eMule1,eMule2,borderType="Artillery")
        self.addBorder(eMule1,fMule2,borderType="Artillery")
        self.addBorder(eMule1,sMule2,borderType="Artillery")

        self.addBorder(fMule1,eMule2,borderType="Artillery")
        self.addBorder(fMule1,fMule2,borderType="Artillery")
        self.addBorder(fMule1,sMule2,borderType="Artillery")

        self.addBorder(sMule1,eMule2,borderType="Artillery")
        self.addBorder(sMule1,fMule2,borderType="Artillery")
        self.addBorder(sMule1,sMule2,borderType="Artillery")
        
        
        for playerID in ["P1","P2","P3","P4","P5","P6"]: 
          factoryID = self.tidBattery[playerID]
          tName = playerID + "-" + str(row) + "," + str(col) + "+"+str(r1) + "," + str(col) +"-EnergyNieghborsBonus"
          members = set([eMule1, eMule2, self.tidPID[playerID]])
          self.addContinent(tName,members,bonus="1",factory=factoryID,factoryType="AutoCapture")

          factoryID = self.tidSmithore[playerID]
          tName = playerID + "-" + str(row) + "," + str(col) + "+"+str(r1) + "," + str(col) +"-SmithoreNieghborsBonus"
          members = set([sMule1, sMule2, self.tidPID[playerID]])
          self.addContinent(tName,members,bonus="1",factory=factoryID,factoryType="AutoCapture")

          factoryID = self.tidMercenary[playerID]
          tName = playerID + "-" + str(row) + "," + str(col) + "+"+str(r1) + "," + str(col) +"-FoodNieghborsBonus"
          members = set([fMule1, fMule2, self.tidPID[playerID]])
          self.addContinent(tName,members,bonus="1",factory=factoryID,factoryType="AutoCapture")

       
  
  def addMuleTerritories(self):
    for row in range(5):
      for col in range(11):
        if self.plotType[row][col] != 'x':
          
          muleName = str(row)+","+str(col)+"-Energy"
          muleX = col*93+60
          muleY = row*94+15        
          etid = self.addTerritory(muleName,muleX,muleY,scenario_type="Neutral Capital",scenario_units="0",scenario_seat="0")                
        
          muleName = str(row)+","+str(col)+"-Food"
          muleY += 28
          ftid = self.addTerritory(muleName,muleX,muleY,scenario_type="Neutral Capital",scenario_units="0",scenario_seat="0")
          
          muleName = str(row)+","+str(col)+"-Smithore"
          muleY += 35
          stid = self.addTerritory(muleName,muleX,muleY,scenario_type="Neutral Capital",scenario_units="0",scenario_seat="0")
          
          for playerID in ["P1","P2","P3","P4","P5","P6"]:
            self.addBorder(self.tidMule1[playerID],etid,direction="One-way",ftattackmod="-3")
            self.addBorder(self.tidMule1[playerID],ftid,direction="One-way",ftattackmod="-3")
            self.addBorder(self.tidMule1[playerID],stid,direction="One-way",ftattackmod="-3")
        
            self.addBorder(self.tidMule2[playerID],etid,direction="One-way",ftattackmod="-3")
            self.addBorder(self.tidMule2[playerID],ftid,direction="One-way",ftattackmod="-3")
            self.addBorder(self.tidMule2[playerID],stid,direction="One-way",ftattackmod="-3")
        
            self.addBorder(self.tidMule3[playerID],etid,direction="One-way",ftattackmod="-3")
            self.addBorder(self.tidMule3[playerID],ftid,direction="One-way",ftattackmod="-3")
            self.addBorder(self.tidMule3[playerID],stid,direction="One-way",ftattackmod="-3")
        
  def addMuleBoxTerritories(self):
    playerX = 0
    for playerID in ["P1","P2","P3","P4","P5","P6"]:
      for boxID in ["1","2","3","4","5","6","7","8"]:
        
        tName = playerID + "-SmithoreBox"+boxID
        tX = playerX*132+((int(boxID)+1)//2-1)*13+19
        if playerX > 2:
          tX = tX + 238
        tY = 532 + (int(boxID)%2) * 12
        self.tidBoxes[playerID][boxID] = self.addTerritory(tName,tX,tY,scenario_type="Allocated",scenario_units="1",scenario_seat=playerID[1:2], max_units="1")
        
        self.addBorder(self.tidSmithore[playerID],self.tidBoxes[playerID][boxID])
      playerX = playerX + 1        
        
  
  def addFortifiesForMercenaries(self):
    for row in range(5):
      for col in range(11):
        if self.plotType[row][col] != 'x':
  
          eMule = self.getTerritoryIDFromName(str(row)+","+str(col)+"-Energy");
          fMule = self.getTerritoryIDFromName(str(row)+","+str(col)+"-Food");
          sMule = self.getTerritoryIDFromName(str(row)+","+str(col)+"-Smithore");
          for playerID in ["P1","P2","P3","P4","P5","P6"]:
            self.addBorder(eMule,self.tidMercenary[playerID],borderType="Fortify Only")
            self.addBorder(fMule,self.tidMercenary[playerID],borderType="Fortify Only")
            self.addBorder(sMule,self.tidMercenary[playerID],borderType="Fortify Only")


  def addMuleFactories(self):
    
    # add factories that Mules earn
    for row in range(5):
      for col in range(11):
        if self.plotType[row][col] != 'x':

          eMule = self.getTerritoryIDFromName(str(row)+","+str(col)+"-Energy");
          fMule = self.getTerritoryIDFromName(str(row)+","+str(col)+"-Food");
          sMule = self.getTerritoryIDFromName(str(row)+","+str(col)+"-Smithore");
          eBonus,fBonus,sBonus = self.getBonusesFromRC(row,col)
          for playerID in ["P1","P2","P3","P4","P5","P6"]:          
  
            # ENERGY MULES PRODUCE FULL ENERGY EVEN WITHOUT BATTERY.
            factoryID = self.tidBattery[playerID]
            tName = playerID + "-" + str(row) + "," + str(col) + "-EnergyMule"
            members = set([eMule, self.tidPID[playerID]])
            self.addContinent(tName,members,bonus=eBonus,factory=factoryID,factoryType="AutoCapture")
  
            ##  FOOD 
            factoryID = self.tidMercenary[playerID]
            tName = playerID + "-" + str(row) + "," + str(col) + "-FoodMule"
            members = set([fMule, self.tidPID[playerID]])
            
            if (fBonus > 2):
              bonus = fBonus-2
              self.addContinent(tName,members,factory=factoryID,bonus=bonus,factoryType="AutoCapture")
              bonus = 2
            else:            
              bonus = fBonus
            
            tName = playerID + "-" + str(row) + "," + str(col) + "-FoodMuleWithEnergy"
            members.add(self.tidBattery[playerID])
            self.addContinent(tName,members,factory=factoryID,bonus=bonus,factoryType="AutoCapture")
  
            ## SMITHORE 
            factoryID = self.tidSmithore[playerID]
            tName = playerID + "-" + str(row) + "," + str(col) + "-SmithoreMule"
            members = set([sMule, self.tidPID[playerID]])
            
            if (sBonus > 2):
              bonus = sBonus-2
              self.addContinent(tName,members,factory=factoryID,bonus=bonus,factoryType="AutoCapture")
              bonus = 2
            else:            
              bonus = sBonus
            
            tName = playerID + "-" + str(row) + "," + str(col) + "-SmithoreMuleWithEnergy"
            members.add(self.tidBattery[playerID])
            self.addContinent(tName,members,factory=factoryID,bonus=bonus,factoryType="AutoCapture")
          
        
        
    # add factories to drain battery
    for row in range(5):
      for col in range(11):
        if self.plotType[row][col] != 'x':
  
          eMule = self.getTerritoryIDFromName(str(row)+","+str(col)+"-Energy");
          fMule = self.getTerritoryIDFromName(str(row)+","+str(col)+"-Food");
          sMule = self.getTerritoryIDFromName(str(row)+","+str(col)+"-Smithore");
          for playerID in ["P1","P2","P3","P4","P5","P6"]:
            factoryID = self.tidBattery[playerID]
            #tName = playerID + "-" + str(row) + "," + str(col) + "-BatteryDrain-Energy"
            #members = set([eMule,  self.tidPID[playerID]])          
            #self.addContinent(tName, members, factory=factoryID, bonus="-1", factoryType="Standard")
            
            tName = playerID + "-" + str(row) + "," + str(col) + "-BatteryDrain-Food"
            members = set([fMule, self.tidPID[playerID]])          
            self.addContinent(tName, members, factory=factoryID, bonus="-1", factoryType="Standard")
            
            tName = playerID + "-" + str(row) + "," + str(col) + "-BatteryDrain-Smithore"
            members = set([sMule, self.tidPID[playerID]])          
            self.addContinent(tName, members, factory=factoryID, bonus="-1", factoryType="Standard")

        
    # add factories to build a mule
    '''
    
    for playerID in ["P1","P2","P3","P4","P5","P6"]:
      members = set()
      for boxID in ["1","2","3","4","5","6","7","8"]:
        members.add(self.tidBoxes[playerID][boxID])
        
      for boxID in ["1","2","3","4","5","6","7","8"]:
        factoryID = self.tidBoxes[playerID][boxID]
        tName = playerID + "-BuildMule-Box"+boxID
        self.addContinent(tName,members,factory=factoryID,bonus="-1",factoryType="Standard")      
      
      factoryID = self.tidMule1[playerID]
      tName = playerID + "-BuildMule1"
      self.addContinent(tName,members,factory=factoryID,bonus="1",factoryType="AutoCapture")
      
      members.add(self.tidMule1[playerID])
      factoryID = self.tidMule2[playerID]
      tName = playerID + "-BuildMule2"
      self.addContinent(tName,members,factory=factoryID,bonus="1",factoryType="AutoCapture")

      members.add(self.tidMule2[playerID])
      factoryID = self.tidMule3[playerID]
      tName = playerID + "-BuildMule3"
      self.addContinent(tName,members,factory=factoryID,bonus="1",factoryType="AutoCapture")

      members.add(self.tidMule3[playerID])
      factoryID = self.tidMule4[playerID]
      tName = playerID + "-BuildMule4"
      self.addContinent(tName,members,factory=factoryID,bonus="1",factoryType="AutoCapture")
      
    '''
    for playerID in ["P1","P2","P3","P4","P5","P6"]:
            
      S = self.tidSmithore[playerID]
      P = self.tidPID[playerID]
      
      U = self.tidMule1[playerID]
      R = self.tidReady1[playerID]
      B1 = self.tidBuild1[playerID]
      B2 = self.tidIng1[playerID]        
      self.addBuilderPattern(S, P, R, B1, B2, U, -10, 1, playerID + "MuleFactory1-")
      
      U = self.tidMule2[playerID]
      R = self.tidReady2[playerID]
      B1 = self.tidBuild2[playerID]
      B2 = self.tidIng2[playerID]        
      self.addBuilderPattern(S, P, R, B1, B2, U, -10, 1, playerID + "MuleFactory2-")
      
      U = self.tidMule3[playerID]
      R = self.tidReady3[playerID]
      B1 = self.tidBuild3[playerID]
      B2 = self.tidIng3[playerID]        
      self.addBuilderPattern(S, P, R, B1, B2, U, -10, 1, playerID + "MuleFactory3-")
      
      
        
    # add free 1 smithore a turn
    for playerID in ["P1","P2","P3","P4","P5","P6"]:
      factoryID = self.tidSmithore[playerID]
      members = set()
      members.add(self.tidPID[playerID])
      tName = playerID + "-" + "-FreeSmithore"
      self.addContinent(tName,members,factory=factoryID,bonus="1",factoryType="AutoCapture")
      
    # add factories to kill mules when more than 1 in a territory.
    for row in range(5):
      for col in range(11):
        if self.plotType[row][col] != 'x':
  
          eMule = self.getTerritoryIDFromName(str(row)+","+str(col)+"-Energy");
          fMule = self.getTerritoryIDFromName(str(row)+","+str(col)+"-Food");
          sMule = self.getTerritoryIDFromName(str(row)+","+str(col)+"-Smithore");
          
          # E & F 
          members = set([eMule,fMule])
          tName = playerID + "-" + str(row) + "," + str(col) + "-Kill-E-ef" 
          self.addContinent(tName,members,factory=eMule,bonus="-100",factoryType="AutoCapture")
  
          tName = playerID + "-" + str(row) + "," + str(col) + "-Kill-F-ef" 
          self.addContinent(tName,members,factory=fMule,bonus="-100",factoryType="AutoCapture")
          
          # E & S
          members = set([eMule,sMule])
          tName = playerID + "-" + str(row) + "," + str(col) + "-Kill-E-es" 
          self.addContinent(tName,members,factory=eMule,bonus="-100",factoryType="AutoCapture")
  
          tName = playerID + "-" + str(row) + "," + str(col) + "-Kill-s-es" 
          self.addContinent(tName,members,factory=sMule,bonus="-100",factoryType="AutoCapture")
          
          # S & F
          members = set([sMule,fMule])
          tName = playerID + "-" + str(row) + "," + str(col) + "-Kill-S-sf" 
          self.addContinent(tName,members,factory=sMule,bonus="-100",factoryType="AutoCapture")
  
          tName = playerID + "-" + str(row) + "," + str(col) + "-Kill-F-sf" 
          self.addContinent(tName,members,factory=fMule,bonus="-100",factoryType="AutoCapture")
        
          
        
      
def setupMuleMap():
  wgmap = MULEWGMap()
  wgmap.loadMapFromFile('//DISKSTATION/data/wargear development/MULE/M.U.L.E.(6).xml')
  wgmap.doSetup()
  wgmap.saveMapToFile('//DISKSTATION/data/wargear development/MULE/Out.xml',False)

    
    

if __name__ == '__main__':
  pass