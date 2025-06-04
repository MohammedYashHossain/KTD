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
        # Draw tower
        pygame.draw.rect(screen, (0, 0, 255), self.rect)
        # Draw range circle if requested
        if show_range:
            pygame.draw.circle(screen, (100, 100, 100, 128), 
                             (int(self.position.x), int(self.position.y)), 
                             self.range, 1)

class Type90Tank(Tower):
    def __init__(self, x, y):
        super().__init__(x, y, damage=8, range=100, fire_rate=1.0, cost=100)  # Increased from 5 damage
    
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
        super().__init__(x, y, damage=5, range=150, fire_rate=1.5, cost=150)  # Increased from 3 damage
    
    def shoot(self, current_time):
        self.last_shot = current_time
        return {
            "type": "maser",
            "damage": self.damage,
            "target": self.target,
            "effect": {"type": "slow", "amount": 0.5, "duration": 2000}  # 2 seconds
        }

class RoboRex(Tower):
    def __init__(self, x, y):
        super().__init__(x, y, damage=15, range=120, fire_rate=2.0, cost=250)  # Increased from 10 damage
    
    def shoot(self, current_time):
        self.last_shot = current_time
        return {
            "type": "missile",
            "damage": self.damage,
            "target": self.target,
            "aoe_radius": 50
        }

class Butterflya(Tower):
    def __init__(self, x, y):
        super().__init__(x, y, damage=0, range=100, fire_rate=5.0, cost=180)
    
    def shoot(self, current_time):
        self.last_shot = current_time
        return {
            "type": "heal",
            "heal_amount": 15,  # Increased from 10
            "range": self.range
        }

class LordRex(Tower):
    def __init__(self, x, y):
        super().__init__(x, y, damage=30, range=200, fire_rate=3.0, cost=350)  # Increased from 20 damage
    
    def shoot(self, current_time):
        self.last_shot = current_time
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
            "width": 10
        } 