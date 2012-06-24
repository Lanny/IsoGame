import pygame, random
import weapons
from blocks import Block, Air, DamageIndicator

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
        ex,ey,ez = sy
        sx,sy,sz = sx

    retVal = ''
    if sx < ex : retVal = 'SW'
    elif sx > ex : retVal = 'NE'
    elif sy < ey : retVal = 'SE'
    elif sy > ey : retVal = 'NW'

    # Up/Down
    if sz > ez : retVal += 'D'
    elif sz < ez : retVal += 'U'

    return retVal

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

        # Try to divine our offsets, probably gets overwritten
        self.x_offset, self.y_offset = self._images[0].get_size()
        self.x_offset = 0-((self.x_offset - 47)/2)
        self.y_offset = 0-(self.y_offset - 30)

        # Track the time we started, and the time between updates.
        # Then we can figure out when we have to switch the image.
        self._start	= pygame.time.get_ticks()
        self._delay	= 1000 / fps
        self._last_update = 0
        self._frame	= 0
        self.image = self._images[self._frame]
        # Defining a default location on screen for our sprite
        self.location = (0,0)

        # Actors should do this
        self.solid = True
        self.supporter = False

        # Per turn actions left
        self.moveActionRemaining = True
        self.standardActionRemaining = True
        self.minorActionRemaining = True

        # Set default values for all our stats :
        self.AC = 0
        self.Will = 0
        self.Fortitude = 0
        self.Reflex = 0

        self.HP = 1
        self.maxHP = 1

    def meleeAttack(self, direction, gameGrid) :
        print 'hearah'
        if self._acting == True : return
        else : self._acting = True

        print directionToCoord(direction, self.gridLocation)
        # Let's try ot acquire our target
        l = gameGrid.getBlock(directionToCoord(direction, self.gridLocation))

        target = None
        for candidate in l :
            print candidate
            if isinstance(candidate, Actor) :
                target = candidate
        if not target :
            print 'No target at indicated location'
            self._acting = False
            return

        # Target is identified, let's roll!
        # /rimshot
        hit = random.randint(1,20)
        # Add our modifiers here...

        dam = self.meleeWeapon.roll()
        # Add our DAM modifiers here...
        
        # And now deal it to our target, throw gameGrid in there because
        # I designed myself into a corner of retardation
        target.dealDamage(hit, 'AC', dam, gameGrid)

        self._facing = direction[:2]
        self._actingFrames = 4

        self.setGraphicState('attacking-%s' % self._facing)

    def dealDamage(self, hit, save, damage, gameGrid) :
        if save == 'AC' : defense = self.AC
        elif save == 'Will' : defense = self.Will
        elif save == 'Fortitude' : defense = self.Fortitude
        elif save == 'Reflex' : defense = self.Reflex
        else : raise Exception('Say what?')

        if defense > hit :
            # Attack missed, in the future do something cool
            return
        
        self.HP -= damage
        gameGrid.setBlock(self.gridLocation[0], self.gridLocation[1], self.gridLocation[2], DamageIndicator(damage, self.gridLocation, gameGrid), ow=False)

        if self.HP < 0 :
            # Dead! Hah!
            self.die(gameGrid)

    def die(self, gameGrid) :
        gameGrid.removeBlock(self, self.gridLocation)

    def walkChain(self, chain, gameGrid) :
        self._walkingChain = chain[1:]
        gameGrid = gameGrid
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
                    self._gameGrid.removeBlock(self, self.gridLocation)
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

                    # Call our callback if it exists
                    try : self._cb()
                    except AttributeError : pass

            # End walking/acting code, start normal animation code
            self._frame += 1

            # Animation finished, cycling to beginning of sequence
            if self._frame >= len(self._images):
                self._frame = 0
                                    
            self.image = self._images[self._frame]
            self._last_update = t

            return pygame.Rect(self.location, self.image.get_size())

    def setGraphicState(self, newState) :
        self._images = self._graphicDict[newState]

        # Try to divine our offsets, probably gets overwritten
        self.x_offset, self.y_offset = self._images[0].get_size()
        self.x_offset = 0-((self.x_offset - 47)/2)
        self.y_offset = 0-(self.y_offset - 30)

        # Force an update, even if it woudn't be due yet
        self._last_update -= self._delay

    def setLoc(self, x_loc, y_loc) :
        self.location = (x_loc, y_loc)

    def setGridLoc(self, gx, gy, gz) :
        self.gridLocation = (gx, gy, gz)
        
    def getPortrait(self) :
      try : return self._graphicDict['portrait']
      except KeyError :
        self._graphicDict['portriat'] = pygame.image.load('assets/actors/default/portrait.png').convert_alpha()
        return self._graphicDict['portriat']

    def isActing(self) :
        return self._acting

    def get_img(self) :
        return self.image

class actorTest(Actor) :
    name = 'Actor Test'
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
                 'attacking-NE' : [pygame.transform.flip(i, True, False) for i in load_sliced_sprites(39, 57, 'assets/actors/test_sprite/attack_back.png')],
                 'portrait' : pygame.image.load('assets/actors/test_sprite/portrait.png')
                }

        Actor.__init__(self,
                       gDict,
                       state = 'standing-SW',
                       fps = 10)

        self.meleeWeapon = weapons.RustyButterKnife()

        self.x_offset = 7
        self.y_offset = -29

class testHound(Actor) :
    name = 'Test Hound'
    def __init__(self) :
        gDict = {'walking-SW' : load_sliced_sprites(48, 39, 'assets/actors/hound/walk_cycle-front.png'),
                 'walking-SE' : [pygame.transform.flip(i, True, False) for i in load_sliced_sprites(48, 39, 'assets/actors/hound/walk_cycle-front.png')],
                 'walking-NW' : load_sliced_sprites(48, 39, 'assets/actors/hound/walk_cycle_back.png'),
                 'walking-NE' : [pygame.transform.flip(i, True, False) for i in load_sliced_sprites(48, 39, 'assets/actors/hound/walk_cycle_back.png')], 
                 'standing-SW' : [pygame.image.load('assets/actors/hound/standing-front.png')],
                 'standing-SE' : [pygame.transform.flip(pygame.image.load('assets/actors/hound/standing-front.png'), True, False)] ,
                 'standing-NW' : [pygame.image.load('assets/actors/hound/standing-back.png')],
                 'standing-NE' : [pygame.transform.flip(pygame.image.load('assets/actors/hound/standing-back.png'), True, False)],
                 'attacking-SW' : load_sliced_sprites(48, 41, 'assets/actors/hound/attack_front.png'),
                 'attacking-SE' : [pygame.transform.flip(i, True, False) for i in load_sliced_sprites(48, 41, 'assets/actors/hound/attack_front.png')],
                 'attacking-NW' : load_sliced_sprites(48, 41, 'assets/actors/hound/attack_back.png'),
                 'attacking-NE' : [pygame.transform.flip(i, True, False) for i in load_sliced_sprites(48, 41, 'assets/actors/hound/attack_back.png')],
                 'portrait' : pygame.image.load('assets/actors/hound/portrait.png')
                }

        Actor.__init__(self,
                       gDict,
                       state = 'standing-SW',
                       fps = 9)

        self.maxHP = 10
        self.HP = 10
        self.AC = 10

        self.meleeWeapon = weapons.HoundClaws()

class breakablePlant(Actor) :
    name = 'Tree'
    def __init__(self) :
        gDict = {'foo' : [pygame.image.load('assets/blocks/tree_1.png')]}
        Actor.__init__(self,
                       gDict,
                       state = 'foo',
                       fps = 1)
