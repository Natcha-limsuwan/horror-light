import csv
from map import level_maps
from sprites import *
from player import Player
from PIL import Image
from game_manager import GameManager
from graph_generator import *
import sys


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
        self.enemy_spawn_delay = 3
        self.enemy_spawn_timer = 0
        self.enemy_spawn_interval = 3
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

        # Font and input box
        border_color_inactive = pygame.Color('lightskyblue3')
        border_color_active = pygame.Color('dodgerblue2')
        input_box = pygame.Rect(WIDTH // 2 - 140, HEIGHT // 2, 280, 50)
        text_color_active = (200, 200, 200)
        text_color_inactive = (255, 255, 255)
        title_font = pygame.font.Font('roundfont.ttf', 50)
        input_font = pygame.font.Font('roundfont.ttf', 40)

        active = True  # Input box active
        border_color = border_color_active
        text = ''
        done = False

        # Buttons - Start, Rank, Stats
        start_button = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 80, 200, 50)
        top_button = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 150, 200, 50)
        stats_button = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 220, 200, 50)
        button_font = pygame.font.Font('roundfont.ttf', 30)

        start_base = (0, 100, 200)
        start_hover = (0, 130, 255)
        rank_base = (0, 150, 100)
        rank_hover = (0, 200, 150)
        stats_base = (150, 0, 150)
        stats_hover = (200, 0, 200)

        while not done:
            current_time = pygame.time.get_ticks()
            mouse_pos = pygame.mouse.get_pos()

            current_text_color = text_color_active if active else text_color_inactive

            # Update GIF animation
            if current_time - last_update_time > frame_rate:
                frame_index = (frame_index + 1) % len(gif_frames)
                last_update_time = current_time

            # Draw background
            self.screen.blit(gif_frames[frame_index], (0, 0))

            # Draw title
            title_text = title_font.render("Enter Your Name", True, WHITE)
            self.screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, HEIGHT // 2 - 60))

            # Draw input box - using the renamed border_color
            pygame.draw.rect(self.screen, border_color, input_box, 2)
            name_surface = input_font.render(text, True, current_text_color)
            input_box.w = max(200, name_surface.get_width() + 10)
            input_box.x = WIDTH // 2 - input_box.w // 2
            text_x = input_box.x + (input_box.w - name_surface.get_width()) // 2
            text_y = input_box.y + (input_box.h - name_surface.get_height()) // 2
            self.screen.blit(name_surface, (text_x, text_y))

            # Event handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                # Mouse click handling
                if event.type == pygame.MOUSEBUTTONDOWN:
                    # Input box focus
                    if input_box.collidepoint(event.pos):
                        active = True
                    else:
                        active = False
                    border_color = border_color_active if active else border_color_inactive

                    # Button clicks
                    if start_button.collidepoint(event.pos) and text.strip():
                        self.player_name = text
                        self.manager = GameManager(self.player_name)
                        done = True

                    if top_button.collidepoint(event.pos):
                        self.show_top_3()

                    if stats_button.collidepoint(event.pos):
                        self.show_statistics()

                # Keyboard input
                if event.type == pygame.KEYDOWN:
                    if active:
                        if event.key == pygame.K_RETURN and text.strip():
                            self.player_name = text
                            self.manager = GameManager(self.player_name)
                            done = True
                        elif event.key == pygame.K_BACKSPACE:
                            text = text[:-1]
                        else:
                            text += event.unicode

            buttons = [
                (start_button, start_base, start_hover, "START"),
                (top_button, rank_base, rank_hover, "RANK"),
                (stats_button, stats_base, stats_hover, "STATS")
            ]

            for rect, base_color, hover_color, label in buttons:
                btn_color = hover_color if rect.collidepoint(mouse_pos) else base_color
                pygame.draw.rect(self.screen, btn_color, rect, border_radius=5)
                label_text = button_font.render(label, True, WHITE)
                self.screen.blit(label_text, (
                    rect.centerx - label_text.get_width() // 2,
                    rect.centery - label_text.get_height() // 2
                ))

            pygame.display.flip()
            self.clock.tick(30)

        self.new_level()

    def show_top_3(self):
        file_path = 'data/game_data.csv'

        if not os.path.isfile(file_path):
            print("No game data found")
            return

        try:
            with open(file_path, 'r', newline='') as f:
                reader = csv.DictReader(f)
                reader.fieldnames = [name.lower().replace(' ', '_') for name in reader.fieldnames]
                data = list(reader)

            if not data:
                print("CSV file is empty")
                return

            # Sort by total_score (now lowercase)
            top_players = sorted(data, key=lambda x: int(x.get('total_score', 0)), reverse=True)[:3]

            font = pygame.font.Font('roundfont.ttf', 40)
            button_font = pygame.font.Font('roundfont.ttf', 30)

            back_button = pygame.Rect(WIDTH // 2 - 75, HEIGHT - 100, 150, 50)
            blue = (0, 100, 200)
            blue_hover = (0, 130, 255)

            running = True
            while running:
                self.screen.fill((0, 0, 50))

                # Title
                title = font.render("Top 3 Players", True, WHITE)
                title_rect = title.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 160))
                self.screen.blit(title, title_rect)

                # Player scores - use lowercase field names
                total_height = len(top_players) * 60
                start_y = (HEIGHT // 2) - (total_height // 2)
                for i, player in enumerate(top_players):
                    line = f"{i + 1}. {player['player_name']} - {player['total_score']} pts"
                    text_surface = font.render(line, True, (255, 255, 100))
                    rect = text_surface.get_rect(center=(WIDTH // 2, start_y + i * 60))
                    self.screen.blit(text_surface, rect)

                # Back button
                mouse_pos = pygame.mouse.get_pos()
                back_color = blue_hover if back_button.collidepoint(mouse_pos) else blue
                pygame.draw.rect(self.screen, back_color, back_button)
                back_text = button_font.render("BACK", True, WHITE)
                back_text_rect = back_text.get_rect(center=back_button.center)
                self.screen.blit(back_text, back_text_rect)
                pygame.display.flip()

                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if back_button.collidepoint(event.pos):
                            running = False

        except Exception as e:
            print(f"Error loading top players: {e}")

    def show_statistics(self):
        self.generate_all_stat_graphs()

        graphs = [
            {'file': 'game_results_pie.png', 'title': 'Game Result'},
            {'file': 'levels_completed_frequency.png', 'title': 'Level Completion'},
            {'file': 'progress_times_boxplot.png', 'title': 'Completion Times'},
            {'file': 'time_stats_table.png', 'title': 'Time Statistics'},
            {'file': 'correlation_matrix.png', 'title': 'Metrics Correlation'}
        ]

        # Load graph images
        loaded_graphs = []
        for graph in graphs:
            try:
                img = pygame.image.load(f'data/stats/{graph["file"]}')
                if img.get_width() > WIDTH * 0.9 or img.get_height() > HEIGHT * 0.7:
                    scale_factor = min(
                        (WIDTH * 0.9) / img.get_width(),
                        (HEIGHT * 0.7) / img.get_height()
                    )
                    img = pygame.transform.scale(img,
                                                 (int(img.get_width() * scale_factor),
                                                  int(img.get_height() * scale_factor)))
                    loaded_graphs.append({
                        'image': img,
                        'title': graph['title']
                    })

            except:
                print(f"Failed to load graph: {graph['file']}")
                loaded_graphs.append(None)

        # Filter out
        valid_graphs = [g for g in loaded_graphs if g is not None]
        if not valid_graphs:
            self.show_error_message("No statistics available")
            return

        # Button setup
        button_font = pygame.font.Font('roundfont.ttf', 30)
        nav_button_width = 150
        nav_button_height = 50

        # Back button
        back_button = pygame.Rect(
            20, HEIGHT - 70,
            nav_button_width, nav_button_height
        )

        # Navigation buttons
        prev_button = pygame.Rect(
            WIDTH // 2 - nav_button_width - 10, HEIGHT - 70,
            nav_button_width, nav_button_height
        )
        next_button = pygame.Rect(
            WIDTH // 2 + 10, HEIGHT - 70,
            nav_button_width, nav_button_height
        )

        current_graph = 0
        running = True

        while running:
            self.screen.fill((0, 0, 50))  # Dark blue background

            # Display current graph
            graph = valid_graphs[current_graph]
            graph_rect = graph['image'].get_rect(center=(WIDTH // 2, HEIGHT // 2 - 30))
            self.screen.blit(graph['image'], graph_rect)

            # Title
            title_font = pygame.font.Font('roundfont.ttf', 40)
            title = title_font.render(graph['title'], True, (255, 255, 200))
            title_rect = title.get_rect(center=(WIDTH // 2, 50))
            self.screen.blit(title, title_rect)

            # Page indicator
            page_font = pygame.font.Font('roundfont.ttf', 25)
            page_text = page_font.render(
                f"Graph {current_graph + 1} of {len(valid_graphs)}",
                True, WHITE
            )
            page_rect = page_text.get_rect(center=(WIDTH // 2, HEIGHT - 95))
            self.screen.blit(page_text, page_rect)

            # Draw buttons
            mouse_pos = pygame.mouse.get_pos()

            # Back button
            back_color = (200, 0, 0) if back_button.collidepoint(mouse_pos) else (150, 0, 0)
            pygame.draw.rect(self.screen, back_color, back_button, border_radius=5)
            back_text = button_font.render("BACK", True, WHITE)
            self.screen.blit(back_text, (
                back_button.centerx - back_text.get_width() // 2,
                back_button.centery - back_text.get_height() // 2
            ))

            if len(valid_graphs) > 1:
                # Previous button
                prev_color = (0, 100, 200) if prev_button.collidepoint(mouse_pos) else (0, 70, 150)
                pygame.draw.rect(self.screen, prev_color, prev_button, border_radius=5)
                prev_text = button_font.render("<", True, WHITE)
                self.screen.blit(prev_text, (
                    prev_button.centerx - prev_text.get_width() // 2,
                    prev_button.centery - prev_text.get_height() // 2
                ))

                # Next button
                next_color = (0, 100, 200) if next_button.collidepoint(mouse_pos) else (0, 70, 150)
                pygame.draw.rect(self.screen, next_color, next_button, border_radius=5)
                next_text = button_font.render(">", True, WHITE)
                self.screen.blit(next_text, (
                    next_button.centerx - next_text.get_width() // 2,
                    next_button.centery - next_text.get_height() // 2
                ))

            pygame.display.flip()

            # Event handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if back_button.collidepoint(event.pos):
                        running = False

                    # Navigation
                    if len(valid_graphs) > 1:
                        if prev_button.collidepoint(event.pos):
                            current_graph = (current_graph - 1) % len(valid_graphs)
                        elif next_button.collidepoint(event.pos):
                            current_graph = (current_graph + 1) % len(valid_graphs)

            self.clock.tick(60)

    def show_error_message(self, message):
        """Show an error message screen"""
        error_font = pygame.font.Font('roundfont.ttf', 40)
        button_font = pygame.font.Font('roundfont.ttf', 30)

        error_text = error_font.render(message, True, (255, 0, 0))
        error_rect = error_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))

        back_button = pygame.Rect(
            WIDTH // 2 - 100, HEIGHT // 2 + 60,
            200, 50
        )

        running = True
        while running:
            self.screen.fill((0, 0, 50))
            self.screen.blit(error_text, error_rect)

            # Draw back button
            mouse_pos = pygame.mouse.get_pos()
            back_color = (0, 100, 200) if back_button.collidepoint(mouse_pos) else (0, 70, 150)
            pygame.draw.rect(self.screen, back_color, back_button, border_radius=5)
            back_text = button_font.render(">", True, WHITE)
            self.screen.blit(back_text, (
                back_button.centerx - back_text.get_width() // 2,
                back_button.centery - back_text.get_height() // 2
            ))

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if back_button.collidepoint(event.pos):
                        running = False

            self.clock.tick(60)

    def generate_all_stat_graphs(self):
        """Generate all statistical graphs by calling the graph generator"""
        try:
            # Create stats directory if it doesn't exist
            os.makedirs('data/stats', exist_ok=True)

            # Call the function to generate all graphs
            generate_all_stats()

        except Exception as e:
            print(f"Error generating statistics: {e}")
            self.show_error_message("Failed to generate statistics")

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

        self.game_start_time = time.time()
        self.enemy_spawn_timer = 0
        self.start_time = time.time()
        self.enemy_speed = ENEMY_SPEED + (self.level - 1) * 0.1
        self.has_key = False

        self.manager.start_level()

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
                self.current_enemies += 1

    def events(self):
        self.events_to_process = pygame.event.get()
        for event in self.events_to_process:
            if event.type == pygame.QUIT:
                stats = {
                    "Player Name": self.player_name,
                    "Levels Completed": self.level,
                    "Total Score": self.score,
                    "Game Result": "quit",
                    "Ghosts Defeated": self.manager.ghosts_defeated,
                    "Total Time": round(time.time() - self.manager.start_time, 2)
                }
                # Add level times
                for level in range(1, self.level + 1):
                    stats[f"Level {level} Time"] = self.manager.level_times.get(str(level), "N/A")
                for level in range(self.level + 1, 4):
                    stats[f"Level {level} Time"] = "N/A"

                self.manager.save_to_csv(stats)
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    stats = {
                        "Player Name": self.player_name,
                        "Levels Completed": self.level,
                        "Total Score": self.score,
                        "Game Result": "quit",
                        "Ghosts Defeated": self.manager.ghosts_defeated,
                        "Total Time": round(time.time() - self.manager.start_time, 2)
                    }
                    # Add level times
                    for level in range(1, self.level + 1):
                        stats[f"Level {level} Time"] = self.manager.level_times.get(str(level), "N/A")
                    # Fill remaining levels with N/A
                    for level in range(self.level + 1, 4):
                        stats[f"Level {level} Time"] = "N/A"

                    self.manager.save_to_csv(stats)
                    pygame.quit()
                    sys.exit()

    def run(self):
        self.game_start_time = time.time()
        while True:
            self.events()
            self.update()
            self.draw()

    def update(self):
        self.all_sprites.update()

        # Handle door collisions and level completion
        for door_rect in self.map.doors:
            if self.player.rect.colliderect(door_rect):
                if self.has_key:
                    self.manager.end_level(self.level)
                    if self.level >= 3:
                        self.manager.save_stats_final("win", self.score, self.level)
                        self.game_over("Victory!")
                    else:
                        self.level += 1
                        self.new_level()

        # Handle enemy spawning
        current_time = time.time()
        if current_time - self.last_spawn_time > self.enemy_spawn_interval and self.current_enemies < self.max_enemies:
            self.spawn_enemy()
            self.last_spawn_time = current_time

        # Handle enemy deaths
        for enemy in self.enemies:
            if hasattr(enemy, 'is_dead') and enemy.is_dead:
                self.current_enemies -= 1
                self.score += 5
                self.manager.add_ghost_defeat()
                enemy.kill()

        # Handle time limit
        level_elapsed_time = time.time() - self.start_time
        if level_elapsed_time > self.time_limit:
            # Create stats before game over
            stats = {
                "Player Name": self.player_name,
                "Levels Completed": self.level,
                "Total Score": self.score,
                "Game Result": "timeout",
                "Ghosts Defeated": self.manager.ghosts_defeated,
                "Total Time": round(time.time() - self.manager.start_time, 2)
            }
            # Add level times
            for level in range(1, self.level + 1):
                stats[f"Level {level} Time"] = self.manager.level_times.get(str(level), "N/A")
            # Fill remaining levels with N/A
            for level in range(self.level + 1, 4):
                stats[f"Level {level} Time"] = "N/A"

            self.manager.save_to_csv(stats)
            self.game_over("Time Out!")

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
            light_mask.fill((0, 0, 0, 0))

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


if __name__ == "__main__":
    game = Game()
    game.run()
