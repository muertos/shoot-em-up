import pygame

class Animation():
  def __init__(self, delay: int, direction: int) -> None:
    # these elements seem universal
    self.sprites: list(pygame.Surface, pygame.Rect) = []
    self.count: int = 0
    self.image = None
    self.mask = None
    # direction to traverse sprites list (forward/backward, ie 1/-1)
    # animation delay in ms
    self.delay: int = delay
    # when to update to the next frame, or sprite
    self.next_frame_time: int = 0

    # these seem specific to player ship animation
    self.direction: int = direction
    self.enabled: bool = False
    # track if the input button is held down
    self.is_pressed: bool = False

  def update_next_frame_time(self, game):
    self.next_frame_time = game.time_now + self.delay

  def update_sprite(self):
    self.image = self.sprites[self.count].image
    self.rect = self.sprites[self.count].rect
    self.mask = pygame.mask.from_surface(self.image)
    self.count += self.direction 
    if self.count == len(self.sprites):
      self.count = 0
    elif self.count == -1:
      self.count = len(self.sprites) - 1
    elif self.count == 0:
      self.direction = 1

  def hold_last_frame_or_reverse(self):
    if self.is_pressed:
      self.direction = 0
    else:
      self.direction = -1

class SpriteData():
  def __init__(self, image, rect) -> None:
    self.image: pygame.Surface = image
    self.rect: pygame.Rect = rect