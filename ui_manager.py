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
        pygame.mixer.init()  # Initialize the sound mixer
        self.font = pygame.font.SysFont('Arial', 24)
        self.small_font = pygame.font.SysFont('Arial', 16)
        self.boss_font = pygame.font.SysFont('Arial', 36, bold=True)
        self.boss_alert_timer = 0
        
        # Load game logo
        try:
            self.logo = pygame.image.load("assets/KTD_Logo.png")
            logo_width = 400
            logo_height = int(self.logo.get_height() * (logo_width / self.logo.get_width()))
            self.logo = pygame.transform.scale(self.logo, (logo_width, logo_height))
        except Exception as e:
            print(f"Error loading logo: {e}")
            self.logo = None
        
        # Load start game sound
        try:
            self.start_sound = pygame.mixer.Sound("assets/Intro_Roar.mp3")
            # Set volume to 70% to avoid being too loud
            self.start_sound.set_volume(0.7)
        except Exception as e:
            print(f"Error loading roar sound: {e}")
            self.start_sound = None
        
        # Tower selection panel
        self.tower_buttons = [
            {"name": "Type 90 Tank", "cost": 100, "class": Type90Tank},
            {"name": "Maser Cannon", "cost": 150, "class": MaserCannon},
            {"name": "Robo Rex", "cost": 250, "class": RoboRex},
            {"name": "Butterflya", "cost": 200, "class": Butterflya},
            {"name": "Lord Rex", "cost": 750, "class": LordRex}
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
            ),
            "auto_skip": Button(
                screen_width - 300, 10,
                140, 40, "Auto Skip: Off", (100, 100, 0), (150, 150, 0)
            )
        }
        
        self.selected_tower = None
        self.show_tower_range = False
        self.tooltip_text = None
        self.tooltip_pos = (0, 0)
        self.selling_mode = False
        self.reward_display = None
        self.reward_display_time = 0
    
    def draw_menu(self, screen):
        if self.logo:
            # Draw logo at the top center of the screen
            logo_rect = self.logo.get_rect(midtop=(self.screen_width//2, 50))
            screen.blit(self.logo, logo_rect)
            
            # Move start button below the logo
            self.buttons["start"] = Button(
                self.screen_width//2 - 100,
                logo_rect.bottom + 50,  # Position button below logo
                200, 50, "Start Game", (0, 100, 0), (0, 150, 0)
            )
        else:
            # Fallback to text title if no logo
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
        
        # Draw sell mode indicator
        if self.selling_mode:
            sell_text = self.font.render("SELL MODE", True, (255, 200, 0))
            screen.blit(sell_text, (600, 10))
        
        # Draw boss wave notification in bottom left if active
        if hasattr(game_manager, 'boss_wave_notification') and game_manager.boss_wave_notification:
            # Update flash timer for text color alternation
            self.boss_alert_timer = (self.boss_alert_timer + 1) % 60
            
            # Flash effect colors
            if self.boss_alert_timer < 30:  # First half of cycle
                text_color = (255, 0, 0)  # Red
                border_color = (255, 165, 0)  # Orange
            else:  # Second half of cycle
                text_color = (255, 165, 0)  # Orange
                border_color = (255, 0, 0)  # Red
            
            # Create the alert box
            boss_text = self.boss_font.render("BOSS WAVE!", True, text_color)
            wave_info = self.small_font.render(f"Wave {game_manager.current_wave}", True, text_color)
            
            # Position the alert box in bottom left
            text_rect = boss_text.get_rect(bottomleft=(20, self.screen_height - 40))
            wave_rect = wave_info.get_rect(bottomleft=(20, self.screen_height - 15))
            
            # Create background rectangle that encompasses both text elements
            bg_rect = pygame.Rect(
                text_rect.left - 10,
                text_rect.top - 10,
                max(text_rect.width, wave_rect.width) + 20,
                (wave_rect.bottom - text_rect.top) + 20
            )
            
            # Draw background and border
            pygame.draw.rect(screen, (0, 0, 0), bg_rect)  # Black background
            pygame.draw.rect(screen, border_color, bg_rect, 3)  # Colored border
            
            # Draw text
            screen.blit(boss_text, text_rect)
            screen.blit(wave_info, wave_rect)
        
        # Always draw auto-skip button
        self.buttons["auto_skip"].draw(screen, self.font)
        
        if game_manager.game_state == "wave_prep":
            self.buttons["next_wave"].draw(screen, self.font)
        
        # Draw reward display if active
        if self.reward_display:
            current_time = pygame.time.get_ticks()
            if current_time - self.reward_display_time < 2000:  # Show for 2 seconds
                # Calculate fade out
                alpha = 255 * (1 - (current_time - self.reward_display_time) / 2000)
                reward_text = self.font.render(self.reward_display, True, (255, 255, 0))
                reward_text.set_alpha(int(alpha))
                text_rect = reward_text.get_rect(center=(self.screen_width//2, 100))
                screen.blit(reward_text, text_rect)
            else:
                self.reward_display = None
    
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
        
        # Add controls section under the towers
        y += 20  # Add some spacing
        controls_title = self.font.render("Game Controls:", True, (255, 255, 0))
        screen.blit(controls_title, (self.screen_width - 180, y))
        
        y += 30
        controls = [
            "Right Click: Toggle Sell Mode",
            "Left Click: Place Tower",
            "ESC: Return to Menu",
            "Auto Skip: Quick Waves"
        ]
        
        for control in controls:
            control_text = self.small_font.render(control, True, (255, 255, 255))
            screen.blit(control_text, (self.screen_width - 180, y))
            y += 20
        
        # Add creator credits
        y += 30  # Extra space before credits
        credit_text = self.small_font.render("Created by:", True, (255, 255, 0))
        screen.blit(credit_text, (self.screen_width - 180, y))
        y += 20
        creator_text = self.small_font.render("Mohammed Y. Hossain", True, (255, 255, 255))
        screen.blit(creator_text, (self.screen_width - 180, y))
    
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
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                if game_manager.game_state == "menu":
                    if self.buttons["start"].rect.collidepoint(event.pos):
                        # Play roar sound if available
                        if hasattr(self, 'start_sound') and self.start_sound:
                            self.start_sound.play()
                            # Wait for roar to finish before starting background music
                            roar_length = self.start_sound.get_length()
                            pygame.time.set_timer(pygame.USEREVENT + 1, int(roar_length * 1000))
                        else:
                            # If no roar sound, start music immediately
                            pygame.mixer.music.play(-1)  # -1 means loop indefinitely
                        game_manager.game_state = "wave_prep"
                        return True
                
                # Handle auto-skip button regardless of game state
                if self.buttons["auto_skip"].rect.collidepoint(event.pos):
                    auto_skip = game_manager.toggle_auto_skip()
                    self.buttons["auto_skip"].text = f"Auto Skip: {'On' if auto_skip else 'Off'}"
                    return True
                
                elif game_manager.game_state == "wave_prep":
                    # Handle next wave button
                    if self.buttons["next_wave"].rect.collidepoint(event.pos):
                        game_manager.start_wave()
                        return True
                    
                    # Handle tower selection
                    tower_info = self.handle_tower_selection(event.pos, game_manager)
                    if tower_info:
                        self.selected_tower = tower_info
                        self.show_tower_range = True
                        self.selling_mode = False
                        return True
            
            elif event.button == 3:  # Right click
                # Toggle selling mode
                self.selling_mode = not self.selling_mode
                self.selected_tower = None
                self.show_tower_range = False
                return True
            
            # Handle tower selling
            if self.selling_mode and event.button == 1:
                if game_manager.sell_tower(event.pos):
                    self.selling_mode = False
                    return True
        
        elif event.type == pygame.MOUSEMOTION:
            # Update button hover states
            if game_manager.game_state == "menu":
                self.buttons["start"].is_hovered = self.buttons["start"].rect.collidepoint(event.pos)
            elif game_manager.game_state == "wave_prep":
                self.buttons["next_wave"].is_hovered = self.buttons["next_wave"].rect.collidepoint(event.pos)
            # Always update auto-skip button hover state
            self.buttons["auto_skip"].is_hovered = self.buttons["auto_skip"].rect.collidepoint(event.pos)
            self.update_tooltip(event.pos, game_manager)
        
        elif event.type == pygame.USEREVENT + 1:  # Custom event for starting background music
            pygame.mixer.music.play(-1)  # Start background music loop
            pygame.time.set_timer(pygame.USEREVENT + 1, 0)  # Disable the timer
        
        return False

    def show_wave_reward(self, amount):
        self.reward_display = f"+${amount} Wave Bonus!"
        self.reward_display_time = pygame.time.get_ticks() 

    def handle_events(self, event, game_manager):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                if game_manager.game_state == "menu":
                    if self.buttons["start"].rect.collidepoint(event.pos):
                        # Play roar sound if available
                        if hasattr(self, 'start_sound') and self.start_sound:
                            self.start_sound.play()
                            # Wait for roar to finish before starting background music
                            roar_length = self.start_sound.get_length()
                            pygame.time.set_timer(pygame.USEREVENT + 1, int(roar_length * 1000))
                        else:
                            # If no roar sound, start music immediately
                            pygame.mixer.music.play(-1)  # -1 means loop indefinitely
                        game_manager.game_state = "wave_prep"
                        return True
                
                # Handle auto-skip button regardless of game state
                if self.buttons["auto_skip"].rect.collidepoint(event.pos):
                    auto_skip = game_manager.toggle_auto_skip()
                    self.buttons["auto_skip"].text = f"Auto Skip: {'On' if auto_skip else 'Off'}"
                    return True
                
                elif game_manager.game_state == "wave_prep":
                    # Handle next wave button
                    if self.buttons["next_wave"].rect.collidepoint(event.pos):
                        game_manager.start_wave()
                        return True
                    
                    # Handle tower selection
                    tower_info = self.handle_tower_selection(event.pos, game_manager)
                    if tower_info:
                        self.selected_tower = tower_info
                        self.show_tower_range = True
                        self.selling_mode = False
                        return True
            
            elif event.button == 3:  # Right click
                # Toggle selling mode
                self.selling_mode = not self.selling_mode
                self.selected_tower = None
                self.show_tower_range = False
                return True
            
            # Handle tower selling
            if self.selling_mode and event.button == 1:
                if game_manager.sell_tower(event.pos):
                    self.selling_mode = False
                    return True
        
        elif event.type == pygame.MOUSEMOTION:
            # Update button hover states
            if game_manager.game_state == "menu":
                self.buttons["start"].is_hovered = self.buttons["start"].rect.collidepoint(event.pos)
            elif game_manager.game_state == "wave_prep":
                self.buttons["next_wave"].is_hovered = self.buttons["next_wave"].rect.collidepoint(event.pos)
            # Always update auto-skip button hover state
            self.buttons["auto_skip"].is_hovered = self.buttons["auto_skip"].rect.collidepoint(event.pos)
            self.update_tooltip(event.pos, game_manager)
        
        elif event.type == pygame.USEREVENT + 1:  # Custom event for starting background music
            pygame.mixer.music.play(-1)  # Start background music loop
            pygame.time.set_timer(pygame.USEREVENT + 1, 0)  # Disable the timer
        
        return False 