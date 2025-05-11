import time
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
        self.level_start_time = time.time()

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
        # Finalize all stats
        if self.flashlight_on_start:
            self.flashlight_time += time.time() - self.flashlight_on_start
            self.flashlight_on_start = None

        # Initialize stats with basic information
        stats = {
            "Player Name": self.player_name,
            "Levels Completed": levels_completed,
            "Total Score": total_score,
            "Game Result": game_result,
            "Ghosts Defeated": self.ghosts_defeated
        }

        # Calculate total time from completed levels only
        total_time = 0.0
        for level in range(1, levels_completed + 1):
            level_time = self.level_times.get(str(level), 0)
            stats[f"Level {level} Time"] = level_time
            if level_time != "N/A":
                total_time += float(level_time)

        # Add the calculated total time
        stats["Total Time"] = round(total_time, 2)

        # Fill in N/A for levels not completed
        for level in range(levels_completed + 1, 4):
            stats[f"Level {level} Time"] = "N/A"

        self.save_to_csv(stats)

    def save_to_csv(self, stats):
        file_path = 'data/game_data.csv'
        os.makedirs("data", exist_ok=True)

        # Define all possible fieldnames
        fieldnames = [
            "Player Name",
            "Levels Completed",
            "Total Score",
            "Game Result",
            "Ghosts Defeated",
            "Total Time",
            "Level 1 Time",
            "Level 2 Time",
            "Level 3 Time"
        ]

        # Check if file exists to determine if we need headers
        file_exists = os.path.isfile(file_path)

        with open(file_path, 'a', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)

            if not file_exists:
                writer.writeheader()

            # Ensure all fields are present in stats
            for field in fieldnames:
                if field not in stats:
                    stats[field] = "N/A"

            writer.writerow(stats)
