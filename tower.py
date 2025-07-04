import pygame
from pygame.math import Vector2
import math

class Tower:
    def __init__(self, x, y, damage, range, fire_rate, cost):
        self.position = Vector2(x, y)
        self.damage = damage * 1.5  # Increase damage by 50%
        self.range = range
        self.fire_rate = fire_rate
        self.cost = cost
        self.last_shot = 0
        self.target = None
        self.rect = pygame.Rect(x - 20, y - 20, 40, 40)
        self.sprite = None  # Will be set by child classes
    
    def can_shoot(self, current_time):
        return current_time - self.last_shot >= self.fire_rate * 1000  # Convert to milliseconds
    
    def in_range(self, enemy):
        distance = (enemy.position - self.position).length()
        return distance <= self.range
    
    def acquire_target(self, enemies):
        self.target = None
        min_distance = float('inf')
        for enemy in enemies:
            if not enemy.is_alive:
                continue
            distance = (enemy.position - self.position).length()
            if distance <= self.range and distance < min_distance:
                min_distance = distance
                self.target = enemy
    
    def shoot(self, current_time):
        self.last_shot = current_time
        return {"type": "basic", "damage": self.damage, "target": self.target}
    
    def draw(self, screen, show_range=False):
        # Draw tower sprite or fallback to rectangle
        if self.sprite:
            screen.blit(self.sprite, (self.rect.x, self.rect.y))
        else:
            pygame.draw.rect(screen, (0, 0, 255), self.rect)
        
        # Draw range circle if requested
        if show_range:
            pygame.draw.circle(screen, (100, 100, 100, 128), 
                             (int(self.position.x), int(self.position.y)), 
                             self.range, 1)
    
    def get_sell_value(self):
        return self.cost // 2  # Return half the original cost

class Type90Tank(Tower):
    def __init__(self, x, y):
        super().__init__(x, y, damage=10, range=100, fire_rate=1.0, cost=100)
        try:
            self.sprite = pygame.image.load("assets/type_90_tank.png")
            self.sprite = pygame.transform.scale(self.sprite, (40, 40))
        except Exception as e:
            print(f"Error loading Type 90 Tank sprite: {e}")
            self.sprite = None
    
    def shoot(self, current_time):
        self.last_shot = current_time
        return {
            "type": "bullet",
            "damage": self.damage,
            "target": self.target,
            "speed": 10
        }

class MaserCannon(Tower):
    def __init__(self, x, y):
        super().__init__(x, y, damage=8, range=150, fire_rate=1.5, cost=150)
        try:
            self.sprite = pygame.image.load("assets/maser_canon.png")
            self.sprite = pygame.transform.scale(self.sprite, (40, 40))
        except Exception as e:
            print(f"Error loading Maser Cannon sprite: {e}")
            self.sprite = None
    
    def shoot(self, current_time):
        self.last_shot = current_time
        return {
            "type": "maser",
            "damage": self.damage,
            "target": self.target,
            "effect": {"type": "slow", "amount": 0.5, "duration": 2000},
            "speed": 20  # Increased from default
        }

class RoboRex(Tower):
    def __init__(self, x, y):
        super().__init__(x, y, damage=50, range=150, fire_rate=2.0, cost=250)
        try:
            self.sprite = pygame.image.load("assets/robo_rex.png")
            self.sprite = pygame.transform.scale(self.sprite, (40, 40))
        except Exception as e:
            print(f"Error loading Robo Rex sprite: {e}")
            self.sprite = None
    
    def acquire_target(self, enemies):
        # Get all enemies in range
        self.targets = []
        for enemy in enemies:
            if not enemy.is_alive:
                continue
            distance = (enemy.position - self.position).length()
            if distance <= self.range:
                self.targets.append(enemy)
        # Set primary target as the first enemy in range (for visual targeting)
        self.target = self.targets[0] if self.targets else None
    
    def shoot(self, current_time):
        self.last_shot = current_time
        if not self.targets:
            return None
        
        # Create a central explosion point (either at the first target or center of mass)
        if self.target:
            explosion_center = Vector2(self.target.position)
        else:
            # Calculate center of mass of all targets as fallback
            center_x = sum(target.position.x for target in self.targets) / len(self.targets)
            center_y = sum(target.position.y for target in self.targets) / len(self.targets)
            explosion_center = Vector2(center_x, center_y)
        
        return {
            "type": "missile",  # Changed to single missile with larger AOE
            "damage": self.damage,
            "target": explosion_center,  # Target the explosion center
            "aoe_radius": self.range * 0.8  # AOE radius is 80% of tower range
        }

class Butterflya(Tower):
    def __init__(self, x, y):
        super().__init__(x, y, damage=2, range=250, fire_rate=0.5, cost=180)  # Reduced damage from 4 to 3
        try:
            self.sprite = pygame.image.load("assets/butterflya.png")
            self.sprite = pygame.transform.scale(self.sprite, (40, 40))
        except Exception as e:
            print(f"Error loading Butterflya sprite: {e}")
            self.sprite = None
    
    def shoot(self, current_time):
        self.last_shot = current_time
        if not self.target:
            return None
        return {
            "type": "bullet",
            "damage": self.damage,
            "target": self.target,
            "speed": 12  # Increased speed to match faster fire rate
        }

class LordRex(Tower):
    def __init__(self, x, y):
        super().__init__(x, y, damage=80, range=170, fire_rate=6.0, cost=750)  # Increased fire_rate from 4.0 to 6.0 seconds, increased damage to compensate
        try:
            self.sprite = pygame.image.load("assets/lord_rex.png")
            self.sprite = pygame.transform.scale(self.sprite, (40, 40))
        except Exception as e:
            print(f"Error loading Lord Rex sprite: {e}")
            self.sprite = None
    
    def shoot(self, current_time):
        self.last_shot = current_time
        if not self.target:
            return None
            
        # Calculate beam end point
        angle = math.atan2(self.target.position.y - self.position.y,
                          self.target.position.x - self.position.x)
        end_x = self.position.x + math.cos(angle) * self.range
        end_y = self.position.y + math.sin(angle) * self.range
        
        return {
            "type": "beam",
            "damage": self.damage,
            "start": self.position,
            "end": Vector2(end_x, end_y),
            "width": 10,
            "duration": 500  # Beam lasts for 0.5 seconds
        } 