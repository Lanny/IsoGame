import pygame
from pygame.locals import *
import blocks
import actors
import pathfinder

# Change this to alter the control scheme
ORIENTATION = 'NW'

class refrence(object) :
    def __init__(self, obj) :
        self._obj = obj

    def set(self, obj) :
        self._obj = obj

    def get(self) :
        return self._obj

class uiHandler() :
    def __init__(self, screen, gameGrid, handlerDict) :
        self.gameGrid = gameGrid
        self.screen = screen
        self.handlerDict = handlerDict

    def handleInput(self, playerInput) :
        try :
            return self.handlerDict[playerInput.key]()

        except KeyError :
            pass

    def get_loc(self) :
        return 'N\\A'

    def getUI(self) :
        return None

class tileSelectionHandler(uiHandler) :
    def __init__(self, sx, sy, sz, callback=None) :
        self.x = sx
        self.y = sy
        self.z = sz
        self.callback=callback
        self.gameGrid = coreVars['gameGrid']

        myDict = {K_DOWN : self.DOWN,
                  K_UP : self.UP,
                  K_LEFT : self.LEFT,
                  K_RIGHT : self.RIGHT,
                  K_RETURN : self.RETURN,
                  K_SPACE : self.space}

        uiHandler.__init__(self, coreVars['screen'], coreVars['gameGrid'], myDict)

        self._arrow = blocks.selectArrow()
        self.gameGrid.setBlock(sx, sy, sz, self._arrow, ow=False)
        self._arrow.setUpdateFlag()
        coreVars['spriteList'].append(self._arrow)

    def space(self) :
        self._actor.meleeAttack(self._actor._facing, self.gameGrid)

    def DOWN(self) :
        # Incriment location
        if ORIENTATION == 'NW' :
            newLoc = (self.x, self.y+1, self.z)

        else :
            newLoc = (self.x-1, self.y, self.z)

        # Opps, can't go there! Abort! Abort!
        if newLoc not in pathfinder.getValidMovement(self.gameGrid, self, True) : return

        # Remove the old arrow
        self.gameGrid.removeBlock(self._arrow, self.x, self.y, self.z)

        self.x, self.y, self.z = newLoc

        self.gameGrid.setBlock(self.x, self.y, self.z, self._arrow, ow=False, insPos=-1)
        self._arrow.setUpdateFlag()

    def UP(self) :
        if ORIENTATION == 'NW' :
            newLoc = (self.x, self.y-1, self.z)

        else :
            newLoc = (self.x+1, self.y, self.z)

        if newLoc not in pathfinder.getValidMovement(self.gameGrid, self, True) : return

        self.gameGrid.removeBlock(self._arrow, self.x, self.y, self.z)

        self.x, self.y, self.z = newLoc

        self.gameGrid.setBlock(self.x, self.y, self.z, self._arrow, ow=False, insPos=-1)
        self._arrow.setUpdateFlag()
       
    def LEFT(self) :
        if ORIENTATION == 'NW' :
            newLoc = (self.x+1, self.y, self.z)

        else :
            newLoc = (self.x, self.y-1, self.z)

        if newLoc not in pathfinder.getValidMovement(self.gameGrid, self, True) : return

        self.gameGrid.removeBlock(self._arrow, self.x, self.y, self.z)

        self.x, self.y, self.z = newLoc

        self.gameGrid.setBlock(self.x, self.y, self.z, self._arrow, ow=False, insPos=-1)
        self._arrow.setUpdateFlag()

    def RIGHT(self) :
        # Incriment location
        if ORIENTATION == 'NW' :
            newLoc = (self.x-1, self.y, self.z)

        else :
            newLoc = (self.x, self.y+1, self.z)

        if newLoc not in pathfinder.getValidMovement(self.gameGrid, self, True) : return

        self.gameGrid.removeBlock(self._arrow, self.x, self.y, self.z)

        self.x, self.y, self.z = newLoc

        self.gameGrid.setBlock(self.x, self.y, self.z, self._arrow, ow=False, insPos=-1)
        self._arrow.setUpdateFlag()

    def RETURN(self) :
        if self.callback :
            self.callback((self.x, self.y, self.z))
            return

        else :
            return

    def get_loc(self) :
        # Just some testing code called form the main loop
        return '(%d,%d,%d)' % (self.x, self.y, self.z)

    def getUI(self) :
      candidateList = self.gameGrid.getBlock((self.x, self.y, self.z))
      actor = None
      for candidate in candidateList :
          if isinstance(candidate, actors.Actor) :
              actor = candidate

      if not actor :
        return None

      return [actorStatsBar(actor)]

class orthagonalSelectionHandler(tileSelectionHandler) :
    def __init__(self, actor) :
        self._actor = actor
        x,y,z = actor.gridLocation

        tileSelectionHandler.__init__(self, x, y, z)

    def DOWN(self) :
        # Incriment location
        x,y,z = self._actor.gridLocation
        if ORIENTATION == 'NW' :
            newLoc = (x, y+1, z)

        else :
            newLoc = (x-1, y, z)

        # Remove the old arrow
        self.gameGrid.removeBlock(self._arrow, self.x, self.y, self.z)

        self.x, self.y, self.z = newLoc

        self.gameGrid.setBlock(self.x, self.y, self.z, self._arrow, ow=False, insPos=-1)
        self._arrow.setUpdateFlag()

    def UP(self) :
        x,y,z = self._actor.gridLocation
        if ORIENTATION == 'NW' :
            newLoc = (x, y-1, z)

        else :
            newLoc = (x+1, y, self.z)

        self.gameGrid.removeBlock(self._arrow, self.x, self.y, self.z)

        self.x, self.y, self.z = newLoc

        self.gameGrid.setBlock(self.x, self.y, self.z, self._arrow, ow=False, insPos=-1)
        self._arrow.setUpdateFlag()
       
    def LEFT(self) :
        x,y,z = self._actor.gridLocation
        if ORIENTATION == 'NW' :
            newLoc = (x+1, y, z)

        else :
            newLoc = (x, y-1, z)

        self.gameGrid.removeBlock(self._arrow, self.x, self.y, self.z)

        self.x, self.y, self.z = newLoc

        self.gameGrid.setBlock(self.x, self.y, self.z, self._arrow, ow=False, insPos=-1)
        self._arrow.setUpdateFlag()

    def RIGHT(self) :
        x,y,z = self._actor.gridLocation
        # Incriment location
        if ORIENTATION == 'NW' :
            newLoc = (x-1, y, z)

        else :
            newLoc = (x, y+1, z)

        self.gameGrid.removeBlock(self._arrow, self.x, self.y, self.z)

        self.x, self.y, self.z = newLoc

        self.gameGrid.setBlock(self.x, self.y, self.z, self._arrow, ow=False, insPos=-1)
        self._arrow.setUpdateFlag()

class meleeAttackHandler(orthagonalSelectionHandler) :
    def __init__(self, actor) :
        orthagonalSelectionHandler.__init__(self, actor)

        self.callback = self.ATTACK

    def ATTACK(self, endLoc) :
        candidateList = self.gameGrid.getBlock(endLoc)
        actor = None
        for candidate in candidateList :
            if isinstance(candidate, actors.Actor) :
                actor = candidate

        if not actor :
            return

        direction = actors.coordToDirection(self._actor.gridLocation, endLoc)
        self._actor.standardActionRemaining = False
        self._actor.meleeAttack(direction, self.gameGrid)

        self.gameGrid.removeBlock(self._arrow, self.x, self.y, self.z)

        currentUIHandler.set(turnMenuHandler(self._actor))

class turnMenuHandler(uiHandler) :
    def __init__(self, actor) :
        self._actor = actor
        self._options = ['Move', 'Attack', 'End Turn']
        self._selectedOption = 0

        myDict = {K_DOWN : self.DOWN,
                  K_UP : self.UP,
                  K_RETURN : self.RETURN
                 }

        uiHandler.__init__(self, coreVars['screen'], coreVars['gameGrid'], myDict)

    def DOWN(self) :
      if self._selectedOption + 1 < len(self._options) :
        self._selectedOption += 1
    def UP(self) :
      if self._selectedOption - 1 >= 0 :
        self._selectedOption -= 1
    def RETURN(self) :
      action = self._options[self._selectedOption]

      if action == 'Move' :
        if not self._actor.moveActionRemaining : return
        currentUIHandler.set(walkToPointHandler(self._actor))

      elif action == 'Attack' :
          if not self._actor.standardActionRemaining : return
          currentUIHandler.set(meleeAttackHandler(self._actor))

      elif action == 'End Turn' :
        combatController()

    def handleInput(self, playerInput) :
        if self._actor.isActing() : return
        try :
            return self.handlerDict[playerInput.key]()

        except KeyError :
            pass

    def getUI(self) :
      surface = uiResources['command_bar'].convert()

      curY = 10
      for option in self._options :
          textColor = (0,0,0)
          if option == self._options[self._selectedOption] :
            surface.blit(uiResources['menu_dot'], (5, curY))
          if option == 'Move' and not self._actor.moveActionRemaining : textColor = (100,100,100)
          elif option == 'Attack' and not self._actor.standardActionRemaining : textColor = (100,100,100)

          surface.blit(uiResources['commands_font'].render(option, True, textColor), (20, curY))
          curY += 15

      loc = coreVars['screen'].get_size()
      loc = (loc[0] - surface.get_size()[0], loc[1] - 150)

      return [(surface, loc), actorStatsBar(self._actor)]

class walkToPointHandler(tileSelectionHandler) :
    def __init__(self, actor) :
        self.gameGrid = coreVars['gameGrid']
        self._actor = actor

        x,y,z = actor.gridLocation

        tileSelectionHandler.__init__(self, x, y, z)

        self.callback = self.startWalk

    def startWalk(self, endLoc) :
        # Last minuite check that there isn't an actor sitting at the destination
        if True in [i.isSolid() for i in self.gameGrid.getBlock(endLoc)] : return

        walkingPath = pathfinder.aStar(self.gameGrid, self._actor.gridLocation, endLoc).getDirections()
        self._actor.walkChain(walkingPath, self.gameGrid)

        # We're done with this arrow, take it out
        self.gameGrid.removeBlock(self._arrow, self.x, self.y, self.z)

        # And this actor's move action is spent
        self._actor.moveActionRemaining = False

        # Hand control back to the administrator function
        currentUIHandler.set(turnMenuHandler(self._actor))

def combatController() :
    coreVars['initList'].append(coreVars['initList'].pop(0))
    currentActor = coreVars['initList'][-1]

    # Give the actor their three action types at the start of the turn
    currentActor.moveActionRemaining = True
    currentActor.standardActionRemaining = True
    currentActor.minorActionRemaining = True

    currentUIHandler.set(turnMenuHandler(currentActor))

def actorStatsBar(actor) :
    surface = uiResources['speech_bar-left']
    surface = surface.convert()

    surface.blit(actor.getPortrait(), (0,0))
    surface.blit(uiResources['stats_font'].render(actor.name, True, (0,0,0)), (120, 10))
    surface.blit(uiResources['stats_font'].render('HP: %d/%d' % (actor.HP, actor.maxHP), True, (0,0,0)), (120, 25))

    loc = coreVars['screen'].get_size()
    loc = (0, loc[1] - 150)

    return (surface, loc)

def initialize() :
    global currentUIHandler
    currentUIHandler = refrence('foo')
    combatController()

    # Load up all our UI resources
    global uiResources
    uiResources = {
        'speech_bar-left' : pygame.image.load('assets/UI/speech_bar.png').convert(),
        'command_bar' : pygame.image.load('assets/UI/command_bar.png').convert(),
        'menu_dot' : pygame.image.load('assets/UI/menu_dot.png').convert_alpha(),
        'stats_font' : pygame.font.Font(None, 18),
        'commands_font' : pygame.font.Font(None, 18)
        }

    return currentUIHandler
