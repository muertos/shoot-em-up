#!/usr/bin/env python

from objects import *
import copy

# Constants
SCREEN_WIDTH = 626
SCREEN_HEIGHT = 476
BG_COLOR = (0,0,0)
PLAYER_HEIGHT = 8
PLAYER_WIDTH = 85
PLAYER_SPEED = 5
BULLET_SPEED = -8
BRICK_HEIGHT = 24
BRICK_WIDTH = 24
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
  [0,0,0,0,0,0,0,0,0,0,0,0],
  [0,0,0,0,0,0,0,0,0,0,0,0],
  [0,0,0,0,1,1,0,1,1,0,0,0],
  [0,0,0,1,1,1,1,1,1,1,0,0],
  [0,0,1,1,0,1,1,1,0,1,1,0],
  [0,0,1,1,1,1,1,1,1,1,1,0],
  [0,0,1,1,1,1,1,1,1,1,1,0],
  [0,0,1,0,1,0,1,0,1,0,1,0],
  [0,0,0,1,1,1,1,1,1,1,0,0]]

_level = [
  [0,0,0,0,0,0,0,0,0,0,0,0],
  [0,0,0,0,0,0,0,0,0,0,0,0],
  [0,0,0,0,1,0,0,0,1,0,0,0],
  [0,0,0,0,0,0,0,0,0,0,0,0],
  [0,0,1,0,0,0,1,0,0,0,1,0],
  [0,0,0,0,0,0,0,0,0,0,0,0],
  [0,0,1,0,1,0,1,0,1,0,1,0],
  [0,0,0,0,0,0,0,0,0,0,0,0],
  [0,0,1,0,1,0,1,0,1,0,1,0],
  [0,0,0,0,0,0,0,0,0,0,0,0],
  [0,0,0,0,1,0,0,0,1,0,0,0],
  [0,0,0,0,0,0,0,0,0,0,0,0],
  [0,0,0,1,0,1,0,1,0,1,0,0],
  [0,0,0,0,0,0,0,0,0,0,0,0],
  [0,0,1,0,0,1,0,1,0,0,1,0],
  [0,0,0,0,0,0,0,0,0,0,0,0]]


def make_level(level, sprites, bricks):
  """ given a matrix, make a level, starting at (0,0) """  
  for i in range(len(level)):
    for j in range(len(level[i])):
      if level[i][j] == 1:
        brick = Brick((BRICK_WIDTH * j) + 3, (BRICK_HEIGHT * i) + 3, sprites)
        sprites.add(brick)
        bricks.append(brick)

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
  player = Player((SCREEN_WIDTH / 2) - (PLAYER_WIDTH / 2), SCREEN_HEIGHT - PLAYER_HEIGHT, sprites)
  bullets = []
  bricks = []
  make_level(level, sprites, bricks)
  next_bullet_time = 0

  while True:
    clock.tick(120)
    screen.blit(background, (0,0))

    keys = pygame.key.get_pressed()
    time_now = pygame.time.get_ticks()
    if keys[pygame.K_LEFT]:
      player.move(-PLAYER_SPEED)
    if keys[pygame.K_RIGHT]:
      player.move(PLAYER_SPEED)
    if keys[pygame.K_END]:
      sys.exit(0)
    if keys[pygame.K_SPACE] and time_now > next_bullet_time:
      bullet = Bullet(player.rect.x, player.rect.y, sprites)
      # introduce delay between bullets
      next_bullet_time = bullet.delay + time_now
      bullets.append(bullet)
    
    # event handler
    for e in pygame.event.get():
      if e.type == QUIT:
        return

    # move bullets
    for bullet in bullets.copy():
      bullet.move(BULLET_SPEED)
      for brick in bricks.copy():
        if bullet.rect.colliderect(brick.rect):
          bullet.kill()
          brick.kill()
          bullets.remove(bullet)
          bricks.remove(brick)
          if not bricks:
            print("you win")
            return
          break
      if bullet.rect.y < 0:
          bullet.kill()
          bullets.remove(bullet)

    # brick movement / collision detection  
    #for brick in bricks.copy():
    #  brick.move_random()
    #  for brick2 in bricks[::-1]:
    #    if brick.rect.colliderect(brick2.rect):
    #      brick2.reverse_direction()
    #      break


    screen.fill((0,0,0))
    sprites.draw(screen)
    pygame.display.flip()

if __name__ == "__main__":
  main()