import pygame
import sys
import os
from pygame.locals import *
from game_manager import GameManager
from ui_manager import UIManager
from projectile import Bullet, Maser, Missile, Beam, HealEffect

# Initialize Pygame
pygame.init()

# Constants
WINDOW_WIDTH = 1024
WINDOW_HEIGHT = 768
FPS = 60

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (50, 50, 50)

# Asset loading
def load_sprite(filename, size=(40, 40)):
    try:
        image = pygame.image.load(os.path.join('assets', filename))
        return pygame.transform.scale(image, size)
    except:
        # Create a default colored rectangle if image loading fails
        surface = pygame.Surface(size)
        surface.fill((100, 100, 100))
        return surface

class Game:
    def __init__(self):
        print("Initializing game...")  # Debug output
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Kaiju Tower Defense")
        self.clock = pygame.time.Clock()
        self.running = True
        
        self.game_manager = GameManager()
        self.ui_manager = UIManager(WINDOW_WIDTH, WINDOW_HEIGHT)
        
        # Load background images (placeholder colors for now)
        self.backgrounds = {
            "tokyo": pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT)),
            "nyc": pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT)),
            "future": pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        }
        self.backgrounds["tokyo"].fill((0, 50, 0))  # Dark green for Tokyo
        self.backgrounds["nyc"].fill((50, 50, 70))  # Dark blue-gray for NYC
        self.backgrounds["future"].fill((0, 0, 50))  # Dark blue for Future
        
        # Load sprite images
        self.sprites = {
            "lord_rex": load_sprite("lord_rex.png"),
            # Add more sprites here as they become available
        }
        
        self.current_theme = "tokyo"
        print("Game initialized successfully")  # Debug output
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                self.running = False
                return
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    if self.game_manager.game_state == "menu":
                        self.running = False
                    else:
                        self.game_manager.game_state = "menu"
                elif event.key == K_t:  # Change theme
                    themes = list(self.backgrounds.keys())
                    current_index = themes.index(self.current_theme)
                    self.current_theme = themes[(current_index + 1) % len(themes)]
            
            # Handle tower placement
            elif event.type == MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    if self.ui_manager.selected_tower:
                        mouse_pos = pygame.mouse.get_pos()
                        if self.game_manager.can_place_tower(mouse_pos):
                            tower_class = self.ui_manager.selected_tower["class"]
                            tower = tower_class(mouse_pos[0], mouse_pos[1])
                            if self.game_manager.cash >= tower.cost:
                                self.game_manager.towers.append(tower)
                                self.game_manager.cash -= tower.cost
                                self.ui_manager.selected_tower = None
                                self.ui_manager.show_tower_range = False
                elif event.button == 3:  # Right click
                    self.ui_manager.selected_tower = None
                    self.ui_manager.show_tower_range = False
            
            try:
                # Handle UI events
                self.ui_manager.handle_events(event, self.game_manager)
            except Exception as e:
                print(f"Error in UI event handling: {e}")  # Debug output
                import traceback
                traceback.print_exc()
    
    def update(self):
        # Update game state
        self.game_manager.update()
        
        # Update towers and projectiles
        current_time = pygame.time.get_ticks()
        
        # Update towers
        for tower in self.game_manager.towers:
            if tower.can_shoot(current_time):
                tower.acquire_target(self.game_manager.enemies)
                if tower.target:
                    shot_info = tower.shoot(current_time)
                    
                    if shot_info["type"] == "bullet":
                        projectile = Bullet(
                            tower.position, tower.target.position,
                            shot_info["damage"]
                        )
                        self.game_manager.projectiles.append(projectile)
                    
                    elif shot_info["type"] == "maser":
                        projectile = Maser(
                            tower.position, tower.target.position,
                            shot_info["damage"], shot_info["effect"]
                        )
                        self.game_manager.projectiles.append(projectile)
                    
                    elif shot_info["type"] == "missile":
                        projectile = Missile(
                            tower.position, tower.target.position,
                            shot_info["damage"], shot_info["aoe_radius"]
                        )
                        self.game_manager.projectiles.append(projectile)
                    
                    elif shot_info["type"] == "beam":
                        beam = Beam(
                            shot_info["start"], shot_info["end"],
                            shot_info["damage"], shot_info["width"]
                        )
                        self.game_manager.projectiles.append(beam)
                    
                    elif shot_info["type"] == "heal":
                        heal = HealEffect(
                            tower.position, shot_info["range"],
                            shot_info["heal_amount"]
                        )
                        self.game_manager.effects.append(heal)
        
        # Update projectiles and check for hits
        for projectile in self.game_manager.projectiles[:]:
            if isinstance(projectile, Beam):
                if not projectile.update():
                    self.game_manager.projectiles.remove(projectile)
                continue
            
            if projectile.update():
                # Handle projectile hit
                for enemy in self.game_manager.enemies:
                    if enemy.rect.colliderect(projectile.rect):
                        enemy.take_damage(projectile.damage)
                        if isinstance(projectile, Maser):
                            enemy.effects.update(projectile.effect)
                        elif isinstance(projectile, Missile):
                            # Handle AOE damage
                            for other_enemy in self.game_manager.enemies:
                                if other_enemy != enemy:
                                    distance = (other_enemy.position - enemy.position).length()
                                    if distance <= projectile.aoe_radius:
                                        other_enemy.take_damage(projectile.damage * 0.5)
                        break
                self.game_manager.projectiles.remove(projectile)
        
        # Update effects
        for effect in self.game_manager.effects[:]:
            if not effect.update():
                self.game_manager.effects.remove(effect)
            elif isinstance(effect, HealEffect):
                # Apply healing to nearby towers
                for tower in self.game_manager.towers:
                    distance = (tower.position - effect.position).length()
                    if distance <= effect.range:
                        # Implement tower healing if we add tower HP later
                        pass
    
    def draw(self):
        # Draw background
        self.screen.blit(self.backgrounds[self.current_theme], (0, 0))
        
        # Draw path
        for i in range(len(self.game_manager.path) - 1):
            start_pos = self.game_manager.path[i]
            end_pos = self.game_manager.path[i + 1]
            pygame.draw.line(self.screen, WHITE, start_pos, end_pos, 40)
        
        # Draw towers
        for tower in self.game_manager.towers:
            tower.draw(self.screen, self.ui_manager.show_tower_range)
        
        # Draw enemies
        for enemy in self.game_manager.enemies:
            enemy.draw(self.screen)
        
        # Draw projectiles
        for projectile in self.game_manager.projectiles:
            projectile.draw(self.screen)
        
        # Draw effects
        for effect in self.game_manager.effects:
            effect.draw(self.screen)
        
        # Draw tower placement preview
        if self.ui_manager.selected_tower:
            mouse_pos = pygame.mouse.get_pos()
            preview_color = (0, 255, 0, 128) if self.game_manager.can_place_tower(mouse_pos) else (255, 0, 0, 128)
            preview_surface = pygame.Surface((40, 40), pygame.SRCALPHA)
            pygame.draw.rect(preview_surface, preview_color, (0, 0, 40, 40))
            self.screen.blit(preview_surface, (mouse_pos[0] - 20, mouse_pos[1] - 20))
            
            if self.ui_manager.show_tower_range:
                tower_class = self.ui_manager.selected_tower["class"]
                tower = tower_class(mouse_pos[0], mouse_pos[1])
                pygame.draw.circle(self.screen, (100, 100, 100, 64),
                                 mouse_pos, tower.range, 1)
        
        # Draw UI
        if self.game_manager.game_state == "menu":
            self.ui_manager.draw_menu(self.screen)
        else:
            self.ui_manager.draw_hud(self.screen, self.game_manager)
            self.ui_manager.draw_tower_panel(self.screen, self.game_manager)
            self.ui_manager.draw_tooltip(self.screen)
        
        # Draw game over or victory screen
        if self.game_manager.game_state in ["game_over", "victory"]:
            surface = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
            surface.fill((0, 0, 0, 128))
            self.screen.blit(surface, (0, 0))
            
            text = "Game Over!" if self.game_manager.game_state == "game_over" else "Victory!"
            font = pygame.font.SysFont('Arial', 72)
            text_surface = font.render(text, True, WHITE)
            text_rect = text_surface.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2))
            self.screen.blit(text_surface, text_rect)
        
        pygame.display.flip()
    
    def run(self):
        print("Starting game loop...")  # Debug output
        while self.running:
            try:
                self.handle_events()
                self.update()
                self.draw()
                self.clock.tick(FPS)
            except Exception as e:
                print(f"Error in game loop: {e}")  # Debug output
                import traceback
                traceback.print_exc()
                self.running = False

def main():
    # Create assets directory if it doesn't exist
    if not os.path.exists('assets'):
        os.makedirs('assets')
        
    game = Game()
    game.run()
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main() 