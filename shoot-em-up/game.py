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
    self.prev_time = None
    self.time_now = pygame.time.get_ticks()
    self.enemy_offset_y = None
    self.intro_enemies = True
    self.running = True
    self.mouse_x = 0
    self.mouse_y = 0
    self.angle = 0

    self.enemy_level = [
      [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
      [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
      [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
      [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
      [0,2,0,0,0,1,0,0,0,1,0,0,0,1,0,0,0,1,0,0,0,1,0,0,0,2,0],
      [0,0,0,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,0,0,0],
      [0,0,0,0,0,1,0,0,0,1,0,0,0,1,0,0,0,1,0,0,0,1,0,0,0,0,0]
    ]

    self.enemy_level = [
      [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
      [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
      [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
      [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
      [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
      [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
      [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
      [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
      [0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0]]

    self.sprite_groups = {
      "bullets": pygame.sprite.Group(),
      "enemies": pygame.sprite.Group(),
      "enemy_bullets": pygame.sprite.Group(),
      "player": pygame.sprite.Group(),
      "asteroids": pygame.sprite.Group(),
      "power_ups": pygame.sprite.Group(),
      "stars": pygame.sprite.Group()
    }

    self.screen.blit(self.background, (0,0))
    self.make_level(self.sprite_groups["enemies"])
    pygame.init()
    self.intro()
    self.calculate_enemy_offscreen_offset_y()
    self.set_y_offset_enemies()

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
        self.draw_text("use left click to move, space to shoot, press enter to play"),
                       (350, self.height / 2 - 30))
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

  def determine_angle(self, x, y):
    try:
      # quadrant 1
      angle = math.degrees(math.atan(abs(y) / x))
    except ZeroDivisionError:
      if y > 0:
        angle = 90
      else:
        angle = 270.0
    # quadrant 2
    if x < 0 and y < 0:
      angle = 180 - abs(angle)
    # quadrant 3
    if x < 0 and y > 0:
      angle = 180 + abs(angle)
    # quadrant 4
    if x > 0 and y > 0:
      angle = 360 - abs(angle)
    return angle

  def handle_input(self, player):
    for event in pygame.event.get():
      keys = pygame.key.get_pressed()
      if event.type == QUIT:
        return
      
      # mouse input
      mouse_input = pygame.mouse.get_pressed()
      if event.type == MOUSEBUTTONDOWN:
        # left button
        if mouse_input[0]:
          player.reset()
          player.moving = True
          self.mouse_x, self.mouse_y = pygame.mouse.get_pos()
          x = self.mouse_x - player.rect.centerx
          y = self.mouse_y - player.rect.centery
          self.angle = self.determine_angle(x, y)
          player.update_velocity_vector(x, y, self.angle)
          if player.delta_x < 0:
            player.left_animation.enabled = True
            player.left_animation.is_pressed = True
          elif player.delta_x > 0:
            player.right_animation.enabled = True
            player.right_animation.is_pressed = True
      if event.type == MOUSEBUTTONUP:
        player.right_animation.is_pressed = False
        player.left_animation.is_pressed = False
          
    # handle most keypresses outside of event loop
    keys = pygame.key.get_pressed()
    if not self.lose:
      if not self.intro_enemies and keys[pygame.K_SPACE] and self.time_now > player.next_bullet_time:
        if player.speed_power_up_expiry == 0:
          bullet = create_bullet(player, player.bullet_delay, self.sprite_groups["bullets"])
          if player.left_gun_enabled:
            bullet.rect.x = player.rect.x + player.left_gun_x_offset
            player.left_gun_enabled = False
            player.right_gun_enabled = True
          elif player.right_gun_enabled:
            bullet.rect.x = player.rect.x + player.right_gun_x_offset
            player.right_gun_enabled = False
            player.left_gun_enabled = True
        else:
          bullet, bullet2 = create_double_bullet(player, player.double_bullet_delay, self.sprite_groups["bullets"])
        # introduce delay between bullets
        player.next_bullet_time = bullet.delay + self.time_now
    if keys[pygame.K_END] or keys[pygame.K_ESCAPE]:
      sys.exit(0)
      
  def increment_animation_delay_counter(self):
    self.animation_delay_counter += 1
    if self.animation_delay_counter == 500:
      self.animation_delay_counter = 1

  def check_player_hp(self, player):
    if player.hp < 1:
      self.lose = True

  def calculate_enemy_offscreen_offset_y(self):
    """ sets offscreen enemy position """
    max_y = 0
    for enemy in self.sprite_groups["enemies"]:
      if enemy.rect.y > max_y:
        max_y = enemy.rect.y
        enemy_height = enemy.rect.height
    self.enemy_offset_y = max_y + enemy_height

  def set_y_offset_enemies(self):
    for enemy in self.sprite_groups["enemies"]:
      enemy.prev_y = enemy.rect.y
      enemy.rect.y -= self.enemy_offset_y
      enemy.y_dir = 1

  def animate_enemies_intro(self):
    for enemy in self.sprite_groups["enemies"]:
      enemy.move()
      if enemy.rect.y > enemy.prev_y:
        enemy.rect.y = enemy.prev_y
        self.intro_enemies = False

  def draw_sprites(self):
    for sprite_group in self.sprite_groups:
      self.sprite_groups[sprite_group].draw(self.screen)

  def enemy_blink_when_hit(self):
    for sprite in self.sprite_groups["enemies"]:
      sprite.blink_when_hit(self)

  def spawn_asteroids(self):
    if self.time_now > self.next_asteroid_time:
      if random.random() > .5:
        spin_direction = 1
      else:
        spin_direction = -1
      animation_delay = random.randrange(10, 50)
      x = random.randrange(
        0,
        int(self.width - self.asteroid_img.get_width()))
      asteroid = Asteroid(
        x,
        0 - self.asteroid_img.get_height(),
        animation_delay,
        spin_direction,
        self.sprite_groups["asteroids"])
      self.next_asteroid_time = self.time_now + random.randrange(2000, 5000)

  def move_asteroids(self, player):
    for asteroid in self.sprite_groups["asteroids"].sprites():
      asteroid.draw(self, player)
        
  def animate_bullets(self, player):
    """ animate player bullets and check for collisions against enemies """
    for bullet in self.sprite_groups["bullets"].sprites():
      bullet.draw(self, player)
      
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
        if type(enemy) is DartingEnemy:
          enemy_bullet.speed = 5
          enemy_bullet.delay = 300
          delta_x = player.rect.centerx - enemy.rect.x
          delta_y = player.rect.centery - enemy.rect.y
          angle = self.determine_angle(delta_x, delta_y)
          enemy_bullet.delta_y = -(enemy_bullet.speed * math.sin(math.radians(angle)))
          enemy_bullet.delta_x = enemy_bullet.speed * math.cos(math.radians(angle))
        enemy.next_bullet_time = self.time_now + enemy_bullet.delay
        self.sprite_groups["enemy_bullets"].add(enemy_bullet)

    for bullet in self.sprite_groups["enemy_bullets"].sprites():
      bullet.draw(self, player)

  def animate_powerups(self, player):
    for power_up in self.sprite_groups["power_ups"]:
      power_up.draw(self, player)
      
  def check_powerup_expiry(self, player):
    if self.time_now > player.speed_power_up_expiry:
      player.speed_power_up_expiry = 0
      player.bullet_delay = 200