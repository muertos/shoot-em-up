import random

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