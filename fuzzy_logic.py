# fuzzy_logic.py
# Fuzzy Logic System for decision making

class FuzzyLogic:
    """
    Fuzzy Logic System for evaluating attack aggressiveness
    
    Inputs:
    - Planet Strength: weak/medium/strong (based on ship ratio)
    - Strategic Value: low/medium/high (based on size and position)
    - Game Phase: early/mid/late (based on turn number)
    
    Output:
    - Aggressiveness: 0.0 to 1.0 (how aggressive to attack)
    """
    
    def __init__(self, board):
        self.board = board
    
    # ========== Membership Functions for Planet Strength ==========
    
    def planet_strength_weak(self, ship_ratio):
        """ship_ratio = target_ships / source_ships"""
        if ship_ratio <= 0.3:
            return 1.0
        elif ship_ratio <= 0.6:
            return (0.6 - ship_ratio) / 0.3
        return 0.0
    
    def planet_strength_medium(self, ship_ratio):
        if ship_ratio <= 0.3:
            return 0.0
        elif ship_ratio <= 0.6:
            return (ship_ratio - 0.3) / 0.3
        elif ship_ratio <= 0.9:
            return (0.9 - ship_ratio) / 0.3
        return 0.0
    
    def planet_strength_strong(self, ship_ratio):
        if ship_ratio <= 0.6:
            return 0.0
        elif ship_ratio <= 0.9:
            return (ship_ratio - 0.6) / 0.3
        return 1.0
    
    # ========== Membership Functions for Strategic Value ==========
    
    def strategic_value_low(self, value):
        """value = size + position_bonus (0-6)"""
        if value <= 2:
            return 1.0
        elif value <= 4:
            return (4 - value) / 2
        return 0.0
    
    def strategic_value_medium(self, value):
        if value <= 2:
            return 0.0
        elif value <= 4:
            return (value - 2) / 2
        elif value <= 6:
            return (6 - value) / 2
        return 0.0
    
    def strategic_value_high(self, value):
        if value <= 4:
            return 0.0
        elif value <= 6:
            return (value - 4) / 2
        return 1.0
    
    # ========== Membership Functions for Game Phase ==========
    
    def game_phase_early(self, turn):
        """turn = current turn number"""
        if turn <= 10:
            return 1.0
        elif turn <= 20:
            return (20 - turn) / 10
        return 0.0
    
    def game_phase_mid(self, turn):
        if turn <= 10:
            return 0.0
        elif turn <= 20:
            return (turn - 10) / 10
        elif turn <= 35:
            return (35 - turn) / 15
        return 0.0
    
    def game_phase_late(self, turn):
        if turn <= 20:
            return 0.0
        elif turn <= 35:
            return (turn - 20) / 15
        return 1.0
    
    # ========== Defuzzification ==========
    
    def defuzzify(self, low_activation, medium_activation, high_activation):
        """
        Convert fuzzy output to crisp value using center of gravity method
        
        Formula: (Σ activation_i * center_i) / (Σ activation_i)
        """
        # Output membership function centers
        low_center = 0.25
        medium_center = 0.5
        high_center = 0.85
        
        numerator = (low_activation * low_center + 
                    medium_activation * medium_center + 
                    high_activation * high_center)
        denominator = low_activation + medium_activation + high_activation
        
        if denominator == 0:
            return 0.5  # Default medium aggressiveness
        
        return numerator / denominator
    
    # ========== Strategic Value Calculator ==========
    
    def calculate_strategic_value(self, planet):
        """
        Calculate strategic value of a planet (0-6)
        
        Factors:
        - Base size (1-3)
        - Center position bonus (+2)
        - Near center bonus (+1)
        - Border penalty (-0.5)
        """
        value = planet.size
        x, y = planet.get_position()
        center_positions = [(1, 1), (1, 2), (2, 1), (2, 2)]
        
        if (x, y) in center_positions:
            value += 2  # Center bonus
        elif 0 < x < 3 and 0 < y < 3:
            value += 1  # Near center bonus
        
        # Border planets get slight penalty (more vulnerable)
        if x == 0 or x == 3 or y == 0 or y == 3:
            value = max(1, value - 0.5)
        
        return value
    
    # ========== Main Fuzzy Evaluation ==========
    
    def evaluate_attack(self, source, target, owner):
        """
        Evaluate attack aggressiveness using fuzzy logic
        
        Process:
        1. Fuzzification: Convert inputs to membership degrees
        2. Rule Evaluation: Apply IF-THEN rules
        3. Defuzzification: Convert to crisp output value
        
        Returns: aggressiveness score (0.0 to 1.0)
        """
        # Calculate inputs
        if source.ships == 0:
            ship_ratio = 1.0
        else:
            ship_ratio = target.ships / source.ships
        
        strategic_value = self.calculate_strategic_value(target)
        current_turn = self.board.turn // 2 + 1
        
        # ========== Fuzzification ==========
        weak = self.planet_strength_weak(ship_ratio)
        medium_strength = self.planet_strength_medium(ship_ratio)
        strong = self.planet_strength_strong(ship_ratio)
        
        low_value = self.strategic_value_low(strategic_value)
        medium_value = self.strategic_value_medium(strategic_value)
        high_value = self.strategic_value_high(strategic_value)
        
        early = self.game_phase_early(current_turn)
        mid = self.game_phase_mid(current_turn)
        late = self.game_phase_late(current_turn)
        
        # ========== Fuzzy Rules ==========
        low_agg = 0.0
        medium_agg = 0.0
        high_agg = 0.0
        
        # Rule 1: If planet is STRONG, aggressiveness is LOW
        low_agg = max(low_agg, strong)
        
        # Rule 2: If planet is WEAK and value is HIGH, aggressiveness is HIGH
        high_agg = max(high_agg, min(weak, high_value))
        
        # Rule 3: If planet is WEAK and value is LOW, aggressiveness is MEDIUM
        medium_agg = max(medium_agg, min(weak, low_value))
        
        # Rule 4: If planet is MEDIUM strength and value is HIGH, aggressiveness is MEDIUM
        medium_agg = max(medium_agg, min(medium_strength, high_value))
        
        # Rule 5: If planet is MEDIUM strength and value is LOW, aggressiveness is LOW
        low_agg = max(low_agg, min(medium_strength, low_value))
        
        # Rule 6: If game is EARLY and planet is WEAK, aggressiveness is HIGH
        high_agg = max(high_agg, min(early, weak))
        
        # Rule 7: If game is LATE and planet is WEAK and HIGH value, aggressiveness is HIGH
        high_agg = max(high_agg, min(late, min(weak, high_value)))
        
        # Rule 8: If game is LATE and planet is STRONG, aggressiveness is LOW
        low_agg = max(low_agg, min(late, strong))
        
        # Rule 9: If game is MID and value is MEDIUM, aggressiveness is MEDIUM
        medium_agg = max(medium_agg, min(mid, medium_value))
        
        # ========== Defuzzification ==========
        aggressiveness = self.defuzzify(low_agg, medium_agg, high_agg)
        
        return aggressiveness
    
    def get_ship_count_recommendation(self, source, target, owner, aggressiveness):
        """
        Recommend number of ships to send based on aggressiveness
        
        Strategy:
        - High aggressiveness (≥0.7): Overwhelming force (1.5x needed)
        - Medium aggressiveness (0.4-0.7): Moderate force (1.2x needed)
        - Low aggressiveness (<0.4): Minimal force or skip
        """
        available_ships = source.ships - 1  # Must leave at least 1
        
        if available_ships <= 0:
            return 0
        
        if target.owner == owner:
            # Reinforcement - send based on aggressiveness
            base_ships = int(available_ships * aggressiveness)
        else:
            # Attack - need to overcome defense
            needed_to_capture = target.ships + 1
            
            if aggressiveness >= 0.7:
                # High aggressiveness - overwhelming force
                base_ships = min(available_ships, int(needed_to_capture * 1.5))
            elif aggressiveness >= 0.4:
                # Medium aggressiveness - moderate force
                base_ships = min(available_ships, int(needed_to_capture * 1.2))
            else:
                # Low aggressiveness - minimal force or skip
                if needed_to_capture < available_ships:
                    base_ships = needed_to_capture
                else:
                    return 0
        
        return max(1, min(base_ships, available_ships))