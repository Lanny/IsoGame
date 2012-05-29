#! /usr/bin/env python

# Untitled isometric game core module
# Copyright(c) 2012 Lan "Lanny" Rogers

import pygame, re, pdb
import blocks, actors, UIhandlers
from pygame.locals import *

DEV_MODE = True

class gameGridException(Exception) :
    pass

class gameGrid(object) :
    def __init__(self, x, y, z) :
        '''Create a game grid of x by y by z dimentions'''
        self.block_map = []

        for x_row in range(x) :
            self.block_map.append([])
            for y_row in range(y) :
                self.block_map[-1].append([])
                for z_row in range(z) :
                    self.block_map[-1][-1].append([blocks.Air()])

        return

    def setBlock(self, x, y, z, block, ow=True, insPos=-1) :
        '''Set a particular location to a particular block or sprite'''
        if ow :
            self.block_map[x][y][z] = [block]

        else :
            self.block_map[x][y][z].insert(insPos, block)

    def removeBlock(self, x, y, z, block) :
        '''Remove a block from a cell-contents list'''
        self.block_map[x][y][z].remove(block) 

        # If cell is left empty, throw an air block in there
        if len(self.block_map[x][y][z]) < 1 :
            self.block_map[x][y][z].append(blocks.Air())

    def getBlock(self, x, y=None, z=None) :
        '''Returns a list of objects present in a given cell. May be more than one'''
        # We can also take a tuple
        if not y and not z and type(x) == tuple :
            x, y, z = x

        return self.block_map[x][y][z]

    def getDims(self) :
        return (len(self.block_map), len(self.block_map[-1]), len(self.block_map[-1][-1]))

    '''def getValidMovement(self, x, y, z) :
        # All possible orthagonal moves
        validMoves = [(x, y+1, z-1),
                      (x, y-1, z-1),
                      (x+1, y, z-1),
                      (x-1, y, z-1),
                      (x, y+1, z),
                      (x, y-1, z),
                      (x+1, y, z),
                      (x-1, y, z),
                      (x, y+1, z+1),
                      (x, y-1, z+1),
                      (x+1, y, z+1),
                      (x-1, y, z+1)]

        for move in validMoves :
            # Get rid of the ones that aren't valid. We use the try/except clause
            # in case we overrun a list.
            try :
                # Test if there is a solid entity in the way of possible move
                if True in [i.isSolid() for i in self.getBlock(move[0], move[1], move[2])] :
                    validMoves.remove(move)

                # Is there a solid block under the proposed move?
                elif True not in [i.isSolid() for i in self.getBlock(move[0], move[1], move[2]-1)] :
                    validMoves.remove(move)

            except IndexError :
                validMoves.remove(move)

        # And hand us back the result
        return validMoves
        '''

def drawMap(grid, surface, flip=True) :
    '''Redraw every item in the a gamegrid to the surface provided. If flip is
    false, won't refresh when done'''
    dims = grid.getDims()

    # Write coords for the blocks.
    x_coord = dims[0] * 23
    y_coord = dims[2] * 29

    # The order we do things in here is a little wonky, z->x->y, but it should work
    for vert_slice in range(dims[2]) :
        for y_row in range(dims[1]) :
            for x_row in range(dims[0]) :
                for block in grid.getBlock(x_row, y_row, vert_slice) :
                    block_img = block.get_img()
                    if block_img :
                        image = block_img.convert()
                        image.set_colorkey((255,255,255))

                        x_coord += block.x_offset
                        y_coord += block.y_offset

                        if isinstance(block, pygame.sprite.Sprite) :
                            block.setLoc(x_coord, y_coord)

                        surface.blit(image, (x_coord,y_coord))

                        x_coord -= block.x_offset
                        y_coord -= block.y_offset

                x_coord -= 23
                y_coord += 9

            x_coord += 23 * dims[0] + 23
            y_coord -= 9 * dims[0] - 9

        # Shift our block up (coords is taken _from_ the top)
        x_coord = dims[0] * 23
        y_coord = dims[2] * 29
        y_coord -= 28 * (vert_slice + 1)

    if flip :
        pygame.display.update()

    return

def loadMap(map_to_load) :
    '''Load a map from somewhere in the project and return a gameGrid object'''
    mapFile = open(map_to_load)

    reObj = re.match(r'(\d+), *(\d+), *(\d+)', mapFile.readline())
    returnGrid = gameGrid(int(reObj.group(1)), int(reObj.group(2)), int(reObj.group(3)))

    for line in mapFile.readlines() :
        if line[0] == '#' :
            pass

        else :
            reObj = re.match(r'(\d+), *(\d+), *(\d+) *: *(.+)', line)

            # Try to set a block. If fails assume an actor
            try :
                returnGrid.setBlock(int(reObj.group(1)), int(reObj.group(2)), int(reObj.group(3)), eval('blocks.' + reObj.group(4) + '()'), ow=False)
                x = returnGrid.getBlock(int(reObj.group(1)), int(reObj.group(2)), int(reObj.group(3)))

                for block in x :
                    if isinstance(block, pygame.sprite.Sprite) :
                        global spriteList
                        spriteList.append(block)

            # If neither raise AttributeError as usual
            except AttributeError :
                returnGrid.setBlock(int(reObj.group(1)), int(reObj.group(2)), int(reObj.group(3)), eval('actors.' + reObj.group(4) + '()'), ow=False)

            # Redundancy here?
            if isinstance(returnGrid.getBlock(int(reObj.group(1)), int(reObj.group(2)), int(reObj.group(3)))[-1], pygame.sprite.Sprite) :
                returnGrid.getBlock(int(reObj.group(1)), int(reObj.group(2)), int(reObj.group(3)))[-1].setGridLoc(int(reObj.group(1)), int(reObj.group(2)), int(reObj.group(3)))

            # If it's a sprite we add it to the sprite list to be re-rendered as needed
            if isinstance(returnGrid.getBlock(int(reObj.group(1)), int(reObj.group(2)), int(reObj.group(3)))[-1], pygame.sprite.Sprite) :
                global spriteList
                spriteList.append(returnGrid.getBlock(int(reObj.group(1)), int(reObj.group(2)), int(reObj.group(3)))[-1])

    return returnGrid

if __name__ == '__main__' :
    # Sprite list is defined before a map is loaded, because during map loading
    # is when the sprite list is built up
    actorList = []
    spriteList = []
    myGrid = loadMap('maps/lanny_test_map1.txt')

    # This is some lame test code. Should find a better way, but w/e.
    myGrid.setBlock(8,4,1, actors.actorTest())
    myGrid.getBlock(8,4,1)[-1].setGridLoc(8,4,1)
    spriteList.append(myGrid.getBlock(8,4,1)[-1])
    actorList.append(myGrid.getBlock(8,4,1)[-1])

    # Pygame ceremony.
    pygame.init()
    screen = pygame.display.set_mode((800, 600))#(1000, 600))#640, 400))
    background = pygame.Surface(screen.get_size())
    background = background.convert()
    background.fill((0, 0, 0))


    # Render the game grid and launch into the primary input loop
    drawMap(myGrid, screen, True)
    running = True

    # Send the data the UI handlers require to function
    UIhandlers.coreVars = {'gameGrid' : myGrid,
                           'screen' : screen,
                           'actorList' : actorList ,
                           'spriteList' : spriteList}

    # Create our UI handler. This is where the UI rendering and control takes
    # place. Keep an eye on it.
    currentUIHandler = UIhandlers.initialize()

    # Dev font
    font = pygame.font.Font(None, 16)
    lastTime = 0

    # Primary event loop. The important stuff goes on here.
    while running:
        # Get our event. Prosessing one at a time because of the nature of our game,
        # we don't need to consider the possibility of simultanious input.
        event = pygame.event.poll()

        # Now we update the screen once events are proccessed.
        # updateRects contains a list of rects that need to be updated, from boh UI and game grid
        updateRects = []

        # Go through and figure out what to do with the input
        if event.type == KEYDOWN :
            updateRects.append(currentUIHandler.get().handleInput(event))

        elif event.type == pygame.QUIT:
            running = False

        # Update the sprites (blits them but doesn't update). There should only
        # be sprites on the grid. No UI elements
        for sprite in spriteList :
            updateRects.append(sprite.update(pygame.time.get_ticks()))

        # Blit the background
        screen.blit(background, (0,0))

        # Blit the entire game-grid here
        drawMap(myGrid, screen, flip=False)

        # Dev mode shit
        if DEV_MODE :
            # Render the cursor location, not always applicable
            screen.blit(font.render("Cursor Loc: %s" % currentUIHandler.get().get_loc(), False, (0,0,255)), (5,5))

            # Calculate FPS
            FPS = 1000/(pygame.time.get_ticks() - lastTime)
            lastTime = pygame.time.get_ticks()
            screen.blit(font.render("FPS: %s" % FPS, False, (0,0,255)), (5,15))


        # This is where we will handle UI updating when we actually have UI. For
        # now all we have is this comment

        # And finally update everything added to updateRects that needs to be
        # drawn to the screen
        pygame.display.update()#updateRects)
