import time
import sys


import RPi.GPIO as GPIO
from Motor import *

class GLOBALS:

  SPIN_SECS = 0.57

  DIRECTION = 0 #How many rotations

  STARTING_POINT_X = 0
  STARTING_POINT_Y = 0

  CURRENT_X = 0
  CURRENT_Y = 0

  GOAL_X = 0
  GOAL_Y = 10

  X_OFFSET = 0
  Y_OFFSET = 0

  TRIG = 27
  ECHO = 22

  PWM=Motor() 

  TILES = []

  STARTING_TILE = None
  GOAL_TILE = None

  FOUND_GOAL = False

  STEP_POSITION = 1

  OPEN_LIST = []
  CLOSED_LIST = []


#SENSOR ============================
def setupPins():
  #SETUP GPIO PINS
  GPIO.setmode(GPIO.BCM)

  TRIG = 27
  ECHO = 22

  GPIO.setup(TRIG, GPIO.OUT)
  GPIO.output(TRIG,0)

  GPIO.setup(ECHO, GPIO.IN)

  #Allows time for setup
  time.sleep(0.1)

#Returns Distance in CM
def getDistance():
  #TRIGGER
  GPIO.output(GLOBALS.TRIG, 1)
  time.sleep(0.00001)
  GPIO.output(GLOBALS.TRIG, 0)

  while GPIO.input(GLOBALS.ECHO) == 0:
          pass
  start = time.time()

  while GPIO.input(GLOBALS.ECHO) == 1:
          pass
  stop = time.time()


  return ((stop - start) * 17000) #Centimeters, 170 for "meters"

def scanForWall():
  scanDis = getDistance()

  if(scanDis < 17):
    return 1
  else:
    return 0


#MOTORS ===================================
def forward(secs):
  GLOBALS.PWM.setMotorModel(1500,1500,1500,1500) 
  time.sleep(secs) #HOW LONG TO GO FORWARD
  GLOBALS.PWM.setMotorModel(0,0,0,0)

def rotate(secs):
  GLOBALS.PWM.setMotorModel(1500,1500,-1500,-1500) 
  time.sleep(secs)
  #ALWAYS MAKE SURE TO CLEAR AFTERWARDS
  GLOBALS.PWM.setMotorModel(0,0,0,0)

def rotateTimes(dir): #number of rotations
  rotate(dir * GLOBALS.SPIN_SECS)

def extendField():
  if(len(GLOBALS.TILES) <= GLOBALS.CURRENT_Y + GLOBALS.Y_OFFSET + 1):
    extend_field_y_positive()
  if(GLOBALS.Y_OFFSET * -1 >  GLOBALS.CURRENT_Y - 1):
    extend_field_y_negative()

  print(len(GLOBALS.TILES[0]))
  if(len(GLOBALS.TILES[0]) <= GLOBALS.CURRENT_X + GLOBALS.X_OFFSET + 1): #add 1 for buffer / remove 1 cause buffer
    extend_field_x_positive()
  if(GLOBALS.X_OFFSET * -1 > GLOBALS.CURRENT_X - 1):
    extend_field_x_negative()

def scanSurrondings():

  #information = [0, 0, 0, 0, 0, 0, 0, 0] #1 value for each of the 8 directions

  waitTime = 0.25

  tempTile = None

  extendField()

  rotate(GLOBALS.SPIN_SECS)

  time.sleep(waitTime)

  tempTile = GLOBALS.TILES[GLOBALS.CURRENT_Y + GLOBALS.Y_OFFSET - 1][GLOBALS.CURRENT_X + GLOBALS.X_OFFSET + 1]
  #NORTH EAST
  if (tempTile.tileType != 2 and tempTile.tileType != 3):
    tempTile.tileType = scanForWall()



  rotate(GLOBALS.SPIN_SECS)
  time.sleep(waitTime)
  #EAST
  tempTile = GLOBALS.TILES[GLOBALS.CURRENT_Y + GLOBALS.Y_OFFSET][GLOBALS.CURRENT_X + GLOBALS.X_OFFSET + 1]
  if (tempTile.tileType != 2 and tempTile.tileType != 3):
    tempTile.tileType = scanForWall()

  rotate(GLOBALS.SPIN_SECS)
  time.sleep(waitTime)
  #SOUTH EAST
  tempTile = GLOBALS.TILES[GLOBALS.CURRENT_Y + GLOBALS.Y_OFFSET + 1][GLOBALS.CURRENT_X + GLOBALS.X_OFFSET + 1]

  if (tempTile.tileType != 2 and tempTile.tileType != 3):
    tempTile.tileType = scanForWall()

  rotate(GLOBALS.SPIN_SECS)
  time.sleep(waitTime)
  #SOUTH 
  tempTile = GLOBALS.TILES[GLOBALS.CURRENT_Y + GLOBALS.Y_OFFSET + 1][GLOBALS.CURRENT_X + GLOBALS.X_OFFSET]

  if (tempTile.tileType != 2 and tempTile.tileType != 3):
    tempTile.tileType = scanForWall()

  rotate(GLOBALS.SPIN_SECS)
  time.sleep(waitTime)
  #SOUTH WEST
  tempTile = GLOBALS.TILES[GLOBALS.CURRENT_Y + GLOBALS.Y_OFFSET + 1][GLOBALS.CURRENT_X + GLOBALS.X_OFFSET - 1]

  if (tempTile.tileType != 2 and tempTile.tileType != 3):
    tempTile.tileType = scanForWall()

  rotate(GLOBALS.SPIN_SECS)
  time.sleep(waitTime)
  #WEST 
  tempTile = GLOBALS.TILES[GLOBALS.CURRENT_Y + GLOBALS.Y_OFFSET][GLOBALS.CURRENT_X + GLOBALS.X_OFFSET - 1]

  if (tempTile.tileType != 2 and tempTile.tileType != 3):
    tempTile.tileType = scanForWall()

  rotate(GLOBALS.SPIN_SECS)
  time.sleep(waitTime)
  #NORTH WEST 
  tempTile = GLOBALS.TILES[GLOBALS.CURRENT_Y + GLOBALS.Y_OFFSET - 1][GLOBALS.CURRENT_X + GLOBALS.X_OFFSET - 1]

  if (tempTile.tileType != 2 and tempTile.tileType != 3):
    tempTile.tileType = scanForWall()

  rotate(GLOBALS.SPIN_SECS)
  time.sleep(waitTime)
  #NORTH 
  tempTile = GLOBALS.TILES[GLOBALS.CURRENT_Y + GLOBALS.Y_OFFSET - 1][GLOBALS.CURRENT_X + GLOBALS.X_OFFSET]

  if (tempTile.tileType != 2 and tempTile.tileType != 3):
    tempTile.tileType = scanForWall()

  
#ALGORITHM =====================================
def distanceFormula(tileOne, tileTwo):  
  return abs(tileTwo.positionY - tileOne.positionY) + abs(tileTwo.positionX - tileOne.positionX)
  #return math.sqrt((tileTwo.positionY - tileOne.positionY)**2 + (tileTwo.positionX - tileOne.positionX)**2)

def setAValues(tileT):
  tileT.astar_G_value = (tileT.prevTile.astar_G_value + 1) 
  tileT.astar_H_value = (distanceFormula(tileT, GLOBALS.GOAL_TILE)) * 10

def setCornerAValues(tileK):
  tileK.astar_G_value = (tileK.prevTile.astar_G_value + 1.4) 
  tileK.astar_H_value = (distanceFormula(tileK, GLOBALS.GOAL_TILE)) * 10

def legalTile(someTile):
  # if exists
      
  if (someTile != None):

    # if not wall
    if(someTile.tileType != 1):

      # check if in closed list or open list
      if not (someTile in GLOBALS.CLOSED_LIST):
        return True

  return False

def adjacentTasks(tileCenter):
  tileCenter.step = GLOBALS.STEP_POSITION
  GLOBALS.STEP_POSITION += 1
  tileCenter.selected = True

  # if exists

  tileBelow = GLOBALS.TILES[tileCenter.positionY + GLOBALS.Y_OFFSET + 1][tileCenter.positionX + GLOBALS.X_OFFSET]
  if (legalTile(tileBelow)):
    #if in open list then update
    if (tileBelow in GLOBALS.OPEN_LIST):
      if(tileBelow.F_Value() > ((tileCenter.astar_G_value + 1) + distanceFormula(tileBelow, GLOBALS.GOAL_TILE))):
        setAValues(tileBelow)
    else:
      tileBelow.inspected = True
      tileBelow.prevTile = tileCenter
      setAValues(tileBelow)
      GLOBALS.OPEN_LIST.append(tileBelow)



  # if exists
  tileAbove = GLOBALS.TILES[tileCenter.positionY + GLOBALS.Y_OFFSET - 1][tileCenter.positionX + GLOBALS.X_OFFSET]
  if (legalTile(tileAbove)):
    if (tileAbove in GLOBALS.OPEN_LIST):
      if(tileAbove.F_Value() > ((tileCenter.astar_G_value + 1) + distanceFormula(tileAbove, GLOBALS.GOAL_TILE))):
        setAValues(tileAbove)
    else:
      tileAbove.inspected = True
      tileAbove.prevTile = tileCenter
      setAValues(tileAbove)
      GLOBALS.OPEN_LIST.append(tileAbove)
  
  tileRight = GLOBALS.TILES[tileCenter.positionY + GLOBALS.Y_OFFSET][tileCenter.positionX + GLOBALS.X_OFFSET + 1]  
  if (legalTile(tileRight)):
    #if in open list then update
    if (tileRight in GLOBALS.OPEN_LIST):

      if(tileRight.F_Value() > ((tileCenter.astar_G_value + 1) + distanceFormula(tileRight, GLOBALS.GOAL_TILE))):
        setAValues(tileRight)

    else:
      tileRight.inspected = True
      tileRight.prevTile = tileCenter
      setAValues(tileRight)
      GLOBALS.OPEN_LIST.append(tileRight)
  
  tileLeft = GLOBALS.TILES[tileCenter.positionY + GLOBALS.Y_OFFSET][tileCenter.positionX + GLOBALS.X_OFFSET - 1]
  if (legalTile(tileLeft)):
    #if in open list then update
    if (tileLeft in GLOBALS.OPEN_LIST):
      if(tileLeft.F_Value() > ((tileCenter.astar_G_value + 1) + distanceFormula(tileLeft, GLOBALS.GOAL_TILE))):
        setAValues(tileLeft)
    else:
      tileLeft.inspected = True
      tileLeft.prevTile = tileCenter
      setAValues(tileLeft)
      GLOBALS.OPEN_LIST.append(tileLeft)
  
  tileUpLeft = GLOBALS.TILES[tileCenter.positionY + GLOBALS.Y_OFFSET - 1][tileCenter.positionX + GLOBALS.X_OFFSET - 1]
  if (legalTile(tileUpLeft)):
    #if in open list then update
    if (tileUpLeft in GLOBALS.OPEN_LIST):
      if(tileUpLeft.F_Value() > ((tileCenter.astar_G_value + 1.4) + distanceFormula(tileUpLeft, GLOBALS.GOAL_TILE))):
        setCornerAValues(tileUpLeft)
    else:
      tileUpLeft.inspected = True
      tileUpLeft.prevTile = tileCenter
      setCornerAValues(tileUpLeft)
      GLOBALS.OPEN_LIST.append(tileUpLeft)

  tileUpRight = GLOBALS.TILES[tileCenter.positionY + GLOBALS.Y_OFFSET - 1][tileCenter.positionX + GLOBALS.X_OFFSET + 1]
  if (legalTile(tileUpRight)):
    #if in open list then update
    if (tileUpRight in GLOBALS.OPEN_LIST):
      if(tileUpRight.F_Value() > ((tileCenter.astar_G_value + 1.4) + distanceFormula(tileUpRight, GLOBALS.GOAL_TILE))):
        setCornerAValues(tileUpLeft)
    else:
      tileUpRight.inspected = True
      tileUpRight.prevTile = tileCenter
      setCornerAValues(tileUpRight)
      GLOBALS.OPEN_LIST.append(tileUpRight)

  tileDownLeft = GLOBALS.TILES[tileCenter.positionY + GLOBALS.Y_OFFSET + 1][tileCenter.positionX + GLOBALS.X_OFFSET - 1]
  if (legalTile(tileDownLeft)):
    #if in open list then update
    if (tileDownLeft in GLOBALS.OPEN_LIST):
      if(tileDownLeft.F_Value() > ((tileCenter.astar_G_value + 1.4) + distanceFormula(tileDownLeft, GLOBALS.GOAL_TILE))):
        setCornerAValues(tileDownLeft)
    else:
      tileDownLeft.inspected = True
      tileDownLeft.prevTile = tileCenter
      setCornerAValues(tileDownLeft)
      GLOBALS.OPEN_LIST.append(tileDownLeft)

  tileDownRight = GLOBALS.TILES[tileCenter.positionY + GLOBALS.Y_OFFSET + 1][tileCenter.positionX + GLOBALS.X_OFFSET + 1]
  if (legalTile(tileDownRight)):
    #if in open list then update
    if (tileDownRight in GLOBALS.OPEN_LIST):
      if(tileDownRight.F_Value() > ((tileCenter.astar_G_value + 1.4) + distanceFormula(tileDownRight, GLOBALS.GOAL_TILE))):
        setCornerAValues(tileDownRight)
    else:
      tileDownRight.inspected = True
      tileDownRight.prevTile = tileCenter
      setCornerAValues(tileDownRight)
      GLOBALS.OPEN_LIST.append(tileDownRight)

def getLowest(tileList):
  lowestTile = tileList[0]
  for tileX in tileList:
    if (tileX.F_Value() < lowestTile.F_Value()):
      lowestTile = tileX
  return lowestTile


# ETC ALO ============

class Tile:

  positionX = 0
  positionY = 0
  tileType = 0

  #selected = False
  #inspected = False

  astar_G_value = 0#99999
  astar_H_value = 0#99999

  prevTile = None

  step = 0

  #Step for local A*
  #step = 0

            

  def set_type(self, t=0):
    self.tileType = t

  # def get_pos(self):
  #   return self.positionX, self.positionY


  def __str__(self):
    return str(self.tileType)

  def __init__(self, posX=0, posY=0, type=0):
    self.positionX = posX
    self.positionY = posY
    self.tileType = type

  def F_Value(self):
    return self.astar_G_value + self.astar_H_value


def create_field():

  yList = []
  xList = []
  startingTile = Tile(0,0,3)
  xList.append(startingTile)
  yList.append(xList)
  GLOBALS.TILES = yList

  GLOBALS.STARTING_TILE = startingTile
  GLOBALS.CLOSED_LIST.append(startingTile)

  xNeg = False
  yNeg = False

  #SET OFFSET BASED ON GOAL:
  if GLOBALS.GOAL_X < 0:
    #GLOBALS.X_OFFSET = 0#GLOBALS.GOAL_X
    xNeg = True

  if GLOBALS.GOAL_Y < 0:
    #GLOBALS.Y_OFFSET = 0#GLOBALS.GOAL_Y
    yNeg = True

  #if negative, extend reverse

  for x in range(abs(GLOBALS.GOAL_X)):
    
    if (xNeg):
      extend_field_x_negative()
    else:
      extend_field_x_positive()

  for y in range(abs(GLOBALS.GOAL_Y)):
    
    if (yNeg):
      extend_field_y_negative()
    else:
      extend_field_y_positive()
    

  goalTile = GLOBALS.TILES[GLOBALS.GOAL_Y + GLOBALS.Y_OFFSET][GLOBALS.GOAL_X + GLOBALS.X_OFFSET]
  goalTile.tileType = 2
  GLOBALS.GOAL_TILE = goalTile



def extend_field_x_positive():

  print("Extending X Pos")


  for tileList in GLOBALS.TILES:
    newTile = Tile(len(tileList) + GLOBALS.X_OFFSET, tileList[0].positionY,5)
    tileList.append(newTile)

  # for y in range(0, len(GLOBALS.TILES)):
  #   newTile = Tile(GLOBALS.TILES[y][len(GLOBALS.TILES[y])-1].positionX + 1, GLOBALS.TILES[y][len(GLOBALS.TILES[y])-1].positionY, 5)
  #   GLOBALS.TILES[y].append(newTile)

def extend_field_x_negative():

  print("Extending X Neg")

  #count = 0

  for tileList in GLOBALS.TILES:
    newTile = Tile(GLOBALS.X_OFFSET - 1, tileList[0].positionY,5)
    tileList.insert(0, newTile)
    

  # for y in range(0, len(GLOBALS.TILES)):
  #   newTile = Tile(y[len(y)-1].positionX - 1, y[len(y)-1].positionY, 5)
  #   GLOBALS.TILES[y].insert(0, newTile)
  GLOBALS.X_OFFSET += 1

def extend_field_y_negative():

  print("Extending Y Neg")

  newList = []
  for x in range(len(GLOBALS.TILES[0])):
    newTile = Tile(GLOBALS.TILES[0][x].positionX, GLOBALS.TILES[0][x].positionY - 1, 5) 
    newList.append(newTile)
  GLOBALS.TILES.insert(0, newList)

  GLOBALS.Y_OFFSET += 1

def extend_field_y_positive():

  print("Extending Y Pos")

  newList = []
  for x in range(len(GLOBALS.TILES[0])):
    newTile = Tile(GLOBALS.TILES[len(GLOBALS.TILES)-1][x].positionX , GLOBALS.TILES[len(GLOBALS.TILES)-1][x].positionY + 1, 5) 
    newList.append(newTile)
  GLOBALS.TILES.append(newList)
   


# Movement part of Alg ==============================================
def getDirection(tileQ):
  diff_X = GLOBALS.CURRENT_X - tileQ.positionX
  diff_Y = GLOBALS.CURRENT_Y - tileQ.positionY

  print(diff_X, " , ", diff_Y)

  if diff_X == 1:
    if diff_Y == 1:
      return 7
    elif diff_Y == -1:
      return 5
    else: #0
      return 6
  elif diff_X == -1:
    if diff_Y == 1:
      return 1
    elif diff_Y == -1:
      return 3
    else: #0
      return 2
  else: #0 
    if diff_Y == 1:
      return 0
    elif diff_Y == -1:
      return 4
    else: #0
      return None


# OTHER ==============================================

def print_field():
  for tileList in GLOBALS.TILES:
    for tile in tileList:
      print(str(tile.tileType), end=" ")
    print()

def print_field_values():
  for tileList in GLOBALS.TILES:
    for tile in tileList:
      print(str(tile.F_Value()), end=" ")
    print()

def print_field_Y_values():
  for tileList in GLOBALS.TILES:
    for tile in tileList:
      print(str(tile.positionY), end=" ")
    print()    

def print_globals():
  print("CURRENT X: ", GLOBALS.CURRENT_X)
  print("CURRENT Y: ", GLOBALS.CURRENT_Y)
  print()
  print("OFFSET X: ", GLOBALS.X_OFFSET)
  print("OFFSET Y: ", GLOBALS.Y_OFFSET)
  print()
  print("GOAL X: ", GLOBALS.GOAL_X)
  print("GOAL Y: ", GLOBALS.GOAL_Y)
  print()
  print("GOAL TILE X: ", GLOBALS.GOAL_TILE.positionX)
  print("GOAL TILE Y: ", GLOBALS.GOAL_TILE.positionY)

def main():

  print("RUNNING AUTONOMOUS")

  GLOBALS.GOAL_X = int(sys.argv[1])
  GLOBALS.GOAL_Y = int(sys.argv[2])

  #Wait for 5 seconds to disconnect
  #time.sleep(3)
  setupPins()

  
  create_field()

  print("Testing print:")
  print_field()
  print("Finished Test Print")


  scanSurrondings()

  print()
  print("After Updating:")
  print_field()

  adjacentTasks(GLOBALS.STARTING_TILE)

  #print_globals()

  print()
  print("After Calcalutions:")
  print_field_values()

  #THIS WILL END UP BEING MAIN LOOP
  lowestTile = getLowest(GLOBALS.OPEN_LIST)
  directionNeeded = getDirection(lowestTile)
  print("DIRE: ", directionNeeded)
  rotateTimes(directionNeeded)
  if (directionNeeded%2 == 0):
    forward(0.5)
  else:
    forward(0.85)

  GLOBALS.CURRENT_X = lowestTile.positionX
  GLOBALS.CURRENT_Y = lowestTile.positionY

  scanSurrondings()

  print()
  print("After Second Scan:")
  print_field()

  directionNeeded = getDirection(lowestTile)
  print("DIRE: ", directionNeeded)
  rotateTimes(directionNeeded)
  if (directionNeeded%2 == 0):
    forward(0.5)
  else:
    forward(0.85)


def destory():
  GPIO.cleanup()



if __name__ == "__main__":
  try:
    main()
  except KeyboardInterrupt:  # When 'Ctrl+C' is pressed, the child program destroy() will be  executed.
    destroy()

