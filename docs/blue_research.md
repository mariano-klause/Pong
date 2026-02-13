# Blue's Research Notes

## Project: Pong
**Started:** 2026-02-13
**Author:** Blue (Senior Software Engineer)

---

## Design Decisions

### Architecture
- **Language:** Python 3 - chosen for rapid development and readability
- **Library:** pygame - mature, stable, well-documented 2D game framework
- **Structure:** Object-oriented with clear separation of concerns:
  - `Ball`: Physics and state management
  - `Paddle`: Player/AI input handling
  - `Game`: State machine and rendering

### Game Mechanics

#### Ball Physics
- Velocity-based movement with floating point precision
- Speed increases 5% on each paddle hit (horizontal) and 2% (vertical)
- Spin calculation based on hit position relative to paddle center
- Gaussian randomness on reset for varied gameplay

#### AI Behavior
- Reactive, not predictive - more realistic feel
- Reaction delay of 3 frames simulates human perception lag
- Gaussian error (σ=10px) prevents perfect play
- Speed variation (±10%) adds organic movement
- Only tracks when ball moving toward AI side (respects game flow)

#### Difficulty Progression
- `SPEED_INCREMENT = 0.5` added to multiplier every 10 paddle hits
- Multiplier affects AI reaction speed proportionally
- Keeps game challenging as player improves

### Security & Safety Considerations
- Boundary clamping prevents object escape
- Ball pushed out of paddle post-collision (prevents sticking)
- Input validation through pygame's event system
- Graceful exit on Q/quit events

### Code Quality
- Type hints throughout for maintainability
- Docstrings for all public methods
- Constants extracted for tunability
- No magic numbers in logic

---

## Known Patterns

### Game Loop Pattern
```python
while running:
    handle_input()
    update()
    draw()
    tick_clock()
```
Standard 60 FPS game loop with fixed timestep.

### State Machine
Game states: `playing` | `paused` | `game_over`
Clear transitions via method calls, no state enums needed for this scope.

### Collision Response
1. Detect overlap (AABB)
2. Reverse appropriate velocity component
3. Apply physics modifiers (spin, speed)
4. Separate objects (prevent tunneling)

---

## Pitfalls Avoided

1. **Ball tunneling:** Using rect collision, not point checks
2. **Frame-dependent speed:** All movement uses constant time base
3. **AI perfection:** Added intentional delays and errors
4. **Memory leaks:** pygame surfaces managed by library, no manual allocation
5. **Unclean exits:** Proper pygame.quit() in all paths

---

## Future Improvements (Backlog)

- [ ] Sound effects (paddle hit, score, win)
- [ ] Particle effects on paddle hits
- [ ] Difficulty settings (Easy/Medium/Hard)
- [ ] Two-player local mode
- [ ] Unit tests for physics engine
- [ ] CI/CD with GitHub Actions
- [ ] Package as executable with PyInstaller

---

## References

- pygame docs: https://www.pygame.org/docs/
- Game Programming Patterns (Nystrom): State, Game Loop, Update Method
