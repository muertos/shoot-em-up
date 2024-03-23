import pygame, random, sys, os
from pygame.locals import *

def load_png(name):
  """ load image and return image object """
  fullname = os.path.join('data', name)
  try:
    image = pygame.image.load(fullname)
    if image.get_alpha is None:
      image = image.convert()
    else:
      image = image.convert_alpha()
  except pygame.error as message:
    print('Cannot load image:', fullname)
    raise SystemExit(message)
  return image, image.get_rect()

class Player(pygame.sprite.Sprite):
  def __init__(self, x, y, sprite_group) -> None:
    # adds Player sprite to sprite_group
    pygame.sprite.Sprite.__init__(self, sprite_group)
    self.image, self.rect = load_png('paddle.png')
    self.rect.x = x
    self.rect.y = y

  def move(self, direction):
    self.rect.x += direction

class Bullet(pygame.sprite.Sprite):
  def __init__(self, x, y, sprite_group) -> None:
    # adds Bullet sprite to sprite_group
    pygame.sprite.Sprite.__init__(self, sprite_group)
    self.image, self.rect = load_png('ball.png')
    self.rect.x = x
    self.rect.y = y

  def move(self, direction):
    self.rect.y += direction

class Brick(pygame.sprite.Sprite):
  def __init__(self, x, y, sprite_group) -> None:
    # adds Brick sprite to sprite_group
    pygame.sprite.Sprite.__init__(self, sprite_group)
    self.image, self.rect = load_png('brick.png')
    self.rect.x = x
    self.rect.y = y