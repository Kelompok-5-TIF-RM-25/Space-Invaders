"""Game state management using Finite State Machine pattern."""
from enum import IntEnum


class GameState(IntEnum):
    """Game states using Finite State Machine pattern."""
    INTRO = 0
    PLAY = 1
    PAUSE = 2
    WIN = 3
    GAMEOVER = 4
    EXIT = 5
