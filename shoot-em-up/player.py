import math
import pygame
import random

from utility_functions import load_png, generate_sprite_rotations
from animation import Animation, SpriteData

import pdb

def create_bullet(player, delay, bullet_group):
  bullet_img = pygame.image.load('data/bullet.png')
  return Bullet(player.rect.x + (player.image.get_width() / 2) - (bullet_img.get_width() / 2),
                player.rect.y - bullet_img.get_height(),
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
  def __init__(self, sprite_group, game) -> None:
    pygame.sprite.Sprite.__init__(self, sprite_group)
    self.sprite_file_name = "ship_simple_red_zoomed.png"
    self.image, self.rect = load_png(self.sprite_file_name)
    self.original_image = self.image
    self.mask = pygame.mask.from_surface(self.image)

    # pygame.Rect.(x|y) use int, so we track these as floats
    self.x: float = self.rect.x
    self.y: float = self.rect.y
    # x/y vectors
    self.x_velocity = 0
    self.y_velocity = 0
    self.dx: float = 0
    self.dy: float = 0
    # x/y travel direction
    self.x_dir = 0
    self.y_dir = 0
    # used for slowing the ship to a stop
    self.accel = 0 # px/s^2
    self.accel_rate = 3000
    self.deccel_rate = -1000
    self.left_timer = 0

    self.left_gun_enabled = True
    self.right_gun_enabled = False
    # used as part of bullet delay calculation
    self.next_bullet_time = 0
    self.bullet_delay = 200
    self.double_bullet_delay = 50

    self.speed_power_up_duration = 5000
    self.speed_power_up_expiry = 0
    self.hit_animation_delay = 500
    self.hit_time_expiry = 0

    self.hp = 5

    # create player movement animations with delay of 50ms
    self.left_animation: Animation = Animation(delay=50, direction=1)
    self.right_animation: Animation = Animation(delay=50, direction=1)
    self.moving = False
    self.moved_recently = False

    self.init_player_position(game)
    self.create_sprite_rotations_left()
    self.create_sprite_rotations_right()

  def load_sprite_animations_left(self):
    for file in self.left_animation_files:
      image, rect = load_png(file)
      sprite_info = SpriteData(image, rect)
      self.left_animation.sprites.append(sprite_info)

  def load_sprite_animations_right(self):
    for file in self.right_animation_files:
      image, rect = load_png(file)
      sprite_info = SpriteData(image, rect)
      self.right_animation.sprites.append(sprite_info)

  def init_player_position(self, game):
    self.rect.x = game.width / 2 - self.image.get_width() / 2
    self.rect.y = game.height - self.image.get_height()
    self.x = self.rect.x
    self.y = self.rect.y

  def move(self, game):
    # animate moving left/right
    prev_x = self.rect.x
    prev_y = self.rect.y

    if self.accel > 0:
      if self.x_dir != 0:
        self.x_velocity = self.x_velocity + self.x_dir * self.accel * game.frame_time
      if self.y_dir != 0:
        self.y_velocity = self.y_velocity + self.y_dir * self.accel * game.frame_time
    elif self.accel < 0:
      decel_force = -self.accel * game.frame_time
      if self.x_velocity != 0:
          previous_x_velocity = self.x_velocity
          self.x_velocity -= math.copysign(decel_force, self.x_velocity)
          if math.copysign(1, previous_x_velocity) != math.copysign(1, self.x_velocity) and self.x_velocity != 0:
              self.x_velocity = 0
      if self.y_velocity != 0:
          previous_y_velocity = self.y_velocity
          self.y_velocity -= math.copysign(decel_force, self.y_velocity)
          if math.copysign(1, previous_y_velocity) != math.copysign(1, self.y_velocity) and self.y_velocity != 0:
              self.y_velocity = 0

    self.dx = self.x_velocity * game.frame_time + .5 * self.accel * game.frame_time**2
    self.x += self.dx
    self.rect.x = self.x
    self.dy = self.y_velocity * game.frame_time + .5 * self.accel * game.frame_time**2
    self.y += self.dy
    self.rect.y = self.y

    if self.rect.x < 0 or (self.rect.x + self.image.get_width() > game.width):
      self.rect.x = prev_x
      self.x = prev_x
      self.x_velocity = 0
    if self.rect.y < game.height / 2 or (self.rect.y + self.image.get_height() > game.height):
      self.rect.y = prev_y
      self.y = prev_y
      self.y_velocity = 0
    if self.left_animation.enabled and self.right_animation.count == 0 and game.time_now > self.left_animation.next_frame_time:
      self.left_animation.next_frame_time = game.time_now + self.left_animation.delay
      self.left_animation.update_sprite()
    if self.right_animation.enabled and self.left_animation.count == 0 and game.time_now > self.right_animation.next_frame_time:
      self.right_animation.next_frame_time = game.time_now + self.right_animation.delay
      self.right_animation.update_sprite()

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
    self.left_animation.sprites = \
      generate_sprite_rotations(5.0, 0, 25, self.sprite_file_name)

  def create_sprite_rotations_right(self):
    self.right_animation.sprites = \
      generate_sprite_rotations(-5.0, 360, 335, self.sprite_file_name)
  
class Bullet(pygame.sprite.Sprite):
  def __init__(self, x, y, delay, sprite_group) -> None:
    # adds Bullet sprite to sprite_group
    pygame.sprite.Sprite.__init__(self, sprite_group)
    self.image, self.rect = load_png('player_bullet_concept2.png')
    # create masks, for pixel perfect collision detection
    self.mask = pygame.mask.from_surface(self.image)
    self.rect.centerx = x
    self.rect.y = y
    self.delay = delay
    self.speed = -4
    self.bullet_animation: Animation = Animation(delay=70, direction=1)
    self.bullet_animation_files = [
      "player_bullet_1.png",
      "player_bullet_2.png",
      "player_bullet_3.png",
      "player_bullet_4.png",
      "player_bullet_5.png"]

    self.load_sprite_animations()

  def load_sprite_animations(self):
    for file in self.bullet_animation_files:
      image, rect = load_png(file)
      sprite_info = SpriteData(image, rect)
      self.bullet_animation.sprites.append(sprite_info)

  def move(self, direction, game, player):
    self.rect.y += direction
    if player.speed_power_up_expiry > 0:
      if game.time_now > self.bullet_animation.next_frame_time:
        self.bullet_animation.update_next_frame_time(game)
        self.bullet_animation.update_sprite()
        self.image = self.bullet_animation.image
        # XXX: update mask?

  def draw(self, game, player):
    self.move(self.speed, game, player)
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