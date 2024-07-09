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

from .General import WGMap

class LegoGridWGMap(WGMap):
  """
  Extends the SquareGridWGMap.
  Creates a rectangle of lego shapes.
  """
  
  class LegoBrick():
    
    def __init__(self):
      
      #r & c are position of the upper left hand corner in grid space
      self.r = None
      self.c = None
      self.randomBrick()
  
  
    def getName(self,mapObj):
      return LegoGridWGMap.getTerritoryName(mapObj,self.c,self.r)
  
    def randomBrick(self):
      rnd = random.randint(1,8)
      #print "Rand",rnd
      # 40% chance 2x1 brick
      if rnd == 1:
        self.width = 2
        self.height = 1
      if rnd == 2:
        self.width = 1
        self.height = 2
      # 20% chance 2x2 brick
      if rnd == 3 or rnd == 4:
        self.width = 2
        self.height = 2
      # 20% chance 4x1 brick
      if rnd == 5:
        self.width = 4
        self.height = 1
      if rnd == 6:
        self.width = 1
        self.height = 4
      # 20% chance 2x4 brick
      if rnd == 7:
        self.width = 2
        self.height = 4
      if rnd == 8:
        self.width = 4
        self.height = 2
            
      if rnd == 9 or rnd == 10:
        self.width = 3
        self.height = 3
        
      def getRandomColor():
        g1 = 0
        r1 = 0
        b1 = 0
        while(( g1==0 and r1==0 and b1==0) or (g1 == 2 and r1 == 2 and b1 == 2)):
          g1 = random.randint(0,2)
          r1 = random.randint(0,2)
          b1 = random.randint(0,2)
        r = 128 *r1
        g = 128 *g1
        b = 128 *b1
        #print r,g,b
        return (r,g,b)      

      self.color = getRandomColor()
  
  
  def __init__(self):
    """Constructor"""
    super(LegoGridWGMap,self).__init__()

    self.boardImage = None
    self.fillImage = None
    self.rows = 16
    self.cols = 16
    self.doWrap = False
    self.brickMaxUnits = None  # set to None to use variable maxs
    self.backgroundTile = None
    #I don't know what exactly this is doing, but it makign cols = cols-1, so use temp vars:
    tempR = self.rows
    tempC= self.cols    
    self.grid = [[None for y in range(tempR)] for x in range(tempC)]                      
                   
    #240 gives a dense board?
    #60 standard board
    #15 gives a sparse board?
    self.retriesBeforeGiveup = 60* sqrt(sqrt(self.rows*self.cols)) 
    self.colWidth=20
    self.rowHeight=20
    self.upperLeftX = 0
    self.upperLeftY = 0
    self.legoCircleRadius = 6
    self.targetWidth = 15
    self.targetHeight=17



  def setRC(self,rows,cols):
    self.rows = rows
    self.cols = cols
    #I don't know what exactly this is doing, but it makign cols = cols-1, so use temp vars:
    tempR = self.rows
    tempC= self.cols    
    self.grid = [[None for y in range(tempR)] for x in range(tempC)]                      
    
#  def setDefaultParameters(self):
#    self.retriesBeforeGiveup = 50
    
  def checkForConflict(self,newBrick):
    
    if newBrick.c+newBrick.width > self.cols:
      return True
    if newBrick.r+newBrick.height> self.rows:
      return True
    #print newBrick.c,newBrick.width,newBrick.r,newBrick.height
    for c in range(newBrick.c,newBrick.c+newBrick.width):
      for r in range(newBrick.r,newBrick.r+newBrick.height):
        #print c,r
        if(self.grid[c][r] != None):
          return True
        
    return False


  def getTerritoryName(self,c,r):
    return "brick"+str(c)+"_"+str(r)



  def addBrick(self,newBrick):
    #print "AddBrick",
    for c in range(newBrick.c,newBrick.c+newBrick.width):
      for r in range(newBrick.r,newBrick.r+newBrick.height):
        #print c,r,
        self.grid[c][r] = newBrick
    print()
    
    
    xPos = int(self.upperLeftX+(newBrick.c + newBrick.width/2.0)*self.colWidth)
    yPos = int(self.upperLeftY+(newBrick.r + newBrick.height/2.0)*self.rowHeight)
    
    
    
    
    if self.mapType == "Hordes":
      maxUnits = int(5+2.5*newBrick.width*newBrick.height)
      self.addTerritory(self.getTerritoryName(newBrick.c,newBrick.r),
                      xPos, yPos, maxUnits)
    else:
      # duel version
      borderW =  (self.rows-self.targetWidth)/2.0
      borderH = (self.cols-self.targetHeight)/2.0
      
      maxUnits = self.brickMaxUnits
      cx = newBrick.c + newBrick.width/2.0
      rx = newBrick.r  + newBrick.height/2.0
      random13 = random.randint(1,3)
      if ((random13 == 3) or (random13 == 5)) and ((rx > borderW) and (rx < self.rows-borderW) and (cx > borderH) and (cx < self.cols-borderH)):
        self.addTerritory(self.getTerritoryName(newBrick.c,newBrick.r),
                      xPos, yPos, maxUnits)
      else:
        self.addTerritory(self.getTerritoryName(newBrick.c,newBrick.r),
                      xPos, yPos, maxUnits,scenario_type="Neutral",scenario_seat="0", scenario_units="0")
      
    #print self.getTerritoryName(newBrick.c,newBrick.r), xPos, yPos, maxUnits
  
  '''
  borderW =  (self.rows-target.width)/2
borderH = (self.cols-target.height)/2

if (r > borderW) and (r < self.rows-borderW) and
  (c > borderH) and (c < self.cols-borderH))
make placeable.
  '''
  
  def createDuelMap(self,mtype):
    self.mapType = 'Duel-'+mtype
    self.retriesBeforeGiveup = 3000
    if (mtype == "Simple"):
      self.brickMaxUnits = 1
      self.setNumFortifies(1)
    elif (mtype == "Advanced"):
      self.brickMaxUnits = 2
      self.setNumFortifies(2)
    else: # Expert
      self.brickMaxUnits = 5
      self.add2x1EdgeBricks()  
      self.retriesBeforeGiveup = 5000
    
    
    
    self.addBricks()
    self.addBrickBorders()
    
  
    for r in range(self.rows):
      for c in range(self.cols):        
        brick = self.grid[c][r]
        if (brick != None):
          brickName = brick.getName(self)
          if(brick.width+brick.height == 3):
            self.addBorder("Red 2x1",brickName,"One-way")
            self.addBorder("Blue 2x1",brickName,"One-way")
          if(brick.width+brick.height == 4):
            self.addBorder("Red 2x2",brickName,"One-way")
            self.addBorder("Blue 2x2",brickName,"One-way")
          if(brick.width+brick.height == 5):
            self.addBorder("Red 4x1",brickName,"One-way")
            self.addBorder("Blue 4x1",brickName,"One-way")
          if(brick.width+brick.height == 6):
            self.addBorder("Red 4x2",brickName,"One-way")
            self.addBorder("Blue 4x2",brickName,"One-way")
        
    
    self.addRotatingFactories(territoryNames=["Red 2x1-A","Red 2x1-B"])
    self.addRotatingFactories(territoryNames=["Red 2x2-A","Red 2x2-B","Red 2x2-C"])
    self.addRotatingFactories(territoryNames=["Red 4x1-A","Red 4x1-B","Red 4x1-C"])
    self.addRotatingFactories(territoryNames=["Red 4x2-A","Red 4x2-B","Red 4x2-C","Red 4x2-D"])

    self.addRotatingFactories(territoryNames=["Blue 2x1-A","Blue 2x1-B"])
    self.addRotatingFactories(territoryNames=["Blue 2x2-A","Blue 2x2-B","Blue 2x2-C"])
    self.addRotatingFactories(territoryNames=["Blue 4x1-A","Blue 4x1-B","Blue 4x1-C"])
    self.addRotatingFactories(territoryNames=["Blue 4x2-A","Blue 4x2-B","Blue 4x2-C","Blue 4x2-D"])

    # add factories to fill adjacent legos
    nameBase = "Red 2x1"    
    tidSource = self.getTerritoryIDFromName(nameBase+"-B")
    tidDest = self.getTerritoryIDFromName(nameBase)
    self.addContinent(nameBase+"-Add",[tidSource],1,tidDest,"AutoCapture")

    nameBase = "Red 2x2"    
    tidSource = self.getTerritoryIDFromName(nameBase+"-C")
    tidDest = self.getTerritoryIDFromName(nameBase)
    self.addContinent(nameBase+"-Add",[tidSource],1,tidDest,"AutoCapture")

    nameBase = "Red 4x1"    
    tidSource = self.getTerritoryIDFromName(nameBase+"-C")
    tidDest = self.getTerritoryIDFromName(nameBase)
    self.addContinent(nameBase+"-Add",[tidSource],1,tidDest,"AutoCapture")

    nameBase = "Red 4x2"    
    tidSource = self.getTerritoryIDFromName(nameBase+"-D")
    tidDest = self.getTerritoryIDFromName(nameBase)
    self.addContinent(nameBase+"-Add",[tidSource],1,tidDest,"AutoCapture")

    nameBase = "Blue 2x1"    
    tidSource = self.getTerritoryIDFromName(nameBase+"-B")
    tidDest = self.getTerritoryIDFromName(nameBase)
    self.addContinent(nameBase+"-Add",[tidSource],1,tidDest,"AutoCapture")

    nameBase = "Blue 2x2"    
    tidSource = self.getTerritoryIDFromName(nameBase+"-C")
    tidDest = self.getTerritoryIDFromName(nameBase)
    self.addContinent(nameBase+"-Add",[tidSource],1,tidDest,"AutoCapture")

    nameBase = "Blue 4x1"    
    tidSource = self.getTerritoryIDFromName(nameBase+"-C")
    tidDest = self.getTerritoryIDFromName(nameBase)
    self.addContinent(nameBase+"-Add",[tidSource],1,tidDest,"AutoCapture")

    nameBase = "Blue 4x2"    
    tidSource = self.getTerritoryIDFromName(nameBase+"-D")
    tidDest = self.getTerritoryIDFromName(nameBase)
    self.addContinent(nameBase+"-Add",[tidSource],1,tidDest,"AutoCapture")


    # add fortify borders from side blocks to gun/ammo
    if (mtype == "Expert"):
      gunDirection = "Two-way";
    else:
      gunDirection = "One-way"
    
    for r in range(self.rows):
      c = 0    
      brick = self.grid[c][r]
      if (brick != None):
        brickName = brick.getName(self)
        self.addBorder(brickName,"Red Gun", gunDirection)
        self.addBorder("Blue Ammo",brickName, 'One-way', "Fortify Only")
    
    for r in range(self.rows):
      c = self.cols-1      
      brick = self.grid[c][r]
      if (brick != None):
        brickName = brick.getName(self)
        self.addBorder(brickName, "Blue Gun", gunDirection)
        self.addBorder("Red Ammo",brickName, 'One-way', "Fortify Only")

    



  
  
  def createHordesMap(self):
    self.mapType = 'Hordes'
    self.backgroundTile = "//DISKSTATION/data/wargear development/LEGO/LEGO_logo20.png"
    self.deleteAllContinents(False)
    self.deleteAllBorders()
    self.deleteAllTerritories()
    self.addBricks()
    self.addBrickBorders()
    
    
    while (not self.checkOneTerritoryCanReachAll()):
      
      self.deleteAllBorders()
      self.deleteAllTerritories()
      tempR = self.rows
      tempC = self.cols
      self.grid = [[None for y in range(tempR)] for x in range(tempC)]
      self.addBricks()
      self.addBrickBorders()
      
    
    self.hordify()
    if (self.rows * self.cols < 10*10):
      self.addViewBordersToNeighbors(3)
      self.setNumFortifies(3)
    else:
      self.addViewBordersToNeighbors(4)
      self.setNumFortifies(4)
    
    self.setFortifyType("connected")
  
  def add2x1EdgeBricks(self):
    
    for r in range(1,self.rows,3):
      newBrick = self.LegoBrick()
      newBrick.width = 2
      newBrick.height = 1
      newBrick.r = r
      newBrick.c = 0
      self.addBrick(newBrick)
      
      newBrick = self.LegoBrick()
      newBrick.r = r
      newBrick.c = self.cols-2
      newBrick.width = 2
      newBrick.height = 1
      self.addBrick(newBrick)
      
  
  def addBricks(self):
    print(self.cols, end=' ')
    print("X", end=' ')
    print(self.rows)
    

    retries = 0

    while (retries < self.retriesBeforeGiveup):
      newBrick = self.LegoBrick()
      
      #print self.grid
      newBrick.r = random.randint(0,self.rows-newBrick.height)
      newBrick.c = random.randint(0,self.cols-newBrick.width)
      
      if (self.checkForConflict(newBrick)):
        retries+=1
        continue
        
      self.addBrick(newBrick)


  def checkForBorder(self,c1,r1,c2,r2):
      return self.grid[c1][r1] != None and self.grid[c2][r2] != None and self.grid[c1][r1] != self.grid[c2][r2]

  def addBrickBorders(self):
         
    print("ADDING BRICK BORDERS")
    for r in range(self.rows):
      for c in range(self.cols-1):
        if (self.checkForBorder(c,r,c+1,r)):
          brick1 = self.grid[c][r]
          brick2 = self.grid[c+1][r]
          b1Name = self.getTerritoryName(brick1.c,brick1.r)
          b2Name = self.getTerritoryName(brick2.c,brick2.r)
          #print "brick1: ",b1Name, "@",c,r,brick1.c,brick1.r
          #print "brick2: ",b2Name, "@",c+1,r,brick2.c,brick2.r
          self.addBorder(b1Name,b2Name)
 
    for r in range(self.rows-1):
      for c in range(self.cols):
        if (self.checkForBorder(c,r,c,r+1)):
          brick1 = self.grid[c][r]
          brick2 = self.grid[c][r+1]
          b1Name = self.getTerritoryName(brick1.c,brick1.r)
          b2Name = self.getTerritoryName(brick2.c,brick2.r)
          #print "brick1: ",b1Name, "@",c,r,brick1.c,brick1.r
          #print "brick2: ",b2Name, "@",c,r+1,brick2.c,brick2.r
          self.addBorder(b1Name,b2Name)
          


 
  def printGrid(self):
    print(str(self.cols) +"X" + str(self.rows))
    print(" ", end=' ')
    for c in range(self.cols):
      print(c%10, end=' ')
    print()
    for r in range(self.rows):
      print(r%10, end=' ')
      for c in range(self.cols):
        if self.grid[c][r] == None:
          print(" ", end=' ')
        else:
          print("x", end=' ')
      print()
        
  
  
  def createPNG(self, filePath):
    '''
    Creates a PNG of a maze with walls
    '''
    if self.boardImage != None:
      boardIm = Image.open(self.boardImage)
    else:    
      boardIm = Image.new("RGBA", ( self.cols*self.colWidth,self.rows*self.rowHeight), (0,0,0,0))
      
    if self.fillImage != None:
      fillIm = Image.open(self.fillImage)
    else:
      fillIm = Image.new("RGB", ( self.cols*self.colWidth,self.rows*self.rowHeight), (0,0,0))
    #print "create new RGB image:", self.cols*colWidth,self.rows*rowHeight
    # @todo: these should all be rowHeight

    wallHalfWidth=2
    
    if self.backgroundTile != None:
      bgtImage = Image.open(self.backgroundTile)
    
    def safePutPixel(im,xy,rgba):
      (x,y) = xy
      #(r,g,b) = rgb
      if (x < 0 or x >= self.cols*self.colWidth):
        return
      if (y < 0 or y >= self.rows*self.rowHeight):
        return
      x = x + self.upperLeftX
      y = y + self.upperLeftY
      xy = (x,y)
      #print "xy",xy
      #print "rgba", rgba
      im.putpixel(xy, rgba)
      
    def drawCircle(c,r):
      rad = self.legoCircleRadius
      for d in range(0,360,int(360/(2*6.28*rad))):
        x = (c+.5)*self.colWidth
        y = (r+.5)*self.rowHeight
        x += rad*cos(d)
        y += rad*sin(d)
        x = int(x)
        y = int(y)
        safePutPixel(boardIm, (x,y), (32,32,32))  
      
    
    def drawRightWall(fromR, fromC):
      if (fromC == self.cols-1):
        whw = wallHalfWidth*2
      else:
        whw = wallHalfWidth
      for y in range(fromR*self.rowHeight-wallHalfWidth,(fromR+1)*self.rowHeight+wallHalfWidth+1):
        for x in range((fromC+1)*self.colWidth-whw,(fromC+1)*self.colWidth+whw+1):
          safePutPixel(fillIm, (x,y), (0,0,0))
          safePutPixel(boardIm, (x,y), (0,0,0))
    
    def drawBottomWall(fromR, fromC):
      if (fromR == self.rows-1):
        whw = wallHalfWidth*2
      else:
        whw = wallHalfWidth
      for x in range(fromC*self.colWidth-wallHalfWidth,(fromC+1)*self.colWidth+wallHalfWidth+1):
        for y in range((fromR+1)*self.rowHeight-whw,(fromR+1)*self.rowHeight+whw+1):
          safePutPixel(fillIm, (x,y), (0,0,0))
          safePutPixel(boardIm, (x,y), (0,0,0))
          

    def drawLeftWall(fromR, fromC):
      if (fromC == 0):
        whw = wallHalfWidth*2-1
      else:
        whw = wallHalfWidth
        
      for y in range(fromR*self.rowHeight-wallHalfWidth,(fromR+1)*self.rowHeight+wallHalfWidth+1):
        for x in range((fromC)*self.colWidth-whw,(fromC)*self.colWidth+whw+1):
          safePutPixel(fillIm, (x,y), (0,0,0))
          safePutPixel(boardIm, (x,y), (0,0,0))
    
    def drawTopWall(fromR, fromC):
      if (fromR == 0):
        whw = wallHalfWidth*2-1
      else:
        whw = wallHalfWidth
      for x in range(fromC*self.colWidth-wallHalfWidth,(fromC+1)*self.colWidth+wallHalfWidth+1):
        for y in range((fromR)*self.rowHeight-whw,(fromR)*self.rowHeight+whw+1):
          safePutPixel(fillIm, (x,y), (0,0,0))
          safePutPixel(boardIm, (x,y), (0,0,0))

    def drawEdgeBorders():
      for y in range(self.rows*self.rowHeight):
        for x in range(wallHalfWidth):
          safePutPixel(fillIm, (x,y), (0,0,0))
          safePutPixel(boardIm, (x,y), (0,0,0))
        for x in range(self.cols*self.colWidth - wallHalfWidth, self.cols*self.colWidth):
          safePutPixel(fillIm, (x,y), (0,0,0))
          safePutPixel(boardIm, (x,y), (0,0,0))
      for x in range(self.cols*self.colWidth):
        for y in range(wallHalfWidth):
          safePutPixel(fillIm, (x,y), (0,0,0))
          safePutPixel(boardIm, (x,y), (0,0,0))
        for y in range(self.rows*self.rowHeight - wallHalfWidth, self.rows*self.rowHeight):
          safePutPixel(fillIm, (x,y), (0,0,0))
          safePutPixel(boardIm, (x,y), (0,0,0))
        
      
    def checkForBrickEdge(c1,r1,c2,r2):
      return self.grid[c1][r1] != self.grid[c2][r2]

    
    
    def fillSquare(im,c,r,color):
      for x in range(c*self.colWidth,(c+1)*self.colWidth):
        for y in range(r*self.rowHeight,(r+1)*self.rowHeight):
          safePutPixel(im, (x,y), color)

    


    for r in range(self.rows):
      for c in range(self.cols):
        if self.grid[c][r] != None:
          fillSquare(fillIm,c,r,self.grid[c][r].color)
          drawCircle(c,r)
        else:
          if self.backgroundTile == None:
            fillSquare(boardIm,c,r,(0,0,0))
          else:
            boardIm.paste(bgtImage, (c*self.colWidth,r*self.rowHeight)) 
        
    drawEdgeBorders()    
     
    for r in range(self.rows):
      for c in range(self.cols-1):
        if checkForBrickEdge(c,r,c+1,r):
          drawRightWall(r,c)
          
          
    for r in range(self.rows-1):
      for c in range(self.cols):        
        if checkForBrickEdge(c,r,c,r+1):
          drawBottomWall(r,c)
        
    '''
    # fill in borders on top 
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
          
    '''          
      
         
         
        

    # add some text  
    #draw = ImageDraw.Draw(im)
    # use a truetype font
    #font = ImageFont.truetype("//BHO/data/wargear development/scripts/nayla.ttf", 15)

    #draw.text((10, 25), "TESETING world TSETING", font=font)



    fillIm.save(filePath + "-FILL.png")
    boardIm.save(filePath + "-BOARD.png")



def setupLegoHordesMap():
  wgmap = LegoGridWGMap()
  wgmap.load_map_from_file('//DISKSTATION/data/wargear development/LEGO/Hoarding LEGO(4).xml')
  #wgmap.loadMapFromFile('//DISKSTATION/data/wargear development/LEGO/Hoarding LEGO.xml')
  
  
  wgmap.setRC(20,20)
                   
  #for 15x15
  #40 gives a dense board? 100 for 25x25
  #10 standard board
  #4 gives a sparse board?
  wgmap.retriesBeforeGiveup = 45 * sqrt(wgmap.rows*wgmap.cols) 
   
  wgmap.createHordesMap()
  wgmap.printGrid()
  wgmap.createPNG('//DISKSTATION/data/wargear development/LEGO/out')
  wgmap.save_map_to_file('//DISKSTATION/data/wargear development/LEGO/out.xml')
 
 
 
def setupLegoDuelMap():
  
  #mtype = "Advanced"
  #mtype = "Simple"
  mtype = "Expert"
  
  wgmap = LegoGridWGMap()
  #wgmap.loadMapFromFile('//DISKSTATION/data/wargear development/LEGO/LFB template - '+mtype+'(4).xml')
  wgmap.load_map_from_file('//DISKSTATION/data/wargear development/LEGO/LFB template - Expert.xml')

  wgmap.upperLeftX = 197
  wgmap.upperLeftY = 20
  wgmap.rowHeight = 30
  wgmap.colWidth = 30
  wgmap.legoCircleRadius = 8
  wgmap.setRC(24,21)
  
  wgmap.targetWidth = 15
  wgmap.targetHeight=17


  wgmap.boardImage = '//DISKSTATION/data/wargear development/LEGO/legoV2-Board.png'
  wgmap.fillImage = '//DISKSTATION/data/wargear development/LEGO/legoV2-FILL.png'
  #X: 826-197=629  ~= 30*21
  #Y: 739-20=719 ~= 30*24
  #goodMap = False
  #while not goodMap:  #this doesn't really work because bricks always border an adjacent lego
  wgmap.createDuelMap(mtype)
  #  goodMap = wgmap.isThereADeadEnd()
    
  wgmap.printGrid()
  wgmap.createPNG('//DISKSTATION/data/wargear development/LEGO/out')
  wgmap.save_map_to_file('//DISKSTATION/data/wargear development/LEGO/out.xml', False)
 
  

if __name__ == '__main__':
  pass
