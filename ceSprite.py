import pygame
from ceSheet import CESheet
from ceScript import *
from ceEntity import CEEntity
import ceGame
import ceColor
import random # TODO: write own RNG library

class CESprite(CEEntity):
    '''This is a particular instance of a sprite, including position/state data.'''

    def __init__(self, sheetFile, scriptFile):
        super(CESprite, self).__init__()

        self.sheet = CESheet(sheetFile)

        self.currentAnim = ''
        self.currentFrame = 0

        self.stage = None

        self.script = CEScript(scriptFile)
        self.script.init(self)

    def setState(self, name):
        if getattr(self, 'state', '') == name:
            # we're already in this state, so don't change
            return
        self.state = name
        self.currentAnim = name
        self.currentFrame = 0

    def moveTo(self, pos):
        self.set('x', pos[0])
        self.set('y', pos[1])

    def move(self, dx, dy):
        '''Checks the stage for collisions'''
        sizeX, sizeY = self.sheet.getSize(self.getFramedef()[0])
        if not self.get('collideWall') or \
          self.stage.isClear(self.get('x')+dx, self.get('y')+dy, sizeX, sizeY):
            self.set('x', self.get('x')+dx)
            self.set('y', self.get('y')+dy)

    def advance(self):
        self.currentFrame = (1+self.currentFrame) % (self.getAnimLength())

    def getAnimLength(self):
        return len(self.sheet.getAnim(self.state))

    def getFramedef(self):
        if (self.currentFrame > self.getAnimLength()):
            print(self.currentFrame, self.sheet.getAnim(self.currentAnim))
            return ('', 1000)
        return self.sheet.getAnim(self.currentAnim)[self.currentFrame]

    def update(self, mils):
        super(CESprite, self).update(mils)
        frameName, frameTime = self.getFramedef()
        if self.timer > frameTime:
            self.timer -= frameTime
            self.advance()
        self.script.run(self)

    def render(self, surf, camx, camy):
        self.sheet.draw(surf,
            self.get('x')-camx, self.get('y')-camy, self.getFramedef()[0])

if __name__=='__main__':
  clock = pygame.time.Clock()

  scr = ceGame.init()
  sprites = []
  for i in range(2):
      sprites.append( CESprite('iris', 'player') )
      sprites[-1].setState('walk-w')
      sprites[-1].moveTo( (random.randint(0, 256), random.randint(0, 224)))

  frames = 0

  while ceGame.running:
    frames += 1
    scr.fill(ceColor.hex('008'))

    mils = clock.tick(60)

    ceGame.update()
    # TODO: Game should keep track of sprites and propagate update/render to all

    sprites.sort(key=(lambda s:s.get('y')))

    for sprite in sprites:
        sprite.update(mils)
        sprite.render(scr, *ceGame.getCamera())

        if sprite.get('x')<-16:
            sprite.set('x',ceGame.XSIZE)
        elif sprite.get('x')>ceGame.XSIZE:
            sprite.set('x',-16)

        if sprite.get('y')<-16:
            sprite.set('y',ceGame.YSIZE)
        elif sprite.get('y')>ceGame.YSIZE:
            sprite.set('y',-16)

    ceGame.render(scr)

    if frames%60==0:
        print(len(sprites), clock.get_fps())
        for x in range(10):
            sprites.append( CESprite('iris', 'player') )
            sprites[-1].setState('walk-w')
            sprites[-1].moveTo( (random.randint(0, 256), random.randint(0, 224)))
