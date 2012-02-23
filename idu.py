#! /usr/bin/env python

# Untitled isometric game level designer utilities
# Copyright(c) 2012 Lan "Lanny" Rogers

from core import *
from sys import argv
from time import sleep
import re

#argv.extend(['--convert-from-ascii-map', 'maps/10x10bigflatmap.txt'])

def renderMap(mapFile, update=False) :
    myGrid = loadMap(mapFile)

    pygame.init()
    screen = pygame.display.set_mode((1000, 600))
    background = pygame.Surface(screen.get_size())
    drawMap(myGrid, screen)
    running = True

    while running :
        event = pygame.event.poll()
        if event.type == pygame.QUIT:
            running = False

        elif update :
            myGrid = loadMap(mapFile)
            drawMap(myGrid, screen)
            background.fill((0,0,0))
            sleep(0.25)


if len(argv) >= 3 and argv[1] == '--render' :
    renderMap(argv[-1], ('-u' in argv))
            
elif len(argv) >= 3 and argv[1] == '--convert-from-ascii-map' :
    # Convert form ascii map to IsoGame format
    asciiMap = open(argv[-1]).readlines() 

    z_coord = -1
    y_coord = 0
    blockDict = {' ':'Air'}
    isoGameMap = asciiMap[0]

    for line in asciiMap :
        if line == '~\n' :
            z_coord += 1
            y_coord = 0

        if re.match(r'\d+=.+', line) :
            reObj = re.match(r'(\d+)=(.+)', line)
            blockDict[reObj.group(1)] = reObj.group(2)

        elif line[0] == '[' :
            foo = line.replace(']','').split('[')[1:]
            for i,block in enumerate(foo) :
                block = block.replace('\n', '')
                if '-r' in argv :
                    isoGameMap += str(i) + ', ' + str(y_coord) + ', ' + str(z_coord) + ':' + blockDict[block] + '\n'
                    
                else :
                    isoGameMap += str(y_coord) + ', ' + str(i) + ', ' + str(z_coord) + ':' + blockDict[block] + '\n'

            y_coord += 1

    open('maps/conversion_output.txt', 'w').write(isoGameMap)

    if '-d' in argv :
        renderMap('maps/conversion_output.txt')

else :
    # Should display help message. Doesn't.
    print 'Pardon?'
