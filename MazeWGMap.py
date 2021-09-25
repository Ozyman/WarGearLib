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
#import General

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
    self.createFeatures()
    
  def createFeatures(self):
    self.features = ['ss','rrllrrll','llrrllrr','rrllrrllrr','llrrllrrll','sssrsssrssrssrsrsrrs','ssslssslsslsslslslls','lrlrlrlrlrlr','rlrlrlrlrlrl']

  def setDefaultParameters(self):
    self.branchingFactor = .4  #Fraction of growth points that will branch
    self.connectionRejection = .8  # % chance a connection from a growth point to a territory w/borders will be retried
    self.chanceToDeadEnd = .33 #Fraction of times a connection from gp to territory w/borders will dead end vs. joining up (assuming !connectionRejected)
  
  
  def setOpenParameters(self):
    self.branchingFactor = .5  #Fraction of growth points that will branch
    self.connectionRejection = .7  # % chance a connection from a growth point to a territory w/borders will be retried
    self.chanceToDeadEnd = .3 #Fraction of times a connection from gp to territory w/borders will dead end vs. joining up (assuming !connectionRejected)
  
  def setWideOpenParameters(self):
    self.branchingFactor = .7  #Fraction of growth points that will branch
    self.connectionRejection = .5  # % chance a connection from a growth point to a territory w/borders will be retried
    self.chanceToDeadEnd = .15 #Fraction of times a connection from gp to territory w/borders will dead end vs. joining up (assuming !connectionRejected)
  
  def setTightParameters(self):
    self.branchingFactor = .25  #Fraction of growth points that will branch
    self.connectionRejection = .85  # % chance a connection from a growth point to a territory w/borders will be retried
    self.chanceToDeadEnd = .6 #Fraction of times a connection from gp to territory w/borders will dead end vs. joining up (assuming !connectionRejected)
   
  def setTighterParameters(self):
    self.branchingFactor = .12  #Fraction of growth points that will branch
    self.connectionRejection = .9 # % chance a connection from a growth point to a territory w/borders will be retried
    self.chanceToDeadEnd = .75 #Fraction of times a connection from gp to territory w/borders will dead end vs. joining up (assuming !connectionRejected)
    
  
  def cleanupFourSquares(self):
    
    for r in range(self.rows-1):
      for c in range(self.cols-1):
        ulID = self.getTerritoryIDFromName(self.getTerritoryName(r,c))
        blID = self.getTerritoryIDFromName(self.getTerritoryName(r+1,c))
        urID = self.getTerritoryIDFromName(self.getTerritoryName(r,c+1))
        brID = self.getTerritoryIDFromName(self.getTerritoryName(r+1,c+1))
        
        if self.doTheyBorder(ulID,blID) and self.doTheyBorder(ulID,urID) and self.doTheyBorder(brID,urID) and self.doTheyBorder(brID,blID):
          print "cleaning up a 4-square at",r,c
          #pick a random border to remove.
          rnd = random.random()
          if rnd < .25:
            self.deleteBorder(ulID,blID)        
          elif rnd < .5:
            self.deleteBorder(ulID,urID)          
          elif rnd < .75:
            self.deleteBorder(brID,urID)          
          else:
            self.deleteBorder(brID,blID)          
 
  def addContinents(self,valueFunction=None):
    
    def divideByTwo(n):
      return n/2
    
    if valueFunction == None:
      valueFunction = divideByTwo
      
      
    colContinents = 0
    for r in range(0,self.rows-1):
      for c in range(self.cols):        
        centerID = self.getTerritoryIDFromName(self.getTerritoryName(r,c))
        aboveID =  self.getTerritoryIDFromName(self.getTerritoryName(r-1,c))
        print "looking for column at",r,c
        # if there a border above, we have done this column continent already      
        if aboveID == None or not self.doTheyBorder(centerID,aboveID):
          print "starting a column at ",centerID,r,c
          membersList = str(centerID)        
          rBelow=r+1
          prevBelowID = centerID
          belowID = self.getTerritoryIDFromName(self.getTerritoryName(rBelow,c))
          contLength = 1
          # Find the extent of the column          
          while rBelow < self.rows and self.doTheyBorder(belowID,prevBelowID) :
            print "continuing a column at ",belowID,rBelow,c 
            membersList += ","  + str(belowID)
            contLength += 1
            rBelow += 1
            prevBelowID = belowID
            belowID = self.getTerritoryIDFromName(self.getTerritoryName(rBelow,c))
          
          if (contLength > 1):
            self.addContinent("Column "+str(colContinents),membersList,valueFunction(contLength))
            colContinents += 1
          
    rowContinents = 0
    for r in range(self.rows):
      for c in range(0,self.cols-1):        
        centerID = self.getTerritoryIDFromName(self.getTerritoryName(r,c))
        leftID =  self.getTerritoryIDFromName(self.getTerritoryName(r,c-1))
        # if there a border above, we have done this column continent already      
        if leftID == None or not self.doTheyBorder(centerID,leftID):
          membersList = str(centerID)        
          cRight=c+1
          prevRightID = centerID
          rightID = self.getTerritoryIDFromName(self.getTerritoryName(r,cRight))
          contLength = 1
          # Find the extent of the column          
          while cRight < self.cols and self.doTheyBorder(rightID,prevRightID):
            membersList += ","  + str(rightID)
            contLength += 1
            cRight += 1
            prevRightID = rightID
            rightID = self.getTerritoryIDFromName(self.getTerritoryName(r,cRight))
          
          if (contLength > 1):
            self.addContinent("Row "+str(rowContinents),membersList,valueFunction(contLength))
            rowContinents += 1
       
            
  def addLineOfSightViewBorders(self):
    for r in range(self.rows):
      for c in range(self.cols):
        tid = self.getTerritoryIDFromName(self.getTerritoryName(r,c))
        print "adding los vborders for",self.getTerritoryName(r,c)
        self.addViewBordersToFellowMembers(tid)
  

  
  def createMazeGame(self,filePath,rowHeight=40,colWidth=40,lineOfSight=False):
    '''Be sure to set the board name by hand'''
    
    xOrigin = colWidth/2
    yOrigin = rowHeight/2
    
    self.rowHeight = rowHeight
    self.colWidth = colWidth
    
    print "Maze (" + str(self.rows) + "x" + str(self.cols) + ")"
    print filePath
    self.deleteAllBorders()
    self.deleteAllTerritories()
    self.deleteAllContinents()

    #self.setBoardName("Knight's Tour (" + str(rows) + "x" + str(cols) + ")")
    
    self.createTerritories(xOrigin, yOrigin, self.rowHeight, self.colWidth)
       
    self.fillWithRandomWalk()
    
    print "begin connect sg"
    returnValue = self.connectSeperateGroups()
    self.cleanupFourSquares()
    
    self.addContinents()
    self.setNumFortifies(int(ceil(sqrt(self.rows*self.cols)/3.75)))
    self.setEliminationBonus(int(ceil(sqrt(self.rows*self.cols))))
    self.setMaxCards(3+int(ceil(sqrt(sqrt(self.rows*self.cols)))))
    
    self.createPNG(filePath)
    if lineOfSight:
      self.addLineOfSightViewBorders()

    self.saveMapToFile(filePath + ".xml")
    '''
    bc = self.getBorderCounts()
    for BName,BCount in bc.iteritems():
      if BCount > 4:
        print BName,"has",BCount,"borders!!"
    '''

    return returnValue
  
  
  def createCloudPNG(self,imHandle):    
    # Thanks to http://pygame.org/project-Perlin+Noise+Generator-1044-.html
    # larger tiledim is 'zoomed out'
    tiledim = 8   #In nodes
    repeats = 1
    Screen = int(sqrt(self.cols*self.colWidth*self.rows*self.rowHeight))
    tilesize = float(Screen)/repeats
    tilesize /= tiledim
    p = []
    for x in xrange(2*tiledim):
      p.append(0)
    permutation = []
    for value in xrange(tiledim):
      permutation.append(value)
    random.shuffle(permutation)

    for i in xrange(tiledim):
      p[i] = permutation[i]
      p[tiledim+i] = p[i]
    

    def grad(hash1, x, y, z):
      #CONVERT LO 4 BITS OF HASH CODE INTO 12 GRADIENT DIRECTIONS.
      h = hash1 & 15
      if h < 8: u = x
      else:     u = y
      if h < 4: v = y
      else:
          if h == 12 or h == 14: v = x
          else:                  v = z
      if h&1 == 0: first = u
      else:        first = -u
      if h&2 == 0: second = v
      else:        second = -v
      return first + second
    def lerp(t, a, b):
      return a + t * (b - a)
    def fade(t):
      return t * t * t * (t * (t * 6 - 15) + 10)
    def noise(x,y,z):
      #FIND UNIT CUBE THAT CONTAINS POINT.
      X = int(x)&(tiledim-1)
      Y = int(y)&(tiledim-1)
      Z = int(z)&(tiledim-1)
      #FIND RELATIVE X,Y,Z OF POINT IN CUBE.
      x -= int(x)
      y -= int(y)
      z -= int(z)
      #COMPUTE FADE CURVES FOR EACH OF X,Y,Z.
      u = fade(x)
      v = fade(y)
      w = fade(z)
      #HASH COORDINATES OF THE 8 CUBE CORNERS
      A = p[X  ]+Y; AA = p[A]+Z; AB = p[A+1]+Z
      B = p[X+1]+Y; BA = p[B]+Z; BB = p[B+1]+Z
      #AND ADD BLENDED RESULTS FROM 8 CORNERS OF CUBE
      offset = 1
      #offset = int(random.random() * 1.5) + 1
      return lerp(w,lerp(v,
                       lerp(u,grad(p[AA  ],x  ,y  ,z  ),
                              grad(p[BA  ],x-offset,y  ,z  )),
                       lerp(u,grad(p[AB  ],x  ,y-offset,z  ),
                              grad(p[BB  ],x-offset,y-offset,z  ))),
                  lerp(v,
                       lerp(u,grad(p[AA+offset],x  ,y  ,z-offset),
                              grad(p[BA+offset],x-offset,y  ,z-offset)),
                       lerp(u,grad(p[AB+offset],x  ,y-offset,z-offset),
                              grad(p[BB+offset],x-offset,y-offset,z-offset))))
    octaves = 2
    persistence = 0.5
    colorBias = 32
    colorScale = 2.5
    amplitude = 2.0
    maxamplitude = 3.0
    for octave in xrange(octaves):
        amplitude *= persistence
        maxamplitude += amplitude

    for x in xrange(self.cols*self.colWidth):
        for y in xrange(self.rows*self.rowHeight):
            sc = float(Screen)/tilesize
            frequency = 1.0
            amplitude = 1.0
            color = 0.0
            for octave in xrange(octaves):
                random.seed()
                sc *= frequency
                grey = noise(sc*float(x)/Screen,sc*float(y)/Screen,0.0)
                grey = (grey+1.0)/2.0
                grey *= amplitude
                color += grey
                frequency *= 2.0
                amplitude *= persistence
            color /= maxamplitude
            color = int(round(color*255.0))
            cc = int(colorScale*color+colorBias)          
            self.safePutPixel(imHandle,(x,y),(int(1.1*cc),cc,int(1.3*cc)))
   
   
  

  def safePutPixel(self, imHandle,xy,rgb):
      (x,y) = xy
      #(r,g,b) = rgb
      if (x < 0 or x >= self.cols*self.colWidth):
        return
      if (y < 0 or y >= self.rows*self.rowHeight):
        return
      imHandle.putpixel(xy, rgb)

  # only place the pixel if it has a greater alpha than already exists. 
  def putOpaquerPixel(self, imHandle,xy,rgba):
      (x,y) = xy
      (r1,g1,b1,a1) = imHandle.getpixel(xy)
      (r2,g2,b2,a2) = rgba
      if a1 > a2:
        return
      #(r,g,b) = rgb
      if (x < 0 or x >= self.cols*self.colWidth):
        return
      if (y < 0 or y >= self.rows*self.rowHeight):
        return
      imHandle.putpixel(xy, rgba)


  # @todo: change putpixel to the  faster way
  def createPNG(self, filePath):
    '''
    Creates PNGs of a maze with walls
    '''
    wallHalfWidth=2
    territoryDividerGrey = (32,32,32)
    
    imFill = Image.new("RGB", ( self.cols*self.colWidth,self.rows*self.rowHeight), "white")
    imFill2 = Image.new("RGB", ( self.cols*self.colWidth+2*wallHalfWidth,self.rows*self.rowHeight+2*wallHalfWidth), "black")
    imBoard = Image.new("RGBA", ( self.cols*self.colWidth,self.rows*self.rowHeight), (1,1,1,0))
    imBoard2 = Image.new("RGBA", ( self.cols*self.colWidth+2*wallHalfWidth,self.rows*self.rowHeight+2*wallHalfWidth), (0,0,0,255))
    
    c=(255,255,255)

    # create wallsa aroudn imboard2 and then later we paste imboard into imboard2
    for x in xrange(self.cols*self.colWidth+2*wallHalfWidth):
      self.safePutPixel(imBoard2,(x,0), c)
    for y in xrange(self.rows*self.rowHeight+2*wallHalfWidth):
      self.safePutPixel(imBoard2,(0,y), c)
      
    #print "create new RGB image:", self.cols*self.colWidth,self.rows*rowHeight
    # @todo: these should all be rowHeight

    
      
    
    def drawRightWall(imHandle,fromR, fromC, onlyOneColor = None):
      if (fromC == self.cols-1):
        whw = wallHalfWidth*2
      else:
        whw = wallHalfWidth
      for y in range(fromR*self.rowHeight-wallHalfWidth,(fromR+1)*self.rowHeight+wallHalfWidth+1):
        for x in range((fromC+1)*self.colWidth-whw,(fromC+1)*self.colWidth+whw+1):
          if ((x == (fromC+1)*self.colWidth-whw)):
            if (onlyOneColor == "Black"):
              continue
            if (onlyOneColor == None):
              c = (0,0,0)  # ugly hack for fill map
            else:
              c = (192,192,192)
          else:
            if (onlyOneColor == "White"):
              continue
            c = (0,0,0)
          self.safePutPixel(imHandle,(x,y), c)

    
    def drawBottomWall(imHandle,fromR, fromC, onlyOneColor = None):
      if (fromR == self.rows-1):
        whw = wallHalfWidth*2
      else:
        whw = wallHalfWidth
      for x in range(fromC*self.colWidth-wallHalfWidth,(fromC+1)*self.colWidth+wallHalfWidth+1):
        for y in range((fromR+1)*self.rowHeight-whw,(fromR+1)*self.rowHeight+whw+1):
          if ((y == (fromR+1)*self.rowHeight-whw)):
            if (onlyOneColor == "Black"):
              continue
            if (onlyOneColor == None):
              c = (0,0,0)  # ugly hack for fill map
            else:
              c = (192,192,192)
          else:
            if (onlyOneColor == "White"):
              continue
            c = (0,0,0)
          self.safePutPixel(imHandle,(x,y), c)

    def drawLeftWall(imHandle,fromR, fromC):
      if (fromC == 0):
        whw = wallHalfWidth*2-1
      else:
        whw = wallHalfWidth
        
      for y in range(fromR*self.rowHeight-wallHalfWidth,(fromR+1)*self.rowHeight+wallHalfWidth+1):
        for x in range((fromC)*self.colWidth-whw,(fromC)*self.colWidth+whw+1):
          if ((x == (fromC)*self.colWidth-whw) or (x == (fromC)*self.colWidth+whw )):
            c = (192,192,192)
          else:
            c = (0,0,0)
          self.safePutPixel(imHandle,(x,y), c)
    
    def drawTopWall(imHandle,fromR, fromC):
      if (fromR == 0):
        whw = wallHalfWidth*2-1
      else:
        whw = wallHalfWidth
      for x in range(fromC*self.colWidth-wallHalfWidth,(fromC+1)*self.colWidth+wallHalfWidth+1):
        for y in range((fromR)*self.rowHeight-whw,(fromR)*self.rowHeight+whw+1):
          if ((y == (fromR)*self.rowHeight-whw) or (y == (fromR)*self.rowHeight+whw)):
            c = (192,192,192)
          else:
            c = (0,0,0)
          self.safePutPixel(imHandle,(x,y), c)

    def drawEdgeBorders(imHandle):
      for y in range(self.rows*self.rowHeight):
        for x in [0,1,2]:
          self.safePutPixel(imHandle,(x, y), (0, 0, 0))
          x2 = self.cols*self.colWidth-x-1
          self.safePutPixel(imHandle,(x2, y), (0, 0, 0))
      for x in range(self.cols*self.colWidth):
        for y in [0,1,2]:
          self.safePutPixel(imHandle,(x, y), (0, 0, 0))
          y2 = self.rows*self.rowHeight-y-1
          self.safePutPixel(imHandle,(x, y2), (0, 0, 0))
        
      
        
        

    '''
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
    '''      
    
    def drawWalls(im,onlyOneColor):
      # draw the rest of the walls
      for r in range(self.rows-1):
        for c in range(self.cols-1):
          centerID = self.getTerritoryIDFromName(self.getTerritoryName(r,c))
          rightID =  self.getTerritoryIDFromName(self.getTerritoryName(r,c+1))
          bottomID =  self.getTerritoryIDFromName(self.getTerritoryName(r+1,c))
          if(not self.doTheyBorder(centerID,rightID)):
            #print "border between",self.getTerritoryName(r,c),self.getTerritoryName(r,c+1)        
            drawRightWall(im,r,c,onlyOneColor)
          if(not self.doTheyBorder(centerID,bottomID)):
            #print "border between",self.getTerritoryName(r,c),self.getTerritoryName(r+1,c)
            drawBottomWall(im,r,c,onlyOneColor)
            
      for r in range(self.rows-1):
        c = self.cols-1
        centerID = self.getTerritoryIDFromName(self.getTerritoryName(r,c))
        bottomID =  self.getTerritoryIDFromName(self.getTerritoryName(r+1,c))
        if(not self.doTheyBorder(centerID,bottomID)):
            #print "border between",self.getTerritoryName(r,c),self.getTerritoryName(r+1,c)
            drawBottomWall(im,r,c,onlyOneColor)
  
        
      for c in range(self.cols-1):
          r = self.rows-1
          centerID = self.getTerritoryIDFromName(self.getTerritoryName(r,c))
          rightID =  self.getTerritoryIDFromName(self.getTerritoryName(r,c+1))      
          if(not self.doTheyBorder(centerID,rightID)):
            #print "border between",self.getTerritoryName(r,c),self.getTerritoryName(r,c+1)        
            drawRightWall(im,r,c,onlyOneColor)
          
    drawWalls(imFill,None)
    drawWalls(imBoard,None)
    #drawWalls(imBoard,"Black")
    #rawWalls(imBoard,"White")
    
    # This will check each pixel.  If the pixel is black, and there is a pixel below that is black, and one above that is not, then make it light-grey
    #  Also check left/right for light-grey
    def addWallTops(im):
      for x in xrange(self.cols*self.colWidth,1,-1):
        for y in xrange(self.rows*self.rowHeight,1,-1):
          #print x,y
          #print im.getpixel((x,y))
          if (im.getpixel((x,y)) == (0,0,0,255)):
            if( (im.getpixel((x,y+1)) == (0,0,0,255)) and (im.getpixel((x,y-1)) != (0,0,0,255)) ):
              im.putpixel((x,y),(255,255,255))
            if( (im.getpixel((x+1,y)) == (0,0,0,255)) and (im.getpixel((x-1,y)) != (0,0,0,255)) ):
              im.putpixel((x,y),(255,255,255))
      for x in xrange(self.cols*self.colWidth,1,-1):
        for y in xrange(self.rows*self.rowHeight,1,-1):
          if ((im.getpixel((x,y+1)) == (255,255,255,255)) and
              (im.getpixel((x+1,y)) == (255,255,255,255)) and
              (im.getpixel((x+2,y)) == (255,255,255,255)) and
              (im.getpixel((x,y)) == (0,0,0,255))):
            im.putpixel((x,y),(255,255,255))
            
          if ((im.getpixel((x,y-1)) == (255,255,255,255)) and
              (im.getpixel((x-1,y)) == (255,255,255,255)) and
              (im.getpixel((x-2,y)) == (255,255,255,255)) and
              (im.getpixel((x,y)) == (0,0,0,255))):
            im.putpixel((x,y),(255,255,255))
            
    # This will check each pixel.  If the pixel is black, and there is a pixel below that is black, and one above that is not, then make it light-grey
    #  Also check left/right for light-grey
    def addWallTops2(im):
      for x in xrange(self.cols*self.colWidth-2,1,-1):
        for y in xrange(self.rows*self.rowHeight-2,1,-1):
          #print x,y
          #print im.getpixel((x,y))
          if (im.getpixel((x,y)) == (0,0,0,255)):
            if( (im.getpixel((x,y+1)) == (0,0,0,255)) and (im.getpixel((x,y-1)) != (0,0,0,255)) ):
              im.putpixel((x,y),(255,255,255))
            if( (im.getpixel((x+1,y)) == (0,0,0,255)) and (im.getpixel((x-1,y)) != (0,0,0,255)) ):
              im.putpixel((x,y),(255,255,255))
      for x in xrange(self.cols*self.colWidth-2,1,-1):
        for y in xrange(self.rows*self.rowHeight-2,1,-1):
          if ((im.getpixel((x,y+1)) == (255,255,255,255)) and
              (im.getpixel((x+1,y)) == (255,255,255,255)) and
              (im.getpixel((x+2,y)) == (255,255,255,255)) and
              (im.getpixel((x,y)) == (0,0,0,255))):
            im.putpixel((x,y),(255,255,255))
            
          if ((im.getpixel((x,y-1)) == (255,255,255,255)) and
              (im.getpixel((x-1,y)) == (255,255,255,255)) and
              (im.getpixel((x-2,y)) == (255,255,255,255)) and
              (im.getpixel((x,y)) == (0,0,0,255))):
            im.putpixel((x,y),(255,255,255))
            
            
    def addWallShadows2(im):
      alphaFade = .65
      minAlpha = 32
      for x in xrange(1,self.cols*self.colWidth):
        for y in xrange(1,self.rows*self.rowHeight):
          (r,g,b,a) = im.getpixel((x,y))
          if (a == 0):
            (ur,ug,ub,ua) = im.getpixel((x,y-1))
            (lr,lg,lb,la) = im.getpixel((x-1,y))
            r = min(ur,lr)
            g = min(ug,lg)
            b = min(ub,lb)
            a = int(alphaFade * max(ua,la))
            #a = int(alphaFade * (ua+la)/2)
            if (a > minAlpha):
              im.putpixel((x,y),(r,g,b,a))

    # This will check each pixel.  If the pixel is black, and there is a pixel above that is black, and one below that is not, then make it shadow
    #  Also check left/right
    
    # then repeat and fill in the corners. 
    def addWallShadows(im):
      for x in xrange(self.cols*self.colWidth-2,1,-1):
        for y in xrange(self.rows*self.rowHeight-2,1,-1):
          #print x,y
          #print im.getpixel((x,y))
          #if ((im.getpixel((x,y)) == (1,1,1,0)) and (im.getpixel((x,y-1)) == (0,0,0,255)) and  (im.getpixel((x-1,y)) == (0,0,0,255))):
          #    self.putOpaquerPixel(im,(x+2,y+2),(0,0,0,64))
          #    self.putOpaquerPixel(im,(x+1,y+1),(0,0,0,128))
          setPixel = False 
          # just got to the right edge of a wall
          if (im.getpixel((x,y)) == (1,1,1,0) and (im.getpixel((x,y-1)) == (0,0,0,255))):
              self.putOpaquerPixel(im,(x,y+3),(0,0,0,48))
              self.putOpaquerPixel(im,(x,y+2),(0,0,0,92))
              self.putOpaquerPixel(im,(x,y+1),(0,0,0,128))
              self.putOpaquerPixel(im,(x,y),(0,0,0,160))
              setPixel = True
          # just got to the bottom edge of a wall
          if (im.getpixel((x,y)) == (1,1,1,0) and (im.getpixel((x-1,y)) == (0,0,0,255))):
              self.putOpaquerPixel(im,(x+3,y),(0,0,0,48))
              self.putOpaquerPixel(im,(x+2,y),(0,0,0,92))              
              self.putOpaquerPixel(im,(x+1,y),(0,0,0,128))
              self.putOpaquerPixel(im,(x,y),(0,0,0,160))
              setPixel = True
    
      for x in xrange(1,self.cols*self.colWidth):
        for y in xrange(1,self.rows*self.rowHeight):
          (_,_,_,alpha1) = im.getpixel((x,y-1))
          (_,_,_,alpha2) = im.getpixel((x-1,y))
                    
          maxalpha = max(alpha1,alpha2)
          minalpha = min(alpha1,alpha2)
          if im.getpixel((x-1,y-1)) ==  im.getpixel((x,y-1)) == im.getpixel((x-1,y)):
                    continue
          if (maxalpha < 255) :          
            self.putOpaquerPixel(im,(x,y),(0,0,0,minalpha))
          
          
            
            
             
 
    #alpha = imBoard.split()[-1]
    #print alpha
         
        

    # add some text  
    #draw = ImageDraw.Draw(imFill)
    # use a truetype font
    #font = ImageFont.truetype("//BHO/data/wargear development/scripts/nayla.ttf", 15)

    #draw.text((10, 25), "TESETING world TSETING", font=font)


    
    
    addWallTops2(imBoard)  
    addWallShadows2(imBoard) 
    
    #draw in grey lines between each square for continent borders. 
    for col in range(self.cols):      
      for y in range(self.rows*self.rowHeight):
        row = floor(y/self.rowHeight)
        #for x in [col*self.colWidth, col*self.colWidth+1,col*self.colWidth+2]:
        for x in [col*self.colWidth]:
          #print x,y
          #print imFill.getpixel((x,y))
          #print "putpixel",x,y           
          if (col != 0):     
            self.safePutPixel(imFill,(x, y), territoryDividerGrey)
            (_,_,_,alpha) = imBoard.getpixel((x,y))
            #print "alpha", alpha
            if alpha < 200:              
              self.safePutPixel(imBoard,(x, y), territoryDividerGrey)
        
    for row in range(self.rows):      
      for x in range(self.cols*self.colWidth):
        
        col = floor(x/self.colWidth)
        #for y in [row*self.rowHeight, row*self.rowHeight+1, row*self.rowHeight-1]:
        for y in [row*self.rowHeight]:
          #print x,y
          #print imFill.getpixel((x,y))
          #print "putpixel",x,y
          if (row != 0):
            self.safePutPixel(imFill,(x, y), territoryDividerGrey)
            (_,_,_,alpha) = imBoard.getpixel((x,y))
            #print "alpha", alpha
            if alpha < 200:
              self.safePutPixel(imBoard,(x, y), territoryDividerGrey)   
     
    drawEdgeBorders(imFill)
    drawEdgeBorders(imBoard) 
        
    imFill2.paste(imFill, (wallHalfWidth, wallHalfWidth))
    imBoard2.paste(imBoard, (wallHalfWidth, wallHalfWidth))


    imFill2.save(filePath + "-FILL.png")
    imBoard2.save(filePath + "-Board.png")
    
    imFog = Image.new("RGB", ( self.cols*self.colWidth,self.rows*self.rowHeight), (64,64,64))
    imFog2 = Image.new("RGB", ( self.cols*self.colWidth+2*wallHalfWidth,self.rows*self.rowHeight+2*wallHalfWidth), (64,64,64))
    self.createCloudPNG(imFog)
    #print "tet"
    '''
    for x in range( self.cols*self.colWidth):
      for y in range (self.rows*self.rowHeight):
        
        shift = (x-y + int(random.random()*32)) % 64
        #if (x-y) < 0:
        #  shift *= -1      
        c = 64 + shift
        color = (c,c,c)
        if random.random() < .02:
          self.safePutPixel(imFog,(x, y), color)
          rrandom = int(20*random.random())
          crandom = int(20*random.random())
          randomColor = random.random() < .5
          for r1 in range(rrandom):
            for c1 in range(crandom):
              #print "tet"
              s1 = 96*20 / int(sqrt(r1*r1+c1*c1)+20)
              if randomColor:
                s1 *= -1
              color = (c+s1,c+s1,c+s1)
              self.safePutPixel(imFog,(x+c1, y+r1), color)
              self.safePutPixel(imFog,(x+c1, y-r1), color)
              self.safePutPixel(imFog,(x-c1, y+r1), color)
              self.safePutPixel(imFog,(x-c1, y-r1), color)
    '''
    
    ''' 
    abstract rectangles
    maxSize = 45
    for ix in range(15 * self.cols * self.rows):
      perDone = ix*ix / float(15*self.cols * self.rows*15*self.cols * self.rows)
      c = 192 - int(random.random()*128)
      color = (c,c,c)
      #fiftyfifty = random.random() < .5
      xsize = int(maxSize * (1-perDone) + random.random() * 10)
      ysize = int(maxSize * (1-perDone) + random.random() * 10)
      x =  int(random.random()*self.cols*self.colWidth)
      y =  int(random.random()*self.rows*self.rowHeight)
      for x1 in range(xsize):
        for y1 in range(ysize):
          self.safePutPixel(imFog,(x + x1, y + y1), color)
              #print "tet"
    '''
    imFog2.paste(imFog, (wallHalfWidth, wallHalfWidth))
    imFog2.save(filePath + "-FOG.png")
    
    self.moveTerritories((2*wallHalfWidth, 2*wallHalfWidth))

  def fillWithRandomWalk(self):
    
    self.addRandomWalk(-1,-1)
    print "TRY AGAIN"
    while(self.countTerritoriesWithBorders(0) > 0):
      print "TRY AGAIN!"
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
            ah, but is it actually created multiple times?  I think addBorder, checks & will not create.
    """
    print "begin addRandomWalk"
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
    
    def addRandomFeature(rFrom,cFrom,rTo,cTo):
      
      feature = random.choice(self.features)
      #oldGrowthPoints = growthPoints.copy()
      print "attempting to add feature",feature,(rFrom,cFrom,rTo,cTo)
      dx = cTo - cFrom
      dy = rTo - rFrom      
      for step in feature:
        if step == 'r':
          (dx,dy) = (dy,-dx)  # these might be backwards. Depends on if up/down is increasing... whatever
        if step == 'l':
          (dx,dy) = (-dy, dx)

        cTo = cFrom + dx
        rTo = rFrom + dy
        if self.doWrap:
          rTo = self.wrapR(rTo)
          cTo = self.wrapC(cTo)
        else:
          if not self.inBorders((rTo, cTo)):
            print "{},{} out of borders - in feature add".format(rTo,cTo)
            #growthPoints.add((rFrom,cFrom))
            #growthPoints = oldGrowthPoints.copy()
            return

        print "next feature step",(rFrom,cFrom,rTo,cTo)
        attemptTerritoryAdd(rFrom,cFrom,rTo,cTo,grow=False)
        (rFrom,cFrom) = (rTo,cTo)
      #growthPoints = oldGrowthPoints.copy()
          
              
    def attemptTerritoryAdd(rFrom,cFrom,rTo,cTo,grow=True):
      
      if self.doWrap:
        rTo = self.wrapR(rTo)
        cTo = self.wrapC(cTo)
      else:
        if not self.inBorders((rTo, cTo)):
          print "{},{} out of borders".format(rTo,cTo)
          growthPoints.add((rFrom,cFrom))
          return
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
            if grow:
              growthPoints.add((rFrom,cFrom))  #add this point back again for another try
            print "target already has borders, connection rejection - try again from {},{}".format(rFrom,cFrom)
          else:             
            if  random.random() > self.chanceToDeadEnd:
              print "attempting border add: {},{} <-> {},{}".format(rFrom,cFrom,rTo,cTo)
              if not self.addBorder((rFrom, cFrom),(rTo, cTo)): #border already existed
                if fromBorders < 3:
                  if grow:                  
                    growthPoints.add((rFrom,cFrom))
                  print "added new border from {},{} to {},{} - continuing".format(rFrom, cFrom,rTo, cTo)
                else:
                  print "target ({},{}) already has 3+ borders".format(rFrom,cFrom)
              else:    
                print "border already existed from {},{} to {},{}".format(rFrom, cFrom,rTo, cTo)
            else:
              print "random deadend"
        else:
          self.addBorder((rFrom, cFrom),(rTo, cTo))
          if grow:
            growthPoints.add((rTo,cTo))
          print "added new border from {},{} to {},{} - autocontinue".format(rFrom, cFrom,rTo, cTo)
          if random.random() < self.branchingFactor:
              if grow:
                growthPoints.add((rFrom,cFrom))
              print "decided to branch, adding {},{} as growth point".format(rFrom, cFrom)
              
      else:
        # add growth point back on, if we couldn't grow from here.
        if grow:
          growthPoints.add((rFrom,cFrom))
          print "to territory doesnt exist, try again from {},{}".format(rFrom,cFrom)
      
      print "done with attempt Territory Add"                
    
    while(len(growthPoints) > 0):      
      (rF, cF) = growthPoints.pop()
      rnd = random.random()
      print "growing at",rF,cF,growthPoints         
      
      if int(rnd*100) % 2 == 0:
        if rnd < .25:
          addRandomFeature(rF, cF, rF, cF-1)          
        elif rnd < .5:
          addRandomFeature(rF, cF, rF,cF+1)
        elif rnd < .75:
          addRandomFeature(rF, cF, rF+1,cF)
        else:
          addRandomFeature(rF, cF, rF-1, cF)
      else:
        if rnd < .25:
          attemptTerritoryAdd(rF, cF, rF, cF-1)          
        elif rnd < .5:
          attemptTerritoryAdd(rF, cF, rF,cF+1)
        elif rnd < .75:
          attemptTerritoryAdd(rF, cF, rF+1,cF)
        else:
          attemptTerritoryAdd(rF, cF, rF-1, cF)
    
    print "done with growth points"    
      
      

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
  originalXML='//DISKSTATION/data/wargear development/Maze/Random Mazes(7).xml'
  wgmap.loadMapFromFile(originalXML)
  print "loading from "+originalXML
  wgmap.doWrap = False;
  for mazeType in ["LineOfSight",""]:
    '''
    #for size in range(8,21,4):
    for size in [8]:
      if (size <= 12):
        territoryWidth = 40
      elif (size > 16):
        territoryWidth = 30
      else:
        territoryWidth = 35
    '''
    
    # Avg 1st round bonus (for 1v1);
    #8,12,16.24,36
    # 64, 144, 256, 480, 720
    Afrbs = [6,14,24,40,67]
    
    # lets assume when you go to 3 player, bonus are reduced to 55%
    Afrbs =  [x * .55 for x in Afrbs]
      
    # crlen = sqrt(cols*rows)
    # min # of territories = 1.5 per crlen
    # Total territories = crlen*crlen   
    # P players 
    # territories for each player (low neutrals) = crlen*crlen/(P + .5) 
    # need at least 1.5 * crlen territories 
    # so crlen*crlen / (P + .5) > 1.5 * crlen
    # crlen / (P + .5) > 1.5
    # crlen > 1.5 * (P + .5) 
    # P + .5 <  crlen / 1.5
    # P < crlen / 1.5 - .5
    
    # for min 1.5/crlen
    """
    for 8.0 P <  4.83333333333
  for 12.0 P <  7.5
  for 16.0 P <  10.1666666667
  for 21.9089023002 P <  14.1059348668
  for 26.83281573 P <  17.38854382
     """
  
  
    """
  1.25
  for 8.0 P <  5.9
  for 12.0 P <  9.1
  for 16.0 P <  12.3
  for 21.9089023002 P <  17.0271218402
  for 26.83281573 P <  20.966252584
  
    crlens2 = [64, 144, 256, 480, 720]
    for crlen2 in crlens2:
      crlen = sqrt(crlen2)
      print "for " + str(crlen) + " P < ", crlen / 1.25 - .5
      
    exit()
    """
    # cards 2,3,3,3,3...
    # bonus 4+(0,.25,.35,.35.,,,)
    #<rules boardid="6320" card_switch="On" card_escalation="c2" card_capture="On" card_non_empty="On" card_max_accrual="5" card_start="1" card_increment="2" card_reset="0" card_rampup_value="0" card_rampup_amount="0" card_acount="18" card_bcount="18" card_ccount="18" card_wcount="2" teamplay_enabled="Yes" team_vision="On" team_unit_placement="On" team_unit_transfer="On" team_card_transfer="Off" attacker_dice_sides="6" defender_dice_sides="6" attack_chance="60" defend_chance="75" resolution_type="0" return_to_placement="Off" return_to_attack="Off" num_attacks="Unlimited" num_fortifies="8" fortify_type="connected" multiple_attack="On" bonus_multiplier="1" bonus_per_x_territories="6" min_bonus_units="4" elimination_bonus="8" reserves_capture="On" reinforce_allow="Unlimited" turn_order="seat" max_reserve_units="Unlimited" max_territory_units="Unlimited" initial_setup="Random" capital_cities="Off" capital_capture="On" capital_assimilation="0" capital_destroy_unallocated="On" initial_units_type="Territory" initial_units_count="3" decrement_initial="5" decrement_floor="20" initial_territory_selection="Automatic" initial_unit_placement="Automatic" neutral_count="Low" abandon_territories="Off" abandon_revert="Immediately" fog="Medium" fog_override="Yes" game_history="Show" lock_seat_colors="Off" lock_seat_order="Off" lock_starting_bonus="0" allow_seat_selection="None" predefined_teams="Off" reinforce_attack="Off" unit_pumping="On" fatigue_amount="0" fatigue_turns="1" order_overloading="Off" order_limit="Unlimited" team_factory_production="0" factory_auto_assign="0" lock_win_condition="0" /><colors><color color_name="Red" color_code="16711680" text_code="16777215" team_name="0" starting_cards="0" starting_bonus="1" seat="1" /><color color_name="Green" color_code="32768" text_code="16777215" team_name="0" starting_cards="0" starting_bonus="2" seat="2" /><color color_name="Blue" color_code="4474111" text_code="16777215" team_name="0" starting_cards="0" starting_bonus="2" seat="3" /><color color_name="White" color_code="16777215" text_code="0" team_name="0" starting_cards="0" starting_bonus="3" seat="4" /><color color_name="Orange" color_code="16753920" text_code="0" team_name="0" starting_cards="0" starting_bonus="3" seat="5" /><color color_name="Purple" color_code="8388736" text_code="16777215" team_name="0" starting_cards="0" starting_bonus="3" seat="6" /><color color_name="Brick Red" color_code="10027008" text_code="16777215" team_name="0" starting_cards="0" starting_bonus="4" seat="7" /><color color_name="Cyan" color_code="65535" text_code="0" team_name="0" starting_cards="0" starting_bonus="4" seat="8" /><color color_name="Lime" color_code="65280" text_code="0" team_name="0" starting_cards="0" starting_bonus="4" seat="9" /><color color_name="Pink" color_code="16761035" text_code="0" team_name="0" starting_cards="0" starting_bonus="4" seat="10" /><color color_name="Yellow" color_code="16776960" text_code="0" team_name="0" starting_cards="0" starting_bonus="5" seat="11" /><color color_name="Navy" color_code="1118592" text_code="16777215" team_name="0" starting_cards="0" starting_bonus="5" seat="12" /><color color_name="Brown" color_code="10053120" text_code="16777215" team_name="0" starting_cards="0" starting_bonus="5" seat="13" /><color color_name="Violet" color_code="15631086" text_code="0" team_name="0" starting_cards="0" starting_bonus="5" seat="14" /><color color_name="Olive" color_code="6723840" text_code="0" team_name="0" starting_cards="0" starting_bonus="6" seat="15" /><color color_name="SkyBlue" color_code="8900346" text_code="0" team_name="0" starting_cards="0" starting_bonus="6" seat="16" /></colors>
    SB = []
    card_start = []
    baseBonus = 4
    b1 = .25
    b2 = .35
    for ix,afrb in  enumerate(Afrbs):
      #SB.append([baseBonus,baseBonus+b1*afrb,baseBonus+b2*afrb,baseBonus+b2*afrb,baseBonus+b2*afrb,baseBonus+b2*afrb,baseBonus+b2*afrb,baseBonus+b2*afrb,baseBonus+b2*afrb,baseBonus+b2*afrb,baseBonus+b2*afrb,baseBonus+b2*afrb,baseBonus+b2*afrb,baseBonus+b2*afrb,baseBonus+b2*afrb,baseBonus+b2*afrb,])
      card_start.append(round(.55*afrb)+2)
    AP = [("2,3,4"),("2,3,4,5,6"),("3,4,5,6,7,8,9,10"),("3,4,5,6,7,8,9,10,11,12,13,14"),("3,4,5,6,7,8,9,10,11,12,13,14,15,16")]
    
    SB = [[2,7,8,8],[3,8,9,9,9,9],[6,9,13,13,13,13,13,13,13,13,13,13,13,13],[8,11,17,17,17,17,17,17,17,17,17,17,17,17,17],[12,16,24,24,24,24,24,24,24,24,24,24,24,24,24,24]]
    for (wgmap.rows,wgmap.cols) in [(8,8), (12,12), (16,16), (20,24), (20,36)]:  
    #for (wgmap.rows,wgmap.cols) in [(8,8)]:
      if (wgmap.cols == 8):
        wgmap.setAvailablePlayers(AP[0])      
        wgmap.setSeatBonuses(SB[0])    
        wgmap.setCardBonuses(card_start=card_start[0], card_increment=2)
        wgmap.setEliminationBonus(Afrbs[0]+5)
      elif (wgmap.cols == 12):
        wgmap.setAvailablePlayers(AP[1])
        wgmap.setSeatBonuses(SB[1])
        wgmap.setCardBonuses(card_start=card_start[1], card_increment=2)
        wgmap.setEliminationBonus(Afrbs[1]+5)
      elif (wgmap.cols == 16):
        wgmap.setAvailablePlayers(AP[2])
        wgmap.setSeatBonuses(SB[2])
        wgmap.setCardBonuses(card_start=card_start[2], card_increment=1)
        wgmap.setEliminationBonus(Afrbs[2]+5)
      elif (wgmap.cols == 24):
        wgmap.setAvailablePlayers(AP[3])
        wgmap.setSeatBonuses(SB[3])
        wgmap.setCardBonuses(card_start=card_start[3], card_increment=1)
        wgmap.setEliminationBonus(Afrbs[3]+5)
      elif (wgmap.cols == 36):
        wgmap.setAvailablePlayers(AP[4])
        wgmap.setSeatBonuses(SB[4])
        wgmap.setCardBonuses(card_start=card_start[4], card_increment=1)
        wgmap.setEliminationBonus(Afrbs[4]+5)
   
      territoryWidth = 35
      wgmap.setReturnToAttack("On")
      wgmap.setReturnToPlace("Off")
      if mazeType == "LineOfSight":
        
        lineOfSight=True
      else:
        wgmap.setFogOverride("Yes")
        lineOfSight=False
      
      #wgmap.setDefaultParameters()
      wgmap.setOpenParameters()
      extension = "-" + mazeType
      wgfile = '//DISKSTATION/data/wargear development/Maze/RandomMaze'+str(wgmap.rows) + 'x' + str(wgmap.cols) + extension
      wgmap.createMazeGame(wgfile,territoryWidth,territoryWidth,lineOfSight)
      
      wgmap.setWideOpenParameters()
      extension = "-" + mazeType + "-Open"    
      wgfile = '//DISKSTATION/data/wargear development/Maze/RandomMaze'+str(wgmap.rows) + 'x' + str(wgmap.cols) + extension
      wgmap.createMazeGame(wgfile,territoryWidth,territoryWidth,lineOfSight)
     
      wgmap.setTighterParameters()
      extension = "-" + mazeType + "-Tight"    
      wgfile = '//DISKSTATION/data/wargear development/Maze/RandomMaze'+str(wgmap.rows) + 'x' + str(wgmap.cols) + extension
      wgmap.createMazeGame(wgfile,territoryWidth,territoryWidth,lineOfSight)
    

if __name__ == '__main__':
  pass
