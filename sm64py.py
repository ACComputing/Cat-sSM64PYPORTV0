import pygame
import math
import sys

# ==========================================
#  PURE PYGAME 3D ENGINE (SOFTWARE RENDER)
# ==========================================
#  No OpenGL, No Ursina. Just Math.
#  Controls:
#    WASD: Move (X/Z axis)
#    SPACE: Jump (Y axis)
#    MOUSE: Rotate Camera (Left/Right)
# ==========================================

# --- CONFIGURATION ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
FOV = 400  # Field of View scale factor

# Colors
SKY_BLUE = (135, 206, 235)
WHITE = (255, 255, 255)
RED = (220, 20, 60)       # Mario
BLUE = (0, 0, 205)        # Overalls
GREEN = (34, 139, 34)     # Grass
GRAY = (128, 128, 128)    # Stone
YELLOW = (255, 215, 0)    # Stars
BLACK = (20, 20, 20)      # Shadow/Outline

# Physics
GRAVITY = 0.5
JUMP_FORCE = -12
MOVE_SPEED = 5
FRICTION = 0.8

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Pygame 3D Software Renderer - SM64 Demake")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 16, bold=True)

# --- 3D MATH HELPERS ---

def rotate_y(x, z, angle):
    """Rotates a point (x,z) around the Y axis (vertical)."""
    rad = math.radians(angle)
    cos_a = math.cos(rad)
    sin_a = math.sin(rad)
    # Rotation matrix logic
    nx = x * cos_a - z * sin_a
    nz = x * sin_a + z * cos_a
    return nx, nz

def project(x, y, z, cam_x, cam_y, cam_z, cam_yaw):
    """
    Projects 3D world coordinates to 2D screen coordinates.
    Returns (screen_x, screen_y, depth) or None if behind camera.
    """
    # 1. Translate relative to camera
    rx = x - cam_x
    ry = y - cam_y
    rz = z - cam_z

    # 2. Rotate relative to camera yaw
    rx, rz = rotate_y(rx, rz, -cam_yaw)

    # 3. Clip if behind camera (or too close)
    if rz <= 1:
        return None

    # 4. Perspective Projection
    scale = FOV / rz
    screen_x = int(SCREEN_WIDTH / 2 + rx * scale)
    screen_y = int(SCREEN_HEIGHT / 2 + ry * scale)
    
    return screen_x, screen_y, rz

# --- CLASSES ---

class Cube:
    def __init__(self, x, y, z, size, color, is_static=True):
        self.x = x
        self.y = y
        self.z = z
        self.w = size  # Width
        self.h = size  # Height
        self.d = size  # Depth
        self.color = color
        self.is_static = is_static
        
        # Physics (only used if not static)
        self.vx = 0
        self.vy = 0
        self.vz = 0
        self.grounded = False

        # Define 8 vertices relative to center
        # We'll calculate absolute positions every frame for rendering
        self.half_size = size / 2

    def get_faces(self):
        """Returns a list of faces. Each face is (avg_z, color, [points_2d])."""
        # Vertices (local space)
        # 0: Front-Top-Left, 1: Front-Top-Right, 2: Front-Bottom-Right, 3: Front-Bottom-Left
        # 4-7: Back equivalent
        hw, hh, hd = self.w/2, self.h/2, self.d/2
        
        verts = [
            (self.x - hw, self.y - hh, self.z - hd), # 0
            (self.x + hw, self.y - hh, self.z - hd), # 1
            (self.x + hw, self.y + hh, self.z - hd), # 2
            (self.x - hw, self.y + hh, self.z - hd), # 3
            (self.x - hw, self.y - hh, self.z + hd), # 4
            (self.x + hw, self.y - hh, self.z + hd), # 5
            (self.x + hw, self.y + hh, self.z + hd), # 6
            (self.x - hw, self.y + hh, self.z + hd), # 7
        ]
        
        # Face definitions (indices of verts)
        # Order matters for simple backface culling (optional, but we stick to Painter's Algo)
        face_indices = [
            (0, 1, 2, 3), # Front
            (5, 4, 7, 6), # Back
            (4, 0, 3, 7), # Left
            (1, 5, 6, 2), # Right
            (4, 5, 1, 0), # Top
            (3, 2, 6, 7), # Bottom
        ]

        # Lighting shading factors (simple fake lighting)
        shades = [1.0, 0.6, 0.8, 0.8, 1.2, 0.4] # Front, Back, Left, Right, Top, Bottom

        return verts, face_indices, shades

    def get_aabb(self):
        """Returns (min_x, max_x, min_y, max_y, min_z, max_z)"""
        hw, hh, hd = self.w/2, self.h/2, self.d/2
        return (self.x - hw, self.x + hw, 
                self.y - hh, self.y + hh, 
                self.z - hd, self.z + hd)

class Player(Cube):
    def __init__(self, x, y, z):
        super().__init__(x, y, z, 40, RED, is_static=False)
        self.yaw = 0 # Look direction

    def update(self, platforms):
        keys = pygame.key.get_pressed()
        
        # Input relative to Camera/Player Yaw
        input_x = 0
        input_z = 0
        
        if keys[pygame.K_w]: input_z = 1
        if keys[pygame.K_s]: input_z = -1
        if keys[pygame.K_a]: input_x = -1
        if keys[pygame.K_d]: input_x = 1
        
        # Rotate input vector by camera yaw
        # We use the global camera yaw stored in game loop, 
        # but here we'll assume we move relative to our own angle for now
        # Actually, let's pass cam_yaw or just do simple movement
        
        # Normalize vector
        if input_x != 0 or input_z != 0:
            length = math.sqrt(input_x**2 + input_z**2)
            input_x /= length
            input_z /= length
            
            # Rotate inputs by the player's current view angle (passed in later)
            # For now, let's just say W moves into Z depth
            
            self.vx += input_x * 1.0
            self.vz += input_z * 1.0

        # Jump
        if keys[pygame.K_SPACE] and self.grounded:
            self.vy = JUMP_FORCE
            self.grounded = False

        # Physics Application
        self.vy += GRAVITY
        
        # Apply Friction
        self.vx *= FRICTION
        self.vz *= FRICTION

        # Move & Collide (Simple AABB)
        # X Axis
        self.x += self.vx
        self.check_collision(platforms, 'x')
        
        # Z Axis
        self.z += self.vz
        self.check_collision(platforms, 'z')
        
        # Y Axis
        self.y += self.vy
        self.grounded = False
        self.check_collision(platforms, 'y')
        
        # Void check
        if self.y > 1000:
            self.x, self.y, self.z = 0, -100, 0
            self.vy = 0

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
                    if self.vy > 0: # Falling down
                        self.y = p_aabb[2] - self.h/2
                        self.grounded = True
                        self.vy = 0
                    elif self.vy < 0: # Hitting head
                        self.y = p_aabb[3] + self.h/2
                        self.vy = 0

# --- MAIN GAME LOOP ---

def main():
    # Setup Level
    player = Player(0, -100, 0)
    
    platforms = []
    # Ground
    platforms.append(Cube(0, 50, 0, 800, GREEN)) # Big floor
    
    # Steps
    platforms.append(Cube(200, 0, 0, 100, GRAY))
    platforms.append(Cube(350, -50, 0, 100, GRAY))
    platforms.append(Cube(500, -100, 0, 100, GRAY))
    
    # Floating platform
    platforms.append(Cube(0, -150, 300, 150, GRAY))
    
    stars = []
    stars.append(Cube(500, -200, 0, 30, YELLOW)) # Star on top of steps
    stars.append(Cube(0, -250, 300, 30, YELLOW)) # Star on floating plat
    
    camera_x, camera_y, camera_z = 0, -200, -600
    camera_yaw = 0
    target_yaw = 0
    
    score = 0
    
    running = True
    while running:
        # 1. Event Handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                    
        # Camera Control
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]: target_yaw -= 3
        if keys[pygame.K_RIGHT]: target_yaw += 3
        
        # Smooth Camera Rotation
        camera_yaw += (target_yaw - camera_yaw) * 0.1

        # 2. Update Physics
        
        # Adjust inputs based on camera angle
        rad_yaw = math.radians(camera_yaw)
        # We manually rotate the input logic inside the game loop to simplify Player class
        fwd_x = math.sin(rad_yaw)
        fwd_z = math.cos(rad_yaw)
        right_x = math.sin(rad_yaw + 1.57)
        right_z = math.cos(rad_yaw + 1.57)
        
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
            
        # Normalize and apply to player
        if input_x != 0 or input_z != 0:
            mag = math.sqrt(input_x**2 + input_z**2)
            player.vx += (input_x / mag) * 0.8 # Acceleration
            player.vz += (input_z / mag) * 0.8

        player.update(platforms)
        
        # Star Collection
        p_aabb = player.get_aabb()
        for s in stars[:]:
            s_aabb = s.get_aabb()
            # Simple AABB check
            if (p_aabb[0] < s_aabb[1] and p_aabb[1] > s_aabb[0] and
                p_aabb[2] < s_aabb[3] and p_aabb[3] > s_aabb[2] and
                p_aabb[4] < s_aabb[5] and p_aabb[5] > s_aabb[4]):
                stars.remove(s)
                score += 1
                print("Star Collected!")

        # Animate Stars (Spin)
        for s in stars:
            # For a pure cube, spinning is hard to render nicely without texture mapping
            # but we can bob them
            s.y = s.y + math.sin(pygame.time.get_ticks() * 0.005) * 0.5

        # Camera Follow Logic (Smoothly follow player)
        desired_cam_x = player.x - math.sin(rad_yaw) * 600
        desired_cam_z = player.z - math.cos(rad_yaw) * 600
        desired_cam_y = player.y - 200 # Look from above
        
        camera_x += (desired_cam_x - camera_x) * 0.05
        camera_z += (desired_cam_z - camera_z) * 0.05
        camera_y += (desired_cam_y - camera_y) * 0.05

        # 3. Rendering (The 3D Pipeline)
        screen.fill(SKY_BLUE)
        
        # Floor Grid (Visual Trick for orientation)
        # Draw a big rectangle for "horizon" or ground at bottom
        # pygame.draw.rect(screen, (50, 150, 50), (0, SCREEN_HEIGHT/2, SCREEN_WIDTH, SCREEN_HEIGHT/2))

        # Collect all faces from all objects to render
        render_list = [] # Stores (avg_depth, [points], color)
        
        all_objects = platforms + stars + [player]
        
        for obj in all_objects:
            verts, faces, shades = obj.get_faces()
            
            # Project all vertices first
            proj_verts = []
            for v in verts:
                p = project(v[0], v[1], v[2], camera_x, camera_y, camera_z, camera_yaw)
                proj_verts.append(p)
                
            # Process faces
            for i, face_idxs in enumerate(faces):
                # Get projected points for this face
                face_points_2d = []
                avg_z = 0
                valid_point_count = 0
                
                for idx in face_idxs:
                    p = proj_verts[idx]
                    if p:
                        face_points_2d.append((p[0], p[1]))
                        avg_z += p[2]
                        valid_point_count += 1
                
                # If any point is behind camera (None), or too close, we might skip
                # For this simple engine, we only draw if ALL 4 points are in front
                if valid_point_count == 4:
                    avg_z /= 4
                    
                    # Apply shading
                    base_color = obj.color
                    shade_factor = shades[i]
                    r = max(0, min(255, int(base_color[0] * shade_factor)))
                    g = max(0, min(255, int(base_color[1] * shade_factor)))
                    b = max(0, min(255, int(base_color[2] * shade_factor)))
                    
                    render_list.append((avg_z, face_points_2d, (r, g, b)))

        # PAINTER'S ALGORITHM: Sort by depth (furthest first)
        render_list.sort(key=lambda x: x[0], reverse=True)
        
        # Draw Faces
        for depth, poly, col in render_list:
            pygame.draw.polygon(screen, col, poly)
            pygame.draw.polygon(screen, BLACK, poly, 1) # Wireframe outline for definition

        # HUD
        score_text = font.render(f"STARS: {score}  |  WASD+SPACE to Move  |  ARROWS to Rotate Cam", True, BLACK)
        screen.blit(score_text, (20, 20))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
