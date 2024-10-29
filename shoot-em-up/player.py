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
    self.speed = 5
    # used as part of bullet delay calculation
    self.next_bullet_time = 0
    self.bullet_delay = 200
    self.double_bullet_delay = 50
    self.speed_power_up_duration = 5000
    self.speed_power_up_expiry = 0
    self.hp = 5

  def move(self, x_direction, y_direction):
    self.rect.x += x_direction
    self.rect.y += y_direction

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