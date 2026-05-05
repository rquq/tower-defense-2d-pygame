# Thư mục: core

## File: `constants.py`

## Function: get_pixel_pos
Docstring for def get_pixel_pos.

---

## Class: GameState
Docstring for class GameState.

---

## Class: ItemType
Docstring for class ItemType.

---

## File: `engine.py`

## Class: Engine
Docstring for class Engine.

---

### Method: Engine.__init__
Docstring for def __init__.

---

### Method: Engine.t
Docstring for def t.

---

### Method: Engine.generate_trees
Docstring for def generate_trees.

---

### Method: Engine._create_tree_data
Docstring for def _create_tree_data.

---

### Method: Engine.render_static_background
Docstring for def render_static_background.

---

### Method: Engine.handle_events
Docstring for def handle_events.

---

### Method: Engine.handle_click
Docstring for def handle_click.

---

### Method: Engine.is_valid_placement
Docstring for def is_valid_placement.

---

### Method: Engine.calculate_adjacency_buffs
Docstring for def calculate_adjacency_buffs.

---

### Method: Engine.force_start_wave
Docstring for def force_start_wave.

---

### Method: Engine.update
Docstring for def update.

---

### Method: Engine.draw
Docstring for def draw.

---

### Method: Engine.apply_blur
Docstring for def apply_blur.

---

### Method: Engine.draw_text_with_shadow
Docstring for def draw_text_with_shadow.

---

### Method: Engine.draw_wrapped_text_centered
Docstring for def draw_wrapped_text_centered.

---

### Method: Engine.draw_menu
Docstring for def draw_menu.

---

### Method: Engine.draw_playing
Docstring for def draw_playing.

---

### Method: Engine.draw_placement_preview
Docstring for def draw_placement_preview.

---

### Method: Engine.draw_ui
Docstring for def draw_ui.

---

### Method: Engine.draw_hud_module
Docstring for def draw_hud_module.

---

### Method: Engine.draw_tooltips
Docstring for def draw_tooltips.

---

### Method: Engine.render_tooltip
Docstring for def render_tooltip.

---

### Method: Engine.draw_surrounding_forests
Docstring for def draw_surrounding_forests.

---

### Method: Engine.draw_monster_cave
Docstring for def draw_monster_cave.

---

### Method: Engine.draw_castle_base
Docstring for def draw_castle_base.

---

### Method: Engine.draw_powerup_menu
Docstring for def draw_powerup_menu.

---

### Method: Engine.draw_game_over
Docstring for def draw_game_over.

---

### Method: Engine.trigger_powerup
Docstring for def trigger_powerup.

---

### Method: Engine.apply_powerup
Docstring for def apply_powerup.

---

### Method: Engine.reset_game
Docstring for def reset_game.

---

### Method: Engine.process_auto_slots
Docstring for def process_auto_slots.

---

### Method: Engine.run
Docstring for def run.

---

## File: `wave_manager.py`

## Class: WaveManager
Orchestrates wave progression tracking enemy states accurately.

---

### Method: WaveManager.__init__
Loads baseline gold stores.

---

### Method: WaveManager.start_wave
Increases total wave numbers dynamically.

---

### Method: WaveManager.spawn_enemy
Spawns units utilizing probability scaling rules.

---

### Method: WaveManager.update
Refreshes enemy conditions efficiently.

---

### Method: WaveManager.draw
Applies batch iteration logic for drawing.

---

# Thư mục: entities

## File: `beacon.py`

## Class: Beacon
Support structure placed on the grid.
Emits beneficial stat buffs to adjacent towers.

---

### Method: Beacon.__init__
Initializes the Beacon at a grid coordinate with specific stats.

Args:
    x (int): X pixel coordinate.
    y (int): Y pixel coordinate.
    beacon_type (str): The type of the beacon determining its stats.

---

### Method: Beacon.add_gem
Attempts to insert a Stat Card into the beacon's upgrade slots.

Args:
    item (InventoryItem): The upgrade card to slot.
    
Returns:
    bool: True if slotting succeeded, False if full.

---

### Method: Beacon.get_all_buffs
Calculates the aggregate buffs provided by the beacon and slotted cards.

Returns:
    dict: Key-value map of stat types and additive buff percentages.

---

### Method: Beacon.draw
Renders the diamond beacon graphic and its active modification sockets.

Args:
    surface (pygame.Surface): The rendering destination.

---

## File: `enemy.py`

## Class: Enemy
Hostile entity executing path waypoints towards player base.

---

### Method: Enemy.__init__
Sets core properties and initial entry vector.

---

### Method: Enemy.update
Moves through waypoint coordinates per frame.

---

### Method: Enemy.draw
Draws current frame state with optional visual effects.

---

## File: `projectile.py`

## Class: Projectile
Projectiles launched by defending towers.
Calculates impact detection and applies status modifiers on targets.

---

### Method: Projectile.__init__
Initializes projectile stats and target tracking.

---

### Method: Projectile.update
Moves toward target position per frame step.

---

### Method: Projectile.hit
Processes damage calculations and triggers area-of-effect payloads.

---

### Method: Projectile.draw
Renders projectile trail curves and pointed orientations.

---

## File: `tower.py`

## Class: Tower
Core defensive structures designed to secure boundaries securely.

---

### Method: Tower.__init__
Initializes individual firing modules.

---

### Method: Tower.add_gem
Appends functional enhancements.

---

### Method: Tower.recalculate
Updates localized stat summaries.

---

### Method: Tower.update
Maintains targeting ranges continually.

---

### Method: Tower.find_target
Locates threats effectively.

---

### Method: Tower.fire
Launches lethal payload protocols.

---

### Method: Tower.draw_design
Processes graphical aesthetics.

---

### Method: Tower.draw
Draws basic modules properly.

---

# Thư mục: systems

## File: `asset_manager.py`

## Class: AssetManager
Handles asset loading and Sprite Sheet parsing/slicing for performance.

---

### Method: AssetManager.__init__
Initializes base asset collection mappings.

---

### Method: AssetManager.get_instance
Retrieves instance via singleton logic safely.

---

### Method: AssetManager.init
Loads sounds and creates target mappings safely.

---

### Method: AssetManager.play_sound
Fires audio playback events effortlessly.

---

### Method: AssetManager._extract_sprites
Splits single strip files into independent surface matrices.

---

## File: `gem_system.py`

## Class: GemType
Enumeration of available gem types.

---

## Class: Gem
Represents an elemental gem that can be slotted into towers.
Modifies base stats and adds elemental properties.

---

### Method: Gem.__init__
Initializes the Gem with a type and its associated visual color.

Args:
    gem_type (GemType): The type of this gem.

---

### Method: Gem.apply_modifier
Applies the specific stat modifications to the target tower.

Args:
    tower (Tower): The tower receiving the modifiers.

---

## File: `inventory_items.py`

## Class: InventoryItem
Represents an item stored in the player's inventory.
Can be a Gem, Beacon, or Stat Card.

---

### Method: InventoryItem.__init__
Initializes the InventoryItem with its type and data.

Args:
    item_type (ItemType): The category of the item.
    data (dict or str): Specific statistics or identifier for the item.

---

### Method: InventoryItem.get_tooltip_data
Generates formatted tooltip lines for UI display.

Args:
    t (function): Translation function for localizing strings.
    
Returns:
    list: List of string lines to show in the tooltip.

---

## File: `pathfinding.py`

## Function: get_path_bfs
Simple Breadth-First Search (BFS) implementation for grid pathfinding.
Efficiently finds the shortest path by exploring layer by layer.

---

## Class: PathSystem
Docstring for class PathSystem.

---

### Method: PathSystem.__init__
Docstring for def __init__.

---

### Method: PathSystem.generate_curvy_path
Docstring for def generate_curvy_path.

---

### Method: PathSystem.add_segment
Docstring for def add_segment.

---

### Method: PathSystem.get_enemy_waypoints
Docstring for def get_enemy_waypoints.

---

## File: `spatial_manager.py`

## Class: SpatialManager
A simple Spatial Hash Grid to optimize entity lookups.
Reduces O(N) searches to approximately O(1) by partitioning space into cells.

---

### Method: SpatialManager.__init__
Docstring for def __init__.

---

### Method: SpatialManager._get_cell
Docstring for def _get_cell.

---

### Method: SpatialManager.clear
Clears the grid for the next frame.

---

### Method: SpatialManager.add_entity
Adds an entity to its corresponding cell.

---

### Method: SpatialManager.get_nearby_entities
Returns a list of entities within the specified radius of (x, y).
Only checks cells that could potentially contain entities within range.

---

### Method: SpatialManager.get_closest_entity
Finds the closest entity within radius. 
Optional 'criteria' lambda can be used for secondary filtering (e.g., strongest).

---

## File: `vfx_system.py`

## Class: Particle
Docstring for class Particle.

---

### Method: Particle.__init__
Docstring for def __init__.

---

### Method: Particle.reset
Docstring for def reset.

---

### Method: Particle.update
Docstring for def update.

---

### Method: Particle.draw
Docstring for def draw.

---

## Class: FloatingText
Docstring for class FloatingText.

---

### Method: FloatingText.__init__
Docstring for def __init__.

---

### Method: FloatingText.reset
Docstring for def reset.

---

### Method: FloatingText.update
Docstring for def update.

---

### Method: FloatingText.draw
Docstring for def draw.

---

## Class: VFXManager
Docstring for class VFXManager.

---

### Method: VFXManager.__init__
Docstring for def __init__.

---

### Method: VFXManager._get_particle
Docstring for def _get_particle.

---

### Method: VFXManager._get_text
Docstring for def _get_text.

---

### Method: VFXManager.create_floating_text
Docstring for def create_floating_text.

---

### Method: VFXManager.create_ambient_particle
Docstring for def create_ambient_particle.

---

### Method: VFXManager.spawn_link_particle
Docstring for def spawn_link_particle.

---

### Method: VFXManager.trigger_shake
Docstring for def trigger_shake.

---

### Method: VFXManager.create_explosion
Docstring for def create_explosion.

---

### Method: VFXManager.create_impact
Docstring for def create_impact.

---

### Method: VFXManager.create_death_effect
Docstring for def create_death_effect.

---

### Method: VFXManager.update
Docstring for def update.

---

### Method: VFXManager.draw
Docstring for def draw.

---

