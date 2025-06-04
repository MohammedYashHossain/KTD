import pygame
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
        self.path = [
            (100, 50),    # Start further from edge
            (300, 50),    # Wider horizontal spread
            (300, 250),   # More vertical space
            (500, 250),   # Wider middle section
            (500, 450),   # More vertical space
            (700, 450),   # Wider end section
            (700, 650),   # More vertical drop
            (900, 650)    # End further from edge
        ]  # Larger, more spread out path
        
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
        
        # Regular waves have enemies equal to the wave number
        num_enemies = min(self.current_wave, 15)  # Cap regular wave enemies at 15
        
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
            enemy_type = pygame.random.choice(available_enemies)
            enemies.append((enemy_type, None))
        
        return enemies
    
    def spawn_enemy(self, current_time):
        if not self.enemies_to_spawn or current_time - self.last_spawn_time < self.wave_delay:
            return
        
        try:
            enemy_type, stage = self.enemies_to_spawn.pop(0)
            enemy = None
            
            if enemy_type == "rackettra":
                enemy = Rackettra(self.path)
            elif enemy_type == "space_rex":
                enemy = SpaceRex(self.path)
            elif enemy_type == "enviorollante":
                enemy = Enviorollante(self.path)
            elif enemy_type == "hydra_boss":
                enemy = EmperorHydra(self.path, is_boss=True)
            elif enemy_type == "demolishyah":
                enemy = Demolishyah(self.path, stage or 1)  # Default to stage 1 if None
            
            if enemy:
                self.enemies.append(enemy)
                self.last_spawn_time = current_time
        except Exception as e:
            print(f"Error spawning enemy: {e}")  # Debug info
            self.enemies_to_spawn = []  # Clear the wave if there's an error
            self.game_state = "wave_prep"  # Return to wave preparation
    
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
    
    def can_place_tower(self, position, tower_size=40):
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