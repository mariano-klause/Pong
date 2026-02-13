# Pong

A classic Pong implementation with player vs computer gameplay, scoring, and progressive difficulty.

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![Pygame](https://img.shields.io/badge/pygame-2.0+-green.svg)
![License](https://img.shields.io/badge/license-MIT-yellow.svg)

## Features

- 🎮 Player vs Computer gameplay
- 📊 Score tracking with win condition (first to 10)
- ⚡ Progressive speed increase as rally continues
- 🤖 AI opponent with realistic reaction time and imperfections
- ⏸️ Pause functionality
- 🔄 Restart anytime

## Installation

```bash
# Clone the repository
git clone https://github.com/mariano-klause/Pong.git
cd Pong

# Create virtual environment (recommended)
python3 -m venv venv

# Activate virtual environment
# On Linux/macOS:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Usage

```bash
# With virtual environment activated
python pong.py

# Or directly using venv python
./venv/bin/python pong.py
```

### Controls

| Key | Action |
|-----|--------|
| ↑ / W | Move paddle up |
| ↓ / S | Move paddle down |
| P | Pause/Resume |
| R | Restart game |
| Q | Quit |

## How It Works

### AI Behavior
The computer opponent uses a reactive approach:
- **Reaction delay:** 3-frame delay simulates human perception
- **Targeting error:** Gaussian randomness (σ=10px) prevents perfect play
- **Speed variation:** ±10% speed variance for organic movement
- **Selective tracking:** Only reacts when ball is approaching

### Difficulty Scaling
Ball speed increases by ~5% on each paddle hit, making rallies progressively more intense. The AI's reaction speed scales with the ball speed multiplier.

## Project Structure

```
Pong/
├── pong.py              # Main game implementation
├── requirements.txt     # Python dependencies
├── README.md           # This file
└── docs/
    └── blue_research.md # Design notes and patterns
```

## Design Philosophy

This implementation prioritizes:
1. **Code clarity** over clever optimizations
2. **Realistic AI** over unbeatable difficulty
3. **Type safety** with full type hints
4. **Documentation** for maintainability

See `docs/blue_research.md` for detailed architecture decisions.

## License

MIT License - See LICENSE file for details.

---

*Built by Blue - Senior Software Engineer*
