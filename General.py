from xml.dom.minidom import parse, Document, parseString
import random
import re
from math import floor, ceil, sqrt, sin, cos, fabs
import string
from sys import exc_info, setrecursionlimit, stdout
import traceback
from copy import deepcopy
import itertools
import exceptions

#import MazeWGMap
#import KnightWGMap

# TODO:       SHould wrap all getAttribute("tid" with an int(), so that we are always teating tid as int.

'''
:module: WGLib
:platform: Unix, Windows
:synopsis: The WGLib module gives access to the WGMap base class as well as more specialized children.  These classes are used to create, load, modify & save War Gear Maps (XML & PNG files).

.. moduleauthor:: Ozyman



@todo: Need to finish wrapping up method groups that do the same thing 
with different arguments. i.e. add a single method that uses try/except 
to figure out what specific method to call.
           also make the sub methods private.  see deleteTerritory().
           (or maybe the by ID one should be public?)

@todo make documentation look better
      http://packages.python.org/an_example_pypi_project/sphinx.html

'''
# Take a string s, and return as an int or float as appropriate
def num (s):
    try:
        return int(s)
    except exceptions.ValueError:
        return float(s)
      
class WGMap(object):
  """
  load, save, store and access a WarGear map
  The map state is represented internally by an XML DOM.

  """

  def __init__(self):
    """Constructor"""
    self.DOM = None
    self.debug = False

    
  def saveMapToFile(self, filePath, printStats=True):
    """
    Save the XML.

    Args:
      filePath (str): 

    >>> saveMapToFile(//SERVER/path/to/map/MapName.xml)    
    """
    if(printStats):
      self.printStatistics()
    #print "writing to: ", filePath
    self.filePath = filePath
    fileHandle = open(filePath,'w')
    #print "DOM: ",self.DOM.toxml()
    fileHandle.write(self.DOM.toxml())
    fileHandle.close()
    
  def writeXML(self):
    """
    Write XML to output
    """
    stdout.write(self.DOM.toxml())

  def loadMapFromXMLString(self, xml):
    """
    Hope this works!
    @todo can I combine this with loadMapFromFile & ducktype/autodetect?
    """
    self.filepath = None
    self.DOM = parseString(xml)

  def loadMapFromFile(self, filePath):
    """
    Loads the state of a map from an XML document.

    Args:
    filePath (str):

    """
    self.filePath = filePath
    fileHandle = open(filePath)
    self.DOM = parse(fileHandle)    

  def printDOM(self):
    """Print the DOM to stdout in XML format."""
    print self.DOM.toprettyxml()

  def createBoard(self, boardName, versionMaj="1", versionMin="0", minPlayers="2",
                  maxPlayers="16", 
                  availablePlayers="2,3,4,5,7,8,9,10,12,13,14,15,16", 
                  gameplayType="Turn Based"):
    '''
    Add a <board> element to the DOM.

    note: all arguments are strings
    note: some problems?  Better to create a new board on wargear.net, export the XML, and use
    loadMapFromFile()
    
    '''
    #self.DOM = Document()
    newWGXMLElement = self.DOM.createElement("WarGearXML")
    self.DOM.appendChild(newWGXMLElement)

    newBoardElement = self.DOM.createElement("board")
    newBoardElement.setAttribute("boardname",str(boardName))
    newBoardElement.setAttribute("version_major",str(versionMaj))
    newBoardElement.setAttribute("version_minor",str(versionMin))
    newBoardElement.setAttribute("min_players",str(minPlayers))
    newBoardElement.setAttribute("max_players",str(maxPlayers))
    newBoardElement.setAttribute("available_players",str(availablePlayers))
    newBoardElement.setAttribute("gameplay_type",str(gameplayType))

    newWGXMLElement.appendChild(newBoardElement)
  
  def isThereADeadEnd(self):
    '''
    check every territory to see if any have just 1 border.  Return true if so, otherwise false.
    '''
    
    borderCounts = self.getBorderCounts()
    # find the max
    
    for BName,BCount in borderCounts.iteritems():
      if BCount == 1:
        return True

    return False
  

      
  
  # todo, check getNeighbors() to take into account one-way borders
  def checkOneTerritoryCanReachAll(self, territoryID=None):
    '''
    Test if the specified territory can reach all other territories.
    
    Always returns true for 0 & 1 territories
    
    Args:
    territoryID (int): The territory ID for testing.  
    If no territory ID is given, the first territory in the DOM is used.

    '''
    # initial setup 
    #self.printDOM()
    
    if len(self.DOM.getElementsByTagName("territory")) == 0:
        return True
    if len(self.DOM.getElementsByTagName("territory")) == 1:
        return True
      
    
    if territoryID == None:
      territoryID = self.DOM.getElementsByTagName("territory")[0].getAttribute("tid")
    #print "territoryID",territoryID
    territoriesReached = set(territoryID)
    #print "territoriesReached",territoriesReached
    territoriesToCheck = set() #territories that have neighbors we may not have looked at yet

    # account for neighbors of first territory
    territoriesToCheck |= self.getNeighborIDsFromID(territoryID)

    #print "territoriesToCheck", territoriesToCheck
    while len(territoriesToCheck) > 0:
      # get a territory to check/reach
      territoryID = territoriesToCheck.pop()
      #print "looking at",territoryID
      # find all of it's neighbors
      neighbors = self.getNeighborIDsFromID(territoryID)
      #print "neighbors", neighbors
      # add any newly available territories
      territoriesToCheck |= (neighbors - territoriesReached)
      #print "territoriesToCheck", territoriesToCheck
      
      territoriesReached.add(territoryID)
   
    # get a set of all the territory ID
    allTerritories = set()
    for territory in  self.DOM.getElementsByTagName("territory"):
      allTerritories.add(int(territory.getAttribute("tid")))

    print "allTerritories",allTerritories
    print "territoriesReached",territoriesReached
    territoriesMissed = allTerritories - territoriesReached
    print "territoriesMissed",territoriesMissed
    if len(territoriesMissed) == 0:
      return True
    else:
      print "all territories:", self.getTerritoryNameFromIDs(allTerritories)
      print "territories reached:",self.getTerritoryNameFromIDs(territoriesReached)
      print "territories missed: ", self.getTerritoryNameFromIDs(allTerritories - territoriesReached)
      
      return False
  
  
  def setAllSoleContinentTerritoriesToNeutral(self,neutralBase=2,neutralMultiplier=2):
    '''
    Find all continents that only have one member, and set that member to neutral
    Unit count is equal to the neutralMultiplier * total continent bonus + neutralBase
    '''
    # <territory id="1360487" tid="229" boardid="1213" name="T20" xpos="553" ypos="543" max_units="0" 
    # scenario_type="Neutral" scenario_seat="0" scenario_units="5" /> 
    # <rules ... initial_setup="Scenario based" 
    #self.printDOM()
    territoryIDAndValue = {}
    for continent in self.DOM.getElementsByTagName("continent"):
      #print continent.getAttribute("members")
      if (len(continent.getAttribute("members").split(',')) == 1):
        territoryIDAndValue[continent.getAttribute("members")] = territoryIDAndValue.get(continent.getAttribute("members"),0)+int(continent.getAttribute("bonus"))
        #print "adding",continent.getAttribute("members")
    
    for tid in territoryIDAndValue.keys():
      territoryElement = self.getTerritoryElement(tid)
      territoryElement.setAttribute("scenario_type","Neutral")
      territoryElement.setAttribute("scenario_units",str(int(neutralBase+territoryIDAndValue[tid]*neutralMultiplier)))
    
    
    self.DOM.getElementsByTagName("rules")[0].setAttribute("initial_setup","Scenario based")
  
  def addViewBordersToNeighbors(self, nDistance=2):
    '''
      An nDistance of 1 does nothing...
    '''
    
    #fileHandle = open(self.filePath)    
    #originalDOM = parse(fileHandle)
    setrecursionlimit(15000)
    originalDOM = deepcopy(self.DOM)    
    newDOM = self.DOM
    
    for t in self.DOM.getElementsByTagName("territory"):
      tid = t.getAttribute("tid") 
      #print "working on tid:",tid
      
      self.DOM = originalDOM
      twoDist = self.getAllTerritoriesWithinNBorders(tid,nDistance) - self.getAllTerritoriesWithinNBorders(tid,1)
      
      self.DOM = newDOM      
      self.addBordersToSet(tid, twoDist,'Two-way', "View Only")
           
    self.DOM = newDOM  



  def addChainContinents(self,baseIDSet,value=1): #,length=2):
    '''
    # this function adds continent chains.  Just works for length=2 now
    '''
    chains = set()
    for base in baseIDSet:
      neighbors = self.getNeighborIDsFromID(base)      
      for neighbor in neighbors:
        chain = frozenset([neighbor, base])        
      chains.add(chain)      
        
        
        
    for chain in chains:
      name = "chain"
      members = set()
      for link in chain:
        name += "." + self.getTerritoryNameFromID(link)
        members.add(link)
      self.addContinent(name,members,bonus=value)
    

# This is the function that makes all the continents. 
# You give it a bunch of values (arguments), and they tell it how to add the factories.
  def addFixedBonusContinents(self,baseIDSet,memberIDSet,fixedBonus,factoryType,CNPrefix,neighborDistance,factoryTarget, borderTypesAllowed = ["Default","Attack Only"]):
   
      
    # print the values that were passed in (just for debug purposes i.e. to check how things are going so far)
    print "addFixedBonusContinents called:"
    print "\t BaseIDSet:",baseIDSet
    print "\t MemberIDSet:",memberIDSet
    print "\t FixedBonus:",fixedBonus
    print "\t FactoryType:",factoryType
    print "\t CNPrefix:",CNPrefix
    print "\t NeighborDistance:",neighborDistance
    print "\t FactoryTarget:",factoryTarget
   


    for baseID in baseIDSet:

      # a negative neighbor distance means use all neighbors, otherwise find the neighbors in range
      if (neighborDistance >= 0):
        neighbors = self.getAllTerritoriesWithinNBorders(baseID,neighborDistance, borderTypesAllowed = borderTypesAllowed)
        
      else:
        neighbors = self.getTerritoryIDsFromNameRegex(".*")
        
          
      possibleMembers = []
      for n in neighbors:
        if memberIDSet == None or n in memberIDSet:
          possibleMembers.append(n)

      # numberOfNeighbors will 1st be 1, then 2, up to the total # of
      # possibleMembers
      for numberOfNeighbors in range(len(possibleMembers)):

        for members in itertools.combinations(possibleMembers, numberOfNeighbors):
          # get value based on # of members
          value = 1
          if (members.size() % 2 == 0):
            value *= -1
          
          if (CNPrefix != None):
            name = CNPrefix
          else:   
            name = "FIXEDBONUS-" 
            
          name += str(baseID) + " "
          for m in members:
            name = str(m) + "."
           
            # def addContinent(self, continentName, memberIDs, bonus=1,factory=-1,factoryType="Standard"):
            # '''
            # factoryType = ["Standard","AutoCapture","Universal"]           
            self.addContinent(name,members.append(baseID),value*fixedBonus,factoryTarget,factoryType)
    
  '''
    for tid in targetIDList:

      neighbors = self.getAllTerritoriesWithinNBorders(tid,neighborDistance, borderTypesAllowed = borderTypesAllowed)
      
      possibleMembers = []
      for n in neighbors:
        if neighborIDs == None or n in neighborIDs:
          possibleMembers.append(n)
      fid = factory
      if factory == "base" and factoryType != "":
        fid = tid
      if fid == None:
        fid = -1
      continentName = "%s%s" % (continentPrefix,str(self.getTerritoryNameFromID(tid)))
      tbonus = num(bonus)
      if isinstance(tbonus, float):
        tbonus = floor(bonus * len(possibleMembers))
      else:
        tbonus = bonus 
        
      #addContinent(self, continentName, memberIDs, bonus=1,factory=-1,factoryType="Standard"):
      self.addContinent(continentName, possibleMembers, tbonus, fid, factoryType)
    
    '''
 
  def addEliminationCombinationContinents(self,IDSet,minRequired, continentSuffix=""):
    
    for _IDSet in itertools.combinations(IDSet,minRequired):
      cs = continentSuffix
      for anID in _IDSet:
        cs += "_" + anID
      self.addEliminationContinents(_IDSet,cs)
    
 
  def addEliminationContinents(self,IDSet, continentSuffix=""):
    
    for territory in self.DOM.getElementsByTagName("territory"):
      continentName = territory.getAttribute("name") + continentSuffix
      targetID = territory.getAttribute('tid')
      self.addContinent(continentName,IDSet,1,targetID,"AutoCapture")
      
    '''
     def addContinent(self, continentName, memberIDs, bonus=1,factory=-1,factoryType="Standard"):

    factoryType = ["Standard","AutoCapture","Universal"]
    '''
      
  
  def addBuilderPattern(self, SupplyID, PlayerID, ReadyID, B1ID, B2ID, UID, N, M, factoryNamePrefix):
    #fortify border supply to B1
    #attack border ready to B1
    
    # All factories AutoCapture
    #-1 factory B1 to Ready
    #-1 factory B2 to ready
    #+1 factory PN to Ready
    #+1 factory B1 to B2
    #-N factory B1 to B1
    #-1 factory B2 to B2        
    #add +M factory (B1,B2) to U
    
    self.addBorder(SupplyID,B1ID,direction="One-way",borderType="Fortify Only")
    self.addBorder(ReadyID, B1ID,direction="One-way",borderType="Attack Only")

    
    self.addContinent(factoryNamePrefix + "B1->Ready",str(B1ID),bonus="-1",factory=str(ReadyID),factoryType="AutoCapture")
    #self.addContinent(factoryNamePrefix + "B2->Ready",str(B2ID),bonus="-1",factory=str(ReadyID),factoryType="AutoCapture")
    self.addContinent(factoryNamePrefix + "P->Ready",str(PlayerID),bonus="1",factory=str(ReadyID),factoryType="AutoCapture")
    self.addContinent(factoryNamePrefix + "B1->B2",str(B1ID),bonus="1",factory=str(B2ID),factoryType="AutoCapture")
    
    self.addContinent(factoryNamePrefix + "B1-Cost",str(B1ID),bonus=str(-1*fabs(N)),factory=str(B1ID),factoryType="AutoCapture")
    self.addContinent(factoryNamePrefix + "B2-Drain",str(B2ID),bonus="-1",factory=str(B2ID),factoryType="AutoCapture")
    self.addContinent(factoryNamePrefix + "NewUnits",str(B1ID)+","+str(B2ID),bonus=str(M),factory=str(UID),factoryType="AutoCapture")
    
    

  # todo: would be better to have this take a list of collectionBonus, so that it worked
  # for a more general case, instead of only for pair-wise collections.
  def addCollectorContinents(self, IDSet, individualBonus = "1", pairBonus="1",factory=None,nameSuffix=None, additionalMembers=None,factoryType="Standard" ):
    
    individualBonus = str(individualBonus)
    pairBonus = str(pairBonus)
    
    IDSet2 = set(IDSet)
    for a in IDSet:
      aint = int(a)
      print "adding",aint,IDSet2
      IDSet2.remove(a)
      aName = self.getTerritoryNameFromIDs(aint)
      if nameSuffix != None:
        aName = aName + nameSuffix
      members = list()
      members.append(aint)
      if additionalMembers:
        members.extend(additionalMembers)
      if int(individualBonus)  !=  0:
        if factory != None:
          self.addContinent(aName,members,individualBonus,factory=factory,factoryType=factoryType)
        else:
          self.addContinent(aName,members,individualBonus,factoryType=factoryType)
      for b in IDSet2:
        b = int(b)
        
        bName = self.getTerritoryNameFromIDs(b)
        abName = aName+ "_" + bName
        if nameSuffix != None:
          abName = abName + nameSuffix
        if int(pairBonus) != 0:        
          if factory != None:
            self.addContinent(abName,members+[b],pairBonus,factory=factory)          
          else:          
            self.addContinent(abName,members+[b],pairBonus)
        
      
  def swapBorderDirection(self, borderElement):
    '''
    Functionally the same border, but from/to is swapped.
    Does nothing if border is not two-way
    '''
    direction = borderElement.getAttribute("direction")
    if direction != "Two-way":
      return
 
    fromid = borderElement.getAttribute("fromid")
    toid = borderElement.getAttribute("toid")
    ftattackmod = borderElement.getAttribute("ftattackmod")
    ftdefendmod = borderElement.getAttribute("ftdefendmod")
    tfattackmod = borderElement.getAttribute("tfattackmod")
    tfdefendmod = borderElement.getAttribute("tfdefendmod")
    
    borderElement.setAttribute("ftattackmod",tfattackmod)
    borderElement.setAttribute("ftdefendmod",tfdefendmod)
    borderElement.setAttribute("tfattackmod",ftattackmod)
    borderElement.setAttribute("tfdefendmod",ftdefendmod)
    
    borderElement.setAttribute("fromid",toid)
    borderElement.setAttribute("toid",fromid)

    
  def splitBorders(self, S1List, S2List):
    '''
     Borders are defined in the XML like this:
    <border direction="Two-way" fromid="39" ftattackmod="0" ftdefendmod="0" tfattackmod="0" tfdefendmod="0" toid="42" type="Default"/>
   '''
    print  "splitBorders called"
    print "S1List",S1List
    print "S2List", S2List
    print "kwargs:"

    bordersToMod = []
    
    for border in self.DOM.getElementsByTagName("border"):
      if (border.getAttribute("direction") != "Two-way"):
        continue
      
      fromid = int(border.getAttribute("fromid"))
      toid = int(border.getAttribute("toid"))

      if ((fromid in S1List) and (toid in S2List)):
        bordersToMod.append(border)
      else:   
        if ((fromid in S2List) and (toid in S1List)):        
          bordersToMod.append(border)

    for border in bordersToMod:
      fromid = border.getAttribute("fromid")
      toid = border.getAttribute("toid")
      border.setAttribute("direction","One-way")
      tfa = border.getAttribute("tfattackmod")
      tfd = border.getAttribute("tfdefendmod")
      btype = border.getAttribute("type")
      self.addBorder(toid, fromid, direction="One-way", borderType = btype, 
                        ftattackmod = tfa, ftdefendmod = tfd) 
                      
    
  def modifyBorders(self, fromList, toList, **kwargs):
    '''
    Modifies a set of borders that fit some criteria.
    
    Borders are defined in the XML like this:
    <border direction="Two-way" fromid="39" ftattackmod="0" ftdefendmod="0" tfattackmod="0" tfdefendmod="0" toid="42" type="Default"/>
    
    The set of borders to modify is defined by their Attack/From and Defend/To territories
    These are given as a list of territory IDs.
    
    The properties that can be modified are 
    attack modifier
    defense modifier
    type
    direction
  
    Any properties that are not passed are left unchanged.
    
    design notes:
      Instead of dealing with from/to in both directions at the same time, can I simplify things for users?

      For example, let's say some wants all territories with a "[M]" in their name to get a +1 defense when attacked.
      
      In the advanced version, you have to do things twice, once with the "[M]" as the from territory and give a tfdefense of 7 and once with the "[M]" as the to territory and give a ftdefense of 7.'
      
      Instead I can have a simpler version. 
      
      Attacking (to) territory set
      Defending (to) territory set
      
      attack modifier
      defense modifier
      border type
      border direction 
      
       Where you define "[M]" as the 'defending territory', and then say defender mod of 1, attacker mod is None.  None means don't change the value of that mod.
      
      When we search for borders, we have to switch around the modifiers if the to/from for the borders is backwards from suggested.
      
      If they ask for one-way and the border is setup backwards, we need to swap the from & to set.
      
      Possible bugs, tricky cases:
      This only works on existing borders, it will not create borders (different form/button for that eventually)
      
      If you have a two-way border, and you change it to 1-way, and then change it 1-way the oppposite way, you do not get two 1-way borders.  This can be a bit tricky if you want (for example) a fortify border in one direction and a view border in the other direction.    What you need to do is when you create the borders originally, do not create them as 2-way borders, but instead create two 1-way borders, and then it will work correctly.
    '''
    direction = kwargs.get('borderDirection',None)
    borderType = kwargs.get('borderType', None)
    attackMod = kwargs.get('attackModifier', None)
    defenseMod = kwargs.get('defenseModifier', None)
    
    print  "modifyBorders called"
    print "fromList",fromList
    print "toList", toList
    print "kwargs:"
    for key, value in kwargs.iteritems():
      print key,value

    
    
    if ((direction == None) and
        (borderType == None) and
        (attackMod == None) and
        (defenseMod == None)):
      print "warning, modifyBorders called with no requested modifications"
      return
    
    bordersToMod = []
    
    def setAttributes(border, attackMod, defenseMod, direction, borderType):
      if (attackMod != None):
        border.setAttribute("ftattackmod",attackMod)
      if (defenseMod != None):
        border.setAttribute("ftdefendmod",defenseMod)
      if (direction != None):        
        border.setAttribute("direction",direction)
      if (borderType != None):
        border.setAttribute("type",borderType)
    
    for border in self.DOM.getElementsByTagName("border"):
      fromid = int(border.getAttribute("fromid"))
      toid = int(border.getAttribute("toid"))

      if ((fromid in fromList) and (toid in toList)):
        bordersToMod.append(border)
        
      else:
        if ((fromid in toList) and (toid in fromList)):
          if (border.getAttribute("direction") == "Two-way"):
            self.swapBorderDirection(border)
            bordersToMod.append(border)


    for border in bordersToMod:
      setAttributes(border, attackMod, defenseMod, direction, borderType)
      # check to see if we need to mode the other direction.
      fromid = int(border.getAttribute("fromid"))
      toid = int(border.getAttribute("toid"))
      if ((fromid in toList) and (toid in fromList)):
        if (border.getAttribute("direction") == "Two-way"):        
          self.swapBorderDirection(border)
          setAttributes(border, attackMod, defenseMod, direction, borderType)
    
            
    
  def continentsFromNeighbors(self, targetIDList, bonus, **kwargs):
    '''
        targetIDList : a list of territory ID to assign continents from.  One continent will be created for every item in targetIDList
        bonus : either an integer, or a float.  
                If it is an integer, then bonus is the bonus for every new continent.  
                If it is a float, then it is multiplied by the # of territories in the new continent to find the bonus.                                  
                                  the result is rounded down  
        
        kwargs:
          neighborDistance : default=1, how far away to find neighbors for continent membership 
          factory : default=None.
                If None - no factory
                If integer - use as tid for factory
                If "base" - use targetID for factory
                
          continentPrefix 
          neigbhborIDs : If None (default) this is not used.
          factoryType
  
    
    
    '''

    neighborDistance = kwargs.get('neighborDistance',1)
    factory = kwargs.get('factory',None)
    factoryType = kwargs.get('factoryType',"Standard")
    continentPrefix = kwargs.get('continentPrefix',"")
    neighborIDs = kwargs.get('neigbhorIDs',None)
    borderTypesAllowed = kwargs.get('borderTypesAllowed',["Default","Attack Only"])
        
    print "continentsFromNeighber called:"
    print "\ttargetIDList:",targetIDList
    print "\tbonus:",bonus
    print "\tneighborDistance:",neighborDistance
    print "\tfactory:",factory
    print "\tfactoryType:",factoryType
    print "\tcontinentPrefix:",continentPrefix
    print "\tneighborIDs:",neighborIDs
    print "borderTypesAllowed:",borderTypesAllowed
    

    for tid in targetIDList:

      neighbors = self.getAllTerritoriesWithinNBorders(tid,neighborDistance, borderTypesAllowed = borderTypesAllowed)
          
      members = []
      for n in neighbors:
        if neighborIDs == None or n in neighborIDs:
          members.append(n)
      fid = factory
      if factory == "base" and factoryType != "":
        fid = tid
      if fid == None:
        fid = -1
      continentName = "%s%s" % (continentPrefix,str(self.getTerritoryNameFromID(tid)))
      tbonus = num(bonus)
      if isinstance(tbonus, float):
        tbonus = floor(bonus * len(members))
      else:
        tbonus = bonus 
        
      #addContinent(self, continentName, memberIDs, bonus=1,factory=-1,factoryType="Standard"):
      self.addContinent(continentName, members, tbonus, fid, factoryType)
    
  
  def hordify(self, bonus="1", continentNameSuffix="", 
              baseRegex=".*", neighborRegex=".*",verificationMode=False):
    '''
    Add continents in a "hordes" style.  For all territories that match baseRegex, a continent is created
    whose members are the original territory and all of the neighbors who match neighborRegex.  

    Args:
      bonus (int): The number of units a player will get for controlling this continent
      continentNameSuffix (str): This is added to the base territory name to get the continent name
      baseRegex (str): Only territorires that match this regex will have continents added.
      neighborRegex (str): Only neighbors that match this regex will be members of the new continents.
      verificationMode (bool): Verifies continent was added succesfully (for testing).
    '''
    
    # visit every territory
    territoryElementList = self.DOM.getElementsByTagName("territory")
    for territoryElement in territoryElementList:
      territoryName = territoryElement.getAttribute("name")
      hordesTerritoryName = territoryName + continentNameSuffix
      #print "comparing: ",baseRegex,territoryName
      if (None == re.search(baseRegex,territoryName)):
        #print "no match"
        continue
      # collect the neighbors & self
      neighborElementSet = self.getNeighbors(territoryElement, "either",neighborRegex)
      neighborElementSet.add(territoryElement)
      if (verificationMode):
        continentElement = self.getContinentFromMembers(neighborElementSet)
        if (None != continentElement):
          print "Hordify Continent:",hordesTerritoryName,"found:",continentElement
        else:
          print "Hordify Continent:",hordesTerritoryName,"MISSING!"
      else:  
        # add the continent
        self.addContinentFromElements(hordesTerritoryName, neighborElementSet, bonus)
      

  # what is the smallest continent that this territory is a member of.
  def getMinContinentSize(self, territoryName):
    """
    Find the smallest continent that territoryName is a member of.

    Args:
      territoryName (str): The territory name to look for.
    """
    minCS = 999999  #ugly hack
    tid = self.getTerritoryIDFromName(territoryName)
    for continent in self.DOM.getElementsByTagName("continent"):
      if tid in [int(i) for i in continent.getAttribute("members").split(',')]:
        size = len(continent.getAttribute("members").split(','))
        if (size < minCS):
          minCS = size
    return minCS

  '''
  def getMinContinentSize(self):
    minCS = len(self.DOM.getElementsByTagName("continent").getAttribute("members").split(','))
    for continent in self.DOM.getElementsByTagName("continent"):
      size = len(continent.getAttribute("members").split(','))
      if (size < minCS):
        minCS = size
    return minCS

  def maxContinentSize(self):
    maxCS = 0
    for continent in self.DOM.getElementsByTagName("continent"):
      size = len(continent.getAttribute("members").split(','))
      if (size > maxCS):
        maxCS = size
    return maxCS
  '''

  def getTerritoryIDsFromNameRegex(self, territoryNameRegex):
    '''
    Given a territory name regex return a list of all of the IDs that match
    
    Args:
      territoryNameRegex (str): The name to look for.    
    '''
    returnSet = set()
    for territoryElement in self.DOM.getElementsByTagName("territory"):
      territoryName = territoryElement.getAttribute("name")
      print "comparing",territoryNameRegex,territoryName
      if (None != re.search(territoryNameRegex,territoryName)):
        returnSet.add(int(territoryElement.getAttribute("tid")))
    #print "found no match for", territoryName
    return returnSet
        

  def getTerritoryIDsFromNames(self, territoryNames):
    '''
    given a collection of territoryNames, return a collection of corresponding IDs, with None in place for missed names
    '''
    territoryIds = []
    for name in territoryNames:
      tid = self.getTerritoryIDFromName(name)
      if (tid != False):
        territoryIds.append(tid)
      else:
        territoryIds.append(None)
      
    return territoryIds
  
  def getTerritoryIDFromName(self, territoryName):
    '''
    Given a territory name find the ID for that territory (or False if not found)
    @TODO: should this return None instead of false?
    Args:
      territoryName (str): The name to look for.

    '''
    for territory in self.DOM.getElementsByTagName("territory"):      
      if (territory.getAttribute("name") == territoryName):
        #if (self.debug):
          #print "found a match",territory.getAttribute("name"),territoryName,"with id",territory.getAttribute("tid")
        return int(territory.getAttribute("tid"))
    print "found no match for", territoryName
    return None 
        
  
  def getTerritoryNameFromIDs(self, territoryIDs):
    '''
    Given a territory ID find the name for that territory (or None if not found)
    
    Args:
      territoryName (str): The name to look for.

    '''
    names = []
    try:
      for tid in territoryIDs:
        #print "searching <territory>s for",tid
        for territory in self.DOM.getElementsByTagName("territory"):
          if (int(territory.getAttribute("tid")) == int(tid)):
            names.append(territory.getAttribute("name"))
      return names

    except TypeError:
      # territoryIDs is not iterable
      return self.getTerritoryNameFromID(territoryIDs)
      
  # refactor with   getTerritoryNameFromIDs
  def getTerritoryNameFromID(self, tid):
    '''
    Given a territory ID find the name for that territory (or None if not found)
    
    Args:
      territoryName (str): The name to look for.

    '''

    #print "searching <territory>s for",tid
    for territory in self.DOM.getElementsByTagName("territory"):
      if (int(territory.getAttribute("tid")) == int(tid)):
        return territory.getAttribute("name")
    return None

  def getATerritoryWithNBorders(self,nBorders):
    
    for territory in self.DOM.getElementsByTagName("territory"):
      if (len(self.getTerritoryBordersByElement(territory)) == nBorders):
        return territory
      
    return None

  # todo: is this the same as getTerritoryIDsByDistance?
  # I think this version has been tested but other has not.
  # return set includes original territoryID
  def getAllTerritoriesWithinNBorders(self,territoryID,nBorders, direction="either", borderTypesAllowed = ["Default","Attack Only"]):
    
    #import pdb;
    tid = int(territoryID)
    #print"gatwnb called with",tid, nBorders
    borderDepth = 0
    allTerritoriesInReach = set()
    allTerritoriesInReach.add(tid)
    nBorders = int(nBorders)
    print "borderDepth:",borderDepth
    print "nBorders:",nBorders
    print "borderTypesAllowed:",borderTypesAllowed
        
    while(borderDepth < nBorders):
      allTerritoriesAddition = set()
      #print "len(allTerritoriesAddition)",len(allTerritoriesAddition)
      for tirID in allTerritoriesInReach:
        tb = self.getNeighborIDsFromID(tirID,direction, ".*", borderTypesAllowed)
        #tb = self.getBorderTerritoryIDsByTerritoryID(tirID,direction)
        #print "for",tirID,"found borders:",tb,"size:",len(tb)  
        #if len(tb) > 8:
        #    pdb.set_trace()      
        allTerritoriesAddition |= set(tb)
      allTerritoriesInReach |= allTerritoriesAddition
      borderDepth = borderDepth + 1 
   
    #print "atir",allTerritoriesInReach
    
    #allTerritoriesInReach.discard(tid)
    print "returning", allTerritoriesInReach
    print "########################    returning set of size:", len(allTerritoriesInReach)
    
    #if len(allTerritoriesInReach) > 72:
    #  pdb.set_trace()
    return allTerritoriesInReach
 
    
 
    
  def getTerritoryIDsByDistance(self, baseID, distance):

    returnSet = set()

    latestNeighbors = set()
    latestNeighbors.add(baseID)
    newNeighbors = set()

    d = 0
    while (d < distance):

      for tid in latestNeighbors:   
        newNeighbors |= self.getNeighborIDsFromID(self, tid)
 
      returnSet |= latestNeighbors
      latestNeighbors.clear()
      latestNeighbors |= newNeighbors
      newNeighbors.clear()
      d += 1

    return returnSet
  
  def getBorderElementsByTerritoryID(self, territoryID,direction="either"):
    ''' 
    Get a collection of borders for this territory.
    Args:
      Identifier: territory ID 
    '''
    borders = self.DOM.getElementsByTagName("border")
    tid = str(territoryID)
    tb = []
    for border in borders:
      if (direction == "either" or direction == "to"):
        if ((tid == border.getAttribute("fromid")) or (tid == border.getAttribute("toid") and border.getAttribute("direction") == "Two-way")):
          tb.append(border)
      if (direction == "either" or direction == "from"):          
        if ((tid == border.getAttribute("toid")) or (tid == border.getAttribute("fromid") and border.getAttribute("direction") == "Two-way")):
          tb.append(border)
    return tb
  
  def getTerritoryBordersByElement(self, territoryElement):
    ''' 
    Get a collection of borders for this territory.
    Args:
      Identifier: territoryElement
    '''
    tid = int(territoryElement.getAttribute("tid"))
    return self.getBorderElementsByTerritoryID(tid)

  def getTerritoryElement(self, identifier):
    ''' 
    Get the territory Element based upon a name or territory ID.
    Args:
      Identifier: can be a Name or territory ID 
    '''
    #print "getTerritoryElement called with identity: ",identifier
    import pdb; pdb.set_trace;
    try:
      ID = int(identifier)
      #got a territory ID
      #print "getting territory element by ID",identifier
      return self.__getTerritoryElementByID(ID)

    except:
      #print "caught error:", exc_info()[0]
      #traceback.print_exc()
      # 
      # must be a name
      #print "getting territory element by name",identifier
      return self.__getTerritoryElementByName(identifier)
 
        
  def __getTerritoryElementByName(self, name):
    #print "looking for",name
    for territory in self.DOM.getElementsByTagName("territory"):
      if territory.getAttribute("name") == name:
        return territory
    return None

  def __getTerritoryElementByID(self, tid):
    for territory in self.DOM.getElementsByTagName("territory"):
      #print "comparing",territory.getAttribute("tid"), tid
      if int(territory.getAttribute("tid")) == int(tid):
        return territory
    return None
    

  def getNeighbors(self, territoryElement, direction="either", neighborRegex=".*"):
    '''
    Get a set of the IDs of the neighbors of a territory that match the neigborRegex.
    
    Args:
      territoryElement (DOMElement): The territory to find neighbors for.
      direction (string): valid values: "to", "from", or "either"
      neigborRegex (str): neigbors that do not match this are not added to the list.
    '''
    print "finding neighbors for",territoryElement.getAttribute("name")
    territoryID = int(territoryElement.getAttribute("tid"))
    return self.getNeighborsFromID(territoryID,direction, neighborRegex)

###############################################################################
  # todo: is this the same as getNeighborIDsFromID ?
  #       other version seems more compact & more powerful.
  # this  doesn't seem to work...
  
  #def getBorderTerritoryIDsByTerritoryID(self, territoryID, direction="either"):
    
    ''' 
    Get a set of borders for this territory.
    Args:
      territoryID: territory ID
      direction: "either","to", or "from"
      
    '''
    '''
    #import pdb; pdb.set_trace();
    borders = self.DOM.getElementsByTagName("border")
    tid = str(territoryID)
    tb = set()
    for border in borders:
      if (direction == "either" or direction == "to" ):
        if (tid == border.getAttribute("fromid")):
          print tid, border.getAttribute("toid")
          tb.add(int(border.getAttribute("toid")))
        if (tid == border.getAttribute("toid") and border.getAttribute("direction") == "Two-way"):
          print tid, border.getAttribute("fromid")
          tb.add(int(border.getAttribute("fromid")))         
      if (direction == "either" or direction == "from" ):          
        if (tid == border.getAttribute("toid")):
          print tid, border.getAttribute("fromid")
          tb.add(int(border.getAttribute("fromid")))  
        if (tid == border.getAttribute("fromid") and border.getAttribute("direction") == "Two-way"):
          print tid, border.getAttribute("toid")
          tb.add(int(border.getAttribute("toid")))
    return tb
    
'''
  def getNeighborIDsFromID(self, territoryID, direction="either", neighborRegex=".*",borderTypesAllowed = ["Default","Attack Only"]):
    '''
    Given territoryID return all IDs of all other territories that share a border with it.
    
    Args:
      territoryID (int): The ID for which neighbors are found.
      direction (int): A string describing the type of neighbor to find.  Valid values::
        "to"
        "from"
        "either"
      nieghborRegex (str): Only include neighbors in the returned set if their name matches this regex.

    .. warning::
      direction is not working(?)

    '''
    #print "borderTypesAllowed:",borderTypesAllowed
    neighborIDs = set()
    for neighbor in self.getNeighborsFromID(territoryID, direction, neighborRegex,borderTypesAllowed):
      neighborIDs.add(int(neighbor.getAttribute("tid")))

    return neighborIDs

  # todo: check that direction works.  We are not looking at 'one-way' vs. 'two-way'
  def getNeighborsFromID(self, territoryID, direction="either", neighborRegex=".*",borderTypesAllowed = ["Default","Attack Only"]):
    '''
    Given territoryID return set of all IDs (as strings) of all other territories that share a border with it.
    
    Args:
      territoryID (int): The ID for which neighbors are found.
      direction (int): A string describing the type of neighbor to find.  Valid values::
        "to"
        "from"
        "either"
      nieghborRegex (str): Only include neighbors in the returned set if their name matches this regex.

    .. warning::
      direction is currently ignored

    '''
    #print "finding neighbors for", territoryID, "with direction",direction
    neighbors = set()
    tid = str(territoryID)
    #print "borderTypesAllowed",borderTypesAllowed
    for border in self.DOM.getElementsByTagName("border"):
      #print "toid:",border.getAttribute("toid"),"fromid:",border.getAttribute("fromid"), "type",border.getAttribute("type") 
      if tid == border.getAttribute("fromid"):
        #print "looking for t:",border.getAttribute("toid")
        neighbor = self.getTerritoryElement(border.getAttribute("toid"))
        #print "comparing:",neighborRegex,neighbor.getAttribute("name"),re.search(neighborRegex,neighbor.getAttribute("name"))
        if ((direction == "either" or direction == "from") and None != re.search(neighborRegex,neighbor.getAttribute("name"))
            and border.getAttribute("type") in borderTypesAllowed):
          neighbors.add(neighbor)
          #print "adding",neighbor.getAttribute("name")
          
      if tid == border.getAttribute("toid"):
        #print "looking for f:",border.getAttribute("fromid")
        neighbor = self.getTerritoryElement(border.getAttribute("fromid"))
        #print "comparing:",neighborRegex,neighbor.getAttribute("name"),re.search(neighborRegex,neighbor.getAttribute("name"))
        if ((direction == "either" or direction == "to") and None != re.search(neighborRegex,neighbor.getAttribute("name"))
            and border.getAttribute("type") in borderTypesAllowed):
          neighbors.add(neighbor)
          #print "adding",neighbor.getAttribute("name")
    #print "found neighbors",neighbors
    return neighbors




  # todo: cache this?
  
  def getBorderCount(self, territoryID):
    '''
    returns the # of borders that a territory identified by territoryID has
    '''
    borderCount = 0
    for borderElement in self.DOM.getElementsByTagName("border"):
      if int(borderElement.getAttribute("toid")) == int(territoryID):
        borderCount += 1
      if int(borderElement.getAttribute("fromid")) == int(territoryID):
        borderCount += 1

    return borderCount

     
  
  def getBorderCounts(self, direction="Two-way"):
    '''
    Returns: 
      dictionary w/ key=territoryName & value=count of their borders
    
    Args:
      direction (int): A string describing the type of neighbor to find.  Valid values::
        "to"
        "from"
        "either"

    .. warning::
      direction is currently ignored
    '''

    borderCounts = {}
    for territoryElement in self.DOM.getElementsByTagName("territory"):
      territoryName = territoryElement.getAttribute("name")
      territoryID = int(territoryElement.getAttribute("tid"))

      borderCounts[territoryName] = 0

      for borderElement in self.DOM.getElementsByTagName("border"):
        if int(borderElement.getAttribute("toid")) == territoryID:
          borderCounts[territoryName] += 1
        if int(borderElement.getAttribute("fromid")) == territoryID:
          borderCounts[territoryName] += 1

    return borderCounts


  def getMostBorderedTerritory(self, direction="Two-way"):
    '''
    Returns: 
      territoryName with the most borders & number of borders
    
    Args:
      direction (int): A string describing the type of neighbor to find.  Valid values::
        "to"
        "from"
        "either"

    .. note::
      In the case of a tie, one of the winners will be returned arbitrarily
    .. warning::
      direction is currently ignored
    '''
    # count up the borders
    borderCounts = self.getBorderCounts(direction)
    # find the max
    returnName = ""
    maxBorders = 0
    for BName,BCount in borderCounts.iteritems():
      if BCount > maxBorders:
        returnName = BName
        maxBorders = BCount

    return returnName, maxBorders

  def getLargestBonusContinent(self):
    '''
    Returns: 
      continentName with the largest bonus & that bonus
    
    .. note::
      In the case of a tie, one of the winners will be returned arbitrarily
    '''
    
    maxBonus = int(self.DOM.getElementsByTagName("continent")[0].getAttribute("bonus"))
    returnName = self.DOM.getElementsByTagName("continent")[0].getAttribute("name")
    for continentElement in self.DOM.getElementsByTagName("continent"):
      bonus = int(continentElement.getAttribute("bonus"))
      if (bonus > maxBonus):
        maxBonus = bonus
        returnName = continentElement.getAttribute("name")

    return returnName,maxBonus

  def getContinentMembersFromName(self,continentName):
    for continentElement in self.DOM.getElementsByTagName("continent"):
      if continentElement.getAttribute("name") == continentName:
        return continentElement.getAttribute("members")
       
    return None

  def getContinentFromMembers(self,neighborElementList):
    '''
    Args:
      neigbhorElementList (list): A list of neighbor elements to compare against.
    
    Returns:
      The first continentElement that has the same neighbors as the neighborElementList (or None)
    '''
    territoryIDSet = set(neighborElementList)

    for continentElement in self.DOM.getElementsByTagName("continent"):
      if set(continentElement.getAttribute("members")) == territoryIDSet:
        return continentElement
    return None

  def getContinentsWithTerritory(self, territoryID):
    '''
    Args:
      territoryID (int): A territory ID to look for.
    
    Returns:
      A set of all continentElements that have territoryID as a member. 
    '''
    territoryID = int(territoryID)
    continentSet = set()
    for continent in self.DOM.getElementsByTagName("continent"):
      if territoryID in map(int, continent.getAttribute("members").split(',')):
        continentSet.add(continent)

    return continentSet

  def setBoardName(self, boardName):
    '''
    Sets the "boardname" attribute of the "board" element.
    '''
    self.DOM.getElementsByTagName("board")[0].setAttribute("boardname",str(boardName))

  def setNumAttacks(self, numAttacks):
    '''
    Sets the 'num_attacks' attribute of the 'rules' element.  numAttacks should be a number or 'Unlimited'
    '''
    self.DOM.getElementsByTagName("rules")[0].setAttribute("num_attacks",str(numAttacks))
    
  def setNumFortifies(self, numFortifies):
    '''
    Sets the 'num_fortifies' attribute of the 'rules' element.  numFortifies should be a number or 'Unlimited'
    '''
    self.DOM.getElementsByTagName("rules")[0].setAttribute("num_fortifies",str(numFortifies))
    

  def setFortifyType(self, fortifyType):
    '''
    Sets the 'num_fortifies' attribute of the 'rules' element.  fortifyType should be "connected","bordered", or ?? 
    '''
    #  fortify_type="connected"
    # 
    self.DOM.getElementsByTagName("rules")[0].setAttribute("fortify_type",fortifyType)
    

  def setEliminationBonus(self, bonus):
    '''
    Sets the 'elimination_bonus' attribute of the 'rules' element.  bonus should be a number
    '''
    self.DOM.getElementsByTagName("rules")[0].setAttribute("elimination_bonus",str(int(bonus)))
    
  def setMaxCards(self, maxCards):
    '''
    Sets the 'card_max_accrual' attribute of the 'rules' element.  maxCards should be a number or 'Unlimited'
    '''
    self.DOM.getElementsByTagName("rules")[0].setAttribute("card_max_accrual",str(maxCards))

  def addBordersFromSetToSet(self, fromIDs, toIDs, direction='Two-way', 
                borderType = "Default", ftattackmod = "0",
                ftdefendmod="0", tfattackmod="0",
                tfdefendmod="0", ftattackmin="0",
                ftdefendmin="0", tfattackmin="0", 
               tfdefendmin="0"):
    
    for fromID in fromIDs:
      self.addBordersToSet(fromID, toIDs, direction, 
                borderType, ftattackmod,
                ftdefendmod, tfattackmod,
                tfdefendmod, ftattackmin,
                ftdefendmin, tfattackmin, 
               tfdefendmin)

  def addBordersToSet(self, fromID, toIDs, direction='Two-way', 
                borderType = "Default", ftattackmod = "0",
                ftdefendmod="0", tfattackmod="0",
                tfdefendmod="0", ftattackmin="0",
                ftdefendmin="0", tfattackmin="0", 
               tfdefendmin="0"):
    
    # had to make this call WGMap, because when called via a subclass with addBorder method, it was trying to call that one, even though the
    # number of arguments was wrong.
    for toID in toIDs:
      WGMap.addBorder(self,fromID,toID,direction, borderType, ftattackmod,
                ftdefendmod, tfattackmod, tfdefendmod, ftattackmin,
                ftdefendmin, tfattackmin,tfdefendmin) 
         
     
  def addBordersViaRegex(self,fromRegex,toRegex, direction = "Two-way", 
                borderType = "Default", ftattackmod = "0",
                ftdefendmod="0", tfattackmod="0",
                tfdefendmod="0", ftattackmin="0",
                ftdefendmin="0", tfattackmin="0", 
                tfdefendmin="0"):
    '''
    Adds borders between every country that matches the fromRegex to every country that matches the toRegex.
    '''
    
    for fromElement in self.DOM.getElementsByTagName("territory"):
      print "comparing: ",fromRegex,fromElement.getAttribute("name")
      if (None != re.search(fromRegex,fromElement.getAttribute("name"))):
        for toElement in self.DOM.getElementsByTagName("territory"):
          if (None != re.search(toRegex,toElement.getAttribute("name"))):
            print"found a match from:", fromElement.getAttribute("name"),"to:", toElement.getAttribute("name")
            self.addBorder(int(fromElement.getAttribute("tid")),int(toElement.getAttribute("tid")), \
                            direction, borderType, ftattackmod, ftdefendmod, tfattackmod, \
                            tfdefendmod, ftattackmin, ftdefendmin, tfattackmin, tfdefendmin )      
  
  def addBorder(self, fromIdentifier, toIdentifier, direction="Two-way", borderType = "Default", ftattackmod = "0",
                ftdefendmod="0", tfattackmod="0",
                tfdefendmod="0", ftattackmin="0",
                ftdefendmin="0", tfattackmin="0", 
                tfdefendmin="0"):
    ''' 
    Adds borders based upon names or territory IDs.
    Arguments correspond to attributes of the new border element.
    
    Args:
      from/to Identifiers: can be a Name or territory ID, but both must be the same 
      
    .. note::
       a "borders" element is created if it does not already exist
       
    .. warning::
      If your territory names are integers, they will get treated as tid attributes, so don't do this!!

    '''
    #print "add border called with identity: ",fromIdentifier,toIdentifier
    
    try:
      fromID = int(fromIdentifier)
      toID = int(toIdentifier)
      #got a territory ID
      #print "getting territory element by ID",fromIdentifier,toIdentifier
      return self.__addBorderByID(fromID,toID,direction, borderType, ftattackmod,
                ftdefendmod, tfattackmod,
                tfdefendmod, ftattackmin,
                ftdefendmin, tfattackmin, 
                tfdefendmin)

    except:
      #print "caught error:", exc_info()[0]
      #traceback.print_exc()

      # must be a name
      #print "adding borders by name",fromIdentifier,toIdentifier
      return self.__addBorderByName(fromIdentifier,toIdentifier,direction, borderType, ftattackmod,
                ftdefendmod, tfattackmod,
                tfdefendmod, ftattackmin,
                ftdefendmin, tfattackmin, 
                tfdefendmin)
    
  def __addBorderByName(self, fromName, toName, direction = "Two-way", 
                borderType = "Default", ftattackmod = "0",
                ftdefendmod="0", tfattackmod="0",
                tfdefendmod="0", ftattackmin="0",
                ftdefendmin="0", tfattackmin="0", 
                tfdefendmin="0"):
      #print "name - adding border from ",fromName,toName
      fromID = self.getTerritoryIDFromName(fromName)
      toID = self.getTerritoryIDFromName(toName)
      
      #print "attempting to add a border between",fromID,toID
      if fromID != False and toID != False :
        #print "adding border between",fromID,toID
        return self.__addBorderByID(fromID, toID, direction, borderType, ftattackmod,
                ftdefendmod, tfattackmod,
                tfdefendmod, ftattackmin,
                ftdefendmin, tfattackmin, 
                tfdefendmin)

    
  def __addBorderByID(self, fromid, toid, direction = "Two-way", 
                borderType = "Default", ftattackmod = "0",
                ftdefendmod="0", tfattackmod="0",
                tfdefendmod="0", ftattackmin="0",
                ftdefendmin="0", tfattackmin="0", 
                tfdefendmin="0"):
    '''
    Adds a border.  Arguments correspond to attributes of the new border element.

    .. note::
       a "borders" element is created if it does not already exist
    '''
    #print "ID - adding border from ",fromid,toid
    
    if(fromid == toid):
      return False
    
    if (self.doTheyBorder(fromid, toid)):
      print "didn't add border - already existed: ",fromid, toid
      return False

    newBorderElement = self.DOM.createElement("border")
    newBorderElement.setAttribute("fromid",str(fromid))
    newBorderElement.setAttribute("toid",str(toid))
    newBorderElement.setAttribute("direction",str(direction))
    newBorderElement.setAttribute("type",str(borderType))
    newBorderElement.setAttribute("ftattackmod",str(ftattackmod))
    newBorderElement.setAttribute("ftdefendmod",str(ftdefendmod))
    newBorderElement.setAttribute("tfattackmod",str(tfattackmod))
    newBorderElement.setAttribute("ftdefendmod",str(ftdefendmod))
    newBorderElement.setAttribute("ftattackmin",str(ftattackmin))
    newBorderElement.setAttribute("ftdefendmin",str(ftdefendmin))
    newBorderElement.setAttribute("tfattackmin",str(tfattackmin))
    newBorderElement.setAttribute("tfdefendmin",str(tfdefendmin))

    bordersElements = self.DOM.getElementsByTagName("borders")
    #print bordersElements
    if (bordersElements == None or len(bordersElements) == 0):
      bordersElement = self.DOM.createElement("borders")
      bordersElement.appendChild(newBorderElement)
      self.DOM.getElementsByTagName("WarGearXML")[0].appendChild(bordersElement)
    else:
      bordersElements[0].appendChild(newBorderElement)


  def addTerritory(self, name, xpos, ypos, maxUnits = "0", **kwargs):
    '''
    Adds a territory.  Arguments correspond to attributes of the new territory element.
    Pass any territory elements in as kwargs to set them.
    e.g.     scenario_type="Neutral" scenario_seat="0" scenario_units="0"
    @todo: refactor calls that use maxunits to do it via kwargs.
    
    .. note::
       a "territories" element is created if it does not already exist
    '''
    
    #import pdb; pdb.set_trace()

    #print "adding territory",name,xpos,ypos
    # get max tid (or 0) & start at one greater
    maxTID = 0
    for territory in self.DOM.getElementsByTagName("territory"):
      if (maxTID <1+ int(territory.getAttribute("tid"))):
        maxTID = 1+int(territory.getAttribute("tid"))

    newTerritoryElement = self.DOM.createElement("territory")
    newTerritoryElement.setAttribute("name",str(name))
    newTerritoryElement.setAttribute("xpos",str(int(xpos)))
    newTerritoryElement.setAttribute("ypos",str(int(ypos)))
    newTerritoryElement.setAttribute("max_units",str(int(maxUnits)))
    newTerritoryElement.setAttribute("tid",str(maxTID))
    
    for key, value in kwargs.iteritems():
      newTerritoryElement.setAttribute(key,value)

    territoriesElements = self.DOM.getElementsByTagName("territories")
    if (territoriesElements == None or territoriesElements.length == 0):
      territoriesElement = self.DOM.createElement("territories")
      wge = self.DOM.getElementsByTagName("WarGearXML")[0]
      wge.appendChild(territoriesElement)
      territoriesElement.appendChild(newTerritoryElement)

    else:
      territoriesElements[0].appendChild(newTerritoryElement)
    
    return maxTID;

  def addContinentFromElements(self, continentName, territoryElementList, bonus=1):
    '''
    Adds a continent.  Arguments correspond to attributes of the new continent element.

    .. note::
       a "continents" element is created if it does not already exist
    '''
    #print "addContinentFromElements:", continentName, territoryElementList, bonus
    territoryIDList = []
    for territoryElement in territoryElementList:
      tid = territoryElement.getAttribute("tid")
      territoryIDList.append(tid)
    territoryIDsString = ",".join(territoryIDList)
    self.addContinent(continentName,territoryIDsString, bonus)




  def addContinent(self, continentName, memberIDs, bonus=1,factory=-1,factoryType="Standard"):
    '''
    factoryType = ["Standard","AutoCapture","Universal"]
    
    '''
    if (self.debug):
      print "continentName",continentName,"memberIDs", memberIDs,"bonus",bonus,"factory",factory,"factoryType",factoryType
    
    if isinstance(memberIDs, basestring):
      self.addContinentFromMemberIDString(continentName, memberIDs, bonus,factory,factoryType)
    else:
      self.addContinentFromMemberIDSet(continentName, memberIDs, bonus,factory,factoryType)

  def addContinentFromMemberIDSet(self, continentName, memberIDSet, bonus=1,factory=-1,factoryType="Standard"):
    
    print memberIDSet
    memberIDString = ""    
    for tid in memberIDSet:
      memberIDString += ("," + str(tid))
    
    self.addContinentFromMemberIDString(continentName,memberIDString[1:],bonus,factory,factoryType)
    

  def addContinentFromMemberIDString(self, continentName, memberIDsString, bonus=1,factory=-1,factoryType="Standard"):
    '''
    Adds a continent.  Arguments correspond to attributes of the new continent element.

    .. note::
       a "continents" element is created if it does not already exist
    '''
    #print "Adding Continent",continentName, memberIDsString, bonus
    newContinentElement = self.DOM.createElement("continent")
    newContinentElement.setAttribute("boardid",str(
        self.DOM.getElementsByTagName("board")[0].getAttribute("boardid")))
    newContinentElement.setAttribute("name",str(continentName))
    newContinentElement.setAttribute("bonus",str(bonus))
    newContinentElement.setAttribute("members",str(memberIDsString))
    newContinentElement.setAttribute("factory",str(factory))
    newContinentElement.setAttribute("factory_type",str(factoryType))

    continentsElements = self.DOM.getElementsByTagName("continents")
#    print "adding continent",str(newContinentElement)
    if (continentsElements == None or len(continentsElements) == 0):
      continentsElement = self.DOM.createElement("continents")
      continentsElement.appendChild(newContinentElement)
      self.DOM.getElementsByTagName("WarGearXML")[0].appendChild(continentsElement)
    else:
      continentsElements[0].appendChild(newContinentElement)
    
    #print "Adding Continent",newContinentElement.toprettyxml()

  def addRotatingFactories(self, **kwargs):
    '''
    Accepted kwargs: namePrefix, territoryIds or territoryNames
    
    '''
    
    if kwargs.get("territoryIds") == None and kwargs.get("territoryNames") == None:
      print "Must pass territoryIds or territoryNames as an argument to addRotatingFactories"
      return
    
    if kwargs.get("territoryNames"):
      tids = self.getTerritoryIDsFromNames(kwargs["territoryNames"])  
    else:
      tids = kwargs["territoryIds"]
    
    namePrefix = kwargs.get("namePrefix")
    
    if namePrefix != None:
      namePrefix += "_"
    else:
      namePrefix = ""
    
    
    for tix in range(len(tids)):
      tix2 = tix + 1;
      if tix2 == len(tids):
        tix2 = 0
      tid1 = tids[tix]
      tid2 = tids[tix2]
      tname1 = self.getTerritoryNameFromID(tid1)
      tname2 = self.getTerritoryNameFromID(tid2)
      
      continentName = namePrefix + tname1 + "_" + tname2      
      self.addContinent(continentName + "-ON", tid1, +1, tid2,"AutoCapture")
      self.addContinent(continentName + "-OFF", tid1, -1, tid1,"AutoCapture")

       
  def printBorderDistributionTable(self):
    '''
    Prints a table to show how many territories there are with N borders.
    '''
    print "Distribution  of  Borders"
    print "-------------------------"
    print "# Borders | # Territories"

    maxBName, maxB = self.getMostBorderedTerritory()
    for ixBorder in range(0,maxB+1):
      print repr(ixBorder).rjust(8),' |',repr(self.countTerritoriesWithBorders(ixBorder)).rjust(6)



  def printContinentBonusDistributionTable(self):
    '''
    Prints a table to show how many continents there are with a bonus of N.
    '''
    print "Distribution of Continent Bonuses"
    print "---------------------------------"
    print "  Bonus |  # of Continents"
    maxBName, maxB = self.getLargestBonusContinent()
    for ixBonus in range(0,maxB+1):
      print repr(ixBonus).rjust(6),' |',repr(self.countContinentsWithBonus(ixBonus)).rjust(6)
          
  def printStatistics(self):
    '''
    Print some statistics about a map.
    '''
    print "Map Name:",self.DOM.getElementsByTagName("board")[0].getAttribute("boardname")
    print "# of Territories:",len(self.DOM.getElementsByTagName("territory"))
    print "# of Continents:",len(self.DOM.getElementsByTagName("continent"))
    print "# of Borders:",len(self.DOM.getElementsByTagName("border"))
    print "Total Continent Bonus",self.calculateTotalContinentBonus()
    print "Total Territory Bonus",self.calculateTotalTerritoryBonus()
    print "Total Bonus",self.calculateTotalBoardBonus()
    print ""
    self.printBorderDistributionTable()
    print ""
    #self.printContinentBonusDistributionTable()

 
  def calculateTotalContinentBonus(self):
    ''' calculateTotalContinentBonus '''
    total = 0
    for continentElement in self.DOM.getElementsByTagName("continent"):
      total += int(continentElement.getAttribute("bonus"))
    return total

  # todo: check that return value is rounding correctly
  def calculateTotalTerritoryBonus(self):
    ''' calculateTotalTerritoryBonus '''
    territoryCount = len(self.DOM.getElementsByTagName("territory"))
    return territoryCount / int(self.DOM.getElementsByTagName("rules")[0].getAttribute("bonus_per_x_territories"))



  def calculateTotalBoardBonus(self):
    ''' calculateTotalBoardBonus '''
    return self.calculateTotalContinentBonus() + self.calculateTotalTerritoryBonus()


  '''  Never finished this.  Instead it would be useful to have functions that calculate graph properties like:
  * http://en.wikipedia.org/wiki/Centrality
  ** http://en.wikipedia.org/wiki/Betweenness_Centrality
  ** http://en.wikipedia.org/wiki/Degree_%28graph_theory%29
  * http://en.wikipedia.org/l/Menger's_theorem
  * http://en.wikipedia.org/wiki/Clustering_coefficient
  * http://en.wikipedia.org/wiki/Cheeger_constant_%28graph_theory%29
  
     
  def calculateChokePoints(self):
    
    # for every territory alculate
    
    # iterate over every territory
    territories = self.DOM.getElementsByTagName("territory")
    for chokepointTerritory in territories:
      for sourceTerritory in territories:
        for destTerritory in territories:
          
        shortestDistance = self.findShortestDistance(sourceTerritory,destTerritory)
        shortestDistanceAvoiding =  self.findShortestDistance(sourceTerritory,destTerritory,chokepointTerritory)
  '''        


  # count how many territories have numBorders
  def countTerritoriesWithBorders(self, numBorders, direction="Two-way"):
    '''  '''
    borderCounts = self.getBorderCounts(direction)
    count = 0;
    for BName,BCount in borderCounts.iteritems():
      if (BCount == numBorders):
        count += 1

    return count;

  # count how many continents have numBonus
  def countContinentsWithBonus(self, numBonus):
    ''' '''
    count = 0;
    for continentElement in self.DOM.getElementsByTagName("continent"):
      #print "continent",continentElement.getAttribute("name")
      #print "bonus",continentElement.getAttribute("bonus")
      if (int(continentElement.getAttribute("bonus")) == numBonus):
        #print "found one with bonus=",numBonus
        count += 1

    return count;

  def doTheyBorder(self, ID1, ID2):
    '''
    Return true if the territories identified by ID1 & ID2 share a border.  False otherwise
    '''
    #print "checking for border:",ID1,ID2
    ID1 = int(ID1)
    ID2 = int(ID2)
    for borderElement in self.DOM.getElementsByTagName("border"):
      fromID = int(borderElement.getAttribute("fromid"))
      toID =  int(borderElement.getAttribute("toid"))
      direction = borderElement.getAttribute("direction")
      if (fromID == ID1 and toID == ID2):
        #print "border found",ID1,ID2
        return True
      if (fromID == ID2 and toID == ID1 and direction == "Two-way"):
        # print "border found",ID1,ID2
        return True
      
    #print "border not found"
    return False
    
    




  def deleteTerritory(self, identifier):
    ''' 
    Delete a territory.
    
    Args:
      identifier can be a Name or ID 
    '''
   
    try:
      ID = int(identifier)
      #got a identifier ID
      return self.__deleteTerritoryByID(ID)  

    except:
      # must be a name
      return self.__deleteTerritoryByName(identifier)
  
  
  def __deleteTerritoryByName(self, territoryName):
    for territory in self.DOM.getElementsByTagName("territory"):
      if (territory.getAttribute("name") == territoryName):        
        return self.__deleteTerritoryByID(territory.getAttribute("tid"))
    return False

  def __deleteTerritoryByID(self, territoryID):
    ''' 
     deletes a territory from the XML, includes relevant borders, 
     and removes itself from continents

     returns false if the territoryID was not found, true otherwise
    '''

    # delete the territory element from the DOM
    found = False
    for territoryElement in self.DOM.getElementsByTagName("territory"):
      #print territoryID
      #print territoryElement.getAttribute("tid")
      if (int(territoryElement.getAttribute("tid")) == int(territoryID)):
        found = True
        territoryElement.parentNode.removeChild(territoryElement)
        territoryElement.unlink()
   
    if not found:
      return False
    # todo: move this to a function
    # find borders that include this territoryID, and remove them
    for borderElement in self.DOM.getElementsByTagName("border"):
      
      if (int(borderElement.getAttribute("fromid")) == int(territoryID) or 
        int(borderElement.getAttribute("toid")) == int(territoryID)):
        borderElement.parentNode.removeChild(borderElement)
        borderElement.unlink()

    # todo: move this to a function
    # remove this territoryID from all continent member lists
    # remove the continent if there are no longer any territories in it.
    #print "in delete by tid",self.DOM.toprettyxml()
    for continentElement in self.DOM.getElementsByTagName("continent"):
      memberList = set()
      #print territoryID,"c:",continentElement.getAttribute("name")," m:",continentElement.getAttribute("members")
      #print continentElement.toprettyxml()
      for memberID in continentElement.getAttribute("members").split(','):
        #print "for",continentElement.getAttribute("name"),"looking at",memberID
        #print "t,m",territoryID,memberID        
        if int(memberID) != int(territoryID):
          memberList.add(str(int(memberID)))
      memberListString = ",".join(memberList)
      #print "mls",memberListString
      continentElement.setAttribute("members",str(memberListString))
      
      if (len(memberList) == 0):
        continentElement.parentNode.removeChild(continentElement)
        continentElement.unlink()
        
      
    return True

  def deleteEmptyContinents(self):
    '''
    Find all continents with no members
    '''
    continentsElement = self.DOM.getElementsByTagName("continents")[0]
    for continentElement in self.DOM.getElementsByTagName("continent"):
      if (len(continentElement.getAttribute("members")) == 0):
        continentsElement.removeChild(continentElement)
        continentElement.unlink()        

  def deleteBorder(self,id1,id2):
    bordersElement = self.DOM.getElementsByTagName("borders")[0]
    for borderElement in self.DOM.getElementsByTagName("border"):
      if (borderElement.getAttribute("fromid") == id1 and borderElement.getAttribute("toid") == id2) or (borderElement.getAttribute("fromid") == id2 and borderElement.getAttribute("toid") == id1):
        bordersElement.removeChild(borderElement)
        borderElement.unlink()
    

  def deleteAllBorders(self):
    bordersElement = self.DOM.getElementsByTagName("borders")[0]
    for borderElement in self.DOM.getElementsByTagName("border"):
      bordersElement.removeChild(borderElement)
      borderElement.unlink()
      
    WarGearXMLElement = self.DOM.getElementsByTagName("WarGearXML")[0]
    WarGearXMLElement.removeChild(bordersElement)

  def deleteAllTerritories(self):
    territoriesElement = self.DOM.getElementsByTagName("territories")[0]
    for territoryElement in self.DOM.getElementsByTagName("territory"):
      territoriesElement.removeChild(territoryElement)
      territoryElement.unlink()
    
    WarGearXMLElement = self.DOM.getElementsByTagName("WarGearXML")[0]
    WarGearXMLElement.removeChild(territoriesElement)
    
  def deleteContinent(self,continentName):
    continentsElements = self.DOM.getElementsByTagName("continents")
    if len(continentsElements) == 0:
      return
    continentsElement = continentsElements[0]
    for continentElement in self.DOM.getElementsByTagName("continent"):
      if (continentElement.getAttribute("name") == continentName):
        continentsElement.removeChild(continentElement)
        continentElement.unlink()

  def deleteAllContinents(self,fullDelete=True):
    continentsElements = self.DOM.getElementsByTagName("continents")
    if len(continentsElements) == 0:
      return
    continentsElement = continentsElements[0]
    for continentElement in self.DOM.getElementsByTagName("continent"):
      continentsElement.removeChild(continentElement)
      continentElement.unlink()
    
    if (fullDelete):
      WarGearXMLElement = self.DOM.getElementsByTagName("WarGearXML")[0]
      WarGearXMLElement.removeChild(continentsElement)

class HexGridWGMap(WGMap):
  """Just a stub """
  pass

class SquareGridWGMap(WGMap):
  """Extends :class:WGMap class for maps on a rectangular grid"""
  
  def __init__(self):
    """Constructor"""
    super(SquareGridWGMap,self).__init__()

    self.rows = 0
    self.cols = 0
    self.doWrap = True

  def wrapR(self,r):
    if (not self.doWrap):
      return r
    if r < 0:
      r = self.wrapR(r+self.rows)
    if r >= self.rows:
      r = self.wrapR(r-self.rows)
    return r
    
  def wrapC(self,c):
    if (not self.doWrap):
      return c
    if c < 0:
      c = self.wrapC(c+self.cols)
    if c >= self.cols:
      c = self.wrapC(c-self.cols)
    return c

  def wrapRC(self,(r,c)):    
    return (self.wrapR(r),self.wrapC(c))

  def inBorders(self,(r,c)):
    if r < 0 or r >= self.rows or c < 0 or c >= self.cols:
      return False
    return True
   
   
  def connectSeperateGroups(self,territoryID = None):
    
    done = False
    while not done:
      done = self.connectTwoGroups(territoryID)
    
    
    
  def connectTwoGroups(self,territoryID = None):
    '''
    Find territory groups that are not connected, and join them up.
    Assumes territories adjacent on the map can share a border.
    '''
    # initial setup 
    if territoryID == None:
      territoryID = self.DOM.getElementsByTagName("territory")[0].getAttribute("tid")
    #print "territoryID",territoryID
    territoriesReached = set(territoryID)
    #print "territoriesReached",territoriesReached
    territoriesToCheck = set() #territories that have neighbors we may not have looked at yet

    # account for neighbors of first territory
    territoriesToCheck |= self.getNeighborIDsFromID(territoryID)

    #print "territoriesToCheck", territoriesToCheck
    while len(territoriesToCheck) > 0:
      # get a territory to check/reach
      territoryID = territoriesToCheck.pop()
      #print "looking at",territoryID
      # find all of it's neighbors
      neighbors = self.getNeighborIDsFromID(territoryID)
      #print "neighbors", neighbors
      # add any newly available territories
      territoriesToCheck |= (neighbors - territoriesReached)
      #print "territoriesToCheck", territoriesToCheck
      
      territoriesReached.add(territoryID)
   
    # get a set of all the territory ID
    allTerritories = set()
    for territory in  self.DOM.getElementsByTagName("territory"):
      allTerritories.add(territory.getAttribute("tid"))

    #print "allTerritories",allTerritories
    #print "territoriesReached",territoriesReached
    
    territoriesMissed = allTerritories - territoriesReached
    #self.printDOM()
    #print "territoriesMissed",territoriesMissed     
    if len(territoriesMissed) == 0:
      return True
    else:
      #import pdb; pdb.set_trace()
      #print "connecting two groups of territories"
      for t1 in territoriesMissed:
        for t2 in territoriesReached:
          (r1,c1) = self.getRC(self.getTerritoryElement(t1))     
          (r2,c2) = self.getRC(self.getTerritoryElement(t2))
          #print "comparing",t1,t2,r1,c1,r2,c2
          if abs(r1-r2)+abs(c1-c2) < 2: #found a neighbor (no diagonals)
            #pdb.set_trace()
            self.addBorder(t1,t2)
            return False
            
      #return False  #give up!          
      #print "all territories:", self.getTerritoryNameFromIDs(allTerritories)
      #print "territories reached:",self.getTerritoryNameFromIDs(territoriesReached)
      #print "territories missed: ", self.getTerritoryNameFromIDs(allTerritories - territoriesReached)
      #return self.connectSeperateGroups(territoryID)

    raise StandardError #we should never get here  
    #return False
  
  
  def createTerritories(self, xOrigin=10, yOrigin=10, xOffset=20, yOffset=20):
    '''
    Args:
      rows,cols (int): The number of rows/columns of territories. 
      xOrigin,yOrigin (int): The position of the upper left grid box.  
      xOffset,yOffset (int): The width of the grid boxes.
    '''
    xpos = xOrigin
    for col in range(self.cols):
      ypos = yOrigin
      for row in range(self.rows):
        territoryName = self.getTerritoryName(row,col)
        self.addTerritory(territoryName, str(xpos), str(ypos))
        ypos += yOffset
      xpos += xOffset
 
  def createBlockContinents(self, bonus):
    ''' 
    Creates continents of every 2x2 block.
    
    Args:
      self.rows,self.cols (int): The number of rows/columns of territories. 
 
    '''
    for uly in range(self.rows-1):
      for ulx in range(self.cols-1):
        territoryElements = []
        # contintent name is name of UL territory
        #print "gridname", self.getTerritoryName(uly,ulx)
        territoryElement = self.getTerritoryElement( 
            self.getTerritoryName(uly,ulx))
        #print "territoryElement",territoryElement
        territoryElements.append( territoryElement)
        territoryElements.append( self.getTerritoryElement( 
            self.getTerritoryName(uly+1,ulx)))
        territoryElements.append( self.getTerritoryElement( 
            self.getTerritoryName(uly,ulx+1)))
        territoryElements.append( self.getTerritoryElement( 
            self.getTerritoryName(uly+1,ulx+1)))
        
        self.addContinentFromElements(self.getTerritoryName(uly,ulx),territoryElements, bonus)

  def getTerritoryName(self, row, col):
    '''
    Calculate the territory name from arguments
    '''
    if self.doWrap:
      return str(self.wrapR(row)) + "_" + str(self.wrapC(col))
    else:
      return str(row) + "_" + str(col)

  def getRC(self, territoryElement):
    
    territoryName = territoryElement.getAttribute("name")
    return  map(int, territoryName.split("_"))

  def getTerritoryElement(self, territoryIdentifier):
    
    #print "MazeWGMap.getTerritoryElement() called with",territoryIdentifier
    
    # if this is a string, we want to make sure python doesn't
    # treat it as a tuple
    if isinstance(territoryIdentifier, basestring):
      return WGMap.getTerritoryElement(self,territoryIdentifier)

    try:
      (r,c) = territoryIdentifier
      return WGMap.getTerritoryElement(self,self.getTerritoryName(r,c))
    
    except:
      #print "caught error:", exc_info()[0]
      #traceback.print_exc()

      # must be a name
      #print "getting territory element by name",identifier
      return WGMap.getTerritoryElement(self,territoryIdentifier)
    
  def addOneWayBordersFromBaseTerritoryID(self,baseID,RC,brange=1,attackBonus=0,defenseBonus=0):
    '''
    RC - row column of source of borders
    '''
    #for currentRange in range(brange):
    #  pass
    #self.addBorder(baseID, toID, "One-way", borderType = "Default", attackBonus.str(),
    #            defenseBonus.str())
    
    
  def addBordersViaRegex(self, ULRC, LRRC):
    '''
    ULRC - Upper Left Row Column
    LRRC - Lower Right Row Column
    '''
    (ULR, ULC) = ULRC
    (LRR, LRC) = LRRC
    
    for row in range(ULR,LRR):
      for col in range(ULC,LRC):
        self.addBorder((row,col),(row+1,col))
        self.addBorder((row,col),(row,col+1))
        

  def addBorder(self, fromRC, toRC):
    
    #print "SquareGridWGMap.addBorder():", fromRC,toRC
    
    # if this is a string, we want to make sure python doesn't
    # treat it as a tuple
    if isinstance(fromRC, basestring):
      return WGMap.addBorder(self,fromRC, toRC)
    
    try:
      (fromR, fromC) = fromRC
      (toR,toC) = toRC
      return WGMap.addBorder(self,self.getTerritoryName(fromR,fromC),self.getTerritoryName(toR,toC))
    
    except:
      #print "caught error:", exc_info()[0]
      #traceback.print_exc()

      # must be a name
      #print "getting territory element by name",identifier
      return WGMap.addBorder(self,fromRC, toRC)

  def doTheyBorder(self, fromRC, toRC):
    
    
    # if this is a string, we want to make sure we don't think
    # it is our r,c tuple
    if isinstance(fromRC, basestring):
      return WGMap.doTheyBorder(self, fromRC, toRC)
    
    try:
      (fromR, fromC) = fromRC
      (toR,toC) = toRC
      toID = self.getTerritoryIDFromName(self.getTerritoryName(toR,toC))
      fromID = self.getTerritoryIDFromName(self.getTerritoryName(fromR,fromC))
      return WGMap.doTheyBorder(self,fromID,toID)
    
    except:
      #print "caught error:", exc_info()[0]
      #traceback.print_exc()

      # must be a name
      #print "getting territory element by name",identifier
      return WGMap.doTheyBorder(self,fromRC, toRC)
    
    

  def addBorderToCoordinate(self, fromID,toRow,toCol):
    '''
    Add a border between fromID and the continent at toRow,toCol 
    '''
    if (toRow >= 0 and toCol >= 0 and toRow < self.rows and toCol < self.cols):
      toTerritoryName = self.getTerritoryName(toRow,toCol)
      toID = self.getTerritoryIDFromName(toTerritoryName)
      self.addBorder(fromID, toID)
      
# todo: this is not finished
  def addSquareBorders(self):
    '''Adds borders for a grid created by createTerritories.  All arguments are ints. (incomplete)
    
       .. warning::
       This function does not work yet.

    '''

    if (self.DOM.getElementsByTagName("borders") == None):
      newBordersElement = self.DOM.createElement("borders")
      self.DOM.getElemntsByTagName("board")[0].appendChild(newBordersElement)
      
    for row in range(self.rows):
      for col in range(self.cols):
        #newBorderElement = self.DOM.createElement("border")
        # todo: need to calculate name
        #newBorderElement.setAttribute("name",str(name))

        territoryName = str(row) + "." + str(col)
        #fromID = self.getTerritoryIDFromName(territoryName)
        if (row > 0):
          toName = str(row-1) + "." + str(col)
          #toID = self.getTerritoryIDFromName(toName)
          
          #finish this.    


        
        
      
# from http://stackoverflow.com/questions/651794/whats-the-best-way-to-initialize-a-dict-of-dicts-in-python
#This function has the side effect that any attempts to get a non-existent key also creates the key.  Typically you would only want to auto create a key if you were at the same time setting a key or subkey. 

class AutoVivification(dict):
    """Implementation of perl's autovivification feature."""
    def __getitem__(self, item):
        try:
            return dict.__getitem__(self, item)
        except KeyError:
            value = self[item] = type(self)()
            return value      
 

  

def hordifySuperMetgear2():
  wgmap = WGMap()
  wgmap.loadMapFromFile('//DISKSTATION/data/wargear development/Super Metgear/Super Metgear - 5. Upper Levels.xml')
  wgmap.hordify()
  wgmap.saveMapToFile('//DISKSTATION/data/wargear development/Super Metgear/Super MetgearHordes - 5. Upper Levels.xml',False)
  
#    
def hordifySuperMetgear():
  wgmap = WGMap()
#  wgmap.loadMapFromFile('//BHO/data/wargear development/Super Metgear/Super_Metgear.xml')
#  print "Statistics before Hordify\n"
#  wgmap.printStatistics()
#  wgmap.hordify()
#  print "\n\nStatistics after Hordify\n"
#  wgmap.saveMapToFile('//BHO/data/wargear development/Super Metgear/Super_MetgearHordes.xml')


  for name in ["2. Crateria","3. Tourain","4. Brinstar","5. Wrecked Ship","6. Maridia","7. Norfair"]:
    wgmap.loadMapFromFile('//DISKSTATION/data/wargear development/Super Metgear/Super Metgear - ' + name + '.xml')
    wgmap.hordify()
    wgmap.saveMapToFile('//DISKSTATION/data/wargear development/Super Metgear/Super MetgearHordes - ' + name + '.xml')


def hordifyPangaea():
  wgmap = WGMap()
  wgmap.loadMapFromFile('//BHO/data/wargear development/pangaea/Pangaea - Land&C.xml')
  print "Statistics before Hordify\n"
  wgmap.printStatistics()
  wgmap.hordify(1,"","Ocean.*","Ocean")
  print "\n\nStatistics after Hordify\n"
  wgmap.saveMapToFile('//BHO/data/wargear development/pangaea/Pangaea - Land&CHordes.xml')

def testHordify():
  ''' Testing - Hordify '''
  wgmap = WGMap()
  wgmap.loadMapFromFile('//BHO/data/wargear development/scripts/KnightsTour8x8.xml')
  print "Statistics before Hordify\n"
  wgmap.printStatistics()
  wgmap.hordify(2,"_h",r"new",r"new",True)
  wgmap.hordify(2,"_h",r"new",r"new")
  print "\n\nStatistics after Hordify\n"
  wgmap.hordify(2,"_h",r"new",r"new",True)
  
  
  wgmap.saveMapToFile('//BHO/data/wargear development/scripts/SimpleBoardHordes.xml')

def addDnDGridTerritories():
  wgmap = SquareGridWGMap()
  wgmap.loadMapFromFile('//BHO/data/wargear development/Dungeons & Dragons/Dungeons & Dragons.xml')
  wgmap.rows = 24
  wgmap.cols = 41
  wgmap.doWrap = False
  ULCR = (0,0)
  LRCR = (24,41)
  wgmap.createTerritories(1*25+25/2,7*25+25/2,25,25)
  wgmap.addBordersViaRegex(ULCR,LRCR)
  wgmap.saveMapToFile('//BHO/data/wargear development/Dungeons & Dragons/Dungeons & Dragons.out.xml')

def addDnDPCBorders():
  wgmap = SquareGridWGMap()
  wgmap.loadMapFromFile('//BHO/data/wargear development/Dungeons & Dragons/Dungeons & Dragons.xml')
  wgmap.rows = 24
  wgmap.cols = 41
  wgmap.doWrap = False
  
  mage1ID = wgmap.getTerritoryIDFromName("Mage 1")
  mage2ID = wgmap.getTerritoryIDFromName("Mage 2")
  mage3ID = wgmap.getTerritoryIDFromName("Mage 3")
  mage4ID = wgmap.getTerritoryIDFromName("Mage 4")
  mage5ID = wgmap.getTerritoryIDFromName("Mage 5")
  
  fighter1ID = wgmap.getTerritoryIDFromName("Fighter 1")
  fighter2ID = wgmap.getTerritoryIDFromName("Fighter 2")
  fighter3ID = wgmap.getTerritoryIDFromName("Fighter 3")
  fighter4ID = wgmap.getTerritoryIDFromName("Fighter 4")
  fighter5ID = wgmap.getTerritoryIDFromName("Fighter 5")
  
  cleric1ID = wgmap.getTerritoryIDFromName("Cleric 1")
  cleric2ID = wgmap.getTerritoryIDFromName("Cleric 2")
  cleric3ID = wgmap.getTerritoryIDFromName("Cleric 3")
  cleric4ID = wgmap.getTerritoryIDFromName("Cleric 4")
  cleric5ID = wgmap.getTerritoryIDFromName("Cleric 5")
  
  rogue1ID = wgmap.getTerritoryIDFromName("Rogue 1")
  rogue2ID = wgmap.getTerritoryIDFromName("Rogue 2")
  rogue3ID = wgmap.getTerritoryIDFromName("Rogue 3")
  rogue4ID = wgmap.getTerritoryIDFromName("Rogue 4")
  rogue5ID = wgmap.getTerritoryIDFromName("Rogue 5")
  
  # do level 1s by hand to boot strap the process.
#  mage1Neighbors = wgmap.getAllTerritoriesWithinNBorders(mage1ID, 2)
#  for mage1NID in mage1Neighbors:
#    WGMap.addBorder(self,mage1ID,mage1NID,"One-way","Default","0")
    
  mage1Neighbors = wgmap.getAllTerritoriesWithinNBorders(mage1ID, 4)
  for mage1NID in mage1Neighbors:
    WGMap.addBorder(wgmap,mage2ID,mage1NID,"One-way","Default","1")
    
  mage1Neighbors = wgmap.getAllTerritoriesWithinNBorders(mage1ID, 6)
  for mage1NID in mage1Neighbors:
    WGMap.addBorder(wgmap,mage3ID,mage1NID,"One-way","Default","2")
    
  mage1Neighbors = wgmap.getAllTerritoriesWithinNBorders(mage1ID, 8)
  for mage1NID in mage1Neighbors:
    WGMap.addBorder(wgmap,mage4ID,mage1NID,"One-way","Default","4")
    
  mage1Neighbors = wgmap.getAllTerritoriesWithinNBorders(mage1ID, 10)
  for mage1NID in mage1Neighbors:
    WGMap.addBorder(wgmap,mage5ID,mage1NID,"One-way","Default","8")
    
    
  
#  fighter1Neighbors = wgmap.getAllTerritoriesWithinNBorders(fighter1ID, 1)
#  for fighter1NID in fighter1Neighbors:
#    WGMap.addBorder(self,fighter1ID,fighter1NID,"One-way","Default","2")
    
  fighter1Neighbors = wgmap.getAllTerritoriesWithinNBorders(fighter1ID, 2)
  for fighter1NID in fighter1Neighbors:
    WGMap.addBorder(wgmap,fighter2ID,fighter1NID,"One-way","Default","4")
    
  fighter1Neighbors = wgmap.getAllTerritoriesWithinNBorders(fighter1ID, 3)
  for fighter1NID in fighter1Neighbors:
    WGMap.addBorder(wgmap,fighter3ID,fighter1NID,"One-way","Default","6")
    
  fighter1Neighbors = wgmap.getAllTerritoriesWithinNBorders(fighter1ID, 4)
  for fighter1NID in fighter1Neighbors:
    WGMap.addBorder(wgmap,fighter4ID,fighter1NID,"One-way","Default","8")
    
  fighter1Neighbors = wgmap.getAllTerritoriesWithinNBorders(fighter1ID, 5)
  for fighter1NID in fighter1Neighbors:
    WGMap.addBorder(wgmap,fighter5ID,fighter1NID,"One-way","Default","10")
    
#  cleric1Neighbors = wgmap.getAllTerritoriesWithinNBorders(cleric1ID, 1)
#  for cleric1NID in cleric1Neighbors:
#    WGMap.addBorder(self,cleric1ID,cleric1NID,"One-way","Default","1")
    
  cleric1Neighbors = wgmap.getAllTerritoriesWithinNBorders(cleric1ID, 2)
  for cleric1NID in cleric1Neighbors:
    WGMap.addBorder(wgmap,cleric2ID,cleric1NID,"One-way","Default","2")
    
  cleric1Neighbors = wgmap.getAllTerritoriesWithinNBorders(cleric1ID, 3)
  for cleric1NID in cleric1Neighbors:
    WGMap.addBorder(wgmap,cleric3ID,cleric1NID,"One-way","Default","3")
    
  cleric1Neighbors = wgmap.getAllTerritoriesWithinNBorders(cleric1ID, 4)
  for cleric1NID in cleric1Neighbors:
    WGMap.addBorder(wgmap,cleric4ID,cleric1NID,"One-way","Default","4")
    
  cleric1Neighbors = wgmap.getAllTerritoriesWithinNBorders(cleric1ID, 5)
  for cleric1NID in cleric1Neighbors:
    WGMap.addBorder(wgmap,cleric5ID,cleric1NID,"One-way","Default","5")
    
#  rogue1Neighbors = wgmap.getAllTerritoriesWithinNBorders(rogue1ID, 3)
#  for rogue1NID in rogue1Neighbors:
#    WGMap.addBorder(self,rogue1ID,rogue1NID,"One-way","Default","1")
   
  rogue1Neighbors = wgmap.getAllTerritoriesWithinNBorders(rogue1ID, 4)
  for rogue1NID in rogue1Neighbors:
    WGMap.addBorder(wgmap,rogue2ID,rogue1NID,"One-way","Default","2")
   
  rogue1Neighbors = wgmap.getAllTerritoriesWithinNBorders(rogue1ID, 5)
  for rogue1NID in rogue1Neighbors:
    WGMap.addBorder(wgmap,rogue3ID,rogue1NID,"One-way","Default","3")
   
  rogue1Neighbors = wgmap.getAllTerritoriesWithinNBorders(rogue1ID, 6)
  for rogue1NID in rogue1Neighbors:
    WGMap.addBorder(wgmap,rogue4ID,rogue1NID,"One-way","Default","4")
   
  rogue1Neighbors = wgmap.getAllTerritoriesWithinNBorders(rogue1ID, 7)
  for rogue1NID in rogue1Neighbors:
    WGMap.addBorder(wgmap,rogue5ID,rogue1NID,"One-way","Default","5")
   
  wgmap.saveMapToFile('//BHO/data/wargear development/Dungeons & Dragons/Dungeons & Dragons.out.xml',False)


def addDnDRodContinents():
  wgmap = SquareGridWGMap()
  wgmap.loadMapFromFile('//BHO/data/wargear development/Dungeons & Dragons/Dungeons & Dragons(5).xml')
  
  rodIDs = wgmap.getTerritoryIDsFromNameRegex("Rod")
  print "ROD IDs",rodIDs
  wgmap.addCollectorContinents(rodIDs,3,3)
  wgmap.saveMapToFile('//BHO/data/wargear development/Dungeons & Dragons/Dungeons & Dragons(5).out.xml',False)
  

def addQbertViewTerritories():
  wgmap = WGMap()
  wgmap.loadMapFromFile('//BHO/data/wargear development/qbert/qbert.xml')
  wgmap.addBordersViaRegex("Disk","^[1234567890]*$","One-way","View Only")
  wgmap.saveMapToFile('//BHO/data/wargear development/qbert/qbertOut.xml')


def addBackForMoreDiceContinents():
  
  wgmap = WGMap()
  wgmap.loadMapFromFile('//BHO/data/wargear development/Back For More/Back For More.xml')
  
  diceTerritoryNames = ["2x","4x","8x","16x","32x","64x"]
  diceMultipliers = [1,3,7,15,31,63]
  
  diceTerritoryIDs = []
  for dtn in diceTerritoryNames:
    diceTerritoryIDs.append(wgmap.getTerritoryIDFromName(dtn))
    
  checkerContinents = wgmap.DOM.getElementsByTagName("continent") 
  for checkerContinent in checkerContinents:
    checkerName = checkerContinent.getAttribute("name")
    checkerID = wgmap.getContinentMembersFromName(checkerName)
    print "Adding dice continents for",checkerName,checkerID
    checkerValue = int(checkerContinent.getAttribute("bonus"))
    
    # add single dice continents
    for diceName,diceID,diceMultiplier in zip(diceTerritoryNames,diceTerritoryIDs,diceMultipliers):
      continentName = checkerName + "_" + diceName
      continentMembers = str(diceID) +  "," + str(checkerID)      
      wgmap.addContinent(continentName,continentMembers,diceMultiplier*checkerValue) 
  
    # add two dice continents
    for d1 in range(6):
      for d2 in range(d1):
        d1Name = diceTerritoryNames[d1]
        d1Multiplier = diceMultipliers[d1]
        d1ID = wgmap.getTerritoryIDFromName(d1Name)
        
        d2Name = diceTerritoryNames[d2]
        d2Multiplier = diceMultipliers[d2]
        d2ID = wgmap.getTerritoryIDFromName(d2Name)
        
        continentName = checkerName + "_" + d1Name + "_" + d2Name
        continentMembers = str(d1ID) +  "," + str(d2ID) + "," + str(checkerID)
        continentValue = -1 * min(d1Multiplier,d2Multiplier)*checkerValue      
        wgmap.addContinent(continentName,continentMembers,continentValue) 
  
    # add three dice continents
    for d1 in range(6):
      for d2 in range(d1):
        for d3 in range(d2):
          d1Name = diceTerritoryNames[d1]
          d1Multiplier = diceMultipliers[d1]
          d1ID = wgmap.getTerritoryIDFromName(d1Name)
        
          d2Name = diceTerritoryNames[d2]
          d2Multiplier = diceMultipliers[d2]
          d2ID = wgmap.getTerritoryIDFromName(d2Name)
        
          d3Name = diceTerritoryNames[d3]
          d3Multiplier = diceMultipliers[d3]
          d3ID = wgmap.getTerritoryIDFromName(d3Name)
        
          continentName = checkerName + "_" + d1Name + "_" + d2Name + "_" + d3Name
          continentMembers = str(d1ID) +  "," + str(d2ID) +  "," + str(d3ID) + "," + str(checkerID)
          continentValue = min(d1Multiplier,d2Multiplier,d3Multiplier)*checkerValue      
          wgmap.addContinent(continentName,continentMembers,continentValue) 
  
    # add four dice continents
    for d1 in range(6):
      for d2 in range(d1):
        for d3 in range(d2):
          for d4 in range(d3):
            d1Name = diceTerritoryNames[d1]
            d1Multiplier = diceMultipliers[d1]
            d1ID = wgmap.getTerritoryIDFromName(d1Name)
          
            d2Name = diceTerritoryNames[d2]
            d2Multiplier = diceMultipliers[d2]
            d2ID = wgmap.getTerritoryIDFromName(d2Name)
          
            d3Name = diceTerritoryNames[d3]
            d3Multiplier = diceMultipliers[d3]
            d3ID = wgmap.getTerritoryIDFromName(d3Name)
          
            d4Name = diceTerritoryNames[d4]
            d4Multiplier = diceMultipliers[d4]
            d4ID = wgmap.getTerritoryIDFromName(d4Name)
          
            continentName = checkerName + "_" + d1Name + "_" + d2Name + "_" + d3Name + "_" + d4Name
            continentMembers = str(d1ID) +  "," + str(d2ID) +  "," + str(d3ID) + "," + str(d4ID) + "," + str(checkerID)
            continentValue =-1 *  min(d1Multiplier,d2Multiplier,d3Multiplier,d4Multiplier)*checkerValue      
            wgmap.addContinent(continentName,continentMembers,continentValue) 
  
    # add five dice continents
    for d1 in range(6):
      for d2 in range(d1):
        for d3 in range(d2):
          for d4 in range(d3):
            for d5 in range(d4):
              d1Name = diceTerritoryNames[d1]
              d1Multiplier = diceMultipliers[d1]
              d1ID = wgmap.getTerritoryIDFromName(d1Name)
            
              d2Name = diceTerritoryNames[d2]
              d2Multiplier = diceMultipliers[d2]
              d2ID = wgmap.getTerritoryIDFromName(d2Name)
            
              d3Name = diceTerritoryNames[d3]
              d3Multiplier = diceMultipliers[d3]
              d3ID = wgmap.getTerritoryIDFromName(d3Name)
            
              d4Name = diceTerritoryNames[d4]
              d4Multiplier = diceMultipliers[d4]
              d4ID = wgmap.getTerritoryIDFromName(d4Name)
            
              d5Name = diceTerritoryNames[d5]
              d5Multiplier = diceMultipliers[d5]
              d5ID = wgmap.getTerritoryIDFromName(d5Name)
            
              continentName = checkerName + "_" + d1Name + "_" + d2Name + "_" + d3Name + "_" + d4Name+ "_" + d5Name
              continentMembers = str(d1ID) +  "," + str(d2ID) +  "," + str(d3ID) + "," + str(d4ID) + "," + str(d5ID) + "," + str(checkerID)
              continentValue = min(d1Multiplier,d2Multiplier,d3Multiplier,d4Multiplier,d5Multiplier)*checkerValue      
              wgmap.addContinent(continentName,continentMembers,continentValue) 
  
    # kind of silly to go through all this for one continent, but eh.
    # add six dice continents
    for d1 in range(6):
      for d2 in range(d1):
        for d3 in range(d2):
          for d4 in range(d3):
            for d5 in range(d4):
              for d6 in range(d5):
                d1Name = diceTerritoryNames[d1]
                d1Multiplier = diceMultipliers[d1]
                d1ID = wgmap.getTerritoryIDFromName(d1Name)
              
                d2Name = diceTerritoryNames[d2]
                d2Multiplier = diceMultipliers[d2]
                d2ID = wgmap.getTerritoryIDFromName(d2Name)
              
                d3Name = diceTerritoryNames[d3]
                d3Multiplier = diceMultipliers[d3]
                d3ID = wgmap.getTerritoryIDFromName(d3Name)
              
                d4Name = diceTerritoryNames[d4]
                d4Multiplier = diceMultipliers[d4]
                d4ID = wgmap.getTerritoryIDFromName(d4Name)
              
                d5Name = diceTerritoryNames[d5]
                d5Multiplier = diceMultipliers[d5]
                d5ID = wgmap.getTerritoryIDFromName(d5Name)
              
                d6Name = diceTerritoryNames[d6]
                d6Multiplier = diceMultipliers[d6]
                d6ID = wgmap.getTerritoryIDFromName(d6Name)
              
                continentName = checkerName + "_" + d1Name + "_" + d2Name + "_" + d3Name + "_" + d4Name + "_" + d5Name + "_" + d6Name
                continentMembers = str(d1ID) +  "," + str(d2ID) +  "," + str(d3ID) + "," + str(d4ID) + "," + str(d5ID) + "," + str(d6ID) + "," + str(checkerID)
                continentValue = -1 *min(d1Multiplier,d2Multiplier,d3Multiplier,d4Multiplier,d5Multiplier,d6Multiplier)*checkerValue      
                wgmap.addContinent(continentName,continentMembers,continentValue) 
     

  
  
  
  wgmap.saveMapToFile('//BHO/data/wargear development/Back For More/Back For More - Out.xml')
  

def addDejeweledContinents():
  wgmap = WGMap()
  wgmap.loadMapFromFile('//DISKSTATION/data/wargear development/Dejeweled/Dejeweled.xml')
  wgmap.deleteAllContinents(False)
  
  columns = ['a','b','c','d','e','f','g','h','i','j','k']
  rows = ['1','2','3','4','5','6','7','8','9','10','11']

  # add row continents  
  for cix in range(len(columns)):
    for rix in range(len(rows) - 2):
      id1 = wgmap.getTerritoryIDFromName(columns[cix]+rows[rix])
      id2 = wgmap.getTerritoryIDFromName(columns[cix]+rows[rix+1])
      id3 = wgmap.getTerritoryIDFromName(columns[cix]+rows[rix+2])
      contName = columns[cix]+rows[rix] + "v"
      contMembers = ",".join([id1, id2, id3])      
      wgmap.addContinent(contName + columns[cix]+rows[rix], contMembers, -5,id1,"Universal")
      wgmap.addContinent(contName + columns[cix]+rows[rix+1], contMembers, -5,id2,"Universal")
      wgmap.addContinent(contName + columns[cix]+rows[rix+2], contMembers, -5,id3,"Universal")
      
      
  # add column continents
  for cix in range(len(columns)-2):
    for rix in range(len(rows)):
      # add row continents
      id1 = wgmap.getTerritoryIDFromName(columns[cix]+rows[rix])
      id2 = wgmap.getTerritoryIDFromName(columns[cix+1]+rows[rix])
      id3 = wgmap.getTerritoryIDFromName(columns[cix+2]+rows[rix])
      contName = columns[cix] +rows[rix]+ "h"
      contMembers = ",".join([id1, id2, id3])      
      wgmap.addContinent(contName + columns[cix]+rows[rix], contMembers, -5,id1,"Universal")
      wgmap.addContinent(contName + columns[cix+1]+rows[rix], contMembers, -5,id2,"Universal")
      wgmap.addContinent(contName + columns[cix+2]+rows[rix], contMembers, -5,id3,"Universal")

  # add individual negative bonuses
  winnerID = wgmap.getTerritoryIDFromName("Winner")
  for c in columns:
    for r in rows:
      tid = wgmap.getTerritoryIDFromName(c+r)
      wgmap.addContinent(c + r + "_noWin",tid,-1,winnerID,"Universal")
      
  
  wgmap.saveMapToFile('//DISKSTATION/data/wargear development/Dejeweled/DejeweledOut.xml',False)


def addSimpleWorldDistantFog():
  wgmap = WGMap()
  wgmap.loadMapFromFile('//DISKSTATION/data/wargear development/simple world/Simple World - Light Fog duel.xml')
  #wgmap.debug = True
  wgmap.addViewBordersToNeighbors(3)
  wgmap.saveMapToFile('//DISKSTATION/data/wargear development/simple world/Simple World - Distant Fog duel.xml',False)
  
  #\\DISKSTATION\data\wargear development\test\hillsanddales
def addHandDHordes():
  wgmap = WGMap()
  wgmap.loadMapFromFile('//DISKSTATION/data/wargear development/test/hillsanddales/Hills and Dales.xml')
  #wgmap.debug = True
  
  #wgmap.hordify(1,"","Ocean.*","Ocean")
  wgmap.deleteAllContinents(False)
  wgmap.hordify("1","","\(1\)","\(1\)")
  wgmap.hordify("1","","\(2\)","\(2\)")
  wgmap.hordify("1","","\(3\)","\(3\)")
  wgmap.hordify("1","","\(4\)","\(4\)")
  wgmap.saveMapToFile('//DISKSTATION/data/wargear development/test/hillsanddales/out.xml',False)


def fixCCJustGems():
  wgmap = WGMap()
  wgmap.loadMapFromFile('//DISKSTATION/data/wargear development/crystal caves/Crystal Caves - Just Gems(3).xml')
  wgmap.debug = True
  
  '''  
  wgmap.deleteAllContinents(False)
  Gems = wgmap.getTerritoryIDsFromNameRegex("Red")
  wgmap.addCollectorContinents(Gems,1,1)
  
  Gems = wgmap.getTerritoryIDsFromNameRegex("Orange")
  wgmap.addCollectorContinents(Gems,1,1)
  
  Gems = wgmap.getTerritoryIDsFromNameRegex("Green")
  wgmap.addCollectorContinents(Gems,1,1)
  
  Gems = wgmap.getTerritoryIDsFromNameRegex("Blue")
  wgmap.addCollectorContinents(Gems,1,1)
  
  
  Gems = wgmap.getTerritoryIDsFromNameRegex("Silver")
  wgmap.addCollectorContinents(Gems,1,1)
  '''
  
  Gems = wgmap.getTerritoryIDsFromNameRegex("Purple")
  wgmap.addCollectorContinents(Gems,1,1)
  
  
  wgmap.saveMapToFile('//DISKSTATION/data/wargear development/crystal caves/Crystal Caves - Just Gems - Out.xml',False)
  
  
def setupLegotaurus():  
  wgmap = WGMap()
  wgmap.loadMapFromFile('//DISKSTATION/data/wargear development/legotaurus/Legotaurus.xml')
  wgmap.debug = True
  rows = ["a","b","c","d","e","f","g","h","i","j","k","l","m","n","o","p","q","r","s","t","u","v","w","x","y","z","aa","bb","cc","dd"]
  cols = ["1","2","3","4","5","6","7","8","9","10","11","12","13","14","15","16","17","18","19","20","21","22","23","24","25","26","27","28","29","30"]

  rBuilders = ["c","d","e","f","g","h","i","j","k","l","m","n","o","p","q","r","s","t","u","v","w","x","y","z","aa","bb"]
  cBuilders = ["6","7","8","9","10","11","12","13","14","15","16","17","18","19","20","21","22","23","24","25"]
  
  attack1ID = wgmap.getTerritoryIDFromName("Attack1")
  attack2ID = wgmap.getTerritoryIDFromName("Attack2")
  attack3ID = wgmap.getTerritoryIDFromName("Attack3")
  attack4ID = wgmap.getTerritoryIDFromName("Attack4")
  
  # add left-right borders
  for r in rows:
    prevC = None
    for c in cols:
      if prevC != None:
        wgmap.addBorder(r+prevC, r+c)
      prevC = c
      
  # add up-down borders
  for c in cols:
    prevR = None
    for r in rows:
      if prevR != None:
        wgmap.addBorder(prevR+c, r+c)
      prevR = r
  
  # set all grid territories to start neutral
  for c in cols:
    for r in rows:
      territory = wgmap.getTerritoryElement(r+c)
      if territory != None:
        #scenario_type="Neutral" scenario_seat="0" scenario_units="0"
        territory.setAttribute("scenario_type","Neutral")
        #territory.setAttribute("scenario_seat","0")
        territory.setAttribute("scenario_units","0")
  
  for c in cBuilders:
    territory = wgmap.getTerritoryElement("Top"+c)
    territory.setAttribute("scenario_type","Neutral")
    territory.setAttribute("scenario_units","0")
  

  # add borders from capitals to top row
  # and add factories to remove old units from the selectors.
  for r in rBuilders:
    territory = wgmap.getTerritoryElement("Left_"+r)
    territory.setAttribute("scenario_type","Neutral")
    territory.setAttribute("scenario_units","0")
    
  
  # add borders from attack to top row
  for c in cBuilders:
    topID = wgmap.getTerritoryIDFromName("Top"+c)
    # def addBorder(self, fromIdentifier, toIdentifier, direction="Two-way", borderType = "Default", ftattackmod = "0",
    wgmap.addBorder(attack1ID,topID,"One-way",ftattackmod="-6")
    wgmap.addBorder(attack2ID,topID,"One-way",ftattackmod="-6")
    wgmap.addBorder(attack3ID,topID,"One-way",ftattackmod="-6")
    wgmap.addBorder(attack4ID,topID,"One-way",ftattackmod="-6")
    wgmap.addContinent(topID+"_cleanup",topID,-1,topID)
  
  # add borders from capitals to top row
  # and add factories to remove old units from the selectors.
  for r in rBuilders:
    leftID = wgmap.getTerritoryIDFromName("Left_"+r)
    wgmap.addBorder(attack1ID,leftID,"One-way",ftattackmod="-6")
    wgmap.addBorder(attack2ID,leftID,"One-way",ftattackmod="-6")
    wgmap.addBorder(attack3ID,leftID,"One-way",ftattackmod="-6")
    wgmap.addBorder(attack4ID,leftID,"One-way",ftattackmod="-6")
    
    #  def addContinent(self, continentName, memberIDs, bonus=1,factory=-1,factoryType="Standard"):
    wgmap.addContinent(leftID+"_cleanup",leftID,-1,leftID)
   
  
   
  # add factories to create walls
  for r in rBuilders:
    for c in cBuilders:
      members = []
      members.append(wgmap.getTerritoryIDFromName("Left_"+r))
      members.append(wgmap.getTerritoryIDFromName("Top"+c))
      target = wgmap.getTerritoryIDFromName(r+c)
      wgmap.addContinent("Builder-"+r+c,members,factory=target,factoryType="Universal")
  
  
  wgmap.saveMapToFile('//DISKSTATION/data/wargear development/legotaurus/Legotaurus-out.xml',False)

def setupTWBB():  
  wgmap = WGMap()
  wgmap.loadMapFromFile('//DISKSTATION/data/wargear development/ThereWillBeBlood/There Will Be Blood!(4).xml')
  wgmap.debug = True

  wgmap.hordify(1,"","Land","Land")
  
  '''
  for each oil well/path/deposit combination, you need several factories:
  12 for addition.  If a player has the oil well & the path & one of the deposits, they get +8 a turn at the oil well.
  ex. - (deposit.well.player#)
  12*12 for deletion.  Same members as above, but it is -1 to each deposit.
  ex - (deposit.well.member#.depletion#)
  '''

  OilPathList = [
                 ["Oil Deposit 1", "Land 8.5","Pipe A1","Pipe A2"], 
                 ["Oil Deposit 1", "Land 4.6","Pipe B1"],
                 ["Oil Deposit 2", "Land 3.8","Pipe D1","Pipe D2"],
                 ["Oil Deposit 2", "Land 6.7","Pipe C1","Pipe C2","Pipe C3"],
                 ["Oil Deposit 3", "Land 5.10","Pipe F1"],
                 ["Oil Deposit 3", "Land 7.11","Pipe G1","Pipe G2"],
                 ["Oil Deposit 4", "Land 8.13","Pipe I1","Pipe I2"],
                 ["Oil Deposit 4", "Land 2.14","Pipe J1","Pipe J2"],
                 ["Oil Deposit 5", "Land 8.5","Pipe A1","Pipe A3","Pipe A4","Pipe A5"], 
                 ["Oil Deposit 5", "Land 6.7","Pipe C1","Pipe C2","Pipe C3","Pipe C4"],
                 ["Oil Deposit 6", "Land 8.9","Pipe E1","Pipe E2","Pipe E3"], 
                 ["Oil Deposit 6", "Land 4.12","Pipe H1","Pipe H2","Pipe H3","Pipe H4","Pipe H5","Pipe H6","Pipe H7","Pipe H8","Pipe H10","Pipe H11","Pipe H12","Pipe H13","Pipe H14"], 
                 ["Oil Deposit 7", "Land 7.11","Pipe G1","Pipe G2","Pipe G3","Pipe G4"], 
                 ["Oil Deposit 7", "Land 4.12","Pipe H1","Pipe H2","Pipe H3"], 
                 ["Oil Deposit 8", "Land 8.5","Pipe A1","Pipe A3","Pipe A6"],
                 ["Oil Deposit 8", "Land 3.8","Pipe D1","Pipe D2","Pipe D3","Pipe D4","Pipe D5","Pipe D6","Pipe D7","Pipe D8","Pipe D9","Pipe D10"],
                 ["Oil Deposit 9", "Land 3.8","Pipe D1","Pipe D2","Pipe D3","Pipe D4","Pipe D5","Pipe D6","Pipe D7","Pipe D8"],
                 ["Oil Deposit 9", "Land 2.14","Pipe J1","Pipe J2","Pipe J3","Pipe J4","Pipe J5","Pipe J6","Pipe J7","Pipe J8","Pipe J9","Pipe J10","Pipe J11","Pipe J12"],
                 ["Oil Deposit 10", "Land 8.9","Pipe E1","Pipe E2","Pipe E3","Pipe E4","Pipe E5","Pipe E6","Pipe E7","Pipe E8"], 
                 ["Oil Deposit 10", "Land 4.12","Pipe H1","Pipe H2","Pipe H3","Pipe H4","Pipe H5","Pipe H6","Pipe H7","Pipe H8","Pipe H9"], 
                 ["Oil Deposit 11", "Land 8.13","Pipe I1","Pipe I2","Pipe I3","Pipe I4","Pipe I5","Pipe I6","Pipe I7"],
                 ["Oil Deposit 11", "Land 2.14","Pipe J1","Pipe J2","Pipe J3","Pipe J4","Pipe J5"]
                 ]
  
  OilAddition = 8
  
  for path in OilPathList:
    deposit = path[0]
    territoryIDs = []
    oilWell = path[1]
    
    for territory in path[1:]:
      territoryIDs.append(wgmap.getTerritoryIDFromName(territory))
      
    for i1 in range(1,13):
      depositID = wgmap.getTerritoryIDFromName(deposit+"."+str(i1))
      territoryIDs.append(depositID)
      for i2 in range(1,13):
        deposit2ID = wgmap.getTerritoryIDFromName(deposit+"."+str(i2))    
        # remove one from each deposit in the well.
        wgmap.addContinent(deposit + "." + oilWell + "." + str(i1)+ "." + str(i2), territoryIDs,-1,deposit2ID,"Universal")              
  
      # add N to top of the well
      wgmap.addContinent(deposit + "." + oilWell + "." + str(i1), territoryIDs, OilAddition, wgmap.getTerritoryIDFromName(oilWell),"Universal")
      territoryIDs.remove(depositID)
  wgmap.saveMapToFile('//DISKSTATION/data/wargear development/ThereWillBeBlood/There Will Be Blood!Out.xml',False)
   
   
def testWGAME():
  wgmap = WGMap()
  wgmap.loadMapFromFile('//DISKSTATION/data/wargear development/test/hordify test - SelfFactories.xml')
  baseIDList = []
  baseIDList.append(1)
  baseIDList.append(2)
  _neighborDistance = 0
  _continentSuffix= "_ch"
  _factory = 3
  _factoryType = "AutoCapture"
  neighborIDList = None
  bonus = 3
  
  wgmap.continentsFromNeighbors(baseIDList, bonus, neighborIds=neighborIDList, neighborDistance=_neighborDistance, continentSuffix=_continentSuffix, factory=_factory, factoryType=_factoryType)
  
  
  wgmap.saveMapToFile('//DISKSTATION/data/wargear development/test/hordify test - SelfFactories-out.xml')

def setupDFMap():
  wgmap = WGMap()
  wgmap.loadMapFromFile('//DISKSTATION/data/wargear development/darkness falls/Darkness Falls.xml')
  
  targetList = ["Kill Factory 1","Kill Factory 2","Kill Factory 3","Kill Factory 4","Kill Factory 5","Kill Factory 6"]
  worldTerritories = ["Venezuana","Brazivia","Colomberu","Baja","Central America","Banks Islands","Baffin","Queen Elizabeth Islands","Ellesmere Islands","Central US","Eastern US","Pacific US","Western US","Newfoundland","Ontario","Quebec","Alberta","British Columbia","Korea","Japan","China","Mongolia","Russia","Finland","Scandinavia","Greece","Egypt","West Africa","Iceland","Britainia","Iberia","Germania","Romania","Portugal","Alaska","Greenland","Kamchatka","Sudopia","Somalya","Congo","Namibia","Madagascar","South Africa","Carribea","Braziguay","Argentina","Algeria","Nigeria","Gaboon","Arabia","Oman","Iran","Manystans","Otherstans","India","Banglapal","Indochina","Philippines","Krasnoyarks","North Urals","Khabarovsk","Yakutia","Chukotka","Irkutsk","South Urals","Tomsk","Tasmania","Western Australia","Central Australia","Eastern Australia","Papau New Guinea","Indonesia","New Zealand","Thule","Daneborg","Scoresbysund","Balkans"]
  
  for wt in worldTerritories:
    memberList = []
    memberList.append(wgmap.getTerritoryIDFromName(wt))
    
    for target in targetList:
      tempList = list(memberList)
      tempList.append(wgmap.getTerritoryIDFromName(target))
      name = "KeepAlive-" + wt + "-" + target
      wgmap.addContinent(name,tempList,"1", wgmap.getTerritoryIDFromName(target),"AutoCapture")
  
  wgmap.saveMapToFile('//DISKSTATION/data/wargear development/darkness falls/Darkness Falls-out.xml',False)

def setupTrivialPursuit():
  wgmap = WGMap()
  wgmap.loadMapFromFile('//DISKSTATION/data/wargear development/Trivial Pursuit/Trivial Pursuit(5).xml')
  Players = ["1","2","3","4","5","6","7","8"]
  Pies = ["A","B","C","D","E","F"]

  # for each player and each "pie acquisition", earn a pie piece  
  for player in Players:
    for pie in Pies:      
      playerID = wgmap.getTerritoryIDFromName("Player "+player)
      boardID = wgmap.getTerritoryIDFromName("Board - "+pie)
      targetID = wgmap.getTerritoryIDFromName("Player "+player + " Pie "+pie)
      members = [playerID, boardID]
      #  def addContinent(self, continentName, memberIDs, bonus=1,factory=-1,factoryType="Standard"):
      wgmap.addContinent("Player " + player + " earn Pie " + pie, members, 1, targetID, "AutoCapture")

  # for each player, if have all pies, autocapture every other player capital
  for player in Players:
    members = []
    for pie in Pies:      
      members.append(wgmap.getTerritoryIDFromName("Player "+player + " Pie "+pie))
    for target in Players:
      if target != player:
        targetID = wgmap.getTerritoryIDFromName("Player "+target)
        wgmap.addContinent("Player "+player + " capture " + target,members,1,targetID,"AutoCapture")

    
  # hordes bonus on main board
  targetIDs = set()
  targetIDs.update(wgmap.getTerritoryIDsFromNameRegex("Board"))
  wgmap.continentsFromNeighbors(targetIDs,"1")
  '''
  # keep alive pattern
  #    each board gives +1 to each capital
  #    each capital has -1 decay on itself
  for boardID in wgmap.getTerritoryIDsFromNameRegex("Board"):
    for player in Players:
      pid = wgmap.getTerritoryIDFromName("Player "+player)
      wgmap.addContinent("Keep Alive " + str(boardID) + " Player " + player,[boardID,pid],1,pid)
  
  for player in Players:
    pid= wgmap.getTerritoryIDFromName("Player "+player)
    wgmap.addContinent("Capital Decay " + player,[pid],"-1",pid)

  '''
  for player in Players:
  # add vision borders.
    for player in Players:
      pid = wgmap.getTerritoryIDFromName("Player "+player)
      
  # from each playerID to each other playerID
      for player2 in Players:
        if player != player2:
          pid2 = wgmap.getTerritoryIDFromName("Player "+player)
          wgmap.addBorder(pid,pid2,borderType="View Only")
          # def addBorder(self, fromIdentifier, toIdentifier, direction="Two-way", borderType = "Default", ftattackmod = "0",
          # from each playerID to every other player pie piece.
          for pie in Pies:      
            targetID = wgmap.getTerritoryIDFromName("Player "+player2 + " Pie "+pie)
            wgmap.addBorder(pid,targetID,borderType="View Only")
        
        
  wgmap.saveMapToFile('//DISKSTATION/data/wargear development/Trivial Pursuit/Trivial Pursuit-out.xml')
  

def setupLizardEscher():
  wgmap = WGMap()
  wgmap.loadMapFromFile('//DISKSTATION/data/wargear development/ESCHER/Lizard Tesselations - M.C. Escher.xml')
  targetIDList = []
  targetIDList.append(wgmap.getTerritoryIDFromName("L1"))
  targetIDList.append(wgmap.getTerritoryIDFromName("L102"))
  targetIDList.append(wgmap.getTerritoryIDFromName("L112"))
  targetIDList.append(wgmap.getTerritoryIDFromName("L15"))
  targetIDList.append(wgmap.getTerritoryIDFromName("L93"))
  targetIDList.append(wgmap.getTerritoryIDFromName("L39"))
  targetIDList.append(wgmap.getTerritoryIDFromName("L59"))
  targetIDList.append(wgmap.getTerritoryIDFromName("L71"))
  
  wgmap.addEliminationCombinationContinents(targetIDList,3,continentSuffix="_Elimination")  
  
  wgmap.saveMapToFile('//DISKSTATION/data/wargear development/ESCHER/Lizard Tesselations - M.C. Escher-out.xml')

  

if __name__ == '__main__':
    print 'Hello World'
    #KnightWGMap.createFunctionCellGame() #.createVerticalStripesKnightsTour() #createRandomKnightTour()
    #KnightWGMap.createStripesGame() #.createVerticalStripesKnightsTour() #createRandomKnightTour()
    #addQbertViewTerritories()
    #createCellsKnightTour();
    #createVerticalStripesKnightsTour()
    #createSnakesGame()
    #createGridGame()
    #createFunctionCellGame()
    #testMazeMap()
    #MazeWGMap.createMazeMaps()
    #createHugeMazeMaps()
    #addBackForMoreDiceContinents()
    #hordifySuperMetgear()
    #hordifySuperMetgear2()           
    #hordifyPangaea()
    #addDnDGridTerritories()
    #addDnDPCBorders()
    #addDnDRodContinents()
    #fixFBorders()
    #addTechFlaskContinents()
    #addDejeweledContinents()
    #fixCCJustGems()
    #setupTWBB()
    #addKnightViewBorders()
    #createSimpleMazeMaps()
    #addSimpleWorldDistantFog()
    #addHandDHordes()
    #setupLegoHordesMap()
    #setupLegoDuelMap()
    #testWGAME()
    #setupLegotaurus()
    #setupLizardEscher()
    #setupFSMMap()
    #setupMuleMap()
    #setupTechMap()
    #setupDFMap()
    #addTechFlaskFortifies()
    #setupTrivialPursuit()
    