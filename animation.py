# animation.py
# Visual effects and animations

import pygame


class Animation:
    """Manages visual animations for attacks"""
    
    def __init__(self):
        self.active_animations = []
    
    def add_attack(self, source_pos, target_pos, color):
        """
        Add attack animation
        
        Parameters:
        - source_pos: (x, y) screen coordinates
        - target_pos: (x, y) screen coordinates
        - color: RGB tuple
        """
        self.active_animations.append({
            'type': 'attack',
            'start': source_pos,
            'end': target_pos,
            'color': color,
            'progress': 0.0,
            'speed': 0.05  # Animation speed (0-1 per frame)
        })
    
    def update(self):
        """Update all animations (call each frame)"""
        for anim in self.active_animations[:]:
            anim['progress'] += anim['speed']
            if anim['progress'] >= 1.0:
                self.active_animations.remove(anim)
    
    def draw(self, screen):
        """
        Draw all active animations
        
        Visual effect:
        - Line from start to current position
        - Circle at current position (projectile)
        """
        for anim in self.active_animations:
            if anim['type'] == 'attack':
                start_x, start_y = anim['start']
                end_x, end_y = anim['end']
                progress = anim['progress']
                
                # Calculate current position (linear interpolation)
                current_x = start_x + (end_x - start_x) * progress
                current_y = start_y + (end_y - start_y) * progress
                
                # Draw line from start to current position
                pygame.draw.line(screen, anim['color'], 
                               (start_x, start_y), 
                               (current_x, current_y), 3)
                
                # Draw moving circle at current position
                pygame.draw.circle(screen, anim['color'], 
                                 (int(current_x), int(current_y)), 5)
    
    def is_playing(self):
        """Check if any animations are playing"""
        return len(self.active_animations) > 0