import pygame, random, sys, os, math
from sprite_objects import *
from pygame.locals import *

class Game():
  def __init__(self, title, width, height, bg_color) -> None:
    self.title = title
    self.width = width
    self.height = height
    self.bg_color = bg_color
    self.screen, self.background = self.create_window()
    self.lose = self.win = False
    # allows animation delays
    self.incrementer = 2
    self.init_time = pygame.time.get_ticks()
    self.next_asteroid_time = 0
    self.asteroid_img = pygame.image.load('data/asteroid.png')
    self.enemy_level = [
      [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
      [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
      [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
      [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
      [0,0,0,0,1,0,0,0,1,0,0,0,1,0,0,0],
      [1,0,0,0,0,0,1,0,0,0,0,1,0,0,1,0],
      [1,0,0,0,0,0,0,0,0,0,0,1,0,0,0,1],
      [0,1,0,0,0,0,0,0,0,0,1,0,1,0,1,0]]
    pygame.init()
    self.screen.blit(self.background, (0,0))

  def create_window(self):
    """ return screen and background objects """
    screen = pygame.display.set_mode((self.width, self.height),
                                      HWSURFACE|DOUBLEBUF)
    background = pygame.Surface(screen.get_size())
    background = background.convert()
    background.fill(self.bg_color)
    screen.blit(background, (0,0))
    pygame.display.flip()
    screen.fill(self.bg_color)
    pygame.display.set_caption(self.title)
    return screen, background
  
  def draw_text(self, text, color=(0,200,0), font_size=30):
    font = pygame.font.SysFont(None, font_size)
    return font.render(text, False, color)

  def draw_hp(self, player):
    for i in range(0, player.hp):
      self.screen.blit(
        self.draw_text("*",
                  (0,200,0), 50),
                  (i*15, self.height - 20))

  def make_level(self, sprites):
    # initialize width / height
    img = pygame.image.load('data/enemy_ship.png')
    """ create sprite group of enemies at coordinates specified by matrix """  
    for i in range(len(self.enemy_level)):
      for j in range(len(self.enemy_level[i])):
        if self.enemy_level[i][j] == 1:
          angle = 270
          radius = 50
          arc_dir = 5
          if random.random() > .5:
            arc_dir = -5
          enemy = Enemy(((img.get_width() + 12) * j),
                       ((img.get_height() + 12)* i),
                       angle,
                       radius,
                       arc_dir,
                       sprites)
          sprites.add(enemy)

  def intro(self):
    while True:
      # need event handler for this loop to function
      for event in pygame.event.get():
        if event.type == QUIT:
          return
      self.screen.blit(self.background, (0,0))
      self.screen.blit(
        self.draw_text("arrow keys to move, space to shoot, press enter to play"),
                       (150, self.height / 2 - 30))
      keys = pygame.key.get_pressed()
      if keys[pygame.K_RETURN]:
        break
      if keys[pygame.K_END] or keys[pygame.K_ESCAPE]:
        sys.exit(0)
      pygame.display.flip()

  def check_state(self):
    if self.win:
      self.screen.blit(
        self.draw_text("you're a winner! :)"),
                      (self.width / 2 - 100, self.height / 2 - 30))
    if self.lose:
      self.screen.blit(
        self.draw_text("you lose :(",
                       (200,0,0)),
                       (self.width / 2 - 100, self.height / 2 - 30))

class Stars():
  def __init__(self, game) -> None:
    random.seed()
    self.direction = "down"
    self.stars = []
    # count of stars per layer
    self.layer_1 = 200
    self.layer_2 = 400
    self.layer_3 = 800
    self.num_stars = self.layer_1 + self.layer_2 + self.layer_3
    self.white = 255, 255, 255
    self.lightblue = 200, 200, 255
    self.lightred = 255, 200, 200
    self.lightyellow = 255, 200, 255
    self.delay = 8
    self.game = game
    self.init(self.game.screen)
    self.init_layer_1()

  def init(self, screen):
    for loop in range(0, self.num_stars):
      star = [random.randrange(0, screen.get_width() - 1),
              random.randrange(0, screen.get_height() - 1)]
      self.stars.append(star);

  def move(self, start, end):
    for loop in range(start, end):
      if (self.direction == "down"):
        if (self.stars[loop][1] != self.game.height - 1):
            self.stars[loop][1] = self.stars[loop][1] + 1
        else:
          self.stars[loop][0] = random.randrange(0, self.game.width - 1)
          self.stars[loop][1] = 1

  def init_layer_1(self):
    for loop in range(0, self.layer_1):
      self.game.screen.set_at(self.stars[loop], self.white)

  def move_layers(self):
    self.move(
      0,
      self.layer_1)
    if (self.game.incrementer % 2 == 0):
      self.move(
        self.layer_1 + 1,
        self.layer_1 + self.layer_2)
    if (self.game.incrementer % 5 == 0):
      self.move(
        self.layer_1 + self.layer_2 + 1,
        self.num_stars)

  def draw(self):
    for loop in range(0, self.layer_1):
      self.game.screen.set_at(self.stars[loop], self.lightblue)
    for loop in range(self.layer_1 + 1, self.layer_1 + self.layer_2):
      self.game.screen.set_at(self.stars[loop], self.lightred)
    for loop in range(self.layer_1 + self.layer_2 + 1, self.num_stars):
      self.game.screen.set_at(self.stars[loop], self.lightyellow)