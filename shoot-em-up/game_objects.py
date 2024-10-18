import pygame, random, sys, os, math
from sprite_objects import *
from pygame.locals import *
import pdb

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
    self.time_now = pygame.time.get_ticks()

    self.enemy_level = [
      [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
      [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
      [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
      [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
      [0,0,0,0,1,0,0,0,1,0,0,0,1,0,0,0],
      [1,0,0,0,0,0,1,0,0,0,0,1,0,0,1,0],
      [1,0,0,0,0,0,0,0,0,0,0,1,0,0,0,1],
      [0,1,0,0,0,0,0,0,0,0,1,0,1,0,1,0]]

    self.enemy_test_level = [
      [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
      [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
      [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
      [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
      [0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0]
    ]

    self.sprite_groups = {
      "bullets": pygame.sprite.Group(),
      "enemies": pygame.sprite.Group(),
      "enemy_bullets": pygame.sprite.Group(),
      "player": pygame.sprite.Group(),
      "asteroids": pygame.sprite.Group(),
      "power_ups": pygame.sprite.Group()
    }

    self.screen.blit(self.background, (0,0))
    #self.make_level(self.sprite_groups["enemies"])
    self.make_test_level(self.sprite_groups["enemies"])
    pygame.init()
    self.intro()

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
    img = pygame.image.load('data/enemy_ship.png')
    """ create sprite group of enemies at coordinates specified by matrix """  
    for i in range(len(self.enemy_level)):
      for j in range(len(self.enemy_level[i])):
        if self.enemy_level[i][j] == 1:
          angle = 270
          radius = 50 + random.randint(0, 20)
          arc_dir = 5
          if random.random() > .5:
            arc_dir = -5
          enemy = Enemy(((img.get_width() + 12) * j),
                       ((img.get_height() + 12) * i),
                       angle,
                       radius,
                       arc_dir,
                       sprites)
          sprites.add(enemy)

  def make_test_level(self, sprites):
    # initialize width / height
    img = pygame.image.load('data/enemy_ship.png')
    """ create sprite group of enemies at coordinates specified by matrix """  
    c = 0
    for i in range(len(self.enemy_test_level)):
      for j in range(len(self.enemy_test_level[i])):
        if self.enemy_test_level[i][j] == 1:
          c += 1
          angle = 270
          radius = 60
          arc_dir = 5
          if c == 2:
            arc_dir = -5
            angle = 135
          enemy = Enemy(((img.get_width() + 12) * j),
                       ((img.get_height() + 12) * i),
                       angle,
                       radius,
                       arc_dir,
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
        self.draw_text("arrow keys to move, space to shoot, press enter to play"),
                       (150, self.height / 2 - 30))
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

  def handle_input(self, player):
    for event in pygame.event.get():
      if event.type == QUIT:
        return

    keys = pygame.key.get_pressed()
    old_player_x = player.rect.x
    old_player_y = player.rect.y

    if not self.lose:
      if keys[pygame.K_LEFT]:
        player.move(-player.speed, 0)
        if player.rect.x < 0:
          player.rect.x = old_player_x
      if keys[pygame.K_RIGHT]:
        player.move(player.speed, 0)
        if player.rect.x + player.image.get_width() > self.width:
          player.rect.x = old_player_x
      if keys[pygame.K_UP]:
        player.move(0, -player.speed)
        if player.rect.y < 0:
          player.rect.y = old_player_y
      if keys[pygame.K_DOWN]:
        player.move(0, player.speed)
        if player.rect.y + player.image.get_height() > self.height:
          player.rect.y = old_player_y
      if keys[pygame.K_SPACE] and self.time_now > player.next_bullet_time:
        #bullet = create_bullet(player, player.bullet_delay, game.sprite_groups["bullets"])
        bullet1, bullet2 = create_double_bullet(player, player.double_bullet_delay, self.sprite_groups["bullets"])
        # introduce delay between bullets
        player.next_bullet_time = bullet1.delay + self.time_now

    if keys[pygame.K_END] or keys[pygame.K_ESCAPE]:
      sys.exit(0)

  def increment_animation_delay_counter(self):
    self.animation_delay_counter += 1
    if self.animation_delay_counter == 500:
      self.animation_delay_counter = 1

  def check_player_hp(self, player):
    if player.hp < 1:
      self.lose = True

  def draw_sprites(self):
    for sprite_group in self.sprite_groups:
      self.sprite_groups[sprite_group].draw(self.screen)

  def spawn_asteroids(self, rotated_sprites):
    if self.time_now > self.next_asteroid_time:
      x = random.randrange(
            0,
            int(self.width - self.asteroid_img.get_width()))
      asteroid = Asteroid(x,
                          0 - self.asteroid_img.get_height(),
                          self.sprite_groups["asteroids"],
                          rotated_sprites)
      self.next_asteroid_time = self.time_now + random.randrange(2000, 5000)

  def move_asteroids(self, player):
    if self.animation_delay_counter % 2 == 0:
      for asteroid in self.sprite_groups["asteroids"].sprites():
        asteroid.rotation_counter += 1
        asteroid.move()
        asteroid.next_sprite()
        if asteroid.rect.y > self.height:
          self.sprite_groups["asteroids"].remove(asteroid)
        collisions = pygame.sprite.groupcollide(
                       self.sprite_groups["asteroids"],
                       self.sprite_groups["player"],
                       False,
                       False,
                       collided=pygame.sprite.collide_mask)
        for collided_asteroid in collisions:
          if not collided_asteroid.collided:
            player.hp -= 3
          collided_asteroid.collided = True

  def animate_bullets(self):
    """ animate player bullets and check for collisions against enemies """
    for bullet in self.sprite_groups["bullets"].sprites():
      bullet.move(bullet.speed)
      collisions = pygame.sprite.spritecollide(
                     bullet,
                     self.sprite_groups["enemies"],
                     False,
                     collided=pygame.sprite.collide_mask)
      for enemy in collisions:
        enemy.hp -= 1
        self.sprite_groups["bullets"].remove(bullet)
        if enemy.hp == 0:
          # 1 in 10 chance to spawn power up
          if random.random() < 0.1:
            power_up = SpeedPowerUp(
                         enemy.rect.x,
                         enemy.rect.y,
                         self.sprite_groups["power_ups"])
          self.sprite_groups["enemies"].remove(enemy)
        if not self.sprite_groups["enemies"]:
          self.win = True
        if bullet.rect.y < 0:
          self.sprite_groups["bullets"].remove(bullet)

  def animate_enemies(self):
    """ animate enemies and check for collisions against themselves """
    if self.animation_delay_counter % 6 == 0:
      for enemy in self.sprite_groups["enemies"].sprites():
        if not enemy.collided:
          enemy.old_arc_x = enemy.rect.x
          enemy.old_arc_y = enemy.rect.y
          enemy.move_arc()
          enemy.check_out_of_bounds(self.width, self.height, enemy.old_arc_x, enemy.old_arc_y)
          collisions = enemy.check_collisions(self.sprite_groups["enemies"])
          if collisions:
            enemy.collided = True
            enemy.rect.x = enemy.old_arc_x
            enemy.rect.y = enemy.old_arc_y
        elif enemy.collided:
          pdb.set_trace()
          enemy.old_x = enemy.rect.x
          enemy.old_y = enemy.rect.y
          print("enemy.move")
          enemy.move()
          enemy.update_center()
          #enemy.move_arc()
          collisions = enemy.check_collisions(self.sprite_groups["enemies"])
          if collisions:
            enemy.rect.x = enemy.old_x
            enemy.rect.y = enemy.old_y
            # try another move direction
            enemy.moves.pop(0)
            print(enemy.moves)
            enemy.set_move_dir2()
          if not collisions:
            enemy.collided = False
              
  def animate_enemy_bullets(self, player):
    """ create enemy bullets, move them, and check for collisions against player """
    for enemy in self.sprite_groups["enemies"].sprites():
      if enemy.shooting and self.time_now > enemy.next_bullet_time:
        enemy_bullet = create_enemy_bullet(enemy, self.sprite_groups["enemy_bullets"])
        self.sprite_groups["enemy_bullets"].add(enemy_bullet)
        enemy.next_bullet_time = self.time_now + enemy_bullet.delay

    for bullet in self.sprite_groups["enemy_bullets"].sprites():
      bullet.move(bullet.speed)
      collisions = pygame.sprite.spritecollide(
                     bullet,
                     self.sprite_groups["player"],
                     False,
                     collided=pygame.sprite.collide_mask)
      if collisions:
        self.sprite_groups["enemy_bullets"].remove(bullet)
        player.hp -= 1

  def animate_powerups(self):
    for power_up in self.sprite_groups["power_ups"]:
      power_up.move(power_up.speed)
      collisions = pygame.sprite.spritecollide(
                     power_up,
                     self.sprite_groups["player"],
                     False,
                     collided=pygame.sprite.collide_mask)
      if collisions:
        self.sprite_groups["power_ups"].remove(power_up)
        player.bullet_delay = 50
        player.speed_power_up_expiry = self.time_now + player.speed_power_up_duration
      if power_up.rect.y > self.height:
        self.sprite_groups["power_ups"].remove(power_up)

  def check_powerup_expiry(self, player):
    if self.time_now > player.speed_power_up_expiry:
      player.speed_power_up_expiry = 0
      player.bullet_delay = 200

class Stars():
  def __init__(self, game) -> None:
    random.seed()
    self.direction = "down"
    self.stars = []
    # count of stars per layer
    self.layer_1 = 200
    self.layer_2 = 400
    self.layer_3 = 800
    self.num_stars = self.layer_1 + self.layer_2 + self.layer_3
    self.white = 255, 255, 255
    self.lightblue = 200, 200, 255
    self.lightred = 255, 200, 200
    self.lightyellow = 255, 200, 255
    self.game = game
    self.init(self.game.screen)
    self.init_layer_1()

  def init(self, screen):
    for loop in range(0, self.num_stars):
      star = [random.randrange(0, int(screen.get_width() - 1)),
              random.randrange(0, int(screen.get_height() - 1))]
      self.stars.append(star);

  def move(self, start, end):
    for loop in range(start, end):
      if (self.direction == "down"):
        if (self.stars[loop][1] != self.game.height - 1):
            self.stars[loop][1] = self.stars[loop][1] + 1
        else:
          self.stars[loop][0] = random.randrange(0, int(self.game.width - 1))
          self.stars[loop][1] = 1

  def init_layer_1(self):
    for loop in range(0, self.layer_1):
      self.game.screen.set_at(self.stars[loop], self.white)

  def move_layers(self):
    self.move(
      0,
      self.layer_1)
    if (self.game.animation_delay_counter % 2 == 0):
      self.move(
        self.layer_1 + 1,
        self.layer_1 + self.layer_2)
    if (self.game.animation_delay_counter % 5 == 0):
      self.move(
        self.layer_1 + self.layer_2 + 1,
        self.num_stars)

  def draw(self):
    for loop in range(0, self.layer_1):
      self.game.screen.set_at(self.stars[loop], self.lightblue)
    for loop in range(self.layer_1 + 1, self.layer_1 + self.layer_2):
      self.game.screen.set_at(self.stars[loop], self.lightred)
    for loop in range(self.layer_1 + self.layer_2 + 1, self.num_stars):
      self.game.screen.set_at(self.stars[loop], self.lightyellow)