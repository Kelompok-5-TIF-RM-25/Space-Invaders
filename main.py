"""ASCII Space Invaders Game - Entry Point

A terminal-based Space Invaders clone using Python curses library.

Controls:
    Arrow Keys / A,D : Move player left/right
    SPACE           : Fire bullet
    S               : Save game
    L               : Load game
    Q               : Quit
"""
import curses
from game_app import GameApp


def main(stdscr):
    """Main entry point for the game.
    
    Args:
        stdscr: Curses standard screen object
    """
    app = GameApp()
    app.run(stdscr)


if __name__ == "__main__":
    curses.wrapper(main)

