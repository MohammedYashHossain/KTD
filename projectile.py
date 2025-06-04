import pygame
from pygame.math import Vector2
import math

class Projectile:
    def __init__(self, start_pos, target_pos, damage, speed=10):
        self.position = Vector2(start_pos)
        self.target = Vector2(target_pos)
        self.damage = damage
        self.speed = speed
        self.is_active = True
        self.rect = pygame.Rect(self.position.x - 3, self.position.y - 3, 6, 6)
    
    def update(self):
        if not self.is_active:
            return False
        
        direction = self.target - self.position
        if direction.length() <= self.speed:
            self.position = Vector2(self.target)
            self.is_active = False
            return True
        
        direction = direction.normalize() * self.speed
        self.position += direction
        self.rect.center = self.position
        return False
    
    def draw(self, screen):
        if not self.is_active:
            return
        pygame.draw.circle(screen, (255, 255, 0), 
                         (int(self.position.x), int(self.position.y)), 3)

class Bullet(Projectile):
    def __init__(self, start_pos, target_pos, damage):
        super().__init__(start_pos, target_pos, damage, speed=10)

class Maser(Projectile):
    def __init__(self, start_pos, target_pos, damage, effect):
        super().__init__(start_pos, target_pos, damage, speed=15)
        self.effect = effect
    
    def draw(self, screen):
        if not self.is_active:
            return
        pygame.draw.circle(screen, (0, 255, 255), 
                         (int(self.position.x), int(self.position.y)), 4)

class Missile(Projectile):
    def __init__(self, start_pos, target_pos, damage, aoe_radius):
        super().__init__(start_pos, target_pos, damage, speed=8)
        self.aoe_radius = aoe_radius
    
    def draw(self, screen):
        if not self.is_active:
            return
        pygame.draw.circle(screen, (255, 100, 0), 
                         (int(self.position.x), int(self.position.y)), 5)

class Beam:
    def __init__(self, start_pos, end_pos, damage, width):
        self.start = Vector2(start_pos)
        self.end = Vector2(end_pos)
        self.damage = damage
        self.width = width
        self.duration = 100  # Duration in milliseconds
        self.start_time = pygame.time.get_ticks()
        self.is_active = True
    
    def update(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.start_time >= self.duration:
            self.is_active = False
        return self.is_active
    
    def draw(self, screen):
        if not self.is_active:
            return
        pygame.draw.line(screen, (255, 0, 255), 
                        (self.start.x, self.start.y),
                        (self.end.x, self.end.y), 
                        self.width)

class HealEffect:
    def __init__(self, position, range, heal_amount):
        self.position = Vector2(position)
        self.range = range
        self.heal_amount = heal_amount
        self.duration = 500  # Duration in milliseconds
        self.start_time = pygame.time.get_ticks()
        self.is_active = True
    
    def update(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.start_time >= self.duration:
            self.is_active = False
        return self.is_active
    
    def draw(self, screen):
        if not self.is_active:
            return
        alpha = 128 * (1 - (pygame.time.get_ticks() - self.start_time) / self.duration)
        surface = pygame.Surface((self.range * 2, self.range * 2), pygame.SRCALPHA)
        pygame.draw.circle(surface, (0, 255, 0, int(alpha)), 
                         (self.range, self.range), self.range)
        screen.blit(surface, 
                   (self.position.x - self.range, self.position.y - self.range)) 