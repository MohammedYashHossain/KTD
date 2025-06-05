import pygame
import random
from enemy import Rackettra, SpaceRex, Enviorollante, EmperorHydra, Demolishyah

class GameManager:
    def __init__(self):
        self.current_wave = 0
        self.max_waves = 50
        self.cash = 200
        self.base_hp = 100
        self.game_state = "menu"  
        self.enemies = []
        self.towers = []
        self.projectiles = []
        self.effects = []
        self.wave_delay = 1000  
        self.last_spawn_time = 0
        self.enemies_to_spawn = []
        self.auto_skip = False  
        self.path = [
            (50, 50),    
            (200, 50),   
            (200, 150),  
            (400, 150),   
            (400, 50),    
            (600, 50),    
            (600, 250),   
            (400, 250),  
            (400, 350),  
            (700, 350),   
            (700, 450),   
            (300, 450),  
            (300, 550), 
            (500, 550),  
            (500, 650),   
            (800, 650),   
            (950, 650)    
        ]  
        
    def start_wave(self):
        if self.current_wave >= self.max_waves:
            return False
        
        self.current_wave += 1
        self.enemies_to_spawn = self._generate_wave()
        self.game_state = "playing"
        self.last_spawn_time = pygame.time.get_ticks()
        return True
    
    def _generate_wave(self):
        enemies = []
        
        # Boss waves
        if self.current_wave in [10, 20, 30, 40, 50]:
            
            self.boss_wave_notification = True
            
            if self.current_wave == 10:
                return [("demolishyah", 1)]  # First boss at wave 10
            elif self.current_wave == 20:
                return [("demolishyah", 2)]  # Second boss at wave 20
            elif self.current_wave == 30:
                return [("demolishyah", 3)]  # Third boss at wave 30
            elif self.current_wave == 40:
                return [("demolishyah", 4)]  # Fourth boss at wave 40
            elif self.current_wave == 50:
                return [("hydra_boss", 1)]  # Final boss with stage parameter
        else:
            self.boss_wave_notification = False
        
       
        num_enemies = min(self.current_wave, 15)  
        
       
        self.wave_delay = max(500, 1000 - (self.current_wave * 10))
        
       
        available_enemies = ["rackettra"]  
        
        if self.current_wave > 10:
            available_enemies.append("space_rex")
        if self.current_wave > 20:
            available_enemies.append("enviorollante")
        
       
        for _ in range(num_enemies):
            enemy_type = random.choice(available_enemies)
            enemies.append((enemy_type, None))
        
        return enemies
    
    def spawn_enemy(self, current_time):
        if not self.enemies_to_spawn or current_time - self.last_spawn_time < self.wave_delay:
            return
        
        try:
            enemy_type, stage = self.enemies_to_spawn.pop(0)
            enemy = None
            
          
            wave_number = self.current_wave
            
            if enemy_type == "rackettra":
                enemy = Rackettra(self.path)
                enemy.wave_number = wave_number
               
                if wave_number > 35:
                    enemy.hp *= 2
                    enemy.max_hp *= 2
            elif enemy_type == "space_rex":
                enemy = SpaceRex(self.path)
                enemy.wave_number = wave_number

                if wave_number > 35:
                    enemy.hp *= 2
                    enemy.max_hp *= 2
            elif enemy_type == "enviorollante":
                enemy = Enviorollante(self.path)
                enemy.wave_number = wave_number
              
                if wave_number > 35:
                    enemy.hp *= 2
                    enemy.max_hp *= 2
            elif enemy_type == "hydra_boss":
                enemy = EmperorHydra(self.path, is_boss=True)
                enemy.wave_number = wave_number
            elif enemy_type == "demolishyah":
                enemy = Demolishyah(self.path, stage or 1)
                enemy.wave_number = wave_number
            
            if enemy:
                self.enemies.append(enemy)
                self.last_spawn_time = current_time
        except Exception as e:
            print(f"Error spawning enemy: {e}")
            self.enemies_to_spawn = []
            self.game_state = "wave_prep"
    
    def update(self):
        current_time = pygame.time.get_ticks()
        
        # Spawn enemies
        if self.game_state == "playing":
            self.spawn_enemy(current_time)
        
        # Update enemies
        for enemy in self.enemies[:]:
            if not enemy.is_alive:
                self.enemies.remove(enemy)
                self.cash += self._get_enemy_reward(enemy)
                continue
            
           
            enemy_update = enemy.update() if hasattr(enemy, 'update') else None
            if enemy_update:
                if enemy_update.get("action") == "damage_base":
                    self.base_hp -= enemy_update["damage"]
                    if self.base_hp <= 0:
                        self.game_state = "game_over"
                        return
            
            if enemy.move():  
                self.base_hp -= enemy.damage
                self.enemies.remove(enemy)
                if self.base_hp <= 0:
                    self.game_state = "game_over"
                    return
        
        
        if self.game_state == "playing" and not self.enemies and not self.enemies_to_spawn:
            if self.current_wave == self.max_waves:
                self.game_state = "victory"
            else:
                self.game_state = "wave_prep"
               
                reward = self._get_wave_completion_reward()
                self.cash += reward
                
                self.wave_reward = reward
                if self.auto_skip:  
                    self.start_wave()
    
    def _get_enemy_reward(self, enemy):
        if isinstance(enemy, Rackettra):
            return 10
        elif isinstance(enemy, SpaceRex):
            return 15
        elif isinstance(enemy, Enviorollante):
            return 15
        elif isinstance(enemy, EmperorHydra):
            return 20
        elif isinstance(enemy, Demolishyah):
            return 50 * enemy.stage
        return 10  
    
    def _get_wave_completion_reward(self):
      
        if self.current_wave < 10:
            return 10
        elif self.current_wave < 20:
            return 20
        elif self.current_wave < 30:
            return 30
        elif self.current_wave < 40:
            return 40
        else:  # waves 40-49
            return 50
    
    def can_place_tower(self, position, tower_size=40):
        # Check if position is on path
        for i in range(len(self.path) - 1):
            start = pygame.math.Vector2(self.path[i])
            end = pygame.math.Vector2(self.path[i + 1])
            
           
            if start.x == end.x:  
                rect = pygame.Rect(
                    start.x - 20, min(start.y, end.y),
                    40, abs(end.y - start.y)
                )
            else:  
                rect = pygame.Rect(
                    min(start.x, end.x), start.y - 20,
                    abs(end.x - start.x), 40
                )
            
            tower_rect = pygame.Rect(
                position[0] - tower_size/2,
                position[1] - tower_size/2,
                tower_size, tower_size
            )
            if rect.colliderect(tower_rect):
                return False
        
        for tower in self.towers:
            if (pygame.math.Vector2(position) - tower.position).length() < tower_size:
                return False
        
        return True
    
    def sell_tower(self, position):
        for tower in self.towers[:]:
            if tower.rect.collidepoint(position):
                self.towers.remove(tower)
                self.cash += tower.get_sell_value()
                return True
        return False
    
    def toggle_auto_skip(self):
        self.auto_skip = not self.auto_skip
        return self.auto_skip 
