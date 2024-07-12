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
    self.delay = 30

  def move(self, direction):
    self.rect.y += direction

class Brick(pygame.sprite.Sprite):
  def __init__(self, x, y, sprite_group) -> None:
    # adds Brick sprite to sprite_group
    pygame.sprite.Sprite.__init__(self, sprite_group)
    self.image, self.rect = load_png('diamond.png')
    self.rect.x = x
    self.rect.y = y
    self.x_dir = 0
    self.y_dir = 0
    self.speed = 1
    self.move_count = 0

  def move_back_and_forth(self):
    self.rect.x += self.speed
    self.move_count +=1
    if self.move_count > 80:
      self.speed = -self.speed
      self.move_count = 0

  def move(self, x_dir, y_dir):
    self.rect.x += x_dir
    self.rect.y += y_dir

  def set_move_direction(self):
    choice = random.randrange(0,6)
    if choice == 0:
      self.x_dir = 1
      self.y_dir = 0
    if choice == 1:
      self.x_dir = -1
      self.y_dir = 0
    if choice == 2:
      self.x_dir = 0
      self.y_dir = 1
    if choice == 3:
      self.x_dir = 0
      self.y_dir = -1
    if choice == 4:
      self.x_dir = 1
      self.y_dir = 1
    if choice == 5:
      self.x_dir = -1
      self.y_dir = -1

  def move_random(self):
    self.rect.x += self.x_dir
    self.rect.y += self.y_dir
    self.move_count += 1
    if self.move_count > 12:
      self.set_move_direction()
      self.move_count = 0

  def reverse_direction(self):
    self.x_dir = -self.x_dir
    self.y_dir = -self.y_dir

  def temp_stop(self):
    pass
    


