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

from General import SquareGridWGMap, WGMap

class KnightWGMap(SquareGridWGMap):
  """
  Extends the SquareGridWGMap.
  Creates a 'chessboard map' in which players
  gain bonuses for 4-squares & borders are connected
  like a knight moves in chess.
  """
  

  def __init__(self):
    """Constructor"""
    super(KnightWGMap,self).__init__()

    self.doWrap = False
  
  def addBordersViaRegex(self):
    '''
    Adds borders as a knight could attack for a grid created 
    by :func:`SquareGridWGMap.createTerritories.
    
    todo: via regex?  Rename this function.
    
    Args are both ints.
    '''
    if self.DOM.getElementsByTagName("borders") == None:
      newBordersElement = self.DOM.createElement("borders")
      self.DOM.getElementsByTagName("board")[0].appendChild(newBordersElement)
      

    for row in range(self.rows):
      for col in range(self.cols):
        # skip half the squares since borders are two way
        if (row+col)%2 == 0:
          continue          
        fromTerritoryName = self.getTerritoryName(row, col)
        fromID = self.getTerritoryIDFromName(fromTerritoryName)
        self.addBorderToCoordinate(fromID,row-2,col-1)
        self.addBorderToCoordinate(fromID,row-2,col+1)
        self.addBorderToCoordinate(fromID,row-1,col-2)
        self.addBorderToCoordinate(fromID,row-1,col+2)
        self.addBorderToCoordinate(fromID,row+1,col-2)
        self.addBorderToCoordinate(fromID,row+2,col-1)
        self.addBorderToCoordinate(fromID,row+1,col+2)
        self.addBorderToCoordinate(fromID,row+2,col+1)

  def createFunctionGame(self,filePath,placeKnightFunc,rowHeight=40,colWidth=40,):
    
    '''Be sure to set the board name by hand'''
    
    xOrigin = colWidth/2
    yOrigin = rowHeight/2
    
    #print "Creating Function Knight's Tour:",filePath,rows,cols,rowHeight,colWidth,xOrigin,yOrigin
    print "Knight's Tour (" + str(self.rows) + "x" + str(self.cols) + ")"#+str(placeKnightFunc)
    
    self.deleteAllBorders()
    self.deleteAllTerritories()
    self.deleteAllContinents()

    #self.setBoardName("Knight's Tour (" + str(rows) + "x" + str(cols) + ")")
    
    self.createTerritories(xOrigin, yOrigin, rowHeight, colWidth)   
    self.addBordersViaRegex()
    #self.createBlockContinents(1)

    print "Deleting Territories",
    territoriesDeleted = []
    inper = .7
    outper = .1
    for r in range(self.rows):
      for c in range(self.cols):
        (doDelete, (inper, outper)) = placeKnightFunc(r, c,  (inper, outper))
        #print doDelete
        if doDelete:
          self.deleteTerritory(self.getTerritoryName(r,c))
          territoriesDeleted.append([r, c])
    
    if (self.checkOneTerritoryCanReachAll() == False):
      return False
    
    territoriesDeleted.extend(self.removeUselessTerritories())
    
    allTerritories = self.getTerritoryIDsFromNameRegex(".*")    
    self.addChainContinents(allTerritories)

    #print "td1",territoriesDeleted
    # find all territories with only one border & no continents - then delete them.
    
    #print "td2",territoriesDeleted

    self.setNumAttacks(int(ceil(sqrt(self.rows*self.cols))))
    self.setNumFortifies(int(ceil(sqrt(sqrt(self.rows*self.cols)))))
    self.setAllSoleContinentTerritoriesToNeutral()
    self.addViewBordersToNeighbors(2)
    
    self.createPNGs(filePath, rowHeight, colWidth, 
                             xOrigin, yOrigin, territoriesDeleted)

    self.saveMapToFile(filePath + ".xml")


    return True
 
  def placeRandomVerticalStripes(self,r,c):
    if(c%5 == 3):
      return (random.random() < .3)        
    if(c%5 == 4):
      return (random.random() < .5)
    
    if(c%5 == 0):
        return True;
    if(c%5 == 1):
      if (random.random() < .5):
        return True;
    if(c%5 == 2):
      if (random.random() < .3):
        return True;

  def placeStripes(self,r,c,(inper,outper)):
    # inper = chance to keep a knight in cell
    # outper = chance to keep a knight out of cell  
    isKnight = False
    
    if ( r%6 == 1 or r%6 == 2 or c%7 == 2 or c%7 == 1):
      isKnight = True
      
  
    # try to even out the random extremes, by increasing the odds if we miss.
    doDelete = not isKnight
    
    return (doDelete, (inper, outper))   
      
 
  def placeRandomSnake(self,r,c):
    if(c%8 == 0) or (c%8 == 7):
      if (r < self.rows-2):
        return random.random() < .85
    if(c%8 ==1) or (c%8 == 6):
      if (r < self.rows-2):
        return random.random() < .15

    if(c%8 == 3) or (c%8 == 4):
      if (r > 1):
        return random.random() < .85
    if(c%8 ==2) or (c%8 == 5):
      if (r > 1):
        return random.random() < .15
      
    return False
 
  def placeGrid(self,r,c):
    
    rFlag = False
    cFlag = False
    if (r%3 == 0):
      rFlag = True
    if (c%3 == 0):
      cFlag = True
    
    if (rFlag and cFlag):
      return False
    
    if (rFlag or cFlag):
      return True
    
    return False
  
  # return true to delete
  def placeCells(self,r,c,(inper,outper)):
    
    inCell = True
    
    # edges
    #if(c==0 or c == self.cols-1 or r==0 or r == self.rows-1):
    #  inCell = False
    
    # dividing rows
#    if( r == self.rows/2-1 or r == self.rows/2):
#    if( r == self.rows/3+1 or r == self.rows/3 or r == 2*self.rows/3+1 or r == 2*self.rows/3):
    if( r % 7 == 4 or  r % 7 == 6 or r % 7== 5):
      inCell = False
    
    # dividing cols
    if( c % 7 == 6 or c % 7 == 4 or c % 7 == 5):
      inCell = False
      
  
    # try to even out the random extremes, by increasing the odds if we miss.
    if (inCell):
      doDelete = (random.random() > inper)
      if doDelete: #delete knight 
        inper += .15  
      else:   #keep knight
        inper = .7
    else:            
      doDelete = (random.random() > outper)
      if doDelete: # delete knight
        outper += .1
      else: # keep knight
        outper = .05
    print doDelete    
    return (doDelete, (inper, outper))

  # return true to delete
  def placeFourSquare(self,r,c,(inper,outper)):
    # inper = chance to keep a knight in cell
    # outper = chance to keep a knight out of cell  
    inCell = True
    
    # edges
    #if(c==0 or c == self.cols-1 or r==0 or r == self.rows-1):
    #  inCell = False
    
    # dividing rows
#    if( r == self.rows/2-1 or r == self.rows/2):
#    if( r == self.rows/3+1 or r == self.rows/3 or r == 2*self.rows/3+1 or r == 2*self.rows/3):
    if( r >= 5 and r <= 9):
      inCell = False
    
    # dividing cols
    if(c >= 5 and c <= 9):
      inCell = False
      
  
    # try to even out the random extremes, by increasing the odds if we miss.
    if (inCell):
      doDelete = (random.random() > inper)
      if doDelete: #delete knight 
        inper += .3
      else:   #keep knight
        inper -= .10
    else:            
      doDelete = (random.random() > outper)
      if doDelete: # delete knight
        outper += .25
      else: # keep knight
        outper -= .5
    #print doDelete    
    print "P4S incell=",inCell, doDelete, (inper, outper)
    return (doDelete, (inper, outper))

  def placeKnightsSpots(self,r,c):
    '''
     012345678
    0 
    1 x  x  x  
    2
    3 x  x  x
    4
    5 x  x  x
    6
    7 x  x  x
    8
    
    '''
    if (r%3==1 and c%3 == 1):
      return True
    else:
      return False
    
     
    

  def createCellsGame(self,filePath,rowHeight=40,colWidth=40):
    
    xOrigin = colWidth/2
    yOrigin = rowHeight/2
    
    print "Creating Cells Knight's Tour:",filePath,self.rows,self.cols,rowHeight,colWidth,xOrigin,yOrigin
    self.deleteAllBorders()
    self.deleteAllTerritories()
    self.deleteAllContinents()

    self.setBoardName("Knight's Tour Cells" + str(self.rows) + "x" + str(self.cols))
    
    if (self.rows%5 != 0 ):
      return -1;
    
    self.createTerritories(xOrigin, yOrigin, rowHeight, colWidth)   
    self.addBordersViaRegex()
    self.createBlockContinents(1)

    print "Deleting Territories",
    territoriesDeleted = [] 
    
    
    #Set knights on all edges.    
    for r in range(self.rows):
      c=0
      self.deleteTerritory(self.getTerritoryName(r,c))
      territoriesDeleted.append([r, c])
      #print r,c," ",

      c = self.cols-1
      self.deleteTerritory(self.getTerritoryName(r,c))
      territoriesDeleted.append([r, c])
      #print r,c," ",
   
    for c in range(self.cols):
      r=0
      self.deleteTerritory(self.getTerritoryName(r,c))
      territoriesDeleted.append([r, c])
      #print r,c," ",
      r = self.rows-1
      self.deleteTerritory(self.getTerritoryName(r,c))
      territoriesDeleted.append([r, c])
      #print r,c," ",

    
    
    # Draw two cols of knights at 4,5,9,10,14,15,...
    # with one open spot on the top half & one in the bottom half.
    for c in range(4,self.cols,5):
      print ""  
      rSkip = random.randint(1, self.rows/2-2) 
      for r in range(1,self.rows/2-1):
        if r != rSkip:
          #print r,c," ",
          self.deleteTerritory(self.getTerritoryName(r,c))
          territoriesDeleted.append([r, c])
          
      rSkip = random.randint(self.rows/2+1, self.rows-2)
      for r in range(self.rows/2+1,self.rows-1):        
        if r != rSkip:
          #print r,c," ",
          self.deleteTerritory(self.getTerritoryName(r,c))
          territoriesDeleted.append([r, c])
      
      c=c+1
      rSkip = random.randint(1, self.rows/2-2)
      for r in range(1,self.rows/2-1):
        if r != rSkip:
          self.deleteTerritory(self.getTerritoryName(r,c))
          territoriesDeleted.append([r, c])
          
      rSkip = random.randint(self.rows/2+1, self.rows-2)
      for r in range(self.rows/2+1,self.rows-1):
        if r != rSkip:
          self.deleteTerritory(self.getTerritoryName(r,c))
          territoriesDeleted.append([r, c])
      
    
    # Draw two rows of knights halfway through the board
    # with 90% coverage.
    r = self.rows/2-1;
    for c in range(self.cols):
      if (random.random() < 0.9):
        self.deleteTerritory(self.getTerritoryName(r,c))
        territoriesDeleted.append([r, c])
        
    r = self.rows/2;
    for c in range(self.cols):
      if (random.random() < 0.9):
        self.deleteTerritory(self.getTerritoryName(r,c))
        territoriesDeleted.append([r, c])

    self.deleteEmptyContinents()
    self.setAllSoleContinentTerritoriesToNeutral()
    self.setNumAttacks(int(ceil(sqrt(self.rows*self.cols))))
    self.setNumFortifies(int(ceil(sqrt(sqrt(self.rows*self.cols)))))

    self.createPNG(filePath, self.rows, self.cols, rowHeight, colWidth, 
                             xOrigin, yOrigin, territoriesDeleted)

    self.saveMapToFile(filePath + ".xml")
    if (self.checkOneTerritoryCanReachAll() == False):
          return False

    return True
 
    
  def createTerritories(self, xOrigin=10, yOrigin=10, xOffset=20, yOffset=20, blackXOffset=-3, blackYOffset=-7, whiteXOffset=3, whiteYOffset=-7):
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
        if ((row+col) % 2 == 0): #black square
          tx = xpos + blackXOffset
          ty = ypos + blackYOffset
        else:
          tx = xpos + whiteXOffset
          ty = ypos + whiteYOffset
          
        self.addTerritory(territoryName, str(tx), str(ty))
        ypos += yOffset
      xpos += xOffset
 
  def genGeoNeighbors(self,territoryID):
    name = self.getTerritoryNameFromID(territoryID)
    (row,col) = name.split("_")     
    print name,row,col
    for x in self.genGeoNeighborsRC(int(row),int(col)):
      yield x
    
      
      
  def genGeoNeighborsRC(self,row,col):
    neighbor = self.getTerritoryIDFromName(self.getTerritoryName(row,col+1))
    if (neighbor != None):
      yield neighbor
      
    neighbor = self.getTerritoryIDFromName(self.getTerritoryName(row,col-1))
    if (neighbor != None):
      yield neighbor
            
    neighbor = self.getTerritoryIDFromName(self.getTerritoryName(row+1,col))
    if (neighbor != None):
      yield neighbor
      
    neighbor = self.getTerritoryIDFromName(self.getTerritoryName(row-1,col))
    if (neighbor != None):
      yield neighbor


  def getRCFromID(self,territoryID):
    name = self.getTerritoryNameFromID(territoryID)
    (row,col) = name.split("_")   
    return [row,col]
  
  def getGeoNeighbors(self,territoryID):  
    (row,col) = self.getRCFromID(territoryID)
    #print name,row,col
    ret = []
    for x in self.genGeoNeighborsRC(int(row),int(col)):
      ret.append(x)
    return ret
    
      
      
  def getGeoNeighborsRC(self,row,col):
    ret = []
    neighbor = self.getTerritoryIDFromName(self.getTerritoryName(row,col+1))
    if (neighbor != None):
      ret.append(neighbor)
      
    neighbor = self.getTerritoryIDFromName(self.getTerritoryName(row,col-1))
    if (neighbor != None):
      ret.append(neighbor)
            
    neighbor = self.getTerritoryIDFromName(self.getTerritoryName(row+1,col))
    if (neighbor != None):
      ret.append(neighbor)
      
    neighbor = self.getTerritoryIDFromName(self.getTerritoryName(row-1,col))
    if (neighbor != None):
      ret.append(neighbor)
    
    return ret
    
  def getNumGeoNeigbors(self, row,col):
    neighbors = 0
    
    neighbor = self.getTerritoryIDFromName(self.getTerritoryName(row,col+1))
    if (neighbor != None):
      neighbors += 1
      
    neighbor = self.getTerritoryIDFromName(self.getTerritoryName(row,col-1))
    if (neighbor != None):
      neighbors += 1
      
    neighbor = self.getTerritoryIDFromName(self.getTerritoryName(row+1,col))
    if (neighbor != None):
      neighbors += 1
      
    neighbor = self.getTerritoryIDFromName(self.getTerritoryName(row-1,col))
    if (neighbor != None):
      neighbors += 1
      

    return neighbors

  def addChainContinents(self,baseIDSet,value=1): #,length=2):
    '''
    # this function adds continent chains.  Just works for length=2 now
    '''
    chains = set()
    for base in baseIDSet:
      ggn = self.getGeoNeighbors(base)
      #print ggn
      for neighbor in ggn:
        chain = frozenset([neighbor, base])        
        chains.add(chain)
                          
    print chains
    for chain in chains:
      name = "chain"
      members = set()
      for link in chain:
        name += "." + self.getTerritoryNameFromID(link)
        members.add(link)
      #print "adding",name
      self.addContinent(name,members,bonus=value)
          

  def removeUselessTerritories(self):
    
    t2d = []
    
    allTerritories = self.getTerritoryIDsFromNameRegex(".*")
    for territory in allTerritories:
      #print "numcont",self.getContinentsWithTerritory(territory)
      if self.getBorderCount(territory) < 2 and len(self.getContinentsWithTerritory(territory)) < 1:
        #print "delete2", territory        
        t2d.append(map(int,self.getRCFromID(territory)))
        self.deleteTerritory(territory)
    #print "T2d",t2d    
    return t2d
        
      
  def isIsthmus(self, row,col):
    
    neighbor = self.getTerritoryIDFromName(self.getTerritoryName(row,col+1))
    #print "neighbor",neighbor
    if (neighbor != None):
      #print "bc",self.getNumGeoNeigbors(row,col+1)
      if (self.getNumGeoNeigbors(row,col+1) == 1):
        return True
      
    neighbor = self.getTerritoryIDFromName(self.getTerritoryName(row,col-1))
    #print "neighbor",neighbor
    if (neighbor != None):
      #print "bc",self.getNumGeoNeigbors(row,col-1)
      if (self.getNumGeoNeigbors(row,col-1) == 1):
        return True
      
    neighbor = self.getTerritoryIDFromName(self.getTerritoryName(row+1,col))
    #print "neighbor",neighbor
    if (neighbor != None):
      #print "bc",self.getNumGeoNeigbors(row+1,col)
      if (self.getNumGeoNeigbors(row+1,col) == 1):
        return True
      
    neighbor = self.getTerritoryIDFromName(self.getTerritoryName(row-1,col))
    #print "neighbor",neighbor
    if (neighbor != None):
      #print "bc",self.getNumGeoNeigbors(row-1,col)
      if (self.getNumGeoNeigbors(row-1,col) == 1):
        return True
      

    return False

  def createRandomGame(self, filePath, rowHeight=45, colWidth=45,
                           percentDeadSquares=.45, xOrigin=-1, yOrigin=-1):
    '''
    returns True if a board was created, False if board creation failed.
    '''
    if xOrigin < 0:
      xOrigin = colWidth/2
    if yOrigin < 0:
      yOrigin = rowHeight/2
    
    print "Creating Random Knight's Tour:",filePath,self.rows,self.cols,rowHeight,colWidth,percentDeadSquares,xOrigin,yOrigin
    
    self.setBoardName("Knight's Tour " + str(self.rows) + "x" + str(self.cols))


    self.deleteAllBorders()
    self.deleteAllTerritories()
    self.deleteAllContinents()
    
    #self.printDOM()

    self.createTerritories(xOrigin, yOrigin, rowHeight, colWidth, blackXOffset=-3, blackYOffset=-7,whiteXOffset=3, whiteYOffset=-7)   
    self.addBordersViaRegex()
    #self.createBlockContinents(1)
    #print "here1",self.DOM.toprettyxml()

    print "Deleting Territories"
    territoriesToDelete = floor(percentDeadSquares*self.rows*self.cols)
    territoriesDeleted = [] 
    while(territoriesToDelete > 0):
      # todo: Can we sort territories in some way to make good boards more likely?
      # 
      row = random.randint(0, self.rows-1)
      col = random.randint(0, self.cols-1)
      # don't use this square if it is one of the two that 
      # attack a corner square
      if ((row == 1 and col == 2) or
          (row == 2 and col == 1) or
          (row == self.rows-2 and col == self.cols-3) or
          (row == self.rows-3 and col == self.cols-2) or
          (row == 1 and col == self.cols-3) or
          (row == 2 and col == self.cols-2) or
          (row == self.rows-2 and col == 2) or
          (row == self.rows-3 and col == 1)):
        #print "skipping",row,col
        continue

      # Also don't use this square if it would create a continent with only
      # one territory in it.
      #if self.getMinContinentSize(self.getTerritoryName(row,col)) <= 2:
        #continue
      
      # don't delete if it would leave a lone territory
      if self.isIsthmus(row,col):
        continue

      if (self.deleteTerritory(self.getTerritoryName(row,col))):
        territoriesToDelete -= 1
        territoriesDeleted.append([row, col])
      #print ".",
      #self.printDOM()
    allTerritories = self.getTerritoryIDsFromNameRegex(".*")
    
    
    #self.setAllSoleContinentTerritoriesToNeutral(neutralBase=2,neutralMultiplier=3)
    
     
    if (self.checkOneTerritoryCanReachAll() == False):
          return False
        
    self.addChainContinents(allTerritories)
    self.setNumAttacks(int(ceil(sqrt(self.rows*self.cols))))
    self.setNumFortifies(int(ceil(sqrt(sqrt(self.rows*self.cols)))))

    print filePath + ".xml"
    self.addViewBordersToNeighbors(2)
    print filePath + ".xml"
    self.createPNGs(filePath, rowHeight, colWidth, 
                             xOrigin, yOrigin, territoriesDeleted)
    print filePath + ".xml"
    self.saveMapToFile(filePath + ".xml")
    print filePath + ".xml"
    #print filePath + ".xml"

    return True
  
  # @todo: territoriesDeleted needs to be handled
  # @todo: change putpixel to the  faster way
  def createPNGs(self, filePath, rowHeight, colWidth, 
                          xOrigin, yOrigin, territoriesDeleted):
    '''
    Creates a PNG of a chessboard w/knights in dead squares..
    '''
    imBoard = Image.new("RGBA", ( self.cols*colWidth,self.rows*rowHeight), (0, 0, 0, 0))
    imFill = Image.new("RGB", ( self.cols*colWidth,self.rows*rowHeight), "white")
    imFog = Image.new("RGB", ( self.cols*colWidth,self.rows*rowHeight), "white")
    
    #print "create new RGB image:", self.cols*colWidth,self.rows*rowHeight
    
    # create fill image
    borderSize = 1; #borderSize = 3; #borders are actually twice this.
    for x in range(self.cols*colWidth):
      for y in range(self.rows*rowHeight):
        row = floor(y/rowHeight)
        col = floor(x/colWidth)
        #print x,y
        #print im.getpixel((x,y))
        #print "putpixel",x,y
        if ((row+col) % 2 == 0): #black square
          if (x - col*colWidth) >=  borderSize and (y - row*rowHeight) >= borderSize and ((col+1)*colWidth - x) >  borderSize and ((row+1)*rowHeight - y) > borderSize:
            imFill.putpixel((x,y), (1, 1, 1)) #off color centers
          else:
            imFill.putpixel((x, y), (0, 0, 0)) 
        else: #white square 
          if (x - col*colWidth) >= borderSize and (y - row*rowHeight) >= borderSize and ((col+1)*colWidth - x) >  borderSize and ((row+1)*rowHeight - y) > borderSize:
            imFill.putpixel((x,y), (254, 254, 254)) #off color centers
          else:
            imFill.putpixel((x, y), (255, 255, 255)) 


    print "pasting"
    #paste in the un/deleted territories to the Board Image
    knightBorder=0
    print "territoriesDeleted", territoriesDeleted
    for col in range(self.cols):
      for row in range(self.rows):
        print territoriesDeleted
        print [ (r,c) for (r,c) in territoriesDeleted]
        found = [(r,c) for (r,c) in territoriesDeleted if r == row if c == col]
        print "found",found
        if found:
          print "found hole!"
          if ((row+col) % 2 == 0): #black square
            tileImage = self.holeDarkImage     
          else:
            tileImage = self.holeLightImage
        else:
          if ((row+col) % 2 == 0): #black square
            tileImage = self.playerDarkImage
            #tileFImage = self.playerDarkFogImage
          else:
            tileImage = self.playerLightImage
            #tileFImage = self.playerLightFogImage
          
        px = col*colWidth + knightBorder
        py = row*rowHeight + knightBorder
        imBoard.paste(tileImage, (px, py))
        
    
        
    #fog now
    for col in range(self.cols):
      for row in range(self.rows):              
        if ((row+col) % 2 == 0): #black square
          tileImage = self.darkFogImage
        else:
          tileImage = self.lightFogImage
                
        px = col*colWidth
        py = row*rowHeight

        imFog.paste(tileImage, (px, py))    


    imBoard.save(filePath + "-BOARD.png")
    imFill.save(filePath + "-FILLFOG.png")
    imFog.save(filePath+ "-FOG.png")
    
  def create1LayerPNG(self, filePath, rowHeight, colWidth, 
                          xOrigin, yOrigin, territoriesDeleted):
    '''
    Creates a PNG of a chessboard w/knights in dead squares..
    '''
    im = Image.new("RGB", ( self.cols*colWidth,self.rows*rowHeight), "white")
    #print "create new RGB image:", self.cols*colWidth,self.rows*rowHeight
    # @todo: these should all be rowHeight
    borderSize = 10; #borderSize = 3; #borders are actually twice this.
    for x in range(self.cols*colWidth):
      for y in range(self.rows*rowHeight):
        row = floor(y/rowHeight)
        col = floor(x/colWidth)
        #print x,y
        #print im.getpixel((x,y))
        #print "putpixel",x,y
        if ((row+col) % 2 == 0): #black square
          if (x - col*colWidth) >=  borderSize and (y - row*rowHeight) >= borderSize and ((col+1)*colWidth - x) >  borderSize and ((row+1)*rowHeight - y) > borderSize:
            im.putpixel((x,y), (1, 1, 1)) #off color centers
          else:
            im.putpixel((x, y), (0, 0, 0)) 
        else: #white square 
          if (x - col*colWidth) >= borderSize and (y - row*rowHeight) >= borderSize and ((col+1)*colWidth - x) >  borderSize and ((row+1)*rowHeight - y) > borderSize:
            im.putpixel((x,y), (245, 254, 254)) #off color centers
          else:
            im.putpixel((x, y), (255, 255, 255)) 


    #paste in the knight icons to the deleted territories
    knightborder=3
    for territory in territoriesDeleted:
      (delr, delc) = territory
      px = delc*colWidth
      py = delr*rowHeight
      if ((delr+delc) % 2 == 0): #black square
        im.paste(self.whiteKnightImage, (px+knightborder, py+knightborder)) 
      else:
        im.paste(self.blackKnightImage, (px+knightborder, py+knightborder)) 


    # add some text  
    #draw = ImageDraw.Draw(im)
    # use a truetype font
    #font = ImageFont.truetype("//BHO/data/wargear development/scripts/nayla.ttf", 15)

    #draw.text((10, 25), "TESETING world TSETING", font=font)



    im.save(filePath + ".png")


  # todo: maybe create knights tour config object
  def setKnightIcons(self, wkpath, bkpath):
    ''' 
    setter
    TODO: It would be great if rowHeight & colWidth were class members (instance variables), and were set 
      by the width/height of these images.
    '''
    self.whiteKnightImage = Image.open(wkpath)
    self.blackKnightImage = Image.open(bkpath)
    
    
  def setMoreKnightIcons(self, playerLightImagePath, playerDarkImagePath, holeLightPath, holeDarkPath):
    ''' 
    setter
    TODO: It would be great if rowHeight & colWidth were class members (instance variables), and were set 
      by the width/height of these images.
    '''

    self.holeDarkImage = Image.open(holeDarkPath)
    self.holeLightImage = Image.open(holeLightPath)
    self.playerDarkImage = Image.open(playerDarkImagePath)
    self.playerLightImage = Image.open(playerLightImagePath)

  def setMoreerKnightIcons(self, playerLightImagePath, playerDarkImagePath, holeLightPath, holeDarkPath, lightImageFogPath, darkImageFogPath, ):
    ''' 
    setter
    TODO: It would be great if rowHeight & colWidth were class members (instance variables), and were set 
      by the width/height of these images.
    '''

    self.holeDarkImage = Image.open(holeDarkPath)
    self.holeLightImage = Image.open(holeLightPath)
    self.playerDarkImage = Image.open(playerDarkImagePath)
    self.playerLightImage = Image.open(playerLightImagePath)
    self.darkFogImage = Image.open(darkImageFogPath)
    self.lightFogImage = Image.open(lightImageFogPath)
    

def addKnightViewBorders():
  wgmap = WGMap()
  
  wgmap.loadMapFromFile('//DISKSTATION/data/wargear development/Knights Tour/Knights Tour NxN - 20x20 - Random.xml')
  wgmap.addViewBordersToNeighbors(2)
  wgmap.saveMapToFile('//DISKSTATION/data/wargear development/Knights Tour/Knights Tour NxN - 20x20 - Random - Out.xml',False)
  

  '''
  wgmap.loadMapFromFile('//DISKSTATION/data/wargear development/Knights Tour/Knights Tour NxN - 25x4 - Random.xml')
  wgmap.addViewBordersTo2Neighbors()
  wgmap.saveMapToFile('//DISKSTATION/data/wargear development/Knights Tour/Knights Tour NxN - 25x4 - Random - Out.xml',False)
  
  wgmap.loadMapFromFile('//DISKSTATION/data/wargear development/Knights Tour/Knights Tour NxN - 26x6 - Stripes.xml')
  wgmap.addViewBordersTo2Neighbors()
  wgmap.saveMapToFile('//DISKSTATION/data/wargear development/Knights Tour/Knights Tour NxN - 26x6 - Stripes - Out.xml',False)
  
  wgmap.loadMapFromFile('//DISKSTATION/data/wargear development/Knights Tour/Knights Tour NxN - 25x6 - Random.xml')
  wgmap.addViewBordersTo2Neighbors()
  wgmap.saveMapToFile('//DISKSTATION/data/wargear development/Knights Tour/Knights Tour NxN - 25x6 - Random.xml',False)
  
  wgmap.loadMapFromFile('//DISKSTATION/data/wargear development/Knights Tour/Knights Tour NxN - 20x21 - Cells.xml')
  wgmap.addViewBordersTo2Neighbors()
  wgmap.saveMapToFile('//DISKSTATION/data/wargear development/Knights Tour/Knights Tour NxN - 20x21 - Cells - Out.xml',False)
  
  wgmap.loadMapFromFile('//DISKSTATION/data/wargear development/Knights Tour/Knights Tour NxN - 20x20 - Snake.xml')
  wgmap.addViewBordersTo2Neighbors()
  wgmap.saveMapToFile('//DISKSTATION/data/wargear development/Knights Tour/Knights Tour NxN - 20x20 - Snake - Out.xml',False)
  
  wgmap.loadMapFromFile('//DISKSTATION/data/wargear development/Knights Tour/Knights Tour NxN - 19x19 - Grid.xml')
  wgmap.addViewBordersTo2Neighbors()
  wgmap.saveMapToFile('//DISKSTATION/data/wargear development/Knights Tour/Knights Tour NxN - 19x19 - Grid - Out.xml',False)
  
  wgmap.loadMapFromFile('//DISKSTATION/data/wargear development/Knights Tour/Knights Tour NxN - 16x16 - Stripes.xml')
  wgmap.addViewBordersTo2Neighbors()
  wgmap.saveMapToFile('//DISKSTATION/data/wargear development/Knights Tour/Knights Tour NxN - 16x16 - Stripes - Out.xml',False)
  
  wgmap.loadMapFromFile('//DISKSTATION/data/wargear development/Knights Tour/Knights Tour NxN - 16x16 - Snake.xml')
  wgmap.addViewBordersTo2Neighbors()
  wgmap.saveMapToFile('//DISKSTATION/data/wargear development/Knights Tour/Knights Tour NxN - 16x16 - Snake - Out.xml',False)
  
  wgmap.loadMapFromFile('//DISKSTATION/data/wargear development/Knights Tour/Knights Tour NxN - 16x16 - Random.xml')
  wgmap.addViewBordersTo2Neighbors()
  wgmap.saveMapToFile('//DISKSTATION/data/wargear development/Knights Tour/Knights Tour NxN - 16x16 - Random - Out.xml',False)
  
  wgmap.loadMapFromFile('//DISKSTATION/data/wargear development/Knights Tour/Knights Tour NxN - 16x16 - Grid.xml')
  wgmap.addViewBordersTo2Neighbors()
  wgmap.saveMapToFile('//DISKSTATION/data/wargear development/Knights Tour/Knights Tour NxN - 16x16 - Grid - Out.xml',False)
  
  wgmap.loadMapFromFile('//DISKSTATION/data/wargear development/Knights Tour/Knights Tour NxN - 16x15 - Cells.xml')
  wgmap.addViewBordersTo2Neighbors()
  wgmap.saveMapToFile('//DISKSTATION/data/wargear development/Knights Tour/Knights Tour NxN - 16x15 - Cells - Out.xml',False)
  
  wgmap.loadMapFromFile('//DISKSTATION/data/wargear development/Knights Tour/Knights Tour NxN - 13x13 - Grid.xml')
  wgmap.addViewBordersTo2Neighbors()
  wgmap.saveMapToFile('//DISKSTATION/data/wargear development/Knights Tour/Knights Tour NxN - 13x13 - Grid - Out.xml',False)
  
  wgmap.loadMapFromFile('//DISKSTATION/data/wargear development/Knights Tour/Knights Tour NxN - 12x12 - Snake.xml')
  wgmap.addViewBordersTo2Neighbors()
  wgmap.saveMapToFile('//DISKSTATION/data/wargear development/Knights Tour/Knights Tour NxN - 12x12 - Snake - Out.xml',False)
  
  wgmap.loadMapFromFile('//DISKSTATION/data/wargear development/Knights Tour/Knights Tour NxN - 12x12 - Random.xml')
  wgmap.addViewBordersTo2Neighbors()
  wgmap.saveMapToFile('//DISKSTATION/data/wargear development/Knights Tour/Knights Tour NxN - 12x12 - Random - Out.xml',False)
  
  wgmap.loadMapFromFile('//DISKSTATION/data/wargear development/Knights Tour/Knights Tour NxN - 10x10 - Random.xml')
  wgmap.addViewBordersTo2Neighbors()
  wgmap.saveMapToFile('//DISKSTATION/data/wargear development/Knights Tour/Knights Tour NxN - 10x10 - Random - Out.xml',False)
  '''

def createRandomKnightTour():
  ''' Create a Knight Tour's map '''
  wgmap = KnightWGMap()
  wgmap.loadMapFromFile('//DISKSTATION/data/wargear development/Knights Tour/Knight\'s Tour(1).xml')
  #  wgmap.setKnightIcons('//DISKSTATION/data/wargear development/Knights Tour/WhiteKnightIcon34.png',
  #                     '//DISKSTATION/data/wargear development/Knights Tour/BlackKnightIcon34.png')

  wgmap.setKnightIcons('//DISKSTATION/data/wargear development/Knights Tour/Parquet1.png',
                       '//DISKSTATION/data/wargear development/Knights Tour/Parquet2.png')


  wgmap.setMoreKnightIcons( '//DISKSTATION/data/wargear development/Knights Tour/PlayerKnightLightWood45.png',
                            '//DISKSTATION/data/wargear development/Knights Tour/PlayerKnightDarkWood45.png',
                            '//DISKSTATION/data/wargear development/Knights Tour/WoodWhite45.png',
                            '//DISKSTATION/data/wargear development/Knights Tour/WoodBlack45.png'
                            )
  wgmap.setMoreerKnightIcons( '//DISKSTATION/data/wargear development/Knights Tour/PlayerKnightLightWood45.png',
                            '//DISKSTATION/data/wargear development/Knights Tour/PlayerKnightDarkWood45.png',
                            '//DISKSTATION/data/wargear development/Knights Tour/DeadKnightLight.png',
                            '//DISKSTATION/data/wargear development/Knights Tour/DeadKnightDark.png',
                            '//DISKSTATION/data/wargear development/Knights Tour/WoodWhite45.png',
                            '//DISKSTATION/data/wargear development/Knights Tour/WoodBlack45.png'                    
                            )
  wgmap.setMoreerKnightIcons( '//DISKSTATION/data/wargear development/Knights Tour/PlayerKnightLightWood45.png',
                            '//DISKSTATION/data/wargear development/Knights Tour/PlayerKnightDarkWood45.png',
                            '//DISKSTATION/data/wargear development/Knights Tour/WoodWhite45.png',
                            '//DISKSTATION/data/wargear development/Knights Tour/WoodBlack45.png' ,                            
                            '//DISKSTATION/data/wargear development/Knights Tour/WoodBlack45.png',
                            '//DISKSTATION/data/wargear development/Knights Tour/WoodWhite45.png'                  
                            )
  wgmap.rows = 8
  wgmap.cols = 8

  numAttempts = 0
  while (numAttempts < 200):  
    if (wgmap.createRandomGame(
        "//DISKSTATION/data/wargear development/Knights Tour/KnightsTour")):
      print "succesfully created a map :^) after", numAttempts+1,"attempts"
      break
    else:
      print "map creation failed. :^( ----  ATTEMPT: ",numAttempts+1
    numAttempts+=1
    
def createCellsKnightTour():
  ''' Create a Knight Tour's map '''
  wgmap = KnightWGMap()
  
  wgmap.loadMapFromFile('//DISKSTATION/data/wargear development/Knights Tour/Knight\'s Tour(1).xml')
  wgmap.setMoreerKnightIcons( '//DISKSTATION/data/wargear development/Knights Tour/PlayerKnightLightWood45.png',
                            '//DISKSTATION/data/wargear development/Knights Tour/PlayerKnightDarkWood45.png',
                            '//DISKSTATION/data/wargear development/Knights Tour/WoodWhite45.png',
                            '//DISKSTATION/data/wargear development/Knights Tour/WoodBlack45.png' ,                            
                            '//DISKSTATION/data/wargear development/Knights Tour/WoodBlack45.png',
                            '//DISKSTATION/data/wargear development/Knights Tour/WoodWhite45.png'                  
                            )

  wgmap.rows = 12
  wgmap.cols = 24
 
  if wgmap.createFunctionGame("//DISKSTATION/data/wargear development/Knights Tour/KnightsTour",
                              wgmap.placeCells):    
#  if (wgmap.createCellsGame(
#      "//BHO/data/wargear development/Knights Tour/KnightsTour")):
    print "succesfully created a map :^)"
  else:
    print "map creation failed. :^( "

def createVerticalStripesKnightsTour():
  ''' Create a Knight Tour's map '''
  wgmap = KnightWGMap()
  wgmap.loadMapFromFile('//DISKSTATION/data/wargear development/Knights Tour/Knights Tour NxN - 16x16 - Stripes.xml')
  wgmap.setKnightIcons('//DISKSTATION/data/wargear development/Knights Tour/WhiteKnightIcon34.png',
                       '//DISKSTATION/data/wargear development/Knights Tour/BlackKnightIcon34.png')

  wgmap.rows = 16
  wgmap.cols = 16
  numAttempts = 0
  while (numAttempts < 20):
    if (wgmap.createFunctionGame(
                                 "//DISKSTATION/data/wargear development/Knights Tour/KnightsTour",wgmap.placeRandomVerticalStripes)):
      print "succesfully created a map :^) after", numAttempts+1,"attempts"
      break
    else:
      print "map creation failed. :^( ----  ATTEMPT: ",numAttempts+1
    numAttempts+=1


def createSnakesGame():
  ''' Create a Knight Tour's map '''
  wgmap = KnightWGMap()
  wgmap.loadMapFromFile('//DISKSTATION/data/wargear development/Knights Tour/Knights Tour NxN - 20^2 - Random Snake.xml')
  wgmap.setKnightIcons('//DISKSTATION/data/wargear development/Knights Tour/WhiteKnightIcon34.png',
                       '//DISKSTATION/data/wargear development/Knights Tour/BlackKnightIcon34.png')

  wgmap.rows = 20
  wgmap.cols = 20

  numAttempts = 0
  while (numAttempts < 20):
    if (wgmap.createFunctionGame(
                                 "//BHO/data/wargear development/Knights Tour/KnightsTour",wgmap.placeRandomSnake)):
      print "succesfully created a map :^) after", numAttempts+1,"attempts"
      break
    else:
      print "map creation failed. :^( ----  ATTEMPT: ",numAttempts+1
    numAttempts+=1

def createFunctionCellGame():
  ''' Create a Knight Tour's map '''
  wgmap = KnightWGMap()
  wgmap.loadMapFromFile('//DISKSTATION/data/wargear development/Knights Tour/Knight\'s Tour(1).xml')
  wgmap.setMoreerKnightIcons( '//DISKSTATION/data/wargear development/Knights Tour/PlayerKnightLightWood45.png',
                            '//DISKSTATION/data/wargear development/Knights Tour/PlayerKnightDarkWood45.png',
                            '//DISKSTATION/data/wargear development/Knights Tour/WoodWhite45.png',
                            '//DISKSTATION/data/wargear development/Knights Tour/WoodBlack45.png' ,                            
                            '//DISKSTATION/data/wargear development/Knights Tour/WoodBlack45.png',
                            '//DISKSTATION/data/wargear development/Knights Tour/WoodWhite45.png'                  
                            )

  wgmap.rows = 11
  wgmap.cols = 18

  numAttempts = 0
  while (numAttempts < 30):
    if (wgmap.createFunctionGame(
                                 "//DISKSTATION/data/wargear development/Knights Tour/KnightsTour",wgmap.placeCells)):
      print "succesfully created a map :^) after", numAttempts+1,"attempts"
      break
    else:
      print "map creation failed. :^( ----  ATTEMPT: ",numAttempts+1
    numAttempts+=1

def createFunctionFourSquareGame():
  ''' Create a Knight Tour's map '''
  wgmap = KnightWGMap()
  wgmap.loadMapFromFile('//DISKSTATION/data/wargear development/Knights Tour/Knight\'s Tour(1).xml')
  wgmap.setMoreerKnightIcons( '//DISKSTATION/data/wargear development/Knights Tour/PlayerKnightLightWood45.png',
                            '//DISKSTATION/data/wargear development/Knights Tour/PlayerKnightDarkWood45.png',
                            '//DISKSTATION/data/wargear development/Knights Tour/WoodWhite45.png',
                            '//DISKSTATION/data/wargear development/Knights Tour/WoodBlack45.png' ,                            
                            '//DISKSTATION/data/wargear development/Knights Tour/WoodBlack45.png',
                            '//DISKSTATION/data/wargear development/Knights Tour/WoodWhite45.png'                  
                            )

  wgmap.rows = 15
  wgmap.cols = 15

  numAttempts = 0
  while (numAttempts < 30):
    if (wgmap.createFunctionGame(
                                 "//DISKSTATION/data/wargear development/Knights Tour/KnightsTour",wgmap.placeFourSquare)):
      print "succesfully created a map :^) after", numAttempts+1,"attempts"
      break
    else:
      print "map creation failed. :^( ----  ATTEMPT: ",numAttempts+1
    numAttempts+=1

def createStripesGame():
  ''' Create a Knight Tour's map '''
  wgmap = KnightWGMap()
  wgmap.loadMapFromFile('//DISKSTATION/data/wargear development/Knights Tour/Knight\'s Tour(1).xml')
  wgmap.setMoreerKnightIcons( '//DISKSTATION/data/wargear development/Knights Tour/PlayerKnightLightWood45.png',
                            '//DISKSTATION/data/wargear development/Knights Tour/PlayerKnightDarkWood45.png',
                            '//DISKSTATION/data/wargear development/Knights Tour/WoodWhite45.png',
                            '//DISKSTATION/data/wargear development/Knights Tour/WoodBlack45.png' ,                            
                            '//DISKSTATION/data/wargear development/Knights Tour/WoodBlack45.png',
                            '//DISKSTATION/data/wargear development/Knights Tour/WoodWhite45.png'                  
                            )

  wgmap.rows = 16
  wgmap.cols = 25

  numAttempts = 0
  while (numAttempts < 30):
    if (wgmap.createFunctionGame(
                                 "//DISKSTATION/data/wargear development/Knights Tour/KnightsTour",wgmap.placeStripes)):
      print "succesfully created a map :^) after", numAttempts+1,"attempts"
      break
    else:
      print "map creation failed. :^( ----  ATTEMPT: ",numAttempts+1
    numAttempts+=1

def createGridGame():
  ''' Create a Knight Tour's map '''
  wgmap = KnightWGMap()
  wgmap.loadMapFromFile('//BHO/data/wargear development/Knights Tour/Knights Tour NxN - 12x12 - Grid.xml')
  wgmap.setKnightIcons('//BHO/data/wargear development/Knights Tour/WhiteKnightIcon34.png',
                       '//BHO/data/wargear development/Knights Tour/BlackKnightIcon34.png')

  wgmap.rows = 13
  wgmap.cols = 13

  numAttempts = 0
  while (numAttempts < 1):
    if (wgmap.createFunctionGame(
                                 "//BHO/data/wargear development/Knights Tour/KnightsTour",wgmap.placeGrid)):
      print "succesfully created a map :^) after", numAttempts+1,"attempts"
      break
    else:
      print "map creation failed. :^( ----  ATTEMPT: ",numAttempts+1
    numAttempts+=1


if __name__ == '__main__':
  pass