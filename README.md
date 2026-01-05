# ASCII Space Invaders

Terminal-based Space Invaders game menggunakan Python dengan library curses.

## 📋 Requirements

- Python 3.7+
- Library `curses` (sudah built-in di macOS/Linux)

### Untuk Windows:
Windows tidak memiliki curses built-in. Install dengan:
```bash
pip install windows-curses
```

## 🚀 Installation

### Clone Repository
```bash
git clone <repository-url>
cd space_invaders
```

### Download Source Code
Atau download ZIP dari repository, extract, lalu:
```bash
cd space_invaders
```

## 🎮 Cara Main

Jalankan game dengan:
```bash
python main.py
```

### Controls

**Menu Utama:**
- `SPACE` - Mulai game baru
- `L` - Load game tersimpan
- `Q` - Quit

**Saat Bermain:**
- `←/→` atau `A/D` - Gerak kiri/kanan
- `SPACE` - Tembak
- `S` - Save game
- `L` - Load game
- `Q` - Quit

**Layar WIN (Setelah menyelesaikan level):**
- `N` - Next Level
- `S` - Save game
- `Q` - Quit

**Layar GAME OVER:**
- `SPACE` - Restart dari level 1
- `S` - Save game
- `L` - Load game
- `Q` - Quit

## 🏗️ Struktur Code

```
space_invaders/
├── main.py              # Entry point aplikasi
├── game_app.py          # Main game loop & rendering
├── game_core.py         # Core game logic (score, lives, level, FSM)
├── game_state.py        # Game state enum (INTRO, PLAY, WIN, GAMEOVER, etc)
├── entities.py          # Data classes untuk game entities
├── alien_system.py      # Sistem alien (movement, spawning, bombs)
├── sprites.py           # ASCII art sprites untuk semua entitas
├── save.json            # File save game (auto-generated)
└── README.md            # Dokumentasi ini
```

### Penjelasan File:

**`main.py`**
- Entry point program
- Initialize curses dan menjalankan game loop

**`game_app.py`**
- Main application class
- Handle input, update, dan rendering
- Collision detection

**`game_core.py`**
- Core game logic
- Finite State Machine untuk game states
- Score, lives, level management
- Save/load system
- Timer system

**`game_state.py`**
- Enum untuk game states (INTRO, PLAY, PAUSE, WIN, GAMEOVER, EXIT)
- Implementasi FSM pattern

**`entities.py`**
- Data classes untuk:
  - `Alien` - Enemy entities
  - `Bomb` - Alien bombs
  - `MysteryShip` - Bonus ship
  - `Bullet` - Player bullets
  - `Player` - Player ship

**`alien_system.py`**
- Mengelola semua alien behaviors
- Movement system
- Bomb dropping mechanism
- Mystery ship logic
- Difficulty scaling per level

**`sprites.py`**
- ASCII art untuk semua visual elements
- Sprites untuk alien, player, bomb, dll

**`save.json`**
- Format:
  ```json
  {
    "version": 1,
    "saved_at": 1234567890,
    "score": 180,
    "lives": 3,
    "level": 2,
    "time_left": 150.5
  }
  ```

## 🎯 Game Features

### Sistem Scoring
- Alien teratas (alien30): **30 poin**
- Alien tengah (alien20): **20 poin**
- Alien bawah (alien10): **10 poin**

### Leveling System
- Level mulai dari 1
- Unlimited levels
- Setiap level:
  - Alien bergerak lebih cepat
  - Bomb drop rate meningkat
  - Delay movement berkurang

### Save System
- Auto-save progress (score, lives, level, time)
- Load kapan saja untuk melanjutkan
- Format JSON untuk mudah di-debug

### Timer System
- Time limit: 180 detik per level
- Reset setiap next level
- Game over jika time habis

## 🐛 Debugging Tips

### Test Level Tertentu
**Cara 1: Edit save.json**
```json
{
  "level": 100,
  "score": 0,
  "lives": 3,
  "time_left": 180
}
```
Lalu load game dengan `L`.

**Cara 2: Edit start_game() di game_core.py**
```python
def start_game(self):
    self.level = 100  # Set level untuk debug
    # ...
```

## ❗ Troubleshooting

### Error: "No module named '_curses'" (Windows)
```bash
pip install windows-curses
```

### Terminal terlalu kecil
- Perbesar window terminal
- Minimum: 80x24 characters

### Game tidak jalan smooth
- Close aplikasi lain yang berat
- Pastikan terminal support Unicode

### Save file corrupt
- Delete `save.json`
- Restart game

## 📝 Notes

- Game menggunakan Finite State Machine pattern untuk state management
- Entity Component System untuk game objects
- Collision detection dengan AABB (Axis-Aligned Bounding Box)
- Rendering menggunakan double-buffering via curses

## 🎓 Design Patterns Used

1. **Finite State Machine (FSM)** - Game state management
2. **Data Classes** - Entity representations
3. **Separation of Concerns** - Logic, rendering, dan data terpisah
4. **Component System** - Alien system sebagai modular component

## 👨‍💻 Development

Dibuat untuk UAS Dasar Pemrograman.

---

**Happy Gaming!** 🚀👾
