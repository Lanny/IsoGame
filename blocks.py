import pygame
x=1

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

class Block(object) :
    '''Generic base class for blocks. Contains basic information pertaining to how they are rendered and treated.'''
    x_offset = 0
    y_offset = 0

    # Determine if actors can normally move through this kind of block
    solid = True
    def __init__(self) :
        pass

    def isSolid(self) :
        return self.solid

class AnimatedBlock(pygame.sprite.Sprite, Block) :
    '''Basically a ripoff of this guy's work :
    http://shinylittlething.com/2009/07/22/pygame-and-animated-sprites-take-2/'''
    def __init__(self, images, fps = 10):
        pygame.sprite.Sprite.__init__(self)
        self._images = images

        # Track the time we started, and the time between updates.
        # Then we can figure out when we have to switch the image.
        self._start	= pygame.time.get_ticks()
        self._delay	= 1000 / fps
        self._last_update = 0
        self._frame	= 0
        self.image = self._images[self._frame]
        # Defining a default location on screen for our sprite
        self.location = (0,0)
        
    def update(self, t):
        '''Called for each sprite sub-class each turn over the event loop'''
        if t - self._last_update > self._delay:
            self._frame += 1
            # Animation finished, cycling to beginning of sequence
            if self._frame >= len(self._images):
                self._frame = 0
                                    
            self.image = self._images[self._frame]
            self._last_update = t

            return pygame.Rect(self.location, self.image.get_size())

    def setGridLoc(self, gx, gy, gz) :
        self.gridLocation = (gx, gy, gz)

    def setLoc(self, x_loc, y_loc) :
        self.location = (x_loc, y_loc)
        
    def render(self, screen):
        self.update(pygame.time.jet_ticks())
        screen.blit(self.image, self.location)

    def get_img(self) :
        return self.image

class Air(Block) :
    name = 'Air'
    solid = False
    def get_img(self) :
        return None

class Dirt(Block) :
    name = 'Dirt'
    def get_img(self) :
        return pygame.image.load('assets/blocks/grass_and_dirt.png')

class Rock1(Block) :
    name = 'Rock1'
    def get_img(self) :
        return pygame.image.load('assets/blocks/rock1.png')

class TallGrass1(Block) :
    name = 'TallGrass1'
    solid = False
    def get_img(self) :
        return pygame.image.load('assets/blocks/tall_grass1.png')

class PlaceHolder(Block) :
    name = 'PlaceHolder'
    def get_img(self) :
        return pygame.image.load('assets/blocks/placeholder.png')

class SpriteTest(AnimatedBlock) :
    def __init__(self) :
        AnimatedBlock.__init__(self, 
                               load_sliced_sprites(47, 47, 'assets/blocks/spritetest.png'), 
                               fps=5)

        return

class FencerTest(AnimatedBlock) :
    x_offset = 7
    y_offset = -11
    def __init__(self) :
        AnimatedBlock.__init__(self, 
                               load_sliced_sprites(32, 58, 'assets/actors/test_sprite/walk_cycle_front.png'), 
                               fps=7)

        return

class selectArrow(AnimatedBlock) :
    name = 'SelectArrow'
    solid = False

    def __init__(self) :
        AnimatedBlock.__init__(self,
                               [0,0],
                               fps = 10)

        self.image = pygame.image.load('assets/UI/arrow.png')

    def get_img(self) :
        return self.image

    def update(self, t) :
        if self._needsUpdate :
            return pygame.Rect(self.location, self.image.get_size())

    def setUpdateFlag(self) :
        self._needsUpdate = 1

    def clearUpdateFlag(self) :
        self._needsUpdate = 0
