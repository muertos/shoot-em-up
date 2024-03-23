#!/usr/bin/env python

from objects import *

# Constants
SCREEN_WIDTH = 626
SCREEN_HEIGHT = 476
BG_COLOR = (0,0,0)
PLAYER_HEIGHT = 8
PLAYER_WIDTH = 85
PLAYER_SPEED = 5
BULLET_SPEED = -8
BRICK_HEIGHT = 11
BRICK_WIDTH = 49
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

def make_level(level, sprites, bricks):
  """ given a matrix, make a level, starting at (0,0) """  
  for i in range(len(level)):
    for j in range(len(level[i])):
      if level[i][j] == 1:
        brick = Brick(BRICK_WIDTH * j, BRICK_HEIGHT * i, sprites)
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

  while True:
    clock.tick(120)
    screen.blit(background, (0,0))

    # event handler
    for e in pygame.event.get():
      if e.type == KEYDOWN:
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE]:
          bullet = Bullet(player.rect.x, player.rect.y, sprites)
          bullets.append(bullet)
      if e.type == QUIT:
        return

    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
      player.move(-PLAYER_SPEED)
    if keys[pygame.K_RIGHT]:
      player.move(PLAYER_SPEED)
    if keys[pygame.K_END]:
      sys.exit(0)
    
    for bullet in bullets:
      bullet.move(BULLET_SPEED)
      if bullet.rect.y < 0:
        bullets.remove(bullet)
        sprites.remove(bullet)
      for brick in bricks:
        if bullet.rect.colliderect(brick.rect):
          sprites.remove(bullet)
          sprites.remove(brick)

    screen.fill((0,0,0))
    sprites.draw(screen)
    pygame.display.flip()

if __name__ == "__main__":
  main()