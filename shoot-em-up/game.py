import pygame
import sys

from pygame.locals import *
from asteroid import Asteroid
from enemies import *
from utility_functions import *
from player import *

class Game():
  def __init__(self, title, width, height, bg_color) -> None:
    self.title = title
    self.width = width
    self.height = height
    self.bg_color = bg_color
    self.screen, self.background = self.create_window()
    self.clock = pygame.time.Clock()
    self.lose = self.win = False
    self.animation_delay_counter = 1
    self.init_time = pygame.time.get_ticks()
    self.next_asteroid_time = 0
    self.asteroid_img = pygame.image.load('data/asteroid.png')
    self.time_now = pygame.time.get_ticks()

    self.enemy_level = [
      [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
      [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
      [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
      [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
      [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
      [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
      [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
      [0,2,0,0,0,1,0,0,0,1,0,0,0,2,0,0,0,1,0,0,0,1,0,0,0,2,0],
      [2,0,2,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,2,0,2],
      [0,2,0,0,0,1,0,0,0,1,0,0,0,2,0,0,0,1,0,0,0,1,0,0,0,2,0]
    ]

    #self.enemy_level = [
    #  [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    #  [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    #  [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    #  [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    #  [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    #  [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    #  [0,0,0,0,0,1,0,1,0,0,0,0,1,0,0,0,0,0,0],
    #  [0,0,0,0,0,0,1,0,0,0,0,1,0,1,0,0,0,0,0],
    #  [0,0,0,0,0,1,0,1,0,0,0,0,1,0,0,0,0,0,0]]

    self.sprite_groups = {
      "bullets": pygame.sprite.Group(),
      "enemies": pygame.sprite.Group(),
      "enemy_bullets": pygame.sprite.Group(),
      "player": pygame.sprite.Group(),
      "asteroids": pygame.sprite.Group(),
      "power_ups": pygame.sprite.Group()
    }

    self.screen.blit(self.background, (0,0))
    self.make_level(self.sprite_groups["enemies"])
    pygame.init()
    self.intro()

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

  def make_level(self, sprites):
    # initialize width / height
    """ create sprite group of enemies at coordinates specified by matrix """  
    for i in range(len(self.enemy_level)):
      for j in range(len(self.enemy_level[i])):
        if self.enemy_level[i][j] == 1:
          img = pygame.image.load('data/enemy_ship_arc.png')
          enemy = ArcEnemy(((img.get_width() + 12) * j),
                       ((img.get_height() + 12) * i),
                       sprites)
          sprites.add(enemy)
        if self.enemy_level[i][j] == 2:
          img = pygame.image.load('data/enemy_ship_dart.png')
          enemy = DartingEnemy(((img.get_width() + 12) * j),
                              ((img.get_height() + 12) * i),
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

  def handle_input(self, player):
    for event in pygame.event.get():
      if event.type == QUIT:
        return

    keys = pygame.key.get_pressed()
    prev_player_x = player.rect.x
    prev_player_y = player.rect.y

    if not self.lose:
      if keys[pygame.K_LEFT]:
        player.move(-player.speed, 0)
        if player.rect.x < 0:
          player.rect.x = prev_player_x
      if keys[pygame.K_RIGHT]:
        player.move(player.speed, 0)
        if player.rect.x + player.image.get_width() > self.width:
          player.rect.x = prev_player_x
      if keys[pygame.K_UP]:
        player.move(0, -player.speed)
        if player.rect.y < 0:
          player.rect.y = prev_player_y
      if keys[pygame.K_DOWN]:
        player.move(0, player.speed)
        if player.rect.y + player.image.get_height() > self.height:
          player.rect.y = prev_player_y
      if keys[pygame.K_SPACE] and self.time_now > player.next_bullet_time:
        #bullet = create_bullet(player, player.bullet_delay, game.sprite_groups["bullets"])
        bullet1, bullet2 = create_double_bullet(player, player.double_bullet_delay, self.sprite_groups["bullets"])
        # introduce delay between bullets
        player.next_bullet_time = bullet1.delay + self.time_now

    if keys[pygame.K_END] or keys[pygame.K_ESCAPE]:
      sys.exit(0)

  def increment_animation_delay_counter(self):
    self.animation_delay_counter += 1
    if self.animation_delay_counter == 500:
      self.animation_delay_counter = 1

  def check_player_hp(self, player):
    if player.hp < 1:
      self.lose = True

  def draw_sprites(self):
    for sprite_group in self.sprite_groups:
      self.sprite_groups[sprite_group].draw(self.screen)

  def reset_animate_hit(self):
    for sprite in self.sprite_groups["enemies"]:
      sprite.animate_hit(self)

  def spawn_asteroids(self, rotated_sprites):
    if self.time_now > self.next_asteroid_time:
      x = random.randrange(
            0,
            int(self.width - self.asteroid_img.get_width()))
      asteroid = Asteroid(x,
                          0 - self.asteroid_img.get_height(),
                          self.sprite_groups["asteroids"],
                          rotated_sprites)
      self.next_asteroid_time = self.time_now + random.randrange(2000, 5000)

  def move_asteroids(self, player):
    if self.animation_delay_counter % 2 == 0:
      for asteroid in self.sprite_groups["asteroids"].sprites():
        asteroid.draw(self, player)
        
  def animate_bullets(self):
    """ animate player bullets and check for collisions against enemies """
    for bullet in self.sprite_groups["bullets"].sprites():
      bullet.draw(self)
      
  def animate_enemies(self):
    """ animate enemies and check for collisions against themselves """
    if self.animation_delay_counter % 3 == 0:
      for enemy in self.sprite_groups["enemies"].sprites():
        enemy.draw(self)
              
  def animate_enemy_bullets(self, player):
    """ create enemy bullets, move them, and check for collisions against player """
    for enemy in self.sprite_groups["enemies"].sprites():
      if enemy.shooting and self.time_now > enemy.next_bullet_time:
        enemy_bullet = create_enemy_bullet(enemy, self.sprite_groups["enemy_bullets"])
        self.sprite_groups["enemy_bullets"].add(enemy_bullet)
        enemy.next_bullet_time = self.time_now + enemy_bullet.delay

    for bullet in self.sprite_groups["enemy_bullets"].sprites():
      bullet.draw(self, player)

  def animate_powerups(self, player):
    for power_up in self.sprite_groups["power_ups"]:
      power_up.draw(self, player)
      
  def check_powerup_expiry(self, player):
    if self.time_now > player.speed_power_up_expiry:
      player.speed_power_up_expiry = 0
      player.bullet_delay = 200