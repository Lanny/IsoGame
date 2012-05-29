import pdb

class Node() :
    def __init__(self, startLoc, endLoc, parent=None) :
        self.x,self.y,self.z = startLoc
        self.parent = parent

        if not parent :
            self.gVal = 0
        else :
            self.gVal = self.parent.gVal + 1

        self.hVal = Heurisitc(startLoc, endLoc)
        self.fVal = self.gVal + self.hVal


    def __str__(self) :
        return '(' + str(self.x) + ',' + str(self.y) + ',' + str(self.z) + ')'

    def __eq__(self, x) :
        try :
            if self.x == x.x and self.y == x.y and self.z == x.z :
                return True
            else :
                return False
        except AttributeError :
            return False

    def getTuple(self) :
        return (self.x,self.y,self.z)

class Path() :
    '''A simple class for building up a path'''
    def __init__(self) :
        self.closedList = []
        self.openList = []

    def __str__(self) :
        return ','.join([str(i) for i in self.closedList])

    def getPath(self) :
        return self.closedList

    def getLastNode(self) :
        return self.closedList[-1]

    def getDirections(self) :
        print [str(i) for i in self.closedList]
        directionList = []

        lastPoint = self.closedList[0].getTuple()
        for point in self.getPath()[1:] :
            point = point.getTuple()
            print point, ':', lastPoint
            nextDir = ''
            if point[0] - lastPoint[0] == -1 :
                nextDir = 'NE'

            elif point[0] - lastPoint[0] == 1 :
                nextDir = 'SW'

            elif point[1] - lastPoint[1] == -1 :
                nextDir = 'NW'

            elif point[1] - lastPoint[1] == 1 :
                nextDir = 'SE'

            if point[2] - lastPoint[2] == -1 :
                nextDir += 'D'

            elif point[2] - lastPoint[2] == 1 :
                nextDir += 'U'

            directionList.append(nextDir)
            lastPoint = point

        return directionList


    def putNode(self, node) :
        if not isinstance(node, Node) :
            raise TypeError('node argument must be instance of Node class')

        else :
            self.closedList.append(node)

def getValidMovement(grid, loc) :
    '''Get all valid orthagonal moves over a given grid for a given location'''
    
    # Unpack loc
    x = loc.x
    y = loc.y
    z = loc.z

    # All possible orthagonal moves
    candidateMoves = [
            #(x, y+1, z-1),
            #(x, y-1, z-1),
            #(x+1, y, z-1),
            #(x-1, y, z-1),
        (x, y+1, z),
        (x, y-1, z),
        (x+1, y, z),
        (x-1, y, z)
        #(x, y+1, z+1),
        #(x, y-1, z+1),
        #(x+1, y, z+1),
        #(x-1, y, z+1)]
        ]

    validMoves = []
    for move in candidateMoves :
        # Get rid of the ones that aren't valid. We use the try/except clause
        # in case we overrun a list.

        # Is move still valid?
        valid = True
        
        try :
            # Test if there is a solid entity in the way of possible move
            if True in [i.isSolid() for i in grid.getBlock(move)] :
                valid = False


            # Is there a solid block under the proposed move?
            else :
                try :
                    if True not in [i.isSolid() for i in grid.getBlock(move[0], move[1], move[2]-1)] :
                        valid = False
                except IndexError :
                    valid = False

        except IndexError :
            valid = False

        if valid : validMoves.append(move)

    # And hand us back the result
    return validMoves

def Heurisitc(startLoc, endLoc) :
    '''A lame heuristic that could be hella better :o'''
    return (abs(startLoc[0]-endLoc[0]) + abs(startLoc[1]-endLoc[1]) + abs(startLoc[2]-endLoc[2]))

def aStar(gameGrid, startLoc, endLoc) :
    '''A* pathfinding algorith, sorta. Returns a Path object'''
    myPath = Path()
    closedList = []
    openList = [Node(startLoc, endLoc)]
    finalNode = Node(endLoc, endLoc)

    while openList :
        # Sort in descending order by F value
        openList.sort(key=lambda x: x.fVal, reverse=True)

        currNode = openList.pop()

        if currNode == finalNode :
            # Found our destination, now trace backwards
            path = [currNode]
            while path[-1].getTuple() != startLoc :
                path.append(path[-1].parent)

            path.reverse()

            # And finally package it in a Path object to be returned
            myPath.closedList = path
            print myPath.getDirections()
            return myPath

        neighbors = [Node(neighbor, endLoc, parent=currNode) for neighbor in getValidMovement(gameGrid, currNode)]

        rList = []
        for node in neighbors :
            if node in closedList :
                rList.append(node)

        for node in rList :
            neighbors.remove(node)

        for node in neighbors :
            if node in openList :
                if currNode.gVal + 1 < node.gVal :
                    node.parent = currNode
                    node.gVal = currNode.gVal+1
                    node.fVal = node.gVal + node.hVal

            else :
                openList.append(node)

        closedList.append(currNode)
