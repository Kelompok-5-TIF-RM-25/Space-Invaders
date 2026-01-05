"""Sprite definitions and utilities for game entities."""
from typing import List


SPRITES = {
    "alien30": [
        [" {@@} ", " /\"\"\\ ", "      "],
        [" {@@} ", " \\__/ ", "      "],
    ],
    "alien20": [
        [" dOOb ", " ^/\\^ ", "      "],
        [" dOOb ", " v\\//v", "      "],
    ],
    "alien10": [
        [" /MM\\ ", " |~~| ", "      "],
        [" \\MM/ ", " |~~| ", "      "],
    ],
    "player": [
        [
            "   _^_   ",
            " _/___\\_ ",
            "  \\___/  ",
        ],
        [
            "   _^_   ",
            " _/___\\_ ",
            "  /___\\  ",
        ],
    ],
}

ALIEN_INTRO = [
    "  ▄██▄  ",
    " ██████ ",
    "▄██▀▀██▄",
    "  ▀  ▀  ",
]


def sprite_size(sprite_lines: List[str]) -> tuple[int, int]:
    """Calculate the width and height of a sprite.
    
    Args:
        sprite_lines: List of strings representing sprite lines
        
    Returns:
        Tuple of (width, height)
    """
    h = len(sprite_lines)
    w = max((len(s) for s in sprite_lines), default=0)
    return w, h
