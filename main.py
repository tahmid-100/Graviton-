# main.py
# Main game loop and event handling

import pygame
import sys
from constants import *
from game_board import GameBoard
from minimax_ai import MinimaxAI
from animation import Animation
from ui import UIRenderer
from fuzzy_logic import FuzzyLogic


class Game:
    """Main game controller"""
    
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Graviton")
        self.clock = pygame.time.Clock()
        
        self.ui = UIRenderer(self.screen)
        self.board = None
        self.difficulty = None
        self.game_mode = None  # 'pvai' or 'aivai'
        self.state = 'menu'  # menu, playing, game_over
        self.ship_count_input = ""
        self.ai_player = None  # AI for 'ai' side
        self.ai_opponent = None  # AI for 'player' side (in AI vs AI mode)
        self.ai_thinking = False
        self.animation = Animation()
        self.target_planet = None
        self.message_display = None
        self.message_timer = 0
        self.ai_move_delay = AI_VS_AI_DELAY  # Delay between AI moves
        self.ai_move_timer = 0
        self.paused = False  # For AI vs AI pause feature
        self.speed_multiplier = 1.0  # Speed control for AI vs AI
    
    def handle_menu_click(self, pos):
        """Handle clicks on menu screen"""
        pvai_rect, aivai_rect, easy_rect, medium_rect, hard_rect = self.ui.draw_menu()
        
        # Check mode selection
        if pvai_rect.collidepoint(pos):
            self.game_mode = 'pvai'
            self.message_display = "Player vs AI selected. Choose difficulty."
            self.message_timer = 120
        elif aivai_rect.collidepoint(pos):
            self.game_mode = 'aivai'
            self.message_display = "AI vs AI selected. Choose difficulty."
            self.message_timer = 120
        
        # Check difficulty selection (only if mode is selected)
        if self.game_mode:
            if easy_rect.collidepoint(pos):
                self.start_game('easy')
            elif medium_rect.collidepoint(pos):
                self.start_game('medium')
            elif hard_rect.collidepoint(pos):
                self.start_game('hard')
    
    def start_game(self, difficulty):
        """Initialize new game"""
        self.difficulty = difficulty
        self.board = GameBoard(ai_vs_ai=(self.game_mode == 'aivai'))
        
        if self.game_mode == 'aivai':
            # Create two AI players with same difficulty; specify which owner each controls
            self.ai_player = MinimaxAI(self.board, difficulty, owner='ai')  # Controls 'ai' side (RED)
            self.ai_opponent = MinimaxAI(self.board, difficulty, owner='player')  # Controls 'player' side (BLUE)
            self.ai_move_timer = self.ai_move_delay
            print(f"\n=== AI vs AI Match Started ===")
            print(f"Difficulty: {difficulty.upper()}")
            print(f"AI Blue (player side) vs AI Red (ai side)")
        else:
            # Player vs AI mode
            self.ai_player = MinimaxAI(self.board, difficulty)
            self.ai_opponent = None
            print(f"\n=== Player vs AI Match Started ===")
            print(f"Difficulty: {difficulty.upper()}")
        
        self.state = 'playing'
        self.ship_count_input = ""
        self.target_planet = None
        self.message_display = None
        self.message_timer = 0
        self.paused = False
        self.speed_multiplier = 1.0
        self.ai_thinking = False
    
    def handle_board_click(self, pos):
        """Handle clicks on game board"""
        if self.board.current_player != 'player':
            return
        
        # Convert screen coordinates to grid coordinates
        x = (pos[0] - BOARD_OFFSET_X) // CELL_SIZE
        y = (pos[1] - BOARD_OFFSET_Y) // CELL_SIZE
        
        if 0 <= x < BOARD_SIZE and 0 <= y < BOARD_SIZE:
            planet = self.board.get_planet_at(x, y)
            
            if self.board.selected_planet is None:
                # Select source planet
                if planet.owner == 'player' and planet.ships > 1:
                    self.board.selected_planet = planet
                    self.message_display = f"Selected planet at {planet.get_position()}"
                    self.message_timer = 60
            else:
                # Select target planet
                if planet != self.board.selected_planet:
                    self.target_planet = planet
                    self.message_display = f"Target: {planet.get_position()}. Enter ships and press ENTER"
                    self.message_timer = 120
                else:
                    # Deselect
                    self.board.selected_planet = None
                    self.target_planet = None
                    self.ship_count_input = ""
                    self.message_display = "Planet deselected"
                    self.message_timer = 60
    
    def execute_player_attack(self):
        """Execute player's attack"""
        if not self.ship_count_input.isdigit() or int(self.ship_count_input) <= 0:
            self.message_display = "Please enter a valid number of ships"
            self.message_timer = 120
            return
        
        ship_count = int(self.ship_count_input)
        
        if ship_count >= self.board.selected_planet.ships:
            self.message_display = "Not enough ships! Must leave at least 1"
            self.message_timer = 120
            return
        
        attack_info = self.board.attack(self.board.selected_planet, self.target_planet, ship_count)
        
        if attack_info:
            # Add animation
            source_screen = (
                BOARD_OFFSET_X + attack_info['source'][0] * CELL_SIZE + CELL_SIZE // 2,
                BOARD_OFFSET_Y + attack_info['source'][1] * CELL_SIZE + CELL_SIZE // 2
            )
            target_screen = (
                BOARD_OFFSET_X + attack_info['target'][0] * CELL_SIZE + CELL_SIZE // 2,
                BOARD_OFFSET_Y + attack_info['target'][1] * CELL_SIZE + CELL_SIZE // 2
            )
            self.animation.add_attack(source_screen, target_screen, BLUE)
            
            self.message_display = f"Attack sent: {ship_count} ships!"
            self.message_timer = 120
            
            self.board.selected_planet = None
            self.target_planet = None
            self.ship_count_input = ""
        else:
            self.message_display = "Attack failed! Invalid move"
            self.message_timer = 120
    
    def execute_ai_turn(self, player):
        """Execute AI's turn for specified player"""
        # Select correct AI based on player
        if player == 'ai':
            ai = self.ai_player
            ai_name = "AI RED"
            color_for_anim = RED
        else:  # player == 'player'
            ai = self.ai_opponent
            ai_name = "AI BLUE"
            color_for_anim = BLUE
        
        # Get best move using minimax
        best_move = ai.get_best_move()
        
        if best_move:
            source, target, ships = best_move
            
            # Debug output
            aggressiveness = ai.fuzzy.evaluate_attack(source, target, player)
            print(f"\n=== {ai_name} MOVE (Turn {self.board.turn // 2 + 1}) ===")
            print(f"From: {source.get_position()} ({source.ships} ships)")
            print(f"To: {target.get_position()} ({target.ships} ships, Owner: {target.owner})")
            print(f"Sending: {ships} ships")
            print(f"Aggressiveness: {aggressiveness:.2f}")
            
            attack_info = self.board.attack(source, target, ships)
            
            # Add animation
            if attack_info:
                source_screen = (
                    BOARD_OFFSET_X + attack_info['source'][0] * CELL_SIZE + CELL_SIZE // 2,
                    BOARD_OFFSET_Y + attack_info['source'][1] * CELL_SIZE + CELL_SIZE // 2
                )
                target_screen = (
                    BOARD_OFFSET_X + attack_info['target'][0] * CELL_SIZE + CELL_SIZE // 2,
                    BOARD_OFFSET_Y + attack_info['target'][1] * CELL_SIZE + CELL_SIZE // 2
                )
                self.animation.add_attack(source_screen, target_screen, color_for_anim)
        else:
            print(f"\n=== {ai_name} has no valid moves! ===")
        
        # End turn
        self.board.end_turn()
        
        # In AI vs AI mode, continue auto-play
        if self.board.ai_vs_ai and not self.board.game_over:
            self.ai_move_timer = int(self.ai_move_delay / self.speed_multiplier)
        else:
            self.ai_thinking = False
    
    def show_fuzzy_analysis(self):
        """Show fuzzy logic analysis (debug feature)"""
        if not self.board.selected_planet or not self.target_planet:
            return
        
        fuzzy = FuzzyLogic(self.board)
        aggressiveness = fuzzy.evaluate_attack(
            self.board.selected_planet, 
            self.target_planet, 
            'player'
        )
        recommended = fuzzy.get_ship_count_recommendation(
            self.board.selected_planet,
            self.target_planet,
            'player',
            aggressiveness
        )
        strategic_value = fuzzy.calculate_strategic_value(self.target_planet)
        
        print(f"\n=== FUZZY LOGIC ANALYSIS ===")
        print(f"Source: {self.board.selected_planet.get_position()} ({self.board.selected_planet.ships} ships)")
        print(f"Target: {self.target_planet.get_position()} ({self.target_planet.ships} ships)")
        print(f"Strategic Value: {strategic_value:.2f}")
        print(f"Aggressiveness: {aggressiveness:.2f}")
        print(f"Recommended Ships: {recommended}")
    
    def run(self):
        """Main game loop"""
        running = True
        
        while running:
            # Event handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                if self.state == 'menu':
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        self.handle_menu_click(event.pos)
                
                elif self.state == 'playing':
                    if event.type == pygame.MOUSEBUTTONDOWN and not self.board.game_over:
                        # Only allow clicks in Player vs AI mode
                        if not self.board.ai_vs_ai:
                            self.handle_board_click(event.pos)
                    
                    elif event.type == pygame.KEYDOWN:
                        if self.board.game_over:
                            if event.key == pygame.K_r:
                                # Restart with same settings
                                self.start_game(self.difficulty)
                            elif event.key == pygame.K_ESCAPE:
                                self.state = 'menu'
                                self.game_mode = None
                        else:
                            # AI vs AI controls
                            if self.board.ai_vs_ai:
                                if event.key == pygame.K_SPACE:
                                    self.paused = not self.paused
                                    status = "PAUSED" if self.paused else "RESUMED"
                                    self.message_display = f"Game {status}"
                                    self.message_timer = 60
                                elif event.key == pygame.K_EQUALS or event.key == pygame.K_PLUS:
                                    self.speed_multiplier = min(4.0, self.speed_multiplier * 1.5)
                                    self.message_display = f"Speed: {self.speed_multiplier:.1f}x"
                                    self.message_timer = 60
                                elif event.key == pygame.K_MINUS:
                                    self.speed_multiplier = max(0.25, self.speed_multiplier / 1.5)
                                    self.message_display = f"Speed: {self.speed_multiplier:.1f}x"
                                    self.message_timer = 60
                                elif event.key == pygame.K_ESCAPE:
                                    self.state = 'menu'
                                    self.game_mode = None
                            
                            # Player vs AI controls
                            else:
                                if event.key == pygame.K_SPACE and self.board.current_player == 'player':
                                    self.board.end_turn()
                                    self.ai_thinking = True
                                
                                elif event.key == pygame.K_RETURN and self.board.selected_planet and self.target_planet:
                                    self.execute_player_attack()
                                
                                elif event.key == pygame.K_BACKSPACE:
                                    self.ship_count_input = self.ship_count_input[:-1]
                                
                                elif event.key == pygame.K_f:
                                    self.show_fuzzy_analysis()
                                
                                elif event.unicode.isdigit() and self.board.selected_planet and self.target_planet:
                                    self.ship_count_input += event.unicode
                                
                                elif event.key == pygame.K_ESCAPE:
                                    self.state = 'menu'
                                    self.game_mode = None
            
            # Update
            self.animation.update()
            if self.message_timer > 0:
                self.message_timer -= 1
            
            # AI turn execution
            if self.board and not self.board.game_over:
                if self.board.ai_vs_ai:
                    # AI vs AI mode - both sides are AI
                    if not self.paused:
                        self.ai_move_timer -= 1
                        if self.ai_move_timer <= 0:
                            # Execute current player's AI turn
                            self.execute_ai_turn(self.board.current_player)
                            self.ai_move_timer = int(self.ai_move_delay / self.speed_multiplier)
                else:
                    # Player vs AI mode - only execute if it's AI's turn
                    if self.board.current_player == 'ai' and self.ai_thinking:
                        self.execute_ai_turn('ai')
            
            # Render
            if self.state == 'menu':
                self.ui.draw_menu()
                # Draw mode selection message if any
                if self.message_display and self.message_timer > 0:
                    msg_surface = pygame.font.Font(None, 24).render(self.message_display, True, GREEN)
                    msg_rect = msg_surface.get_rect(center=(WINDOW_WIDTH // 2, 350))
                    self.screen.blit(msg_surface, msg_rect)
            elif self.state == 'playing':
                self.ui.draw_board(self.board, self.animation, self.message_display, 
                                  self.message_timer, self.ship_count_input, self.difficulty, self.game_mode)
                
                # Show pause indicator
                if self.board.ai_vs_ai and self.paused:
                    pause_font = pygame.font.Font(None, 36)
                    pause_text = pause_font.render("PAUSED", True, YELLOW)
                    pause_rect = pause_text.get_rect(center=(WINDOW_WIDTH // 2, 50))
                    pygame.draw.rect(self.screen, BLACK, pause_rect.inflate(20, 10))
                    pygame.draw.rect(self.screen, YELLOW, pause_rect.inflate(20, 10), 2)
                    self.screen.blit(pause_text, pause_rect)
                
                if self.board.game_over:
                    self.ui.draw_game_over(self.board.winner, self.board.ai_vs_ai)
            
            pygame.display.flip()
            self.clock.tick(60)
        
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = Game()
    game.run()