import pygame
import random
from enemy import Rackettra, SpaceRex, Enviorollante, EmperorHydra, Demolishyah

class GameManager:
    def __init__(self):
        self.current_wave = 0
        self.max_waves = 50
        self.cash = 200
        self.base_hp = 100
        self.game_state = "menu"  # menu, wave_prep, playing, game_over
        self.enemies = []
        self.towers = []
        self.projectiles = []
        self.effects = []
        self.wave_delay = 1000  # Delay between enemy spawns in ms
        self.last_spawn_time = 0
        self.enemies_to_spawn = []
        self.auto_skip = False  # New auto-skip feature
        self.max_towers = 20  # Maximum number of towers allowed
        self.path = [
            (50, 50),     # Start
            (200, 50),    # First horizontal
            (200, 150),   # Down
            (400, 150),   # Right
            (400, 50),    # Up
            (600, 50),    # Right
            (600, 250),   # Long down
            (400, 250),   # Left
            (400, 350),   # Down
            (700, 350),   # Right
            (700, 450),   # Down
            (300, 450),   # Long left
            (300, 550),   # Down
            (500, 550),   # Right
            (500, 650),   # Down
            (800, 650),   # Final stretch
            (950, 650)    # End
        ]  # Longer, more complex path with multiple turns
        
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
            # Set boss wave notification
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
        
        # Regular waves have enemies equal to the wave number
        num_enemies = self.current_wave  # Remove the min() cap to allow unlimited enemies
        
        # Adjust wave_delay based on wave number
        self.wave_delay = max(500, 1000 - (self.current_wave * 10))
        
        # Choose enemy types based on wave progression
        available_enemies = ["rackettra"]  # Always have at least one enemy type
        
        if self.current_wave > 10:
            available_enemies.append("space_rex")
        if self.current_wave > 20:
            available_enemies.append("enviorollante")
        
        # Generate enemies
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
            
            # Set wave number for HP scaling
            wave_number = self.current_wave
            
            if enemy_type == "rackettra":
                enemy = Rackettra(self.path)
                enemy.wave_number = wave_number
                # Apply 2x health scaling after round 35
                if wave_number > 35:
                    enemy.hp *= 2
                    enemy.max_hp *= 2
            elif enemy_type == "space_rex":
                enemy = SpaceRex(self.path)
                enemy.wave_number = wave_number
                # Apply 2x health scaling after round 35
                if wave_number > 35:
                    enemy.hp *= 2
                    enemy.max_hp *= 2
            elif enemy_type == "enviorollante":
                enemy = Enviorollante(self.path)
                enemy.wave_number = wave_number
                # Apply 2x health scaling after round 35
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
            
            # Update enemy and handle any special actions
            enemy_update = enemy.update() if hasattr(enemy, 'update') else None
            if enemy_update:
                if enemy_update.get("action") == "damage_base":
                    self.base_hp -= enemy_update["damage"]
                    if self.base_hp <= 0:
                        self.game_state = "game_over"
                        return
            
            if enemy.move():  # Returns True if reached end
                self.base_hp -= enemy.damage
                self.enemies.remove(enemy)
                if self.base_hp <= 0:
                    self.game_state = "game_over"
                    return
        
        # Check if wave is complete
        if self.game_state == "playing" and not self.enemies and not self.enemies_to_spawn:
            if self.current_wave == self.max_waves:
                self.game_state = "victory"
            else:
                self.game_state = "wave_prep"
                # Add wave completion reward
                reward = self._get_wave_completion_reward()
                self.cash += reward
                # Signal UI to show reward (will be handled in main.py)
                self.wave_reward = reward
                if self.auto_skip:  # Auto-start next wave if enabled
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
        return 10  # Default reward
    
    def _get_wave_completion_reward(self):
        # Wave completion rewards based on wave ranges
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
        # Check tower limit first
        if len(self.towers) >= self.max_towers:
            return False

        # Check if position is on path
        for i in range(len(self.path) - 1):
            start = pygame.math.Vector2(self.path[i])
            end = pygame.math.Vector2(self.path[i + 1])
            
            # Create a rect for the path segment
            if start.x == end.x:  # Vertical path
                rect = pygame.Rect(
                    start.x - 20, min(start.y, end.y),
                    40, abs(end.y - start.y)
                )
            else:  # Horizontal path
                rect = pygame.Rect(
                    min(start.x, end.x), start.y - 20,
                    abs(end.x - start.x), 40
                )
            
            # Check if tower overlaps with path
            tower_rect = pygame.Rect(
                position[0] - tower_size/2,
                position[1] - tower_size/2,
                tower_size, tower_size
            )
            if rect.colliderect(tower_rect):
                return False
        
        # Check collision with other towers
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