import pygame
import sys
import os
from pygame.locals import *
from game_manager import GameManager
from ui_manager import UIManager
from projectile import Bullet, Maser, Missile, Beam, HealEffect
from enemy import Rackettra, SpaceRex, Enviorollante, EmperorHydra, Demolishyah
import random

# Created By: Mohammed Hossaim


pygame.init()


WINDOW_WIDTH = 1024
WINDOW_HEIGHT = 768
FPS = 60

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (50, 50, 50)


def load_sprite(filename, size=(40, 40)):
    try:
        image = pygame.image.load(os.path.join('assets', filename))
        return pygame.transform.scale(image, size)
    except:
        
        surface = pygame.Surface(size)
        surface.fill((100, 100, 100))
        return surface

class Game:
    def __init__(self):
        print("Initializing game...")  
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Kaiju Tower Defense")
        pygame.mixer.init()  # Initialize audio
        self.clock = pygame.time.Clock()
        self.running = True
        
       
        try:
            pygame.mixer.music.load("assets/background_music.mp3")
            pygame.mixer.music.set_volume(0.4)  
        except Exception as e:
            print(f"Error loading background music: {e}")
        
        self.game_manager = GameManager()
        self.ui_manager = UIManager(WINDOW_WIDTH, WINDOW_HEIGHT)
        
      
        self.background = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.create_city_background()
        
        print("Game initialized successfully")  
    
    def create_city_background(self):
        
        self.background.fill((40, 40, 40))
        
        
        road_color = (70, 70, 70)
        
        for i in range(len(self.game_manager.path) - 1):
            start = self.game_manager.path[i]
            end = self.game_manager.path[i + 1]
            pygame.draw.line(self.background, road_color, start, end, 40)
        
        
        building_colors = [
            (60, 60, 65),  
            (80, 80, 85),  
            (100, 100, 105),  
        ]
        
       
        building_sizes = [(60, 60), (80, 80), (100, 100)]
        for x in range(0, WINDOW_WIDTH, 120):
            for y in range(0, WINDOW_HEIGHT, 120):
                
                can_place = True
                for i in range(len(self.game_manager.path) - 1):
                    start = pygame.math.Vector2(self.game_manager.path[i])
                    end = pygame.math.Vector2(self.game_manager.path[i + 1])
                    pos = pygame.math.Vector2(x + 30, y + 30)
                    if self.point_to_line_distance(pos, start, end) < 60:
                        can_place = False
                        break
                
                if can_place:
                    color = building_colors[random.randint(0, len(building_colors)-1)]
                    size = building_sizes[random.randint(0, len(building_sizes)-1)]
                    pygame.draw.rect(self.background, color, 
                                   (x, y, size[0], size[1]))
                    # Add windows (lighter gray)
                    window_color = (120, 120, 125)
                    window_size = 8
                    for wx in range(x + 10, x + size[0] - 10, 20):
                        for wy in range(y + 10, y + size[1] - 10, 20):
                            pygame.draw.rect(self.background, window_color,
                                          (wx, wy, window_size, window_size))

    def point_to_line_distance(self, point, line_start, line_end):
        # Calculate distance from point to line segment
        line_vec = line_end - line_start
        point_vec = point - line_start
        line_length = line_vec.length()
        if line_length == 0:
            return point_vec.length()
        
        t = max(0, min(1, point_vec.dot(line_vec) / (line_length * line_length)))
        projection = line_start + line_vec * t
        return (point - projection).length()

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
                elif event.key == K_t:  
                    themes = list(self.backgrounds.keys())
                    current_index = themes.index(self.current_theme)
                    self.current_theme = themes[(current_index + 1) % len(themes)]
            
            
            elif event.type == MOUSEBUTTONDOWN:
                if event.button == 1:  
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
                elif event.button == 3: 
                    self.ui_manager.selected_tower = None
                    self.ui_manager.show_tower_range = False
            
            try:
                
                self.ui_manager.handle_events(event, self.game_manager)
            except Exception as e:
                print(f"Error in UI event handling: {e}")  
                import traceback
                traceback.print_exc()
    
    def update(self):
        
        previous_state = self.game_manager.game_state
        self.game_manager.update()
        
       
        if hasattr(self.game_manager, 'wave_reward'):
            self.ui_manager.show_wave_reward(self.game_manager.wave_reward)
            delattr(self.game_manager, 'wave_reward')
        
       
        current_time = pygame.time.get_ticks()
        
        
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
                        if "speed" in shot_info:
                            projectile.speed = shot_info["speed"]
                        self.game_manager.projectiles.append(projectile)
                    
                    elif shot_info["type"] == "missile":
                        projectile = Missile(
                            tower.position, tower.target.position,
                            shot_info["damage"], shot_info["aoe_radius"]
                        )
                        self.game_manager.projectiles.append(projectile)
                    
                    elif shot_info["type"] == "multi_missile":
                        for target in shot_info["targets"]:
                            projectile = Missile(
                                tower.position, target.position,
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
        
        for projectile in self.game_manager.projectiles[:]:
            if isinstance(projectile, Beam):
                if not projectile.update():
                    self.game_manager.projectiles.remove(projectile)
                else:
                    
                    beam_rect = pygame.Rect(
                        min(projectile.start.x, projectile.end.x),
                        min(projectile.start.y, projectile.end.y),
                        abs(projectile.end.x - projectile.start.x) or projectile.width,
                        abs(projectile.end.y - projectile.start.y) or projectile.width
                    )
                    for enemy in self.game_manager.enemies:
                        if enemy.rect.colliderect(beam_rect):
                            enemy.take_damage(projectile.damage * 0.1)  
                continue
            
            if projectile.update():
                
                for enemy in self.game_manager.enemies:
                    if enemy.rect.colliderect(projectile.rect):
                        enemy.take_damage(projectile.damage)
                        if isinstance(projectile, Maser):
                            enemy.effects.update(projectile.effect)
                        elif isinstance(projectile, Missile):
                            
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
                       
                        pass
    
    def draw(self):
        
        self.screen.blit(self.background, (0, 0))
        
        for i in range(len(self.game_manager.path) - 1):
            start_pos = self.game_manager.path[i]
            end_pos = self.game_manager.path[i + 1]
          
            pygame.draw.line(self.screen, (100, 100, 100), start_pos, end_pos, 42)
          
            pygame.draw.line(self.screen, (80, 80, 80), start_pos, end_pos, 40)

        for tower in self.game_manager.towers:
            tower.draw(self.screen, self.ui_manager.show_tower_range)
        
       
        for enemy in self.game_manager.enemies:
            enemy.draw(self.screen)
        
        
        for projectile in self.game_manager.projectiles:
            projectile.draw(self.screen)
        
       
        for effect in self.game_manager.effects:
            effect.draw(self.screen)
        
        
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
        
        
        if self.game_manager.game_state == "menu":
            self.ui_manager.draw_menu(self.screen)
        else:
            self.ui_manager.draw_hud(self.screen, self.game_manager)
            self.ui_manager.draw_tower_panel(self.screen, self.game_manager)
            self.ui_manager.draw_tooltip(self.screen)
        
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
        print("Starting game loop...")  
        while self.running:
            try:
                self.handle_events()
                self.update()
                self.draw()
                self.clock.tick(FPS)
            except Exception as e:
                print(f"Error in game loop: {e}")  
                import traceback
                traceback.print_exc()
                self.running = False

def main():
    
    if not os.path.exists('assets'):
        os.makedirs('assets')
        
    game = Game()
    game.run()
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main() 
