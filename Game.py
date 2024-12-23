import pygame
import math
import random

# Initialize Pygame
pygame.init()

# Set up the display
WIDTH = 800
HEIGHT = 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Interactive 3D Earth")

# Colors
BLUE = (0, 105, 148)      # Ocean
GREEN = (34, 139, 34)     # Land
CLOUD = (255, 255, 255)   # Clouds
ATMOSPHERE = (135, 206, 235)  # Sky blue
UI_COLOR = (200, 200, 200)  # UI elements

class Earth:
    def __init__(self):
        self.base_radius = 150
        self.radius = self.base_radius  # Current radius (for zoom)
        self.center = [WIDTH // 2, HEIGHT // 2]  # Now a list for movement
        self.rotation_x = 0  # Rotation around X axis
        self.rotation_y = 0  # Rotation around Y axis
        self.rotation_z = 0  # Rotation around Z axis
        self.land_points = self.generate_land_points()
        self.cloud_points = self.generate_cloud_points()
        self.zoom_level = 1.0
        
    def generate_land_points(self):
        points = []
        # Generate points distributed across a sphere
        for _ in range(50):
            # Use spherical coordinates for better distribution
            theta = random.uniform(0, 2 * math.pi)
            phi = random.uniform(0, math.pi)
            size = random.randint(20, 40)
            # Convert to Cartesian coordinates
            x = self.base_radius * math.sin(phi) * math.cos(theta)
            y = self.base_radius * math.sin(phi) * math.sin(theta)
            z = self.base_radius * math.cos(phi)
            points.append((x, y, z, size))
        return points
    
    def generate_cloud_points(self):
        points = []
        for _ in range(30):
            theta = random.uniform(0, 2 * math.pi)
            phi = random.uniform(0, math.pi)
            size = random.randint(10, 30)
            x = (self.base_radius + 10) * math.sin(phi) * math.cos(theta)
            y = (self.base_radius + 10) * math.sin(phi) * math.sin(theta)
            z = (self.base_radius + 10) * math.cos(phi)
            points.append((x, y, z, size))
        return points
    
    def rotate(self, dx, dy, dz):
        self.rotation_x += dx
        self.rotation_y += dy
        self.rotation_z += dz
    
    def move(self, dx, dy):
        self.center[0] += dx
        self.center[1] += dy
    
    def zoom(self, factor):
        self.zoom_level *= factor
        self.radius = self.base_radius * self.zoom_level
    
    def transform_point(self, x, y, z):
        # Apply rotations (in 3D)
        # Rotate around X axis
        y2 = y * math.cos(math.radians(self.rotation_x)) - z * math.sin(math.radians(self.rotation_x))
        z2 = y * math.sin(math.radians(self.rotation_x)) + z * math.cos(math.radians(self.rotation_x))
        y, z = y2, z2
        
        # Rotate around Y axis
        x2 = x * math.cos(math.radians(self.rotation_y)) + z * math.sin(math.radians(self.rotation_y))
        z2 = -x * math.sin(math.radians(self.rotation_y)) + z * math.cos(math.radians(self.rotation_y))
        x, z = x2, z2
        
        # Rotate around Z axis
        x2 = x * math.cos(math.radians(self.rotation_z)) - y * math.sin(math.radians(self.rotation_z))
        y2 = x * math.sin(math.radians(self.rotation_z)) + y * math.cos(math.radians(self.rotation_z))
        x, y = x2, y2
        
        # Apply perspective (basic z-buffer)
        scale = 1000 / (1000 + z)
        x = x * scale * self.zoom_level
        y = y * scale * self.zoom_level
        
        return x, y, z, scale
    
    def draw(self, screen):
        # Draw atmosphere glow
        for r in range(5):
            alpha = 100 - (r * 20)
            s = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            pygame.draw.circle(s, (*ATMOSPHERE, alpha), 
                             (int(self.center[0]), int(self.center[1])), 
                             int(self.radius + r * 4))
            screen.blit(s, (0, 0))
        
        # Draw base sphere (ocean)
        pygame.draw.circle(screen, BLUE, 
                         (int(self.center[0]), int(self.center[1])), 
                         int(self.radius))
        
        # Store all points for z-sorting
        visible_points = []
        
        # Transform and store land points
        for x, y, z, size in self.land_points:
            tx, ty, tz, scale = self.transform_point(x, y, z)
            if tz < 500:  # Only if point is in front
                visible_points.append(('land', 
                                     (self.center[0] + tx, self.center[1] + ty),
                                     size * scale, tz))
        
        # Transform and store cloud points
        for x, y, z, size in self.cloud_points:
            tx, ty, tz, scale = self.transform_point(x, y, z)
            if tz < 500:
                visible_points.append(('cloud', 
                                     (self.center[0] + tx, self.center[1] + ty),
                                     size * scale, tz))
        
        # Sort points by z-coordinate (painter's algorithm)
        visible_points.sort(key=lambda p: p[3], reverse=True)
        
        # Draw all points in order
        for point_type, pos, size, _ in visible_points:
            if point_type == 'land':
                pygame.draw.circle(screen, GREEN, 
                                 (int(pos[0]), int(pos[1])), 
                                 int(size))
            else:  # Cloud
                s = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                pygame.draw.circle(s, (*CLOUD, 128), 
                                 (int(pos[0]), int(pos[1])), 
                                 int(size))
                screen.blit(s, (0, 0))

def draw_ui(screen, earth):
    # Draw UI elements
    font = pygame.font.Font(None, 24)
    
    controls = [
        "Left Click + Drag: Rotate",
        "Right Click + Drag: Move",
        "Mouse Wheel: Zoom",
        "R: Reset View",
        f"Zoom: {earth.zoom_level:.2f}x"
    ]
    
    y = 10
    for text in controls:
        surface = font.render(text, True, UI_COLOR)
        screen.blit(surface, (10, y))
        y += 25

def main():
    clock = pygame.time.Clock()
    earth = Earth()
    
    # Control variables
    rotating = False
    moving = False
    last_mouse_pos = None
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    rotating = True
                    last_mouse_pos = event.pos
                elif event.button == 3:  # Right click
                    moving = True
                    last_mouse_pos = event.pos
                elif event.button == 4:  # Mouse wheel up
                    earth.zoom(1.1)
                elif event.button == 5:  # Mouse wheel down
                    earth.zoom(0.9)
                    
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    rotating = False
                elif event.button == 3:
                    moving = False
                last_mouse_pos = None
                
            elif event.type == pygame.MOUSEMOTION:
                if last_mouse_pos:
                    dx = event.pos[0] - last_mouse_pos[0]
                    dy = event.pos[1] - last_mouse_pos[1]
                    
                    if rotating:
                        earth.rotate(dy * 0.5, dx * 0.5, 0)
                    elif moving:
                        earth.move(dx, dy)
                        
                    last_mouse_pos = event.pos
                    
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:  # Reset view
                    earth = Earth()
        
        # Clear screen
        screen.fill((0, 0, 0))
        
        # Draw earth
        earth.draw(screen)
        
        # Draw UI
        draw_ui(screen, earth)
        
        # Update display
        pygame.display.flip()
        
        # Control frame rate
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
