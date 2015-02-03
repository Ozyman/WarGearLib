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

from General import SquareGridWGMap

class MazeWGMap(SquareGridWGMap):
  """
  Extends the SquareGridWGMap.
  Creates a 'maze map' in which players
  gain bonuses for completing a row or column
  """
  
  
  def __init__(self):
    """Constructor"""
    super(MazeWGMap,self).__init__()

    self.setDefaultParameters()

  def setDefaultParameters(self):
    self.branchingFactor = .3  #Fraction of growth points that will branch
    self.connectionRejection = .8  # % chance a connection from a growth point to a territory w/borders will be retried
    self.chanceToDeadEnd = .4 #Fraction of times a connection from gp to territory w/borders will dead end vs. joining up (assuming !connectionRejected)
  
  
  def setOpenParameters(self):
    self.branchingFactor = .4  #Fraction of growth points that will branch
    self.connectionRejection = .8  # % chance a connection from a growth point to a territory w/borders will be retried
    self.chanceToDeadEnd = .33 #Fraction of times a connection from gp to territory w/borders will dead end vs. joining up (assuming !connectionRejected)
  
  def setWideOpenParameters(self):
    self.branchingFactor = .6  #Fraction of growth points that will branch
    self.connectionRejection = .7  # % chance a connection from a growth point to a territory w/borders will be retried
    self.chanceToDeadEnd = .25 #Fraction of times a connection from gp to territory w/borders will dead end vs. joining up (assuming !connectionRejected)
  
  def setTightParameters(self):
    self.branchingFactor = .2  #Fraction of growth points that will branch
    self.connectionRejection = .92  # % chance a connection from a growth point to a territory w/borders will be retried
    self.chanceToDeadEnd = .6 #Fraction of times a connection from gp to territory w/borders will dead end vs. joining up (assuming !connectionRejected)
   
  def setTighterParameters(self):
    self.branchingFactor = .15  #Fraction of growth points that will branch
    self.connectionRejection = .94  # % chance a connection from a growth point to a territory w/borders will be retried
    self.chanceToDeadEnd = .7 #Fraction of times a connection from gp to territory w/borders will dead end vs. joining up (assuming !connectionRejected)
    
  
  def cleanupFourSquares(self):
    
    for r in range(self.rows):
      for c in range(self.cols):
        ulID = self.getTerritoryIDFromName(self.getTerritoryName(r,c))
        blID = self.getTerritoryIDFromName(self.getTerritoryName(r+1,c))
        urID = self.getTerritoryIDFromName(self.getTerritoryName(r,c+1))
        lrID = self.getTerritoryIDFromName(self.getTerritoryName(r+1,c+1))
        
        if self.doTheyBorder(ulID,blID) and self.doTheyBorder(ulID,urID) and self.doTheyBorder(lrID,urID) and self.doTheyBorder(lrID,blID):
          #print "cleaning up a 4-square at",r,c
          #pick a random border to remove.
          rnd = random.random()
          if rnd < .25:
            self.deleteBorder(ulID,blID)        
          elif rnd < .5:
            self.deleteBorder(ulID,urID)          
          elif rnd < .75:
            self.deleteBorder(lrID,urID)          
          else:
            self.deleteBorder(lrID,blID)          
 
  def addContinents(self,valueFunction=None):
    
    def divideByTwo(n):
      return n/2
    
    if valueFunction == None:
      valueFunction = divideByTwo
      
      
    colContinents = 0
    for r in range(self.rows):
      for c in range(self.cols):        
        centerID = self.getTerritoryIDFromName(self.getTerritoryName(r,c))
        aboveID =  self.getTerritoryIDFromName(self.getTerritoryName(r-1,c))
        # if there a border above, we have done this column continent already      
        if(not self.doTheyBorder(centerID,aboveID)):
          #print "starting a column at ",centerID,r,c
          membersList = str(centerID)        
          rBelow=r+1
          prevBelowID = centerID
          belowID = self.getTerritoryIDFromName(self.getTerritoryName(rBelow,c))
          contLength = 1
          # Find the extent of the column          
          while self.doTheyBorder(belowID,prevBelowID):
            #print "continuing a column at ",belowID,rBelow,c 
            membersList += ","  + belowID
            contLength += 1
            rBelow += 1
            prevBelowID = belowID
            belowID = self.getTerritoryIDFromName(self.getTerritoryName(rBelow,c))
          
          if (contLength > 1):
            self.addContinent("Column "+str(colContinents),membersList,valueFunction(contLength))
            colContinents += 1
          
    rowContinents = 0
    for r in range(self.rows):
      for c in range(self.cols):        
        centerID = self.getTerritoryIDFromName(self.getTerritoryName(r,c))
        leftID =  self.getTerritoryIDFromName(self.getTerritoryName(r,c-1))
        # if there a border above, we have done this column continent already      
        if(not self.doTheyBorder(centerID,leftID)):
          membersList = str(centerID)        
          cRight=c+1
          prevRightID = centerID
          rightID = self.getTerritoryIDFromName(self.getTerritoryName(r,cRight))
          contLength = 1
          # Find the extent of the column          
          while self.doTheyBorder(rightID,prevRightID):
            membersList += ","  + rightID
            contLength += 1
            cRight += 1
            prevRightID = rightID
            rightID = self.getTerritoryIDFromName(self.getTerritoryName(r,cRight))
          
          if (contLength > 1):
            self.addContinent("Row "+str(rowContinents),membersList,valueFunction(contLength))
            rowContinents += 1
       
            
                                
  
  
  def createMazeGame(self,filePath,rowHeight=40,colWidth=40):
    '''Be sure to set the board name by hand'''
    
    xOrigin = colWidth/2
    yOrigin = rowHeight/2
    
    print "Maze (" + str(self.rows) + "x" + str(self.cols) + ")"#+str(placeKnightFunc)
    print filePath
    self.deleteAllBorders()
    self.deleteAllTerritories()
    self.deleteAllContinents()

    #self.setBoardName("Knight's Tour (" + str(rows) + "x" + str(cols) + ")")
    
    self.createTerritories(xOrigin, yOrigin, rowHeight, colWidth)
       
    self.fillWithRandomWalk()
    
    
    returnValue = self.connectSeperateGroups()
    self.cleanupFourSquares()
    
    self.addContinents()
    self.setNumFortifies(int(ceil(sqrt(self.rows*self.cols))))
    self.setEliminationBonus(int(ceil(sqrt(self.rows*self.cols))))
    self.setMaxCards(2+int(ceil(sqrt(sqrt(self.rows*self.cols)))))
    
    self.createPNG(filePath, rowHeight, colWidth)


    self.saveMapToFile(filePath + ".xml")
    
    bc = self.getBorderCounts()
    for BName,BCount in bc.iteritems():
      if BCount > 4:
        print BName,"has",BCount,"borders!!"

    return returnValue
  
  

  # @todo: change putpixel to the  faster way
  def createPNG(self, filePath, rowHeight, colWidth):
    '''
    Creates a PNG of a maze with walls
    '''
    im = Image.new("RGB", ( self.cols*colWidth,self.rows*rowHeight), "white")
    #print "create new RGB image:", self.cols*colWidth,self.rows*rowHeight
    # @todo: these should all be rowHeight

    wallHalfWidth=2
    
    def safePutPixel(xy,rgb):
      (x,y) = xy
      #(r,g,b) = rgb
      if (x < 0 or x >= self.cols*colWidth):
        return
      if (y < 0 or y >= self.rows*rowHeight):
        return
      im.putpixel(xy, rgb)
      
    
    def drawRightWall(fromR, fromC):
      if (fromC == self.cols-1):
        whw = wallHalfWidth*2
      else:
        whw = wallHalfWidth
      for y in range(fromR*rowHeight-wallHalfWidth,(fromR+1)*rowHeight+wallHalfWidth+1):
        for x in range((fromC+1)*colWidth-whw,(fromC+1)*colWidth+whw+1):
          safePutPixel((x,y), (0,0,0))
    
    def drawBottomWall(fromR, fromC):
      if (fromR == self.rows-1):
        whw = wallHalfWidth*2
      else:
        whw = wallHalfWidth
      for x in range(fromC*colWidth-wallHalfWidth,(fromC+1)*colWidth+wallHalfWidth+1):
        for y in range((fromR+1)*rowHeight-whw,(fromR+1)*rowHeight+whw+1):
          safePutPixel((x,y), (0,0,0))

    def drawLeftWall(fromR, fromC):
      if (fromC == 0):
        whw = wallHalfWidth*2-1
      else:
        whw = wallHalfWidth
        
      for y in range(fromR*rowHeight-wallHalfWidth,(fromR+1)*rowHeight+wallHalfWidth+1):
        for x in range((fromC)*colWidth-whw,(fromC)*colWidth+whw+1):
          safePutPixel((x,y), (0,0,0))
    
    def drawTopWall(fromR, fromC):
      if (fromR == 0):
        whw = wallHalfWidth*2-1
      else:
        whw = wallHalfWidth
      for x in range(fromC*colWidth-wallHalfWidth,(fromC+1)*colWidth+wallHalfWidth+1):
        for y in range((fromR)*rowHeight-whw,(fromR)*rowHeight+whw+1):
          safePutPixel((x,y), (0,0,0))

    def drawEdgeBorders():
      for y in range(self.rows*rowHeight):
        x = 0
        safePutPixel((x, y), (128, 128, 128))
        x = self.cols*colWidth-1
        safePutPixel((x, y), (128, 128, 128))
      for x in range(self.cols*colWidth):
        y = 0
        safePutPixel((x, y), (128, 128, 128))
        y = self.rows*rowHeight-1
        safePutPixel((x, y), (128, 128, 128))
        
      
        
    #draw in grey lines between each square for continent borders. 
    for col in range(self.cols):      
      for y in range(self.rows*rowHeight):
        row = floor(y/rowHeight)
        x = col*colWidth
        #print x,y
        #print im.getpixel((x,y))
        #print "putpixel",x,y
        if (col != 0):     
          safePutPixel((x, y), (128, 128, 128))
        
    for row in range(self.rows):      
      for x in range(self.cols*colWidth):
        col = floor(x/colWidth)
        y = row*rowHeight
        #print x,y
        #print im.getpixel((x,y))
        #print "putpixel",x,y
        if (row != 0):
          safePutPixel((x, y), (128, 128, 128))
        
    drawEdgeBorders()     


    # fill in strong borders on top 
    for c in range(self.cols):
      topID = self.getTerritoryIDFromName(self.getTerritoryName(0,c))
      bottomID = self.getTerritoryIDFromName(self.getTerritoryName(self.rows-1,c))
      if(not self.doTheyBorder(topID,bottomID)):
        #print "border between",self.getTerritoryName(r,c),self.getTerritoryName(r+1,c)
        drawTopWall(0,c)
      
    # & left sides
    for r in range(self.rows):
      leftID = self.getTerritoryIDFromName(self.getTerritoryName(r,0))
      rightID = self.getTerritoryIDFromName(self.getTerritoryName(r,self.cols-1))
      if(not self.doTheyBorder(leftID,rightID)):
        #print "border between",self.getTerritoryName(r,c),self.getTerritoryName(r+1,c)
        drawLeftWall(r,0)
      
    
    # draw the rest of the walls
    for r in range(self.rows):
      for c in range(self.cols):
        centerID = self.getTerritoryIDFromName(self.getTerritoryName(r,c))
        rightID =  self.getTerritoryIDFromName(self.getTerritoryName(r,c+1))
        bottomID =  self.getTerritoryIDFromName(self.getTerritoryName(r+1,c))
        if(not self.doTheyBorder(centerID,rightID)):
          #print "border between",self.getTerritoryName(r,c),self.getTerritoryName(r,c+1)        
          drawRightWall(r,c)
        if(not self.doTheyBorder(centerID,bottomID)):
          #print "border between",self.getTerritoryName(r,c),self.getTerritoryName(r+1,c)
          drawBottomWall(r,c)
          
          
      
         
         
        

    # add some text  
    #draw = ImageDraw.Draw(im)
    # use a truetype font
    #font = ImageFont.truetype("//BHO/data/wargear development/scripts/nayla.ttf", 15)

    #draw.text((10, 25), "TESETING world TSETING", font=font)



    im.save(filePath + ".png")

  def fillWithRandomWalk(self):
    
    self.addRandomWalk(-1,-1)
    while(self.countTerritoriesWithBorders(0) > 0):
      self.addRandomWalk(-2,-2)

  def addRandomWalk(self,r,c):
    """
    adds a maze starting at r,c
    if r & c are -2, a territory with no borders is found (if it exists), and the random walk is started there.
    otherwise if r or c is negative, they are set to the middle of the map.
    
    todo: This seems to hang on a rare occasion (recursion to infinity).  What is happening?  Does it get stuck in a corner somehow?
           Also a problem, it can get called with no r,c more than once, and we start again at the same place...
           
           Also somehow (maybe related to above), I am seeing the same border created multiple times.  
            The example I saw had 4 copies of the border from tid: 0 to tid: 1.  
            ah, but is it actually created multiple times.  I think addBorder, checks & will not create.
    """

    # set r & c to a zero-border territory    
    if r == -2 or c == -2:
      startingTerritory = self.getATerritoryWithNBorders(0)
      (r,c) = self.getRC(startingTerritory)
      r = int(r)
      c = int(c)
      print "found a new starting spot at",r,c 
    
    
    if (r < 0 or c < 0):
      print "r,c < 0 ?!?!?"
      r = self.rows/2
      c = self.cols/2
    
    growthPoints = set()
    
    growthPoints.add((r, c))
    
    def attemptTerritoryAdd(rFrom,cFrom,rTo,cTo):
      #if not self.inBorders((rTo, cTo)):
      #  return
      #rTo = self.wrapR(rTo)
      #cTo = self.wrapC(cTo)
      fromTerritory = self.getTerritoryElement((rFrom,cFrom))
      toTerritory = self.getTerritoryElement((rTo, cTo))
      fromBorders = self.getBorderCount(fromTerritory.getAttribute("tid"))
      print "base has borders:",fromBorders
      
      print "attempting",rFrom,cFrom,rTo,cTo
      if (toTerritory != None):
        toBorders = self.getBorderCount(toTerritory.getAttribute("tid"))
        print "target has borders:",toBorders
        if (toBorders > 0):
          if random.random() < self.connectionRejection:
            growthPoints.add((rFrom,cFrom))  #add this point back again for another try
            print "try again from {},{}".format(rFrom,cFrom)
          else:             
            if  random.random() > self.chanceToDeadEnd:
              if not self.addBorder((rFrom, cFrom),(rTo, cTo)): #border already existed
                if fromBorders < 3:
                  growthPoints.add((rFrom,cFrom))
                  print "added new border from {},{} to {},{} - continuing".format(rFrom, cFrom,rTo, cTo)
                print "border already existed from {},{} to {},{}".format(rFrom, cFrom,rTo, cTo)
              print "random deadend"
        else:
          self.addBorder((rFrom, cFrom),(rTo, cTo))
          growthPoints.add((rTo,cTo))
          print "added new border from {},{} to {},{} - autocontinue".format(rFrom, cFrom,rTo, cTo)
          if random.random() < self.branchingFactor:
              growthPoints.add((rFrom,cFrom))
              print "adding {},{} as growth point".format(rFrom, cFrom)
              
      else:
        # add growth point back on, if we couldn't grow from here.
        growthPoints.add((rFrom,cFrom))
        print "try again from {},{}".format(rFrom,cFrom)
                      
    
    while(len(growthPoints) > 0):      
      (rF, cF) = growthPoints.pop()
      #print "growing at",rFrom,cFrom
      rnd = random.random()
      if rnd < .25:
        attemptTerritoryAdd(rF, cF, rF, cF-1)          
      elif rnd < .5:
        attemptTerritoryAdd(rF, cF, rF,cF+1)
      elif rnd < .75:
        attemptTerritoryAdd(rF, cF, rF+1,cF)
      else:
        attemptTerritoryAdd(rF, cF, rF-1, cF)
          
      
      

def createHugeMazeMaps():
  wgmap = MazeWGMap()
  wgmap.loadMapFromFile('//BHO/data/wargear development/Maze/Random Mazes.xml')
  
  size = 30
    
  wgmap.rows = size
  wgmap.cols = size
  extension = "C"
  wgfile = '//BHO/data/wargear development/Maze/RandomMaze'+str(wgmap.rows) + 'x' + str(wgmap.cols) + extension
  wgmap.createMazeGame(wgfile,25,25)
    
  wgmap.setWideOpenParameters()
  extension = "A"    
  wgfile = '//BHO/data/wargear development/Maze/RandomMaze'+str(wgmap.rows) + 'x' + str(wgmap.cols) + extension
  wgmap.createMazeGame(wgfile,25,25)

  wgmap.setOpenParameters()
  extension = "B"    
  wgfile = '//BHO/data/wargear development/Maze/RandomMaze'+str(wgmap.rows) + 'x' + str(wgmap.cols) + extension
  wgmap.createMazeGame(wgfile,25,25)
    
  wgmap.setTightParameters()
  extension = "D"    
  wgfile = '//BHO/data/wargear development/Maze/RandomMaze'+str(wgmap.rows) + 'x' + str(wgmap.cols) + extension
  wgmap.createMazeGame(wgfile,25,25)

  wgmap.setTighterParameters()
  extension = "E"    
  wgfile = '//BHO/data/wargear development/Maze/RandomMaze'+str(wgmap.rows) + 'x' + str(wgmap.cols) + extension
  wgmap.createMazeGame(wgfile,25,25)
  
def createSimpleMazeMaps():
  wgmap = MazeWGMap()
  wgmap.loadMapFromFile('//DISKSTATION/data/wargear development/Maze/Random Mazes.xml')
  wgmap.doWrap = False;
  size = 12
  if (size <= 12):
    territoryWidth = 40
  elif (size > 16):
    territoryWidth = 30
  else:
    territoryWidth = 35

  wgmap.rows = size
  wgmap.cols = size
  extension = "C"
  wgfile = '//DISKSTATION/data/wargear development/Maze/RandomMaze-EZ-'+str(wgmap.rows) + 'x' + str(wgmap.cols) + extension
  import pdb
  pdb.set_trace()
  wgmap.createMazeGame(wgfile,territoryWidth,territoryWidth)
      
   
  
def createMazeMaps():
  wgmap = MazeWGMap()
  wgmap.loadMapFromFile('//DISKSTATION/data/wargear development/Maze/Random Mazes.xml')
  
  for size in range(8,21,4):
    
    if (size <= 12):
      territoryWidth = 40
    elif (size > 16):
      territoryWidth = 30
    else:
      territoryWidth = 35
    
    wgmap.rows = size
    wgmap.cols = size
    extension = "C"
    wgfile = '//DISKSTATION/data/wargear development/Maze/RandomMaze'+str(wgmap.rows) + 'x' + str(wgmap.cols) + extension
    wgmap.createMazeGame(wgfile,territoryWidth,territoryWidth)
      
    wgmap.setWideOpenParameters()
    extension = "A"    
    wgfile = '//DISKSTATION/data/wargear development/Maze/RandomMaze'+str(wgmap.rows) + 'x' + str(wgmap.cols) + extension
    wgmap.createMazeGame(wgfile,territoryWidth,territoryWidth)
  
    wgmap.setOpenParameters()
    extension = "B"    
    wgfile = '//DISKSTATION/data/wargear development/Maze/RandomMaze'+str(wgmap.rows) + 'x' + str(wgmap.cols) + extension
    wgmap.createMazeGame(wgfile,territoryWidth,territoryWidth)
      
    wgmap.setTightParameters()
    extension = "D"    
    wgfile = '//DISKSTATION/data/wargear development/Maze/RandomMaze'+str(wgmap.rows) + 'x' + str(wgmap.cols) + extension
    wgmap.createMazeGame(wgfile,territoryWidth,territoryWidth)
  
    wgmap.setTighterParameters()
    extension = "E"    
    wgfile = '//DISKSTATION/data/wargear development/Maze/RandomMaze'+str(wgmap.rows) + 'x' + str(wgmap.cols) + extension
    wgmap.createMazeGame(wgfile,territoryWidth,territoryWidth)
    

if __name__ == '__main__':
  pass
