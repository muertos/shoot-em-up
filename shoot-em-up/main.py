#!/usr/bin/env python3

import pygame

from game import Game
from stars import Stars
from player import Player
from utility_functions import generate_sprite_rotations

import pdb

SCREEN_WIDTH = 800 * 1.5
SCREEN_HEIGHT = 600 * 1.5
BG_COLOR = 10, 10, 20
GAME_TITLE = "Shoot 'em up"

def main():
  game = Game(
    GAME_TITLE,
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    BG_COLOR)
  stars = Stars(game)
  player = Player(game.sprite_groups["player"], game)
  player.draw_hp(game)
  
  while game.running:
    game.prev_time = game.time_now
    game.time_now = pygame.time.get_ticks()
    game.clock.tick(120)
    game.increment_animation_delay_counter()
    game.handle_input(player)
    player.calculate_speed(game)
    player.move(game)
    game.spawn_asteroids()
    game.move_asteroids(player)
    game.animate_bullets(player)
    if game.intro_enemies:
      game.animate_enemies_intro()
    else:
      game.animate_enemies()
      game.animate_enemy_bullets(player)
    game.animate_powerups(player)
    stars.move_layers()
    game.check_player_hp(player)
    game.check_powerup_expiry(player)
    game.screen.fill(game.bg_color)
    #stars.draw()
    game.draw_sprites()
    game.enemy_blink_when_hit()
    player.draw_hp(game)
    # FIXME:
    #player.blink_when_hit(game)
    game.check_state()
    pygame.display.flip()

if __name__ == "__main__":
  main()
