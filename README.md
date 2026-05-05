# Fantasy Tower Defense 2D

A high-fidelity, strategy-rich Tower Defense game built entirely in Python using the Pygame library. This project features a vibrant Pixel Art fantasy forest environment, a modern dynamic UI, and advanced game mechanics designed to provide deep tactical gameplay.

## 🌟 Key Features

- **Advanced UI & Inventory**: Scrollable inventory system managing towers, support beacons, and elemental upgrade gems.
- **Adjacency Buff System**: Place Beacons to automatically broadcast attack, speed, and range buffs to nearby defensive towers.
- **Elemental Gem System**: Socket Fire or Ice gems into your towers to modify bullet properties (burn damage over time, or chill/slow effects).
- **VFX & Polish**: High-performance Object Pooled particle system for explosions, dynamic damage floating text, and screen shake on critical impacts.
- **Auto-Slotting AI**: A Deterministic algorithm that automatically plays the game by scanning grid coverage and placing towers/beacons in optimal chokepoints.
- **Spatial Partitioning**: Highly optimized collision detection using Spatial Hashing, maintaining a smooth 60 FPS even with hundreds of entities on a 1080p screen.
- **Intelligent Pathfinding**: Breadth-First Search (BFS) combined with dynamic waypoint calculations.

## 🛠️ Installation & Execution

### Prerequisites
Make sure you have Python 3.9+ installed.

### Setup
1. Clone the repository:
   ```bash
   git clone https://github.com/rquq/tower-defense-2d-pygame.git
   cd tower-defense-2d-pygame
   ```

2. Install dependencies:
   ```bash
   pip install pygame
   ```

3. Run the game:
   ```bash
   python main.py
   ```

## 🎮 Controls
- **Mouse Click (LMB)**: Place towers, select items from the inventory, toggle UI buttons.
- **Mouse Scroll**: Scroll through the inventory items.
- **1-5 Keys**: Quick-select towers (Earth Cannon, Wind Ballista, Fire Mortar, Storm Spire, Frost Cannon).
- **T Key**: Toggle Trash (Sell) mode to remove towers and refund resources.
- **N Key**: Force start the next wave immediately.
- **L Key (In Menu)**: Toggle Language (English / Tiếng Việt).
- **ESC**: Deselect current item / cancel placement mode.

## 📁 Project Architecture
- `core/`: Core engine loop, singletons, constants (`C`), and wave management.
- `entities/`: Base classes for Towers, Enemies, Projectiles, and Beacons.
- `systems/`: Advanced management systems (`SpatialManager`, `VFXManager`, `AssetManager`, `PathSystem`).
- `assets/`: Game textures, pixel art, and audio files.

---
*Built as a final project for IT003.Q21.CTTN - Ho Chi Minh City University of Information Technology.*
