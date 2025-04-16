import pygame
import sys
import time
import json
import math
from settings import *
from map import level_maps
from sprites import *
from player import Player
from PIL import Image


def load_gif_frames(filename):
    image = Image.open(filename)
    frames = []

    try:
        while True:
            frame = image.convert("RGBA")
            mode = frame.mode
            size = frame.size
            data = frame.tobytes()

            py_image = pygame.image.fromstring(data, size, mode)
            py_image = pygame.transform.scale(py_image, (WIDTH, HEIGHT))
            frames.append(py_image)

            image.seek(image.tell() + 1)
    except EOFError:
        pass  # หมด frame แล้ว

    return frames


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Horror Light")
        self.clock = pygame.time.Clock()
        self.background_images = {
            1: pygame.image.load('BG/Level1.png').convert(),
            2: pygame.image.load('BG/Level_2.png').convert(),
            3: pygame.image.load('BG/Level_3.png').convert()
        }
        self.background_image = self.background_images[1]

        self.level = 1
        self.score = 0
        self.start_time = time.time()
        self.game_start_time = time.time()
        self.player_name = ""
        self.time_limit = TIME_LIMIT
        self.enemy_speed = ENEMY_SPEED
        self.enemy_spawn_delay = 5
        self.enemy_spawn_timer = 0
        self.enemy_spawn_interval = 5
        self.max_enemies = self.level + 2
        self.keys = pygame.sprite.Group()
        self.doors = pygame.sprite.Group()
        self.has_key = False  # สถานะกุญแจ
        self.load_start_screen()
        self.current_enemies = 0
        self.last_spawn_time = time.time()

    def load_start_screen(self):
        gif_frames = load_gif_frames('sea.GIF')
        frame_index = 0
        frame_rate = 100
        last_update_time = pygame.time.get_ticks()

        # Font และ input box
        input_box = pygame.Rect(WIDTH // 2 - 140, HEIGHT // 2, 280, 50)
        color_inactive = pygame.Color('lightskyblue3')
        color_active = pygame.Color('dodgerblue2')
        color = color_inactive
        title_font = pygame.font.Font('roundfont.ttf', 50)
        input_font = pygame.font.Font('roundfont.ttf', 40)

        active = True
        text = ''
        done = False

        # ปุ่ม Start และ Top 3
        start_button = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 80, 200, 50)
        top_button = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 150, 200, 50)
        button_font = pygame.font.Font('roundfont.ttf', 30)

        blue = (0, 100, 200)
        blue_hover = (0, 130, 255)

        green = (0, 150, 100)
        green_hover = (0, 200, 150)

        while not done:
            current_time = pygame.time.get_ticks()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if input_box.collidepoint(event.pos):
                        active = not active
                    else:
                        active = False
                    color = color_active if active else color_inactive

                    if start_button.collidepoint(event.pos):
                        if text.strip():
                            self.player_name = text
                            done = True

                    if top_button.collidepoint(event.pos):
                        self.show_top_3()

                if event.type == pygame.KEYDOWN:
                    if active:
                        if event.key == pygame.K_RETURN:
                            self.player_name = text
                            done = True
                        elif event.key == pygame.K_BACKSPACE:
                            text = text[:-1]
                        else:
                            text += event.unicode

            # update frame gif
            if current_time - last_update_time > frame_rate:
                frame_index = (frame_index + 1) % len(gif_frames)
                last_update_time = current_time

            self.screen.blit(gif_frames[frame_index], (0, 0))

            # text
            txt_surface = title_font.render("Enter Your Name", True, WHITE)
            name_surface = input_font.render(text, True, color)
            width = max(200, name_surface.get_width() + 10)
            input_box.w = width
            input_box.x = (WIDTH - input_box.w) // 2
            self.screen.blit(txt_surface, (WIDTH // 2 - txt_surface.get_width() // 2, HEIGHT // 2 - 60))
            name_rect = name_surface.get_rect(center=input_box.center)
            name_rect.y += 3
            self.screen.blit(name_surface, name_rect)

            mouse_pos = pygame.mouse.get_pos()

            # เช็กเม้า
            start_color = blue_hover if start_button.collidepoint(mouse_pos) else blue
            top_color = green_hover if top_button.collidepoint(mouse_pos) else green

            pygame.draw.rect(self.screen, start_color, start_button)
            pygame.draw.rect(self.screen, top_color, top_button)

            pygame.draw.rect(self.screen, color, input_box, 2)

            start_text = button_font.render("START", True, WHITE)
            start_text_rect = start_text.get_rect(center=start_button.center)
            self.screen.blit(start_text, start_text_rect)

            top_text = button_font.render("RANK", True, WHITE)
            top_text_rect = top_text.get_rect(center=top_button.center)
            self.screen.blit(top_text, top_text_rect)

            pygame.display.flip()
            self.clock.tick(30)

        self.new_level()

    def show_top_3(self):
        try:
            with open('data/game_data.json', 'r') as f:
                data = json.load(f)
        except:
            print("No game data found.")
            return

        if isinstance(data, dict):
            data = [data]

        top_players = sorted(data, key=lambda x: x.get('total_score', 0), reverse=True)[:3]

        font = pygame.font.Font('roundfont.ttf', 40)
        button_font = pygame.font.Font('roundfont.ttf', 30)

        # เตรียมปุ่ม Back
        back_button = pygame.Rect(WIDTH // 2 - 75, HEIGHT - 100, 150, 50)
        blue = (0, 100, 200)
        blue_hover = (0, 130, 255)

        running = True
        while running:
            self.screen.fill((0, 0, 50))

            # วาด Title
            title = font.render("Top 3 Players", True, WHITE)
            title_rect = title.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 160))
            self.screen.blit(title, title_rect)

            # วาดรายชื่อ
            total_height = len(top_players) * 60
            start_y = (HEIGHT // 2) - (total_height // 2)
            for i, player in enumerate(top_players):
                line = f"{i + 1}. {player['player_name']} - {player['total_score']} pts"
                text_surface = font.render(line, True, (255, 255, 100))
                rect = text_surface.get_rect(center=(WIDTH // 2, start_y + i * 60))
                self.screen.blit(text_surface, rect)

            # วาดปุ่ม Back
            mouse_pos = pygame.mouse.get_pos()
            back_color = blue_hover if back_button.collidepoint(mouse_pos) else blue
            pygame.draw.rect(self.screen, back_color, back_button)
            back_text = button_font.render("BACK", True, WHITE)
            back_text_rect = back_text.get_rect(center=back_button.center)
            self.screen.blit(back_text, back_text_rect)

            pygame.display.flip()

            # รอคลิกที่ปุ่ม
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if back_button.collidepoint(event.pos):
                        running = False

    def new_level(self):
        self.current_enemies = 0
        self.last_spawn_time = time.time()
        self.background_image = self.background_images[self.level]
        self.background_image = pygame.transform.scale(self.background_image, (WIDTH, HEIGHT))

        self.all_sprites = pygame.sprite.Group()
        self.obstacles = pygame.sprite.Group()
        self.gems = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()

        self.map = Map(self, level_maps[self.level])
        self.player = Player(self, (WIDTH // 2, HEIGHT // 2), [self.all_sprites])

        # Reset timers
        self.game_start_time = time.time()
        self.enemy_spawn_timer = 0
        self.start_time = time.time()
        self.enemy_speed = ENEMY_SPEED + (self.level - 1) * 0.1

        # Reset key
        self.has_key = False

    def spawn_enemy(self):
        if self.current_enemies < self.max_enemies:
            from random import choice
            empty_spaces = []

            for row_index, row in enumerate(level_maps[self.level]):
                for col_index, cell in enumerate(row):
                    if cell == '.':
                        x = col_index * TILESIZE + TILESIZE // 2
                        y = row_index * TILESIZE + TILESIZE // 2
                        empty_spaces.append((x, y))

            if empty_spaces:
                spawn_pos = choice(empty_spaces)
                Enemy(self, spawn_pos, [self.all_sprites, self.enemies])
                self.current_enemies += 1  # add enemy

    def events(self):
        self.events_to_process = pygame.event.get()
        for event in self.events_to_process:
            if event.type == pygame.QUIT:
                self.save_game_data('quit')
                pygame.quit()
                sys.exit()

    def run(self):
        while True:
            self.events()
            self.update()
            self.draw()

    def update(self):
        self.all_sprites.update()

        for door_rect in self.map.doors:
            if self.player.rect.colliderect(door_rect):
                if self.has_key:
                    self.level += 1
                    if self.level > 3:
                        self.save_game_data('win')
                        self.game_over("Victory!")
                    else:
                        self.new_level()

        current_time = time.time()
        elapsed_time = current_time - self.game_start_time

        if elapsed_time > self.enemy_spawn_delay:
            if current_time - self.last_spawn_time > self.enemy_spawn_interval:
                self.spawn_enemy()
                self.last_spawn_time = current_time

        for enemy in self.enemies:
            if hasattr(enemy, 'is_dead') and enemy.is_dead:
                self.current_enemies -= 1
                self.score += 5
                enemy.kill()

        # if not self.gems:
        #     if self.level < 3:
        #         self.level += 1
        #         self.new_level()
        #     else:
        #         self.save_game_data('win')
        #         self.game_over('Victory!')

        # Time check
        level_elapsed_time = time.time() - self.start_time
        if level_elapsed_time > self.time_limit:
            self.save_game_data('timeout')
            self.game_over('Time Out!')

    def draw(self):
        self.map.draw(self.screen)
        self.screen.blit(self.background_image, (0, 0))
        self.all_sprites.draw(self.screen)

        fog = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)

        if self.player.flashlight_on:
            fog.fill((30, 30, 30, 200))
        else:
            fog.fill((20, 20, 20, 250))

        if self.player.flashlight_on:
            light_mask = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            light_mask.fill((0, 0,0, 0))

            player_center = self.player.rect.center
            direction = self.player.facing_direction
            beam_length = 150
            cone_width = 25

            angle = math.atan2(-direction.y, direction.x)
            points = [
                player_center,
                (
                    player_center[0] + beam_length * math.cos(angle - math.radians(cone_width / 2)),
                    player_center[1] - beam_length * math.sin(angle - math.radians(cone_width / 2))
                ),
                (
                    player_center[0] + beam_length * math.cos(angle + math.radians(cone_width / 2)),
                    player_center[1] - beam_length * math.sin(angle + math.radians(cone_width / 2))
                )
            ]
            pygame.draw.polygon(light_mask, (255, 240, 180, 60), points)  # เจาะรูแสง

            fog.blit(light_mask, (0, 0))

        self.screen.blit(fog, (0, 0))

        self.draw_ui()
        pygame.display.flip()

    def draw_ui(self):
        # font = pygame.font.Font(None, 36)
        font = pygame.font.Font('roundfont.ttf', 30)
        # Score
        score_text = font.render(f"Score : {self.score}", True, WHITE)
        self.screen.blit(score_text, (10, 10))

        # Time
        time_left = max(0, int(self.time_limit - (time.time() - self.start_time)))
        time_text = font.render(f"Time : {time_left}", True, WHITE)
        self.screen.blit(time_text, (10, 50))

        # Flashlight Status
        flashlight_status = "ON" if self.player.flashlight_on else "OFF"
        flashlight_text = font.render(f"Flashlight : {flashlight_status}", True, WHITE)
        self.screen.blit(flashlight_text, (10, 90))

        # แสดงสถานะกุญแจ
        key_font = pygame.font.Font('roundfont.ttf', 25)
        if self.has_key:
            key_text = key_font.render("Key : YES", True, (0, 255, 0))
        else:
            key_text = key_font.render("Key : NO", True, (255, 0, 0))
        self.screen.blit(key_text, (WIDTH - 125, 10))

    def draw_flashlight(self):
        darkness = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        darkness.fill((40, 40, 40, 160))

        if self.player.flashlight_on:
            player_center = self.player.rect.center
            direction = self.player.facing_direction.normalize()

            light_beam = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)

            cone_width = 25
            beam_length = 150
            angle = math.atan2(-direction.y, direction.x)

            points = [
                player_center,
                (
                    player_center[0] + beam_length * math.cos(angle - math.radians(cone_width / 2)),
                    player_center[1] - beam_length * math.sin(angle - math.radians(cone_width / 2))
                ),
                (
                    player_center[0] + beam_length * math.cos(angle + math.radians(cone_width / 2)),
                    player_center[1] - beam_length * math.sin(angle + math.radians(cone_width / 2))
                )
            ]

            pygame.draw.polygon(light_beam, (255, 200, 100, 150), points)

            darkness.blit(light_beam, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

        self.screen.blit(darkness, (0, 0))

    def game_over(self, message):
        font = pygame.font.Font('roundfont.ttf', 50)
        text = font.render(message, True, WHITE)
        rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        self.screen.fill(BLACK)
        self.screen.blit(text, rect)
        pygame.display.flip()
        pygame.time.delay(3000)
        pygame.quit()
        sys.exit()

    def save_game_data(self, result):
        new_entry = {
            "player_name": self.player_name,
            "levels_completed": self.level,
            "total_score": self.score,
            "game_result": result,
            "date_played": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        }

        file_path = 'data/game_data.json'

        # อ่านข้อมูลเก่า
        try:
            with open(file_path, 'r') as f:
                existing_data = json.load(f)
                if not isinstance(existing_data, list):
                    existing_data = [existing_data]
        except (FileNotFoundError, json.JSONDecodeError):
            existing_data = []

        # เพิ่มข้อมูลใหม่
        existing_data.append(new_entry)

        # บันทึกทั้งหมด
        with open(file_path, 'w') as f:
            json.dump(existing_data, f, indent=4)


if __name__ == "__main__":
    game = Game()
    game.run()
