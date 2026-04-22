# Project Roadmap: Fantasy Tower Defense 2D

## Phase 1: Foundation & Low-Res Rendering
- [x] Initialize Pygame window (1920x1080).
- [x] Implement the internal 480x270 rendering surface logic with 4x scaling.
- [x] Create basic asset loader for pixel-perfect sprites.
- [x] Setup the main Game Engine and State Machine (MENU, PLAYING, BLESSING).

## Phase 2: Waypoints & Enemy Systems
- [x] Implement waypoint-based pathing system.
- [x] Create the `Enemy` base class with movement and health logic.
- [x] Develop the `WaveManager` for spawning and exponential HP scaling.
- [x] Basic enemy death and gold rewards.

## Phase 3: Tower Arsenal & Combat
- [x] Create the `Tower` base class with targeting logic (First, Strongest, Closest).
- [x] Implement 3 base types:
    - **Gunner**: Rapid fire, low damage.
    - **Sniper**: High range/damage, slow fire rate.
    - **Blaster**: Splash damage/AoE.
- [x] Develop the `Projectile` system for tracking and collision.

## Phase 4: Gems & Modifiers
- [x] Implement Drop Rate logic for Modifier Gems (Fire, Ice, Overclock).
- [x] Create the Gem Equipment UI for towers (2 slots per tower).
- [x] Code the Modifier Effects:
    - **Fire**: Visible indicator (Projectiles turn orange).
    - **Ice**: Added placeholder for slow logic.
    - **Overclock**: 30% reduction in fire rate (Faster).
- [x] Implement Grid Snapping (16x16) and Placement Validation (Path/Tower collisions).
- [x] HUD UI with clickable buttons & hotkey indicators.

## Phase 5: Blessings & Meta-Progression
- [x] Implement the Wave 3 "Blessing" pause logic (Every 3 waves).
- [x] Create the Blessing UI (Pick 1 of 3 global buffs).
- [x] Integrate global modifiers (e.g., +50% Gold, -20% Tower Cost, +Bonus DMG/Crit).
- [x] Final UI/UX pass: Hover descriptions for all turrets and stat tooltips.
