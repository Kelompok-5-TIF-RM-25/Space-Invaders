"""Core game logic and state management."""
import os
import json
import time
from game_state import GameState


class GameCore:
    """Core game logic managing score, lives, level, and game state."""
    
    def __init__(self):
        self.state = GameState.INTRO
        self.running = True

        self.score = 0
        self.lives = 3
        self.level = 1

        self.frame = 0
        self.alien_y = -5

        # Timer
        self.time_limit = 60
        self.time_left = self.time_limit
        self.last_time = time.time()

        # Save
        self.save_path = "save.json"
        self.has_save = os.path.exists(self.save_path)
        self.last_status_msg = ""
        self.last_status_ts = 0.0

    def set_status(self, msg: str, ttl: float = 1.5):
        """Set a status message to display temporarily.
        
        Args:
            msg: Message to display
            ttl: Time to live in seconds
        """
        self.last_status_msg = msg
        self.last_status_ts = time.time() + ttl

    def get_status(self) -> str:
        """Get current status message if still active.
        
        Returns:
            Status message or empty string if expired
        """
        if not self.last_status_msg:
            return ""
        if time.time() > self.last_status_ts:
            self.last_status_msg = ""
            return ""
        return self.last_status_msg

    def reset_timer(self):
        """Reset the game timer to initial value."""
        self.time_left = self.time_limit
        self.last_time = time.time()

    def update_timer(self):
        """Update timer and check if time has run out."""
        now = time.time()
        elapsed_time = now - self.last_time
        self.time_left -= elapsed_time
        self.last_time = now
        if self.time_left <= 0:
            self.state = GameState.GAMEOVER

    def start_game(self):
        """Start a new game with default values."""
        self.score = 0
        self.lives = 3
        self.level = 1
        self.state = GameState.PLAY
        self.reset_timer()

    def save_game(self) -> bool:
        """Save current game state to JSON file.
        
        Returns:
            True if save successful, False otherwise
        """
        payload = {
            "version": 1,
            "saved_at": int(time.time()),
            "score": int(self.score),
            "lives": int(self.lives),
            "level": int(self.level),
            "time_left": float(max(0.0, self.time_left)),
        }
        try:
            with open(self.save_path, "w", encoding="utf-8") as f:
                json.dump(payload, f, ensure_ascii=False, indent=2)
            self.has_save = True
            self.set_status("Saved ✓")
            return True
        except Exception as e:
            self.set_status(f"Save failed: {e}")
            return False

    def load_game(self) -> bool:
        """Load game state from JSON file.
        
        Returns:
            True if load successful, False otherwise
        """
        if not os.path.exists(self.save_path):
            self.has_save = False
            self.set_status("No save file")
            return False

        try:
            with open(self.save_path, "r", encoding="utf-8") as f:
                payload = json.load(f)

            self.score = int(payload.get("score", 0))
            self.lives = int(payload.get("lives", 3))
            self.level = int(payload.get("level", 1))

            tl = payload.get("time_left", self.time_limit)
            try:
                self.time_left = float(tl)
            except Exception:
                self.time_left = float(self.time_limit)

            self.last_time = time.time()
            self.state = GameState.PLAY
            self.has_save = True
            self.set_status("Loaded ✓")
            return True
        except Exception as e:
            self.set_status(f"Load failed: {e}")
            return False

    def quit(self):
        """Quit the game."""
        self.state = GameState.EXIT
        self.running = False

    def handle_input(self, key: str):
        """Handle keyboard input based on current game state.
        
        Args:
            key: Input key character
        """
        k = key.lower()

        if self.state == GameState.INTRO:
            if key == " ":
                self.start_game()
            elif k == "l":
                self.load_game()
            elif k == "q":
                self.quit()

        elif self.state == GameState.PLAY:
            if k == "q":
                self.quit()
            elif k == "s":
                self.save_game()
            elif k == "l":
                self.load_game()

        elif self.state in (GameState.WIN, GameState.GAMEOVER):
            if key == " ":
                self.start_game()
            elif k == "q":
                self.quit()
            elif k == "s":
                self.save_game()
            elif k == "l":
                self.load_game()

    def update(self, all_aliens_dead: bool):
        """Update game logic each frame.
        
        Args:
            all_aliens_dead: Whether all aliens have been destroyed
        """
        self.frame += 1

        if self.state == GameState.PLAY:
            self.update_timer()

            if self.time_left <= 0 and not all_aliens_dead:
                self.state = GameState.GAMEOVER

            if all_aliens_dead:
                self.state = GameState.WIN

            if self.lives <= 0:
                self.state = GameState.GAMEOVER

        elif self.state == GameState.INTRO:
            if self.frame % 2 == 0:
                self.alien_y += 1
