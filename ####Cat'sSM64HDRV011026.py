import pygame
import math
import sys
import random
import time
import json
import os

# --- CONSTANTS & CONFIGURATION ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
SKY_BLUE = (135, 206, 235)
GRASS_GREEN = (34, 139, 34)
PARCHMENT = (238, 232, 205)
PARCHMENT_INK = (30, 25, 20)
PARCHMENT_SHADOW = (180, 170, 150)
DEBUG_BLUE = (0, 0, 128)
DEBUG_YELLOW = (255, 255, 0)
YELLOW = (255, 255, 0)

# --- MAP/LEVEL MANAGEMENT SYSTEM ---

class MapObject:
    """Base class for all map objects (platforms, enemies, collectibles, etc.)"""
    def __init__(self, x, y, z, width=100, height=100, depth=100, color=WHITE, obj_type="platform"):
        self.x = x
        self.y = y
        self.z = z
        self.width = width
        self.height = height
        self.depth = depth
        self.color = color
        self.type = obj_type
        self.collected = False
        
    def get_corners(self):
        """Get all 8 corners of the 3D box"""
        hw = self.width / 2
        hh = self.height / 2
        hd = self.depth / 2
        
        return [
            (self.x - hw, self.y - hh, self.z - hd),  # Front-bottom-left
            (self.x + hw, self.y - hh, self.z - hd),  # Front-bottom-right
            (self.x + hw, self.y + hh, self.z - hd),  # Front-top-right
            (self.x - hw, self.y + hh, self.z - hd),  # Front-top-left
            (self.x - hw, self.y - hh, self.z + hd),  # Back-bottom-left
            (self.x + hw, self.y - hh, self.z + hd),  # Back-bottom-right
            (self.x + hw, self.y + hh, self.z + hd),  # Back-top-right
            (self.x - hw, self.y + hh, self.z + hd),  # Back-top-left
        ]

class GameMap:
    """Represents a complete 3D level/map"""
    def __init__(self, name, theme="grassland", star_count=6):
        self.name = name
        self.theme = theme
        self.star_count = star_count
        self.objects = []
        self.spawn_point = (0, 100, 0)  # Default spawn
        self.sky_color = SKY_BLUE
        self.ground_color = GRASS_GREEN
        self.stars_collected = 0
        
        # Set theme colors
        self.set_theme(theme)
        
        # Add default ground
        self.create_ground()
    
    def set_theme(self, theme):
        """Set visual theme for the map"""
        if theme == "grassland":
            self.sky_color = SKY_BLUE
            self.ground_color = GRASS_GREEN
        elif theme == "desert":
            self.sky_color = (255, 229, 180)
            self.ground_color = (210, 180, 140)
        elif theme == "snow":
            self.sky_color = (225, 245, 255)
            self.ground_color = (240, 248, 255)
        elif theme == "water":
            self.sky_color = (135, 206, 250)
            self.ground_color = (64, 164, 223)
        elif theme == "castle":
            self.sky_color = (70, 70, 70)
            self.ground_color = (100, 100, 100)
    
    def create_ground(self):
        """Create the base ground plane"""
        # Large ground platform
        self.add_object(0, -50, 0, 2000, 100, 2000, self.ground_color, "ground")
    
    def add_object(self, x, y, z, width, height, depth, color, obj_type="platform"):
        """Add an object to the map"""
        obj = MapObject(x, y, z, width, height, depth, color, obj_type)
        self.objects.append(obj)
        return obj
    
    def add_platform(self, x, y, z, size=100, color=None):
        """Add a floating platform"""
        if color is None:
            color = (random.randint(100, 200), random.randint(100, 200), random.randint(100, 200))
        return self.add_object(x, y, z, size, 20, size, color, "platform")
    
    def add_star(self, x, y, z):
        """Add a collectible star"""
        return self.add_object(x, y, z, 40, 40, 40, YELLOW, "star")
    
    def add_coin(self, x, y, z):
        """Add a collectible coin"""
        return self.add_object(x, y, z, 30, 30, 10, (255, 215, 0), "coin")
    
    def add_enemy(self, x, y, z, enemy_type="goomba"):
        """Add an enemy"""
        color = (139, 69, 19) if enemy_type == "goomba" else (255, 0, 0)
        return self.add_object(x, y, z, 60, 60, 60, color, enemy_type)
    
    def check_collision(self, player_x, player_y, player_z, player_radius=40):
        """Check collision between player and map objects"""
        collisions = []
        
        for obj in self.objects:
            if obj.collected and obj.type in ["star", "coin"]:
                continue
                
            # Simple sphere-AABB collision
            dx = max(obj.x - obj.width/2, min(player_x, obj.x + obj.width/2))
            dy = max(obj.y - obj.height/2, min(player_y, obj.y + obj.height/2))
            dz = max(obj.z - obj.depth/2, min(player_z, obj.z + obj.depth/2))
            
            distance = math.sqrt((dx - player_x)**2 + (dy - player_y)**2 + (dz - player_z)**2)
            
            if distance < player_radius:
                collisions.append(obj)
                
        return collisions

# --- PRE-DEFINED MAPS/LEVELS ---

def create_test_map():
    """Create a simple test map"""
    game_map = GameMap("Test Course", "grassland", 1)
    game_map.spawn_point = (0, 100, 0)
    
    # Add platforms
    game_map.add_platform(0, 50, 200)
    game_map.add_platform(200, 100, 0)
    game_map.add_platform(-200, 150, -200)
    game_map.add_platform(0, 200, -400)
    
    # Add a star at the highest platform
    game_map.add_star(0, 250, -400)
    
    # Add some coins
    for i in range(5):
        x = random.randint(-300, 300)
        z = random.randint(-300, 300)
        game_map.add_coin(x, 150, z)
    
    # Add an enemy
    game_map.add_enemy(100, 70, 200)
    
    return game_map

def create_bobomb_battlefield():
    """Recreate Bob-omb Battlefield from SM64"""
    game_map = GameMap("Bob-omb Battlefield", "grassland", 7)
    game_map.spawn_point = (0, 100, 0)
    
    # Main mountain
    game_map.add_object(0, 50, 0, 800, 100, 800, (100, 80, 60), "mountain")
    
    # Platforms leading up
    game_map.add_platform(0, 150, 300, 120, (150, 120, 90))
    game_map.add_platform(0, 250, 500, 100, (160, 130, 100))
    
    # Top platform with star
    game_map.add_platform(0, 350, 700, 80, (170, 140, 110))
    game_map.add_star(0, 390, 700)
    
    # Side platforms with coins
    game_map.add_platform(300, 180, 100, 80, (140, 110, 80))
    game_map.add_coin(300, 220, 100)
    
    game_map.add_platform(-300, 180, 100, 80, (140, 110, 80))
    game_map.add_coin(-300, 220, 100)
    
    # Enemies
    game_map.add_enemy(200, 110, 200, "goomba")
    game_map.add_enemy(-200, 110, 200, "goomba")
    
    return game_map

def create_whomp_fortress():
    """Create Whomp's Fortress inspired level"""
    game_map = GameMap("Whomp's Fortress", "castle", 8)
    game_map.spawn_point = (0, 100, -300)
    
    # Main fortress structure
    game_map.add_object(0, 100, 0, 400, 200, 400, (150, 150, 150), "fortress")
    
    # Platforms leading to fortress
    z_positions = [-200, -100, 0]
    for i, z in enumerate(z_positions):
        height = 50 + i * 50
        game_map.add_platform(0, height, z, 120, (180, 180, 180))
    
    # Top of fortress
    game_map.add_platform(0, 250, 0, 100, (200, 200, 200))
    game_map.add_star(0, 290, 0)
    
    # Side towers
    game_map.add_platform(200, 180, 200, 60, (140, 140, 140))
    game_map.add_coin(200, 210, 200)
    
    game_map.add_platform(-200, 180, 200, 60, (140, 140, 140))
    game_map.add_coin(-200, 210, 200)
    
    return game_map

def create_jolly_roger_bay():
    """Create Jolly Roger Bay inspired water level"""
    game_map = GameMap("Jolly Roger Bay", "water", 6)
    game_map.spawn_point = (0, 100, -500)
    
    # Underwater terrain
    game_map.add_object(0, -100, 0, 1000, 50, 1000, (80, 120, 160), "water_floor")
    
    # Sunken ship
    game_map.add_object(200, 0, 200, 300, 100, 600, (139, 69, 19), "ship")
    
    # Platforms above water
    game_map.add_platform(0, 150, 0, 150, (200, 200, 150))
    game_map.add_platform(-300, 200, 100, 100, (200, 200, 150))
    
    # Star inside ship
    game_map.add_star(200, 50, 200)
    
    # Coins around the bay
    for angle in range(0, 360, 45):
        rad = math.radians(angle)
        x = 400 * math.cos(rad)
        z = 400 * math.sin(rad)
        game_map.add_coin(x, 50, z)
    
    return game_map

def create_cool_cool_mountain():
    """Create Cool, Cool Mountain inspired snow level"""
    game_map = GameMap("Cool, Cool Mountain", "snow", 7)
    game_map.spawn_point = (0, 100, -400)
    
    # Snowy mountain
    game_map.add_object(0, 0, 0, 600, 300, 600, (240, 248, 255), "mountain")
    
    # Icy platforms
    platforms = [
        (0, 150, 200, 120),
        (200, 200, 0, 100),
        (-200, 250, -100, 100),
        (0, 300, -200, 80)
    ]
    
    for x, y, z, size in platforms:
        game_map.add_platform(x, y, z, size, (220, 240, 255))
    
    # Star at the peak
    game_map.add_star(0, 350, 0)
    
    # Icy slide path
    for i in range(10):
        x = i * 50 - 200
        z = i * 50
        game_map.add_platform(x, 100, z, 40, (200, 220, 240))
        if i % 3 == 0:
            game_map.add_coin(x, 130, z)
    
    return game_map

def create_desert_map():
    """Create a desert/pyramid themed map"""
    game_map = GameMap("Shifting Sand Land", "desert", 6)
    game_map.spawn_point = (0, 100, -600)
    
    # Pyramid
    game_map.add_object(0, 0, 0, 400, 200, 400, (218, 165, 32), "pyramid")
    
    # Pyramid steps
    for i in range(5):
        height = 50 + i * 40
        size = 300 - i * 60
        game_map.add_object(0, height, 0, size, 40, size, (210, 180, 140), "pyramid_step")
    
    # Star at pyramid top
    game_map.add_star(0, 250, 0)
    
    # Quicksand areas (hazard)
    game_map.add_object(300, -40, 0, 200, 20, 200, (194, 178, 128), "quicksand")
    game_map.add_object(-300, -40, 0, 200, 20, 200, (194, 178, 128), "quicksand")
    
    # Cacti
    for i in range(4):
        x = random.randint(-500, 500)
        z = random.randint(-500, 500)
        if abs(x) > 250 or abs(z) > 250:  # Outside pyramid area
            game_map.add_object(x, 50, z, 40, 100, 40, (34, 139, 34), "cactus")
            if random.random() > 0.5:
                game_map.add_coin(x, 120, z)
    
    return game_map

# --- MAP MANAGER ---

class MapManager:
    """Manages all game maps and level progression"""
    
    # All available maps
    ALL_MAPS = {
        "test": create_test_map,
        "bobomb": create_bobomb_battlefield,
        "whomp": create_whomp_fortress,
        "jolly": create_jolly_roger_bay,
        "cool": create_cool_cool_mountain,
        "desert": create_desert_map
    }
    
    # Map order for progression
    MAP_ORDER = ["test", "bobomb", "whomp", "jolly", "cool", "desert"]
    
    def __init__(self):
        self.current_map_index = 0
        self.current_map = None
        self.loaded_maps = {}
        self.player_stars = 0
        self.unlocked_maps = {"test"}  # Start with test map unlocked
        
        # Load the first map
        self.load_map(self.MAP_ORDER[0])
    
    def load_map(self, map_name):
        """Load a map by name"""
        if map_name in self.loaded_maps:
            self.current_map = self.loaded_maps[map_name]
        else:
            create_func = self.ALL_MAPS.get(map_name)
            if create_func:
                self.current_map = create_func()
                self.loaded_maps[map_name] = self.current_map
        
        # Update current map index
        if map_name in self.MAP_ORDER:
            self.current_map_index = self.MAP_ORDER.index(map_name)
    
    def next_map(self):
        """Load the next map in progression"""
        if self.current_map_index < len(self.MAP_ORDER) - 1:
            next_map_name = self.MAP_ORDER[self.current_map_index + 1]
            if next_map_name in self.unlocked_maps:
                self.load_map(next_map_name)
                return True
        return False
    
    def previous_map(self):
        """Load the previous map"""
        if self.current_map_index > 0:
            prev_map_name = self.MAP_ORDER[self.current_map_index - 1]
            self.load_map(prev_map_name)
            return True
        return False
    
    def unlock_next_map(self):
        """Unlock the next map in progression"""
        if self.current_map_index < len(self.MAP_ORDER) - 1:
            next_map_name = self.MAP_ORDER[self.current_map_index + 1]
            self.unlocked_maps.add(next_map_name)
            return True
        return False
    
    def collect_star(self):
        """Collect a star in the current map"""
        if self.current_map:
            self.current_map.stars_collected += 1
            self.player_stars += 1
            
            # Unlock next map if all stars collected
            if self.current_map.stars_collected >= self.current_map.star_count:
                self.unlock_next_map()
    
    def get_map_name(self):
        """Get the name of the current map"""
        return self.current_map.name if self.current_map else "Unknown"
    
    def get_total_stars(self):
        """Get total stars collected across all maps"""
        return self.player_stars
    
    def get_map_stars(self):
        """Get stars collected in current map"""
        return self.current_map.stars_collected if self.current_map else 0
    
    def reset_current_map(self):
        """Reset the current map"""
        map_name = self.MAP_ORDER[self.current_map_index]
        if map_name in self.ALL_MAPS:
            self.current_map = self.ALL_MAPS[map_name]()
            self.loaded_maps[map_name] = self.current_map

# --- STATE MANAGEMENT SYSTEM ---

class GameState:
    """Base class for all game states."""
    def __init__(self, manager):
        self.manager = manager

    def handle_events(self, events):
        pass

    def update(self):
        pass

    def render(self, screen):
        pass
    
    def on_enter(self):
        """Called when state is entered"""
        pass

# --- STATES ---

class IntroState(GameState):
    """
    1:1 Recreation of the SM64 'Dear Mario' Intro.
    """
    def __init__(self, manager):
        super().__init__(manager)
        self.state = "READ" 
        
        # EXACT SM64 Letter Text
        self.lines = [
            "Dear Mario,",
            "Please come to the",
            "castle. I've baked",
            "a cake for you.",
            "",
            "Yours truly--",
            "Princess Toadstool"
        ]
        
        # Robust Font Loading for Mac/Windows
        self.font = pygame.font.SysFont("georgia", 38, bold=True)
        if not self.font:
            self.font = pygame.font.SysFont("timesnewroman", 38, bold=True)
            
        self.sig_font = pygame.font.SysFont("brushscriptmt", 46, italic=True)
        if not self.sig_font:
             self.sig_font = pygame.font.SysFont("arial", 40, bold=True, italic=True)

        self.parchment_w = SCREEN_WIDTH
        self.parchment_h = SCREEN_HEIGHT
        self.parchment_surf = pygame.Surface((self.parchment_w, self.parchment_h))
        self._render_parchment_texture()

    def _render_parchment_texture(self):
        self.parchment_surf.fill(PARCHMENT)
        border_margin = 30
        border_color = (139, 69, 19)
        pygame.draw.rect(self.parchment_surf, border_color, 
                         (border_margin, border_margin, 
                          self.parchment_w - 2*border_margin, 
                          self.parchment_h - 2*border_margin), 5)
        
        inner_margin = border_margin + 8
        pygame.draw.rect(self.parchment_surf, border_color, 
                         (inner_margin, inner_margin, 
                          self.parchment_w - 2*inner_margin, 
                          self.parchment_h - 2*inner_margin), 2)

        start_y = 150
        line_height = 55
        
        for i, line in enumerate(self.lines):
            is_signature = (i == len(self.lines) - 1)
            is_yours_truly = (i == len(self.lines) - 2)
            is_salutation = (i == 0)
            
            font = self.sig_font if is_signature else self.font
            color = (220, 20, 60) if is_signature else PARCHMENT_INK
            
            rendered_line = font.render(line, True, color)
            shadow_color = PARCHMENT_SHADOW
            rendered_shadow = font.render(line, True, shadow_color)

            text_w = rendered_line.get_width()
            
            if is_salutation:
                pos_x = border_margin + 70
            elif is_signature or is_yours_truly:
                pos_x = self.parchment_w - text_w - border_margin - 70
            else:
                pos_x = (self.parchment_w - text_w) // 2
            
            if not is_signature:
                self.parchment_surf.blit(rendered_shadow, (pos_x + 2, start_y + 2))
            
            self.parchment_surf.blit(rendered_line, (pos_x, start_y))
            start_y += line_height

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_SPACE, pygame.K_RETURN, pygame.K_ESCAPE, pygame.K_x):
                    self.manager.change_state("FILE_SELECT")
            if event.type == pygame.MOUSEBUTTONDOWN:
                 self.manager.change_state("FILE_SELECT")

    def render(self, screen):
        screen.blit(self.parchment_surf, (0, 0))
        pulse = abs(math.sin(pygame.time.get_ticks() * 0.005)) * 255
        prompt_font = pygame.font.SysFont("arial", 24, bold=True)
        prompt = prompt_font.render("- PRESS START -", True, (80, 40, 0))
        prompt.set_alpha(int(pulse))
        
        prompt_x = SCREEN_WIDTH // 2 - prompt.get_width() // 2
        prompt_y = SCREEN_HEIGHT - 60
        screen.blit(prompt, (prompt_x, prompt_y))

class FileSelectState(GameState):
    """
    Standard File Select Menu.
    """
    def __init__(self, manager):
        super().__init__(manager)
        self.title_font = pygame.font.SysFont("arial", 48, bold=True)
        self.font = pygame.font.SysFont("arial", 36, bold=True)
        self.selected = 0
        
    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.selected = (self.selected - 1) % 4
                elif event.key == pygame.K_DOWN:
                    self.selected = (self.selected + 1) % 4
                elif event.key in (pygame.K_SPACE, pygame.K_RETURN):
                    self.manager.change_state("MAP_SELECT")
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.manager.change_state("MAP_SELECT")
        
    def render(self, screen):
        screen.fill((60, 0, 0)) 
        title_surf = self.title_font.render("SELECT FILE", True, (255, 215, 0))
        screen.blit(title_surf, (SCREEN_WIDTH//2 - title_surf.get_width()//2, 50))
        
        start_y = 150
        slot_height = 90
        
        for i in range(4):
            rect = pygame.Rect(150, start_y + i*slot_height, 500, 70)
            is_sel = (i == self.selected)
            
            color = (100, 100, 200) if is_sel else (100, 50, 50)
            border_color = (255, 255, 0) if is_sel else (200, 200, 200)
            
            pygame.draw.rect(screen, color, rect, border_radius=10)
            pygame.draw.rect(screen, border_color, rect, 3, border_radius=10)
            
            label = f"MARIO {chr(65+i)}"
            text_surf = self.font.render(label, True, WHITE)
            screen.blit(text_surf, (rect.x + 20, rect.y + 15))
            
            stars_count = 0 if i > 0 else 3 
            stars = f"* {stars_count}"
            star_surf = self.font.render(stars, True, (255, 255, 0))
            screen.blit(star_surf, (rect.right - 100, rect.y + 15))

        hint = self.font.render("PRESS START", True, (255, 255, 255))
        screen.blit(hint, (SCREEN_WIDTH//2 - hint.get_width()//2, SCREEN_HEIGHT - 60))

class MapSelectState(GameState):
    """
    Map/Level Selection Screen
    """
    def __init__(self, manager):
        super().__init__(manager)
        self.title_font = pygame.font.SysFont("arial", 48, bold=True)
        self.font = pygame.font.SysFont("arial", 36, bold=True)
        self.small_font = pygame.font.SysFont("arial", 24, bold=True)
        self.selected_index = 0
        self.preview_time = 0
        self.map_previews = {}
        self.create_map_previews()
        self.grid_rects = [] # Store rects for mouse interaction

    def create_map_previews(self):
        preview_size = (200, 150)
        preview_colors = {
            "test": (SKY_BLUE, GRASS_GREEN, BLUE, RED),
            "bobomb": (SKY_BLUE, GRASS_GREEN, (139, 69, 19), YELLOW),
            "whomp": ((70, 70, 70), (100, 100, 100), (150, 150, 150), YELLOW),
            "jolly": ((135, 206, 250), (64, 164, 223), (139, 69, 19), YELLOW),
            "cool": ((225, 245, 255), (240, 248, 255), (200, 220, 240), YELLOW),
            "desert": ((255, 229, 180), (210, 180, 140), (218, 165, 32), YELLOW)
        }
        
        # Use manager's map list
        for map_name in self.manager.map_manager.MAP_ORDER:
            if map_name in preview_colors:
                sky, ground, plat, star = preview_colors[map_name]
                preview = pygame.Surface(preview_size)
                preview.fill(sky)
                pygame.draw.rect(preview, ground, (0, preview_size[1]//2, preview_size[0], preview_size[1]//2))
                pygame.draw.rect(preview, plat, (50, 40, 100, 20))
                pygame.draw.rect(preview, plat, (20, 70, 60, 15))
                pygame.draw.rect(preview, plat, (120, 90, 70, 15))
                pygame.draw.circle(preview, star, (preview_size[0]//2, 30), 10)
                pygame.draw.rect(preview, WHITE, (0, 0, preview_size[0], preview_size[1]), 3)
                self.map_previews[map_name] = preview
    
    def handle_events(self, events):
        map_manager = self.manager.map_manager
        
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    self.selected_index = (self.selected_index - 1) % len(map_manager.MAP_ORDER)
                elif event.key == pygame.K_RIGHT:
                    self.selected_index = (self.selected_index + 1) % len(map_manager.MAP_ORDER)
                elif event.key == pygame.K_UP:
                    self.selected_index = max(0, self.selected_index - 3)
                elif event.key == pygame.K_DOWN:
                    self.selected_index = min(len(map_manager.MAP_ORDER)-1, self.selected_index + 3)
                elif event.key in (pygame.K_SPACE, pygame.K_RETURN):
                    map_name = map_manager.MAP_ORDER[self.selected_index]
                    if map_name in map_manager.unlocked_maps:
                        map_manager.load_map(map_name)
                        self.manager.change_state("GAMEPLAY")
                elif event.key == pygame.K_ESCAPE:
                    self.manager.change_state("FILE_SELECT")
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                for i, rect in enumerate(self.grid_rects):
                    if rect.collidepoint(mouse_pos):
                        self.selected_index = i
                        map_name = map_manager.MAP_ORDER[i]
                        if map_name in map_manager.unlocked_maps:
                            map_manager.load_map(map_name)
                            self.manager.change_state("GAMEPLAY")
                        break
    
    def update(self):
        if self.preview_time > 0:
            self.preview_time -= 1
    
    def render(self, screen):
        screen.fill(DEBUG_BLUE)
        title = self.title_font.render("SELECT COURSE", True, DEBUG_YELLOW)
        screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 40))
        
        grid_width = 3
        cell_width = 250
        cell_height = 200
        start_x = (SCREEN_WIDTH - grid_width * cell_width) // 2
        start_y = 120
        
        map_manager = self.manager.map_manager
        self.grid_rects = []
        
        for i, map_name in enumerate(map_manager.MAP_ORDER):
            row = i // grid_width
            col = i % grid_width
            
            x = start_x + col * cell_width
            y = start_y + row * cell_height
            
            is_unlocked = map_name in map_manager.unlocked_maps
            is_selected = (i == self.selected_index)
            
            box_color = (100, 200, 100) if is_unlocked else (100, 100, 100)
            border_color = DEBUG_YELLOW if is_selected else (200, 200, 200)
            
            box_rect = pygame.Rect(x + 10, y + 10, cell_width - 20, cell_height - 20)
            self.grid_rects.append(box_rect) # Save for collision
            
            pygame.draw.rect(screen, box_color, box_rect, border_radius=15)
            pygame.draw.rect(screen, border_color, box_rect, 3 if is_selected else 1, border_radius=15)
            
            if not is_unlocked:
                lock_size = 60
                lock_rect = pygame.Rect(x + cell_width//2 - lock_size//2, y + cell_height//2 - lock_size//2, lock_size, lock_size)
                pygame.draw.rect(screen, (50, 50, 50), lock_rect, border_radius=10)
                pygame.draw.rect(screen, (100, 100, 100), lock_rect, 3, border_radius=10)
                pygame.draw.circle(screen, (150, 150, 150), (lock_rect.centerx, lock_rect.centery - 10), 8)
                pygame.draw.rect(screen, (150, 150, 150), (lock_rect.centerx - 4, lock_rect.centery, 8, 15))
                lock_text = self.small_font.render("LOCKED", True, WHITE)
                screen.blit(lock_text, (lock_rect.centerx - lock_text.get_width()//2, lock_rect.bottom + 10))
            else:
                if map_name in self.map_previews:
                    preview = self.map_previews[map_name]
                    preview_x = box_rect.centerx - preview.get_width()//2
                    preview_y = box_rect.top + 10
                    screen.blit(preview, (preview_x, preview_y))
                
                map_display_name = map_manager.ALL_MAPS[map_name]().name if map_name in map_manager.ALL_MAPS else map_name
                name_text = self.font.render(map_display_name, True, WHITE)
                screen.blit(name_text, (box_rect.centerx - name_text.get_width()//2, box_rect.bottom - 40))
                
                if is_selected:
                    map_obj = map_manager.ALL_MAPS[map_name]()
                    stars_text = self.small_font.render(f"Stars: {map_obj.star_count}", True, YELLOW)
                    screen.blit(stars_text, (box_rect.centerx - stars_text.get_width()//2, box_rect.bottom - 70))
        
        selected_map_name = map_manager.MAP_ORDER[self.selected_index]
        is_unlocked = selected_map_name in map_manager.unlocked_maps
        
        if is_unlocked:
            info_y = start_y + 2 * cell_height + 30
            descriptions = {
                "test": "A simple test course to learn the basics.",
                "bobomb": "Battle Bob-ombs on this grassy battlefield!",
                "whomp": "Scale the stone fortress and defeat Whomp!",
                "jolly": "Dive into the sunken ship in this watery bay.",
                "cool": "Slide down icy slopes in this frozen mountain.",
                "desert": "Navigate shifting sands and ancient pyramids."
            }
            desc = descriptions.get(selected_map_name, "No description available.")
            desc_text = self.small_font.render(desc, True, WHITE)
            screen.blit(desc_text, (50, info_y))
            
            controls_y = info_y + 30 + 20
            controls_text = self.small_font.render("CONTROLS: Arrows-Move, Space-Jump, R-Respawn, D-Debug", True, (200, 200, 200))
            screen.blit(controls_text, (50, controls_y))
        
        if is_unlocked:
            select_text = self.font.render("PRESS ENTER TO START", True, DEBUG_YELLOW)
        else:
            select_text = self.font.render("COLLECT MORE STARS TO UNLOCK", True, RED)
        
        screen.blit(select_text, (SCREEN_WIDTH//2 - select_text.get_width()//2, SCREEN_HEIGHT - 60))
        
        total_stars = map_manager.get_total_stars()
        stars_text = self.font.render(f"TOTAL STARS: {total_stars}", True, YELLOW)
        screen.blit(stars_text, (SCREEN_WIDTH - stars_text.get_width() - 20, 20))

class GameplayState(GameState):
    """
    3D Beta World - Updated to use MapManager
    """
    def __init__(self, manager):
        super().__init__(manager)
        
        # We access map_manager from self.manager
        self.angle = 0 
        self.vel_y = 0
        self.on_ground = True
        self.speed = 0
        self.x = 0
        self.y = 0
        self.z = 0
        
        self.cam_dist = 500
        self.cam_height = 250
        self.fov = 400
        
        self.font = pygame.font.SysFont("couriernew", 20, bold=True)
        self.big_font = pygame.font.SysFont("arial", 36, bold=True)
        
        self.lives = 3
        self.coins = 0
        self.score = 0
        self.respawn_time = 0
        self.show_debug = True

    def on_enter(self):
        """Called whenever we switch to this state"""
        self.respawn()

    def handle_events(self, events):
        map_manager = self.manager.map_manager
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and self.on_ground:
                    self.vel_y = 15
                    self.on_ground = False
                elif event.key == pygame.K_ESCAPE:
                    self.manager.change_state("MAP_SELECT")
                elif event.key == pygame.K_r:
                    self.respawn()
                elif event.key == pygame.K_n:
                    if map_manager.next_map():
                        self.respawn()
                elif event.key == pygame.K_p:
                    if map_manager.previous_map():
                        self.respawn()
                elif event.key == pygame.K_d:
                    self.show_debug = not self.show_debug
                elif event.key == pygame.K_t:
                    self.x, self.y, self.z = map_manager.current_map.spawn_point
                    self.vel_y = 0

    def update(self):
        map_manager = self.manager.map_manager
        
        if self.respawn_time > 0:
            self.respawn_time -= 1
            return
            
        keys = pygame.key.get_pressed()
        
        if keys[pygame.K_LEFT]: self.angle -= 0.05
        if keys[pygame.K_RIGHT]: self.angle += 0.05
            
        if keys[pygame.K_UP]: self.speed = 6
        elif keys[pygame.K_DOWN]: self.speed = -4
        else: self.speed *= 0.85 
            
        old_x, old_z = self.x, self.z
        
        # Calculate proposed new position
        next_x = self.x + math.sin(self.angle) * self.speed
        next_z = self.z + math.cos(self.angle) * self.speed
        
        # --- Horizontal Collision Check ---
        collisions_horiz = map_manager.current_map.check_collision(next_x, self.y, next_z)
        hit_wall = False
        for obj in collisions_horiz:
            if obj.type in ["ground", "platform", "mountain", "fortress", "pyramid"]:
                # If we were not colliding before, but are now, it's a wall
                # Simple check: if vertical separation is not enough to stand on or hit head
                if not (self.y > obj.y + obj.height/2 or self.y < obj.y - obj.height/2):
                    hit_wall = True
                    break
        
        if not hit_wall:
            self.x = next_x
            self.z = next_z
        else:
            self.speed = 0 # Stop if hit wall
        
        # Gravity / Jumping
        self.y += self.vel_y
        self.vel_y -= 0.8
        
        # --- Vertical Collision Check ---
        collisions = map_manager.current_map.check_collision(self.x, self.y, self.z)
        
        self.on_ground = False # Assume falling unless hit ground
        
        for obj in collisions:
            if obj.type in ["ground", "platform", "mountain", "fortress", "pyramid", "pyramid_step"]:
                # Landing on top
                if self.vel_y <= 0 and self.y > obj.y + obj.height/2 - 10:
                    self.y = obj.y + obj.height/2 + 40
                    self.vel_y = 0
                    self.on_ground = True
                # Hitting head
                elif self.vel_y > 0 and self.y < obj.y - obj.height/2 + 10:
                    self.y = obj.y - obj.height/2 - 40
                    self.vel_y = 0
            
            elif obj.type == "star" and not obj.collected:
                obj.collected = True
                map_manager.collect_star()
                self.score += 1000
                if map_manager.get_map_stars() >= map_manager.current_map.star_count:
                    map_manager.unlock_next_map()
            
            elif obj.type == "coin" and not obj.collected:
                obj.collected = True
                self.coins += 1
                self.score += 100
                if self.coins >= 100:
                    self.coins -= 100
                    self.lives += 1
            
            elif obj.type in ["goomba", "enemy", "cactus", "quicksand"]:
                if obj.type == "quicksand":
                     self.lives -= 1
                     self.respawn()
                     return
                     
                if self.vel_y < 0 and obj.type not in ["cactus"]: 
                    self.vel_y = 10
                    self.score += 200
                else: 
                    self.lives -= 1
                    if self.lives <= 0:
                        self.game_over()
                    else:
                        self.respawn_time = 60
                        self.respawn()
        
        if self.y < -500:
            self.lives -= 1
            if self.lives <= 0:
                self.game_over()
            else:
                self.respawn()

    def respawn(self):
        """Respawn player at map spawn point"""
        map_manager = self.manager.map_manager
        self.x, self.y, self.z = map_manager.current_map.spawn_point
        self.vel_y = 0
        self.on_ground = False
        self.angle = 0
        self.speed = 0

    def game_over(self):
        self.lives = 3
        self.coins = 0
        self.score = 0
        self.manager.map_manager.reset_current_map()
        self.respawn()

    def project(self, x, y, z):
        cam_x = self.x - math.sin(self.angle) * self.cam_dist
        cam_z = self.z - math.cos(self.angle) * self.cam_dist
        cam_y = self.y + self.cam_height
        
        dx = x - cam_x
        dy = y - cam_y
        dz = z - cam_z
        
        cos_a = math.cos(-self.angle)
        sin_a = math.sin(-self.angle)
        
        rx = dx * cos_a - dz * sin_a
        rz = dx * sin_a + dz * cos_a
        ry = dy
        
        if rz <= 1:
            return None
            
        scale = self.fov / rz
        screen_x = SCREEN_WIDTH // 2 + rx * scale
        screen_y = SCREEN_HEIGHT // 2 - ry * scale
        
        return (int(screen_x), int(screen_y), scale)

    def render(self, screen):
        map_manager = self.manager.map_manager
        current_map = map_manager.current_map
        
        screen.fill(current_map.sky_color)
        
        if self.show_debug:
            grid_size = 1000
            step = 200
            for i in range(-grid_size, grid_size + 1, step):
                p1 = self.project(i, 0, -grid_size)
                p2 = self.project(i, 0, grid_size)
                if p1 and p2:
                    pygame.draw.line(screen, (0, 100, 0), p1[:2], p2[:2], 1)
                p3 = self.project(-grid_size, 0, i)
                p4 = self.project(grid_size, 0, i)
                if p3 and p4:
                    pygame.draw.line(screen, (0, 100, 0), p3[:2], p4[:2], 1)
        
        # Sort objects by distance for primitive painter's algorithm
        # Calculate distance to camera for all objects
        render_list = []
        for obj in current_map.objects:
            if obj.collected and obj.type in ["star", "coin"]:
                continue
            
            # Distance from camera approx
            dist = math.sqrt((obj.x - self.x)**2 + (obj.z - self.z)**2)
            render_list.append((obj, dist))
            
        # Add mario to render list
        render_list.append(("mario", 0)) # Mario usually close, handled separately
        
        # Simple sort, though proper 3D depth sorting requires more
        # Here we just draw them in order, maybe simple distance sort helps
        render_list.sort(key=lambda x: x[1], reverse=True)
        
        for item, dist in render_list:
            if item == "mario":
                 # Render Mario
                shadow = self.project(self.x, 0, self.z)
                if shadow:
                    sw = int(50 * shadow[2])
                    sh = int(25 * shadow[2])
                    pygame.draw.ellipse(screen, (0, 50, 0, 128), (shadow[0]-sw//2, shadow[1]-sh//2, sw, sh))
                    
                mario = self.project(self.x, self.y, self.z)
                if mario:
                    alpha = 128 if self.respawn_time > 0 and self.respawn_time % 10 < 5 else 255
                    size = int(80 * mario[2])
                    rect = pygame.Rect(mario[0] - size//2, mario[1] - size, size, size)
                    mario_surf = pygame.Surface((size, size), pygame.SRCALPHA)
                    pygame.draw.rect(mario_surf, (*BLUE, alpha), (0, 0, size, size))
                    pygame.draw.rect(mario_surf, (*RED, alpha), (0, 0, size, size // 3))
                    screen.blit(mario_surf, (rect.x, rect.y))
                    dir_length = size
                    end_x = mario[0] + math.sin(self.angle) * dir_length
                    end_y = mario[1] - size//2 - math.cos(self.angle) * dir_length
                    pygame.draw.line(screen, WHITE, (mario[0], mario[1] - size//2), (end_x, end_y), 2)
            else:
                self.draw_object(screen, item)

        self.render_hud(screen)

    def draw_object(self, screen, obj):
        corners = obj.get_corners()
        proj_points = [self.project(*p) for p in corners]
        
        if any(p is None for p in proj_points):
            return
        
        if obj.type == "star":
            self.draw_star(screen, obj)
            return
        if obj.type == "coin":
            self.draw_coin(screen, obj)
            return
        if obj.type in ["goomba", "enemy"]:
            self.draw_enemy(screen, obj)
            return
        
        front_face = [proj_points[i][:2] for i in range(4)]
        
        if obj.type == "ground":
            pygame.draw.polygon(screen, obj.color, front_face)
            for i in range(0, 4, 2):
                pygame.draw.line(screen, (obj.color[0]//2, obj.color[1]//2, obj.color[2]//2), 
                                front_face[i], front_face[(i+1)%4], 1)
        else:
            pygame.draw.polygon(screen, obj.color, front_face)
            pygame.draw.polygon(screen, BLACK, front_face, 2)
            top_face = [proj_points[i+4][:2] for i in range(4)]
            top_color = tuple(min(255, c+30) for c in obj.color)
            pygame.draw.polygon(screen, top_color, top_face)
            pygame.draw.polygon(screen, BLACK, top_face, 1)
            for i in range(4):
                pygame.draw.line(screen, BLACK, front_face[i], top_face[i], 2)

    def draw_star(self, screen, star):
        center = self.project(star.x, star.y, star.z)
        if not center: return
        cx, cy, scale = center
        radius = int(30 * scale)
        time_ms = pygame.time.get_ticks()
        spin_angle = time_ms * 0.01
        bounce = abs(math.sin(time_ms * 0.005)) * 10
        points = []
        for i in range(5):
            angle = spin_angle + i * 2 * math.pi / 5
            x1 = cx + radius * math.cos(angle)
            y1 = cy - bounce + radius * math.sin(angle)
            points.append((x1, y1))
            angle += math.pi / 5
            x2 = cx + radius * 0.5 * math.cos(angle)
            y2 = cy - bounce + radius * 0.5 * math.sin(angle)
            points.append((x2, y2))
        pygame.draw.polygon(screen, YELLOW, points)
        pygame.draw.polygon(screen, (255, 200, 0), points, 3)

    def draw_coin(self, screen, coin):
        center = self.project(coin.x, coin.y, coin.z)
        if not center: return
        cx, cy, scale = center
        radius = int(20 * scale)
        time_ms = pygame.time.get_ticks()
        spin_angle = time_ms * 0.02
        width = radius * 2
        height = int(radius * abs(math.cos(spin_angle)) * 1.5)
        if height > 5:
            pygame.draw.ellipse(screen, (255, 215, 0), (cx - width//2, cy - height//2, width, height))
            pygame.draw.ellipse(screen, (218, 165, 32), (cx - width//2, cy - height//2, width, height), 2)

    def draw_enemy(self, screen, enemy):
        center = self.project(enemy.x, enemy.y, enemy.z)
        if not center: return
        cx, cy, scale = center
        size = int(40 * scale)
        pygame.draw.circle(screen, enemy.color, (cx, cy - size//4), size//2)
        for i in [-1, 1]:
            pygame.draw.circle(screen, (0, 0, 0), (cx + i*size//3, cy + size//3), size//4)
        eye_size = size // 6
        for i in [-1, 1]:
            pygame.draw.circle(screen, WHITE, (cx + i*size//4, cy - size//4), eye_size)
            pygame.draw.circle(screen, BLACK, (cx + i*size//4, cy - size//4), eye_size//2)

    def render_hud(self, screen):
        map_manager = self.manager.map_manager
        hud_bg = pygame.Surface((SCREEN_WIDTH, 100), pygame.SRCALPHA)
        hud_bg.fill((0, 0, 0, 128))
        screen.blit(hud_bg, (0, 0))
        
        map_name = map_manager.get_map_name()
        name_text = self.big_font.render(map_name, True, WHITE)
        screen.blit(name_text, (20, 20))
        
        stars_text = self.font.render(f"STARS: {map_manager.get_map_stars()}/{map_manager.current_map.star_count}", True, YELLOW)
        screen.blit(stars_text, (20, 60))
        
        coins_text = self.font.render(f"COINS: {self.coins:03d}", True, (255, 215, 0))
        screen.blit(coins_text, (SCREEN_WIDTH - 150, 20))
        
        lives_text = self.font.render(f"LIVES: {self.lives}", True, RED)
        screen.blit(lives_text, (SCREEN_WIDTH - 150, 50))
        
        score_text = self.font.render(f"SCORE: {self.score:06d}", True, WHITE)
        screen.blit(score_text, (SCREEN_WIDTH - 200, 80))
        
        if self.show_debug:
            debug_lines = [
                f"POS: ({int(self.x)}, {int(self.y)}, {int(self.z)})",
                f"MAP: {map_manager.MAP_ORDER[map_manager.current_map_index]}",
            ]
            for i, line in enumerate(debug_lines):
                debug_text = self.font.render(line, True, DEBUG_YELLOW)
                screen.blit(debug_text, (SCREEN_WIDTH - 300, 20 + i * 25))
        
        if not self.show_debug:
            controls = self.font.render("ESC: Map Select | D: Debug Info", True, (200, 200, 200))
            screen.blit(controls, (SCREEN_WIDTH//2 - controls.get_width()//2, SCREEN_HEIGHT - 30))

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Ultra Mario 3D N64 - Debug Build")
        self.clock = pygame.time.Clock()
        
        # Initialize Shared Manager
        self.map_manager = MapManager()
        
        self.states = {
            "INTRO": IntroState(self),
            "FILE_SELECT": FileSelectState(self),
            "MAP_SELECT": MapSelectState(self),
            "GAMEPLAY": GameplayState(self)
        }
        self.current_state_name = "INTRO"
        self.current_state = self.states["INTRO"]

    def change_state(self, new_state_name):
        if new_state_name in self.states:
            self.current_state_name = new_state_name
            self.current_state = self.states[new_state_name]
            # Trigger enter event
            self.current_state.on_enter()

    def run(self):
        running = True
        while running:
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    running = False
            
            self.current_state.handle_events(events)
            self.current_state.update()
            self.current_state.render(self.screen)
            
            pygame.display.flip()
            self.clock.tick(FPS)
            
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run()
