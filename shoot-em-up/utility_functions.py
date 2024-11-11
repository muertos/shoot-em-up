import pygame
import os

def load_png(name: str) -> (pygame.Surface, pygame.Rect):
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

def generate_sprite_rotations(angle_of_rotation: float, start_angle: float, end_angle: float, image: pygame.Surface) -> list: 
  # rotate a sprite, return list of rotated sprite objects
  image, orig_rect = load_png(image)
  rotated_sprites: list = []
  angle = start_angle
  for loop in range(0, int((end_angle - start_angle) / angle_of_rotation)):
    angle += angle_of_rotation
    rotated_img = pygame.transform.rotate(image, angle)
    rotated_rect = rotated_img.get_rect(center=orig_rect.center)
    rotated_sprite = {
      "image": rotated_img,
      "rect": rotated_rect
      }
    rotated_sprites.append(rotated_sprite)
  return rotated_sprites