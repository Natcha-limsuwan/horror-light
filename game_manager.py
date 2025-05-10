import time
import json
import os
import csv


class GameManager:
    def __init__(self, player_name="Unknown"):
        self.player_name = player_name
        self.reset_game()

    def reset_game(self):
        self.start_time = time.time()
        self.flashlight_time = 0
        self.flashlight_on_start = None
        self.ghosts_defeated = 0
        self.gems_collected = 0
        self.deaths = 0
        self.rooms_cleared = 0
        self.keys_collected = 0
        self.level_times = {}

    def update_flashlight_state(self, is_on):
        current_time = time.time()
        if is_on and self.flashlight_on_start is None:
            self.flashlight_on_start = current_time
        elif not is_on and self.flashlight_on_start is not None:
            self.flashlight_time += current_time - self.flashlight_on_start
            self.flashlight_on_start = None

    def add_ghost_defeat(self):
        self.ghosts_defeated += 1

    def add_gem_collected(self):
        self.gems_collected += 1

    def add_death(self):
        self.deaths += 1

    def add_room_cleared(self):
        self.rooms_cleared += 1

    def add_key_collected(self):
        self.keys_collected += 1

    def start_level(self):
        self.level_start_time = time.time()

    def end_level(self, level):
        elapsed = round(time.time() - self.level_start_time, 2)
        self.level_times[str(level)] = elapsed

    def save_stats_final(self, game_result, total_score, levels_completed):
        if self.flashlight_on_start:
            self.flashlight_time += time.time() - self.flashlight_on_start
            self.flashlight_on_start = None
        self.time_elapsed = time.time() - self.start_time

        # ✅ Flatten level_times for CSV
        level_time_fields = [f"level{i + 1}_time" for i in range(levels_completed)]
        level_time_values = [self.level_times.get(str(i + 1), "") for i in range(levels_completed)]

        row = {
            "player_name": self.player_name,
            "levels_completed": levels_completed,
            "total_score": total_score,
            "game_result": game_result,
            "ghosts_defeated": self.ghosts_defeated,
            "date_played": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        }

        for i, t in enumerate(level_time_values):
            row[f"level{i + 1}_time"] = t

        # ✅ File path
        os.makedirs("data", exist_ok=True)
        filename = "data/game_data.csv"

        file_exists = os.path.isfile(filename)

        # ✅ Write to CSV
        with open(filename, "a", newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=row.keys())

            if not file_exists:
                writer.writeheader()

            writer.writerow(row)
