# ui.py
# User interface rendering (separated for readability - import in main.py)

import pygame
from constants import *


class UIRenderer:
    """Handles all UI rendering"""
    
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.Font(None, 28)
        self.large_font = pygame.font.Font(None, 48)
        self.small_font = pygame.font.Font(None, 22)
    
    def draw_menu(self):
        """Draw main menu screen"""
        self.screen.fill(BLACK)
        
        title = self.large_font.render("GRAVITON", True, YELLOW)
        title_rect = title.get_rect(center=(WINDOW_WIDTH // 2, 100))
        self.screen.blit(title, title_rect)
        
        # Mode selection
        mode_title = self.font.render("Select Game Mode:", True, WHITE)
        mode_rect = mode_title.get_rect(center=(WINDOW_WIDTH // 2, 180))
        self.screen.blit(mode_title, mode_rect)
        
        # Player vs AI button
        pvai_rect = pygame.Rect(WINDOW_WIDTH // 2 - 150, 220, 300, 50)
        pygame.draw.rect(self.screen, BLUE, pvai_rect)
        pygame.draw.rect(self.screen, WHITE, pvai_rect, 2)
        pvai_text = self.font.render("PLAYER vs AI", True, WHITE)
        self.screen.blit(pvai_text, pvai_text.get_rect(center=pvai_rect.center))
        
        # AI vs AI button
        aivai_rect = pygame.Rect(WINDOW_WIDTH // 2 - 150, 290, 300, 50)
        pygame.draw.rect(self.screen, PURPLE, aivai_rect)
        pygame.draw.rect(self.screen, WHITE, aivai_rect, 2)
        aivai_text = self.font.render("AI vs AI (Watch)", True, WHITE)
        self.screen.blit(aivai_text, aivai_text.get_rect(center=aivai_rect.center))
        
        subtitle = self.font.render("Select Difficulty:", True, WHITE)
        subtitle_rect = subtitle.get_rect(center=(WINDOW_WIDTH // 2, 370))
        self.screen.blit(subtitle, subtitle_rect)
        
        # Difficulty buttons
        easy_rect = pygame.Rect(WINDOW_WIDTH // 2 - 100, 420, 200, 60)
        medium_rect = pygame.Rect(WINDOW_WIDTH // 2 - 100, 500, 200, 60)
        hard_rect = pygame.Rect(WINDOW_WIDTH // 2 - 100, 580, 200, 60)
        
        pygame.draw.rect(self.screen, GREEN, easy_rect)
        pygame.draw.rect(self.screen, YELLOW, medium_rect)
        pygame.draw.rect(self.screen, RED, hard_rect)
        
        easy_text = self.font.render("EASY", True, BLACK)
        medium_text = self.font.render("MEDIUM", True, BLACK)
        hard_text = self.font.render("HARD", True, BLACK)
        
        self.screen.blit(easy_text, easy_text.get_rect(center=easy_rect.center))
        self.screen.blit(medium_text, medium_text.get_rect(center=medium_rect.center))
        self.screen.blit(hard_text, hard_text.get_rect(center=hard_rect.center))
        
        return pvai_rect, aivai_rect, easy_rect, medium_rect, hard_rect
    
    def draw_board(self, board, animation, message_display, message_timer, ship_count_input, difficulty, game_mode="pvai"):
        """Draw game board with all UI elements"""
        self.screen.fill(BLACK)
        
        # Draw title
        if board.ai_vs_ai:
            title_text = f"Turn {board.turn // 2 + 1} - AI {board.current_player.upper()}'s Turn"
            title_color = BLUE if board.current_player == 'player' else RED
        else:
            title_text = f"Turn {board.turn // 2 + 1} - {board.current_player.upper()}'s Turn"
            title_color = BLUE if board.current_player == 'player' else RED
        
        title = self.font.render(title_text, True, title_color)
        self.screen.blit(title, (BOARD_OFFSET_X, 20))
        
        # Show game mode and difficulty
        mode_text = "AI vs AI" if board.ai_vs_ai else "Player vs AI"
        diff_text = self.small_font.render(f"{mode_text} | Difficulty: {difficulty.upper()}", True, YELLOW)
        self.screen.blit(diff_text, (BOARD_OFFSET_X, 55))
        
        # Draw grid and planets
        self._draw_planets(board)
        
        # Draw animations
        animation.draw(self.screen)
        
        # Draw info panel
        self._draw_info_panel(board, ship_count_input)
        
        # Draw status message
        if message_display and message_timer > 0:
            self._draw_message(message_display)
    
    def _draw_planets(self, board):
        """Draw all planets on the board"""
        for y in range(BOARD_SIZE):
            for x in range(BOARD_SIZE):
                planet = board.grid[y][x]
                screen_x = BOARD_OFFSET_X + x * CELL_SIZE
                screen_y = BOARD_OFFSET_Y + y * CELL_SIZE
                
                # Draw cell border
                pygame.draw.rect(self.screen, (50, 50, 50), 
                               (screen_x, screen_y, CELL_SIZE, CELL_SIZE), 1)
                
                # Planet color based on owner
                color = LIGHT_GRAY
                if planet.owner == 'player':
                    color = BLUE
                elif planet.owner == 'ai':
                    color = RED
                
                radius = 15 + planet.size * 8
                center = (screen_x + CELL_SIZE // 2, screen_y + CELL_SIZE // 2)
                
                # Highlight selected planet with pulsing effect
                if planet == board.selected_planet:
                    pulse = abs(pygame.time.get_ticks() % 1000 - 500) / 500
                    glow_radius = radius + 5 + int(pulse * 5)
                    pygame.draw.circle(self.screen, YELLOW, center, glow_radius, 3)
                
                # Draw planet shadow
                shadow_offset = 3
                pygame.draw.circle(self.screen, (30, 30, 30), 
                                 (center[0] + shadow_offset, center[1] + shadow_offset), radius)
                
                # Draw planet
                pygame.draw.circle(self.screen, color, center, radius)
                pygame.draw.circle(self.screen, tuple(max(0, c - 50) for c in color), center, radius, 2)
                
                # Draw size
                size_text = self.small_font.render(str(planet.size), True, BLACK)
                size_rect = size_text.get_rect(center=(center[0], center[1] - 5))
                self.screen.blit(size_text, size_rect)
                
                # Draw ship count
                if planet.owner:
                    pygame.draw.circle(self.screen, BLACK, (center[0], center[1] + 10), 15)
                    ship_text = self.small_font.render(str(planet.ships), True, WHITE)
                    ship_rect = ship_text.get_rect(center=(center[0], center[1] + 10))
                    self.screen.blit(ship_text, ship_rect)
    
    def _draw_info_panel(self, board, ship_count_input):
        """Draw information panel on the right"""
        panel_x = INFO_PANEL_X
        y_offset = 100
        
        # Game status box
        pygame.draw.rect(self.screen, (30, 30, 30), (panel_x - 10, y_offset - 10, 380, 150))
        pygame.draw.rect(self.screen, YELLOW, (panel_x - 10, y_offset - 10, 380, 150), 2)
        
        info_title = self.font.render("GAME STATUS", True, YELLOW)
        self.screen.blit(info_title, (panel_x, y_offset))
        y_offset += 40
        
        # Planet counts
        player_count = len(board.get_player_planets('player'))
        ai_count = len(board.get_player_planets('ai'))
        neutral_count = len([p for p in board.planets if p.owner is None])
        
        # Label based on mode
        player_label = "AI Blue" if board.ai_vs_ai else "Player"
        ai_label = "AI Red"
        
        pygame.draw.circle(self.screen, BLUE, (panel_x - 5, y_offset + 10), 8)
        player_info = self.small_font.render(f"{player_label} Planets: {player_count}", True, WHITE)
        self.screen.blit(player_info, (panel_x + 15, y_offset))
        y_offset += 30
        
        pygame.draw.circle(self.screen, RED, (panel_x - 5, y_offset + 10), 8)
        ai_info = self.small_font.render(f"{ai_label} Planets: {ai_count}", True, WHITE)
        self.screen.blit(ai_info, (panel_x + 15, y_offset))
        y_offset += 30
        
        pygame.draw.circle(self.screen, LIGHT_GRAY, (panel_x - 5, y_offset + 10), 8)
        neutral_info = self.small_font.render(f"Neutral: {neutral_count}", True, WHITE)
        self.screen.blit(neutral_info, (panel_x + 15, y_offset))
        y_offset += 30
        
        # Turn progress bar
        turn_progress = min(1.0, (board.turn // 2) / 50)
        bar_width = 200
        bar_height = 15
        pygame.draw.rect(self.screen, (50, 50, 50), (panel_x, y_offset, bar_width, bar_height))
        pygame.draw.rect(self.screen, GREEN, (panel_x, y_offset, int(bar_width * turn_progress), bar_height))
        pygame.draw.rect(self.screen, WHITE, (panel_x, y_offset, bar_width, bar_height), 1)
        
        turn_text = self.small_font.render(f"Turn {board.turn // 2 + 1} / 15", True, WHITE)
        self.screen.blit(turn_text, (panel_x + bar_width + 10, y_offset))
        y_offset += 50
        
        # Selected planet info
        if board.selected_planet:
            y_offset = self._draw_selected_planet_info(board.selected_planet, panel_x, y_offset)
        
        # Controls
        self._draw_controls(panel_x, max(y_offset + 20, 450), ship_count_input, board.ai_vs_ai)
    
    def _draw_selected_planet_info(self, planet, panel_x, y_offset):
        """Draw selected planet information"""
        pygame.draw.rect(self.screen, (30, 30, 30), (panel_x - 10, y_offset - 10, 380, 180))
        pygame.draw.rect(self.screen, PURPLE, (panel_x - 10, y_offset - 10, 380, 180), 2)
        
        select_title = self.font.render("SELECTED PLANET", True, PURPLE)
        self.screen.blit(select_title, (panel_x, y_offset))
        y_offset += 40
        
        # Owner
        owner_text = "Neutral"
        owner_color = LIGHT_GRAY
        if planet.owner == 'player':
            owner_text = "Player"
            owner_color = BLUE
        elif planet.owner == 'ai':
            owner_text = "AI"
            owner_color = RED
        
        owner_info = self.small_font.render(f"Owner: {owner_text}", True, owner_color)
        self.screen.blit(owner_info, (panel_x, y_offset))
        y_offset += 30
        
        # Position
        pos_info = self.small_font.render(f"Position: {planet.get_position()}", True, WHITE)
        self.screen.blit(pos_info, (panel_x, y_offset))
        y_offset += 30
        
        # Size
        size_text = "★" * planet.size + "☆" * (3 - planet.size)
        size_info = self.small_font.render(f"Size: {size_text}", True, YELLOW)
        self.screen.blit(size_info, (panel_x, y_offset))
        y_offset += 30
        
        # Ships with capacity bar
        ships_info = self.small_font.render(f"Ships: {planet.ships} / {planet.max_ships}", True, WHITE)
        self.screen.blit(ships_info, (panel_x, y_offset))
        y_offset += 25
        
        capacity_ratio = planet.ships / planet.max_ships if planet.max_ships > 0 else 0
        capacity_width = 150
        pygame.draw.rect(self.screen, (50, 50, 50), (panel_x, y_offset, capacity_width, 10))
        
        bar_color = GREEN if capacity_ratio < 0.5 else YELLOW if capacity_ratio < 0.8 else RED
        pygame.draw.rect(self.screen, bar_color, (panel_x, y_offset, int(capacity_width * capacity_ratio), 10))
        pygame.draw.rect(self.screen, WHITE, (panel_x, y_offset, capacity_width, 10), 1)
        
        return y_offset + 30
    
    def _draw_controls(self, panel_x, y_offset, ship_count_input, ai_vs_ai=False):
        """Draw control instructions"""
        pygame.draw.rect(self.screen, (30, 30, 30), (panel_x - 10, y_offset - 10, 380, 200))
        pygame.draw.rect(self.screen, ORANGE, (panel_x - 10, y_offset - 10, 380, 200), 2)
        
        inst_title = self.font.render("CONTROLS", True, ORANGE)
        self.screen.blit(inst_title, (panel_x, y_offset))
        y_offset += 35
        
        if ai_vs_ai:
            instructions = [
                "• Watch AI agents battle!",
                "• SPACE to pause/resume",
                "• + to speed up",
                "• - to slow down",
                "• R to restart",
                "• ESC for menu"
            ]
        else:
            instructions = [
                "• Click planet to select",
                "• Click target to choose",
                "• Type ships to send",
                "• ENTER to confirm attack",
                "• SPACE to end turn",
                "• F for fuzzy analysis"
            ]
        
        for inst in instructions:
            inst_text = self.small_font.render(inst, True, WHITE)
            self.screen.blit(inst_text, (panel_x, y_offset))
            y_offset += 23
        
        # Ship input display (only for player mode)
        if ship_count_input and not ai_vs_ai:
            y_offset += 10
            input_bg = pygame.Rect(panel_x - 10, y_offset - 5, 150, 35)
            pygame.draw.rect(self.screen, (20, 80, 20), input_bg)
            pygame.draw.rect(self.screen, GREEN, input_bg, 2)
            
            input_text = self.font.render(f"Ships: {ship_count_input}", True, GREEN)
            self.screen.blit(input_text, (panel_x, y_offset))
    
    def _draw_message(self, message_display):
        """Draw status message at bottom of screen"""
        msg_surface = self.font.render(message_display, True, GREEN)
        msg_rect = msg_surface.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 50))
        
        bg_rect = msg_rect.inflate(20, 10)
        pygame.draw.rect(self.screen, BLACK, bg_rect)
        pygame.draw.rect(self.screen, GREEN, bg_rect, 2)
        
        self.screen.blit(msg_surface, msg_rect)
    
    def draw_game_over(self, winner, ai_vs_ai=False):
        """Draw game over screen"""
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        if winner == 'tie':
            result_text = "GAME TIED!"
            color = YELLOW
        elif winner == 'player':
            result_text = "AI BLUE WINS!" if ai_vs_ai else "YOU WIN!"
            color = GREEN if not ai_vs_ai else BLUE
        else:
            result_text = "AI RED WINS!"
            color = RED
        
        result = self.large_font.render(result_text, True, color)
        result_rect = result.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 50))
        self.screen.blit(result, result_rect)
        
        restart_text = self.font.render("Press R to restart or ESC for menu", True, WHITE)
        restart_rect = restart_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 50))
        self.screen.blit(restart_text, restart_rect)