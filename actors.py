import pygame
from blocks import Block, Air

def load_sliced_sprites(w, h, filename):
    '''
    Specs :
    	Master can be any height.
    	Sprites frames width must be the same width
    	Master width must be len(frames)*frame.width
    '''
    images = []
    master_image = pygame.image.load(filename)

    master_width, master_height = master_image.get_size()
    for i in xrange(int(master_width/w)):
    	images.append(master_image.subsurface((i*w,0,w,h)))
    return images

def directionToCoord(direction, x, y=None, z=None) :
    if not y and not z and type(x) == tuple :
        x,y,z = x

    if direction == 'NW' : y -= 1
    elif direction == 'SW' : x += 1
    elif direction == 'NE' : x -= 1
    elif direction == 'SE' : y += 1

    return (x, y, z)

def coordToDirection(sx, sy, sz=None, ex=None, ey=None, ez=None) :
    '''Convert two adjacent locations to a direction, behaviour becomes erratic if locations are not adjacent.'''
    if None in (sz,ex,ey,ez) and type(sx) == tuple and type(sy) == tuple :
        sx,sy,sz = sx
        ex,ey,ez = sy

    retVal = ''
    if sx < ex : retVal = 'SW'
    elif sx > ex : retVal = 'NE'
    elif sy < ey : retVal = 'SE'
    elif sy > ey : retVal = 'SW'

    # Up/Down
    if sz > ez : retVal += 'D'
    elif sz < ez : retVal += 'U'

class Actor(pygame.sprite.Sprite, Block) :
    '''All actors should extend this class.
    Basically an actor is an NPC or a player controlled character.'''
    def __init__(self, graphicDict, state = 'standing', fps = 10):
        pygame.sprite.Sprite.__init__(self)
        # Our graphic state
        self._state = state

        # Our selection of animations
        self._graphicDict = graphicDict
        self._images = self._graphicDict[state]

        # Is the actor currently doing something?
        self._acting = False

        # When 0, do whatever, otherwise act out remaining frames
        self._walkingFrames = 0
        self._actingFrames = 0

        # Store this, we may need it
        self._fps = fps

        # Our sprite offsets. Used for rendering non 47x47 sprites, or moving any
        # sprite on the screen.
        self.x_offset = 7
        self.y_offset = -13

        # Track the time we started, and the time between updates.
        # Then we can figure out when we have to switch the image.
        self._start	= pygame.time.get_ticks()
        self._delay	= 1000 / fps
        self._last_update = 0
        self._frame	= 0
        self.image = self._images[self._frame]
        # Defining a default location on screen for our sprite
        self.location = (0,0)

    def meleeAttack(self, direction, gameGrid) :
        if self._acting == True : return
        else : self._acting = True

        self._facing = direction[:2]
        self._actingFrames = 4

        self.setGraphicState('attacking-%s' % self._facing)

    def walkChain(self, chain, gameGrid) :
        self._walkingChain = chain[1:]
        self._gameGrid = gameGrid
        self.walk(chain[0], gameGrid)

    def walkNext(self, gameGrid) :
        try : 
            if self._walkingChain == [] : return
        except AttributeError : 
            return

        direction = self._walkingChain[0]
        self._walkingChain = self._walkingChain[1:]
        self.walk(direction, gameGrid)

    def walk(self, direction, gameGrid) :
        if self._acting :
            return

        # Direction is going to look like "NWU" so just take the first two chars
        self._facing = direction[:2]
        print self._facing

        self._acting = True
        self._walkingFrames = self._fps

        self._xChange = 23 / self._fps
        self._yChange = 10 / self._fps
        self._newLoc = list(self.gridLocation)

        # Animate the motion
        self.setGraphicState('walking-%s' % self._facing)

        # The global game grid. This feels wrong but I don't know how else to do
        # it.
        self._gameGrid = gameGrid

        if 'NW' in direction :
            self._xChange = -self._xChange
            self._yChange = -self._yChange
            self._newLoc[1] -= 1

        elif 'SW' in direction :
            self._xChange = -self._xChange
            self._newLoc[0] += 1

        elif 'NE' in direction :
            self._yChange = -self._yChange
            self._newLoc[0] -= 1

        elif 'SE' in direction :
            self._newLoc[1] += 1

        if 'U' in direction :
            self._yChange -= 47 / self._fps
            self._newLoc[2] += 1

        elif 'D' in direction :
            self._yChange += 47 / self._fps
            self._newLoc[2] -= 1

        # Make sure move is valid
        #if tuple(self._newLoc) not in self._gameGrid.getValidMovement(self.gridLocation[0], self.gridLocation[1], self.gridLocation[2]) :
        #    print 'Invalid move! Alert! Alert!'
        #    self._walkingFrames = 0
        #    self._acting = False
        #    return

        for block in self._gameGrid.getBlock(self._newLoc[0], self._newLoc[1], self._newLoc[2]) :
            if block.isSolid() :
                # Target cell is occupied.
                # We should attempt to jump, but I'm not worrying about jumping just now
                # Stops walk action if progress isn't possible
                self._walkingFrames = 0
                self._acting = False

    def update(self, t):
        '''Advance through the spritesheet if nessecary. Called every cycle
        through the game loop.'''
        if t - self._last_update > self._delay:
            # Walking code. Sloopy but what can ya do?
            if self._walkingFrames :
                self._walkingFrames -= 1
                self.x_offset += self._xChange
                self.y_offset += self._yChange

                if not self._walkingFrames :
                    # Reached end of cycle, reset offsets and move actor to new grid location
                    self.x_offset -= self._xChange * self._fps
                    self.y_offset -= self._yChange * self._fps

                    self._gameGrid.setBlock(self._newLoc[0], self._newLoc[1], self._newLoc[2], self, ow=False, insPos=0)
                    self._gameGrid.removeBlock(self.gridLocation[0], self.gridLocation[1], self.gridLocation[2], self)
                    self.gridLocation = tuple(self._newLoc)

                    # Set graphic state back to standing
                    self.setGraphicState('standing-' + self._facing)

                    # Set acting to false to allow further commands
                    self._acting = False

                    self.walkNext(self._gameGrid)

            # General acting code
            if self._actingFrames :
                self._actingFrames -= 1

                if not self._actingFrames :
                    self.setGraphicState('standing-%s' % self._facing)
                    self._acting = False

            # End walking code, start normal animation code
            self._frame += 1

            # Animation finished, cycling to beginning of sequence
            if self._frame >= len(self._images):
                self._frame = 0
                                    
            self.image = self._images[self._frame]
            self._last_update = t

            return pygame.Rect(self.location, self.image.get_size())

    def setGraphicState(self, newState) :
        self._images = self._graphicDict[newState]

        # Force an update, even if it woudn't be due yet
        self._last_update -= self._delay

    def setLoc(self, x_loc, y_loc) :
        self.location = (x_loc, y_loc)

    def setGridLoc(self, gx, gy, gz) :
        self.gridLocation = (gx, gy, gz)
        
    def render(self, screen) :
        self.update(pygame.time.jet_ticks())
        screen.blit(self.image, self.location)

    def isActing(self) :
        return self._acting

    def get_img(self) :
        return self.image

class actorTest(Actor) :
    def __init__(self) :
        gDict = {'walking-SW' : load_sliced_sprites(32, 58, 'assets/actors/test_sprite/walk_cycle_front.png'),
                 'walking-SE' : [pygame.transform.flip(i, True, False) for i in load_sliced_sprites(32, 58, 'assets/actors/test_sprite/walk_cycle_front.png')],
                 'walking-NW' : load_sliced_sprites(32, 58, 'assets/actors/test_sprite/walk_cycle_back.png'),
                 'walking-NE' : [pygame.transform.flip(i, True, False) for i in load_sliced_sprites(32, 58, 'assets/actors/test_sprite/walk_cycle_back.png')], 
                 'standing-SW' : [pygame.image.load('assets/actors/test_sprite/standing-SW.png')],
                 'standing-SE' : [pygame.transform.flip(pygame.image.load('assets/actors/test_sprite/standing-SW.png'), True, False)] ,
                 'standing-NW' : [pygame.image.load('assets/actors/test_sprite/standing-NW.png')],
                 'standing-NE' : [pygame.transform.flip(pygame.image.load('assets/actors/test_sprite/standing-NW.png'), True, False)],
                 'attacking-SW' : load_sliced_sprites(39, 57, 'assets/actors/test_sprite/attack_front.png'),
                 'attacking-SE' : [pygame.transform.flip(i, True, False) for i in load_sliced_sprites(39, 57, 'assets/actors/test_sprite/attack_front.png')],
                 'attacking-NW' : load_sliced_sprites(39, 57, 'assets/actors/test_sprite/attack_back.png'),
                 'attacking-NE' : [pygame.transform.flip(i, True, False) for i in load_sliced_sprites(39, 57, 'assets/actors/test_sprite/attack_back.png')]
                }

        Actor.__init__(self,
                       gDict,
                       state = 'standing-SW',
                       fps = 10)

        self.x_offset = 7
        self.y_offset = -29
