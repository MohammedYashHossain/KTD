import pygame
from tower import Type90Tank, MaserCannon, RoboRex, Butterflya, LordRex

class Button:
    def __init__(self, x, y, width, height, text, color, hover_color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.is_hovered = False
        
    def draw(self, screen, font):
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, (255, 255, 255), self.rect, 2)
        
        text_surface = font.render(self.text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Left click
            if self.rect.collidepoint(event.pos):
                return True
        return False

class UIManager:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        pygame.font.init()
        self.font = pygame.font.SysFont('Arial', 24)
        self.small_font = pygame.font.SysFont('Arial', 16)
        
        # Tower selection panel
        self.tower_buttons = [
            {"name": "Type 90 Tank", "cost": 100, "class": Type90Tank},
            {"name": "Maser Cannon", "cost": 150, "class": MaserCannon},
            {"name": "Robo Rex", "cost": 250, "class": RoboRex},
            {"name": "Butterflya", "cost": 180, "class": Butterflya},
            {"name": "Lord Rex", "cost": 350, "class": LordRex}
        ]
        
        # Create buttons
        self.buttons = {
            "start": Button(
                screen_width//2 - 100, screen_height//2 - 25,
                200, 50, "Start Game", (0, 100, 0), (0, 150, 0)
            ),
            "next_wave": Button(
                screen_width - 150, 10,
                140, 40, "Next Wave", (0, 100, 0), (0, 150, 0)
            )
        }
        
        self.selected_tower = None
        self.show_tower_range = False
        self.tooltip_text = None
        self.tooltip_pos = (0, 0)
    
    def draw_menu(self, screen):
        # Draw title
        title = self.font.render("Kaiju Tower Defense", True, (255, 255, 255))
        title_rect = title.get_rect(center=(self.screen_width//2, self.screen_height//3))
        screen.blit(title, title_rect)
        
        # Draw start button
        self.buttons["start"].draw(screen, self.font)
    
    def draw_hud(self, screen, game_manager):
        # Draw top bar
        pygame.draw.rect(screen, (50, 50, 50), (0, 0, self.screen_width, 50))
        
        # Draw cash
        cash_text = self.font.render(f"Cash: ${game_manager.cash}", True, (255, 255, 0))
        screen.blit(cash_text, (10, 10))
        
        # Draw wave number
        wave_text = self.font.render(f"Wave: {game_manager.current_wave}/50", True, (255, 255, 255))
        screen.blit(wave_text, (200, 10))
        
        # Draw base HP
        hp_text = self.font.render(f"Base HP: {game_manager.base_hp}", True, (255, 100, 100))
        screen.blit(hp_text, (400, 10))
        
        if game_manager.game_state == "wave_prep":
            self.buttons["next_wave"].draw(screen, self.font)
    
    def draw_tower_panel(self, screen, game_manager):
        panel_rect = pygame.Rect(self.screen_width - 200, 50, 200, self.screen_height - 50)
        pygame.draw.rect(screen, (50, 50, 50), panel_rect)
        
        y = 60
        for tower in self.tower_buttons:
            button_rect = pygame.Rect(self.screen_width - 180, y, 160, 50)
            color = (100, 100, 100) if game_manager.cash >= tower["cost"] else (50, 50, 50)
            
            pygame.draw.rect(screen, color, button_rect)
            pygame.draw.rect(screen, (255, 255, 255), button_rect, 1)
            
            # Draw tower name and cost
            name_text = self.small_font.render(tower["name"], True, (255, 255, 255))
            cost_text = self.small_font.render(f"${tower['cost']}", True, (255, 255, 0))
            
            screen.blit(name_text, (button_rect.x + 5, button_rect.y + 5))
            screen.blit(cost_text, (button_rect.x + 5, button_rect.y + 25))
            
            y += 60
    
    def draw_tooltip(self, screen):
        if self.tooltip_text:
            text_surface = self.small_font.render(self.tooltip_text, True, (255, 255, 255))
            background_rect = text_surface.get_rect(topleft=self.tooltip_pos)
            background_rect.inflate_ip(10, 10)
            
            pygame.draw.rect(screen, (0, 0, 0), background_rect)
            pygame.draw.rect(screen, (255, 255, 255), background_rect, 1)
            screen.blit(text_surface, self.tooltip_pos)
    
    def handle_tower_selection(self, pos, game_manager):
        if game_manager.game_state != "wave_prep":
            return None
        
        y = 60
        for tower in self.tower_buttons:
            button_rect = pygame.Rect(self.screen_width - 180, y, 160, 50)
            if button_rect.collidepoint(pos):
                if game_manager.cash >= tower["cost"]:
                    return tower
                break
            y += 60
        return None
    
    def update_tooltip(self, pos, game_manager):
        self.tooltip_text = None
        
        # Check tower buttons
        y = 60
        for tower in self.tower_buttons:
            button_rect = pygame.Rect(self.screen_width - 180, y, 160, 50)
            if button_rect.collidepoint(pos):
                self.tooltip_text = f"{tower['name']}\nCost: ${tower['cost']}"
                self.tooltip_pos = (pos[0], pos[1] + 20)
                break
            y += 60
    
    def handle_events(self, event, game_manager):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Left click
            if game_manager.game_state == "menu":
                if self.buttons["start"].rect.collidepoint(event.pos):
                    game_manager.game_state = "wave_prep"
                    return True
            
            elif game_manager.game_state == "wave_prep":
                if self.buttons["next_wave"].rect.collidepoint(event.pos):
                    game_manager.start_wave()
                    return True
                
                tower_info = self.handle_tower_selection(event.pos, game_manager)
                if tower_info:
                    self.selected_tower = tower_info
                    self.show_tower_range = True
                    return True
        
        elif event.type == pygame.MOUSEMOTION:
            # Update button hover states
            if game_manager.game_state == "menu":
                self.buttons["start"].is_hovered = self.buttons["start"].rect.collidepoint(event.pos)
            elif game_manager.game_state == "wave_prep":
                self.buttons["next_wave"].is_hovered = self.buttons["next_wave"].rect.collidepoint(event.pos)
            self.update_tooltip(event.pos, game_manager)
        
        return False 