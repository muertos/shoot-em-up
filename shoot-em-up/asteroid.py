import pygame

from animation import Animation

from utility_functions import generate_sprite_rotations, load_png

class Asteroid(pygame.sprite.Sprite):
  def __init__(self, x: int, y: int, delay: int, spin_direction: int, sprite_group) -> None:
    pygame.sprite.Sprite.__init__(self, sprite_group)
    self.image, self.rect = load_png('asteroid.png')
    self.mask = pygame.mask.from_surface(self.image)
    self.rect.x = x
    self.rect.y = y
    self.speed = 1
    self.delay = delay
    self.spin_direction = spin_direction
    # pre-load sprite rotations to not make the cpu work so hard
    self.animation: Animation = Animation(delay, spin_direction)
    self.collided = False

    self.load_sprite_animations()

  def load_sprite_animations(self):
    self.animation.sprites = generate_sprite_rotations(
      1.0,
      0,
      360.0,
      'asteroid.png')

  def move(self):
    self.rect.y += self.speed

  def draw(self, game, player):
    x = self.rect.centerx
    y = self.rect.centery
    self.move()
    if game.time_now > self.animation.next_frame_time:
      self.animation.update_next_frame_time(game)
      self.animation.update_sprite()
      self.image = self.animation.image
      self.rect = self.animation.rect
      self.mask = self.animation.mask
      self.rect.centerx = x
      self.rect.centery = y
    if self.rect.y > game.height:
      game.sprite_groups["asteroids"].remove(self)
    collisions = pygame.sprite.groupcollide(
      game.sprite_groups["asteroids"],
      game.sprite_groups["player"],
      False,
      False,
      collided=pygame.sprite.collide_mask)
    for collided_asteroid in collisions:
      if not collided_asteroid.collided:
        player.hp -= 3
      collided_asteroid.collided = True