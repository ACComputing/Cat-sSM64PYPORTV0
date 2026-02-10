import pygame
import math
import sys
import random
import time

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
PARCHMENT = (238, 232, 205)  # Authentic creamy parchment color
PARCHMENT_INK = (30, 25, 20) # Almost black, very dark brown
PARCHMENT_SHADOW = (180, 170, 150) # Darker parchment for text shadow
DEBUG_BLUE = (0, 0, 128)     # Classic N64 debug background blue
DEBUG_YELLOW = (255, 255, 0) # Highlight color

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
        # Body: Try Georgia (closest to N64), then Times
        self.font = pygame.font.SysFont("georgia", 38, bold=True)
        if not self.font:
            self.font = pygame.font.SysFont("timesnewroman", 38, bold=True)
            
        # Signature: Try Brush Script, then Corsiva, then fallback
        self.sig_font = pygame.font.SysFont("brushscriptmt", 46, italic=True)
        if not self.sig_font:
             self.sig_font = pygame.font.SysFont("arial", 40, bold=True, italic=True)

        # Make parchment fill the entire screen
        self.parchment_w = SCREEN_WIDTH
        self.parchment_h = SCREEN_HEIGHT
        self.parchment_surf = pygame.Surface((self.parchment_w, self.parchment_h))
        self._render_parchment_texture()

    def _render_parchment_texture(self):
        # 1. Fill background
        self.parchment_surf.fill(PARCHMENT)
        
        # 2. Draw SM64 Style Border
        border_margin = 30
        
        # Outer darker border
        border_color = (139, 69, 19) # SaddleBrown
        pygame.draw.rect(self.parchment_surf, border_color, 
                         (border_margin, border_margin, 
                          self.parchment_w - 2*border_margin, 
                          self.parchment_h - 2*border_margin), 5)
        
        # Inner thin border
        inner_margin = border_margin + 8
        pygame.draw.rect(self.parchment_surf, border_color, 
                         (inner_margin, inner_margin, 
                          self.parchment_w - 2*inner_margin, 
                          self.parchment_h - 2*inner_margin), 2)

        # 3. Draw Text
        start_y = 150
        line_height = 55
        
        for i, line in enumerate(self.lines):
            is_signature = (i == len(self.lines) - 1)  # "Princess Toadstool"
            is_yours_truly = (i == len(self.lines) - 2)  # "Yours truly--"
            is_salutation = (i == 0)  # "Dear Mario,"
            
            # Select Font
            font = self.sig_font if is_signature else self.font
            
            # Select Color
            if is_signature:
                color = (220, 20, 60)  # Crimson Red
            else:
                color = PARCHMENT_INK
            
            # Render Main Text
            rendered_line = font.render(line, True, color)
            
            # Render Shadow (Solid color to prevent artifacts)
            shadow_color = PARCHMENT_SHADOW
            rendered_shadow = font.render(line, True, shadow_color)

            # Alignment Logic
            text_w = rendered_line.get_width()
            
            if is_salutation:
                # Left aligned with indentation
                pos_x = border_margin + 70
            elif is_signature or is_yours_truly:
                # Right aligned
                pos_x = self.parchment_w - text_w - border_margin - 70
            else:
                # Centered
                pos_x = (self.parchment_w - text_w) // 2
            
            # Draw Shadow first (offset) - SKIP shadow for signature to be cleaner
            if not is_signature:
                self.parchment_surf.blit(rendered_shadow, (pos_x + 2, start_y + 2))
            
            # Draw Text
            self.parchment_surf.blit(rendered_line, (pos_x, start_y))
            
            start_y += line_height

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_SPACE, pygame.K_RETURN, pygame.K_ESCAPE, pygame.K_x):
                    self.manager.change_state("FILE_SELECT")
            if event.type == pygame.MOUSEBUTTONDOWN:
                 self.manager.change_state("FILE_SELECT")

    def update(self):
        pass
            
    def render(self, screen):
        screen.blit(self.parchment_surf, (0, 0))
        
        # "Press Start" Pulse
        pulse = abs(math.sin(pygame.time.get_ticks() * 0.005)) * 255
        prompt_font = pygame.font.SysFont("arial", 24, bold=True)
        prompt = prompt_font.render("- PRESS START -", True, (80, 40, 0))
        prompt.set_alpha(int(pulse))
        
        prompt_x = SCREEN_WIDTH // 2 - prompt.get_width() // 2
        prompt_y = SCREEN_HEIGHT - 60
        screen.blit(prompt, (prompt_x, prompt_y))

class FileSelectState(GameState):
    """
    Standard File Select Menu (Mario Head Removed).
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
                    self.manager.change_state("GAMEPLAY")
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.manager.change_state("GAMEPLAY")

    def update(self):
        pass
        
    def render(self, screen):
        # Classic Dark Red/Brown background pattern simulation (solid for now)
        screen.fill((60, 0, 0)) 
        
        # Title
        title_surf = self.title_font.render("SELECT FILE", True, (255, 215, 0))
        screen.blit(title_surf, (SCREEN_WIDTH//2 - title_surf.get_width()//2, 50))
        
        # Draw Slots
        start_y = 150
        slot_height = 90
        
        for i in range(4):
            # Slot Background
            rect = pygame.Rect(150, start_y + i*slot_height, 500, 70)
            is_sel = (i == self.selected)
            
            # Highlight color vs Normal color
            color = (100, 100, 200) if is_sel else (100, 50, 50)
            border_color = (255, 255, 0) if is_sel else (200, 200, 200)
            
            pygame.draw.rect(screen, color, rect, border_radius=10)
            pygame.draw.rect(screen, border_color, rect, 3, border_radius=10)
            
            # Text
            label = f"MARIO {chr(65+i)}"
            text_surf = self.font.render(label, True, WHITE)
            screen.blit(text_surf, (rect.x + 20, rect.y + 15))
            
            # Stars count (Fake data)
            stars_count = 0 if i > 0 else 3 # Slot A has 3 stars
            stars = f"* {stars_count}"
            star_surf = self.font.render(stars, True, (255, 255, 0))
            screen.blit(star_surf, (rect.right - 100, rect.y + 15))

        # Helper text
        hint = self.font.render("PRESS START", True, (255, 255, 255))
        screen.blit(hint, (SCREEN_WIDTH//2 - hint.get_width()//2, SCREEN_HEIGHT - 60))

class GameplayState(GameState):
    """
    Beta Debug Menu - Replaces the 3D Playground.
    Classic N64 Dev Environment style.
    """
    def __init__(self, manager):
        super().__init__(manager)
        
        # Monospace font for that "dev console" look
        self.font = pygame.font.SysFont("couriernew", 24, bold=True)
        self.small_font = pygame.font.SysFont("couriernew", 16)
        
        self.options = [
            "LEVEL SELECT",
            "OBJ  TEST",
            "SFX  TEST",
            "GFX  TEST",
            "MEMORY DUMP",
            "CRASH HANDLER",
            "EXIT TO TITLE"
        ]
        self.selected_index = 0
        self.blink_timer = 0
        
        # Fake memory stats
        self.mem_allocated = 0.0
        
    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.selected_index = (self.selected_index - 1) % len(self.options)
                elif event.key == pygame.K_DOWN:
                    self.selected_index = (self.selected_index + 1) % len(self.options)
                elif event.key == pygame.K_RETURN:
                    if self.options[self.selected_index] == "EXIT TO TITLE":
                        self.manager.change_state("INTRO")
                    else:
                        # Just a visual feedback for other options
                        self.mem_allocated += random.uniform(0.1, 0.5)

    def update(self):
        self.blink_timer += 1
        # Fluctuate memory "usage"
        self.mem_allocated = max(0, min(8.0, self.mem_allocated + random.uniform(-0.01, 0.01)))

    def render(self, screen):
        # 1. Background - Classic Dev Blue
        screen.fill(DEBUG_BLUE)
        
        # 2. Header Information
        header_text = self.font.render("SUPER MARIO 64 - DEBUG BUILD 95-07-29", True, WHITE)
        screen.blit(header_text, (40, 40))
        
        sub_text = self.small_font.render("RS P: OK  RDP: OK  Z-BUF: ON", True, (200, 200, 200))
        screen.blit(sub_text, (40, 70))
        
        # 3. Dynamic Stats
        fps_text = self.small_font.render(f"FPS: {int(self.manager.clock.get_fps())}", True, YELLOW if self.manager.clock.get_fps() < 55 else WHITE)
        mem_text = self.small_font.render(f"RAM: {4.0 + self.mem_allocated:.2f}MB / 8.0MB", True, WHITE)
        
        screen.blit(fps_text, (SCREEN_WIDTH - 150, 40))
        screen.blit(mem_text, (SCREEN_WIDTH - 200, 60))

        # 4. Render Menu Options
        start_y = 150
        line_height = 40
        
        for i, option in enumerate(self.options):
            is_selected = (i == self.selected_index)
            
            # Cursor
            if is_selected:
                cursor = self.font.render(">", True, DEBUG_YELLOW)
                screen.blit(cursor, (80, start_y))
            
            # Option Text
            color = DEBUG_YELLOW if is_selected else WHITE
            
            # Blink effect on selected
            if is_selected and (self.blink_timer // 10) % 2 == 0:
                # Slight dimming instead of full disappear
                pass 
                
            text = self.font.render(option, True, color)
            screen.blit(text, (110, start_y))
            
            start_y += line_height
            
        # 5. Footer / Build Info
        footer = self.small_font.render("BUILD: M64_950729_NTSC   CONFIDENTIAL - NINTENDO EAD", True, (100, 100, 200))
        screen.blit(footer, (40, SCREEN_HEIGHT - 40))
        
        # 6. Random Hex Dump for "Atmosphere"
        hex_y = 400
        for i in range(5):
            hex_str = f"0x80{random.randint(100000, 999999)}: {random.randint(0, 99)} {random.randint(0, 99)} {random.randint(0, 99)} {random.randint(0, 99)}"
            hex_text = self.small_font.render(hex_str, True, (0, 0, 80)) # Very dark blue text
            screen.blit(hex_text, (SCREEN_WIDTH - 250, hex_y + i * 20))

# --- HELPERS ---
YELLOW = (255, 255, 0)

# --- GAME MANAGER ---

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Ultra Mario 3D N64 - Debug Build")
        self.clock = pygame.time.Clock()
        
        self.states = {
            "INTRO": IntroState(self),
            "FILE_SELECT": FileSelectState(self),
            "GAMEPLAY": GameplayState(self)
        }
        self.current_state_name = "INTRO"
        self.current_state = self.states["INTRO"]

    def change_state(self, new_state_name):
        if new_state_name in self.states:
            self.current_state_name = new_state_name
            self.current_state = self.states[new_state_name]

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
