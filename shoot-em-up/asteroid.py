import pygame

from utility_functions import load_png

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

  def draw(self, game, player):
    self.rotation_counter += 1
    self.move()
    self.next_sprite()
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