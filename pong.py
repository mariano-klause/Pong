#!/usr/bin/env python3
"""
Pong - A classic arcade game implementation.
Player vs Computer with scoring and progressive difficulty.

Author: Blue (Senior Software Engineer)
License: MIT
"""

import pygame
import random
import sys
from dataclasses import dataclass
from typing import Tuple

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)

# Game constants
PADDLE_WIDTH = 15
PADDLE_HEIGHT = 100
BALL_SIZE = 15

PADDLE_SPEED = 6
BALL_BASE_SPEED = 5
SPEED_INCREMENT = 0.5
WINNING_SCORE = 10


@dataclass
class Ball:
    """Represents the game ball with position and velocity."""
    x: float
    y: float
    vx: float
    vy: float

    def get_rect(self) -> pygame.Rect:
        """Get the ball's rectangle for collision detection."""
        return pygame.Rect(self.x - BALL_SIZE//2, self.y - BALL_SIZE//2, BALL_SIZE, BALL_SIZE)

    def move(self) -> None:
        """Update ball position based on velocity."""
        self.x += self.vx
        self.y += self.vy

    def reset(self, direction: int) -> None:
        """Reset ball to center with initial velocity."""
        self.x = SCREEN_WIDTH // 2
        self.y = SCREEN_HEIGHT // 2
        speed = BALL_BASE_SPEED + random.uniform(0, 2)
        angle = random.uniform(-45, 45)
        self.vx = direction * speed * random.choice([0.8, 1.0, 1.2])
        self.vy = speed * random.choice([-1, 1]) * random.uniform(0.5, 1.0)


class Paddle:
    """Represents a paddle with position and AI behavior."""
    
    def __init__(self, x: float, is_ai: bool = False):
        self.x = x
        self.y = SCREEN_HEIGHT // 2 - PADDLE_HEIGHT // 2
        self.is_ai = is_ai
        self.speed = PADDLE_SPEED
        self.reaction_delay = 0
    
    def get_rect(self) -> pygame.Rect:
        """Get paddle rectangle for collision detection."""
        return pygame.Rect(self.x, self.y, PADDLE_WIDTH, PADDLE_HEIGHT)
    
    def move_up(self) -> None:
        """Move paddle up with boundary checking."""
        self.y = max(0, self.y - self.speed)
    
    def move_down(self) -> None:
        """Move paddle down with boundary checking."""
        self.y = min(SCREEN_HEIGHT - PADDLE_HEIGHT, self.y + self.speed)
    
    def ai_update(self, ball: Ball, ball_speed_multiplier: float) -> None:
        """AI paddle update with prediction and competitive behavior."""
        if not self.is_ai:
            return
        
        # AI only reacts when ball is moving toward it
        if ball.vx < 0:
            return
        
        # Simulate minimal reaction time (reduced from 3 to 1)
        self.reaction_delay += 1
        if self.reaction_delay < 1:
            return
        self.reaction_delay = 0
        
        # PREDICT where ball will be when it reaches AI paddle
        if ball.vx > 0:
            # Time for ball to reach AI side
            distance_to_ai = self.x - ball.x
            time_to_reach = distance_to_ai / ball.vx if ball.vx > 0 else 1
            
            # Predict Y position with bounce physics
            predicted_y = ball.y + ball.vy * time_to_reach
            
            # Account for wall bounces
            while predicted_y < 0 or predicted_y > SCREEN_HEIGHT:
                if predicted_y < 0:
                    predicted_y = -predicted_y
                elif predicted_y > SCREEN_HEIGHT:
                    predicted_y = 2 * SCREEN_HEIGHT - predicted_y
            
            target_y = predicted_y - PADDLE_HEIGHT // 2
        else:
            target_y = ball.y - PADDLE_HEIGHT // 2
        
        # Reduced inaccuracy (σ=5px vs σ=10px for better play)
        error = random.gauss(0, 5)
        target_y += error
        
        # Clamp target to valid range
        target_y = max(0, min(SCREEN_HEIGHT - PADDLE_HEIGHT, target_y))
        
        # Faster AI speed (base 8 vs base 6, shorter when needed)
        ai_speed = self.speed * 1.4 * ball_speed_multiplier * random.uniform(0.95, 1.05)
        
        # Move toward target
        if self.y < target_y - 3:  # Tighter tolerance
            self.y = min(SCREEN_HEIGHT - PADDLE_HEIGHT, self.y + ai_speed)
        elif self.y > target_y + 3:
            self.y = max(0, self.y - ai_speed)


class Game:
    """Main game controller managing state and rendering."""
    
    def __init__(self):
        pygame.init()
        
        # Initialize sound with graceful fallback
        self.sound_enabled = False
        try:
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
            self.sound_enabled = True
            self._init_sounds()
        except pygame.error:
            print("Warning: Audio not available. Game will run without sound.")
            self.sound_enabled = False
        
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Pong - Player vs Computer")
        self.clock = pygame.time.Clock()
        self.font_large = pygame.font.Font(None, 74)
        self.font_medium = pygame.font.Font(None, 48)
        self.font_small = pygame.font.Font(None, 36)
        
        self.reset_game()
    
    def _init_sounds(self) -> None:
        """Generate synthetic sound effects."""
        import numpy as np
        
        def generate_beep(frequency: float, duration: float, volume: float = 0.3) -> pygame.mixer.Sound:
            """Generate a beep sound using numpy."""
            sample_rate = 44100
            num_samples = int(duration * sample_rate)
            
            # Generate sine wave
            t = np.linspace(0, duration, num_samples, False)
            wave = np.sin(2 * np.pi * frequency * t)
            
            # Apply envelope (attack and decay)
            attack = int(sample_rate * 0.01)
            decay = int(sample_rate * 0.05)
            envelope = np.ones(num_samples)
            envelope[:attack] = np.linspace(0, 1, attack)
            envelope[-decay:] = np.linspace(1, 0, decay)
            
            wave = wave * envelope * volume
            
            # Convert to 16-bit PCM
            audio = (wave * 32767).astype(np.int16)
            audio = np.column_stack((audio, audio))  # Stereo
            
            return pygame.sndarray.make_sound(audio)
        
        # Create sounds
        self.sounds = {
            'paddle_hit': generate_beep(440, 0.1),      # A4 - mid tone
            'score': generate_beep(880, 0.2),            # A5 - high tone
            'win': generate_beep(1320, 0.5),            # E6 - victory
        }
    
    def _play_sound(self, sound_name: str) -> None:
        """Play a sound if audio is enabled."""
        if self.sound_enabled and sound_name in self.sounds:
            self.sounds[sound_name].play()
    
    def reset_game(self) -> None:
        """Initialize or reset game state."""
        self.player_paddle = Paddle(20, is_ai=False)
        self.ai_paddle = Paddle(SCREEN_WIDTH - 35, is_ai=True)
        self.ball = Ball(SCREEN_WIDTH//2, SCREEN_HEIGHT//2, 0, 0)
        self.ball.reset(direction=random.choice([-1, 1]))
        
        self.player_score = 0
        self.ai_score = 0
        self.ball_speed_multiplier = 1.0
        self.game_over = False
        self.winner = None
        self.paused = False
    
    def update(self) -> None:
        """Update game state for one frame."""
        if self.game_over or self.paused:
            return
        
        # Update AI paddle
        self.ai_paddle.ai_update(self.ball, self.ball_speed_multiplier)
        
        # Move ball
        self.ball.move()
        
        # Ball collision with top/bottom walls
        if self.ball.y - BALL_SIZE//2 <= 0 or self.ball.y + BALL_SIZE//2 >= SCREEN_HEIGHT:
            self.ball.vy *= -1
            self.ball.y = max(BALL_SIZE//2, min(SCREEN_HEIGHT - BALL_SIZE//2, self.ball.y))
        
        # Ball collision with player paddle
        player_rect = self.player_paddle.get_rect()
        ball_rect = self.ball.get_rect()
        
        if ball_rect.colliderect(player_rect) and self.ball.vx < 0:
            self._handle_paddle_hit(self.player_paddle)
        
        # Ball collision with AI paddle
        ai_rect = self.ai_paddle.get_rect()
        if ball_rect.colliderect(ai_rect) and self.ball.vx > 0:
            self._handle_paddle_hit(self.ai_paddle)
        
        # Score detection
        if self.ball.x < 0:
            self._score_point(ai_wins=True)  # Ball passed player (left side), AI scores
        elif self.ball.x > SCREEN_WIDTH:
            self._score_point(ai_wins=False)  # Ball passed AI (right side), player scores
    
    def _handle_paddle_hit(self, paddle: Paddle) -> None:
        """Handle ball hitting a paddle with physics."""
        # Reverse horizontal direction
        self.ball.vx *= -1
        
        # Add "spin" based on where ball hit paddle
        hit_pos = (self.ball.y - paddle.y) / PADDLE_HEIGHT
        self.ball.vy += (hit_pos - 0.5) * 4
        
        # Increase speed gradually
        self.ball.vx *= 1.05
        self.ball.vy *= 1.02
        self.ball_speed_multiplier += SPEED_INCREMENT / 10
        
        # Play paddle hit sound
        self._play_sound('paddle_hit')
        
        # Push ball out of paddle to prevent sticking
        if paddle.is_ai:
            self.ball.x = paddle.x - BALL_SIZE//2 - 1
        else:
            self.ball.x = paddle.x + PADDLE_WIDTH + BALL_SIZE//2 + 1
    
    def _score_point(self, ai_wins: bool) -> None:
        """Update score and check for game over."""
        if ai_wins:
            self.ai_score += 1
            self.ball.reset(direction=-1)
        else:
            self.player_score += 1
            self.ball.reset(direction=1)
        
        # Play score sound
        self._play_sound('score')
        
        # Check for winner
        if self.player_score >= WINNING_SCORE:
            self.game_over = True
            self.winner = "Player"
            self._play_sound('win')
        elif self.ai_score >= WINNING_SCORE:
            self.game_over = True
            self.winner = "Computer"
            self._play_sound('win')
    
    def draw(self) -> None:
        """Render the game frame."""
        self.screen.fill(BLACK)
        
        # Draw center line
        for y in range(0, SCREEN_HEIGHT, 20):
            pygame.draw.rect(self.screen, GRAY, (SCREEN_WIDTH//2 - 2, y, 4, 10))
        
        # Draw paddles
        pygame.draw.rect(self.screen, WHITE, self.player_paddle.get_rect())
        pygame.draw.rect(self.screen, WHITE, self.ai_paddle.get_rect())
        
        # Draw ball
        pygame.draw.rect(self.screen, WHITE, self.ball.get_rect())
        
        # Draw scores
        player_text = self.font_large.render(str(self.player_score), True, WHITE)
        ai_text = self.font_large.render(str(self.ai_score), True, WHITE)
        self.screen.blit(player_text, (SCREEN_WIDTH//4 - player_text.get_width()//2, 20))
        self.screen.blit(ai_text, (3*SCREEN_WIDTH//4 - ai_text.get_width()//2, 20))
        
        # Draw speed indicator
        if not self.game_over:
            speed_text = self.font_small.render(f"Speed: {self.ball_speed_multiplier:.1f}x", True, GRAY)
            self.screen.blit(speed_text, (SCREEN_WIDTH//2 - speed_text.get_width()//2, 60))
        
        # Draw game over screen
        if self.game_over:
            self._draw_game_over()
        elif self.paused:
            self._draw_pause()
        
        pygame.display.flip()
    
    def _draw_game_over(self) -> None:
        """Render game over overlay."""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        game_over_text = self.font_large.render("GAME OVER", True, WHITE)
        winner_text = self.font_medium.render(f"{self.winner} Wins!", True, WHITE)
        restart_text = self.font_small.render("Press R to restart, Q to quit", True, GRAY)
        
        self.screen.blit(game_over_text, 
                        (SCREEN_WIDTH//2 - game_over_text.get_width()//2, SCREEN_HEIGHT//2 - 80))
        self.screen.blit(winner_text, 
                        (SCREEN_WIDTH//2 - winner_text.get_width()//2, SCREEN_HEIGHT//2))
        self.screen.blit(restart_text, 
                        (SCREEN_WIDTH//2 - restart_text.get_width()//2, SCREEN_HEIGHT//2 + 60))
    
    def _draw_pause(self) -> None:
        """Render pause overlay."""
        pause_text = self.font_large.render("PAUSED", True, WHITE)
        hint_text = self.font_small.render("Press P to resume", True, GRAY)
        self.screen.blit(pause_text, 
                        (SCREEN_WIDTH//2 - pause_text.get_width()//2, SCREEN_HEIGHT//2 - 40))
        self.screen.blit(hint_text, 
                        (SCREEN_WIDTH//2 - hint_text.get_width()//2, SCREEN_HEIGHT//2 + 20))
    
    def handle_input(self) -> bool:
        """Process input events. Returns False to quit."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    return False
                elif event.key == pygame.K_r:
                    self.reset_game()
                elif event.key == pygame.K_p:
                    self.paused = not self.paused
        
        # Continuous key presses for paddle movement
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.player_paddle.move_up()
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.player_paddle.move_down()
        
        return True
    
    def run(self) -> None:
        """Main game loop."""
        running = True
        while running:
            running = self.handle_input()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        
        pygame.quit()


def main() -> None:
    """Entry point with dependency check."""
    try:
        import pygame
    except ImportError:
        print("Error: pygame is required. Install with: pip install pygame")
        sys.exit(1)
    
    game = Game()
    game.run()


if __name__ == "__main__":
    main()