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
    self.sprite_file_name = "ship5.png"
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
    # gun offsets
    self.left_gun_x_offset = 3
    self.right_gun_x_offset = 48
    self.left_gun_offsets = [
      (3,48),
      (5,45),
      (6,42),
      (7,39),
      (10,36),
      (14,34)
    ]
    self.right_gun_offsets = [
      (3,48),
      (5,47),
      (9,45),
      (12,43),
      (16,40),
      (18,38)
    ]
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
    self.right_animation_files = [
      "ship5_right1.png",
      "ship5_right2.png",
      "ship5_right3.png",
      "ship5_right4.png",
      "ship5_right5.png",
      "ship5_right6.png"
    ]
    self.left_animation_files = [
      "ship5_left1.png",
      "ship5_left2.png",
      "ship5_left3.png",
      "ship5_left4.png",
      "ship5_left5.png",
      "ship5_left6.png"
    ]
    self.moving = False

    self.init_player_position(game)
    self.load_sprite_animations_left()
    self.load_sprite_animations_right()

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
    self.centerx = self.rect.centerx
    self.centery = self.rect.centery

  def calculate_stop_distance(self):
    time_to_stop = (0 - self.original_speed) / self.accel
    velocity_avg = self.speed / 2
    distance = (velocity_avg * time_to_stop) 
    return distance

  def move(self, game):
    # animate moving left/right
    if self.left_animation.enabled and game.time_now > self.left_animation.next_frame_time:
      self.left_animation.update_next_frame_time(game)
      # hold player position at last animation frame if input being received, otherwise cycle back through animation stack
      if self.left_animation.count == len(self.left_animation.sprites) - 1:
        self.left_animation.hold_last_frame_or_reverse()
      self.left_animation.update_sprite()
      self.image = self.left_animation.image
      if self.left_animation.count == 0:
        self.left_animation.enabled = False
        self.image = self.original_image
      self.left_gun_x_offset, self.right_gun_x_offset = self.left_gun_offsets[self.left_animation.count]
    if self.right_animation.enabled and game.time_now > self.right_animation.next_frame_time:
      self.right_animation.update_next_frame_time(game)
      if self.right_animation.count == len(self.right_animation.sprites) - 1:
        self.right_animation.hold_last_frame_or_reverse()
      self.right_animation.update_sprite()
      self.image = self.right_animation.image
      if self.right_animation.count == 0:
        self.right_animation.enabled = False
        self.image = self.original_image
      self.left_gun_x_offset, self.right_gun_x_offset = self.right_gun_offsets[self.right_animation.count]

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