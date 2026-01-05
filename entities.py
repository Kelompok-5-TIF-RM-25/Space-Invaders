"""Entity data classes for game objects."""
from dataclasses import dataclass
from typing import List


@dataclass
class Alien:
    """Alien enemy entity."""
    x: int
    y: int
    kind: str = "alien10"
    alive: bool = True


@dataclass
class Bomb:
    """Bomb dropped by aliens."""
    x: int
    y: int
    active: bool = True


@dataclass
class MysteryShip:
    """Mystery ship that appears randomly."""
    x: int
    y: int = 1
    active: bool = False
    direction: int = 1


@dataclass
class Bullet:
    """Bullet fired by player."""
    x: int
    y: int
    active: bool = True


@dataclass
class Player:
    """Player ship entity."""
    x: int
    y: int
    bullets: List[Bullet]
    last_fire_time: float = 0.0
