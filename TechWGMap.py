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

class TechWGMap(WGMap):
  """
  Extends WGMap.
  A convenient way to organize all the stuff for my 'Invention' map with the tech tree.
  """
  # todo: all this is wrong, because getContinentMembersFromName() returns
  # a string instead of a set.
  def doFullSetup(self):
      
    self.loadIDSets()    
    self.setupTechMapScience()
    self.setupTechMapLife()
    self.setupTechMapWar()
    self.setupTechPointFactories()
    
 
    
 
  def loadIDSets(self):
    self.USATerritories = set(self.getContinentMembersFromName("USA").split(','))
    self.ChinaTerritories = set(self.getContinentMembersFromName("China").split(','))
    self.UKTerritories = set(self.getContinentMembersFromName("UK").split(','))
    self.SAfricaTerritories = set(self.getContinentMembersFromName("South Africa").split(','))
    
    self.NATerritories = set(self.getContinentMembersFromName("North America").split(','))
    self.AsiaTerritories = set(self.getContinentMembersFromName("Asia").split(','))
    self.EuropeTerritories = set(self.getContinentMembersFromName("Europe").split(','))
    self.AfricaTerritories = set(self.getContinentMembersFromName("Africa").split(','))
    
    self.WorldTerritories = set()
    self.WorldTerritories |= self.NATerritories | self.AsiaTerritories | self.EuropeTerritories | self.AfricaTerritories
    self.WorldTerritories |= set(self.getContinentMembersFromName("Oceania").split(','))
    self.WorldTerritories |= set(self.getContinentMembersFromName("South America").split(','))

    self.DC = set()
    self.DC.add(self.getTerritoryIDFromName("DC"))
    self.Beijing = set()
    self.Beijing.add(self.getTerritoryIDFromName("Beijing"))
    self.Capetown = set()
    self.Capetown.add(self.getTerritoryIDFromName("Capetown"))
    self.London = set()
    self.London.add(self.getTerritoryIDFromName("London"))
    
    self.Capitals = set()
    self.Capitals |=  self.DC
    self.Capitals |=  self.Beijing
    self.Capitals |=  self.Capetown
    self.Capitals |=  self.London

    LabNames = set()
    LabNames.add("Southern Alaska")
    LabNames.add("Southwest USA")
    LabNames.add("North Brazil")
    LabNames.add("Kitaa")
    LabNames.add("Poland")
    LabNames.add("Algeria")
    LabNames.add("Congo")
    LabNames.add("Saudi Arabia")
    LabNames.add("Siberia")
    LabNames.add("Western Australia")
    
    self.LabTerritories = set(self.getTerritoryIDsFromNames(LabNames))
        
    self.AfricaFlask = self.getTerritoryIDFromName("Africa Flask")
    self.ChinaFlask = self.getTerritoryIDFromName("China Flask")
    self.USAFlask = self.getTerritoryIDFromName("USA Flask")
    self.UKFlask = self.getTerritoryIDFromName("UK Flask")
    
    self.AfricaHome = set()
    self.AfricaHome.add(self.getTerritoryIDFromName("South Africa"))
    self.ChinaHome = set()
    self.ChinaHome.add(self.getTerritoryIDFromName("North China"))
    self.USAHome = set()
    self.USAHome.add(self.getTerritoryIDFromName("Northeast USA"))
    self.UKHome = set()
    self.UKHome.add(self.getTerritoryIDFromName("Britain"))
    
 
  def setupTechPointFactories(self):
    
    USAFlask = self.getTerritoryElement("USA Flask")
    DC = self.getTerritoryElement("DC")
    continentName = "DC Tech Point"
    self.addContinent(continentName, set([DC.getAttribute("tid")]), "2", USAFlask.getAttribute("tid"), factoryType="AutoCapture")
    
    continentName = "USA Tech Points"
    memberList = ",".join(self.USATerritories | set([DC.getAttribute("tid")]))
    self.addContinent(continentName, memberList, "3", USAFlask.getAttribute("tid"), factoryType="AutoCapture")

    continentName = "NA Tech Points"
    memberList = ",".join(self.NATerritories | set([DC.getAttribute("tid")]))
    self.addContinent(continentName, memberList, "4", USAFlask.getAttribute("tid"), factoryType="AutoCapture")
    
    UKFlask = self.getTerritoryElement("UK Flask")
    lndn = self.getTerritoryElement("London")
    continentName = "London Tech Point"
    self.addContinent(continentName, set([lndn.getAttribute("tid")]), "2", UKFlask.getAttribute("tid"), factoryType="AutoCapture")
    
    continentName = "UK Tech Points"
    memberList = ",".join(self.UKTerritories | set([lndn.getAttribute("tid")]))
    self.addContinent(continentName, memberList, "3", UKFlask.getAttribute("tid"), factoryType="AutoCapture")
    
    continentName = "Europe Tech Points"
    memberList = ",".join(self.EuropeTerritories | set([lndn.getAttribute("tid")]))
    self.addContinent(continentName, memberList, "4", UKFlask.getAttribute("tid"), factoryType="AutoCapture")
    
    ChinaFlask = self.getTerritoryElement("China Flask")
    BJ = self.getTerritoryElement("Beijing")
    continentName = "Beijing Tech Point"
    self.addContinent(continentName, set([BJ.getAttribute("tid")]), "2", ChinaFlask.getAttribute("tid"), factoryType="AutoCapture")
    
    continentName = "China Tech Points"
    memberList = ",".join(self.ChinaTerritories | set([BJ.getAttribute("tid")]))
    self.addContinent(continentName, memberList, "3", ChinaFlask.getAttribute("tid"), factoryType="AutoCapture")
    
    continentName = "Asia Tech Points"
    memberList = ",".join(self.AsiaTerritories| set([BJ.getAttribute("tid")]))
    self.addContinent(continentName, memberList, "4", ChinaFlask.getAttribute("tid"), factoryType="AutoCapture")
    
    AfricaFlask = self.getTerritoryElement("Africa Flask")
    continentName = "Capetown Tech Point"
    Cpt = self.getTerritoryElement("Capetown")
    self.addContinent(continentName, set([Cpt.getAttribute("tid")]), "2", AfricaFlask.getAttribute("tid"), factoryType="AutoCapture")
    
    continentName = "South Africa Tech Points"
    memberList = ",".join(self.SAfricaTerritories | set([Cpt.getAttribute("tid")]))
    self.addContinent(continentName, memberList, "3", AfricaFlask.getAttribute("tid"), factoryType="AutoCapture")
    
    continentName = "Africa Tech Points"
    memberList = ",".join(self.AfricaTerritories | set([Cpt.getAttribute("tid")]))
    self.addContinent(continentName, memberList, "4", AfricaFlask.getAttribute("tid"), factoryType="AutoCapture")

    DC = self.getTerritoryIDFromName("DC")
    Beijing = self.getTerritoryIDFromName("Beijing")
    Capetown = self.getTerritoryIDFromName("Capetown")
    London = self.getTerritoryIDFromName("London")

    # these were getting set to Standard instead of AutoCapture  I don't know why
    print("lab territories",self.LabTerritories)    
    self.addCollectorContinents(self.LabTerritories,individualBonus=1,pairBonus=1,factory=self.AfricaFlask,nameSuffix="_Africa-LAB",additionalMembers=[Capetown], factoryType="AutoCapture")
    self.addCollectorContinents(self.LabTerritories,individualBonus=1,pairBonus=1,factory=self.USAFlask,nameSuffix="_USA-LAB",additionalMembers=[DC], factoryType="AutoCapture")
    self.addCollectorContinents(self.LabTerritories,individualBonus=1,pairBonus=1,factory=self.UKFlask,nameSuffix="_UK-LAB",additionalMembers=[London], factoryType="AutoCapture")
    self.addCollectorContinents(self.LabTerritories,individualBonus=1,pairBonus=1,factory=self.ChinaFlask,nameSuffix="_China-LAB",additionalMembers=[Beijing], factoryType="AutoCapture")
    
    

    
  def setupTechMapLife(self):
    USAGranary = self.getTerritoryIDFromName("USA Granary")
    ChinaGranary = self.getTerritoryIDFromName("China Granary")
    UKGranary = self.getTerritoryIDFromName("UK Granary")
    AfricaGranary = self.getTerritoryIDFromName("Africa Granary")
    
    USAConscription = self.getTerritoryIDFromName("USA Conscription")
    ChinaConscription = self.getTerritoryIDFromName("China Conscription")
    UKConscription = self.getTerritoryIDFromName("UK Conscription")
    AfricaConscription = self.getTerritoryIDFromName("Africa Conscription")
    
    USASanitation = self.getTerritoryIDFromName("USA Sanitation")
    ChinaSanitation = self.getTerritoryIDFromName("China Sanitation")
    UKSanitation = self.getTerritoryIDFromName("UK Sanitation")
    AfricaSanitation = self.getTerritoryIDFromName("Africa Sanitation")
    
    USANationalism = self.getTerritoryIDFromName("USA Nationalism")
    ChinaNationalism = self.getTerritoryIDFromName("China Nationalism")
    UKNationalism = self.getTerritoryIDFromName("UK Nationalism")
    AfricaNationalism = self.getTerritoryIDFromName("Africa Nationalism")
    
    USAMedicine = self.getTerritoryIDFromName("USA Medicine")
    ChinaMedicine = self.getTerritoryIDFromName("China Medicine")
    UKMedicine = self.getTerritoryIDFromName("UK Medicine")
    AfricaMedicine = self.getTerritoryIDFromName("Africa Medicine")
    
    USAPropaganda = self.getTerritoryIDFromName("USA Propaganda")
    ChinaPropaganda = self.getTerritoryIDFromName("China Propaganda")
    UKPropaganda = self.getTerritoryIDFromName("UK Propaganda")
    AfricaPropaganda = self.getTerritoryIDFromName("Africa Propaganda")
    
    DC = self.getTerritoryIDFromName("DC")
    Beijing = self.getTerritoryIDFromName("Beijing")
    Capetown = self.getTerritoryIDFromName("Capetown")
    London = self.getTerritoryIDFromName("London")
    
    self.addContinent("USA Granary",set([DC, USAGranary]),"1",DC)
    self.addContinent("UK Granary",set([London, UKGranary]),"1",London)
    self.addContinent("China Granary",set([Beijing, ChinaGranary]),"1",Beijing)
    self.addContinent("Africa Granary",set([Capetown, AfricaGranary]),"1",Capetown)
    
    self.addContinent("USA Conscription",set([DC, USAConscription]),"2",DC)
    self.addContinent("UK Conscription",set([London, UKConscription]),"2",London)
    self.addContinent("China Conscription",set([Beijing, ChinaConscription]),"2",Beijing)
    self.addContinent("Africa Conscription",set([Capetown, AfricaConscription]),"2",Capetown)
    
    for USAT in self.USATerritories | set([DC]):
      te = self.getTerritoryElement(USAT)
      continentName = "USA Nationalism - " +  te.getAttribute("name")
      memberList = ",".join([te.getAttribute("tid"), USANationalism, DC])
      self.addContinent(continentName, memberList, "2", te.getAttribute("tid"))
        
    # +2 for nation
    for USAT in self.USATerritories | set([DC]):
      te = self.getTerritoryElement(USAT)
      continentName = "USA Sanitation - " +  te.getAttribute("name")
      memberList = ",".join([te.getAttribute("tid"), USASanitation, DC])
      self.addContinent(continentName, memberList, "1", te.getAttribute("tid"))
    
    for WT in self.NATerritories | set([DC]):
      te = self.getTerritoryElement(WT)
      continentName = "USA Medicine - " +  te.getAttribute("name")
      memberList = ",".join([te.getAttribute("tid"), USAMedicine, DC])
      self.addContinent(continentName, memberList, "1", te.getAttribute("tid"))
    
    for WT in self.NATerritories | set([DC]):
      print("WT",WT)
      te = self.getTerritoryElement(WT)
      print("tid",te.getAttribute("tid"))
      print("usap:",USAPropaganda)
      continentName = "USA Propaganda - " +  te.getAttribute("name")
      memberList = ",".join([te.getAttribute("tid"), USAPropaganda, DC])
      self.addContinent(continentName, memberList, "2", te.getAttribute("tid"))
    
    
    for CT in self.ChinaTerritories | set([Beijing]):
      te = self.getTerritoryElement(CT)
      continentName = "China Nationalism - " +  te.getAttribute("name")
      memberList = ",".join([te.getAttribute("tid"), ChinaNationalism, Beijing])
      self.addContinent(continentName, memberList, "2", te.getAttribute("tid"))
    
    for CT in self.ChinaTerritories | set([Beijing]):
      te = self.getTerritoryElement(CT)
      continentName = "China Sanitation - " +  te.getAttribute("name")
      memberList = ",".join([te.getAttribute("tid"), ChinaSanitation, Beijing])
      self.addContinent(continentName, memberList, "1", te.getAttribute("tid"))
    
    for WT in self.AsiaTerritories | set([Beijing]):
      te = self.getTerritoryElement(WT)
      continentName = "China Medicine - " +  te.getAttribute("name")
      memberList = ",".join([te.getAttribute("tid"), ChinaMedicine, Beijing])
      self.addContinent(continentName, memberList, "1", te.getAttribute("tid"))
    
    for WT in self.AsiaTerritories | set([Beijing]):
      te = self.getTerritoryElement(WT)
      continentName = "China Propaganda - " +  te.getAttribute("name")
      memberList = ",".join([te.getAttribute("tid"), ChinaPropaganda, Beijing])
      self.addContinent(continentName, memberList, "2", te.getAttribute("tid"))
    
    
    for AT in self.SAfricaTerritories | set([Capetown]):
      te = self.getTerritoryElement(AT)
      continentName = "Africa Nationalism - " +  te.getAttribute("name")
      memberList = ",".join([te.getAttribute("tid"), AfricaNationalism, Capetown])
      self.addContinent(continentName, memberList, "2", te.getAttribute("tid"))
    
    for AT in self.SAfricaTerritories | set([Capetown]):
      te = self.getTerritoryElement(AT)
      continentName = "Africa Sanitation - " +  te.getAttribute("name")
      memberList = ",".join([te.getAttribute("tid"), AfricaSanitation, Capetown])
      self.addContinent(continentName, memberList, "1", te.getAttribute("tid"))
    
    for WT in self.AfricaTerritories | set([Capetown]):
      te = self.getTerritoryElement(WT)
      continentName = "Africa Medicine - " +  te.getAttribute("name")
      memberList = ",".join([te.getAttribute("tid"), AfricaMedicine, Capetown])
      self.addContinent(continentName, memberList, "1", te.getAttribute("tid"))
    
    for WT in self.AfricaTerritories | set([Capetown]):
      te = self.getTerritoryElement(WT)
      continentName = "Africa Propaganda - " +  te.getAttribute("name")
      memberList = ",".join([te.getAttribute("tid"), AfricaPropaganda, Capetown])
      self.addContinent(continentName, memberList, "2", te.getAttribute("tid"))
    
    
    for UKT in self.UKTerritories | set([London]):
      te = self.getTerritoryElement(UKT)
      continentName = "UK Sanitation - " +  te.getAttribute("name")
      memberList = ",".join([te.getAttribute("tid"), UKSanitation, London])
      self.addContinent(continentName, memberList, "1", te.getAttribute("tid"))
    
    for UKT in self.UKTerritories | set([London]):
      te = self.getTerritoryElement(UKT)
      continentName = "UK Nationalism - " +  te.getAttribute("name")
      memberList = ",".join([te.getAttribute("tid"), UKNationalism, London])
      self.addContinent(continentName, memberList, "2", te.getAttribute("tid"))
    
    for WT in self.EuropeTerritories | set([London]):
      te = self.getTerritoryElement(WT)
      continentName = "UK Medicine - " +  te.getAttribute("name")
      memberList = ",".join([te.getAttribute("tid"), UKMedicine, London])
      self.addContinent(continentName, memberList, "1", te.getAttribute("tid"))
    
    for WT in self.EuropeTerritories | set([London]):
      te = self.getTerritoryElement(WT)
      continentName = "UK Propaganda - " +  te.getAttribute("name")
      memberList = ",".join([te.getAttribute("tid"), UKPropaganda, London])
      self.addContinent(continentName, memberList, "2", te.getAttribute("tid"))
    
    
    
    
    
  def setupTechMapScience(self):
    
    USARadar = self.getTerritoryIDFromName("USA Radar")
    ChinaRadar = self.getTerritoryIDFromName("China Radar")
    UKRadar = self.getTerritoryIDFromName("UK Radar")
    AfricaRadar = self.getTerritoryIDFromName("Africa Radar")
    
    USASatellite = self.getTerritoryIDFromName("USA Satellite")
    ChinaSatellite = self.getTerritoryIDFromName("China Satellite")
    UKSatellite = self.getTerritoryIDFromName("UK Satellite")
    AfricaSatellite = self.getTerritoryIDFromName("Africa Satellite")
  
    USAPlane = self.getTerritoryIDFromName("USA Plane")
    ChinaPlane = self.getTerritoryIDFromName("China Plane")
    UKPlane = self.getTerritoryIDFromName("UK Plane")
    AfricaPlane = self.getTerritoryIDFromName("Africa Plane")
    
    USAJet = self.getTerritoryIDFromName("USA Jet")
    ChinaJet = self.getTerritoryIDFromName("China Jet")
    UKJet = self.getTerritoryIDFromName("UK Jet")
    AfricaJet = self.getTerritoryIDFromName("Africa Jet")
    
   
  

    self.addBordersToSet(USARadar, self.NATerritories | self.DC, 'One-way', "View Only")
    self.addBordersToSet(AfricaRadar, self.AfricaTerritories | self.Capetown , 'One-way', "View Only")
    self.addBordersToSet(ChinaRadar, self.AsiaTerritories | self.Beijing, 'One-way', "View Only")
    self.addBordersToSet(UKRadar, self.EuropeTerritories | self.London, 'One-way', "View Only")
  
    self.addBordersToSet(USASatellite, self.WorldTerritories, 'One-way', "View Only")
    self.addBordersToSet(AfricaSatellite, self.WorldTerritories, 'One-way', "View Only")
    self.addBordersToSet(ChinaSatellite, self.WorldTerritories, 'One-way', "View Only")
    self.addBordersToSet(UKSatellite, self.WorldTerritories, 'One-way', "View Only")
  
    self.addBordersToSet(USAPlane,self.NATerritories | self.DC, 'Two-way', "Fortify Only")
    self.addBordersToSet(ChinaPlane,self.AsiaTerritories |  self.Beijing, 'Two-way', "Fortify Only")
    self.addBordersToSet(UKPlane,self.EuropeTerritories |self.London, 'Two-way', "Fortify Only")
    self.addBordersToSet(AfricaPlane,self.AfricaTerritories| self.Capetown, 'Two-way', "Fortify Only")
    
    self.addBordersToSet(USAJet,self.WorldTerritories | self.Capitals, 'Two-way', "Fortify Only")
    self.addBordersToSet(ChinaJet,self.WorldTerritories | self.Capitals, 'Two-way', "Fortify Only")
    self.addBordersToSet(UKJet,self.WorldTerritories | self.Capitals, 'Two-way', "Fortify Only")
    self.addBordersToSet(AfricaJet,self.WorldTerritories | self.Capitals, 'Two-way', "Fortify Only")
    
    
    
    
  
  def setupTechMapWar(self):
    USAArtillery = self.getTerritoryIDFromName("USA Artillery")
    ChinaArtillery = self.getTerritoryIDFromName("China Artillery")
    UKArtillery = self.getTerritoryIDFromName("UK Artillery")
    AfricaArtillery = self.getTerritoryIDFromName("Africa Artillery")
    
    USAMissile = self.getTerritoryIDFromName("USA Missile")
    ChinaMissile = self.getTerritoryIDFromName("China Missile")
    UKMissile = self.getTerritoryIDFromName("UK Missile")
    AfricaMissile = self.getTerritoryIDFromName("Africa Missile")
    
    USAICBM = self.getTerritoryIDFromName("USA ICBM")
    ChinaICBM = self.getTerritoryIDFromName("China ICBM")
    UKICBM = self.getTerritoryIDFromName("UK ICBM")
    AfricaICBM = self.getTerritoryIDFromName("Africa ICBM")
    
    USANuclearICBM = self.getTerritoryIDFromName("USA Nuclear ICBM")
    ChinaNuclearICBM = self.getTerritoryIDFromName("China Nuclear ICBM")
    UKNuclearICBM = self.getTerritoryIDFromName("UK Nuclear ICBM")
    AfricaNuclearICBM = self.getTerritoryIDFromName("Africa Nuclear ICBM")
    
    USAEspionage = self.getTerritoryIDFromName("USA Espionage")
    ChinaEspionage = self.getTerritoryIDFromName("China Espionage")
    UKEspionage = self.getTerritoryIDFromName("UK Espionage")
    AfricaEspionage = self.getTerritoryIDFromName("Africa Espionage")
    
    USAAssasination = self.getTerritoryIDFromName("USA Assasination")
    ChinaAssasination = self.getTerritoryIDFromName("China Assasination")
    UKAssasination = self.getTerritoryIDFromName("UK Assasination")
    AfricaAssasination = self.getTerritoryIDFromName("Africa Assasination")
                
    WarTech = set()
    Tech = set()
    Tech.add(self.getTerritoryIDFromName("USA Flight"))
    Tech.add(self.getTerritoryIDFromName("USA Radar"))
    Tech.add(self.getTerritoryIDFromName("USA Advanced Flight"))
    Tech.add(self.getTerritoryIDFromName("USA Satellite"))
    Tech.add(self.getTerritoryIDFromName("USA Computers"))
    Tech.add(self.getTerritoryIDFromName("USA Internet"))
    Tech.add(self.getTerritoryIDFromName("USA Granary"))
    Tech.add(self.getTerritoryIDFromName("USA Sanitation"))
    Tech.add(self.getTerritoryIDFromName("USA Conscription"))
    Tech.add(self.getTerritoryIDFromName("USA Nationalism"))
    Tech.add(self.getTerritoryIDFromName("USA Propaganda"))
    Tech.add(self.getTerritoryIDFromName("USA Medicine"))
    #Tech.add(self.getTerritoryIDFromName("DC"))
    WarTech.add(USAMissile)
    WarTech.add(USAArtillery)
    WarTech.add(USAICBM)
    WarTech.add(USANuclearICBM)
    WarTech.add(USAEspionage)
    WarTech.add(USAAssasination)
    Tech.add(self.getTerritoryIDFromName("China Flight"))
    Tech.add(self.getTerritoryIDFromName("China Radar"))
    Tech.add(self.getTerritoryIDFromName("China Advanced Flight"))
    Tech.add(self.getTerritoryIDFromName("China Satellite"))
    Tech.add(self.getTerritoryIDFromName("China Computers"))
    Tech.add(self.getTerritoryIDFromName("China Internet"))
    Tech.add(self.getTerritoryIDFromName("China Granary"))
    Tech.add(self.getTerritoryIDFromName("China Sanitation"))
    Tech.add(self.getTerritoryIDFromName("China Conscription"))
    Tech.add(self.getTerritoryIDFromName("China Nationalism"))
    Tech.add(self.getTerritoryIDFromName("China Propaganda"))
    Tech.add(self.getTerritoryIDFromName("China Medicine"))
    #Tech.add(self.getTerritoryIDFromName("Beijing"))
    WarTech.add(ChinaMissile)
    WarTech.add(ChinaArtillery)
    WarTech.add(ChinaICBM)
    WarTech.add(ChinaNuclearICBM)
    WarTech.add(ChinaEspionage)
    WarTech.add(ChinaAssasination)
        
    Tech.add(self.getTerritoryIDFromName("Africa Flight"))
    Tech.add(self.getTerritoryIDFromName("Africa Radar"))
    Tech.add(self.getTerritoryIDFromName("Africa Advanced Flight"))
    Tech.add(self.getTerritoryIDFromName("Africa Satellite"))
    Tech.add(self.getTerritoryIDFromName("Africa Computers"))
    Tech.add(self.getTerritoryIDFromName("Africa Internet"))
    Tech.add(self.getTerritoryIDFromName("Africa Granary"))
    Tech.add(self.getTerritoryIDFromName("Africa Sanitation"))
    Tech.add(self.getTerritoryIDFromName("Africa Conscription"))
    Tech.add(self.getTerritoryIDFromName("Africa Nationalism"))
    Tech.add(self.getTerritoryIDFromName("Africa Propaganda"))
    Tech.add(self.getTerritoryIDFromName("Africa Medicine"))
    #Tech.add(self.getTerritoryIDFromName("Capetown"))
    WarTech.add(AfricaMissile)
    WarTech.add(AfricaArtillery)
    WarTech.add(AfricaICBM)
    WarTech.add(AfricaNuclearICBM)
    WarTech.add(AfricaEspionage)
    WarTech.add(AfricaAssasination)
        
    Tech.add(self.getTerritoryIDFromName("UK Flight"))
    Tech.add(self.getTerritoryIDFromName("UK Radar"))
    Tech.add(self.getTerritoryIDFromName("UK Advanced Flight"))
    Tech.add(self.getTerritoryIDFromName("UK Satellite"))
    Tech.add(self.getTerritoryIDFromName("UK Computers"))
    Tech.add(self.getTerritoryIDFromName("UK Internet"))
    Tech.add(self.getTerritoryIDFromName("UK Granary"))
    Tech.add(self.getTerritoryIDFromName("UK Sanitation"))
    Tech.add(self.getTerritoryIDFromName("UK Conscription"))
    Tech.add(self.getTerritoryIDFromName("UK Nationalism"))
    Tech.add(self.getTerritoryIDFromName("UK Propaganda"))
    Tech.add(self.getTerritoryIDFromName("UK Medicine"))
    #Tech.add(self.getTerritoryIDFromName("London"))
    WarTech.add(UKMissile)
    WarTech.add(UKArtillery)
    WarTech.add(UKICBM)
    WarTech.add(UKNuclearICBM)
    WarTech.add(UKEspionage)
    WarTech.add(UKAssasination)    
    
    AllHomes = self.USAHome|self.AfricaHome|self.ChinaHome|self.UKHome
    DefendableTerritories = self.LabTerritories | AllHomes
    AllNormalTerritories = self.WorldTerritories-DefendableTerritories
    
    
    print("homes",AllHomes)
    print("DefendableTerritories",DefendableTerritories)

    self.addBordersToSet(USAArtillery, (self.USATerritories-self.LabTerritories)-self.USAHome, 'One-way', 
                  "Artillery", "1")
    self.addBordersToSet(AfricaArtillery, self.SAfricaTerritories-self.LabTerritories-self.AfricaHome, 'One-way', 
                  "Artillery", "1")
    self.addBordersToSet(ChinaArtillery, self.ChinaTerritories-self.LabTerritories-self.ChinaHome, 'One-way', 
                  "Artillery", "1")
    self.addBordersToSet(UKArtillery, self.UKTerritories-self.LabTerritories-self.UKHome, 'One-way', 
                  "Artillery", "1")
    
    self.addBordersToSet(USAMissile, self.NATerritories-self.LabTerritories-self.USAHome, 'One-way', 
                  "Artillery", "1")
    self.addBordersToSet(AfricaMissile, self.AfricaTerritories-self.LabTerritories-self.AfricaHome, 'One-way', 
                  "Artillery", "1")
    self.addBordersToSet(ChinaMissile, self.AsiaTerritories-self.LabTerritories-self.ChinaHome, 'One-way', 
                  "Artillery", "1")
    self.addBordersToSet(UKMissile, self.EuropeTerritories-self.LabTerritories-self.UKHome, 'One-way', 
                  "Artillery", "1")
    
    self.addBordersToSet(USAICBM, AllNormalTerritories, 'One-way', 
                  "Artillery", "1")
    self.addBordersToSet(AfricaICBM,AllNormalTerritories, 'One-way', 
                  "Artillery", "1")
    self.addBordersToSet(ChinaICBM, AllNormalTerritories, 'One-way', 
                  "Artillery", "1")
    self.addBordersToSet(UKICBM, AllNormalTerritories, 'One-way', 
                  "Artillery", "1")
    
    
    self.addBordersToSet(USANuclearICBM, AllNormalTerritories, 'One-way', 
                  "Artillery", "2")
    self.addBordersToSet(AfricaNuclearICBM, AllNormalTerritories, 'One-way', 
                  "Artillery", "2")
    self.addBordersToSet(ChinaNuclearICBM, AllNormalTerritories, 'One-way', 
                  "Artillery", "2")
    self.addBordersToSet(UKNuclearICBM, AllNormalTerritories, 'One-way', 
                  "Artillery", "2")
    
    self.addBordersToSet(USAArtillery, self.USATerritories&(DefendableTerritories), 'One-way', 
                  "Artillery", "1", "1")
    self.addBordersToSet(AfricaArtillery, self.SAfricaTerritories&(DefendableTerritories), 'One-way', 
                  "Artillery", "1", "1")
    self.addBordersToSet(ChinaArtillery, self.ChinaTerritories&(DefendableTerritories), 'One-way', 
                  "Artillery", "1", "1")
    self.addBordersToSet(UKArtillery, self.UKTerritories&DefendableTerritories, 'One-way', 
                  "Artillery", "1", "1")
    
    self.addBordersToSet(USAMissile, self.NATerritories&DefendableTerritories, 'One-way', 
                  "Artillery", "1", "1")
    self.addBordersToSet(AfricaMissile, self.AfricaTerritories&DefendableTerritories, 'One-way', 
                  "Artillery", "1", "1")
    self.addBordersToSet(ChinaMissile, self.AsiaTerritories&DefendableTerritories, 'One-way', 
                  "Artillery", "1", "1")
    self.addBordersToSet(UKMissile, self.EuropeTerritories&DefendableTerritories, 'One-way', 
                  "Artillery", "1", "1")
    
    self.addBordersToSet(USAICBM, self.WorldTerritories&DefendableTerritories, 'One-way', 
                  "Artillery", "1", "1")
    self.addBordersToSet(AfricaICBM,self.WorldTerritories&DefendableTerritories, 'One-way', 
                  "Artillery", "1", "1")
    self.addBordersToSet(ChinaICBM, self.WorldTerritories&DefendableTerritories, 'One-way', 
                  "Artillery", "1", "1")
    self.addBordersToSet(UKICBM, self.WorldTerritories&DefendableTerritories, 'One-way', 
                  "Artillery", "1", "1")
    
    
    self.addBordersToSet(USANuclearICBM, self.WorldTerritories&DefendableTerritories, 'One-way', 
                  "Artillery", "2", "1")
    self.addBordersToSet(AfricaNuclearICBM, self.WorldTerritories&DefendableTerritories, 'One-way', 
                  "Artillery", "2", "1")
    self.addBordersToSet(ChinaNuclearICBM, self.WorldTerritories&DefendableTerritories, 'One-way', 
                  "Artillery", "2", "1")
    self.addBordersToSet(UKNuclearICBM, self.WorldTerritories&DefendableTerritories, 'One-way', 
                  "Artillery", "2", "1")
    
    self.addBordersToSet(USAEspionage,Tech, 'One-Way', "Default","-1")
    self.addBordersToSet(USAEspionage,WarTech, 'One-Way')
    
    self.addBordersToSet(ChinaEspionage,Tech, 'One-Way', "Default","-1")
    self.addBordersToSet(ChinaEspionage,WarTech, 'One-Way')
    
    self.addBordersToSet(UKEspionage,Tech, 'One-Way', "Default","-1")
    self.addBordersToSet(UKEspionage,WarTech, 'One-Way')
    
    self.addBordersToSet(AfricaEspionage,Tech, 'One-Way',"Default","-1")
    self.addBordersToSet(AfricaEspionage,WarTech, 'One-Way')
    
    
  
def fixFBorders():
  wgmap = TechWGMap()
  wgmap.load_map_from_file('//DISKSTATION/data/wargear development/Technology/Invention(6).xml')
  for border in wgmap.DOM.getElementsByTagName("border"):
 
    if (border.getAttribute("type") =="Fortify"):
      print("borderbetween",border.getAttribute("fromid"),border.getAttribute("toid"))
      border.setAttribute("type","Fortify Only")
    
  wgmap.save_map_to_file('//DISKSTATION/data/wargear development/Technology/InventionOut.xml', False)
  
  
  

def setupTechMap():
    
  wgmap = TechWGMap()
  wgmap.load_map_from_file('//DISKSTATION/data/wargear development/Invention/Invention - Default(10).xml')
  wgmap.doFullSetup()
  wgmap.save_map_to_file('//DISKSTATION/data/wargear development/Invention/InventionOut.xml', False)

def addTechFlaskFortifies():
  wgmap = TechWGMap()
  wgmap.load_map_from_file('//DISKSTATION/data/wargear development/Invention/Invention - Default(11).xml')
  wgmap.debug = True
  for civ in ["USA","China","UK","Africa"]:
    Granary = wgmap.getTerritoryIDFromName(civ + " Granary")
    Conscription = wgmap.getTerritoryIDFromName(civ + " Conscription")
    Sanitation = wgmap.getTerritoryIDFromName(civ + " Sanitation")
    Nationalism = wgmap.getTerritoryIDFromName(civ + " Nationalism")
    Medicine = wgmap.getTerritoryIDFromName(civ + " Medicine")
    Propaganda = wgmap.getTerritoryIDFromName(civ + " Propaganda")
    
    
    Radar = wgmap.getTerritoryIDFromName(civ + " Radar")
    Flight = wgmap.getTerritoryIDFromName(civ + " Flight")
    Computers = wgmap.getTerritoryIDFromName(civ + " Computers")
    Satellite = wgmap.getTerritoryIDFromName(civ + " Satellite")
    AdvancedFlight = wgmap.getTerritoryIDFromName(civ + " Advanced Flight")
    Internet = wgmap.getTerritoryIDFromName(civ + " Internet")
    
    Artillery = wgmap.getTerritoryIDFromName(civ + " Artillery")
    Missile = wgmap.getTerritoryIDFromName(civ + " Missile")
    ICBM = wgmap.getTerritoryIDFromName(civ + " ICBM")
    NuclearICBM = wgmap.getTerritoryIDFromName(civ + " Nuclear ICBM")
    Espionage = wgmap.getTerritoryIDFromName(civ + " Espionage")
    Assasination = wgmap.getTerritoryIDFromName(civ + " Assasination")
    
    wgmap.addBorder(Granary,Nationalism,borderType="Fortify Only")
    wgmap.addBorder(Granary,Medicine,borderType="Fortify Only")
    wgmap.addBorder(Granary,Propaganda,borderType="Fortify Only")
    wgmap.addBorder(Conscription,Nationalism,borderType="Fortify Only")
    wgmap.addBorder(Conscription,Medicine,borderType="Fortify Only")
    wgmap.addBorder(Conscription,Propaganda,borderType="Fortify Only")
    wgmap.addBorder(Sanitation,Medicine,borderType="Fortify Only")
    wgmap.addBorder(Sanitation,Propaganda,borderType="Fortify Only")
    wgmap.addBorder(Nationalism,Propaganda,borderType="Fortify Only")
             
    wgmap.addBorder(Radar,Satellite,borderType="Fortify Only")
    wgmap.addBorder(Radar,AdvancedFlight,borderType="Fortify Only")
    wgmap.addBorder(Radar,Internet,borderType="Fortify Only")
    wgmap.addBorder(Flight,Satellite,borderType="Fortify Only")
    wgmap.addBorder(Flight,AdvancedFlight,borderType="Fortify Only")
    wgmap.addBorder(Flight,Internet,borderType="Fortify Only")
    wgmap.addBorder(Computers,Internet,borderType="Fortify Only")
    wgmap.addBorder(Computers,AdvancedFlight,borderType="Fortify Only")
    wgmap.addBorder(Satellite,Internet,borderType="Fortify Only")

    wgmap.addBorder(Artillery,NuclearICBM,borderType="Fortify Only")
    wgmap.addBorder(Artillery,Espionage,borderType="Fortify Only")
    wgmap.addBorder(Artillery,Assasination,borderType="Fortify Only")
    wgmap.addBorder(Missile,NuclearICBM,borderType="Fortify Only")
    wgmap.addBorder(Missile,Espionage,borderType="Fortify Only")
    wgmap.addBorder(Missile,Assasination,borderType="Fortify Only")
    wgmap.addBorder(ICBM,Assasination,borderType="Fortify Only")
    wgmap.addBorder(ICBM,Espionage,borderType="Fortify Only")
    wgmap.addBorder(NuclearICBM,Assasination,borderType="Fortify Only")
    
  wgmap.save_map_to_file('//DISKSTATION/data/wargear development/Invention/InventionOut.xml', False)

def addTechFlaskContinents():
  wgmap = TechWGMap()
  wgmap.load_map_from_file('//DISKSTATION/data/wargear development/Technology/Invention(7).xml')
  wgmap.debug = True
  flaskTerritories = set()
  # need to make these ints before adding - getTerritoryNameFromIDs, thinks 65 is 6,5
  flaskTerritories.add(int(wgmap.getTerritoryIDFromName("Southern Alaska")))
  flaskTerritories.add(int(wgmap.getTerritoryIDFromName("Southwest USA")))
  flaskTerritories.add(int(wgmap.getTerritoryIDFromName("North Brazil")))
  flaskTerritories.add(int(wgmap.getTerritoryIDFromName("Kitaa")))
  flaskTerritories.add(int(wgmap.getTerritoryIDFromName("Poland")))
  flaskTerritories.add(int(wgmap.getTerritoryIDFromName("Algeria")))
  flaskTerritories.add(int(wgmap.getTerritoryIDFromName("Congo")))
  flaskTerritories.add(int(wgmap.getTerritoryIDFromName("Saudi Arabia")))
  flaskTerritories.add(int(wgmap.getTerritoryIDFromName("Siberia")))
  flaskTerritories.add(int(wgmap.getTerritoryIDFromName("Western Australia")))
  
  Flasks = []
  Capitals = []
  Flasks.append(int(wgmap.getTerritoryIDFromName("UK Flask")))
  Flasks.append(int(wgmap.getTerritoryIDFromName("USA Flask")))
  Flasks.append(int(wgmap.getTerritoryIDFromName("China Flask")))
  Flasks.append(int(wgmap.getTerritoryIDFromName("Africa Flask")))
  Capitals.append(int(wgmap.getTerritoryIDFromName("London")  ))
  Capitals.append(int(wgmap.getTerritoryIDFromName("South Africa")  ))
  Capitals.append(int(wgmap.getTerritoryIDFromName("Beijing")  ))
  Capitals.append(int(wgmap.getTerritoryIDFromName("DC")  ))

#  import pdb;
#  pdb.set_trace()
     
  individualBonus = str(1)
  pairBonus = str(1)
  
  for flask,capital in zip(Flasks,Capitals):
    IDSet = flaskTerritories
    IDSet2 = set(IDSet)
    for a in IDSet:
      print("adding",a,IDSet2)
      IDSet2.remove(a)
      #import pdb; pdb.set_trace()
      aName = wgmap.get_territory_name_from_ID(a)
      cName = wgmap.get_territory_name_from_ID(capital)
      name = cName + " Tech - " + aName
      #print name
      wgmap.addContinent( name ,set([a]),individualBonus,flask)
      for b in IDSet2:
        bName = wgmap.get_territory_name_from_ID(b)
        abName = cName + " Tech" + " - " + aName + " and " + bName
        #print abName 
        wgmap.addContinent(abName,set([a,b,capital]),pairBonus,flask)
        
        
  wgmap.save_map_to_file('//DISKSTATION/data/wargear development/Technology/InventionOut.xml', False)

    

if __name__ == '__main__':
  pass