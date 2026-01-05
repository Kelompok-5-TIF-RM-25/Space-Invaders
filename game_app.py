"""Main game application managing rendering and game loop."""
import curses
import time
from typing import Optional, List
from game_core import GameCore
from game_state import GameState
from alien_system import AlienSystem
from entities import Player, Bullet
from sprites import SPRITES, ALIEN_INTRO, sprite_size


class GameApp:
    """Main game application class handling rendering and game loop."""
    
    def __init__(self):
        self.game = GameCore()
        self.stdscr = None

        self.last_time = time.time()

        self.aliens: Optional[AlienSystem] = None
        self.player: Optional[Player] = None

        self.bullet_limit = 3
        self.fire_rate = 0.25

        self.player_frames = SPRITES["player"]
        self.player_w, self.player_h = sprite_size(self.player_frames[0])

    def setup_curses(self, stdscr):
        """Setup curses terminal configuration.
        
        Args:
            stdscr: Curses standard screen object
        """
        self.stdscr = stdscr
        curses.curs_set(0)
        stdscr.nodelay(True)
        stdscr.timeout(50)
        stdscr.keypad(True)

    def safe_addstr(self, y: int, x: int, text: str, attr: int = 0):
        """Safely add string to screen with bounds checking.
        
        Args:
            y: Y coordinate
            x: X coordinate
            text: Text to display
            attr: Text attributes
        """
        h, w = self.stdscr.getmaxyx()
        if y < 0 or y >= h:
            return
        if x < 0:
            text = text[-x:]
            x = 0
        if x >= w:
            return
        text = text[: max(0, w - x)]
        if not text:
            return
        try:
            self.stdscr.addstr(y, x, text, attr)
        except curses.error:
            pass

    def draw_sprite(self, y: int, x: int, sprite_lines: List[str], attr: int = 0):
        """Draw a multi-line sprite.
        
        Args:
            y: Y coordinate
            x: X coordinate
            sprite_lines: List of sprite line strings
            attr: Text attributes
        """
        for i, line in enumerate(sprite_lines):
            self.safe_addstr(y + i, x, line, attr)

    def key_to_text(self, k: int) -> str:
        """Convert curses key code to text character.
        
        Args:
            k: Curses key code
            
        Returns:
            Character string or empty string
        """
        if k == -1:
            return ""
        if k == 32:
            return " "
        if 97 <= k <= 122 or 65 <= k <= 90:
            return chr(k)
        return ""

    def on_enter_play(self):
        """Initialize game entities when entering play state."""
        h, w = self.stdscr.getmaxyx()
        if self.aliens is None:
            self.aliens = AlienSystem(w)
        else:
            self.aliens.spawn()

        px = max(1, (w - self.player_w) // 2)
        py = max(1, h - self.player_h - 1)

        self.player = Player(
            x=px,
            y=py,
            bullets=[]
        )

    def poll_input(self):
        """Poll for keyboard input and handle player controls."""
        k = self.stdscr.getch()
        key = self.key_to_text(k)

        # Handle global shortcuts
        if key:
            prev = self.game.state
            self.game.handle_input(key)

            # Spawn world when transitioning to PLAY state
            if prev != GameState.PLAY and self.game.state == GameState.PLAY:
                self.on_enter_play()

        # Player controls
        if self.game.state == GameState.PLAY and self.player:
            h, w = self.stdscr.getmaxyx()

            if k == curses.KEY_LEFT or (key and key.lower() == "a"):
                self.player.x -= 2
            elif k == curses.KEY_RIGHT or (key and key.lower() == "d"):
                self.player.x += 2
            elif key == " ":
                self.try_fire()

            self.player.x = max(1, min(self.player.x, w - self.player_w - 1))

    def update(self):
        """Update game state each frame."""
        now = time.time()
        dt = now - self.last_time
        self.last_time = now

        aliens_dead = False
        if self.game.state == GameState.PLAY and self.aliens and len(self.aliens.aliens) > 0:
            if not any(a.alive for a in self.aliens.aliens):
                aliens_dead = True

        # Check if we just entered PLAY from WIN (next level triggered)
        prev_state = getattr(self, '_prev_state', None)
        if self.game.state == GameState.PLAY and prev_state == GameState.WIN:
            # Respawn aliens for new level
            if self.aliens:
                self.aliens.spawn()
        
        self._prev_state = self.game.state

        self.game.update(aliens_dead)

        if self.game.state == GameState.PLAY:
            self.update_play(dt)

    def update_play(self, dt: float):
        """Update game entities during play state.
        
        Args:
            dt: Delta time since last frame
        """
        h, w = self.stdscr.getmaxyx()

        if self.aliens:
            self.aliens.update(self.game.level, dt, w, h)

        for b in self.player.bullets:
            if b.active:
                b.y -= 1
                if b.y <= 0:
                    b.active = False

        self.check_collisions()

        self.player.bullets = [b for b in self.player.bullets if b.active]

    def try_fire(self):
        """Attempt to fire a bullet from player ship."""
        now = time.time()
        if len(self.player.bullets) >= self.bullet_limit:
            return
        if now - self.player.last_fire_time < self.fire_rate:
            return

        bx = self.player.x + (self.player_w // 2)
        by = self.player.y - 1

        self.player.bullets.append(Bullet(bx, by))
        self.player.last_fire_time = now

    def render(self):
        """Render current game state."""
        if self.game.state == GameState.INTRO:
            self.render_intro()
        elif self.game.state == GameState.PLAY:
            self.render_play()
        elif self.game.state in (GameState.WIN, GameState.GAMEOVER):
            self.render_end()

        self.stdscr.refresh()

    def render_intro(self):
        """Render intro screen."""
        self.stdscr.clear()
        h, w = self.stdscr.getmaxyx()

        title = "ASCII SPACE INVADERS"
        if (self.game.frame // 15) % 2 == 0:
            self.safe_addstr(h // 2 - 8, (w - len(title)) // 2, title, curses.A_BOLD)

        ax = w // 2 - len(ALIEN_INTRO[0]) // 2
        for i, line in enumerate(ALIEN_INTRO):
            y = self.game.alien_y + i
            if 0 <= y < h:
                self.safe_addstr(y, ax, line)

        if self.game.alien_y > h:
            self.game.alien_y = -len(ALIEN_INTRO)

        menu = [
            "SPACE : Start Game",
            "L     : Load Game" if self.game.has_save else "L     : Load Game (N/A)",
            "Q     : Quit",
            "",
            "During game: S = Save | L = Load | Q = Quit",
        ]
        my = h // 2
        for i, item in enumerate(menu):
            self.safe_addstr(my + i, (w - len(item)) // 2, item)

        status = self.game.get_status()
        if status:
            self.safe_addstr(h - 2, (w - len(status)) // 2, status, curses.A_BOLD)

    def render_play(self):
        """Render gameplay screen."""
        self.stdscr.clear()

        if not self.aliens or not self.player:
            return

        frame_idx = (self.game.frame // 6) % 2
        wobble = 0 if (self.game.frame // 3) % 2 == 0 else 1

        # Render aliens
        for a in self.aliens.aliens:
            if not a.alive:
                continue
            sprite_frames = SPRITES.get(a.kind, SPRITES["alien10"])
            sprite = sprite_frames[frame_idx]
            for i, line in enumerate(sprite):
                self.safe_addstr(a.y + i, a.x + wobble, line)

        # Render bombs
        for b in self.aliens.bombs:
            if b.active:
                char = "|" if (self.game.frame % 2 == 0) else "!"
                self.safe_addstr(b.y, b.x, char)

        # Render mystery ship
        if self.aliens.mystery.active:
            self.safe_addstr(self.aliens.mystery.y, self.aliens.mystery.x, "_/MMM\\_")

        # Render player
        ship_sprite = self.player_frames[frame_idx]
        self.draw_sprite(self.player.y, self.player.x, ship_sprite)

        # Render bullets
        for b in self.player.bullets:
            self.safe_addstr(b.y, b.x, "!")

        # Render HUD
        info = (
            f"SCORE: {self.game.score} | LIVES: {self.game.lives} | "
            f"LEVEL: {self.game.level} | TIME: {max(0,int(self.game.time_left))}s"
        )
        self.safe_addstr(0, 0, info)

        hint = "S=Save  L=Load  Q=Quit"
        self.safe_addstr(1, 0, hint)

        status = self.game.get_status()
        if status:
            self.safe_addstr(2, 0, status, curses.A_BOLD)

    def render_end(self):
        """Render game over / win screen."""
        self.stdscr.clear()
        h, w = self.stdscr.getmaxyx()

        text = "YOU WIN!" if self.game.state == GameState.WIN else "GAME OVER"
        self.safe_addstr(h // 2 - 2, (w - len(text)) // 2, text, curses.A_BOLD)

        if self.game.state == GameState.WIN:
            self.safe_addstr(h // 2, (w - 20) // 2, "N : Next Level")
            self.safe_addstr(h // 2 + 1, (w - 10) // 2, "S : Save")
            self.safe_addstr(h // 2 + 2, (w - 10) // 2, "Q : Quit")
        else:
            self.safe_addstr(h // 2, (w - 28) // 2, "SPACE : Restart")
            self.safe_addstr(h // 2 + 1, (w - 10) // 2, "Q : Quit")
            self.safe_addstr(h // 2 + 2, (w - 18) // 2, "S : Save  L : Load")

        status = self.game.get_status()
        if status:
            self.safe_addstr(h - 2, (w - len(status)) // 2, status, curses.A_BOLD)

    def check_collisions(self):
        """Check and handle collisions between game entities."""
        if not self.player or not self.aliens:
            return

        # BULLET vs ALIEN
        for bullet in self.player.bullets:
            if not bullet.active:
                continue
            for alien in self.aliens.aliens:
                if not alien.alive:
                    continue
                if (alien.x <= bullet.x < alien.x + 6) and (alien.y <= bullet.y <= alien.y + 1):
                    alien.alive = False
                    bullet.active = False

                    if alien.kind == "alien30":
                        self.game.score += 30
                    elif alien.kind == "alien20":
                        self.game.score += 20
                    else:
                        self.game.score += 10
                    break

        # BOMB vs PLAYER
        px1 = self.player.x
        py1 = self.player.y
        px2 = self.player.x + self.player_w - 1
        py2 = self.player.y + self.player_h - 1

        h, w = self.stdscr.getmaxyx()

        for bomb in self.aliens.bombs:
            if not bomb.active:
                continue
            if (px1 <= bomb.x <= px2) and (py1 <= bomb.y <= py2):
                bomb.active = False
                self.game.lives -= 1

                self.player.x = max(1, (w - self.player_w) // 2)

                try:
                    curses.beep()
                    curses.flash()
                except Exception:
                    pass

    def run(self, stdscr):
        """Main game loop.
        
        Args:
            stdscr: Curses standard screen object
        """
        self.setup_curses(stdscr)
        self.last_time = time.time()

        while self.game.running:
            self.poll_input()
            self.update()
            self.render()
            time.sleep(0.03)
