import pygame
from pygame.locals import *
import blocks

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
    def __init__(self, gameGrid, actor) :
        self.gameGrid = gameGrid
        self.actor = actor

        x,y,z = actor.gridLocation
        global currentUIHandler
        currentUIHandler = refrence(tileSelectionHandler(x, y, z, self.startWalk))

    def startWalk(self) :
        print 'Haha, I am using the INTERNET!'

def walkToPoint(gameGrid, actor) :
    x, y, z = actor.gridLocation
    global currentUIHandler

class tileSelectionHandler(uiHandler) :
    def __init__(self, sx, sy, sz, callback=None) :
        self.x = sx
        self.y = sy
        self.z = sz
        self.callback=callback

        myDict = {K_DOWN : self.DOWN,
                  K_UP : self.UP,
                  K_LEFT : self.LEFT,
                  K_RIGHT : self.RIGHT,
                  K_RETURN : self.RETURN}

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

    def RETURN(self) :
        if self.callback :
            self.callback((self.x, self.y, self.z))
            return

        else :
            return

def initialize() :
    global currentUIHandler
    currentUIHandler = refrence(None)
    walkToPointHandler(coreVars['gameGrid'], coreVars['actorList'][-1]))

    return currentUIHandler
