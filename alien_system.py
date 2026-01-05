"""Alien system managing alien movement, bombs, and mystery ship."""
import random
from typing import List
from entities import Alien, Bomb, MysteryShip
from sprites import SPRITES


class AlienSystem:
    """System managing all alien-related entities and behaviors."""
    
    def __init__(self, screen_w: int):
        self.screen_w = screen_w
        self.aliens: List[Alien] = []
        self.bombs: List[Bomb] = []

        self.direction = 1
        self.speed = 1
        self.drop_rate = 0.01

        self.move_timer = 0.0
        self.move_delay = 0.4

        self.mystery = MysteryShip(x=0)
        self.spawn()

    def spawn(self):
        """Spawn a new formation of aliens."""
        self.aliens.clear()
        self.bombs.clear()

        sprite_w = len(SPRITES["alien10"][0][0])
        sprite_h = len(SPRITES["alien10"][0])

        gap_x = 3
        gap_y = 1

        start_x = 10
        start_y = 5

        rows = 3
        cols = 10

        row_kind = {0: "alien30", 1: "alien20", 2: "alien10"}

        for r in range(rows):
            kind = row_kind.get(r, "alien10")
            for c in range(cols):
                x = start_x + c * (sprite_w + gap_x)
                y = start_y + r * (sprite_h + gap_y)
                self.aliens.append(Alien(x, y, kind=kind))

        self.direction = 1
        self.move_timer = 0.0
        self.mystery.active = False

    def update(self, level: int, dt: float, screen_w: int, screen_h: int):
        """Update alien system each frame.
        
        Args:
            level: Current game level
            dt: Delta time since last frame
            screen_w: Screen width
            screen_h: Screen height
        """
        self.screen_w = screen_w

        self.speed = min(3, 1 + level // 2)
        self.drop_rate = min(0.05, 0.01 + level * 0.005)
        self.move_delay = max(0.15, 0.4 - level * 0.03)

        self.move_timer += dt
        if self.move_timer >= self.move_delay:
            self.move_timer = 0.0
            self.move()
            self.drop_bomb()

        self.update_bombs(screen_h)
        self.update_mystery(screen_w)

    def move(self):
        """Move all aliens and handle wall collisions."""
        hit_wall = False
        for a in self.aliens:
            if not a.alive:
                continue
            a.x += self.direction * self.speed
            if a.x <= 1 or a.x >= self.screen_w - 10:
                hit_wall = True

        if hit_wall:
            self.direction *= -1
            for a in self.aliens:
                if a.alive:
                    a.y += 1

    def drop_bomb(self):
        """Randomly drop a bomb from a living alien."""
        for a in self.aliens:
            if a.alive and random.random() < self.drop_rate:
                self.bombs.append(Bomb(a.x + 1, a.y + 1))
                break

    def update_bombs(self, screen_h: int):
        """Update bomb positions and remove off-screen bombs.
        
        Args:
            screen_h: Screen height
        """
        for b in self.bombs:
            if b.active:
                b.y += 1
                if b.y >= screen_h - 1:
                    b.active = False
        self.bombs = [b for b in self.bombs if b.active]

    def update_mystery(self, screen_w: int):
        """Update mystery ship position and spawning.
        
        Args:
            screen_w: Screen width
        """
        if not self.mystery.active:
            if random.random() < 0.002:
                self.mystery.active = True
                self.mystery.direction = 1
                self.mystery.x = 1
        else:
            self.mystery.x += self.mystery.direction * 2
            if self.mystery.x > screen_w - 10:
                self.mystery.active = False
