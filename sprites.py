import pygame
import time
from settings import *
from random import randint
import math


class Map:
    def __init__(self, game, layout):
        self.game = game
        self.layout = layout
        self.create_map(layout)

    def create_map(self, layout):
        for row_index, row in enumerate(layout):
            for col_index, cell in enumerate(row):
                x = col_index * TILESIZE
                y = row_index * TILESIZE

                if cell == '1':
                    Obstacle((x, y), [self.game.all_sprites, self.game.obstacles])
                elif cell == '.':
                    if randint(0, 15) == 0:
                        Gem((x + TILESIZE // 2, y + TILESIZE // 2), [self.game.all_sprites, self.game.gems])
                    elif randint(0, 40) == 0:
                        Enemy(self.game, (x + TILESIZE // 2, y + TILESIZE // 2),
                              [self.game.all_sprites, self.game.enemies])
                elif cell == 'k':


    def draw(self, screen):
        for row_index, row in enumerate(self.layout):
            for col_index, cell in enumerate(row):
                if cell == '.':
                    x = col_index * TILESIZE
                    y = row_index * TILESIZE
                    pygame.draw.rect(screen, (20, 20, 20), (x, y, TILESIZE, TILESIZE))


class Obstacle(pygame.sprite.Sprite):
    def __init__(self, pos, groups):
        super().__init__(groups)
        self.image = pygame.Surface((TILESIZE, TILESIZE), pygame.SRCALPHA)
        self.image.fill((0, 0, 0, 0))
        self.rect = self.image.get_rect(topleft=pos)


class Gem(pygame.sprite.Sprite):
    def __init__(self, pos, groups):
        super().__init__(groups)

        sprite_sheet = pygame.image.load('allgem.png').convert_alpha()

        self.frame_width = sprite_sheet.get_width() // 5
        self.frame_height = sprite_sheet.get_height()

        self.frames = []
        for i in range(5):
            frame = sprite_sheet.subsurface(pygame.Rect(i * self.frame_width, 0, self.frame_width, self.frame_height))
            frame = pygame.transform.scale(frame, (TILESIZE, TILESIZE))
            self.frames.append(frame)

        self.frame_index = 0
        self.animation_speed = 0.05
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect(center=pos)

    def update(self):
        self.frame_index += self.animation_speed
        if self.frame_index >= len(self.frames):
            self.frame_index = 0

        self.image = self.frames[int(self.frame_index)]
        self.rect = self.image.get_rect(center=self.rect.center)


class Enemy(pygame.sprite.Sprite):
    def __init__(self, game, pos, groups):
        super().__init__(groups)
        self.game = game
        self.image = pygame.image.load("ghost/gh_down.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (30, 50))
        self.rect = self.image.get_rect(center=pos)
        self.is_active = False  # เริ่มต้นแบบไม่เคลื่อนที่
        self.health = 50
        self.is_dead = False
        self.speed = ENEMY_SPEED

    def update(self):
        if self.health <= 0:
            self.is_dead = True
            self.kill()

        if self.game.player.flashlight_on:
            # คำนวณว่าผีอยู่ในแสง
            player_center = self.game.player.rect.center
            direction = self.game.player.facing_direction
            beam_length = 200
            cone_width = 40
            to_enemy = pygame.math.Vector2(
                self.rect.centerx - player_center[0],
                self.rect.centery - player_center[1]
            )

            if to_enemy.length() < beam_length:
                angle = math.degrees(math.atan2(-direction.y, direction.x) - math.atan2(-to_enemy.y, to_enemy.x))
                if abs(angle) < cone_width / 2:
                    self.is_active = True

        if self.game.player.flashlight_on:
            direction = pygame.math.Vector2(self.game.player.rect.center) - pygame.math.Vector2(self.rect.center)
            if direction.length() != 0:
                direction = direction.normalize()

            else:
                direction = pygame.math.Vector2(0, 0)

            move_vector = direction * self.game.enemy_speed
            self.rect.center += move_vector

        else:
            pass


