import pygame, random, sys, os, math
from pygame.locals import *

def load_png(name):
  """ load image and return image object """
  fullname = os.path.join('data', name)
  try:
    image = pygame.image.load(fullname)
    if image.get_alpha is None:
      image = image.convert()
    else:
      image = image.convert_alpha()
  except pygame.error as message:
    print('Cannot load image:', fullname)
    raise SystemExit(message)
  return image, image.get_rect()

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

def create_enemy_bullet(enemy, enemy_bullet_group):
  enemy_bullet_img = pygame.image.load('data/enemy_bullet.png')
  return EnemyBullet(enemy.rect.x + enemy.image.get_width() / 2 - enemy_bullet_img.get_width() / 2,
                     enemy.rect.y + enemy_bullet_img.get_height(),
                     enemy_bullet_group)

def generate_sprite_rotations(angle, image):
  # rotate a sprite 360 degrees, return list of rotated sprites
  image, orig_rect = load_png(image)
  rotated_sprites = []
  current_angle = 0.0
  for loop in range(0, int(360.0 / angle)):
    current_angle = current_angle + angle
    rotated_img = pygame.transform.rotate(image, current_angle)
    rotated_rect = rotated_img.get_rect(center=orig_rect.center)
    rotated_sprites.append((rotated_img, rotated_rect))
  return rotated_sprites

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
    self.speed_power_up_duration = 5000
    self.speed_power_up_expiry = 0
    self.hp = 5

  def move(self, direction):
    self.rect.x += direction

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

class Enemy(pygame.sprite.Sprite):
  def __init__(self, x, y, angle, radius, arc_dir, sprite_group) -> None:
    # adds Enemy sprite to sprite_group
    pygame.sprite.Sprite.__init__(self, sprite_group)
    self.image, self.rect = load_png('enemy_ship.png')
    self.mask = pygame.mask.from_surface(self.image)
    self.rect.x = x
    self.rect.y = y
    self.old_x = 0
    self.old_y = 0
    self.x_dir = 0
    self.y_dir = 0
    self.speed = 1
    self.move_count = 0
    self.shooting = True
    self.next_bullet_time = 0
    self.hp = 3
    self.radius = radius 
    self.angle = angle
    self.arc_dir = arc_dir
    self.centerx = self.rect.x + self.radius * math.sin(self.angle)
    self.centery = self.rect.y - self.radius * math.cos(self.angle)
    self.radius_inc = 1
    self.collided = False
    self.movement_style = "random"
    self.movement_timer = 5000

  def move_back_and_forth(self):
    self.rect.x += self.speed
    self.move_count +=1
    if self.move_count > 80:
      self.speed = -self.speed
      self.move_count = 0

  def move(self):
    self.rect.x += self.x_dir
    self.rect.y += self.y_dir

  def set_move_direction(self):
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

  def move_random(self):
    self.move()
    self.move_count += 1
    if self.move_count > 12:
      self.set_move_direction()
      self.move_count = 0

  def reverse_direction(self):
    self.x_dir = -self.x_dir
    self.y_dir = -self.y_dir

  def move_arc(self):
    angle = math.radians(self.angle)
    self.rect.x = self.centerx + (math.sin(angle) * self.radius)
    self.rect.y = self.centery + (math.cos(angle) * self.radius)
    self.angle += self.arc_dir
    self.radius += self.radius_inc
    if self.radius > 200:
      self.radius_inc = -1
    if self.radius < 1:
      self.radius_inc = 1
    #if self.angle > 420:
    #  self.arc_dir = -5
    #if self.angle < 300:
    #  self.arc_dir = 5

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

class Asteroid(pygame.sprite.Sprite):
  def __init__(self, x, y, sprite_group, rotated_sprites) -> None:
    pygame.sprite.Sprite.__init__(self, sprite_group)
    self.image, self.rect = load_png('asteroid.png')
    #self.orig_rect = self.rect
    #self.orig_image = self.image
    self.mask = pygame.mask.from_surface(self.image)
    self.centerx = x
    self.centery = y
    self.speed = 1
    # pre-load sprite rotations to not make the cpu work so hard
    self.rotated_sprites = rotated_sprites
    self.rotation_counter = 0

  def move(self):
    self.centery += self.speed

  def next_sprite(self):
    # update mask?
    if self.rotation_counter == len(self.rotated_sprites):
      self.rotation_counter = 0
    self.image = self.rotated_sprites[self.rotation_counter][0]
    self.rect = self.rotated_sprites[self.rotation_counter][1]
    self.mask = pygame.mask.from_surface(self.image)
    self.rect.centerx = self.centerx
    self.rect.centery = self.centery