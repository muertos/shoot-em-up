import pygame
import random

from utility_functions import load_png

def create_player(group, game):
  player_img = pygame.image.load('data/ship.png')
  return Player((game.width / 2) - (player_img.get_width() / 2),
                 game.height - player_img.get_height(),
                 group)

def create_bullet(player, delay, bullet_group):
  bullet_img = pygame.image.load('data/bullet.png')
  return Bullet(player.rect.x + (player.image.get_width() / 2) - (bullet_img.get_width() / 2),
                player.rect.y,
                delay,
                bullet_group)

def create_double_bullet(player, delay, bullet_group):
  bullet_img = pygame.image.load('data/bullet.png')
  return (Bullet(player.rect.x - (bullet_img.get_width() / 2),
                player.rect.y,
                delay,
                bullet_group),
         Bullet(player.rect.x + (player.image.get_width()) - (bullet_img.get_width() / 2),
                player.rect.y,
                delay,
                bullet_group))

class Player(pygame.sprite.Sprite):
  def __init__(self, x, y, sprite_group) -> None:
    pygame.sprite.Sprite.__init__(self, sprite_group)
    self.image, self.rect = load_png('ship.png')
    self.mask = pygame.mask.from_surface(self.image)
    self.rect.x = x
    self.rect.y = y
    self.x_direction = 0
    self.y_direction = 0
    self.speed = 3
    self.original_speed = self.speed
    # used for slowing the ship to a stop
    self.accel = -5
    # time ship takes to come to a stop in ms
    self.accel_duration = 1000
    # time in the future to stop acceleration
    self.accel_stop_time = None
    self.accelerating = False
    # used as part of bullet delay calculation
    self.next_bullet_time = 0
    self.bullet_delay = 200
    self.double_bullet_delay = 50
    self.speed_power_up_duration = 5000
    self.speed_power_up_expiry = 0
    self.hp = 5

  def move(self, game):
    prev_x = self.rect.x
    prev_y = self.rect.y
    self.rect.x += self.x_direction * self.speed
    self.rect.y += self.y_direction * self.speed
    if self.rect.x < 0:
      self.rect.x = prev_x
    if self.rect.x + self.image.get_width() > game.width:
      self.rect.x = prev_x
    if self.rect.y < 0:
      self.rect.y = prev_y
    if self.rect.y + self.image.get_height() > game.height:
      self.rect.y = prev_y

  def update_speed(self, game):
    #if game.time_now < self.accel_stop_time:
    if self.speed > 0:
      frame_time = game.time_now - game.prev_time
      self.speed = self.speed + self.accel * frame_time/1000
    else:
      self.accelerating = False
      self.speed = self.original_speed
      self.x_direction = 0
      self.y_direction = 0

  def draw_hp(self, game):
    for i in range(0, self.hp):
      game.screen.blit(
        game.draw_text(
          "*",
          (0,200,0), 50),
          (i*15, game.height - 20))

class Bullet(pygame.sprite.Sprite):
  def __init__(self, x, y, delay, sprite_group) -> None:
    # adds Bullet sprite to sprite_group
    pygame.sprite.Sprite.__init__(self, sprite_group)
    self.image, self.rect = load_png('bullet.png')
    # create masks, for pixel perfect collision detection
    self.mask = pygame.mask.from_surface(self.image)
    self.rect.x = x
    self.rect.y = y
    self.delay = delay
    self.speed = -8

  def move(self, direction):
    self.rect.y += direction

  def draw(self, game):
    self.move(self.speed)
    collisions = pygame.sprite.spritecollide(
                   self,
                   game.sprite_groups["enemies"],
                   False,
                   collided=pygame.sprite.collide_mask)
    for enemy in collisions:
      enemy.hit_time_expiry = game.time_now + enemy.hit_animation_delay
      enemy.hp -= 1
      game.sprite_groups["bullets"].remove(self)
      if enemy.hp == 0:
        # 1 in 10 chance to spawn power up
        if random.random() < 0.1:
          power_up = SpeedPowerUp(
                       enemy.rect.x,
                       enemy.rect.y,
                       game.sprite_groups["power_ups"])
        game.sprite_groups["enemies"].remove(enemy)
      if not game.sprite_groups["enemies"]:
        game.win = True
      if self.rect.y < 0:
        game.sprite_groups["bullets"].remove(self)

class SpeedPowerUp(pygame.sprite.Sprite):
  def __init__(self, x, y, sprite_group) -> None:
    pygame.sprite.Sprite.__init__(self, sprite_group)
    self.image, self.rect = load_png('speed_power_up.png')
    self.mask = pygame.mask.from_surface(self.image)
    self.rect.x = x
    self.rect.y = y
    self.speed = 1

  def move(self, direction):
    self.rect.y += direction

  def draw(self, game, player):
    self.move(self.speed)
    collisions = pygame.sprite.spritecollide(
                     self,
                     game.sprite_groups["player"],
                     False,
                     collided=pygame.sprite.collide_mask)
    if collisions:
      game.sprite_groups["power_ups"].remove(self)
      player.bullet_delay = 50
      player.speed_power_up_expiry = game.time_now + player.speed_power_up_duration
    if self.rect.y > game.height:
      game.sprite_groups["power_ups"].remove(self)