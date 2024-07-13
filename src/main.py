#!/usr/bin/env python

from objects import *
import copy

# Constants
SCREEN_WIDTH = 626
SCREEN_HEIGHT = 476
BG_COLOR = (0,0,0)
GAME_TITLE = "Shoot 'em up"

# define testing level
level = [
  [0,0,0,0,0,0,0,0,0,0,0,0],
  [0,0,0,0,0,0,0,0,0,0,0,0],
  [0,0,0,0,1,1,0,1,1,0,0,0],
  [0,0,0,1,1,1,1,1,1,1,0,0],
  [0,0,1,1,0,1,1,1,0,1,1,0],
  [0,0,1,1,1,1,1,1,1,1,1,0],
  [0,0,1,0,1,0,1,0,1,0,1,0],
  [0,0,0,0,0,0,0,0,0,0,0,0]]
  
def make_level(level, sprites, enemies):
  # initialize width / height
  img = pygame.image.load('data/enemy_ship.png')
  """ given a matrix, make a level, starting at (0,0) """  
  for i in range(len(level)):
    for j in range(len(level[i])):
      if level[i][j] == 1:
        enemy = Enemy(((img.get_width() + 12) * j), ((img.get_height() + 12)* i), sprites)
        sprites.add(enemy)
        enemies.append(enemy)

def main():
  pygame.init()
  screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
  background = pygame.Surface(screen.get_size())
  background = background.convert()
  background.fill(BG_COLOR)
  screen.blit(background, (0,0))
  pygame.display.flip()
  screen.fill(BG_COLOR)
  pygame.display.set_caption(GAME_TITLE)
  clock = pygame.time.Clock()
  sprites = pygame.sprite.Group()
  # load placeholder player image
  player_img = pygame.image.load('data/ship.png')
  player = Player((SCREEN_WIDTH / 2) - (player_img.get_width() / 2), SCREEN_HEIGHT - player_img.get_height(), sprites)
  # load placeholder bullet images
  bullet_img = pygame.image.load('data/bullet.png')
  enemy_bullet_img = pygame.image.load('data/enemy_bullet.png')
  bullets = []
  enemies = []
  enemy_bullets = []
  make_level(level, sprites, enemies)
  next_bullet_time = 0

  while True:
    clock.tick(120)
    screen.blit(background, (0,0))

    keys = pygame.key.get_pressed()
    time_now = pygame.time.get_ticks()
    prev_x = player.rect.x
    if keys[pygame.K_LEFT]:
      player.move(-player.speed)
      if player.rect.x < 0:
        player.rect.x = prev_x
    if keys[pygame.K_RIGHT]:
      player.move(player.speed)
      if player.rect.x + player.image.get_width() > screen.get_width():
        player.rect.x = prev_x
    if keys[pygame.K_END]:
      sys.exit(0)
    if keys[pygame.K_SPACE] and time_now > next_bullet_time:
      bullet = Bullet(player.rect.x + (player_img.get_width() / 2) - (bullet_img.get_width() / 2), player.rect.y, sprites)
      # introduce delay between bullets
      next_bullet_time = bullet.delay + time_now
      bullets.append(bullet)
    
    # event handler
    for e in pygame.event.get():
      if e.type == QUIT:
        return

    # move bullets
    for bullet in bullets.copy():
      bullet.move(bullet.speed)
      for enemy in enemies.copy():
        if bullet.rect.colliderect(enemy.rect):
          bullet.kill()
          enemy.kill()
          bullets.remove(bullet)
          enemies.remove(enemy)
          if not enemies:
            print("you win")
            return
          break
      if bullet.rect.y < 0:
          bullet.kill()
          bullets.remove(bullet)

    # enemy movement / collision detection  
    enemies_copy = enemies.copy()
    for enemy in enemies_copy:
      # remove iterating enemy because it would always collide with itself
      enemies_copy.remove(enemy)
      prev_x = enemy.rect.x
      prev_y = enemy.rect.y
      enemy.move_random()
      if enemy.rect.collidelist(enemies_copy) != -1:
        enemy.rect.x = prev_x
        enemy.rect.y = prev_y
      # check if enemies are out of bounds  
      if enemy.rect.x + enemy.image.get_width() > screen.get_width():
        enemy.rect.x = prev_x
      if enemy.rect.x < 0:
        enemy.rect.x = prev_x

    # create enemy bullets
    for enemy in enemies:
      if enemy.shooting and time_now > enemy.next_bullet_time:
        enemy_bullet = EnemyBullet(enemy.rect.x + enemy.image.get_width() / 2 - enemy_bullet_img.get_width() / 2, enemy.rect.y + enemy_bullet_img.get_height(), sprites)
        enemy_bullets.append(enemy_bullet)
        enemy.next_bullet_time = time_now + enemy_bullet.delay

    # move enemy bullets
    for bullet in enemy_bullets:
      bullet.move(bullet.speed)


    screen.fill((0,0,0))
    sprites.draw(screen)
    pygame.display.flip()

if __name__ == "__main__":
  main()