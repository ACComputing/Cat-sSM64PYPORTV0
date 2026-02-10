import pygame
import math
import sys

# ==========================================
#  SUPER PYGAME 64 (Engine Rewrite)
# ==========================================
#  A pure Python 3D engine mimicking SM64 behavior.
#  
#  CONTROLS:
#    WASD: Move Mario (Relative to Camera)
#    SPACE: Jump / Double Jump
#    ARROW KEYS: "C-Buttons" (Rotate Camera)
#    SHIFT: Sprint/Run
# ==========================================

# --- CONFIGURATION ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
FOV = 500 

# Colors
SKY_BLUE = (92, 148, 252)  # SM64 Sky
WHITE = (255, 255, 255)
MARIO_RED = (255, 0, 0)
MARIO_BLUE = (0, 0, 255)
MARIO_SKIN = (255, 200, 150)
GRASS_GREEN = (0, 160, 0)
STONE_GRAY = (180, 180, 180)
COIN_GOLD = (255, 220, 0)
SHADOW_BLACK = (0, 0, 0)

# Physics Constants
GRAVITY = 0.8
JUMP_FORCE = -16
MOVE_SPEED = 8
FRICTION = 0.85
AIR_RESISTANCE = 0.95

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Super Pygame 64 - Lakitu Cam Update")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial Black", 20)

# --- 3D MATH ENGINE ---

def rotate_y(x, z, angle_rad):
    """Rotates a point (x,z) around the Y axis."""
    cos_a = math.cos(angle_rad)
    sin_a = math.sin(angle_rad)
    nx = x * cos_a - z * sin_a
    nz = x * sin_a + z * cos_a
    return nx, nz

class Camera:
    def __init__(self, target):
        self.target = target
        self.x = 0
        self.y = -200
        self.z = -500
        
        # Lakitu State
        self.distance = 600
        self.height = 250
        self.angle_around_player = 0 # Radians
        self.target_angle = 0
        
        # Smoothness factors
        self.lag_speed = 0.08  # How fast Lakitu catches up (Lower = Lazier)
        self.rot_speed = 0.1   # How fast camera rotates

    def update(self):
        # 1. Handle Input (C-Buttons / Arrow Keys)
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.target_angle -= 0.05
        if keys[pygame.K_RIGHT]:
            self.target_angle += 0.05
            
        # Smoothly interpolate angle
        self.angle_around_player += (self.target_angle - self.angle_around_player) * self.rot_speed
        
        # 2. Calculate "Ideal" Position
        # Lakitu wants to be behind the player at a specific angle and distance
        ideal_x = self.target.x - math.sin(self.angle_around_player) * self.distance
        ideal_z = self.target.z - math.cos(self.angle_around_player) * self.distance
        ideal_y = self.target.y - self.height

        # 3. Apply "Lakitu Lag" (Lerp)
        self.x += (ideal_x - self.x) * self.lag_speed
        self.z += (ideal_z - self.z) * self.lag_speed
        self.y += (ideal_y - self.y) * self.lag_speed
        
    def get_yaw(self):
        """Returns the camera's looking direction (yaw) in radians."""
        # Simple look-at logic: Camera looks at player
        dx = self.target.x - self.x
        dz = self.target.z - self.z
        return math.atan2(dx, dz)

# --- OBJECT CLASSES ---

class Cube:
    def __init__(self, x, y, z, size, color, is_static=True):
        self.x, self.y, self.z = x, y, z
        self.w = self.h = self.d = size
        self.color = color
        self.is_static = is_static
        self.visible = True
        
        # Render helpers
        self.half_size = size / 2

    def get_screen_polygon(self, cam):
        """Calculates screen coordinates for the cube. Returns list of faces."""
        
        # 1. World to Camera Space
        rel_x = self.x - cam.x
        rel_y = self.y - cam.y
        rel_z = self.z - cam.z
        
        # Rotate world around camera (inverse camera rotation)
        cam_yaw = cam.get_yaw()
        rx, rz = rotate_y(rel_x, rel_z, -cam_yaw)
        ry = rel_y
        
        # Cull if behind camera
        if rz <= 10: return []

        # 2. Generate Vertices (Local to object, then transformed)
        h = self.half_size
        # Local offsets
        local_verts = [
            (-h, -h, -h), (h, -h, -h), (h, h, -h), (-h, h, -h), # Front
            (-h, -h, h), (h, -h, h), (h, h, h), (-h, h, h)      # Back
        ]
        
        proj_verts = []
        for lx, ly, lz in local_verts:
            # Rotate local vertex by SAME camera angle? 
            # No, we translate object center, then add rotated local offsets.
            # But for correct 3D rotation, we should rotate the absolute vertex positions.
            # Optimized approach:
            
            # Absolute pos of vertex
            vx = self.x + lx
            vy = self.y + ly
            vz = self.z + lz
            
            # Rel to camera
            vrx = vx - cam.x
            vry = vy - cam.y
            vrz = vz - cam.z
            
            # Rotate around cam
            rot_x, rot_z = rotate_y(vrx, vrz, -cam_yaw)
            rot_y = vry
            
            # Project
            if rot_z < 1: 
                proj_verts.append(None)
            else:
                scale = FOV / rot_z
                sx = int(SCREEN_WIDTH / 2 + rot_x * scale)
                sy = int(SCREEN_HEIGHT / 2 + rot_y * scale)
                proj_verts.append((sx, sy, rot_z))

        # 3. Build Faces (Painter's Algo Prep)
        faces = [
            (0, 1, 2, 3, 1.0), # Front
            (5, 4, 7, 6, 0.7), # Back
            (4, 0, 3, 7, 0.8), # Left
            (1, 5, 6, 2, 0.8), # Right
            (4, 5, 1, 0, 1.2), # Top
            (3, 2, 6, 7, 0.4), # Bottom
        ]
        
        render_faces = []
        for f in faces:
            p_indices = f[:4]
            shade = f[4]
            
            points = []
            avg_z = 0
            valid = True
            
            for idx in p_indices:
                if proj_verts[idx] is None:
                    valid = False
                    break
                points.append((proj_verts[idx][0], proj_verts[idx][1]))
                avg_z += proj_verts[idx][2]
            
            if valid:
                avg_z /= 4
                # Apply shading
                r = min(255, int(self.color[0] * shade))
                g = min(255, int(self.color[1] * shade))
                b = min(255, int(self.color[2] * shade))
                render_faces.append({'z': avg_z, 'points': points, 'color': (r,g,b)})
                
        return render_faces

    def get_aabb(self):
        h = self.half_size
        return (self.x - h, self.x + h, self.y - h, self.y + h, self.z - h, self.z + h)

class Player(Cube):
    def __init__(self, x, y, z):
        super().__init__(x, y, z, 50, MARIO_RED, is_static=False)
        self.vx = 0
        self.vy = 0
        self.vz = 0
        self.grounded = False
        self.facing_angle = 0

    def move(self, camera, platforms):
        keys = pygame.key.get_pressed()
        
        # Input relative to Camera Angle
        cam_yaw = camera.get_yaw()
        
        # Calculate forward/right vectors based on camera
        fwd_x = math.sin(cam_yaw)
        fwd_z = math.cos(cam_yaw)
        right_x = math.sin(cam_yaw + 1.57) # 90 degrees
        right_z = math.cos(cam_yaw + 1.57)
        
        input_x = 0
        input_z = 0
        
        if keys[pygame.K_w]: 
            input_x += fwd_x
            input_z += fwd_z
        if keys[pygame.K_s]: 
            input_x -= fwd_x
            input_z -= fwd_z
        if keys[pygame.K_a]: 
            input_x -= right_x
            input_z -= right_z
        if keys[pygame.K_d]: 
            input_x += right_x
            input_z += right_z
            
        # Normalize input
        if input_x != 0 or input_z != 0:
            mag = math.sqrt(input_x**2 + input_z**2)
            input_x /= mag
            input_z /= mag
            
            # Acceleration
            self.vx += input_x * 1.5
            self.vz += input_z * 1.5
            
            # Update facing angle for visuals (not used in cube rendering but good for logic)
            self.facing_angle = math.atan2(input_x, input_z)

        # Jump
        if keys[pygame.K_SPACE] and self.grounded:
            self.vy = JUMP_FORCE
            self.grounded = False

        # Physics
        self.vy += GRAVITY
        self.vx *= FRICTION
        self.vz *= FRICTION
        
        # Terminal velocity
        if self.vy > 20: self.vy = 20

        # Collision Loop
        # X Movement
        self.x += self.vx
        self.check_collision(platforms, 'x')
        
        # Z Movement
        self.z += self.vz
        self.check_collision(platforms, 'z')
        
        # Y Movement
        self.y += self.vy
        self.grounded = False # Assume air until collision proves otherwise
        self.check_collision(platforms, 'y')

        # Void Reset
        if self.y > 2000:
            self.respawn()

    def respawn(self):
        self.x, self.y, self.z = 0, -200, 0
        self.vx, self.vy, self.vz = 0, 0, 0

    def check_collision(self, platforms, axis):
        my_aabb = self.get_aabb()
        
        for p in platforms:
            p_aabb = p.get_aabb()
            
            if (my_aabb[0] < p_aabb[1] and my_aabb[1] > p_aabb[0] and
                my_aabb[2] < p_aabb[3] and my_aabb[3] > p_aabb[2] and
                my_aabb[4] < p_aabb[5] and my_aabb[5] > p_aabb[4]):
                
                if axis == 'x':
                    if self.vx > 0: self.x = p_aabb[0] - self.w/2
                    elif self.vx < 0: self.x = p_aabb[1] + self.w/2
                    self.vx = 0
                elif axis == 'z':
                    if self.vz > 0: self.z = p_aabb[4] - self.d/2
                    elif self.vz < 0: self.z = p_aabb[5] + self.d/2
                    self.vz = 0
                elif axis == 'y':
                    if self.vy > 0: # Landing
                        self.y = p_aabb[2] - self.h/2
                        self.grounded = True
                        self.vy = 0
                    elif self.vy < 0: # Bonk head
                        self.y = p_aabb[3] + self.h/2
                        self.vy = 0

# --- MAIN ENGINE ---

def main():
    # Setup World
    mario = Player(0, -100, 0)
    lakitu = Camera(mario)
    
    # Level Geometry (Bob-omb Battlefield-ish)
    platforms = []
    
    # Main Floor
    platforms.append(Cube(0, 100, 0, 2000, GRASS_GREEN)) 
    
    # The Bridge
    platforms.append(Cube(0, 50, 400, 150, STONE_GRAY))
    platforms.append(Cube(0, 0, 550, 150, STONE_GRAY))
    platforms.append(Cube(0, -50, 700, 150, STONE_GRAY))
    
    # The Mountain
    platforms.append(Cube(-400, 0, -400, 200, STONE_GRAY))
    platforms.append(Cube(-450, -100, -450, 150, STONE_GRAY))
    platforms.append(Cube(-500, -200, -500, 100, WHITE)) # Snow cap
    
    # Floating Blocks
    platforms.append(Cube(300, -150, 0, 80, COIN_GOLD))
    platforms.append(Cube(450, -250, 0, 80, COIN_GOLD))
    
    running = True
    while running:
        # Event Handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                if event.key == pygame.K_r:
                    mario.respawn()

        # Update Logic
        mario.move(lakitu, platforms)
        lakitu.update()

        # Rendering
        screen.fill(SKY_BLUE)
        
        # Draw Floor Grid (Fake Horizon effect)
        pygame.draw.rect(screen, (0, 100, 0), (0, SCREEN_HEIGHT/2, SCREEN_WIDTH, SCREEN_HEIGHT/2))

        # Collect All Renderable Faces
        draw_queue = []
        
        # 1. Process Static Geometry
        for p in platforms:
            faces = p.get_screen_polygon(lakitu)
            draw_queue.extend(faces)
            
        # 2. Process Mario
        mario_faces = mario.get_screen_polygon(lakitu)
        draw_queue.extend(mario_faces)
        
        # 3. Sort by Depth (Painter's Algorithm)
        # Sort by Z (depth) descending (furthest first)
        draw_queue.sort(key=lambda x: x['z'], reverse=True)
        
        # 4. Draw
        for face in draw_queue:
            pts = face['points']
            if len(pts) > 2:
                pygame.draw.polygon(screen, face['color'], pts)
                pygame.draw.polygon(screen, SHADOW_BLACK, pts, 1)

        # UI / HUD
        fps_text = font.render(f"FPS: {int(clock.get_fps())}", True, WHITE)
        cam_text = font.render("ARROWS: Rotate Cam | WASD: Move | SPACE: Jump", True, WHITE)
        screen.blit(fps_text, (10, 10))
        screen.blit(cam_text, (10, 40))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
