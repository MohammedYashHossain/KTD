import pygame
from pygame.math import Vector2

class Enemy:
    def __init__(self, path, hp, speed, damage):
        self.position = Vector2(path[0])  # Start at first point of path
        self.path = path
        self.current_path_index = 0
        self.hp = hp * 0.6  # Reduce HP by 40%
        self.max_hp = hp * 0.6
        self.speed = speed * 0.5  # Reduce speed by 50%
        self.damage = damage
        self.target = Vector2(path[1])  # Next point to move towards
        self.rect = pygame.Rect(self.position.x - 20, self.position.y - 20, 40, 40)
        self.is_alive = True
        self.effects = {}  # Dictionary to store active effects (slow, poison, etc.)
    
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
        # Draw enemy
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
    
    def apply_effect(self, effect_type, amount, duration):
        if effect_type == "slow" and self.flying:
            return False  # Immune to slow effects
        self.effects[effect_type] = {"amount": amount, "duration": duration}
        return True

class SpaceRex(Enemy):
    def __init__(self, path):
        super().__init__(path, hp=180, speed=0.7, damage=20)  # Reduced from 300 HP and 1.0 speed
        self.crystal_spawn_timer = 0
    
    def update(self):
        self.crystal_spawn_timer += 1
        if self.crystal_spawn_timer >= 180:  # Spawn crystal every 3 seconds
            self.crystal_spawn_timer = 0
            return {"action": "spawn_crystal", "position": Vector2(self.position)}
        return None

class Enviorollante(Enemy):
    def __init__(self, path):
        super().__init__(path, hp=150, speed=0.8, damage=15)  # Reduced from 250 HP and 1.2 speed
        self.heal_timer = 0
    
    def update(self):
        self.heal_timer += 1
        if self.heal_timer >= 60:  # Heal every second
            self.heal_timer = 0
            self.hp = min(self.hp + 5, self.max_hp)

class EmperorHydra(Enemy):
    def __init__(self, path, is_boss=False):
        if is_boss:
            # Final boss stats
            super().__init__(path, hp=2000, speed=0.7, damage=100)  # Massive HP and damage for final boss
            self.is_boss = True
            self.lightning_cooldown = 180  # Faster lightning attacks (every 3 seconds)
            self.regen_amount = 10  # Health regeneration
        else:
            # Regular Hydra stats (not used in normal waves anymore)
            super().__init__(path, hp=240, speed=0.9, damage=25)
            self.is_boss = False
            self.lightning_cooldown = 360  # Normal lightning cooldown (6 seconds)
            self.regen_amount = 0
        self.lightning_timer = 0
    
    def update(self):
        self.lightning_timer += 1
        
        # Boss version regenerates health
        if self.is_boss and self.lightning_timer % 60 == 0:  # Every second
            self.hp = min(self.hp + self.regen_amount, self.max_hp)
        
        if self.lightning_timer >= self.lightning_cooldown:
            self.lightning_timer = 0
            return {
                "action": "lightning_attack",
                "position": Vector2(self.position),
                "damage": self.damage * 2 if self.is_boss else self.damage
            }
        return None

class Demolishyah(Enemy):
    def __init__(self, path, stage=1):
        hp = 600 * stage  # Reduced from 1000 * stage
        speed = 0.6 + (stage * 0.15)  # Reduced from 1.0 + (stage * 0.2)
        damage = 50 * stage
        super().__init__(path, hp=hp, speed=speed, damage=damage)
        self.stage = stage
        self.special_timer = 0
    
    def update(self):
        self.special_timer += 1
        if self.special_timer >= 300:  # Special ability every 5 seconds
            self.special_timer = 0
            if self.stage == 1:
                return {"action": "roar", "position": Vector2(self.position)}
            elif self.stage == 2:
                return {"action": "aoe_attack", "position": Vector2(self.position)}
            else:  # stage 3 (final form)
                return {"action": "summon_minions", "position": Vector2(self.position)} 