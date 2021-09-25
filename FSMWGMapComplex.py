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


class FSMWGMapComplex(WGMap):
  """
  Extends WGMap.
  A convenient way to organize all the stuff for my 'Finite State Machine' map with the tech tree.
  """
  
  
  # How it all works.

  # PC movement
  # setupStateTransitions does sets the next PC arrow based on the bits @ the current PC
  # first assume no bits, then any 1 bit removes the zero bit setting & adds itself, 2 bits removes its 2 1-bit settings and adds itself, 3 bits, etc.
  
  # Grid Movement:
  # Tag along to PC movement.  
  # Every time we setup something moving to a state, add a head in the current PC direction, pointing in the direction defined by the next PC direction
  # Also factories to build walls.  Member is any head.  Target is the wall for that grid.
  # Also factories to remove old heads.  Member is any wall.  Target is all the heads in that grid.
  
  
  # Elimination
  # For each cell, Factories with wall as member have -1 to all heads in that wall.  This handles Collision with opponents wall.
  # More complicated is eliminations for collision with own wall.  The previously mentioned factories will remove your head, but it is too late, 
  # because it is already being respawned in a nearby cell.  So we need additional factories:
  # Members = wall and a associated head.  Target is all heads in the bordering cells in the direction of the current head.
   
  '''
  def addEliminationTerritories(self):
    for xi in range(10):
      for yi in range(10):
        members = #wall
        for direction in ["Up","Down","Left","Right"]:
          factory = #direction
          self.addContinent()
          
  '''    
 
    
  
  
  # todo: all this is wrong, because getContinentMembersFromName() returns
  # a string instead of a set.
  def doFullSetup(self):
      
    self.loadIDSets()    
    self.setupStateTransitions()
    self.addGrid()
    self.addGridFactories()
    self.addHeadFactories()
  
    #     PC    0,1,2,3,4,5,6,7
    # 0 actions r,d,l,u,l,d,u,r
    # 1 actions l,d,r,u,r,d,u,l

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
  
  
  '''
  def addHeadFactories(self,xi,yi,playerNum,PCID,b0ID,b1ID,b2ID):
  
    name= str(playerNum) + "-PC"+str(PCID)+"-"+str(xi)+"-"+str(yi)+"-"+direction
    members = set()
    members.add(self.getTerritoryIDFromName("grid-"+str(xi)+"-"+str(yi)+"-"+direction))
    members.add(self.PC[0][1])
    factory = self.getTerritoryIDFromName("grid-"+str(xi+1)+"-"+str(yi)+"-Wall")
    self.addContinent(name,members,bonus=4,factory=factory,factoryType="AutoCapture")
  '''  
    
  
  def addGridFactories(self):
    
    # 0 actions r,d,l,u,l,d,u,r
    # 1 actions l,d,r,u,r,d,u,l
    #
    #           self.addTerritory("grid-"+str(xi)+"-"+str(yi)+"-Right",x-10,y,4,scenario_type="Neutral", scenario_seat="0", scenario_units="0")
    #       self.addTerritory("grid-"+str(xi)+"-"+str(yi)+"-Left",x+10,y,4,scenario_type="Neutral", scenario_seat="0", scenario_units="0")
    #      self.addTerritory("grid-"+str(xi)+"-"+str(yi)+"-Up",x,y+10,4,scenario_type="Neutral", scenario_seat="0", scenario_units="0")
    #     self.addTerritory("grid-"+str(xi)+"-"+str(yi)+"-Down",x,y-10,4,scenario_type="Neutral", scenario_seat="0", scenario_units="0")
    #    self.addTerritory("grid-"+str(xi)+"-"+str(yi)+"-Wall",x,y+12,4,scenario_type="Neutral", scenario_seat="0", scenario_units="0")

    for xi in range(10):
      for yi in range(10):
        for direction in ["Up","Down","Left","Right"]:
          # head desctruction factories
          name="Kill "+str(xi)+"-"+str(yi)+"-"+direction+" Head"
          members = set()
          members.add(self.getTerritoryIDFromName("grid-"+str(xi)+"-"+str(yi)+"-Wall"))
          factory = self.getTerritoryIDFromName("grid-"+str(xi)+"-"+str(yi)+"-"+direction)
          self.addContinent(name,members,bonus=-1,factory=factory,factoryType="Standard")
          
          # wall building factories    
          name="Build "+str(xi)+"-"+str(yi)+"-"+direction+" Wall"
          members = set()
          members.add(self.getTerritoryIDFromName("grid-"+str(xi)+"-"+str(yi)+"-"+direction))
          factory = self.getTerritoryIDFromName("grid-"+str(xi)+"-"+str(yi)+"-Wall")
          self.addContinent(name,members,bonus=1,factory=factory,factoryType="AutoCapture")
             
    
 
  def addGrid(self):
    # UL X = 360, UL Y = 250
    for xi in range(10):
      for yi in range (10):
        x = 360+xi*30
        y = 250+yi*30
        self.addTerritory("grid-"+str(xi)+"-"+str(yi)+"-Right",x-10,y,4,scenario_type="Neutral", scenario_seat="0", scenario_units="0")
        self.addTerritory("grid-"+str(xi)+"-"+str(yi)+"-Left",x+10,y,4,scenario_type="Neutral", scenario_seat="0", scenario_units="0")
        self.addTerritory("grid-"+str(xi)+"-"+str(yi)+"-Up",x,y+10,4,scenario_type="Neutral", scenario_seat="0", scenario_units="0")
        self.addTerritory("grid-"+str(xi)+"-"+str(yi)+"-Down",x,y-10,4,scenario_type="Neutral", scenario_seat="0", scenario_units="0")
        self.addTerritory("grid-"+str(xi)+"-"+str(yi)+"-Wall",x,y+12,4,scenario_type="Neutral", scenario_seat="0", scenario_units="0")
    
    
    
  def getBitName(self,computerN,state, bitSignificance):
    return str(computerN)+"-"+state+"-b"+str(bitSignificance)
    
  
  def loadIDSets(self):
    
    self.states = ["000","001", "010","011","100","101", "110","111"]
    self.PC = []
    self.PC.append([])
    self.PC.append([])
    for nPC in range(8):
      self.PC[0].append(str(self.getTerritoryIDFromName("0-pc-"+str(nPC)))) 
      self.PC[1].append(self.getTerritoryIDFromName("1-pc-"+str(nPC)))
          
          
  # head determines which cell to move into.
  # bits & PC determine which heads in cell to turn on/off
  # these factories move the heads around.
  def addHeadFactories(self):

    def getXOffset(stringDir):
      if(stringDir=="Left"):
        return -1
      if(stringDir=="Right"):
        return 1
      else:
        return 0
      

    def getYOffset(stringDir):
      if(stringDir=="Up"):
        return -1
      if(stringDir=="Down"):
        return 1
      else:
        return 0
      

    for xi in range(10):
      for yi in range(10):
        for nextDirection in  ["Up","Down","Left","Right"]:

          targetX = xi + getXOffset(nextDirection)
          targetY = yi + getYOffset(nextDirection)
          if (targetX < 0 or targetX > 9):
            continue
          if (targetY < 0 or targetY > 9):
            continue
          
          members = set()
          # add member of this xi,yi,nextDirection head.
          members.add(self.getTerritoryIDFromName("grid-"+str(targetX)+"-"+str(targetY)+"-"+nextDirection))
  
          
  
          # have to create separate factories for each player, so that opponent PC arrow does not influence your snake.
          for nPlayer in [0,1]:
  
            #setup factoryIDs for each state
            direction000 = self.getPCDirection(nPlayer,0)
            factory000 = self.getTerritoryIDFromName("grid-"+str(targetX)+"-"+str(targetY)+"-"+direction000)
  
            direction001 = self.getPCDirection(nPlayer,1)
            factory001 = self.getTerritoryIDFromName("grid-"+str(targetX)+"-"+str(targetY)+"-"+direction001)
   
            direction010 = self.getPCDirection(nPlayer,0)
            factory010 = self.getTerritoryIDFromName("grid-"+str(targetX)+"-"+str(targetY)+"-"+direction010)
           
            direction011 = self.getPCDirection(nPlayer,0)
            factory011 = self.getTerritoryIDFromName("grid-"+str(targetX)+"-"+str(targetY)+"-"+direction011)
  
            direction100 = self.getPCDirection(nPlayer,0)
            factory100 = self.getTerritoryIDFromName("grid-"+str(targetX)+"-"+str(targetY)+"-"+direction100)
  
            direction101 = self.getPCDirection(nPlayer,0)
            factory101 = self.getTerritoryIDFromName("grid-"+str(targetX)+"-"+str(targetY)+"-"+direction101)
  
            direction110 = self.getPCDirection(nPlayer,0)
            factory110 = self.getTerritoryIDFromName("grid-"+str(targetX)+"-"+str(targetY)+"-"+direction110)
  
            direction111 = self.getPCDirection(nPlayer,0)
            factory111 = self.getTerritoryIDFromName("grid-"+str(targetX)+"-"+str(targetY)+"-"+direction111)
  
            for nPC in range(8):
  
              b0 = str(self.getTerritoryIDFromName(self.getBitName(str(nPlayer),self.states[nPC],0)))
              b1 = str(self.getTerritoryIDFromName(self.getBitName(str(nPlayer),self.states[nPC],1)))
              b2 = str(self.getTerritoryIDFromName(self.getBitName(str(nPlayer),self.states[nPC],2)))     
              
              # add PC arrow to members set.
              # members set is now PC Arrow & current head
              PCHMembers = list(members)
              PCHMembers.append(self.PC[nPlayer][nPC])
  
              #Add Factory - In case no bits are set, use factory000 direction as the default 
              name = nextDirection + str(xi)+","+str(yi)+"_"+str(nPlayer)+"-State"+str(nPC)+"-A1"           
              self.addContinent(name,PCHMembers,factory=factory000,bonus=1,factoryType="AutoCapture")
                      
              # if 1 bit is set
              # add factory001, 010, 100  (for each factory add on bit as member)
              # remove factory000     
              tempMembers = list(PCHMembers)       
              tempMembers.append(b0)
              name = nextDirection +str(xi)+","+str(yi)+"_"+str(nPlayer)+"-State"+str(nPC)+"-B1"         
              self.addContinent(name,tempMembers,factory=factory001,bonus=1,factoryType="AutoCapture")
              name = nextDirection +str(xi)+","+str(yi)+"_"+str(nPlayer)+"-State"+str(nPC)+"-B2"         
              self.addContinent(name,tempMembers,factory=factory000,bonus=-1,factoryType="AutoCapture")
  
              tempMembers = list(PCHMembers)       
              tempMembers.append(b1)
              name = nextDirection +str(xi)+","+str(yi)+"_"+str(nPlayer)+"-State"+str(nPC)+"-B3"         
              self.addContinent(name,tempMembers,factory=factory010,bonus=1,factoryType="AutoCapture")
              name = nextDirection +str(xi)+","+str(yi)+"_"+str(nPlayer)+"-State"+str(nPC)+"-B4"         
              self.addContinent(name,tempMembers,factory=factory000,bonus=-1,factoryType="AutoCapture")
  
              tempMembers = list(PCHMembers)       
              tempMembers.append(b2)
              name =nextDirection + str(xi)+","+str(yi)+"_"+str(nPlayer)+"-State"+str(nPC)+"-B5"         
              self.addContinent(name,tempMembers,factory=factory100,bonus=1,factoryType="AutoCapture")
              name =nextDirection + str(xi)+","+str(yi)+"_"+str(nPlayer)+"-State"+str(nPC)+"-B6"         
              self.addContinent(name,tempMembers,factory=factory000,bonus=-1,factoryType="AutoCapture")
           
              # if 2 bits are set
              # remove factory001, 010, 100
              # add factory 011, 101, 110
              tempMembers = list(PCHMembers)       
              tempMembers.append(b0)
              tempMembers.append(b1)
              name = nextDirection +str(xi)+","+str(yi)+"_"+str(nPlayer)+"-State"+str(nPC)+"-C1"         
              self.addContinent(name,tempMembers,factory=factory011,bonus=1,factoryType="AutoCapture")
              name = nextDirection +str(xi)+","+str(yi)+"_"+str(nPlayer)+"-State"+str(nPC)+"-C2"         
              self.addContinent(name,tempMembers,factory=factory001,bonus=-1,factoryType="AutoCapture")
              name = nextDirection +str(xi)+","+str(yi)+"_"+str(nPlayer)+"-State"+str(nPC)+"-C3"         
              self.addContinent(name,tempMembers,factory=factory010,bonus=-1,factoryType="AutoCapture")
  
              tempMembers = list(PCHMembers)       
              tempMembers.append(b1)
              tempMembers.append(b2)
              name = nextDirection +str(xi)+","+str(yi)+"_"+str(nPlayer)+"-State"+str(nPC)+"-C4"         
              self.addContinent(name,tempMembers,factory=factory110,bonus=1,factoryType="AutoCapture")
              name =nextDirection + str(xi)+","+str(yi)+"_"+str(nPlayer)+"-State"+str(nPC)+"-C5"         
              self.addContinent(name,tempMembers,factory=factory010,bonus=-1,factoryType="AutoCapture")
              name = nextDirection +str(xi)+","+str(yi)+"_"+str(nPlayer)+"-State"+str(nPC)+"-C6"         
              self.addContinent(name,tempMembers,factory=factory100,bonus=-1,factoryType="AutoCapture")
  
              tempMembers = list(PCHMembers)       
              tempMembers.append(b0)
              tempMembers.append(b2)
              name = nextDirection +str(xi)+","+str(yi)+"_"+str(nPlayer)+"-State"+str(nPC)+"-C7"         
              self.addContinent(name,tempMembers,factory=factory101,bonus=1,factoryType="AutoCapture")
              name = nextDirection +str(xi)+","+str(yi)+"_"+str(nPlayer)+"-State"+str(nPC)+"-C8"         
              self.addContinent(name,tempMembers,factory=factory001,bonus=-1,factoryType="AutoCapture")
              name = nextDirection +str(xi)+","+str(yi)+"_"+str(nPlayer)+"-State"+str(nPC)+"-C9"         
              self.addContinent(name,tempMembers,factory=factory100,bonus=-1,factoryType="AutoCapture")
  
   
              # if 3 bits are set
              # removefactory 011, 101, 110
              # add factory 111
              tempMembers = list(PCHMembers)       
              tempMembers.append(b0)
              tempMembers.append(b1)
              tempMembers.append(b2)
              name = nextDirection +str(xi)+","+str(yi)+"_"+str(nPlayer)+"-State"+str(nPC)+"-D1"         
              self.addContinent(name,tempMembers,factory=factory111,bonus=1,factoryType="AutoCapture")
              name = nextDirection +str(xi)+","+str(yi)+"_"+str(nPlayer)+"-State"+str(nPC)+"-D2"         
              self.addContinent(name,tempMembers,factory=factory001,bonus=-1,factoryType="AutoCapture")
              name =nextDirection + str(xi)+","+str(yi)+"_"+str(nPlayer)+"-State"+str(nPC)+"-D3"         
              self.addContinent(name,tempMembers,factory=factory010,bonus=-1,factoryType="AutoCapture")
              name = nextDirection +str(xi)+","+str(yi)+"_"+str(nPlayer)+"-State"+str(nPC)+"-D4"         
              self.addContinent(name,tempMembers,factory=factory100,bonus=-1,factoryType="AutoCapture")

 
        
          
    
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
       
      
      
      
      
        
        
