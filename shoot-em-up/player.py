import math
import pygame
import random

from utility_functions import load_png, generate_sprite_rotations
from animation import Animation, SpriteData

import pdb

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
  def __init__(self, sprite_group, game) -> None:
    pygame.sprite.Sprite.__init__(self, sprite_group)
    self.sprite_file_name = "ship_concept_5.png"
    self.image, self.rect = load_png(self.sprite_file_name)
    self.original_image = self.image
    self.mask = pygame.mask.from_surface(self.image)
    # pygame.Rect.(x|y) use int, so we track these as floats
    self.centerx: float = self.rect.centerx
    self.centery: float = self.rect.centery
    self.speed = 3
    self.original_speed = self.speed
    self.delta_x: float = 0
    self.delta_y: float = 0
    # used for slowing the ship to a stop
    self.accel = -.02
    self.accelerating = False
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
    self.create_sprite_rotations_left()
    self.create_sprite_rotations_right()
    self.moving = False

    self.init_player_position(game)

  def init_player_position(self, game):
    self.rect.x = game.width / 2 - self.image.get_width() / 2
    self.rect.y = game.height - self.image.get_height()
    self.centerx = self.rect.centerx
    self.centery = self.rect.centery

  def calculate_stop_distance(self):
    time_to_stop = (0 - self.original_speed) / self.accel
    velocity_avg = self.speed / 2
    distance = (velocity_avg * time_to_stop) 
    return distance

  def move(self, game):
    # move to where mouse clicked
    if abs(self.delta_x) > 0:
      self.centerx += self.delta_x
      self.rect.centerx = int(round(self.centerx, 0))
      # a window of 2 pixels seems best here
      if abs(self.rect.centerx - game.mouse_x) < 2:
        self.delta_x = 0
    if abs(self.delta_y) > 0:
      self.centery += self.delta_y
      self.rect.centery = int(round(self.centery, 0))
      if abs(self.rect.centery - game.mouse_y) < 2:
        self.delta_y = 0

    if self.delta_x == 0 and self.delta_y == 0:
      self.reset()

    # check to see if player should start accelerating
    if not self.accelerating:
      a = self.centerx - game.mouse_x
      b = self.centery - game.mouse_y
      c = math.sqrt(a**2 + b**2)
      stop_dist = self.calculate_stop_distance()
      if c <= stop_dist and self.moving:
        self.accelerating = True

    # boundary collision checking
    if self.rect.x < 0:
      self.rect.x = 0
      self.centerx = self.rect.centerx
    if self.rect.x + self.image.get_width() > game.width:
      self.rect.x = game.width - self.image.get_width()
      self.centerx = self.rect.centerx
    if self.rect.y < game.height / 2:
      self.rect.y = game.height / 2
      self.centery = self.rect.centery
    if self.rect.y + self.image.get_height() > game.height:
      self.rect.y = game.height - self.image.get_height()
      self.centery = self.rect.centery

    # animate moving left/right
    if self.left_animation.enabled and self.right_animation.count == 0 and game.time_now > self.left_animation.next_frame_time:
      self.left_animation.update_next_frame_time(game)
      self.next_sprite(self.left_animation)
    if self.right_animation.enabled and self.left_animation.count == 0 and game.time_now > self.right_animation.next_frame_time:
      self.right_animation.update_next_frame_time(game)
      self.next_sprite(self.right_animation)

  def reset(self):
    self.accelerating = False
    self.delta_x = 0
    self.delta_y = 0
    self.speed = self.original_speed
    self.moving = False

  def calculate_speed(self, game):
    """ adjusts player speed if accelerating """
    if self.accelerating:
      if self.speed > 0:
        frame_time = game.time_now - game.prev_time
        self.speed = self.speed + self.accel
        self.update_velocity_vector(self.delta_x, self.delta_y, game.angle)
      else:
        self.reset()

  def update_velocity_vector(self, a, b, angle):
    delta_y = -(self.speed * math.sin(math.radians(angle)))
    delta_x = self.speed * math.cos(math.radians(angle))
    self.delta_x = delta_x
    self.delta_y = delta_y

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
  
  def next_sprite(self, animation):
    x = self.rect.centerx
    y = self.rect.centery
    self.image = animation.sprites[animation.count].image
    self.rect = animation.sprites[animation.count].rect
    self.mask = pygame.mask.from_surface(self.image)
    self.rect.centerx = x
    self.rect.centery = y
    animation.count += animation.direction
    if animation.count == len(animation.sprites) - 1:
      if not animation.key_down:
        animation.direction = -1
      else:
        animation.direction = 0
    if animation.count == -1 and animation.direction == -1:
      animation.enabled = False
      animation.direction = 1
      animation.count = 0
      self.image = self.original_image

class Bullet(pygame.sprite.Sprite):
  def __init__(self, x, y, delay, sprite_group) -> None:
    # adds Bullet sprite to sprite_group
    pygame.sprite.Sprite.__init__(self, sprite_group)
    self.image, self.rect = load_png('bullet.png')
    # create masks, for pixel perfect collision detection
    self.mask = pygame.mask.from_surface(self.image)
    self.rect.centerx = x
    self.rect.y = y
    self.delay = delay
    self.speed = -8
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