import pygame
from pygame.locals import *
import blocks

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

class testControlHandler(uiHandler) :
    def __init__(self, screen, gameGrid, actor) :
        self._actor = actor

        myDict = {K_DOWN : self.DOWN,
                  K_UP : self.UP,
                  K_LEFT : self.LEFT,
                  K_RIGHT : self.RIGHT,
                  K_h : self.K_H,
                  K_g : self.K_G}

        uiHandler.__init__(self, screen, gameGrid, myDict)

    def DOWN(self) :
        if self._actor.isActing() :
            return

        self._actor.setGraphicState('walking-SE')
        self._actor.walk('SE', self.gameGrid)

    def UP(self) :
        if self._actor.isActing() :
            return

        self._actor.setGraphicState('walking-NW')
        self._actor.walk('NW', self.gameGrid)

    def LEFT(self) :
        if self._actor.isActing() :
            return

        self._actor.setGraphicState('walking-SW')
        self._actor.walk('SW', self.gameGrid)

    def RIGHT(self) :
        if self._actor.isActing() :
            return

        self._actor.setGraphicState('walking-NE')
        self._actor.walk('NE', self.gameGrid)

    def K_H(self) :
        if self._actor.isActing() :
            return

        self._actor.setGraphicState('walking-NE')
        self._actor.walk('NEU', self.gameGrid)

    def K_G(self) :
        if self._actor.isActing() :
            return

        self._actor.setGraphicState('walking-SW')
        self._actor.walk('SWD', self.gameGrid)

class walkToPointHandler(uiHandler) :
    pass

class tileSelectionHandler(uiHandler) :
    def __init__(self, sx, sy, sz) :
        self.x = sx
        self.y = sy
        self.z = sz

        myDict = {K_DOWN : self.DOWN,
                  K_UP : self.UP,
                  K_LEFT : self.LEFT,
                  K_RIGHT : self.RIGHT}

        uiHandler.__init__(self, coreVars['screen'], coreVars['gameGrid'], myDict)

        self._arrow = blocks.selectArrow()
        self.gameGrid.setBlock(sx, sy, sz, self._arrow, ow=False)
        self._arrow.setUpdateFlag()
        coreVars['spriteList'].append(self._arrow)

    def DOWN(self) :
        # Remove the old arrow
        self.gameGrid.removeBlock(self.x, self.y, self.z, self._arrow)

        # Incriment location
        if ORIENTATION == 'NW' :
            self.y += 1

        else :
            self.x -= 1

        self.gameGrid.setBlock(self.x, self.y, self.z, self._arrow, ow=False)
        self._arrow.setUpdateFlag()

    def UP(self) :
        self.gameGrid.removeBlock(self.x, self.y, self.z, self._arrow)

        if ORIENTATION == 'NW' :
            self.y -= 1

        else :
            self.x += 1

        self.gameGrid.setBlock(self.x, self.y, self.z, self._arrow, ow=False)
        self._arrow.setUpdateFlag()
       
    def LEFT(self) :
        self.gameGrid.removeBlock(self.x, self.y, self.z, self._arrow)

        if ORIENTATION == 'NW' :
            self.x += 1

        else :
            self.y -= 1

        self.gameGrid.setBlock(self.x, self.y, self.z, self._arrow, ow=False)
        self._arrow.setUpdateFlag()

    def RIGHT(self) :
        self.gameGrid.removeBlock(self.x, self.y, self.z, self._arrow)

        if ORIENTATION == 'NW' :
            self.x -= 1

        else :
            self.y += 1

        self.gameGrid.setBlock(self.x, self.y, self.z, self._arrow, ow=False)
        self._arrow.setUpdateFlag()

###

def Manhattan(startCoOrds, endCoOrds) :
    hVal = 0

    hVal += abs(startCoOrds[0] - endCoOrds[0])
    hVal += abs(startCoOrds[1] - endCoOrds[1])
    hVal += abs(startCoOrds[2] - endCoOrds[2])

    return hVal

def findPath(startCoOrds, endCoOrds, gameGrid, heuristic=Manhattan) :
    '''A* pathfinding algorithm. Defaults to using Manhattan heuristic'''
    pass

###

def initialize() :
    global currentUIHandler
    currentUIHandler = refrence(testControlHandler(coreVars['screen'], coreVars['gameGrid'], coreVars['actorList'][-1]))

    return currentUIHandler
