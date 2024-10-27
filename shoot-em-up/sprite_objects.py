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

class ArcEnemy(Enemy):
  def __init__(self, x, y, sprite_group) -> None:
    Enemy.__init__(self, x, y, sprite_group)
    self.image, self.rect = load_png('enemy_ship_arc.png')
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

class Asteroid(pygame.sprite.Sprite):
  def __init__(self, x, y, sprite_group, rotated_sprites) -> None:
    pygame.sprite.Sprite.__init__(self, sprite_group)
    self.image, self.rect = load_png('asteroid.png')
    self.mask = pygame.mask.from_surface(self.image)
    self.centerx = x
    self.centery = y
    self.speed = 1
    # pre-load sprite rotations to not make the cpu work so hard
    self.rotated_sprites = rotated_sprites
    self.rotation_counter = 0
    self.collided = False

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