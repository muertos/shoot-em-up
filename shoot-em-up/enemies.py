import math
import pygame
import random

from utility_functions import load_png

def create_enemy_bullet(enemy, enemy_bullet_group):
  enemy_bullet_img = pygame.image.load('data/enemy_bullet.png')
  return EnemyBullet(enemy.rect.x + enemy.image.get_width() / 2 - enemy_bullet_img.get_width() / 2,
                     enemy.rect.y + enemy_bullet_img.get_height(),
                     enemy_bullet_group)

class Enemy(pygame.sprite.Sprite):
  def __init__(self, x, y, sprite_group) -> None:
    # adds Enemy sprite to sprite_group
    pygame.sprite.Sprite.__init__(self, sprite_group)
    self.prev_x = None
    self.prev_y = None
    self.x_dir = 0
    self.y_dir = 0
    self.speed = 1
    self.move_count = 0
    self.move_delta = 1
    self.shooting = True
    self.next_bullet_time = 0
    self.hit_animation_delay = 500
    self.hit_time_expiry = 0
    self.hp = 3
    self.collided = False
    self.moves = ["up", "down", "left", "right"]

  def move(self):
    self.rect.x += self.x_dir
    self.rect.y += self.y_dir

  def set_prev_position(self):
    self.prev_x = self.rect.x
    self.prev_y = self.rect.y
  
  def reset_position(self):
    self.rect.x = self.prev_x
    self.rect.y = self.prev_y

  def reset_moves(self):
    self.moves = ["up", "down", "left", "right"]

  def set_move_dir(self):
    if not self.moves:
      self.reset_moves()
      self.move_delta +=1
    if self.moves[0] == "left":
      self.x_dir = -self.move_delta
      self.y_dir = 0
    elif self.moves[0] == "right": 
      self.x_dir = self.move_delta
      self.y_dir = 0
    elif self.moves[0] == "up":
      self.y_dir = -self.move_delta
      self.x_dir = 0
    elif self.moves[0] == "down":
      self.y_dir = self.move_delta
      self.x_dir = 0

  def check_collisions(self, sprite_group):
    collisions = pygame.sprite.spritecollide(
                   self,
                   sprite_group,
                   False,
                   collided=pygame.sprite.collide_mask)
    collisions.remove(self)
    return collisions

  def animate_hit(self, game):
    """ create a blinking effect when hit """
    if game.time_now < self.hit_time_expiry:
      remainder = self.hit_time_expiry - game.time_now
      if remainder % 3 == 0:
        self.image = self.original_image
      else:
        self.image = self.mask.to_surface(setcolor=(0,0,0,0))
    if game.time_now > self.hit_time_expiry:
      self.image = self.original_image

class ArcEnemy(Enemy):
  def __init__(self, x, y, sprite_group) -> None:
    Enemy.__init__(self, x, y, sprite_group)
    self.image, self.rect = load_png('enemy_ship_arc.png')
    self.original_image = self.image
    self.mask = pygame.mask.from_surface(self.image)
    self.rect.x = x
    self.rect.y = y
    self.centerx = None
    self.centery = None
    self.prev_centerx = None
    self.prev_centery = None
    self.prev_angle = None
    self.radius = 50 
    self.angle = 180
    self.arc_dir = 5
    self.radius_inc = 1
    self.hp = 3
    self.set_center()
    self.set_move_dir()

  def set_prev_center(self):
    self.prev_centerx = self.rect.x
    self.prev_centery = self.rect.y
  
  def reset_center(self):
    self.rect.x = self.prev_centerx
    self.rect.y = self.prev_centery

  def set_center(self):
    # we add 180 degrees b/c trig
    angle = math.radians(self.angle + 180)
    self.centery = self.rect.y - (self.radius * math.sin(angle))
    self.centerx = self.rect.x + (self.radius * math.cos(angle))

  def set_angle(self):
    side = abs(self.centery - self.rect.y)
    if self.angle <= 90:
      self.angle = math.degrees(math.asin(side / self.radius))
    if self.angle <= 180 and self.angle > 90:
      self.angle = 180 - math.degrees(math.asin(side / self.radius))
    if self.angle <= 270 and self.angle > 180:
      self.angle = 270 - math.degrees(math.acos(side / self.radius))
    if self.angle <= 360 and self.angle > 270:
      self.angle = 360 - math.degrees(math.acos(side / self.radius))

  def move_center(self):
    self.centerx += self.x_dir
    self.centery += self.y_dir

  def move_arc(self):
    angle = math.radians(self.angle)
    self.angle += self.arc_dir
    if self.radius > 200:
      self.radius_inc = -1
    if self.radius < 1:
      self.radius_inc = 1
    if self.angle < 180 or self.angle > 360:
      self.arc_dir = -self.arc_dir
    # pygame y coordinates increment with down direction
    self.rect.y = self.centery - (math.sin(angle) * self.radius)
    self.rect.x = self.centerx + (math.cos(angle) * self.radius)

  def check_out_of_bounds(self, width, height):
    if self.rect.x + self.image.get_width() > width:
      self.rect.x = width - self.image.get_width()
    if self.rect.x < 0:
      self.rect.x = 1
    if self.rect.y + self.image.get_height() > height:
      self.rect.y = height - self.image.get_height()
    if self.rect.y < 0:
      self.rect.y = 1

  def draw(self, game):
    self.set_prev_position()
    if not self.collided:
      self.prev_angle = self.angle
      self.move_arc()
      collisions = self.check_collisions(game.sprite_groups["enemies"])
      if collisions:
        self.collided = True
        self.reset_position()
        self.angle = self.prev_angle
    elif self.collided:
      self.set_prev_center()
      self.move()
      self.move_center()
      collisions = self.check_collisions(game.sprite_groups["enemies"])
      if collisions:
        self.reset_position()
        self.reset_center()
        # try another move direction
        self.moves.pop(0)
        self.set_move_dir()
      if not collisions:
        self.move_delta = 1
        self.collided = False
    self.check_out_of_bounds(game.width, game.height)    

class DartingEnemy(Enemy):
  def __init__(self, x, y, sprite_group) -> None:
    Enemy.__init__(self, x, y, sprite_group)
    self.image, self.rect = load_png('enemy_ship_dart.png')
    self.mask = pygame.mask.from_surface(self.image)
    self.original_image = self.image
    self.rect.x = x
    self.rect.y = y
    self.accel = 14
  
  def move_dart(self):
    # accelerate in a direction, then pause for a lil bit
    self.rect.x += self.x_dir * self.speed * self.accel
    self.rect.y += self.y_dir * self.speed * self.accel
    if self.accel > 1:
      self.accel -= 1
    self.move_count += 1
    if self.accel < 2 and self.move_count > 15:
      self.accel = 1 
    if self.accel == 1 and self.move_count > 25:
      self.accel = 0
    if self.move_count > 40:
      self.accel = 14
      self.move_count = 0
      self.set_move_direction_random()

  def draw(self, game):
    self.set_prev_position()
    if not self.collided:
      self.move_dart()
      collisions = self.check_collisions(game.sprite_groups["enemies"])
      if collisions:
        self.collided = True
        self.reset_position()
    elif self.collided:
      self.move()
      collisions = self.check_collisions(game.sprite_groups["enemies"])
      if collisions:
        self.reset_position()
        # try another move direction
        self.moves.pop(0)
        self.set_move_dir()
      if not collisions:
        self.collided = False
    self.check_out_of_bounds(game.width, game.height)

  def check_out_of_bounds(self, width, height):
    if self.rect.x + self.image.get_width() > width:
      self.rect.x = width - self.image.get_width()
      self.x_dir = -self.x_dir
    if self.rect.x < 0:
      self.rect.x = 1
      self.x_dir = -self.x_dir
    if self.rect.y + self.image.get_height() > height:
      self.rect.y = height - self.image.get_height()
      self.y_dir = -self.y_dir
    if self.rect.y < 0:
      self.rect.y = 1
      self.y_dir = -self.y_dir
  
  #def set_move_dir(self):
  #  if self.x_dir > 0:
  #    self.x_dir = -self.x_dir
  #  if self.y_dir > 0:
  #    self.y_dir = -self.y_dir

  def set_move_direction_random(self):
    choice = random.randrange(0,8)
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
    if choice == 6:
      self.x_dir = -1
      self.y_dir = 1
    if choice == 7:
      self.x_dir = 1
      self.y_dir = -1

class EnemyBullet(pygame.sprite.Sprite):
  def __init__(self, x, y, sprite_group) -> None:
    # adds Enemy bullet sprite to sprite_group
    pygame.sprite.Sprite.__init__(self, sprite_group)
    self.image, self.rect = load_png('enemy_bullet.png')
    self.rect.x = x
    self.rect.y = y
    self.speed = 1.5
    self.delay = random.randrange(2500,3500)

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
      game.sprite_groups["enemy_bullets"].remove(self)
      player.hp -= 1