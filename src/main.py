#!/usr/bin/env python3

from game_objects import *
import copy

# Constants
SCREEN_WIDTH = 800 * 1.5
SCREEN_HEIGHT = 600 * 1.5
BG_COLOR = 10, 10, 20
GAME_TITLE = "Shoot 'em up"

def main():
  # initialize pygame and game object
  game = Game(GAME_TITLE,
              SCREEN_WIDTH,
              SCREEN_HEIGHT,
              BG_COLOR)
  # generate scrolling star background              
  stars = Stars(game)

  # FIXME: dict
  # sprite groups
  bullet_group = pygame.sprite.Group()
  enemy_group = pygame.sprite.Group()
  enemy_bullet_group = pygame.sprite.Group()
  player_group = pygame.sprite.Group()
  asteroid_group = pygame.sprite.Group()
  power_ups = pygame.sprite.Group()
  
  # game state and game objects
  player = create_player(player_group, game)
  game.make_level(enemy_group)

  # load introduction
  game.intro()
  game.draw_hp(player)

  # render rotated asteroids
  rotated_asteroid_sprites = generate_sprite_rotations(
                               1.0,
                               'asteroid.png')

  while True:
    # counter to delay animations
    game.incrementer += 1

    # set current time
    time_now = pygame.time.get_ticks()

    # event handler
    for event in pygame.event.get():
      if event.type == QUIT:
        return

    keys = pygame.key.get_pressed()
    old_player_x = player.rect.x

    if not game.lose:
      if keys[pygame.K_LEFT]:
        player.move(-player.speed)
        if player.rect.x < 0:
          player.rect.x = old_player_x
      if keys[pygame.K_RIGHT]:
        player.move(player.speed)
        if player.rect.x + player.image.get_width() > game.width:
          player.rect.x = old_player_x
      if keys[pygame.K_SPACE] and time_now > player.next_bullet_time:
        bullet = create_bullet(player, player.bullet_delay, bullet_group)
        # introduce delay between bullets
        player.next_bullet_time = bullet.delay + time_now

    if keys[pygame.K_END] or keys[pygame.K_ESCAPE]:
      sys.exit(0)

    # spawn asteroids
    if time_now > game.next_asteroid_time:
      x = random.randrange(
            0,
            game.width - game.asteroid_img.get_width())
      asteroid = Asteroid(x,
                          0 - game.asteroid_img.get_height(),
                          asteroid_group,
                          rotated_asteroid_sprites)
      game.next_asteroid_time = time_now + random.randrange(2000, 5000)

    # move asteroids
    if game.incrementer % 2 == 0:
      for asteroid in asteroid_group.sprites():
        asteroid.rotation_counter += 1
        asteroid.move()
        asteroid.next_sprite()
        if asteroid.rect.y > game.height:
          asteroid_group.remove(asteroid)

    # move bullets / bullet collision detection
    for bullet in bullet_group.sprites():
      bullet.move(bullet.speed)
      collisions = pygame.sprite.spritecollide(
                     bullet,
                     enemy_group,
                     False,
                     collided=pygame.sprite.collide_mask)
      for enemy in collisions:
        enemy.hp -= 1
        bullet_group.remove(bullet)
        if enemy.hp == 0:
          # 1 in 10 chance to spawn power up
          if random.random() < 0.1:
            power_up = SpeedPowerUp(
                         enemy.rect.x,
                         enemy.rect.y,
                         power_ups)
          enemy_group.remove(enemy)
        if not enemy_group:
          game.win = True
        if bullet.rect.y < 0:
          bullet_group.remove(bullet)
          
    # enemy movement / collision detection  
    if game.incrementer % 3 == 0:
      for enemy in enemy_group.sprites():
        if not enemy.collided:
          enemy.old_x = enemy.rect.x
          enemy.old_y = enemy.rect.y
          # move enemies in different patterns based on elapsed time
          if time_now < game.init_time + enemy.movement_timer:
            enemy.move_arc()
          else:
            enemy.move_random()
        # check if enemies are out of bounds  
        if enemy.rect.x + enemy.image.get_width() > game.width:
          enemy.rect.x = enemy.old_x
        if enemy.rect.x < 0:
          enemy.rect.x = enemy.old_x
        if enemy.rect.y + enemy.image.get_height() > game.height:
          enemy.rect.y = enemy.old_y
        if enemy.rect.y < 0:
          enemy.rect.y = enemy.old_y
      for enemy in enemy_group.sprites():
        enemy_collisions = pygame.sprite.spritecollide(
                             enemy,
                             enemy_group,
                             False,
                             collided=pygame.sprite.collide_mask)
        #asteroid_collisions = pygame.sprite.spritecollide(enemy, asteroid_group, False, collided=pygame.sprite.collide_mask)
        enemy_collisions.remove(enemy)
        if enemy_collisions:
          enemy.collided = True
          enemy.rect.x = enemy.old_x
          enemy.rect.y = enemy.old_y
          for collided_enemy in enemy_collisions:
            collided_enemy.rect.x = collided_enemy.old_x
            collided_enemy.rect.y = collided_enemy.old_y
        if not enemy_collisions:
          enemy.collided = False

    # create enemy bullets
    for enemy in enemy_group.sprites():
      if enemy.shooting and time_now > enemy.next_bullet_time:
        enemy_bullet = create_enemy_bullet(enemy, enemy_bullet_group)
        enemy_bullet_group.add(enemy_bullet)
        enemy.next_bullet_time = time_now + enemy_bullet.delay

    # move enemy bullets
    for bullet in enemy_bullet_group.sprites():
      bullet.move(bullet.speed)
      collisions = pygame.sprite.spritecollide(
                     bullet,
                     player_group,
                     False,
                     collided=pygame.sprite.collide_mask)
      if collisions:
        enemy_bullet_group.remove(bullet)
        player.hp -= 1
      if player.hp == 0:
        game.lose = True

    # move power ups
    for power_up in power_ups:
      power_up.move(power_up.speed)
      collisions = pygame.sprite.spritecollide(
                     power_up,
                     player_group,
                     False,
                     collided=pygame.sprite.collide_mask)
      if collisions:
        power_ups.remove(power_up)
        player.bullet_delay = 50
        player.speed_power_up_expiry = time_now + player.speed_power_up_duration
      if power_up.rect.y > game.height:
        power_ups.remove(power_up)

    # check if power up buff has expired
    if time_now > player.speed_power_up_expiry:
      player.speed_power_up_expiry = 0
      player.bullet_delay = 200

    # we draw things after screen.fill, otherwise they don't display!
    game.screen.fill(game.bg_color)

    # check if game is won or lost
    game.check_state()

    # update star positions and draw
    stars.move_layers()
    stars.draw()

    # don't let this incrememter grow infinitely
    if game.incrementer == 500:
      game.incrementer = 2

    # draw sprite groups
    asteroid_group.draw(game.screen)
    bullet_group.draw(game.screen)
    enemy_group.draw(game.screen)
    enemy_bullet_group.draw(game.screen)
    power_ups.draw(game.screen)
    player_group.draw(game.screen)
    game.draw_hp(player)

    # pygame things
    pygame.time.delay(stars.delay)
    pygame.display.flip()

if __name__ == "__main__":
  main()
