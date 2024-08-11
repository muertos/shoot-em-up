#!/usr/bin/env python3

from objects import *
import copy

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
BG_COLOR = 10, 10, 20
GAME_TITLE = "Shoot 'em up"
# top layer
STAR_LAYER_1 = 200
# middle
STAR_LAYER_2 = 400
# bottom
STAR_LAYER_3 = 800
NUM_STARS = STAR_LAYER_1 + STAR_LAYER_2 + STAR_LAYER_3
WHITE = 255, 255, 255
LIGHTBLUE = 200, 200, 255
#LIGHTGRAY = 180, 180, 180
LIGHTRED = 255, 200, 200 
#DARKGRAY = 120, 120, 120
LIGHTYELLOW = 255, 200, 255 
DOWN = 1

# define testing level
level = [
  [0,0,0,0,1,0,0,0,1,0,0,0,1,0,0,0],
  [1,0,0,0,0,0,1,0,0,0,0,1,0,0,1,0],
  [1,0,0,0,0,0,0,0,0,0,0,1,0,0,0,1],
  [0,1,0,0,0,0,0,0,0,0,1,0,1,0,1,0]]

def init_stars(screen):
  stars = []
  for loop in range(0, NUM_STARS):
    star = [random.randrange(0, screen.get_width() - 1),
            random.randrange(0, screen.get_height() - 1)]
    stars.append(star);
  return stars

def move_stars(screen, stars, start, end, direction):
  for loop in range(start, end):
    if (direction == DOWN):
      if (stars[loop][1] != screen.get_height() - 1):
          stars[loop][1] = stars[loop][1] + 1
      else:
        stars[loop][0] = random.randrange(0, screen.get_width() - 1)
        stars[loop][1] = 1
  return stars
 
def make_level(level, sprites):
  # initialize width / height
  img = pygame.image.load('data/enemy_ship.png')
  """ given a matrix, make a level, starting at (0,0) """  
  for i in range(len(level)):
    for j in range(len(level[i])):
      if level[i][j] == 1:
        enemy = Enemy(((img.get_width() + 12) * j), ((img.get_height() + 12)* i), sprites)
        sprites.add(enemy)

def draw_text(text, color=(0,200,0), font_size=30):
  font = pygame.font.SysFont(None, font_size)
  return font.render(text, False, color)

def create_game_window():
  screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), HWSURFACE|DOUBLEBUF)
  background = pygame.Surface(screen.get_size())
  background = background.convert()
  background.fill(BG_COLOR)
  screen.blit(background, (0,0))
  pygame.display.flip()
  screen.fill(BG_COLOR)
  pygame.display.set_caption(GAME_TITLE)
  return screen, background

def create_player(group):
  player_img = pygame.image.load('data/ship.png')
  return Player((SCREEN_WIDTH / 2) - (player_img.get_width() / 2), SCREEN_HEIGHT - player_img.get_height(), group)

def create_bullet(player, delay, bullet_group):
  bullet_img = pygame.image.load('data/bullet.png')
  return Bullet(player.rect.x + (player.image.get_width() / 2) - (bullet_img.get_width() / 2), player.rect.y, delay, bullet_group)

def create_enemy_bullet(enemy, enemy_bullet_group):
  enemy_bullet_img = pygame.image.load('data/enemy_bullet.png')
  return EnemyBullet(enemy.rect.x + enemy.image.get_width() / 2 - enemy_bullet_img.get_width() / 2, enemy.rect.y + enemy_bullet_img.get_height(), enemy_bullet_group)

def draw_hp(player, screen):
  for i in range(0, player.hp):
    screen.blit(draw_text("*", (0,200,0), 50), (i*15, screen.get_height() - 20))

def generate_sprite_rotations(angle, image):
  image, orig_rect = load_png(image)
  rotated_sprites = []
  current_angle = 0.0
  for loop in range(0, int(360.0 / angle)):
    current_angle = current_angle + angle
    rotated_img = pygame.transform.rotate(image, current_angle)
    rotated_rect = rotated_img.get_rect(center=orig_rect.center)
    rotated_sprites.append((rotated_img, rotated_rect))
  return rotated_sprites

def intro(screen, background):
  while True:
    # need event handler for this loop to function
    for event in pygame.event.get():
      if event.type == QUIT:
        return
    screen.blit(background, (0,0))
    screen.blit(draw_text("arrow keys to move, space to shoot, press enter to play"), (150, SCREEN_HEIGHT / 2 - 30))
    keys = pygame.key.get_pressed()
    if keys[pygame.K_RETURN]:
      break
    if keys[pygame.K_END] or keys[pygame.K_ESCAPE]:
      sys.exit(0)
    pygame.display.flip()

def main():
  # initialize pygame and game screen
  pygame.init()
  screen, background = create_game_window()

  # stars
  random.seed()
  delay = 8
  inc = 2
  direction = DOWN
  stars = init_stars(screen)
  # Place layer 1 stars 
  for loop in range(0, STAR_LAYER_1):
    screen.set_at(stars[loop], WHITE)

  # sprite groups
  bullet_group = pygame.sprite.Group()
  enemy_group = pygame.sprite.Group()
  enemy_bullet_group = pygame.sprite.Group()
  player_group = pygame.sprite.Group()
  asteroid_group = pygame.sprite.Group()
  power_ups = pygame.sprite.Group()
  
  # game state and game objects
  lose = win = False
  player = create_player(player_group)
  make_level(level, enemy_group)
  next_asteroid_time = 0
  asteroid_spawn_delay = random.randrange(7000, 15000)
  asteroid_img = pygame.image.load('data/asteroid.png')

  # load introduction
  intro(screen, background)

  clock = pygame.time.Clock()
  screen.blit(background, (0,0))
  draw_hp(player, screen)

  # render rotated asteroids
  rotated_asteroid_sprites = generate_sprite_rotations(1.0, 'asteroid.png')
  
  while True:
    # counter to delay animations
    inc += 1

    # event handler
    for event in pygame.event.get():
      if event.type == QUIT:
        return
    keys = pygame.key.get_pressed()
    time_now = pygame.time.get_ticks()
    prev_x = player.rect.x
    if not lose:
      if keys[pygame.K_LEFT]:
        player.move(-player.speed)
        if player.rect.x < 0:
          player.rect.x = prev_x
      if keys[pygame.K_RIGHT]:
        player.move(player.speed)
        if player.rect.x + player.image.get_width() > screen.get_width():
          player.rect.x = prev_x
      if keys[pygame.K_SPACE] and time_now > player.next_bullet_time:
        bullet = create_bullet(player, player.bullet_delay, bullet_group)
        # introduce delay between bullets
        player.next_bullet_time = bullet.delay + time_now
    if keys[pygame.K_END] or keys[pygame.K_ESCAPE]:
      sys.exit(0)

    # spawn asteroids
    if time_now > next_asteroid_time:
      x = random.randrange(0, screen.get_width() - asteroid_img.get_width())
      asteroid = Asteroid(x, 0 - asteroid_img.get_height(), asteroid_group, rotated_asteroid_sprites)
      next_asteroid_time = time_now + random.randrange(2000, 5000)

    # move asteroids
    if inc % 2 == 0:
      for asteroid in asteroid_group.sprites():
        asteroid.rotation_counter += 1
        asteroid.move()
        asteroid.next_sprite()
        if asteroid.rect.y > screen.get_height():
          asteroid_group.remove(asteroid)

    # move bullets / bullet collision detection
    for bullet in bullet_group.sprites():
      bullet.move(bullet.speed)
      collisions = pygame.sprite.spritecollide(bullet, enemy_group, False, collided=pygame.sprite.collide_mask)
      for enemy in collisions:
        enemy.hp -= 1
        bullet_group.remove(bullet)
        if enemy.hp == 0:
          # 1 in 10 chance to spawn power up
          if random.random() < 0.1:
            power_up = SpeedPowerUp(enemy.rect.x, enemy.rect.y, power_ups)
          enemy_group.remove(enemy)
        if not enemy_group:
          win = True
        if bullet.rect.y < 0:
          bullet_group.remove(bullet)
          
    # enemy movement / collision detection  
    for enemy in enemy_group.sprites():
      prev_x = enemy.rect.x
      prev_y = enemy.rect.y
      enemy.move_random()
      enemy_collisions = pygame.sprite.spritecollide(enemy, enemy_group, False, collided=pygame.sprite.collide_mask)
      asteroid_collisions = pygame.sprite.spritecollide(enemy, asteroid_group, False, collided=pygame.sprite.collide_mask)
      enemy_collisions.remove(enemy)
      if enemy_collisions or asteroid_collisions:
        enemy.rect.x = prev_x
        enemy.rect.y = prev_y
      # check if enemies are out of bounds  
      if enemy.rect.x + enemy.image.get_width() > screen.get_width():
        enemy.rect.x = prev_x
      if enemy.rect.x < 0:
        enemy.rect.x = prev_x
      if enemy.rect.y + enemy.image.get_height() > screen.get_height():
        enemy.rect.y = prev_y
      if enemy.rect.y < 0:
        enemy.rect.y = prev_y

    # create enemy bullets
    for enemy in enemy_group.sprites():
      if enemy.shooting and time_now > enemy.next_bullet_time:
        enemy_bullet = create_enemy_bullet(enemy, enemy_bullet_group)
        enemy_bullet_group.add(enemy_bullet)
        enemy.next_bullet_time = time_now + enemy_bullet.delay

    # move enemy bullets
    for bullet in enemy_bullet_group.sprites():
      bullet.move(bullet.speed)
      collisions = pygame.sprite.spritecollide(bullet, player_group, False, collided=pygame.sprite.collide_mask)
      if collisions:
        enemy_bullet_group.remove(bullet)
        player.hp -= 1
      if player.hp == 0:
        lose = True

    # move power ups
    for power_up in power_ups:
      power_up.move(power_up.speed)
      collisions = pygame.sprite.spritecollide(power_up, player_group, False, collided=pygame.sprite.collide_mask)
      if collisions:
        power_ups.remove(power_up)
        player.bullet_delay = 50
        player.speed_power_up_expiry = time_now + player.speed_power_up_duration
      if power_up.rect.y > screen.get_height():
        power_ups.remove(power_up)

    # check if power up buff has expired
    if time_now > player.speed_power_up_expiry:
      player.speed_power_up_expiry = 0
      player.bullet_delay = 200

    # we draw things after screen.fill, otherwise they don't display!
    screen.fill(BG_COLOR)

    # Check if stars hit the screen border
    stars = move_stars(screen, stars, 0, STAR_LAYER_1, direction)
    if (inc % 2 == 0):
      stars = move_stars(screen, stars, STAR_LAYER_1 + 1, STAR_LAYER_1 + STAR_LAYER_2, direction)
    if (inc % 5 == 0):
      stars = move_stars(screen, stars, STAR_LAYER_1 + STAR_LAYER_2 + 1, NUM_STARS, direction)

    # Place star layers
    for loop in range(0, STAR_LAYER_1):
      screen.set_at(stars[loop], LIGHTBLUE)
    for loop in range(STAR_LAYER_1 + 1, STAR_LAYER_1 + STAR_LAYER_2):
      screen.set_at(stars[loop], LIGHTRED)
    for loop in range(STAR_LAYER_1 + STAR_LAYER_2 + 1, NUM_STARS):
      screen.set_at(stars[loop], LIGHTYELLOW)

    if inc == 500:
      inc = 2

    if win:
      screen.blit(draw_text("you're a winner! :)"), (SCREEN_WIDTH / 2 - 100, SCREEN_HEIGHT / 2 - 30))
    if lose:
      screen.blit(draw_text("you lose :(", (200,0,0)), (SCREEN_WIDTH / 2 - 100, SCREEN_HEIGHT / 2 - 30))

    asteroid_group.draw(screen)
    bullet_group.draw(screen)
    enemy_group.draw(screen)
    enemy_bullet_group.draw(screen)
    power_ups.draw(screen)
    player_group.draw(screen)
    draw_hp(player, screen)

    pygame.time.delay(delay)
    pygame.display.flip()

if __name__ == "__main__":
  main()
