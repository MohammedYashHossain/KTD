import pygame
from pygame.math import Vector2

class Enemy:
    def __init__(self, path, hp, speed, damage):
        self.position = Vector2(path[0])  # Start at first point of path
        self.path = path
        self.current_path_index = 0
        # Calculate HP scaling based on wave number (passed from game manager)
        wave_scaling = 1.0
        if hasattr(self, 'wave_number'):
            scaling_factor = (self.wave_number // 5) * 0.2  # 20% increase every 5 waves
            wave_scaling = 1.0 + scaling_factor
        self.hp = hp * 0.6 * wave_scaling  # Base reduction + wave scaling
        self.max_hp = hp * 0.6 * wave_scaling
        self.speed = speed * 0.5  # Reduce speed by 50%
        self.damage = damage
        self.target = Vector2(path[1])  # Next point to move towards
        self.rect = pygame.Rect(self.position.x - 20, self.position.y - 20, 40, 40)
        self.is_alive = True
        self.effects = {}  # Dictionary to store active effects (slow, poison, etc.)
        self.sprite = None  # Will be set by child classes
    
    def move(self):
        if self.current_path_index >= len(self.path) - 1:
            return True  # Reached the end
        
        direction = self.target - self.position
        if direction.length() <= self.speed:
            self.position = Vector2(self.target)
            self.current_path_index += 1
            if self.current_path_index < len(self.path) - 1:
                self.target = Vector2(self.path[self.current_path_index + 1])
        else:
            direction = direction.normalize() * self.speed
            # Apply slow effect if present
            if "slow" in self.effects:
                direction *= (1 - self.effects["slow"]["amount"])
            self.position += direction
        
        # Update rectangle position
        self.rect.center = self.position
        return False
    
    def take_damage(self, amount):
        self.hp -= amount
        if self.hp <= 0:
            self.is_alive = False
            return True
        return False
    
    def draw(self, screen):
        # Draw enemy sprite or fallback to rectangle
        if self.sprite:
            screen.blit(self.sprite, (self.rect.x, self.rect.y))
        else:
            pygame.draw.rect(screen, (255, 0, 0), self.rect)
            
        # Draw health bar
        health_bar_width = 40
        health_percentage = self.hp / self.max_hp
        pygame.draw.rect(screen, (255, 0, 0), 
                        (self.rect.x, self.rect.y - 10, health_bar_width, 5))
        pygame.draw.rect(screen, (0, 255, 0),
                        (self.rect.x, self.rect.y - 10, health_bar_width * health_percentage, 5))

class Rackettra(Enemy):
    def __init__(self, path):
        super().__init__(path, hp=30, speed=2.0, damage=5)  # Reduced from 50 HP and 3.0 speed
        self.flying = True
        try:
            self.sprite = pygame.image.load("assets/Rackettra.png")
            self.sprite = pygame.transform.scale(self.sprite, (40, 40))
        except Exception as e:
            print(f"Error loading Rackettra sprite: {e}")
            self.sprite = None
    
    def apply_effect(self, effect_type, amount, duration):
        if effect_type == "slow" and self.flying:
            return False  # Immune to slow effects
        self.effects[effect_type] = {"amount": amount, "duration": duration}
        return True

class SpaceRex(Enemy):
    def __init__(self, path):
        super().__init__(path, hp=180, speed=1.5, damage=20)  # Increased speed from 0.7 to 1.0 (still slower than Rackettra's 2.0)
        self.crystal_spawn_timer = 0
        try:
            self.sprite = pygame.image.load("assets/Space_Rex.png")
            self.sprite = pygame.transform.scale(self.sprite, (40, 40))
        except Exception as e:
            print(f"Error loading Space Rex sprite: {e}")
            self.sprite = None
    
    def update(self):
        self.crystal_spawn_timer += 1
        if self.crystal_spawn_timer >= 180:  # Spawn crystal every 3 seconds
            self.crystal_spawn_timer = 0
            return {"action": "spawn_crystal", "position": Vector2(self.position)}
        return None

    def take_damage(self, amount):
        self.hp -= amount
        if self.hp <= 0:
            self.is_alive = False
            # If this is a boss (determined by wave number in game manager)
            if hasattr(self, 'wave_number') and self.wave_number in [30, 40]:
                # Spawn 3 regular enemies on death
                return {
                    "action": "spawn_on_death",
                    "enemies": [
                        {"type": "Rackettra", "position": Vector2(self.position)},
                        {"type": "SpaceRex", "position": Vector2(self.position)},
                        {"type": "Enviorollante", "position": Vector2(self.position)}
                    ]
                }
            return True
        return False

class Enviorollante(Enemy):
    def __init__(self, path):
        super().__init__(path, hp=150, speed=0.8, damage=15)
        self.heal_timer = 0
        try:
            self.sprite = pygame.image.load("assets/Enviorollante.png")
            self.sprite = pygame.transform.scale(self.sprite, (40, 40))
        except Exception as e:
            print(f"Error loading Enviorollante sprite: {e}")
            self.sprite = None
    
    def update(self):
        self.heal_timer += 1
        if self.heal_timer >= 30:  # Heal every 0.5 seconds (changed from 60)
            self.heal_timer = 0
            self.hp = min(self.hp + 8, self.max_hp)  # Increased heal amount from 5 to 8

class EmperorHydra(Enemy):
    def __init__(self, path, is_boss=False):
        # Final boss stats
        hp = 8000 if is_boss else 240
        speed = 0.7 if is_boss else 0.9
        damage = 100 if is_boss else 25
        super().__init__(path, hp=hp, speed=speed, damage=damage)
        self.is_boss = is_boss
        self.lightning_cooldown = 180 if is_boss else 360
        self.regen_amount = 20 if is_boss else 0
        self.base_damage_timer = 0 if is_boss else None
        self.lightning_timer = 0
        
        try:
            self.sprite = pygame.image.load("assets/EmperorHydra.png")
            self.sprite = pygame.transform.scale(self.sprite, (40, 40))
        except Exception as e:
            print(f"Error loading EmperorHydra sprite: {e}")
            self.sprite = None
        
        # Add wave number scaling after round 35
        if hasattr(self, 'wave_number') and self.wave_number > 35:
            self.hp *= 2  # Double health after round 35
            self.max_hp = self.hp  # Also double max health to maintain health bar display

    def update(self):
        self.lightning_timer += 1
        
        # Boss version regenerates health and damages base
        if self.is_boss:
            if self.lightning_timer % 60 == 0:  # Every second
                self.hp = min(self.hp + self.regen_amount, self.max_hp)
            
            # Automatic base damage every 7 seconds
            self.base_damage_timer += 1
            if self.base_damage_timer >= 420:  # 7 seconds * 60 frames
                self.base_damage_timer = 0
                return {
                    "action": "damage_base",
                    "damage": 5
                }
        
        if self.lightning_timer >= self.lightning_cooldown:
            self.lightning_timer = 0
            return {
                "action": "lightning_attack",
                "position": Vector2(self.position),
                "damage": self.damage * 2 if self.is_boss else self.damage
            }
        return None

    def take_damage(self, amount):
        self.hp -= amount
        if self.hp <= 0:
            self.is_alive = False
            # If this is a boss (determined by wave number in game manager)
            if hasattr(self, 'wave_number') and self.wave_number in [30, 40]:
                # Spawn 4 enemies on death for boss version
                return {
                    "action": "spawn_on_death",
                    "enemies": [
                        {"type": "Rackettra", "position": Vector2(self.position)},
                        {"type": "SpaceRex", "position": Vector2(self.position)},
                        {"type": "Enviorollante", "position": Vector2(self.position)},
                        {"type": "EmperorHydra", "position": Vector2(self.position)}
                    ]
                }
            return True
        return False

class Demolishyah(Enemy):
    def __init__(self, path, stage=1):
        # Significantly increased HP for each stage
        hp = 800 * stage  # Increased from 600 * stage
        speed = 1 + (stage * 0.15)
        damage = 50 * stage
        super().__init__(path, hp=hp, speed=speed, damage=damage)
        self.stage = stage
        self.special_timer = 0
        self.base_damage_timer = 0 if stage == 4 else None  # Only final form has base damage
        self.regen_amount = 5 if stage == 4 else 0  # Only final form has health regen
        
        try:
            sprite_path = f"assets/Demolishyah_Stage_{stage}.png"
            self.sprite = pygame.image.load(sprite_path)
            self.sprite = pygame.transform.scale(self.sprite, (40, 40))
        except Exception as e:
            print(f"Error loading Demolishyah stage {stage} sprite: {e}")
            self.sprite = None
    
    def update(self):
        self.special_timer += 1
        
        # Health regeneration for final form
        if self.stage == 4 and self.special_timer % 60 == 0:  # Every second
            self.hp = min(self.hp + self.regen_amount, self.max_hp)
        
        # Base damage for final form
        if self.stage == 4:
            self.base_damage_timer += 1
            if self.base_damage_timer >= 420:  # 7 seconds * 60 frames
                self.base_damage_timer = 0
                return {"action": "damage_base", "damage": 5}
        
        # Special abilities
        if self.special_timer >= 300:  # Special ability every 5 seconds
            self.special_timer = 0
            if self.stage == 1:
                return {"action": "roar", "position": Vector2(self.position)}
            elif self.stage == 2:
                return {"action": "aoe_attack", "position": Vector2(self.position)}
            elif self.stage >= 3:  # Both stage 3 and 4 can summon minions
                return {"action": "summon_minions", "position": Vector2(self.position)} 