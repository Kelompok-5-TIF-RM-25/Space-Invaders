#!/usr/bin/env python3
"""
ASCII Space Invaders - Python version
Based on ascii-invaders by Thomas Munro
A curses-based Space Invaders game with ASCII art
"""

import curses
import time
import random
import json
import os
from enum import IntEnum

class GameState(IntEnum):
    INTRO = 1
    PLAY = 2
    EXPLODE = 3
    WAIT = 4
    GAMEOVER = 5
    PAUSED = 6

# ASCII Sprites
SPRITES = {
    'alien30_1': [
        " {@@} ",
        " /\"\"\\ ",
        "      "
    ],
    'alien30_2': [
        " {@@} ",
        "  \\/  ",
        "      "
    ],
    'alien20_1': [
        " dOOb ",
        " ^/\\^ ",
        "      "
    ],
    'alien20_2': [
        " dOOb ",
        " ~||~ ",
        "      "
    ],
    'alien10_1': [
        " /MM\\ ",
        " |~~| ",
        "      "
    ],
    'alien10_2': [
        " /MM\\ ",
        " \\~~/ ",
        "      "
    ],
    'mystery': [
        "_/MMM\\_",
        "qWAVAWp"
    ],
    'gunner': [
        "  mAm  ",
        " MAZAM "
    ],
    'gunner_explode': [
        " ,' %  ",
        " ;&+,! "
    ],
    'alien_explode': [
        " \\||/ ",
        " /||\\ ",
        "      "
    ],
    'shelter': [
        "/MMMMM\\",
        "MMMMMMM",
        "MMM MMM"
    ]
}

BOMB_CHARS = "\\|/-"

class Bullet:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.active = True

class Bomb:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.anim = 0
        self.active = True

class Alien:
    def __init__(self, alien_type, x, y):
        self.type = alien_type  # 10, 20, or 30 points
        self.x = x
        self.y = y
        self.frame = 0
        self.alive = True
        self.explode_counter = 0

class Gunner:
    def __init__(self, x):
        self.x = x
        self.lives = 3
        self.exploding = False
        self.explode_counter = 0

class Shelter:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.health = [[True for _ in range(7)] for _ in range(3)]

class Game:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.height, self.width = stdscr.getmaxyx()
        self.score = 0
        self.level = 1
        self.state = GameState.INTRO
        self.frame = 0
        self.save_file = 'space_invaders_save.json'
        
        # Game objects
        self.gunner = Gunner(self.width // 2)
        self.aliens = []
        self.shelters = []
        self.bullets = []
        self.bombs = []
        self.mystery_ship = None
        self.mystery_active = False
        
        # Alien movement
        self.alien_direction = 1
        self.alien_speed = 0
        self.alien_drop = False
        
        # Setup curses
        curses.curs_set(0)
        stdscr.nodelay(1)
        stdscr.timeout(50)
        
        # Colors
        if curses.has_colors():
            curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
            curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
            curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)
            curses.init_pair(4, curses.COLOR_CYAN, curses.COLOR_BLACK)
            curses.init_pair(5, curses.COLOR_WHITE, curses.COLOR_BLACK)
    
    def setup_game(self):
        """Initialize game objects"""
        self.aliens = []
        self.bullets = []
        self.bombs = []
        self.mystery_ship = None
        self.mystery_active = False
        
        # Create aliens (5 rows of 11 aliens)
        alien_types = [30, 30, 20, 20, 10]
        start_x = 5
        start_y = 3
        
        for row in range(5):
            for col in range(11):
                x = start_x + col * 7
                y = start_y + row * 4
                if x < self.width - 10:
                    alien = Alien(alien_types[row], x, y)
                    self.aliens.append(alien)
        
        # Create shelters
        self.shelters = []
        shelter_y = self.height - 8
        num_shelters = 4
        spacing = self.width // (num_shelters + 1)
        
        for i in range(num_shelters):
            x = spacing * (i + 1) - 3
            if x > 0 and x < self.width - 7:
                self.shelters.append(Shelter(x, shelter_y))
        
        # Reset gunner
        self.gunner.x = self.width // 2
        self.gunner.exploding = False
        self.alien_direction = 1
    
    def save_game(self):
        """Save game state to JSON file"""
        if self.state not in [GameState.PLAY, GameState.PAUSED]:
            return False
        
        save_data = {
            'score': self.score,
            'level': self.level,
            'frame': self.frame,
            'gunner': {
                'x': self.gunner.x,
                'lives': self.gunner.lives,
                'exploding': self.gunner.exploding,
                'explode_counter': self.gunner.explode_counter
            },
            'aliens': [{
                'type': a.type,
                'x': a.x,
                'y': a.y,
                'frame': a.frame,
                'alive': a.alive,
                'explode_counter': a.explode_counter
            } for a in self.aliens],
            'shelters': [{
                'x': s.x,
                'y': s.y,
                'health': s.health
            } for s in self.shelters],
            'bullets': [{
                'x': b.x,
                'y': b.y,
                'active': b.active
            } for b in self.bullets],
            'bombs': [{
                'x': b.x,
                'y': b.y,
                'anim': b.anim,
                'active': b.active
            } for b in self.bombs],
            'alien_direction': self.alien_direction,
            'mystery_active': self.mystery_active,
            'mystery_ship': self.mystery_ship
        }
        
        try:
            with open(self.save_file, 'w') as f:
                json.dump(save_data, f, indent=2)
            return True
        except Exception as e:
            return False
    
    def load_game(self):
        """Load game state from JSON file"""
        if not os.path.exists(self.save_file):
            return False
        
        try:
            with open(self.save_file, 'r') as f:
                save_data = json.load(f)
            
            self.score = save_data['score']
            self.level = save_data['level']
            self.frame = save_data['frame']
            
            # Restore gunner
            g = save_data['gunner']
            self.gunner.x = g['x']
            self.gunner.lives = g['lives']
            self.gunner.exploding = g['exploding']
            self.gunner.explode_counter = g['explode_counter']
            
            # Restore aliens
            self.aliens = []
            for a_data in save_data['aliens']:
                alien = Alien(a_data['type'], a_data['x'], a_data['y'])
                alien.frame = a_data['frame']
                alien.alive = a_data['alive']
                alien.explode_counter = a_data['explode_counter']
                self.aliens.append(alien)
            
            # Restore shelters
            self.shelters = []
            for s_data in save_data['shelters']:
                shelter = Shelter(s_data['x'], s_data['y'])
                shelter.health = s_data['health']
                self.shelters.append(shelter)
            
            # Restore bullets
            self.bullets = []
            for b_data in save_data['bullets']:
                bullet = Bullet(b_data['x'], b_data['y'])
                bullet.active = b_data['active']
                self.bullets.append(bullet)
            
            # Restore bombs
            self.bombs = []
            for b_data in save_data['bombs']:
                bomb = Bomb(b_data['x'], b_data['y'])
                bomb.anim = b_data['anim']
                bomb.active = b_data['active']
                self.bombs.append(bomb)
            
            self.alien_direction = save_data['alien_direction']
            self.mystery_active = save_data['mystery_active']
            self.mystery_ship = save_data['mystery_ship']
            
            self.state = GameState.PLAY
            return True
        except Exception as e:
            return False
    
    def draw_sprite(self, sprite, x, y, color=1):
        """Draw an ASCII sprite at position"""
        try:
            for i, line in enumerate(sprite):
                if 0 <= y + i < self.height and 0 <= x < self.width:
                    self.stdscr.addstr(y + i, x, line[:self.width - x], curses.color_pair(color))
        except curses.error:
            pass
    
    def draw_intro(self):
        """Draw intro screen"""
        self.stdscr.clear()
        title = "ASCII SPACE INVADERS"
        subtitle = "Press SPACE to start"
        load_text = "Press L to load saved game"
        controls = ["Controls:", "A/D or Arrow Keys - Move", "SPACE - Fire", "P - Pause", "Q - Quit"]
        
        try:
            y = self.height // 2 - 5
            self.stdscr.addstr(y, (self.width - len(title)) // 2, title, curses.color_pair(3) | curses.A_BOLD)
            
            # Draw sample aliens
            self.draw_sprite(SPRITES['alien30_1'], self.width // 2 - 10, y + 2, 1)
            self.draw_sprite(SPRITES['alien20_1'], self.width // 2 - 3, y + 2, 2)
            self.draw_sprite(SPRITES['alien10_1'], self.width // 2 + 4, y + 2, 4)
            
            self.stdscr.addstr(y + 6, (self.width - len(subtitle)) // 2, subtitle, curses.color_pair(5))
            
            if os.path.exists(self.save_file):
                self.stdscr.addstr(y + 7, (self.width - len(load_text)) // 2, load_text, curses.color_pair(3))
            
            for i, control in enumerate(controls):
                self.stdscr.addstr(y + 9 + i, (self.width - len(control)) // 2, control, curses.color_pair(5))
        except curses.error:
            pass
    
    def draw_paused(self):
        """Draw pause overlay"""
        try:
            # Draw game in background
            self.draw_game()
            
            # Draw pause overlay
            title = "PAUSED"
            options = [
                "P - Resume",
                "S - Save Game",
                "Q - Quit to Menu"
            ]
            
            # Draw semi-transparent box
            box_height = 8
            box_width = 30
            start_y = self.height // 2 - box_height // 2
            start_x = self.width // 2 - box_width // 2
            
            for i in range(box_height):
                self.stdscr.addstr(start_y + i, start_x, " " * box_width, curses.color_pair(5) | curses.A_REVERSE)
            
            # Draw text
            self.stdscr.addstr(start_y + 2, (self.width - len(title)) // 2, title, curses.color_pair(3) | curses.A_BOLD)
            
            for i, option in enumerate(options):
                self.stdscr.addstr(start_y + 4 + i, (self.width - len(option)) // 2, option, curses.color_pair(5))
        except curses.error:
            pass
    
    def draw_game(self):
        """Draw game screen"""
        self.stdscr.clear()
        
        # Draw score and lives
        try:
            score_text = f"SCORE: {self.score:05d}"
            lives_text = f"LIVES: {self.gunner.lives}"
            level_text = f"LEVEL: {self.level}"
            
            self.stdscr.addstr(0, 2, score_text, curses.color_pair(5))
            self.stdscr.addstr(0, self.width - len(lives_text) - 2, lives_text, curses.color_pair(5))
            self.stdscr.addstr(0, (self.width - len(level_text)) // 2, level_text, curses.color_pair(3))
        except curses.error:
            pass
        
        # Draw aliens
        for alien in self.aliens:
            if alien.alive:
                if alien.explode_counter > 0:
                    self.draw_sprite(SPRITES['alien_explode'], alien.x, alien.y, 2)
                else:
                    sprite_name = f'alien{alien.type}_{(self.frame // 10) % 2 + 1}'
                    color = 1 if alien.type == 30 else (2 if alien.type == 20 else 4)
                    self.draw_sprite(SPRITES[sprite_name], alien.x, alien.y, color)
        
        # Draw mystery ship
        if self.mystery_active and self.mystery_ship:
            self.draw_sprite(SPRITES['mystery'], self.mystery_ship['x'], 1, 3)
        
        # Draw gunner
        if not self.gunner.exploding:
            self.draw_sprite(SPRITES['gunner'], self.gunner.x, self.height - 3, 1)
        else:
            self.draw_sprite(SPRITES['gunner_explode'], self.gunner.x, self.height - 3, 2)
        
        # Draw shelters
        for shelter in self.shelters:
            for row in range(3):
                for col in range(7):
                    if shelter.health[row][col]:
                        try:
                            char = SPRITES['shelter'][row][col]
                            if char != ' ':
                                self.stdscr.addstr(shelter.y + row, shelter.x + col, char, curses.color_pair(4))
                        except curses.error:
                            pass
        
        # Draw bullets
        for bullet in self.bullets:
            if bullet.active:
                try:
                    if 0 <= bullet.y < self.height and 0 <= bullet.x < self.width:
                        self.stdscr.addstr(bullet.y, bullet.x, "|", curses.color_pair(5))
                except curses.error:
                    pass
        
        # Draw bombs
        for bomb in self.bombs:
            if bomb.active:
                try:
                    if 0 <= bomb.y < self.height and 0 <= bomb.x < self.width:
                        self.stdscr.addstr(bomb.y, bomb.x, BOMB_CHARS[bomb.anim % 4], curses.color_pair(2))
                except curses.error:
                    pass
    
    def draw_gameover(self):
        """Draw game over screen"""
        self.stdscr.clear()
        title = "GAME OVER"
        score_text = f"Final Score: {self.score}"
        restart = "Press R to restart or Q to quit"
        
        try:
            y = self.height // 2
            self.stdscr.addstr(y, (self.width - len(title)) // 2, title, curses.color_pair(2) | curses.A_BOLD)
            self.stdscr.addstr(y + 2, (self.width - len(score_text)) // 2, score_text, curses.color_pair(5))
            self.stdscr.addstr(y + 4, (self.width - len(restart)) // 2, restart, curses.color_pair(5))
        except curses.error:
            pass
    
    def update_aliens(self):
        """Update alien positions and animations"""
        if not self.aliens:
            return
        
        # Move aliens
        if self.frame % 20 == 0:
            move_down = False
            
            # Check if aliens hit edge
            for alien in self.aliens:
                if alien.alive:
                    if (alien.x <= 1 and self.alien_direction < 0) or \
                       (alien.x >= self.width - 8 and self.alien_direction > 0):
                        move_down = True
                        break
            
            if move_down:
                self.alien_direction *= -1
                for alien in self.aliens:
                    if alien.alive:
                        alien.y += 1
            else:
                for alien in self.aliens:
                    if alien.alive:
                        alien.x += self.alien_direction
        
        # Update explosion counters
        for alien in self.aliens:
            if alien.explode_counter > 0:
                alien.explode_counter -= 1
                if alien.explode_counter == 0:
                    alien.alive = False
        
        # Random bomb dropping
        if self.frame % 30 == 0 and len(self.bombs) < 5:
            alive_aliens = [a for a in self.aliens if a.alive]
            if alive_aliens:
                shooter = random.choice(alive_aliens)
                self.bombs.append(Bomb(shooter.x + 3, shooter.y + 3))
    
    def update_mystery_ship(self):
        """Update mystery ship"""
        if self.mystery_active:
            if self.mystery_ship:
                self.mystery_ship['x'] += self.mystery_ship['dir']
                if self.mystery_ship['x'] < 0 or self.mystery_ship['x'] > self.width:
                    self.mystery_active = False
                    self.mystery_ship = None
        elif self.frame % 400 == 0 and random.random() < 0.5:
            direction = random.choice([-1, 1])
            x = 0 if direction > 0 else self.width - 7
            self.mystery_ship = {'x': x, 'dir': direction}
            self.mystery_active = True
    
    def update_bullets(self):
        """Update bullet positions"""
        for bullet in self.bullets:
            if bullet.active:
                bullet.y -= 1
                if bullet.y < 2:
                    bullet.active = False
        
        self.bullets = [b for b in self.bullets if b.active]
    
    def update_bombs(self):
        """Update bomb positions"""
        for bomb in self.bombs:
            if bomb.active:
                bomb.y += 1
                bomb.anim += 1
                if bomb.y >= self.height - 1:
                    bomb.active = False
        
        self.bombs = [b for b in self.bombs if b.active]
    
    def check_collisions(self):
        """Check for collisions"""
        # Bullets hitting aliens
        for bullet in self.bullets:
            if not bullet.active:
                continue
            for alien in self.aliens:
                if alien.alive and alien.explode_counter == 0:
                    if alien.x <= bullet.x < alien.x + 6 and alien.y <= bullet.y < alien.y + 3:
                        alien.explode_counter = 10
                        bullet.active = False
                        self.score += alien.type
                        break
        
        # Bullets hitting mystery ship
        if self.mystery_active and self.mystery_ship:
            for bullet in self.bullets:
                if not bullet.active:
                    continue
                if self.mystery_ship['x'] <= bullet.x < self.mystery_ship['x'] + 7 and bullet.y <= 2:
                    bullet.active = False
                    self.mystery_active = False
                    self.score += random.choice([50, 100, 150, 200])
                    break
        
        # Bullets hitting shelters
        for bullet in self.bullets:
            if not bullet.active:
                continue
            for shelter in self.shelters:
                if shelter.y <= bullet.y < shelter.y + 3 and \
                   shelter.x <= bullet.x < shelter.x + 7:
                    row = bullet.y - shelter.y
                    col = bullet.x - shelter.x
                    if 0 <= row < 3 and 0 <= col < 7:
                        shelter.health[row][col] = False
                        bullet.active = False
                        break
        
        # Bombs hitting gunner
        if not self.gunner.exploding:
            for bomb in self.bombs:
                if bomb.active:
                    if self.gunner.x <= bomb.x < self.gunner.x + 7 and \
                       bomb.y >= self.height - 3:
                        bomb.active = False
                        self.gunner.exploding = True
                        self.gunner.explode_counter = 30
                        self.gunner.lives -= 1
                        break
        
        # Bombs hitting shelters
        for bomb in self.bombs:
            if not bomb.active:
                continue
            for shelter in self.shelters:
                if shelter.y <= bomb.y < shelter.y + 3 and \
                   shelter.x <= bomb.x < shelter.x + 7:
                    row = bomb.y - shelter.y
                    col = bomb.x - shelter.x
                    if 0 <= row < 3 and 0 <= col < 7:
                        shelter.health[row][col] = False
                        bomb.active = False
                        break
    
    def handle_input(self, key):
        """Handle keyboard input"""
        if self.state == GameState.INTRO:
            if key == ord(' '):
                self.state = GameState.PLAY
                self.setup_game()
            elif key in [ord('l'), ord('L')]:
                if self.load_game():
                    self.state = GameState.PLAY
        
        elif self.state == GameState.PLAY:
            if key in [ord('p'), ord('P')]:
                self.state = GameState.PAUSED
            elif not self.gunner.exploding:
                if key in [ord('a'), ord('A'), curses.KEY_LEFT]:
                    self.gunner.x = max(1, self.gunner.x - 2)
                elif key in [ord('d'), ord('D'), curses.KEY_RIGHT]:
                    self.gunner.x = min(self.width - 8, self.gunner.x + 2)
                elif key == ord(' '):
                    # Fire bullet
                    if len(self.bullets) < 3:
                        self.bullets.append(Bullet(self.gunner.x + 3, self.height - 4))
        
        elif self.state == GameState.PAUSED:
            if key in [ord('p'), ord('P')]:
                self.state = GameState.PLAY
            elif key in [ord('s'), ord('S')]:
                self.save_game()
            elif key in [ord('q'), ord('Q')]:
                self.save_game()
                self.state = GameState.INTRO
        
        elif self.state == GameState.GAMEOVER:
            if key in [ord('r'), ord('R')]:
                self.score = 0
                self.level = 1
                self.gunner.lives = 3
                self.state = GameState.INTRO
        
        if key in [ord('q'), ord('Q')] and self.state != GameState.PAUSED:
            return False
        
        return True
    
    def run(self):
        """Main game loop"""
        running = True
        
        while running:
            key = self.stdscr.getch()
            
            if key != -1:
                running = self.handle_input(key)
                if not running:
                    break
            
            if self.state == GameState.INTRO:
                self.draw_intro()
            
            elif self.state == GameState.PLAY:
                self.frame += 1
                
                # Update game objects
                self.update_aliens()
                self.update_mystery_ship()
                self.update_bullets()
                self.update_bombs()
                self.check_collisions()
                
                # Update gunner explosion
                if self.gunner.exploding:
                    self.gunner.explode_counter -= 1
                    if self.gunner.explode_counter <= 0:
                        if self.gunner.lives <= 0:
                            self.state = GameState.GAMEOVER
                        else:
                            self.gunner.exploding = False
                            self.gunner.x = self.width // 2
                
                # Check win condition
                alive_aliens = [a for a in self.aliens if a.alive]
                if not alive_aliens:
                    self.level += 1
                    self.setup_game()
                
                # Check lose condition (aliens reached bottom)
                for alien in self.aliens:
                    if alien.alive and alien.y >= self.height - 6:
                        self.state = GameState.GAMEOVER
                
                self.draw_game()
            
            elif self.state == GameState.PAUSED:
                self.draw_paused()
            
            elif self.state == GameState.GAMEOVER:
                self.draw_gameover()
            
            self.stdscr.refresh()
            time.sleep(0.05)

def main(stdscr):
    game = Game(stdscr)
    game.run()

if __name__ == "__main__":
    curses.wrapper(main)
