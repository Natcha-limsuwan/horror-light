import pygame
from settings import *
from sprites import Enemy, Gem
import math
import os


class Player(pygame.sprite.Sprite):
    def __init__(self, game, pos, groups):
        super().__init__(groups)
        self.game = game

        self.direction_images = {
            'up': pygame.image.load('character/ch_up.png').convert_alpha(),
            'down': pygame.image.load('character/ch_down.png').convert_alpha(),
            'left': pygame.image.load('character/ch_left.PNG').convert_alpha(),
            'right': pygame.image.load('character/ch_right.png').convert_alpha()
        }

        for direction, image in self.direction_images.items():
            self.direction_images[direction] = pygame.transform.scale(image, (40, 75))

        self.current_direction = 'down'
        self.image = self.direction_images[self.current_direction]
        self.rect = self.image.get_rect(center=pos)

        self.speed = PLAYER_SPEED
        self.direction = pygame.math.Vector2()
        self.facing_direction = pygame.math.Vector2(0, 1)  # เริ่มต้นหันเข้าจอ
        self.flashlight_on = False
        self.flashlight_cooldown = 0
        self.f_key_pressed = False

    def input(self):
        keys = pygame.key.get_pressed()
        x_direction = keys[pygame.K_d] - keys[pygame.K_a] or keys[pygame.K_RIGHT] - keys[pygame.K_LEFT]
        y_direction = keys[pygame.K_s] - keys[pygame.K_w] or keys[pygame.K_DOWN] - keys[pygame.K_UP]

        self.direction.x = x_direction
        self.direction.y = y_direction

        if x_direction != 0 or y_direction != 0:
            self.facing_direction = pygame.math.Vector2(x_direction, y_direction).normalize()

            if abs(x_direction) > abs(y_direction):
                if x_direction > 0:
                    self.current_direction = 'right'
                else:
                    self.current_direction = 'left'
            else:
                if y_direction > 0:
                    self.current_direction = 'down'
                else:
                    self.current_direction = 'up'

            self.image = self.direction_images[self.current_direction]

        for event in self.game.events_to_process:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_a:
                self.flashlight_on = not self.flashlight_on

    def move(self):
        if self.direction.magnitude() != 0:
            self.direction = self.direction.normalize()
        self.rect.x += self.direction.x * self.speed
        self.collision('horizontal')
        self.rect.y += self.direction.y * self.speed
        self.collision('vertical')

    def collision(self, direction):
        for sprite in self.game.obstacles:
            if sprite.rect.colliderect(self.rect):
                if direction == 'horizontal':
                    if self.direction.x > 0:
                        self.rect.right = sprite.rect.left
                    if self.direction.x < 0:
                        self.rect.left = sprite.rect.right
                if direction == 'vertical':
                    if self.direction.y > 0:
                        self.rect.bottom = sprite.rect.top
                    if self.direction.y < 0:
                        self.rect.top = sprite.rect.bottom

    def flashlight_kill(self):
        if not self.flashlight_on:
            return

        beam_length = 200
        cone_width = 40

        player_pos = pygame.math.Vector2(self.rect.center)
        facing_dir = pygame.math.Vector2(self.facing_direction).normalize()

        angle = math.atan2(-facing_dir.y, facing_dir.x)
        left_angle = angle - math.radians(cone_width / 2)
        right_angle = angle + math.radians(cone_width / 2)

        for enemy in list(self.game.enemies):
            enemy_pos = pygame.math.Vector2(enemy.rect.center)
            to_enemy = enemy_pos - player_pos

            if to_enemy.length() > beam_length:
                continue

            enemy_angle = math.atan2(-to_enemy.y, to_enemy.x)
            if left_angle <= enemy_angle <= right_angle:
                enemy.kill()
                self.game.score += 10

    def collect_gems(self):
        for gem in pygame.sprite.spritecollide(self, self.game.gems, True):
            self.game.score += 5

    def check_collision_with_enemy(self):
        if pygame.sprite.spritecollideany(self, self.game.enemies):
            self.game.save_game_data('killed_by_enemy')
            self.game.game_over('You were caught!')

    def collect_key(self):
        keys_collected = pygame.sprite.spritecollide(self, self.game.keys, True)
        if keys_collected:
            self.game.has_key = True
            # สามารถเพิ่มเสียงหรือเอฟเฟกต์ที่นี่

    def check_door(self):
        if pygame.sprite.spritecollideany(self, self.game.doors):
            if self.game.has_key:  # ตรวจสอบว่ามีกุญแจ
                if self.game.level < 3:
                    self.game.level += 1
                    self.game.has_key = False  # รีเซ็ตสถานะกุญแจ
                    self.game.new_level()
                else:
                    self.game.save_game_data('win')
                    self.game.game_over('Victory!')

    def update(self):
        if self.flashlight_cooldown > 0:
            self.flashlight_cooldown -= 1

        self.input()
        self.move()
        self.collect_gems()
        self.flashlight_kill()
        self.check_collision_with_enemy()
        self.collect_key()
        self.check_door()