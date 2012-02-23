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

class Actor(pygame.sprite.Sprite, Block) :
    '''All actors should extend this class.
    Basically an actor is an NPC or a player controlled character.'''
    def __init__(self, graphicDict, state = 'standing', fps = 10):
        pygame.sprite.Sprite.__init__(self)
        self._state = state
        self._graphicDict = graphicDict
        self._images = self._graphicDict[state]
        self._acting = False
        self._walkingFrames = 0

        # Store this, we may need it
        self._fps = fps

        # Our sprite offsets. Used for rendering non 47x47 sprites, or moving any
        # sprite on the screen.
        self.x_offset = 7
        self.y_offset = -11

        # Track the time we started, and the time between updates.
        # Then we can figure out when we have to switch the image.
        self._start	= pygame.time.get_ticks()
        self._delay	= 1000 / fps
        self._last_update = 0
        self._frame	= 0
        self.image = self._images[self._frame]
        # Defining a default location on screen for our sprite
        self.location = (0,0)

    def walk(self, direction, gameGrid) :
        if self._acting :
            return

        self._facing = direction[:2]

        self._acting = True
        self._walkingFrames = self._fps

        self._xChange = 23 / self._fps
        self._yChange = 10 / self._fps
        self._newLoc = list(self.gridLocation)

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
        if tuple(self._newLoc) not in self._gameGrid.getValidMovement(self.gridLocation[0], self.gridLocation[1], self.gridLocation[2]) :
            print 'Invalid move! Alert! Alert!'
            self._walkingFrames = 0
            self._acting = False
            return

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

                    self._gameGrid.setBlock(self._newLoc[0], self._newLoc[1], self._newLoc[2], self)
                    self._gameGrid.setBlock(self.gridLocation[0], self.gridLocation[1], self.gridLocation[2], Air())
                    self.gridLocation = tuple(self._newLoc)

                    # Set graphic state back to standing
                    self.setGraphicState('standing-' + self._facing)

                    # Set acting to false to allow further commands
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
        self.x_offset = 7
        self.y_offset = -11

        gDict = {'walking-SW' : load_sliced_sprites(32, 58, 'assets/actors/test_sprite/walk_cycle_front.png'),
                 'walking-SE' : [pygame.transform.flip(i, True, False) for i in load_sliced_sprites(32, 58, 'assets/actors/test_sprite/walk_cycle_front.png')],
                 'walking-NW' : load_sliced_sprites(32, 58, 'assets/actors/test_sprite/walk_cycle_back.png'),
                 'walking-NE' : [pygame.transform.flip(i, True, False) for i in load_sliced_sprites(32, 58, 'assets/actors/test_sprite/walk_cycle_back.png')], 
                 'standing-SW' : [pygame.image.load('assets/actors/test_sprite/standing-SW.png')],
                 'standing-SE' : [pygame.transform.flip(pygame.image.load('assets/actors/test_sprite/standing-SW.png'), True, False)] ,
                 'standing-NW' : [pygame.image.load('assets/actors/test_sprite/standing-NW.png')],
                 'standing-NE' : [pygame.transform.flip(pygame.image.load('assets/actors/test_sprite/standing-NW.png'), True, False)] }

        Actor.__init__(self,
                       gDict,
                       state = 'standing-SW',
                       fps = 7)
