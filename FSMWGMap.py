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
      
class FSMWGMap(WGMap):
  """
  Extends WGMap.
  A convenient way to organize all the stuff for my 'Finite State Machine' map 

  
  # How it all works.

  # PC movement
  # setupStateTransitions does sets the next PC arrow based on the bits @ the current PC
  # first assume no bits, then any 1 bit removes the zero bit setting & adds itself, 2 bits removes its 2 1-bit settings and adds itself, 3 bits, etc.
  

  
  # Elimination
  # For each cell, Factories with wall as member have -1 to head in that wall. 
  # eliminations for collision with own wall -  for head movement factories, also cancel that movement with -1 if head & wall owned.   
  """  
  
  
  def doFullSetup(self):
      
    self.loadIDSets()    
    self.setupStateTransitions()
    self.addGrid()
    self.addGridFactories()
    self.addHeadFactories()
    self.addInitializationGrid()
  
  
    #     PC    0,1,2,3,4,5,6,7
    # 0 actions r,d,l,u,l,d,u,r
    # 1 actions l,d,r,u,r,d,u,l

  def addInitializationGrid(self):
    for xi in range(3):
      for yi in range (1,7):
        x = 380+xi*5
        y = 600+yi*5
        self.addTerritory("Init-"+str(xi)+"-"+str(yi),x,y)
        
        members = set()
        members.add(self.getTerritoryIDFromName("Init-"+str(xi)+"-"+str(yi)))
        
        # clear starting values from init grid
        factory = self.getTerritoryIDFromName("Init-"+str(xi)+"-"+str(yi))
        self.addContinent("Init-"+str(xi)+"-"+str(yi),members,-1,factory,factoryType="AutoCapture")
        
        
        # transfer starting value to p0 bits        
        members2 = set(members)
        members2.add(self.getTerritoryIDFromName("0-Bit Bank"))
        factory = self.getTerritoryIDFromName(self.getBitName("0",self.states[yi], xi))
        self.addContinent("Init-P0-"+str(xi)+"-"+str(yi),members2,1,factory,factoryType="AutoCapture")

        # transfer starting value to p1 bits        
        members2 = set(members)
        members2.add(self.getTerritoryIDFromName("1-Bit Bank"))
        factory = self.getTerritoryIDFromName(self.getBitName("1",self.states[yi], xi)) 
        self.addContinent("Init-P1-"+str(xi)+"-"+str(yi),members2,1,factory,factoryType="AutoCapture")


  def getPCDeltaX(self,player,PC):
    if (PC == 1 or PC == 3 or PC == 5 or PC == 6):
      return 0;
    
    if (player==0):
      if (PC==0 or PC == 7):
        return 1;
      else:
        return -1;
      
    if (player==1):
      if (PC==0 or PC == 7):
        return -1;
      else:
        return 1;
      
  def getPCDeltaY(self,PC):
    if (PC == 0 or PC ==2 or PC == 4 or PC == 7):
      return 0;
    
    if (PC==1 or PC == 5):
      return 1;
    else:
      return -1;

  def getXOffset(self,stringDir):
    if(stringDir=="Left"):
      return -1
    if(stringDir=="Right"):
      return 1
    else:
      return 0
    

  def getYOffset(self,stringDir):
    if(stringDir=="Up"):
      return -1
    if(stringDir=="Down"):
      return 1
    else:
      return 0
      
      
  def getPCDirection(self,player,PC):
    if self.getPCDeltaX(player,PC) == 1:
      return "Right"
    if self.getPCDeltaX(player,PC) == -1:
      return "Left"
    if self.getPCDeltaY(PC) == 1:
      return "Down"
    if self.getPCDeltaY(PC) == -1:
      return "Up"

    raise LookupError,"getPCDirection failed. for " + str( player ) + "," + str(PC)
  
  
  
  def addGridFactories(self):
    
    # 0 actions r,d,l,u,l,d,u,r
    # 1 actions l,d,r,u,r,d,u,l

    for xi in range(10):
      for yi in range(10):
   
        # head desctruction factories
        name="Kill-"+str(xi)+"-"+str(yi)+"-Head"
        members = set()
        members.add(self.getTerritoryIDFromName("grid-"+str(xi)+"-"+str(yi)+"-Wall"))
        factory = self.getTerritoryIDFromName("grid-"+str(xi)+"-"+str(yi)+"-Head")
        self.addContinent(name,members,bonus=-1,factory=factory,factoryType="AutoCapture")
        
        # wall building factories    
        name="Build-"+str(xi)+"-"+str(yi)+"-Wall"
        members = set()
        members.add(self.getTerritoryIDFromName("grid-"+str(xi)+"-"+str(yi)+"-Head"))
        factory = self.getTerritoryIDFromName("grid-"+str(xi)+"-"+str(yi)+"-Wall")
        self.addContinent(name,members,bonus=1,factory=factory,factoryType="AutoCapture")
             
    
  def addGrid(self):
    # UL X = 360, UL Y = 250
    for xi in range(10):
      for yi in range (10):
        x = 360+xi*30
        y = 250+yi*30
        self.addTerritory("grid-"+str(xi)+"-"+str(yi)+"-Head",x,y,1,scenario_type="Neutral Capital", scenario_seat="0", scenario_units="0")
        self.addTerritory("grid-"+str(xi)+"-"+str(yi)+"-Wall",x-10,y-10,1,scenario_type="Neutral", scenario_seat="0", scenario_units="0")
    
    
  def getBitName(self,computerN,state, bitSignificance):
    return str(computerN)+"-"+str(state)+"-b"+str(bitSignificance)
    
  
  def loadIDSets(self):
    self.states = ["000","001", "010","011","100","101", "110","111"]
    self.PC = []
    self.PC.append([])
    self.PC.append([])
    for nPC in range(8):
      self.PC[0].append(str(self.getTerritoryIDFromName("0-pc-"+str(nPC)))) 
      self.PC[1].append(self.getTerritoryIDFromName("1-pc-"+str(nPC)))
          

  def inBounds(self,targetX,targetY):
    if (targetX < 0 or targetX > 9):
      return False
    if (targetY < 0 or targetY > 9):
      return False
    return True
          
          
  # head determines which cell to move into.
  # bits & PC determine which heads in cell to turn on/off
  # these factories move the heads around.
  def addHeadFactories(self):

    for xi in range(10):
      for yi in range(10):
        for nPlayer in [0,1]:
          for nPC in range(8):
            nextDirection = self.getPCDirection(nPlayer,nPC)            

            targetX = xi + self.getXOffset(nextDirection)
            targetY = yi + self.getYOffset(nextDirection)
            if not self.inBounds(targetX,targetY):
              continue
            
          
            targetID = self.getTerritoryIDFromName("grid-"+str(targetX)+"-"+str(targetY)+"-Head")
                    
            members = set()
            # add member of this xi,yi,head & Program Counter
            members.add(self.getTerritoryIDFromName("grid-"+str(xi)+"-"+str(yi)+"-Head"))
            members.add(self.PC[nPlayer][nPC])                  
              
            name = "MoveHead-"+str(xi)+","+str(yi)+"_"+str(nPlayer)+"-State"+str(nPC)        
            self.addContinent(name,members,factory=targetID,bonus=1,factoryType="AutoCapture")
            
            # now check if the head was in a wall and remove it.          
            members.add(self.getTerritoryIDFromName("grid-"+str(xi)+"-"+str(yi)+"-Wall"))
            name = "RemoveHead-"+str(xi)+","+str(yi)+"_"+str(nPlayer)+"-State"+str(nPC)      
            self.addContinent(name,members,factory=targetID,bonus=-1,factoryType="AutoCapture")
            
            

        # remove old heads
        members = set()
        members.add(self.getTerritoryIDFromName("grid-"+str(xi)+"-"+str(yi)+"-Head"))
        targetID = self.getTerritoryIDFromName("grid-"+str(xi)+"-"+str(yi)+"-Head")
        name = "RemoveHead-"+str(xi)+","+str(yi)        
        self.addContinent(name,members,factory=targetID,bonus=-1,factoryType="AutoCapture")

               
  def setupStateTransitions(self):
    
    for computerN in [0,1]:
      #Remove all set PC indicators, in case no other bits are set, set 000 as the default
      self.addContinent(str(computerN)+"-A0",self.PC[computerN][0],factory=self.PC[computerN][0],bonus=-1,factoryType="AutoCapture")
      self.addContinent(str(computerN)+"-A1",self.PC[computerN][1],factory=self.PC[computerN][1],bonus=-1,factoryType="AutoCapture")
      self.addContinent(str(computerN)+"-A2",self.PC[computerN][2],factory=self.PC[computerN][2],bonus=-1,factoryType="AutoCapture")
      self.addContinent(str(computerN)+"-A3",self.PC[computerN][3],factory=self.PC[computerN][3],bonus=-1,factoryType="AutoCapture")
      self.addContinent(str(computerN)+"-A4",self.PC[computerN][4],factory=self.PC[computerN][4],bonus=-1,factoryType="AutoCapture")
      self.addContinent(str(computerN)+"-A5",self.PC[computerN][5],factory=self.PC[computerN][5],bonus=-1,factoryType="AutoCapture")
      self.addContinent(str(computerN)+"-A6",self.PC[computerN][6],factory=self.PC[computerN][6],bonus=-1,factoryType="AutoCapture")
      self.addContinent(str(computerN)+"-A7",self.PC[computerN][7],factory=self.PC[computerN][7],bonus=-1,factoryType="AutoCapture")
      
      
    # def addContinent(self, continentName, memberIDs, bonus=1,factory=-1,factoryType="Standard"):
    for nPC in range(8):
      for computerN in [0,1]:
     
        
        self.addContinent(str(computerN)+"-State"+str(nPC)+"-A8",self.PC[computerN][nPC],factory=self.PC[computerN][0],bonus=1,factoryType="AutoCapture")
     
        b0 = str(self.getTerritoryIDFromName(self.getBitName(str(computerN),self.states[nPC],0)))
        b1 = str(self.getTerritoryIDFromName(self.getBitName(str(computerN),self.states[nPC],1)))
        b2 = str(self.getTerritoryIDFromName(self.getBitName(str(computerN),self.states[nPC],2)))      
        
        # For all single bit next states, clear the 000 state, and set the according next state.
        # 001
        self.addContinent(str(computerN)+"-State"+str(nPC)+"-B0",[self.PC[computerN][nPC], b0],factory=self.PC[computerN][1],bonus=1,factoryType="AutoCapture")
        self.addContinent(str(computerN)+"-State"+str(nPC)+"-B1",[self.PC[computerN][nPC] , b0],factory=self.PC[computerN][0],bonus=-1,factoryType="AutoCapture")
        
        # 010
        self.addContinent(str(computerN)+"-State"+str(nPC)+"-B2",[self.PC[computerN][nPC] , b1],factory=self.PC[computerN][2],bonus=1,factoryType="AutoCapture")
        self.addContinent(str(computerN)+"-State"+str(nPC)+"-B3",[self.PC[computerN][nPC] , b1],factory=self.PC[computerN][0],bonus=-1,factoryType="AutoCapture")
        
        # 100
        self.addContinent(str(computerN)+"-State"+str(nPC)+"-B4",[self.PC[computerN][nPC] , b2],factory=self.PC[computerN][4],bonus=1,factoryType="AutoCapture")
        self.addContinent(str(computerN)+"-State"+str(nPC)+"-B5",[self.PC[computerN][nPC] , b2],factory=self.PC[computerN][0],bonus=-1,factoryType="AutoCapture")
       
       
        # For all double bit next states, clear the 1 bit states, and set the next state
        # 011
        self.addContinent(str(computerN)+"-State"+str(nPC)+"-C0",[self.PC[computerN][nPC] , b0 , b1],factory=self.PC[computerN][3],bonus=1,factoryType="AutoCapture")
        self.addContinent(str(computerN)+"-State"+str(nPC)+"-C1",[self.PC[computerN][nPC] , b0 , b1],factory=self.PC[computerN][1],bonus=-1,factoryType="AutoCapture")       
        self.addContinent(str(computerN)+"-State"+str(nPC)+"-C2",[self.PC[computerN][nPC] , b0 , b1],factory=self.PC[computerN][2],bonus=-1,factoryType="AutoCapture")
        
        # 101
        self.addContinent(str(computerN)+"-State"+str(nPC)+"-C4",[self.PC[computerN][nPC] , b2 , b0],factory=self.PC[computerN][5],bonus=1,factoryType="AutoCapture")
        self.addContinent(str(computerN)+"-State"+str(nPC)+"-C5",[self.PC[computerN][nPC] , b2 , b0],factory=self.PC[computerN][1],bonus=-1,factoryType="AutoCapture")
        self.addContinent(str(computerN)+"-State"+str(nPC)+"-C7",[self.PC[computerN][nPC] , b2 , b0],factory=self.PC[computerN][4],bonus=-1,factoryType="AutoCapture")
        
        # 110
        self.addContinent(str(computerN)+"-State"+str(nPC)+"-C8",[self.PC[computerN][nPC] , b2 , b1],factory=self.PC[computerN][6],bonus=1,factoryType="AutoCapture")
        self.addContinent(str(computerN)+"-State"+str(nPC)+"-C10",[self.PC[computerN][nPC] , b2 , b1],factory=self.PC[computerN][2],bonus=-1,factoryType="AutoCapture")
        self.addContinent(str(computerN)+"-State"+str(nPC)+"-C11",[self.PC[computerN][nPC] , b2 , b1],factory=self.PC[computerN][4],bonus=-1,factoryType="AutoCapture")
       
        
        # For 111, clear all states except 111.
        self.addContinent(str(computerN)+"-State"+str(nPC)+"-D1",[self.PC[computerN][nPC] , b2 , b1 , b0],factory=self.PC[computerN][7],bonus=1,factoryType="AutoCapture")
        self.addContinent(str(computerN)+"-State"+str(nPC)+"-D5",[self.PC[computerN][nPC] , b2 , b1 , b0],factory=self.PC[computerN][3],bonus=-1,factoryType="AutoCapture")
        self.addContinent(str(computerN)+"-State"+str(nPC)+"-D7",[self.PC[computerN][nPC] , b2 , b1 , b0],factory=self.PC[computerN][5],bonus=-1,factoryType="AutoCapture")
        self.addContinent(str(computerN)+"-State"+str(nPC)+"-D8",[self.PC[computerN][nPC] , b2 , b1 , b0],factory=self.PC[computerN][6],bonus=-1,factoryType="AutoCapture")
       
       
def setupFSMMap():
  wgmap = FSMWGMap()
  wgmap.load_map_from_file('//DISKSTATION/data/wargear development/Finite State Machine/Finite State Machine(6).xml')
  #wgmap.loadMapFromFile('//DISKSTATION/data/wargear development/LEGO/Hoarding LEGO.xml')

  wgmap.doFullSetup()
  wgmap.save_map_to_file('//DISKSTATION/data/wargear development/Finite State Machine/out.xml', False)
 


if __name__ == '__main__':
  pass