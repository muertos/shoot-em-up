import pygame
import random

from utility_functions import load_png, generate_sprite_rotations

import pdb

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
  bullet_img = pygame.image.load('data/player_bullet_1.png')
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
    self.original_image = self.image
    self.mask = pygame.mask.from_surface(self.image)
    self.rect.x = x
    self.rect.y = y
    self.x_direction = 0
    self.y_direction = 0
    self.speed = 3
    self.original_speed = self.speed
    # used for slowing the ship to a stop
    self.accel = -5
    self.accelerating = False
    self.moved_recently = False
    # used as part of bullet delay calculation
    self.next_bullet_time = 0
    self.bullet_delay = 200
    self.double_bullet_delay = 50
    self.speed_power_up_duration = 5000
    self.speed_power_up_expiry = 0
    self.hit_animation_delay = 500
    self.hit_time_expiry = 0
    self.hp = 5
    self.left_animation = {
      "sprites": [],
      "count": 0,
      "direction": 1,
      "delay": 50,
      "next_frame_time": 0,
      "enabled": False,
      "key_down": False
      }
    self.right_animation = {
      "sprites": [],
      "count": 0,
      "direction": 1,
      "delay": 50,
      "next_frame_time": 0,
      "enabled": False,
      "key_down": False
      }
    self.create_sprite_rotations_left()
    self.create_sprite_rotations_right()

  def move(self, game):
    prev_x = self.rect.x
    prev_y = self.rect.y
    self.rect.x += self.x_direction * self.speed
    self.rect.y += self.y_direction * self.speed
    if self.rect.x < 0:
      self.rect.x = prev_x
    if self.rect.x + self.image.get_width() > game.width:
      self.rect.x = prev_x
    if self.rect.y < game.height / 2:
      self.rect.y = prev_y
    if self.rect.y + self.image.get_height() > game.height:
      self.rect.y = prev_y
    if self.left_animation["enabled"] and self.right_animation["count"] == 0 and game.time_now > self.left_animation["next_frame_time"]:
      self.left_animation["next_frame_time"] = game.time_now + self.left_animation["delay"]
      self.next_sprite(self.left_animation)
    if self.right_animation["enabled"] and self.left_animation["count"] == 0 and game.time_now > self.right_animation["next_frame_time"]:
      self.right_animation["next_frame_time"] = game.time_now + self.right_animation["delay"]
      self.next_sprite(self.right_animation)

  def reset(self):
    self.accelerating = False
    self.x_direction = 0
    self.y_direction = 0
    self.speed = self.original_speed

  def check_update_speed(self, game):
    """ adjusts player speed if accelerating """
    if self.accelerating:
      if self.speed > 0:
        frame_time = game.time_now - game.prev_time
        self.speed = self.speed + self.accel * frame_time/1000
      else:
        self.reset()

  def draw_hp(self, game):
    for i in range(0, self.hp):
      game.screen.blit(
        game.draw_text(
          "*",
          (0,200,0), 50),
          (i*15, game.height - 20))

  def blink_when_hit(self, game):
    """ create a blinking effect when hit """
    if game.time_now < self.hit_time_expiry:
      remainder = self.hit_time_expiry - game.time_now
      if remainder % 3 == 0:
        self.image = self.original_image
      else:
        self.image = self.mask.to_surface(setcolor=(0,0,0,0))
    if game.time_now > self.hit_time_expiry:
      self.image = self.original_image

  def create_sprite_rotations_left(self):
    self.left_animation["sprites"] = \
      generate_sprite_rotations(5.0, 0, 25, 'ship.png')

  def create_sprite_rotations_right(self):
    self.right_animation["sprites"] = \
      generate_sprite_rotations(-5.0, 360, 335, 'ship.png')
  
  def next_sprite(self, animation):
    x = self.rect.centerx
    y = self.rect.centery
    self.image = animation["sprites"][animation["count"]]["image"]
    self.rect = animation["sprites"][animation["count"]]["rect"]
    self.mask = pygame.mask.from_surface(self.image)
    self.rect.centerx = x
    self.rect.centery = y
    animation["count"] += animation["direction"]
    if animation["count"] == len(animation["sprites"]) - 1:
      if not animation["key_down"]:
        animation["direction"] = -1
      else:
        animation["direction"] = 0
    if animation["count"] == -1 and animation["direction"] == -1:
      animation["enabled"] = False
      animation["direction"] = 1
      animation["count"] = 0
      self.image = self.original_image

class Bullet(pygame.sprite.Sprite):
  def __init__(self, x, y, delay, sprite_group) -> None:
    # adds Bullet sprite to sprite_group
    pygame.sprite.Sprite.__init__(self, sprite_group)
    self.image, self.rect = load_png('player_bullet_1.png')
    # create masks, for pixel perfect collision detection
    self.mask = pygame.mask.from_surface(self.image)
    self.rect.centerx = x
    self.rect.y = y
    self.delay = delay
    self.speed = -8
    self.bullet_animation_data = {
      "images": ["player_bullet_1.png", "player_bullet_2.png", "player_bullet_3.png","player_bullet_4.png", "player_bullet_5.png"],
      "delay": 70,
      "next_animation_time": 0,
      "count": 0
    }

  def move(self, direction, game):
    self.rect.y += direction
    if game.time_now > self.bullet_animation_data["next_animation_time"]:
      self.bullet_animation_data["next_animation_time"] = self.bullet_animation_data["delay"] + game.time_now
      self.image, rect = load_png(self.bullet_animation_data["images"][self.bullet_animation_data["count"]])
      self.bullet_animation_data["count"] += 1
      if self.bullet_animation_data["count"] == len(self.bullet_animation_data["images"]):
        self.bullet_animation_data["count"] = 0

  def draw(self, game):
    self.move(self.speed, game)
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