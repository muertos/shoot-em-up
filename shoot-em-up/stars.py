import pygame
import random

from utility_functions import load_png

class Star(pygame.sprite.Sprite):
  def __init__(self, image_file, sprite_group) -> None:
    pygame.sprite.Sprite.__init__(self, sprite_group)
    self.image, self.rect = load_png(image_file)

class Stars():
  def __init__(self, game) -> None:
    random.seed()
    self.direction = "down"
    self.stars = []
    # count of stars per layer
    self.layer_1 = 80
    self.layer_2 = 70
    self.layer_3 = 50
    self.num_stars = self.layer_1 + self.layer_2 + self.layer_3
    self.game = game
    self.init(game)
    #self.init_layer_1()

  def init(self, game):
    # XXX: DRY
    for loop in range(0, self.layer_1):
      star = Star("star_blue_white.png", game.sprite_groups["stars"])
      x = random.randrange(0, int(game.width - 1))
      y = random.randrange(0, int(game.height - 1))
      star.rect.x = x
      star.rect.y = y
      self.stars.append(star)
    for loop in range(self.layer_1 + 1, self.layer_1 + self.layer_2 + 1):
      star = Star("star_orange.png", game.sprite_groups["stars"])
      x = random.randrange(0, int(game.width - 1))
      y = random.randrange(0, int(game.height - 1))
      star.rect.x = x
      star.rect.y = y
      self.stars.append(star)
    for loop in range(self.layer_1 + self.layer_2 + 1, self.num_stars):
      star = Star("star_red.png", game.sprite_groups["stars"])
      x = random.randrange(0, int(game.width - 1))
      y = random.randrange(0, int(game.height - 1))
      star.rect.x = x
      star.rect.y = y
      self.stars.append(star)

  def move(self, start, end):
    for loop in range(start, end):
      if (self.direction == "down"):
        if (self.stars[loop].rect.y != self.game.height - 1):
            self.stars[loop].rect.y += 1
        else:
          self.stars[loop].rect.x = random.randrange(0, int(self.game.width - 1))
          self.stars[loop].rect.y = 1

  def move_layers(self):
    self.move(
      0,
      self.layer_1)
    if (self.game.animation_delay_counter % 2 == 0):
      self.move(
        self.layer_1 + 1,
        self.layer_1 + self.layer_2)
    if (self.game.animation_delay_counter % 5 == 0):
      self.move(
        self.layer_1 + self.layer_2 + 1,
        self.num_stars - 1)