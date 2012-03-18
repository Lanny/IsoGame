class Node() :
    def __init__(self, x, y, z, parent=None) :
        self.x = x
        self.y = y
        self.z = z
        self.parent = parent

    def __str__(self) :
        return '(' + str(self.x) + ',' + str(self.y) + ',' + str(self.z) + ')'

    def __tuple__(self) :
        return (x,y,z)

class Path() :
    '''A simple class for building up a path'''
    def __init__(self) :
        self.closedList = []
        self.openList = []

    def __str__(self) :
        return '\n'.join([tuple(i) for i in self.closedList])

    def getPath(self) :
        return self.closedList

    def getLastNode(self) :
        return self.closedList[-1]

    def putNode(self, node) :
        if not isinstance(node, Node) :
            raise TypeError('node argument must be instance of Node class')

        else :
            self.closedList.append(node)

def getValidMovement(self, grid, loc) :
    '''Get all valid orthagonal moves over a given grid for a given location'''
    
    # Unpack loc
    x = loc[0]
    y = loc[1]
    z = loc[2]

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
                  (x, y+1, z+1),
                  (x+1, y, z+1),
                  (x-1, y, z+1)]

    for move in validMoves :
        # Get rid of the ones that aren't valid. We use the try/except clause
        # in case we overrun a list.
        try :
            # Test if there is a solid entity in the way of possible move
            if True in [i.isSolid() for i in grid.getBlock(move[0], move[1], move[2])] :
                validMoves.remove(move)

            # Is there a solid block under the proposed move?
            elif True not in [i.isSolid() for i in grid.getBlock(move[0], move[1], move[2]-1)] :
                validMoves.remove(move)

        except IndexError :
            validMoves.remove(move)

    # And hand us back the result
    return validMoves

def CheapHeurisitc(startLoc, endLoc) :
    '''A lame heuristic that could be hella better :o'''
    return abs(startLoc[0]-endLoc[0]) + abs(startLoc[1]-endLoc[1])

def aStar(gameGrid, startLoc, endLoc) :
    '''A* pathfinding algorith, sorta.'''
    myPath = Path()
    myPath.putNode(Node(startLoc[0], startLoc[1], startLoc[2]))
    soultionFound = False
    
    while not soultionFound :
        myPath.openList = getValidMovement(myPath.getLastNode())

        # We already weeded out invalid moves, so now we're just skeezing along
        # Find the place with the lowest manhattan distance to our target
        nextNode = myPath.openList[0]
        for node in myPath.openList :
            if CheapHeuristic(tuple(node), endLoc) < CheapHeuristic(tuple(nextNode), endLoc) :
                nextNode = node

        # Enter the node into the path
        myPath.putNode(nextNode)

        if tuple(myPath.getLastNode()) == endLoc :
            return myPath

