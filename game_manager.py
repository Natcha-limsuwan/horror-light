
import time
import json
import os

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

    def end_game(self):
        if self.flashlight_on_start:
            self.flashlight_time += time.time() - self.flashlight_on_start
            self.flashlight_on_start = None
        self.time_elapsed = time.time() - self.start_time
        self.save_stats()

    def save_stats(self):
        stats = {
            "player": self.player_name,
            "time_elapsed": round(self.time_elapsed, 2),
            "flashlight_usage": round(self.flashlight_time, 2),
            "ghosts_defeated": self.ghosts_defeated,
            "gems_collected": self.gems_collected,
            "deaths": self.deaths,
            "rooms_cleared": self.rooms_cleared,
            "keys_collected": self.keys_collected
        }

        os.makedirs("data", exist_ok=True)
        filename = f"data/{self.player_name}_stats.json"
        with open(filename, "w") as f:
            json.dump(stats, f, indent=4)
