import pygame
import os

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