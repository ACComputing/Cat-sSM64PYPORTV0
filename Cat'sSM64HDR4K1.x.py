import pygame
import math
import sys
import random
import time

# --- CONSTANTS & CONFIGURATION ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
TILE_SIZE = 40
GRAVITY = 0.6
MAX_FALL_SPEED = 12

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
GREEN = (0, 200, 0)
SKY_BLUE = (135, 206, 235)
GRASS_GREEN = (34, 139, 34)
PARCHMENT = (238, 232, 205)
PARCHMENT_INK = (30, 25, 20)
PARCHMENT_SHADOW = (180, 170, 150)
DEBUG_BLUE = (0, 0, 128)
DEBUG_YELLOW = (255, 255, 0)
COIN_GOLD = (255, 215, 0)
STAR_YELLOW = (255, 255, 100)

# --- LEVEL DATA ---
# Each level: name, bg_color, ground_color, platform_color, theme_extras
# Tile legend: G=ground, P=platform, C=coin, S=star, E=enemy(goomba), K=enemy(koopa),
#              B=enemy(boo), L=lava, W=water, I=ice, N=sand, T=thwomp, .=air

LEVEL_DEFS = [
    {
        "name": "BOB-OMB BATTLEFIELD",
        "sky": (100, 180, 255),
        "ground_color": (80, 160, 50),
        "plat_color": (139, 90, 43),
        "accent": (60, 130, 30),
        "music_hint": "grass",
        "map": [
            "....................",
            ".......C...C.......",
            "....PPPP..PPPP.....",
            "..C................",
            "..PPP.....C........",
            ".........PPP.......",
            "...E.........C..S..",
            "..PPPP....PPPPPPP..",
            ".......E...........",
            "....PPPPPPPP.......",
            "..C................",
            "..PPP.....E...C....",
            ".........PPPPPP....",
            "...E...............",
            "GGGGGGGGGGGGGGGGGGGG",
        ],
    },
    {
        "name": "WHOMP'S FORTRESS",
        "sky": (150, 200, 255),
        "ground_color": (130, 130, 130),
        "plat_color": (160, 160, 160),
        "accent": (100, 100, 110),
        "music_hint": "fortress",
        "map": [
            "..............C.S..",
            "..............PPPP.",
            "...C...............",
            "...PP.....T........",
            "..........PPP......",
            ".....C.............",
            ".....PPPP..........",
            "..........C........",
            "......T...PPP......",
            "...PPPP............",
            "..........C........",
            "..C.......PPPPPP...",
            "..PPP..............",
            "...........E...E...",
            "GGGGGGGGGGGGGGGGGGGG",
        ],
    },
    {
        "name": "JOLLY ROGER BAY",
        "sky": (60, 120, 180),
        "ground_color": (194, 178, 128),
        "plat_color": (100, 140, 100),
        "accent": (40, 100, 160),
        "music_hint": "water",
        "map": [
            "....................",
            "...C.......C.......",
            "...PP.....PP.......",
            "....................",
            "..........C........",
            "........PPPP.......",
            "....C..............",
            "....PPP............",
            ".............C..S..",
            "..W......PPPPPPP...",
            "..WW...............",
            "..WWW....E.........",
            "..WWWW..PPPP.......",
            "..WWWWW............",
            "GGGGGGGGGGGGGGGGGGGG",
        ],
    },
    {
        "name": "COOL COOL MOUNTAIN",
        "sky": (200, 220, 255),
        "ground_color": (230, 230, 245),
        "plat_color": (180, 200, 220),
        "accent": (150, 180, 210),
        "music_hint": "snow",
        "map": [
            "...........S.......",
            "..........PPPP.....",
            "....C..............",
            "....II.............",
            "........C..........",
            "........III........",
            "..C................",
            "..III......C.......",
            "..........III......",
            "....C..............",
            "....III............",
            "..........E..C.....",
            "........IIIIII.....",
            "...E...............",
            "GGGGGGGGGGGGGGGGGGGG",
        ],
    },
    {
        "name": "BIG BOO'S HAUNT",
        "sky": (20, 10, 40),
        "ground_color": (60, 50, 70),
        "plat_color": (80, 70, 90),
        "accent": (100, 80, 120),
        "music_hint": "spooky",
        "map": [
            "..............S....",
            "..............PP...",
            "..C................",
            "..PPP......B.......",
            "..........PPP......",
            ".....C.............",
            ".....PPPP..........",
            "..........B........",
            "..........PPP......",
            "...PPP.............",
            "..........C........",
            "..B.......PPPPPP...",
            "..PPP..............",
            "...........B...B...",
            "GGGGGGGGGGGGGGGGGGGG",
        ],
    },
    {
        "name": "HAZY MAZE CAVE",
        "sky": (30, 25, 40),
        "ground_color": (90, 75, 60),
        "plat_color": (110, 95, 80),
        "accent": (70, 55, 40),
        "music_hint": "cave",
        "map": [
            "....................",
            "...C...........S...",
            "...PP........PPPP..",
            "....................",
            "........C..........",
            "......PPPPP........",
            "....................",
            "..C......E.........",
            "..PPP....PPP.......",
            "..........C........",
            "......PPPPPP.......",
            "..E................",
            "..PPP......C.......",
            ".........PPPP..E...",
            "GGGGGGGGGGGGGGGGGGGG",
        ],
    },
    {
        "name": "LETHAL LAVA LAND",
        "sky": (40, 10, 0),
        "ground_color": (80, 30, 10),
        "plat_color": (120, 50, 20),
        "accent": (200, 60, 0),
        "music_hint": "lava",
        "map": [
            "..............S....",
            "..............PP...",
            "..C................",
            "..PPP..............",
            "........C..........",
            "........PPP........",
            "....C..............",
            "....PPP....C.......",
            "..........PPP......",
            "....................",
            "...PPP.............",
            "..........E..C.....",
            "........PPPPPP.....",
            "...E...............",
            "LLLLLLLLLLLLLLLLLLLL",
        ],
    },
    {
        "name": "SHIFTING SAND LAND",
        "sky": (255, 200, 100),
        "ground_color": (220, 190, 130),
        "plat_color": (200, 170, 100),
        "accent": (180, 150, 80),
        "music_hint": "desert",
        "map": [
            "....................",
            "...........S.......",
            "..........PPPP.....",
            "..C................",
            "..NNN..............",
            "........C..........",
            "........NNN........",
            "..C................",
            "..NNN......C.......",
            "..........NNN......",
            "....C..............",
            "....NNN....E.......",
            "..........NNNNNN...",
            "...E...............",
            "GGGGGGGGGGGGGGGGGGGG",
        ],
    },
    {
        "name": "DIRE DIRE DOCKS",
        "sky": (20, 50, 100),
        "ground_color": (100, 120, 140),
        "plat_color": (80, 100, 130),
        "accent": (30, 70, 120),
        "music_hint": "water",
        "map": [
            "....................",
            "...C.........S.....",
            "...PP......PPPP....",
            "....................",
            "..........C........",
            "........PPPP.......",
            "..W................",
            "..WW...C...........",
            "..WWW..PPP.........",
            "..WWWW.....C.......",
            "..WWWWW..PPPP......",
            "..WWWWWW...........",
            "..WWWWWWW..E.......",
            "..WWWWWWWW.........",
            "GGGGGGGGGGGGGGGGGGGG",
        ],
    },
    {
        "name": "SNOWMAN'S LAND",
        "sky": (180, 200, 230),
        "ground_color": (220, 225, 240),
        "plat_color": (190, 200, 220),
        "accent": (160, 175, 200),
        "music_hint": "snow",
        "map": [
            "..............S....",
            "..............II...",
            "..C................",
            "..III..............",
            "........C..........",
            "........III........",
            "....C..............",
            "....III....E.......",
            "..........III......",
            "..C................",
            "..III..............",
            "..........C........",
            "........IIIIII.....",
            "...E...........E...",
            "GGGGGGGGGGGGGGGGGGGG",
        ],
    },
    {
        "name": "WET DRY WORLD",
        "sky": (140, 170, 200),
        "ground_color": (150, 150, 160),
        "plat_color": (120, 130, 150),
        "accent": (90, 110, 140),
        "music_hint": "fortress",
        "map": [
            "..............S....",
            "..............PP...",
            "..C................",
            "..PPP..............",
            "..WW...C...........",
            "..WWW..PPP.........",
            "..WWWW.............",
            "..WWWWW..C.........",
            "..WWWWW..PPP.......",
            "..WWWW.............",
            "..WWW....E.........",
            "..WW.....PPPPPP....",
            "..W..........C.....",
            "...E...............",
            "GGGGGGGGGGGGGGGGGGGG",
        ],
    },
    {
        "name": "TALL TALL MOUNTAIN",
        "sky": (120, 190, 255),
        "ground_color": (100, 80, 60),
        "plat_color": (130, 110, 80),
        "accent": (80, 65, 45),
        "music_hint": "grass",
        "map": [
            "..S................",
            "..PP...............",
            "......C............",
            "......PPP..........",
            "..........C........",
            "..........PPP......",
            "..............C....",
            "..............PPP..",
            "..........C........",
            "........PPP........",
            "....C..............",
            "....PPP....E.......",
            "..C................",
            "..PPP..........E...",
            "GGGGGGGGGGGGGGGGGGGG",
        ],
    },
    {
        "name": "TINY HUGE ISLAND",
        "sky": (100, 200, 100),
        "ground_color": (80, 160, 70),
        "plat_color": (100, 130, 60),
        "accent": (60, 140, 50),
        "music_hint": "grass",
        "map": [
            "....................",
            "..C..........S.....",
            "..PPP......PPPP....",
            "....................",
            "......C............",
            "......PPPPPPP......",
            "....................",
            "..E......C.........",
            "..PPP....PPP.......",
            "....................",
            "......PPPPPP.......",
            "..C................",
            "..PPP......E..C....",
            ".........PPPP......",
            "GGGGGGGGGGGGGGGGGGGG",
        ],
    },
    {
        "name": "TICK TOCK CLOCK",
        "sky": (40, 30, 50),
        "ground_color": (100, 90, 70),
        "plat_color": (140, 130, 100),
        "accent": (180, 160, 100),
        "music_hint": "cave",
        "map": [
            "..S................",
            "..PP...............",
            "......C............",
            "......PP...........",
            "..........C........",
            "..........PP.......",
            "..T...............C",
            ".............PP....",
            "........C..........",
            "........PP.........",
            "....C.....T........",
            "....PP.............",
            "..C................",
            "..PP...........E...",
            "GGGGGGGGGGGGGGGGGGGG",
        ],
    },
    {
        "name": "RAINBOW RIDE",
        "sky": (60, 20, 100),
        "ground_color": (180, 100, 200),
        "plat_color": (200, 130, 220),
        "accent": (150, 80, 180),
        "music_hint": "sky",
        "map": [
            "..............S....",
            "..............PP...",
            "..C................",
            "..PP...............",
            "......C............",
            "......PP...........",
            "..........C........",
            "..........PP.......",
            "..............C....",
            "..............PP...",
            "..........C........",
            "........PP.........",
            "....C..............",
            "....PP.........E...",
            "GGGGGGGGGGGGGGGGGGGG",
        ],
    },
]


# --- SPRITE CLASSES ---

class Camera:
    def __init__(self):
        self.x = 0
        self.y = 0

    def update(self, target_x, target_y, level_w, level_h):
        self.x = target_x - SCREEN_WIDTH // 2
        self.y = target_y - SCREEN_HEIGHT // 2
        # Clamp
        self.x = max(0, min(self.x, level_w - SCREEN_WIDTH))
        self.y = max(0, min(self.y, level_h - SCREEN_HEIGHT))


class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.w = 28
        self.h = 38
        self.vx = 0
        self.vy = 0
        self.on_ground = False
        self.facing = 1  # 1=right, -1=left
        self.health = 8
        self.max_health = 8
        self.coins = 0
        self.stars = 0
        self.lives = 4
        self.invincible_timer = 0
        self.anim_frame = 0
        self.anim_timer = 0
        self.wall_jump_timer = 0
        self.triple_jump_count = 0
        self.triple_jump_timer = 0
        self.is_crouching = False
        self.is_diving = False
        self.dive_timer = 0
        self.ground_pound = False
        self.gp_timer = 0
        self.dead = False
        self.death_timer = 0
        self.star_collected_timer = 0

    @property
    def rect(self):
        return pygame.Rect(self.x, self.y, self.w, self.h)

    def take_damage(self, amount=1):
        if self.invincible_timer > 0:
            return
        self.health -= amount
        self.invincible_timer = 90  # 1.5 seconds
        if self.health <= 0:
            self.die()

    def die(self):
        self.dead = True
        self.death_timer = 120
        self.vy = -10
        self.lives -= 1

    def collect_coin(self):
        self.coins += 1
        if self.coins % 50 == 0:
            self.lives += 1
        if self.health < self.max_health:
            self.health = min(self.max_health, self.health + 1)

    def collect_star(self):
        self.stars += 1
        self.star_collected_timer = 180

    def update(self, keys, tiles):
        if self.dead:
            self.vy += GRAVITY
            self.y += self.vy
            self.death_timer -= 1
            return

        if self.star_collected_timer > 0:
            self.star_collected_timer -= 1
            return

        if self.invincible_timer > 0:
            self.invincible_timer -= 1

        # --- Input ---
        accel = 0.5
        decel = 0.3
        max_speed = 5
        jump_power = -11
        
        if self.is_crouching:
            max_speed = 1
        
        move_left = keys[pygame.K_LEFT] or keys[pygame.K_a]
        move_right = keys[pygame.K_RIGHT] or keys[pygame.K_d]
        
        if move_left:
            self.vx -= accel
            self.facing = -1
        elif move_right:
            self.vx += accel
            self.facing = 1
        else:
            # Decelerate
            if abs(self.vx) < decel:
                self.vx = 0
            elif self.vx > 0:
                self.vx -= decel
            else:
                self.vx += decel

        self.vx = max(-max_speed, min(max_speed, self.vx))

        # Crouch
        self.is_crouching = (keys[pygame.K_DOWN] or keys[pygame.K_s]) and self.on_ground

        # Ground pound
        if self.ground_pound:
            self.vy = 14
            self.vx = 0
            self.gp_timer -= 1
            if self.gp_timer <= 0:
                self.ground_pound = False

        # Gravity
        self.vy += GRAVITY
        if self.vy > MAX_FALL_SPEED:
            self.vy = MAX_FALL_SPEED

        # --- Horizontal Movement & Collision ---
        self.x += self.vx
        player_rect = self.rect
        for tile in tiles:
            if player_rect.colliderect(tile["rect"]):
                if self.vx > 0:
                    self.x = tile["rect"].left - self.w
                elif self.vx < 0:
                    self.x = tile["rect"].right
                self.vx = 0
                player_rect = self.rect

        # --- Vertical Movement & Collision ---
        self.y += self.vy
        self.on_ground = False
        player_rect = self.rect
        for tile in tiles:
            if player_rect.colliderect(tile["rect"]):
                if self.vy > 0:
                    self.y = tile["rect"].top - self.h
                    self.vy = 0
                    self.on_ground = True
                    self.is_diving = False
                    self.ground_pound = False
                    # Lava damage
                    if tile.get("type") == "lava":
                        self.take_damage(2)
                        self.vy = -12
                elif self.vy < 0:
                    self.y = tile["rect"].bottom
                    self.vy = 0
                player_rect = self.rect

        # Triple jump timer
        if self.triple_jump_timer > 0:
            self.triple_jump_timer -= 1
        else:
            self.triple_jump_count = 0

        # Animation
        self.anim_timer += 1
        if abs(self.vx) > 0.5:
            if self.anim_timer % 8 == 0:
                self.anim_frame = (self.anim_frame + 1) % 4
        else:
            self.anim_frame = 0

        # Fall off screen
        if self.y > 2000:
            self.die()

    def jump(self):
        if self.dead or self.star_collected_timer > 0:
            return
        if self.on_ground:
            self.triple_jump_count += 1
            self.triple_jump_timer = 20
            if self.triple_jump_count >= 3 and abs(self.vx) > 3:
                self.vy = -14  # Triple jump!
                self.triple_jump_count = 0
            else:
                self.vy = -11
            self.on_ground = False

    def ground_pound_start(self):
        if not self.on_ground and not self.ground_pound:
            self.ground_pound = True
            self.gp_timer = 60
            self.vy = 0  # Pause briefly

    def dive(self):
        if not self.on_ground and not self.is_diving:
            self.is_diving = True
            self.vx = self.facing * 8
            self.vy = 2

    def draw(self, screen, cam):
        sx = self.x - cam.x
        sy = self.y - cam.y

        if self.dead:
            # Death animation - spin
            angle = self.death_timer * 10
            surf = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
            # Body red
            pygame.draw.rect(surf, RED, (4, 8, 20, 22))
            pygame.draw.ellipse(surf, (255, 200, 150), (6, 0, 16, 16))
            rotated = pygame.transform.rotate(surf, angle)
            screen.blit(rotated, (sx - rotated.get_width()//2 + self.w//2,
                                   sy - rotated.get_height()//2 + self.h//2))
            return

        # Blink when invincible
        if self.invincible_timer > 0 and (self.invincible_timer // 4) % 2 == 0:
            return

        # --- Procedural Mario ---
        # Flip based on facing
        flip = (self.facing == -1)

        # Create surface
        surf = pygame.Surface((self.w, self.h), pygame.SRCALPHA)

        if self.is_crouching:
            # Crouching Mario - shorter
            # Hat
            pygame.draw.rect(surf, RED, (4, 14, 20, 6))
            # Face
            pygame.draw.ellipse(surf, (255, 200, 150), (6, 16, 16, 12))
            # Eyes
            ex = 16 if not flip else 10
            pygame.draw.rect(surf, (0, 0, 80), (ex, 20, 4, 4))
            # Body
            pygame.draw.rect(surf, RED, (6, 26, 16, 8))
            # Legs tucked
            pygame.draw.rect(surf, (0, 0, 180), (6, 32, 16, 6))
        elif self.ground_pound:
            # Ground pound - butt first
            pygame.draw.rect(surf, (0, 0, 180), (4, 20, 20, 14))  # Pants
            pygame.draw.rect(surf, RED, (6, 8, 16, 14))  # Body
            pygame.draw.ellipse(surf, (255, 200, 150), (8, 0, 12, 12))  # Head
        elif self.is_diving:
            # Diving - horizontal
            pygame.draw.rect(surf, RED, (2, 14, 24, 12))
            pygame.draw.ellipse(surf, (255, 200, 150), (0 if not flip else 18, 12, 12, 12))
            pygame.draw.rect(surf, (0, 0, 180), (2, 24, 24, 8))
        else:
            # Normal / Walking / Jumping
            # === Hat ===
            pygame.draw.rect(surf, RED, (2, 0, 24, 8))
            hat_brim_x = 0 if not flip else 8
            pygame.draw.rect(surf, RED, (hat_brim_x, 6, 20, 4))

            # === Face ===
            pygame.draw.ellipse(surf, (255, 200, 150), (4, 6, 20, 16))

            # === Eyes ===
            ex = 16 if not flip else 8
            pygame.draw.rect(surf, (0, 0, 80), (ex, 12, 5, 5))
            pygame.draw.rect(surf, WHITE, (ex + 1, 12, 2, 2))

            # === Mustache ===
            mx = 10 if not flip else 8
            pygame.draw.rect(surf, (80, 40, 10), (mx, 17, 12, 3))

            # === Body / Overalls ===
            pygame.draw.rect(surf, RED, (4, 20, 20, 6))  # Shirt
            pygame.draw.rect(surf, (0, 0, 180), (6, 24, 16, 8))  # Overalls
            # Overall buttons
            pygame.draw.rect(surf, YELLOW, (9, 25, 3, 3))
            pygame.draw.rect(surf, YELLOW, (16, 25, 3, 3))

            # === Legs (animated) ===
            if not self.on_ground:
                # Jumping pose
                pygame.draw.rect(surf, (0, 0, 180), (4, 30, 8, 6))
                pygame.draw.rect(surf, (0, 0, 180), (16, 30, 8, 6))
                # Shoes
                pygame.draw.rect(surf, (120, 50, 20), (2, 34, 10, 4))
                pygame.draw.rect(surf, (120, 50, 20), (16, 34, 10, 4))
            elif self.anim_frame % 2 == 0:
                # Stand / walk frame 1
                pygame.draw.rect(surf, (0, 0, 180), (6, 30, 7, 5))
                pygame.draw.rect(surf, (0, 0, 180), (15, 30, 7, 5))
                pygame.draw.rect(surf, (120, 50, 20), (5, 34, 8, 4))
                pygame.draw.rect(surf, (120, 50, 20), (15, 34, 8, 4))
            else:
                # Walk frame 2
                pygame.draw.rect(surf, (0, 0, 180), (3, 30, 7, 5))
                pygame.draw.rect(surf, (0, 0, 180), (18, 30, 7, 5))
                pygame.draw.rect(surf, (120, 50, 20), (2, 34, 8, 4))
                pygame.draw.rect(surf, (120, 50, 20), (18, 34, 8, 4))

            # === Arms ===
            if not self.on_ground:
                # Arms up when jumping
                pygame.draw.rect(surf, (255, 200, 150), (0, 16, 5, 4))
                pygame.draw.rect(surf, (255, 200, 150), (23, 16, 5, 4))
            else:
                arm_y = 22 + (1 if self.anim_frame % 2 else 0)
                pygame.draw.rect(surf, (255, 200, 150), (0, arm_y, 5, 6))
                pygame.draw.rect(surf, (255, 200, 150), (23, arm_y, 5, 6))
                # Gloves
                pygame.draw.rect(surf, WHITE, (0, arm_y+4, 5, 3))
                pygame.draw.rect(surf, WHITE, (23, arm_y+4, 5, 3))

        if flip:
            surf = pygame.transform.flip(surf, True, False)

        screen.blit(surf, (sx, sy))


class Coin:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.w = 20
        self.h = 24
        self.collected = False
        self.anim_timer = random.randint(0, 100)
        self.bob_offset = random.uniform(0, math.pi * 2)

    @property
    def rect(self):
        return pygame.Rect(self.x + 4, self.y, 12, self.h)

    def update(self):
        self.anim_timer += 1

    def draw(self, screen, cam):
        if self.collected:
            return
        sx = self.x - cam.x
        sy = self.y - cam.y + math.sin(self.anim_timer * 0.08 + self.bob_offset) * 3

        # Spinning coin effect
        phase = (self.anim_timer % 40) / 40.0
        coin_w = max(2, int(abs(math.sin(phase * math.pi * 2)) * 18))
        cx = sx + (20 - coin_w) // 2

        # Coin body
        pygame.draw.ellipse(screen, COIN_GOLD, (cx, sy, coin_w, 22))
        if coin_w > 6:
            pygame.draw.ellipse(screen, (200, 170, 0), (cx + 2, sy + 2, coin_w - 4, 18))
            # Shine
            if coin_w > 10:
                pygame.draw.ellipse(screen, (255, 250, 200), (cx + coin_w//3, sy + 4, 4, 6))


class Star:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.w = 32
        self.h = 32
        self.collected = False
        self.anim_timer = 0
        self.sparkles = []

    @property
    def rect(self):
        return pygame.Rect(self.x, self.y, self.w, self.h)

    def update(self):
        self.anim_timer += 1
        # Sparkle particles
        if self.anim_timer % 10 == 0 and not self.collected:
            self.sparkles.append({
                "x": self.x + random.randint(-8, 32),
                "y": self.y + random.randint(-8, 32),
                "life": 30,
                "size": random.randint(2, 5)
            })
        for s in self.sparkles:
            s["life"] -= 1
            s["y"] -= 0.5
        self.sparkles = [s for s in self.sparkles if s["life"] > 0]

    def draw(self, screen, cam):
        if self.collected:
            return
        sx = self.x - cam.x
        sy = self.y - cam.y + math.sin(self.anim_timer * 0.05) * 5

        # Draw sparkles behind
        for s in self.sparkles:
            alpha = int((s["life"] / 30.0) * 255)
            spark_surf = pygame.Surface((s["size"]*2, s["size"]*2), pygame.SRCALPHA)
            pygame.draw.circle(spark_surf, (255, 255, 200, alpha),
                             (s["size"], s["size"]), s["size"])
            screen.blit(spark_surf, (s["x"] - cam.x - s["size"],
                                      s["y"] - cam.y - s["size"]))

        # Draw star shape
        points = []
        for i in range(10):
            angle = math.radians(i * 36 - 90)
            r = 16 if i % 2 == 0 else 7
            px = sx + 16 + math.cos(angle) * r
            py = sy + 16 + math.sin(angle) * r
            points.append((px, py))

        glow = abs(math.sin(self.anim_timer * 0.1)) * 40
        color = (255, 255, int(100 + glow))
        pygame.draw.polygon(screen, color, points)
        # Inner star
        inner_pts = []
        for i in range(10):
            angle = math.radians(i * 36 - 90)
            r = 10 if i % 2 == 0 else 4
            px = sx + 16 + math.cos(angle) * r
            py = sy + 16 + math.sin(angle) * r
            inner_pts.append((px, py))
        pygame.draw.polygon(screen, (255, 255, 220), inner_pts)
        # Eyes
        pygame.draw.circle(screen, BLACK, (int(sx + 12), int(sy + 14)), 2)
        pygame.draw.circle(screen, BLACK, (int(sx + 20), int(sy + 14)), 2)


class Goomba:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.w = 30
        self.h = 28
        self.vx = -1.5
        self.vy = 0
        self.alive = True
        self.squish_timer = 0
        self.anim_timer = 0
        self.on_ground = False

    @property
    def rect(self):
        return pygame.Rect(self.x, self.y, self.w, self.h)

    def update(self, tiles):
        if not self.alive:
            self.squish_timer -= 1
            return

        self.anim_timer += 1
        self.vy += GRAVITY
        if self.vy > MAX_FALL_SPEED:
            self.vy = MAX_FALL_SPEED

        # Horizontal
        self.x += self.vx
        r = self.rect
        for t in tiles:
            if r.colliderect(t["rect"]):
                if self.vx > 0:
                    self.x = t["rect"].left - self.w
                elif self.vx < 0:
                    self.x = t["rect"].right
                self.vx *= -1
                r = self.rect

        # Vertical
        self.y += self.vy
        self.on_ground = False
        r = self.rect
        for t in tiles:
            if r.colliderect(t["rect"]):
                if self.vy > 0:
                    self.y = t["rect"].top - self.h
                    self.vy = 0
                    self.on_ground = True
                elif self.vy < 0:
                    self.y = t["rect"].bottom
                    self.vy = 0
                r = self.rect

        # Turn at edges
        if self.on_ground:
            edge_check = pygame.Rect(self.x + (self.w if self.vx > 0 else -5), self.y + self.h + 2, 5, 5)
            on_edge = True
            for t in tiles:
                if edge_check.colliderect(t["rect"]):
                    on_edge = False
                    break
            if on_edge:
                self.vx *= -1

    def stomp(self):
        self.alive = False
        self.squish_timer = 30

    def draw(self, screen, cam):
        sx = self.x - cam.x
        sy = self.y - cam.y

        if not self.alive:
            if self.squish_timer > 0:
                # Squished flat
                pygame.draw.ellipse(screen, (139, 90, 43), (sx, sy + 20, 30, 8))
            return

        # Body (mushroom shape)
        body_bob = math.sin(self.anim_timer * 0.15) * 2
        # Brown dome
        pygame.draw.ellipse(screen, (139, 90, 43), (sx, sy + body_bob, 30, 18))
        pygame.draw.ellipse(screen, (100, 60, 20), (sx + 2, sy + 2 + body_bob, 26, 14))
        # Face area
        pygame.draw.ellipse(screen, (220, 190, 150), (sx + 4, sy + 10 + body_bob, 22, 14))
        # Eyes (angry)
        ey = sy + 13 + body_bob
        # Left eye
        pygame.draw.ellipse(screen, WHITE, (sx + 5, ey, 9, 8))
        pygame.draw.circle(screen, BLACK, (int(sx + 9), int(ey + 4)), 3)
        # Right eye
        pygame.draw.ellipse(screen, WHITE, (sx + 16, ey, 9, 8))
        pygame.draw.circle(screen, BLACK, (int(sx + 20), int(ey + 4)), 3)
        # Angry brows
        pygame.draw.line(screen, BLACK, (sx + 5, ey - 1), (sx + 12, ey + 2), 2)
        pygame.draw.line(screen, BLACK, (sx + 25, ey - 1), (sx + 18, ey + 2), 2)
        # Feet
        foot_offset = 3 if (self.anim_timer // 10) % 2 == 0 else -3
        pygame.draw.ellipse(screen, (20, 20, 20), (sx + 2 + foot_offset, sy + 22, 12, 8))
        pygame.draw.ellipse(screen, (20, 20, 20), (sx + 16 - foot_offset, sy + 22, 12, 8))


class Boo:
    """Big Boo's Haunt ghost enemy - chases when you're not looking"""
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.w = 34
        self.h = 34
        self.alive = True
        self.anim_timer = 0
        self.alpha = 180
        self.target_alpha = 180
        self.original_x = x
        self.original_y = y

    @property
    def rect(self):
        return pygame.Rect(self.x + 2, self.y + 2, self.w - 4, self.h - 4)

    def update(self, player_facing, player_x):
        if not self.alive:
            return
        self.anim_timer += 1

        # Boo behavior: chase when player faces away, hide when facing
        facing_boo = (player_facing == 1 and player_x < self.x) or \
                     (player_facing == -1 and player_x > self.x)

        if facing_boo:
            # Player is facing Boo - become transparent and stop
            self.target_alpha = 80
        else:
            # Player facing away - chase!
            self.target_alpha = 200
            dx = player_x - self.x
            if abs(dx) > 5:
                self.x += (1.5 if dx > 0 else -1.5)

        # Smooth alpha transition
        if self.alpha < self.target_alpha:
            self.alpha = min(self.target_alpha, self.alpha + 5)
        elif self.alpha > self.target_alpha:
            self.alpha = max(self.target_alpha, self.alpha - 5)

        # Bob up/down
        self.y = self.original_y + math.sin(self.anim_timer * 0.04) * 10

    def draw(self, screen, cam):
        if not self.alive:
            return

        sx = self.x - cam.x
        sy = self.y - cam.y

        surf = pygame.Surface((40, 40), pygame.SRCALPHA)

        # Ghost body
        body_color = (255, 255, 255, int(self.alpha))
        pygame.draw.ellipse(surf, body_color, (3, 2, 34, 28))
        # Wavy bottom
        for i in range(4):
            wave_y = 26 + math.sin(self.anim_timer * 0.1 + i) * 3
            pygame.draw.ellipse(surf, body_color,
                              (3 + i * 8, wave_y, 10, 10))

        # Eyes
        eye_alpha = min(255, int(self.alpha + 40))
        eye_color = (0, 0, 0, eye_alpha)
        pygame.draw.ellipse(surf, eye_color, (10, 10, 8, 10))
        pygame.draw.ellipse(surf, eye_color, (22, 10, 8, 10))
        # Pupils
        pygame.draw.ellipse(surf, (180, 0, 0, eye_alpha), (12, 14, 4, 5))
        pygame.draw.ellipse(surf, (180, 0, 0, eye_alpha), (24, 14, 4, 5))
        # Mouth
        pygame.draw.ellipse(surf, eye_color, (14, 22, 12, 6))

        screen.blit(surf, (sx - 3, sy - 2))


class Thwomp:
    """Whomp's Fortress / Tick Tock Clock falling block"""
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.w = TILE_SIZE
        self.h = TILE_SIZE
        self.original_y = y
        self.state = "wait"  # wait, fall, rise
        self.vy = 0
        self.wait_timer = 60
        self.alive = True

    @property
    def rect(self):
        return pygame.Rect(self.x, self.y, self.w, self.h)

    def update(self, player_x):
        if abs(player_x - self.x) < 80:
            if self.state == "wait":
                self.wait_timer -= 1
                if self.wait_timer <= 0:
                    self.state = "fall"
                    self.vy = 0
        else:
            self.wait_timer = 60

        if self.state == "fall":
            self.vy += 0.8
            self.y += self.vy
            if self.y > self.original_y + 200:
                self.state = "rise"
        elif self.state == "rise":
            self.y -= 2
            if self.y <= self.original_y:
                self.y = self.original_y
                self.state = "wait"
                self.wait_timer = 90

    def draw(self, screen, cam):
        sx = self.x - cam.x
        sy = self.y - cam.y

        # Stone block
        pygame.draw.rect(screen, (130, 130, 140), (sx, sy, self.w, self.h))
        pygame.draw.rect(screen, (90, 90, 100), (sx, sy, self.w, self.h), 3)
        # Angry face
        # Eyes
        pygame.draw.rect(screen, WHITE, (sx + 6, sy + 8, 10, 10))
        pygame.draw.rect(screen, WHITE, (sx + 24, sy + 8, 10, 10))
        pygame.draw.rect(screen, BLACK, (sx + 9, sy + 12, 5, 5))
        pygame.draw.rect(screen, BLACK, (sx + 27, sy + 12, 5, 5))
        # Mouth
        pygame.draw.rect(screen, BLACK, (sx + 12, sy + 26, 16, 6))
        # Teeth
        for i in range(4):
            pygame.draw.rect(screen, WHITE, (sx + 13 + i * 4, sy + 26, 3, 3))


class Particle:
    def __init__(self, x, y, color, vel=None, life=30, size=3):
        self.x = x
        self.y = y
        self.color = color
        self.vx = vel[0] if vel else random.uniform(-2, 2)
        self.vy = vel[1] if vel else random.uniform(-4, -1)
        self.life = life
        self.max_life = life
        self.size = size

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.1
        self.life -= 1

    def draw(self, screen, cam):
        if self.life <= 0:
            return
        sx = self.x - cam.x
        sy = self.y - cam.y
        alpha = int((self.life / self.max_life) * 255)
        s = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
        pygame.draw.circle(s, (*self.color, alpha), (self.size, self.size), self.size)
        screen.blit(s, (sx - self.size, sy - self.size))


# --- LEVEL BUILDER ---

def build_level(level_def):
    """Parse a level map into game objects"""
    tiles = []
    coins = []
    stars = []
    enemies = []
    thwomps = []
    player_start = (100, 400)

    tile_map = level_def["map"]
    ground_color = level_def["ground_color"]
    plat_color = level_def["plat_color"]

    for row_i, row in enumerate(tile_map):
        for col_i, cell in enumerate(row):
            x = col_i * TILE_SIZE
            y = row_i * TILE_SIZE

            if cell == 'G':
                tiles.append({
                    "rect": pygame.Rect(x, y, TILE_SIZE, TILE_SIZE),
                    "color": ground_color,
                    "type": "ground"
                })
            elif cell == 'P':
                tiles.append({
                    "rect": pygame.Rect(x, y, TILE_SIZE, TILE_SIZE),
                    "color": plat_color,
                    "type": "platform"
                })
            elif cell == 'I':
                tiles.append({
                    "rect": pygame.Rect(x, y, TILE_SIZE, TILE_SIZE),
                    "color": (180, 210, 240),
                    "type": "ice"
                })
            elif cell == 'N':
                tiles.append({
                    "rect": pygame.Rect(x, y, TILE_SIZE, TILE_SIZE),
                    "color": (210, 180, 120),
                    "type": "sand"
                })
            elif cell == 'L':
                tiles.append({
                    "rect": pygame.Rect(x, y, TILE_SIZE, TILE_SIZE),
                    "color": (220, 80, 0),
                    "type": "lava"
                })
            elif cell == 'W':
                tiles.append({
                    "rect": pygame.Rect(x, y, TILE_SIZE, TILE_SIZE),
                    "color": (30, 100, 200),
                    "type": "water"
                })
            elif cell == 'C':
                coins.append(Coin(x + 10, y + 8))
            elif cell == 'S':
                stars.append(Star(x + 4, y + 4))
            elif cell == 'E':
                enemies.append(Goomba(x, y - 28))
            elif cell == 'B':
                enemies.append(Boo(x, y))
            elif cell == 'T':
                thwomps.append(Thwomp(x, y))

    # Find a good starting position (leftmost ground tile area)
    for row_i in range(len(tile_map) - 2, -1, -1):
        for col_i in range(len(tile_map[row_i])):
            if tile_map[row_i][col_i] == '.' and row_i + 1 < len(tile_map) and tile_map[row_i + 1][col_i] == 'G':
                player_start = (col_i * TILE_SIZE + 5, row_i * TILE_SIZE - 38)
                break
        else:
            continue
        break

    return tiles, coins, stars, enemies, thwomps, player_start


# --- HUD ---

def draw_hud(screen, player, level_name):
    # Semi-transparent HUD bar
    hud_surf = pygame.Surface((SCREEN_WIDTH, 50), pygame.SRCALPHA)
    hud_surf.fill((0, 0, 0, 140))
    screen.blit(hud_surf, (0, 0))

    hud_font = pygame.font.SysFont("arial", 22, bold=True)

    # Health meter (pie wedges like SM64)
    health_x = 20
    health_y = 25
    for i in range(player.max_health):
        angle_start = math.radians(i * (360 / player.max_health))
        angle_end = math.radians((i + 1) * (360 / player.max_health))
        color = (60, 180, 255) if i < player.health else (60, 60, 60)
        # Draw as small circles around center
        ax = health_x + math.cos(angle_start + 0.2) * 14
        ay = health_y + math.sin(angle_start + 0.2) * 14
        pygame.draw.circle(screen, color, (int(ax), int(ay)), 5)

    # Coins
    coin_text = hud_font.render(f"x {player.coins}", True, COIN_GOLD)
    # Mini coin icon
    pygame.draw.ellipse(screen, COIN_GOLD, (80, 12, 16, 20))
    pygame.draw.ellipse(screen, (200, 170, 0), (82, 14, 12, 16))
    screen.blit(coin_text, (100, 12))

    # Stars
    star_text = hud_font.render(f"x {player.stars}", True, STAR_YELLOW)
    # Mini star
    pts = []
    for j in range(10):
        a = math.radians(j * 36 - 90)
        r = 10 if j % 2 == 0 else 4
        pts.append((200 + math.cos(a) * r, 22 + math.sin(a) * r))
    pygame.draw.polygon(screen, STAR_YELLOW, pts)
    screen.blit(star_text, (215, 12))

    # Lives
    lives_text = hud_font.render(f"LIVES: {player.lives}", True, WHITE)
    screen.blit(lives_text, (320, 12))

    # Level name
    name_text = hud_font.render(level_name, True, WHITE)
    screen.blit(name_text, (SCREEN_WIDTH - name_text.get_width() - 20, 12))


def draw_star_get_screen(screen, star_timer):
    """SM64 Star Get! overlay"""
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    alpha = min(180, star_timer * 3)
    overlay.fill((255, 255, 200, alpha))
    screen.blit(overlay, (0, 0))

    big_font = pygame.font.SysFont("arial", 64, bold=True)
    sub_font = pygame.font.SysFont("arial", 32, bold=True)

    # Bouncy star text
    bounce = abs(math.sin(star_timer * 0.08)) * 20
    text = big_font.render("STAR GET!", True, (200, 150, 0))
    screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2,
                       SCREEN_HEIGHT // 2 - 60 - bounce))

    # Draw big rotating star
    cx, cy = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 40
    rotation = star_timer * 3
    pts = []
    for i in range(10):
        a = math.radians(i * 36 - 90 + rotation)
        r = 50 if i % 2 == 0 else 20
        pts.append((cx + math.cos(a) * r, cy + math.sin(a) * r))
    pygame.draw.polygon(screen, STAR_YELLOW, pts)
    pygame.draw.polygon(screen, (255, 255, 220), pts, 3)


# --- STATE MANAGEMENT ---

class GameState:
    def __init__(self, manager):
        self.manager = manager
    def handle_events(self, events):
        pass
    def update(self):
        pass
    def render(self, screen):
        pass


class IntroState(GameState):
    def __init__(self, manager):
        super().__init__(manager)

        self.lines = [
            "Dear Mario,",
            "Please come to the",
            "castle. I've baked",
            "a cake for you.",
            "",
            "Yours truly--",
            "Princess Toadstool"
        ]

        self.font = pygame.font.SysFont("georgia", 38, bold=True)
        if not self.font:
            self.font = pygame.font.SysFont("timesnewroman", 38, bold=True)
        self.sig_font = pygame.font.SysFont("brushscriptmt", 46, italic=True)
        if not self.sig_font:
            self.sig_font = pygame.font.SysFont("arial", 40, bold=True, italic=True)

        self.parchment_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self._render_parchment()

    def _render_parchment(self):
        self.parchment_surf.fill(PARCHMENT)
        border_margin = 30
        border_color = (139, 69, 19)
        pygame.draw.rect(self.parchment_surf, border_color,
                         (border_margin, border_margin,
                          SCREEN_WIDTH - 2*border_margin,
                          SCREEN_HEIGHT - 2*border_margin), 5)
        inner_margin = border_margin + 8
        pygame.draw.rect(self.parchment_surf, border_color,
                         (inner_margin, inner_margin,
                          SCREEN_WIDTH - 2*inner_margin,
                          SCREEN_HEIGHT - 2*inner_margin), 2)

        start_y = 150
        line_height = 55
        for i, line in enumerate(self.lines):
            is_sig = (i == len(self.lines) - 1)
            is_yours = (i == len(self.lines) - 2)
            is_sal = (i == 0)
            font = self.sig_font if is_sig else self.font
            color = (220, 20, 60) if is_sig else PARCHMENT_INK

            rendered = font.render(line, True, color)
            shadow = font.render(line, True, PARCHMENT_SHADOW)
            text_w = rendered.get_width()

            if is_sal:
                pos_x = border_margin + 70
            elif is_sig or is_yours:
                pos_x = SCREEN_WIDTH - text_w - border_margin - 70
            else:
                pos_x = (SCREEN_WIDTH - text_w) // 2

            if not is_sig:
                self.parchment_surf.blit(shadow, (pos_x + 2, start_y + 2))
            self.parchment_surf.blit(rendered, (pos_x, start_y))
            start_y += line_height

    def handle_events(self, events):
        for e in events:
            if e.type == pygame.KEYDOWN:
                if e.key in (pygame.K_SPACE, pygame.K_RETURN, pygame.K_ESCAPE, pygame.K_x):
                    self.manager.change_state("LEVEL_SELECT")
            if e.type == pygame.MOUSEBUTTONDOWN:
                self.manager.change_state("LEVEL_SELECT")

    def render(self, screen):
        screen.blit(self.parchment_surf, (0, 0))
        pulse = abs(math.sin(pygame.time.get_ticks() * 0.005)) * 255
        pf = pygame.font.SysFont("arial", 24, bold=True)
        prompt = pf.render("- PRESS START -", True, (80, 40, 0))
        prompt.set_alpha(int(pulse))
        screen.blit(prompt, (SCREEN_WIDTH//2 - prompt.get_width()//2, SCREEN_HEIGHT - 60))


class LevelSelectState(GameState):
    """Debug-style level select with all 15 SM64 levels"""
    def __init__(self, manager):
        super().__init__(manager)
        self.font = pygame.font.SysFont("couriernew", 20, bold=True)
        self.title_font = pygame.font.SysFont("couriernew", 26, bold=True)
        self.small_font = pygame.font.SysFont("couriernew", 14)
        self.selected = 0
        self.scroll_offset = 0
        self.visible_count = 12
        self.blink = 0

    def handle_events(self, events):
        for e in events:
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_UP:
                    self.selected = (self.selected - 1) % len(LEVEL_DEFS)
                elif e.key == pygame.K_DOWN:
                    self.selected = (self.selected + 1) % len(LEVEL_DEFS)
                elif e.key in (pygame.K_RETURN, pygame.K_SPACE):
                    self.manager.start_level(self.selected)
                elif e.key == pygame.K_ESCAPE:
                    self.manager.change_state("INTRO")

        # Adjust scroll
        if self.selected < self.scroll_offset:
            self.scroll_offset = self.selected
        elif self.selected >= self.scroll_offset + self.visible_count:
            self.scroll_offset = self.selected - self.visible_count + 1

    def update(self):
        self.blink += 1

    def render(self, screen):
        screen.fill(DEBUG_BLUE)

        # Header
        header = self.title_font.render("SUPER MARIO 64 - LEVEL SELECT", True, WHITE)
        screen.blit(header, (40, 30))

        build = self.small_font.render("BUILD 95-07-29  RSP:OK  RDP:OK  Z-BUF:ON", True, (180, 180, 200))
        screen.blit(build, (40, 60))

        fps_t = self.small_font.render(f"FPS: {int(self.manager.clock.get_fps())}", True, WHITE)
        screen.blit(fps_t, (SCREEN_WIDTH - 120, 30))

        # Separator
        pygame.draw.line(screen, (60, 60, 160), (40, 85), (SCREEN_WIDTH - 40, 85), 1)

        # Level list
        start_y = 100
        line_h = 36

        for i in range(self.scroll_offset, min(self.scroll_offset + self.visible_count, len(LEVEL_DEFS))):
            ldef = LEVEL_DEFS[i]
            is_sel = (i == self.selected)
            y = start_y + (i - self.scroll_offset) * line_h

            if is_sel:
                # Highlight bar
                pygame.draw.rect(screen, (40, 40, 120),
                               (50, y - 2, SCREEN_WIDTH - 100, line_h - 4))
                # Cursor
                cursor = self.font.render(">", True, DEBUG_YELLOW)
                screen.blit(cursor, (55, y + 2))

            # Level number
            num_str = f"{i+1:02d}"
            num = self.font.render(num_str, True, (120, 120, 180))
            screen.blit(num, (80, y + 2))

            # Level name
            color = DEBUG_YELLOW if is_sel else WHITE
            name = self.font.render(ldef["name"], True, color)
            screen.blit(name, (130, y + 2))

            # Theme preview (small color swatch)
            pygame.draw.rect(screen, ldef["sky"], (SCREEN_WIDTH - 120, y + 4, 20, 20))
            pygame.draw.rect(screen, ldef["ground_color"], (SCREEN_WIDTH - 96, y + 4, 20, 20))
            pygame.draw.rect(screen, ldef["plat_color"], (SCREEN_WIDTH - 72, y + 4, 20, 20))

        # Scroll indicators
        if self.scroll_offset > 0:
            up_arrow = self.font.render("^ MORE ^", True, (150, 150, 200))
            screen.blit(up_arrow, (SCREEN_WIDTH//2 - up_arrow.get_width()//2, 88))
        if self.scroll_offset + self.visible_count < len(LEVEL_DEFS):
            dn_arrow = self.font.render("v MORE v", True, (150, 150, 200))
            screen.blit(dn_arrow, (SCREEN_WIDTH//2 - dn_arrow.get_width()//2,
                                    start_y + self.visible_count * line_h))

        # Controls help
        ctrl_y = SCREEN_HEIGHT - 80
        pygame.draw.line(screen, (60, 60, 160), (40, ctrl_y - 10), (SCREEN_WIDTH - 40, ctrl_y - 10), 1)

        controls = [
            "ARROW KEYS: Navigate  |  ENTER: Start Level  |  ESC: Back",
            "IN-GAME: Arrows/WASD=Move  Z=Jump  X=Dive  C=Ground Pound"
        ]
        for j, c in enumerate(controls):
            ct = self.small_font.render(c, True, (150, 150, 200))
            screen.blit(ct, (40, ctrl_y + j * 20))

        # Footer
        footer = self.small_font.render("CONFIDENTIAL - NINTENDO EAD - NOT FOR DISTRIBUTION", True, (80, 80, 140))
        screen.blit(footer, (40, SCREEN_HEIGHT - 25))


class GameplayState(GameState):
    """Full platforming gameplay state"""
    def __init__(self, manager, level_index=0):
        super().__init__(manager)
        self.level_index = level_index
        self.level_def = LEVEL_DEFS[level_index]
        self.tiles, self.coins, self.stars, self.enemies, self.thwomps, player_start = build_level(self.level_def)
        self.player = Player(*player_start)
        self.camera = Camera()
        self.particles = []
        self.paused = False
        self.pause_selected = 0
        self.pause_font = pygame.font.SysFont("arial", 36, bold=True)
        self.complete = False
        self.complete_timer = 0
        self.lava_anim = 0
        self.water_anim = 0

        # Level dimensions
        map_data = self.level_def["map"]
        self.level_w = len(map_data[0]) * TILE_SIZE
        self.level_h = len(map_data) * TILE_SIZE

    def handle_events(self, events):
        for e in events:
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    if self.paused:
                        self.paused = False
                    else:
                        self.paused = True
                        self.pause_selected = 0

                if self.paused:
                    if e.key == pygame.K_UP:
                        self.pause_selected = (self.pause_selected - 1) % 3
                    elif e.key == pygame.K_DOWN:
                        self.pause_selected = (self.pause_selected + 1) % 3
                    elif e.key in (pygame.K_RETURN, pygame.K_SPACE):
                        if self.pause_selected == 0:  # Resume
                            self.paused = False
                        elif self.pause_selected == 1:  # Restart
                            self.manager.start_level(self.level_index)
                        elif self.pause_selected == 2:  # Quit
                            self.manager.change_state("LEVEL_SELECT")
                    return

                if e.key in (pygame.K_z, pygame.K_SPACE, pygame.K_UP, pygame.K_w):
                    self.player.jump()
                elif e.key == pygame.K_x:
                    self.player.dive()
                elif e.key in (pygame.K_c, pygame.K_DOWN, pygame.K_s):
                    if not self.player.on_ground:
                        self.player.ground_pound_start()

    def update(self):
        if self.paused:
            return
        if self.complete:
            self.complete_timer -= 1
            if self.complete_timer <= 0:
                self.manager.change_state("LEVEL_SELECT")
            return

        keys = pygame.key.get_pressed()
        self.player.update(keys, self.tiles)

        # Death handling
        if self.player.dead and self.player.death_timer <= 0:
            if self.player.lives > 0:
                self.manager.start_level(self.level_index)
            else:
                self.manager.change_state("LEVEL_SELECT")
            return

        # Camera
        self.camera.update(self.player.x + self.player.w // 2,
                          self.player.y + self.player.h // 2,
                          self.level_w, self.level_h)

        # Coins
        for coin in self.coins:
            coin.update()
            if not coin.collected and self.player.rect.colliderect(coin.rect):
                coin.collected = True
                self.player.collect_coin()
                # Coin particles
                for _ in range(8):
                    self.particles.append(
                        Particle(coin.x + 10, coin.y + 10, (255, 215, 0),
                                vel=(random.uniform(-3, 3), random.uniform(-5, -1)),
                                life=20, size=3))

        # Stars
        for star in self.stars:
            star.update()
            if not star.collected and self.player.rect.colliderect(star.rect):
                star.collected = True
                self.player.collect_star()
                # Big star particles
                for _ in range(30):
                    self.particles.append(
                        Particle(star.x + 16, star.y + 16,
                                random.choice([(255, 255, 100), (255, 200, 50), (255, 255, 255)]),
                                vel=(random.uniform(-5, 5), random.uniform(-8, -2)),
                                life=60, size=random.randint(2, 6)))

        # Check if all stars collected
        all_stars = all(s.collected for s in self.stars) and len(self.stars) > 0
        if all_stars and self.player.star_collected_timer == 1:
            self.complete = True
            self.complete_timer = 180

        # Enemies
        for enemy in self.enemies:
            if isinstance(enemy, Goomba):
                enemy.update(self.tiles)
                if enemy.alive and self.player.rect.colliderect(enemy.rect):
                    # Check if stomping
                    if self.player.vy > 0 and self.player.y + self.player.h - 10 < enemy.y + 5:
                        enemy.stomp()
                        self.player.vy = -8
                        self.player.coins += 1
                        for _ in range(5):
                            self.particles.append(
                                Particle(enemy.x + 15, enemy.y, (139, 90, 43),
                                        life=20, size=2))
                    elif self.player.ground_pound and self.player.vy > 0:
                        enemy.stomp()
                        for _ in range(8):
                            self.particles.append(
                                Particle(enemy.x + 15, enemy.y, (139, 90, 43),
                                        vel=(random.uniform(-4, 4), random.uniform(-6, -2)),
                                        life=25, size=3))
                    else:
                        self.player.take_damage()
            elif isinstance(enemy, Boo):
                enemy.update(self.player.facing, self.player.x)
                if enemy.alive and enemy.alpha > 150:
                    if self.player.rect.colliderect(enemy.rect):
                        self.player.take_damage()

        # Thwomps
        for thwomp in self.thwomps:
            thwomp.update(self.player.x)
            if self.player.rect.colliderect(thwomp.rect):
                if self.player.vy > 0 and self.player.y + self.player.h < thwomp.y + 15:
                    self.player.y = thwomp.y - self.player.h
                    self.player.vy = 0
                    self.player.on_ground = True
                else:
                    self.player.take_damage()

        # Particles
        for p in self.particles:
            p.update()
        self.particles = [p for p in self.particles if p.life > 0]

        # Anim counters
        self.lava_anim += 1
        self.water_anim += 1

    def render(self, screen):
        # Sky
        screen.fill(self.level_def["sky"])

        # Background decorations based on theme
        self._draw_bg_decor(screen)

        # Tiles
        for tile in self.tiles:
            sx = tile["rect"].x - self.camera.x
            sy = tile["rect"].y - self.camera.y
            r = pygame.Rect(sx, sy, TILE_SIZE, TILE_SIZE)

            if tile["type"] == "lava":
                # Animated lava
                base = tile["color"]
                flicker = int(math.sin(self.lava_anim * 0.1 + tile["rect"].x * 0.05) * 30)
                color = (min(255, base[0] + flicker), max(0, base[1] + flicker // 2), base[2])
                pygame.draw.rect(screen, color, r)
                # Lava surface shine
                for i in range(3):
                    lx = sx + random.randint(0, TILE_SIZE)
                    ly = sy + 2
                    pygame.draw.circle(screen, (255, 200, 50), (lx, ly), random.randint(1, 3))
            elif tile["type"] == "water":
                # Animated water
                wave = int(math.sin(self.water_anim * 0.05 + tile["rect"].x * 0.03) * 10)
                color = (30, max(0, 100 + wave), min(255, 200 + wave))
                pygame.draw.rect(screen, color, r)
                # Surface ripples
                if sy < SCREEN_HEIGHT:
                    ry = sy + 2
                    pygame.draw.line(screen, (80, 160, 255), (sx, ry), (sx + TILE_SIZE, ry + 2), 1)
            elif tile["type"] == "ice":
                pygame.draw.rect(screen, tile["color"], r)
                # Ice shine
                pygame.draw.line(screen, (220, 240, 255), (sx + 3, sy + 3), (sx + 15, sy + 15), 1)
                pygame.draw.line(screen, (220, 240, 255), (sx + 20, sy + 5), (sx + 30, sy + 10), 1)
            elif tile["type"] == "sand":
                pygame.draw.rect(screen, tile["color"], r)
                # Sand dots
                for _ in range(3):
                    dx = random.randint(2, TILE_SIZE - 2)
                    dy = random.randint(2, TILE_SIZE - 2)
                    pygame.draw.circle(screen, (190, 160, 100), (sx + dx, sy + dy), 1)
            else:
                pygame.draw.rect(screen, tile["color"], r)
                # Ground/platform detail
                darker = tuple(max(0, c - 30) for c in tile["color"])
                pygame.draw.rect(screen, darker, r, 2)
                # Top highlight
                lighter = tuple(min(255, c + 40) for c in tile["color"])
                pygame.draw.line(screen, lighter, (sx, sy), (sx + TILE_SIZE, sy), 2)

        # Coins
        for coin in self.coins:
            coin.draw(screen, self.camera)

        # Stars
        for star in self.stars:
            star.draw(screen, self.camera)

        # Enemies
        for enemy in self.enemies:
            enemy.draw(screen, self.camera)

        # Thwomps
        for thwomp in self.thwomps:
            thwomp.draw(screen, self.camera)

        # Particles
        for p in self.particles:
            p.draw(screen, self.camera)

        # Player
        self.player.draw(screen, self.camera)

        # HUD
        draw_hud(screen, self.player, self.level_def["name"])

        # Star Get overlay
        if self.player.star_collected_timer > 0:
            draw_star_get_screen(screen, 180 - self.player.star_collected_timer)

        # Pause menu
        if self.paused:
            self._draw_pause(screen)

        # Level complete overlay
        if self.complete:
            self._draw_complete(screen)

    def _draw_bg_decor(self, screen):
        """Theme-specific background decorations"""
        theme = self.level_def["music_hint"]
        t = pygame.time.get_ticks()

        if theme == "grass":
            # Distant hills
            for i in range(5):
                hx = (i * 250 - self.camera.x * 0.2) % (SCREEN_WIDTH + 200) - 100
                hy = SCREEN_HEIGHT - 200
                color = tuple(min(255, c + 30) for c in self.level_def["sky"])
                pygame.draw.ellipse(screen, color, (hx, hy, 300, 150))

        elif theme == "snow":
            # Snowflakes
            for i in range(20):
                sx = (i * 47 + t // 20) % SCREEN_WIDTH
                sy = (i * 31 + t // 15) % SCREEN_HEIGHT
                pygame.draw.circle(screen, WHITE, (sx, sy), 2)

        elif theme == "spooky":
            # Fog
            fog = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            alpha = int(abs(math.sin(t * 0.001)) * 40) + 20
            fog.fill((100, 80, 120, alpha))
            screen.blit(fog, (0, 0))

        elif theme == "lava":
            # Heat haze at top
            for i in range(SCREEN_WIDTH // 10):
                hx = i * 10
                hy = int(math.sin(t * 0.003 + i * 0.5) * 5) + 5
                pygame.draw.line(screen, (60, 20, 0, 80), (hx, hy), (hx + 10, hy), 2)

        elif theme == "cave":
            # Stalactites
            for i in range(8):
                cx = (i * 120 - int(self.camera.x * 0.1)) % (SCREEN_WIDTH + 60) - 30
                pygame.draw.polygon(screen, (50, 40, 35),
                                   [(cx, 0), (cx + 15, 60), (cx + 30, 0)])

        elif theme == "desert":
            # Distant pyramids
            for i in range(3):
                px = (i * 350 - int(self.camera.x * 0.15)) % (SCREEN_WIDTH + 200) - 100
                py = SCREEN_HEIGHT - 250
                pygame.draw.polygon(screen, (200, 170, 100),
                                   [(px, py + 100), (px + 60, py), (px + 120, py + 100)])

        elif theme == "sky":
            # Rainbow stripes
            rainbow_colors = [(255, 0, 0), (255, 127, 0), (255, 255, 0),
                            (0, 255, 0), (0, 0, 255), (75, 0, 130), (148, 0, 211)]
            for i, rc in enumerate(rainbow_colors):
                stripe_y = 50 + i * 15
                stripe_surf = pygame.Surface((SCREEN_WIDTH, 12), pygame.SRCALPHA)
                stripe_surf.fill((*rc, 40))
                screen.blit(stripe_surf, (0, stripe_y))

        elif theme == "water":
            # Light rays from above
            for i in range(5):
                rx = (i * 180 + int(t * 0.02)) % SCREEN_WIDTH
                ray_surf = pygame.Surface((30, SCREEN_HEIGHT), pygame.SRCALPHA)
                ray_surf.fill((200, 220, 255, 15))
                screen.blit(ray_surf, (rx, 0))

        elif theme == "fortress":
            # Brick pattern overlay
            for row in range(0, SCREEN_HEIGHT, 40):
                offset = 20 if (row // 40) % 2 else 0
                for col in range(-20 + offset, SCREEN_WIDTH + 20, 40):
                    pygame.draw.rect(screen, (0, 0, 0, 10),
                                   (col, row, 38, 18), 1)

    def _draw_pause(self, screen):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        screen.blit(overlay, (0, 0))

        title = self.pause_font.render("PAUSED", True, WHITE)
        screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 180))

        options = ["CONTINUE", "RESTART", "EXIT TO MENU"]
        for i, opt in enumerate(options):
            is_sel = (i == self.pause_selected)
            color = YELLOW if is_sel else WHITE
            prefix = "> " if is_sel else "  "
            text = self.pause_font.render(prefix + opt, True, color)
            screen.blit(text, (SCREEN_WIDTH//2 - text.get_width()//2, 260 + i * 50))

    def _draw_complete(self, screen):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        alpha = min(200, (180 - self.complete_timer) * 3)
        overlay.fill((0, 0, 0, alpha))
        screen.blit(overlay, (0, 0))

        big = pygame.font.SysFont("arial", 52, bold=True)
        sub = pygame.font.SysFont("arial", 28, bold=True)

        text = big.render("COURSE CLEAR!", True, STAR_YELLOW)
        screen.blit(text, (SCREEN_WIDTH//2 - text.get_width()//2, 200))

        coins_t = sub.render(f"COINS: {self.player.coins}", True, COIN_GOLD)
        screen.blit(coins_t, (SCREEN_WIDTH//2 - coins_t.get_width()//2, 300))

        stars_t = sub.render(f"STARS: {self.player.stars}", True, STAR_YELLOW)
        screen.blit(stars_t, (SCREEN_WIDTH//2 - stars_t.get_width()//2, 340))


# --- GAME MANAGER ---

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Ultra Mario 3D N64 - Debug Build")
        self.clock = pygame.time.Clock()

        self.states = {
            "INTRO": IntroState(self),
            "LEVEL_SELECT": LevelSelectState(self),
        }
        self.current_state_name = "INTRO"
        self.current_state = self.states["INTRO"]

    def change_state(self, name):
        if name not in self.states:
            if name == "LEVEL_SELECT":
                self.states["LEVEL_SELECT"] = LevelSelectState(self)
        self.current_state_name = name
        self.current_state = self.states[name]

    def start_level(self, level_index):
        state = GameplayState(self, level_index)
        self.states["GAMEPLAY"] = state
        self.current_state_name = "GAMEPLAY"
        self.current_state = state

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
